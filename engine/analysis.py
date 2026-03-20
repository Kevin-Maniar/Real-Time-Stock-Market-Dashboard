import pandas as pd

def calculate_change(current, previous):
    """Logic to calculate price change and percentage."""
    if previous == 0:
        return 0, 0
    change = current - previous
    percent_change = (change / previous) * 100
    return change, percent_change

def get_market_conclusion(metrics):
    live = metrics['live_price']
    prev = metrics['prev_close']
    high = metrics['day_high']
    low = metrics['day_low'] 
    
    change_pct = ((live - prev) / prev) * 100 if prev > 0 else 0

    if live > prev:
        sentiment = "Bullish"
        color = "green" 
        msg = f"Stock is up {change_pct:.2f}% from yesterday."
    else:
        sentiment = "Bearish"
        color = "red"
        msg = f"Stock is down {abs(change_pct):.2f}% from yesterday." 
    
    if live >= high * 0.995:
        strength = "Strong Momentum - Near Day High"
    elif live <= low * 1.005:
        strength = "Weak Momentum - Near Day Low"
    else:
        strength = "Consolidating within Day Range"
    return {
        "sentiment": sentiment,
        "strength": strength,
        "message": msg,
        "color": color
    }

def format_volume(vol):
    if vol >= 10000000: return f"{vol/10000000:.2f} Cr"
    if vol >= 100000: return f"{vol/100000:.2f} L"
    return f"{vol:,}"

def calculate_rsi(df, periods=14):
    """Calculates the 14-Day Relative Strength Index (RSI)."""
    # Get the daily price changes
    close_delta = df['Close'].diff()
    
    # Separate the winning days (up) from the losing days (down)
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    
    # Calculate the exponential moving average of gains and losses
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    
    # RSI math
    rs = ma_up / ma_down
    rsi = 100 - (100 / (1 + rs))
    
    # It will Return the very last (most current) RSI number
    return rsi.iloc[-1]

def get_rsi_status(rsi_value):
    """Translates the number into Overbought/Oversold text."""
    if pd.isna(rsi_value):
        return "N/A"
    elif rsi_value >= 70:
        return "Overbought 🔴"
    elif rsi_value <= 30:
        return "Oversold 🟢"
    else:
        return "Neutral 🟡"