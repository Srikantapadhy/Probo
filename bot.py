import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🟢 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC 5 min", callback_data="btc_5")],
        [InlineKeyboardButton("BTC 10 min", callback_data="btc_10")],
        [InlineKeyboardButton("BTC 15 min", callback_data="btc_15")],
        [InlineKeyboardButton("Probo Style Question", callback_data="probo")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to Probo Predictor Bot!", reply_markup=reply_markup)

# 🔁 BUTTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "btc_5":
        await query.edit_message_text(text="⚡ Predicting BTC price for next 5 minutes...")
        # Call your real function here
    elif query.data == "btc_10":
        await query.edit_message_text(text="⚡ Predicting BTC price for next 10 minutes...")
    elif query.data == "btc_15":
        await query.edit_message_text(text="⚡ Predicting BTC price for next 15 minutes...")
    elif query.data == "probo":
        await query.edit_message_text(text="🧠 Send your Probo-style question (e.g. Will BTC cross 68k tonight?)")

# 🔁 PROBO-STYLE TEXT HANDLER
async def handle_probo_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    # You can add model logic here like calling your RSI + Binance logic
    reply = f"🤖 Prediction for: *{question}*\n\n📉 Direction: DOWN\n📊 Confidence: 74%\n📈 RSI: 62"
    await update.message.reply_markdown(reply)

# MAIN ENTRY
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("probo", handle_probo_question))
    app.add_handler(CommandHandler("btc", button_handler))
    app.add_handler(CommandHandler("btc_5", button_handler))
    app.add_handler(CommandHandler("btc_10", button_handler))
    app.add_handler(CommandHandler("btc_15", button_handler))
    app.add_handler(CommandHandler("help", start))

    # Text input after 'Probo' button
    app.add_handler(
        telegram.ext.MessageHandler(telegram.ext.filters.TEXT & ~telegram.ext.filters.COMMAND, handle_probo_question)
    )

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
