from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import yfinance as yf
import pandas as pd

app = FastAPI(title="GoldRocks Dashboard - Public")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_gold_signal():
    """
    Fetches latest gold futures data and returns simple BUY/SELL signals.
    Uses 1-minute and 15-minute intervals.
    """
    try:
        # Pull recent gold futures data
        data_1m = yf.download(tickers="GC=F", period="60m", interval="1m")
        data_15m = yf.download(tickers="GC=F", period="1d", interval="15m")

        # Simple example strategy: moving average crossover
        # 1M timeframe
        if not data_1m.empty:
            ma_short = data_1m['Close'].iloc[-3:].mean()
            ma_long = data_1m['Close'].iloc[-10:].mean()
            signal_1m = "BUY" if ma_short > ma_long else "SELL"
        else:
            signal_1m = "BUY"

        # 15M timeframe
        if not data_15m.empty:
            ma_short = data_15m['Close'].iloc[-2:].mean()
            ma_long = data_15m['Close'].iloc[-8:].mean()
            signal_15m = "BUY" if ma_short > ma_long else "SELL"
        else:
            signal_15m = "SELL"

        return {'1m': signal_1m, '15m': signal_15m}
    except:
        return {'1m': 'BUY', '15m': 'SELL'}  # fallback if API fails

@app.get("/", response_class=HTMLResponse)
def home():
    signals = get_gold_signal()
    html = f"""
    <html>
    <head>
        <title>GoldRocks Dashboard</title>
        <meta http-equiv='refresh' content='15'>
        <style>
            body {{
                background-color: #101010;
                color: #fff;
                font-family: Arial, sans-serif;
                text-align: center;
            }}
            .wrapper {{
                display: flex;
                justify-content: center;
                margin-top: 100px;
                gap: 50px;
            }}
            .box {{
                width: 200px;
                height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 20px;
                font-size: 30px;
                font-weight: bold;
                box-shadow: 0 0 15px rgba(255,255,255,0.2);
            }}
            .buy {{ background-color: #0a8f00; }}
            .sell {{ background-color: #c00; }}
        </style>
    </head>
    <body>
        <h1>GoldRocks Final Signals</h1>
        <p>Live Auto-Updating Signals (Every 15s)</p>
        <div class='wrapper'>
            <div class='box {"buy" if signals["1m"]=="BUY" else "sell"}'>1M: {signals["1m"]}</div>
            <div class='box {"buy" if signals["15m"]=="BUY" else "sell"}'>15M: {signals["15m"]}</div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
