import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
import httpx
import pandas as pd
import ta

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC in 5 min", callback_data='btc_5')],
        [InlineKeyboardButton("BTC in 10 min", callback_data='btc_10')],
        [InlineKeyboardButton("BTC in 15 min", callback_data='btc_15')],
        [InlineKeyboardButton("Probo BTC?", callback_data='probo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("btc"):
        minutes = int(query.data.split("_")[1])
        response = await predict_btc(minutes)
        await query.edit_message_text(text=f"BTC Prediction for {minutes} min:
{response}")
    elif query.data == "probo":
        response = await probo_answer()
        await query.edit_message_text(text=f"Probo-style Answer:
{response}")

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
        movement = "UP" if rsi < 30 else "DOWN" if rsi > 70 else "SIDEWAYS"
        confidence = round(abs(rsi - 50) / 50 * 100, 2)
        return f"Price is likely to move **{movement}**
RSI: {rsi:.2f}
Confidence: {confidence}%"
    except Exception as e:
        return f"Error: {str(e)}"

async def probo_answer() -> str:
    return await predict_btc(5)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
