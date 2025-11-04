# YFinance Chatbot 📈

A conversational chatbot for querying stock market data using natural language. Built with FastAPI, Streamlit, Plotly, and NocoDB.

## Features

- 🤖 **AI-Powered Conversations** - Natural language queries powered by Google Gemini 2.0 Flash
- 💬 **Interactive Chatbot** - Ask any question about stocks, investing, or market analysis
- 📊 **Dynamic Charts** - Beautiful interactive charts (candlestick, line, volume, dividends)
- 🎯 **Smart Suggestions** - Get follow-up question recommendations after each query
- ⚡ **Quick Actions** - One-click buttons for common queries
- 🔄 **Real-time Data** - Live stock data from Yahoo Finance
- 📈 **Comprehensive Analysis** - P/E ratios, market cap, dividends, volume, and more
- 💾 **History Tracking** - Save all queries to NocoDB
- 🎨 **Beautiful UI** - Modern, responsive interface with Streamlit
- 🚀 **Fast API** - High-performance backend with FastAPI

## Project Structure

```
yfinance-chatbot/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── app.py              # Streamlit app
│   └── requirements.txt    # Frontend dependencies
├── .env.example            # Environment variables template
└── README.md
```

## Setup

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pip install -r requirements.txt
```

### 2. Configure Google Gemini API

1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Update `backend/.env` with your API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Configure NocoDB (Optional)

1. Install and run NocoDB:
```bash
docker run -d --name nocodb -p 8080:8080 nocodb/nocodb:latest
```

2. Create a new table with these fields:
   - `question` (SingleLineText)
   - `ticker` (SingleLineText)
   - `timestamp` (DateTime)
   - `response` (LongText)

3. Get your API token and table ID from NocoDB

4. Update `backend/.env` with your NocoDB credentials

### 4. Run the Application

**Start Backend (Terminal 1):**
```bash
cd backend
python main.py
```
The API will be available at `http://localhost:8000`

**Start Frontend (Terminal 2):**
```bash
cd frontend
streamlit run app.py
```
The app will open in your browser at `http://localhost:8501`

## Usage

1. Enter a stock ticker in the sidebar (e.g., AAPL, GOOGL, MSFT)
2. Select a time period
3. Ask questions in natural language:
   - "Show me the price chart"
   - "What's the company info?"
   - "Show me the volume"
   - "What are the dividends?"
   - "Show me the price trend"

## Example Questions

The chatbot can handle a wide variety of questions:

**Basic Queries:**
- "Show me the price chart"
- "What's the current price?"
- "Tell me about this company"

**Analysis & Insights:**
- "How has this stock performed this year?"
- "Is this stock overvalued?"
- "Give me a detailed analysis"
- "What's the P/E ratio?"
- "Compare to the 52-week high"

**Market Data:**
- "Show me the trading volume"
- "What are the dividends?"
- "What sector is this in?"
- "Show me the price trend"

**Investment Questions:**
- "Should I invest in this stock?"
- "What are the risks?"
- "Explain the recent trend"
- "How volatile is this stock?"

## API Endpoints

- `GET /` - Health check
- `POST /query` - Process natural language query
- `GET /history` - Get query history from NocoDB

## Technologies

- **AI**: Google Gemini Flash (gemini-1.5-flash)
- **Backend**: FastAPI, YFinance, Pandas
- **Frontend**: Streamlit, Plotly
- **Database**: NocoDB
- **Data Source**: Yahoo Finance

## Notes

- NocoDB is optional - the app works without it, but history won't be saved
- Make sure both backend and frontend are running
- The backend must be running on port 8000 for the frontend to connect

## License

MIT
