from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YFinance Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# NocoDB configuration
NOCODB_URL = os.getenv("NOCODB_URL", "http://localhost:8080")
NOCODB_TOKEN = os.getenv("NOCODB_TOKEN", "")
NOCODB_TABLE_ID = os.getenv("NOCODB_TABLE_ID", "")

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("✅ Gemini 2.0 Flash configured successfully")
    except Exception as e:
        print(f"⚠️ Gemini 2.0 Flash configuration error: {e}")
        model = None
else:
    model = None
    print("⚠️ No Gemini API key found, using fallback mode")

class QueryRequest(BaseModel):
    question: str
    ticker: Optional[str] = None
    period: Optional[str] = "1mo"

class QueryResponse(BaseModel):
    answer: str
    data: dict
    chart_type: str

def save_to_nocodb(question: str, ticker: str, response: dict):
    """Save query history to NocoDB"""
    if not NOCODB_TOKEN or not NOCODB_TABLE_ID:
        return
    
    try:
        headers = {
            "xc-token": NOCODB_TOKEN,
            "Content-Type": "application/json"
        }
        data = {
            "question": question,
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "response": str(response)
        }
        requests.post(
            f"{NOCODB_URL}/api/v1/db/data/noco/{NOCODB_TABLE_ID}",
            headers=headers,
            json=data,
            timeout=5
        )
    except Exception as e:
        # Silently fail if NocoDB is not available
        pass

def get_stock_data(ticker: str, period: str):
    """Fetch comprehensive stock data"""
    try:
        # Create ticker with proper headers to avoid rate limiting
        stock = yf.Ticker(ticker)
        
        # Fetch history - yfinance v0.2.32+ uses different method
        hist = pd.DataFrame()
        try:
            hist = stock.history(period=period, interval="1d", actions=False, auto_adjust=True, back_adjust=False, repair=True, keepna=False, proxy=None, rounding=False, timeout=30)
        except Exception as e:
            print(f"History fetch error: {e}")
            # Try alternative method
            try:
                import yfinance.shared as shared
                shared._ERRORS.clear()
                hist = stock.history(period=period)
            except:
                pass
        
        # Get info with fallback
        info = {}
        try:
            info = stock.info
            if not info or len(info) == 0:
                # Try fast_info as fallback
                try:
                    fast_info = stock.fast_info
                    info = {
                        "longName": ticker,
                        "currentPrice": fast_info.get("lastPrice", 0),
                        "marketCap": fast_info.get("marketCap", 0),
                        "sector": "N/A"
                    }
                except:
                    info = {"longName": ticker, "currentPrice": 0, "sector": "N/A"}
        except Exception as e:
            print(f"Info fetch error: {e}")
            info = {"longName": ticker, "currentPrice": 0, "sector": "N/A"}
        
        # Get dividends
        dividends = pd.Series()
        try:
            dividends = stock.dividends
        except Exception as e:
            print(f"Dividends fetch error: {e}")
        
        # If we have history, update current price from it
        if not hist.empty and "currentPrice" not in info:
            info["currentPrice"] = float(hist["Close"].iloc[-1])
        
        return {
            "history": hist,
            "info": info,
            "dividends": dividends,
            "ticker": ticker
        }
    except Exception as e:
        print(f"Stock data error: {e}")
        raise HTTPException(status_code=400, detail=f"Unable to fetch data for {ticker}. Please check the ticker symbol and try again.")

def analyze_with_gemini(question: str, stock_data: dict):
    """Use Gemini to understand user intent and generate response"""
    if not model:
        # Fallback to simple keyword matching
        return analyze_without_gemini(question, stock_data)
    
    try:
        ticker = stock_data["ticker"]
        info = stock_data["info"]
        hist = stock_data["history"]
        
        # Prepare context for Gemini
        context = f"""
You are a financial assistant analyzing stock data for {ticker}.

Available data:
- Company: {info.get('longName', ticker)}
- Sector: {info.get('sector', 'N/A')}
- Current Price: ${info.get('currentPrice', 0):.2f}
- Market Cap: ${info.get('marketCap', 0):,.0f}
- 52 Week High: ${info.get('fiftyTwoWeekHigh', 0):.2f}
- 52 Week Low: ${info.get('fiftyTwoWeekLow', 0):.2f}
- P/E Ratio: {info.get('trailingPE', 'N/A')}
- Dividend Yield: {info.get('dividendYield', 0) * 100:.2f}%

Recent price data available: {len(hist)} days

User question: {question}

Based on the question, determine:
1. What type of chart to show: "candlestick", "line", "volume", "bar", or "none"
2. A brief, informative answer (2-3 sentences max)

Respond in this exact format:
CHART_TYPE: [type]
ANSWER: [your answer]
"""
        
        response = model.generate_content(context)
        response_text = response.text.strip()
        
        # Parse Gemini response
        chart_type = "none"
        answer = response_text
        
        if "CHART_TYPE:" in response_text and "ANSWER:" in response_text:
            parts = response_text.split("ANSWER:")
            chart_type_part = parts[0].replace("CHART_TYPE:", "").strip().lower()
            answer = parts[1].strip()
            
            # Validate chart type
            valid_types = ["candlestick", "line", "volume", "bar", "none"]
            for vtype in valid_types:
                if vtype in chart_type_part:
                    chart_type = vtype
                    break
        
        return chart_type, answer
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return analyze_without_gemini(question, stock_data)

