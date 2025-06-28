import os
import logging
import requests
import pandas as pd
import pandas_ta as ta
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler
)

# Load environment variables
load_dotenv("key.env")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Fetch historical Binance data
def fetch_binance_data(interval='1m', limit=100):
    url = f'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval={interval}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'num_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    return df

# Calculate RSI and generate prediction
def generate_prediction(interval_minutes):
    interval_map = {5: '5m', 10: '10m', 15: '15m'}
    interval = interval_map.get(interval_minutes, '5m')

    df = fetch_binance_data(interval=interval, limit=100)
    df['rsi'] = ta.rsi(df['close'], length=14)

    latest_rsi = df['rsi'].iloc[-1]
    current_price = df['close'].iloc[-1]

    if latest_rsi < 30:
        direction = "🟢 Likely to go **UP** (Oversold)"
        confidence = 80
    elif latest_rsi > 70:
        direction = "🔴 Likely to go **DOWN** (Overbought)"
        confidence = 80
    else:
        direction = "🟡 Might stay sideways or slight move"
        confidence = 60

    return f"""
📊 *BTC {interval_minutes}m Prediction*
Price: `${current_price:,.2f}`
RSI: `{latest_rsi:.2f}`
Direction: {direction}
Confidence: {confidence}%
""".strip()

# For /probo questions
def probo_response(question):
    df = fetch_binance_data(interval='1m', limit=100)
    df['rsi'] = ta.rsi(df['close'], length=14)
    latest_rsi = df['rsi'].iloc[-1]
    price = df['close'].iloc[-1]

    if latest_rsi < 30:
        movement = "UP"
        confidence = 80
    elif latest_rsi > 70:
        movement = "DOWN"
        confidence = 80
    else:
        movement = "FLAT"
        confidence = 60

    return f"""
🤖 *Probo Prediction Engine*
Q: {question}

📈 Current BTC Price: `${price:,.2f}`
📊 RSI: `{latest_rsi:.2f}`

Prediction: `{movement}`
Confidence: `{confidence}%`
""".strip()

# Telegram Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC 5m", callback_data='btc_5')],
        [InlineKeyboardButton("BTC 10m", callback_data='btc_10')],
        [InlineKeyboardButton("BTC 15m", callback_data='btc_15')],
        [InlineKeyboardButton("Ask Probo", callback_data='probo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🚀 Choose an option:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("btc_"):
        mins = int(query.data.split("_")[1])
        prediction = generate_prediction(mins)
        await query.edit_message_text(prediction, parse_mode='Markdown')
    elif query.data == "probo":
        await query.edit_message_text("📝 Send your Probo-style question.\nE.g., _Will BTC cross 68k tonight?_")

# When user types /probo or sends probo question
async def probo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("❓ Please enter a question. E.g.:\n`/probo Will BTC cross 68k tonight?`", parse_mode='Markdown')
        return

    answer = probo_response(question)
    await update.message.reply_text(answer, parse_mode='Markdown')

# Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CommandHandler("probo", probo_handler))

    print("✅ Bot is running...")
    app.run_polling()