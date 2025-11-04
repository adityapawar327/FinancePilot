# YFinance Chatbot 📈

A conversational chatbot for querying stock market data using natural language. Built with FastAPI, Streamlit, Plotly, and NocoDB.

## Features

- 💬 Natural language queries powered by Google Gemini Flash
- 🤖 Intelligent understanding of stock-related questions
- 📊 Dynamic interactive charts (candlestick, line, volume, dividends)
- 🔄 Real-time data from Yahoo Finance
- 💾 Query history saved to NocoDB
- 🎨 Beautiful UI with Streamlit
- ⚡ Fast API backend with FastAPI

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

- **Price Data**: "Show me the price chart", "What's the current price?"
- **Company Info**: "Tell me about the company", "What sector is it in?"
- **Volume**: "Show me the trading volume"
- **Dividends**: "What are the dividends?"
- **Trends**: "Show me the price trend"

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
