import requests
import pandas as pd
import ta
import re

def get_btc_data(interval='1m', limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume','_','_','_','_','_','_'])
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df

def calculate_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd_diff()
    df['ema5'] = df['close'].ewm(span=5).mean()
    df['ema20'] = df['close'].ewm(span=20).mean()
    return df

def generate_prediction(df):
    latest = df.iloc[-1]
    score = 0
    reasons = []

    if latest['rsi'] < 30:
        score += 1
        reasons.append("RSI < 30 (Oversold)")
    if latest['macd'] > 0:
        score += 1
        reasons.append("MACD Bullish")
    if latest['ema5'] > latest['ema20']:
        score += 1
        reasons.append("EMA5 > EMA20")
    if df['volume'].iloc[-1] > df['volume'].mean():
        score += 1
        reasons.append("Volume Spike")

    confidence = (score / 4) * 100
    direction = "UP" if score >= 3 else "DOWN"
    suggestion = "YES" if confidence >= 80 else "NO"

    return {
        "direction": direction,
        "confidence": round(confidence, 1),
        "reasons": reasons,
        "suggestion": suggestion
    }

def predict_btc_direction(interval='1m'):
    df = get_btc_data(interval)
    df = calculate_indicators(df)
    result = generate_prediction(df)
    msg = f"""
Direction: {result['direction']}
Confidence: {result['confidence']}%
Reason:
- {'\n- '.join(result['reasons'])}
Timeframe: {interval.replace('m','')} minutes
Suggestion: {result['suggestion']}
"""
    return msg

def handle_probo_question(question):
    price_match = re.search(r"\b(\d{4,6})\b", question)
    time_match = re.search(r"(\d{1,2})\s*min", question.lower())

    target = float(price_match.group(1)) if price_match else None
    timeframe = int(time_match.group(1)) if time_match else 15

    df = get_btc_data('1m')
    df = calculate_indicators(df)
    result = generate_prediction(df)
    current_price = df['close'].iloc[-1]

    msg = f"""
Probo Prediction
Answer: {result['suggestion']}
Direction: {result['direction']}
Confidence: {result['confidence']}%
Reason:
- {'\n- '.join(result['reasons'])}
Timeframe: {timeframe} minutes
Current Price: {current_price} | Target: {target if target else "Not detected"}
"""
    return msg