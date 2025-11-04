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

# Sidebar
with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Stock Ticker", value="AAPL", help="Enter stock symbol (e.g., AAPL, GOOGL)")
    period = st.selectbox(
        "Time Period",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=2
    )
    
    st.markdown("---")
    st.markdown("### Example Questions")
    st.markdown("""
    - Show me the price chart
    - What's the company info?
    - Show me the volume
    - What are the dividends?
    - Show me the price trend
    """)
    
    st.markdown("---")
    if st.button("View History"):
        try:
            response = requests.get(f"{API_URL}/history")
            if response.status_code == 200:
                history = response.json()
                st.json(history)
        except Exception as e:
            st.error(f"Error fetching history: {e}")

# Chat interface
st.markdown("### Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "chart" in message:
            st.plotly_chart(message["chart"], use_container_width=True)

# Chat input
if prompt := st.chat_input("Ask about a stock..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "question": prompt,
                        "ticker": ticker,
                        "period": period
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    data = result["data"]
                    chart_type = result["chart_type"]
                    
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
                            "chart": chart
                        })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer
                        })
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

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
