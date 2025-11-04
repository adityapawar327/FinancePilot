import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="YFinance Chatbot",
    page_icon="📈",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quick_question" not in st.session_state:
    st.session_state.quick_question = None
if "ticker" not in st.session_state:
    st.session_state.ticker = "AAPL"

def create_candlestick_chart(data):
    """Create candlestick chart with Plotly"""
    fig = go.Figure(data=[go.Candlestick(
        x=data["dates"],
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"],
        name="Price"
    )])
    
    fig.update_layout(
        title="Stock Price Chart",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        height=500,
        template="plotly_dark"
    )
    
    return fig

def create_line_chart(data):
    """Create line chart with Plotly"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data["dates"],
        y=data["close"],
        mode="lines",
        name="Close Price",
        line=dict(color="#00ff00", width=2)
    ))
    
    fig.update_layout(
        title="Stock Price Trend",
        yaxis_title="Price (USD)",
        xaxis_title="Date",
        height=500,
        template="plotly_dark"
    )
    
    return fig

def create_volume_chart(data):
    """Create volume bar chart with Plotly"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data["dates"],
        y=data["volume"],
        name="Volume",
        marker_color="#1f77b4"
    ))
    
    fig.update_layout(
        title="Trading Volume",
        yaxis_title="Volume",
        xaxis_title="Date",
        height=500,
        template="plotly_dark"
    )
    
    return fig

def create_dividend_chart(data):
    """Create dividend bar chart with Plotly"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data["dates"],
        y=data["dividends"],
        name="Dividends",
        marker_color="#ff7f0e"
    ))
    
    fig.update_layout(
        title="Dividend History",
        yaxis_title="Dividend (USD)",
        xaxis_title="Date",
        height=500,
        template="plotly_dark"
    )
    
    return fig

# Title
st.title("📈 YFinance Chatbot")
st.markdown("Ask questions about stocks and get instant answers with interactive charts!")

# Market Overview Section
with st.expander("📊 Market Overview - Top Movers", expanded=True):
    with st.spinner("Loading market data..."):
        try:
            market_data = requests.get(f"{API_URL}/market-overview", timeout=10).json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🚀 Top Gainers")
                for stock in market_data.get("gainers", [])[:5]:
                    change_color = "green" if stock["change_pct"] > 0 else "red"
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 4px 0; background-color: rgba(255,255,255,0.05); border-radius: 5px;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong style="color: #1f77b4;">{stock['ticker']}</strong><br>
                                <small style="color: #888;">{stock['name'][:20]}</small>
                            </div>
                            <div style="text-align: right;">
                                <strong>${stock['price']}</strong><br>
                                <small style="color: {change_color};">+{stock['change']} (+{stock['change_pct']}%)</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📉 Top Losers")
                for stock in market_data.get("losers", [])[:5]:
                    change_color = "red"
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 4px 0; background-color: rgba(255,255,255,0.05); border-radius: 5px;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong style="color: #1f77b4;">{stock['ticker']}</strong><br>
                                <small style="color: #888;">{stock['name'][:20]}</small>
                            </div>
                            <div style="text-align: right;">
                                <strong>${stock['price']}</strong><br>
                                <small style="color: {change_color};">{stock['change']} ({stock['change_pct']}%)</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("### 🔥 Most Active")
                for stock in market_data.get("active", [])[:5]:
                    change_color = "green" if stock["change_pct"] > 0 else "red"
                    sign = "+" if stock["change_pct"] > 0 else ""
                    st.markdown(f"""
                    <div style="padding: 8px; margin: 4px 0; background-color: rgba(255,255,255,0.05); border-radius: 5px;">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <strong style="color: #1f77b4;">{stock['ticker']}</strong><br>
                                <small style="color: #888;">{stock['name'][:20]}</small>
                            </div>
                            <div style="text-align: right;">
                                <strong>${stock['price']}</strong><br>
                                <small style="color: {change_color};">{sign}{stock['change']} ({sign}{stock['change_pct']}%)</small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.info("Market overview loading...")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    ticker = st.text_input("Stock Ticker", value="AAPL", help="Enter stock symbol (e.g., AAPL, GOOGL, MSFT, TSLA)")
    period = st.selectbox(
        "Time Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=2
    )
    
    st.markdown("---")
    st.markdown("### 💡 Try These")
    
    # Quick action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Price Chart", use_container_width=True):
            st.session_state.quick_question = "Show me the price chart"
        if st.button("📈 Performance", use_container_width=True):
            st.session_state.quick_question = "How has this stock performed?"
        if st.button("💰 Dividends", use_container_width=True):
            st.session_state.quick_question = "What are the dividends?"
    
    with col2:
        if st.button("ℹ️ Company Info", use_container_width=True):
            st.session_state.quick_question = "Tell me about this company"
        if st.button("📊 Volume", use_container_width=True):
            st.session_state.quick_question = "Show me the trading volume"
        if st.button("🎯 Analysis", use_container_width=True):
            st.session_state.quick_question = "Give me a detailed analysis"
    
    st.markdown("---")
    st.markdown("### 📝 Example Questions")
    st.markdown("""
    - What's the P/E ratio?
    - Is this stock overvalued?
    - Compare to 52-week high
    - What sector is this in?
    - Should I invest in this?
    - Explain the recent trend
    """)
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Popular Stocks")
    popular = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META"]
    selected_stock = st.selectbox("Quick Select", popular, index=0)
    if st.button("Load Stock", use_container_width=True):
        st.session_state.ticker = selected_stock
        st.rerun()

# Chat interface
st.markdown("### Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chart" in message:
            st.plotly_chart(message["chart"], use_container_width=True)

# Handle quick questions from sidebar
if st.session_state.quick_question:
    prompt = st.session_state.quick_question
    st.session_state.quick_question = None
    st.rerun()

# Chat input
prompt = st.chat_input("Ask me anything about stocks... 💬")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "question": prompt,
                        "ticker": ticker,
                        "period": period
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    data = result["data"]
                    chart_type = result["chart_type"]
                    suggestions = result.get("suggestions", [])
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Create and display chart
                    chart = None
                    if chart_type == "candlestick" and data:
                        chart = create_candlestick_chart(data)
                    elif chart_type == "line" and data:
                        chart = create_line_chart(data)
                    elif chart_type == "volume" and data:
                        chart = create_volume_chart(data)
                    elif chart_type == "bar" and data:
                        chart = create_dividend_chart(data)
                    
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "chart": chart,
                            "suggestions": suggestions
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "suggestions": suggestions
                        })
                    
                    # Display suggestions
                    if suggestions:
                        st.markdown("**💡 You might also want to ask:**")
                        cols = st.columns(min(len(suggestions), 2))
                        for idx, suggestion in enumerate(suggestions[:4]):
                            with cols[idx % 2]:
                                if st.button(suggestion, key=f"sug_{idx}_{len(st.session_state.messages)}"):
                                    st.session_state.quick_question = suggestion
                                    st.rerun()
                else:
                    error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            
            except Exception as e:
                error_msg = f"Error connecting to API: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
