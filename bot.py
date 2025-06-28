import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import httpx
import pandas as pd
import ta

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC in 5 min", callback_data='btc_5')],
        [InlineKeyboardButton("BTC in 10 min", callback_data='btc_10')],
        [InlineKeyboardButton("BTC in 15 min", callback_data='btc_15')],
        [InlineKeyboardButton("Probo BTC?", callback_data='probo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Choose an option:", reply_markup=reply_markup)

# Button press handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("btc"):
        minutes = int(query.data.split("_")[1])
        response = await predict_btc(minutes)
        await query.edit_message_text(
            text=f"BTC Prediction for {minutes} min:\n{response}",
            parse_mode="Markdown"
        )
    elif query.data == "probo":
        response = await probo_answer()
        await query.edit_message_text(
            text=f"Probo-style Answer:\n{response}",
            parse_mode="Markdown"
        )

# BTC prediction logic
async def predict_btc(minutes: int) -> str:
    try:
        async with httpx.AsyncClient() as client:
            url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
            r = await client.get(url)
            data = r.json()

        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "_", "__", "___", "____", "_____", "______"
        ])
        df["close"] = pd.to_numeric(df["close"])
        rsi = ta.momentum.RSIIndicator(df["close"], window=14).rsi().iloc[-1]

        if rsi < 30:
            movement = "UP"
        elif rsi > 70:
            movement = "DOWN"
        else:
            movement = "SIDEWAYS"

        confidence = round(abs(rsi - 50) / 50 * 100, 2)
        return f"*Price likely to move:* **{movement}**\n*RSI:* {rsi:.2f}\n*Confidence:* {confidence}%"
    except Exception as e:
        return f"Error: {str(e)}"

# Probo-style response
async def probo_answer() -> str:
    return await predict_btc(5)

# Main function
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

# Entry point
if __name__ == "__main__":
    main()