def analyze_without_gemini(question: str, stock_data: dict):
    """Fallback analysis without Gemini"""
    question_lower = question.lower()
    ticker = stock_data["ticker"]
    info = stock_data["info"]
    hist = stock_data["history"]
    
    if any(word in question_lower for word in ["info", "about", "company", "details", "sector", "business"]):
        answer = f"{info.get('longName', ticker)} operates in the {info.get('sector', 'N/A')} sector. "
        answer += f"Market Cap: ${info.get('marketCap', 0):,.0f}. Current Price: ${info.get('currentPrice', 0):.2f}"
        return "none", answer
    
    elif any(word in question_lower for word in ["price", "chart", "history", "trend", "performance"]):
        if not hist.empty:
            latest_price = hist["Close"].iloc[-1]
            change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100
            answer = f"{ticker} is currently at ${latest_price:.2f}, {change:+.2f}% change in the selected period."
            return "candlestick", answer
        return "none", "No price data available"
    
    elif "dividend" in question_lower:
        dividends = stock_data["dividends"]
        if not dividends.empty:
            answer = f"Latest dividend: ${dividends.iloc[-1]:.2f} on {dividends.index[-1].strftime('%Y-%m-%d')}"
            return "bar", answer
        return "none", f"{ticker} has no dividend history or doesn't pay dividends."
    
    elif "volume" in question_lower:
        if not hist.empty:
            avg_volume = hist["Volume"].mean()
            answer = f"{ticker} average trading volume: {avg_volume:,.0f} shares"
            return "volume", answer
        return "none", "No volume data available"
    
    else:
        if not hist.empty:
            latest_price = hist["Close"].iloc[-1]
            answer = f"{ticker} current price: ${latest_price:.2f}. Ask me about price trends, company info, dividends, or volume!"
            return "line", answer
        return "none", "Please ask about price, company info, dividends, or volume."

def parse_question(question: str, ticker: str, period: str):
    """Parse natural language question and fetch data"""
    if not ticker:
        return {
            "answer": "Please provide a stock ticker symbol (e.g., AAPL, GOOGL, MSFT)",
            "data": {},
            "chart_type": "none"
        }
    
    try:
        # Fetch stock data
        stock_data = get_stock_data(ticker, period)
        
        # Analyze with Gemini
        chart_type, answer = analyze_with_gemini(question, stock_data)
        
        # Prepare chart data based on chart type
        data_dict = {}
        hist = stock_data["history"]
        
        if chart_type == "candlestick" and not hist.empty:
            data_dict = {
                "dates": hist.index.strftime("%Y-%m-%d").tolist(),
                "open": hist["Open"].tolist(),
                "high": hist["High"].tolist(),
                "low": hist["Low"].tolist(),
                "close": hist["Close"].tolist(),
                "volume": hist["Volume"].tolist()
            }
        elif chart_type == "line" and not hist.empty:
            data_dict = {
                "dates": hist.index.strftime("%Y-%m-%d").tolist(),
                "close": hist["Close"].tolist()
            }
        elif chart_type == "volume" and not hist.empty:
            data_dict = {
                "dates": hist.index.strftime("%Y-%m-%d").tolist(),
                "volume": hist["Volume"].tolist()
            }
        elif chart_type == "bar":
            dividends = stock_data["dividends"]
            if not dividends.empty:
                recent_divs = dividends.tail(10)
                data_dict = {
                    "dates": recent_divs.index.strftime("%Y-%m-%d").tolist(),
                    "dividends": recent_divs.tolist()
                }
        
        return {
            "answer": answer,
            "data": data_dict,
            "chart_type": chart_type
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "YFinance Chatbot API"}

@app.post("/query", response_model=QueryResponse)
def query_stock(request: QueryRequest):
    """Process natural language query about stocks"""
    result = parse_question(request.question, request.ticker, request.period)
    
    # Save to NocoDB
    save_to_nocodb(request.question, request.ticker or "", result)
    
    return result

@app.get("/history")
def get_history():
    """Get query history from NocoDB"""
    if not NOCODB_TOKEN or not NOCODB_TABLE_ID:
        return {"message": "NocoDB not configured", "data": []}
    
    try:
        headers = {"xc-token": NOCODB_TOKEN}
        response = requests.get(
            f"{NOCODB_URL}/api/v1/db/data/noco/{NOCODB_TABLE_ID}",
            headers=headers
        )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
