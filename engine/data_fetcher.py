import yfinance as yf
import pandas as pd
import streamlit as st

def format_ticker(ticker):
    ticker = ticker.upper().strip()
    if not (ticker.endswith(".NS") or ticker.endswith(".BO")):
        return f"{ticker}.NS"
    return ticker

def get_live_metrics(ticker):
    formatted_ticker = format_ticker(ticker)
    stock = yf.Ticker(formatted_ticker)
    
    # 1d data for live stats
    data = stock.history(period="1d", interval="1m")
    if data.empty:
        return None
    
    latest_row = data.iloc[-1]
    first_row = data.iloc[0] 
    
    return {
        "live_price": latest_row["Close"],
        "open_price": first_row["Open"], 
        "prev_close": stock.info.get("previousClose", 0),
        "day_high": data["High"].max(),
        "day_low": data["Low"].min(),
        "live_volume": int(data["Volume"].sum())  # Total cumulative volume for the day
    }
    
@st.cache_data(ttl=60) 
def get_historical_data(ticker, timeframe):
    formatted_ticker = format_ticker(ticker)
    stock = yf.Ticker(formatted_ticker)
    
    settings = {
        "1D": {"p": "1d", "i": "5m"},
        "3M": {"p": "3mo", "i": "1d"},
        "6M": {"p": "6mo", "i": "1d"},
        "1Y": {"p": "1y", "i": "1d"},
        "5Y": {"p": "5y", "i": "1mo"},
        
    }
    conf = settings.get(timeframe)
    return stock.history(period=conf["p"], interval=conf["i"])