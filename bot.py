import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    CallbackContext
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🟢 START COMMAND
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("BTC 5 min", callback_data="btc_5")],
        [InlineKeyboardButton("BTC 10 min", callback_data="btc_10")],
        [InlineKeyboardButton("BTC 15 min", callback_data="btc_15")],
        [InlineKeyboardButton("Probo Style Question", callback_data="probo")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to Probo Predictor Bot!", reply_markup=reply_markup)

# 🔁 BUTTON HANDLER
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "btc_5":
        query.message.reply_text("⚡ Predicting BTC price for next 5 minutes...")
    elif query.data == "btc_10":
        query.message.reply_text("⚡ Predicting BTC price for next 10 minutes...")
    elif query.data == "btc_15":
        query.message.reply_text("⚡ Predicting BTC price for next 15 minutes...")
    elif query.data == "probo":
        query.message.reply_text("🧠 Send your Probo-style question (e.g. Will BTC cross 68k tonight?)")

# 🧠 PROBO QUESTION HANDLER
def handle_probo_question(update: Update, context: CallbackContext):
    question = update.message.text
    reply = (
        f"🤖 Prediction for: *{question}*\n\n"
        f"📉 Direction: DOWN\n"
        f"📊 Confidence: 74%\n"
        f"📈 RSI: 62"
    )
    update.message.reply_text(reply, parse_mode="Markdown")

# ❓ UNKNOWN COMMAND HANDLER
def unknown_command(update: Update, context: CallbackContext):
    update.message.reply_text("❓ Unknown command. Please use /start to see options.")

# ⚠️ ERROR HANDLER
def error(update: Update, context: CallbackContext):
    logger.warning(f"⚠️ Update {update} caused error: {context.error}")

# 🚀 MAIN FUNCTION
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))  # reuse start for help
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_probo_question))
    dp.add_handler(MessageHandler(Filters.command, unknown_command))
    dp.add_error_handler(error)

    logger.info("✅ Bot is running (v13.7)...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
