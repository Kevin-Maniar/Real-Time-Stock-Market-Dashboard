import streamlit as st
import plotly.graph_objects as go
import time
import datetime
import pytz

from engine.data_fetcher import get_live_metrics, get_historical_data
from engine.analysis import get_market_conclusion, format_volume, calculate_rsi, get_rsi_status


st.set_page_config(page_title="Indian Stock Tracker", layout="wide")

# Custom CSS for styling
st.markdown("""<style> .stMetric { background-color: #068; padding: 10px; border-radius: 10px; } </style>""", unsafe_allow_html=True)

# --- MARKET TIME CHECKER ---
def is_market_open():
    """Checks if the current time is within Indian Market Hours (Mon-Fri, 9:15 AM - 3:30 PM)"""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    
    # 1. Check if it's the weekend (5 = Saturday, 6 = Sunday)
    if now.weekday() >= 5:
        return False
        
    # 2. Check the time window (9:15 AM to 3:30 PM)
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    if market_open <= now <= market_close:
        return True
    return False

# Getting current status
market_status = is_market_open()

# --- HEADER WITH DYNAMIC STATUS ---
if market_status:
    st.title("Equity Performance Monitor 🟢 Live")
else:
    st.title("Equity Performance Monitor 🔴 Closed")

# --- SIDEBAR ---
ticker = st.sidebar.text_input("Enter Symbol (e.g. RELIANCE, TCS)", value="RELIANCE")
# auto_refresh = st.sidebar.checkbox("Auto-Refresh Data (15s)", value=True)

if ticker:
    # --- LIVE METRICS ---
    metrics = get_live_metrics(ticker)
    
    if metrics:
        # Fetching 3 Months of data specifically to feed the 14-Day RSI calculator
        data_3m = get_historical_data(ticker, "3M")
        
        # Calculated RSI
        if not data_3m.empty:
            current_rsi = calculate_rsi(data_3m)
            rsi_text = get_rsi_status(current_rsi)
        else:
            current_rsi = 0
            rsi_text = "N/A"

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        
        m1.metric("Live Price", f"₹{metrics['live_price']:.2f}")
        m2.metric("Open", f"₹{metrics['open_price']:.2f}")
        m3.metric("Prev Close", f"₹{metrics['prev_close']:.2f}")
        m4.metric("Day High", f"₹{metrics['day_high']:.2f}")
        m5.metric("Volume", format_volume(metrics['live_volume']))
        m6.metric(f"RSI Status: {rsi_text}", f"{current_rsi:.1f}")
            
        # Conclusion
        concl = get_market_conclusion(metrics)
        st.info(f"**Conclusion:** {concl['sentiment']} ({concl['strength']}) - {concl['message']}")
        
        st.divider()
        
        # --- MULTI-TIMEFRAME CHARTS ---
        t1, t2, t3, t4, t5  = st.tabs(["1 Day", "3 Months", "6 Months", "1 Year", "5 Years"])
        
        def draw_candle(df, title):
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(
                title=title, 
                xaxis_rangeslider_visible=False, 
                height=500,
                dragmode=False,
                xaxis=dict(
                    fixedrange=True,
                    range=[df.index[0], df.index[-1]]), 
                yaxis=dict(fixedrange=True)
            )
            st.plotly_chart(fig, width='stretch')
        
        with t1:
            data_1d = get_historical_data(ticker, "1D")
            if not data_1d.empty: draw_candle(data_1d, "1 Day View")
            
        with t2:
            data_3m = get_historical_data(ticker, "3M")
            if not data_3m.empty: draw_candle(data_3m, "3 Months View")
            
        with t3:
            data_6m = get_historical_data(ticker, "6M")
            if not data_6m.empty: draw_candle(data_6m, "6 Months View")
            
        with t4:
            data_1y = get_historical_data(ticker, "1Y")
            if not data_1y.empty: draw_candle(data_1y, "1 Year View")
            
        with t5:
            data_5y = get_historical_data(ticker, "5Y")
            if not data_5y.empty: draw_candle(data_5y, "5 Years View")

        # --- REFRESH LOGIC ---
        # if auto_refresh:
            if market_status:
                time.sleep(15)
                st.rerun()
            else:
                st.sidebar.warning(" Market Closed ")
    else:
        st.error("No data found for this ticker. Please check the symbol and try again.")   