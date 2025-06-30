import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv

# Load API keys
load_dotenv("key.env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("BTC 5min", callback_data='btc_5')],
        [InlineKeyboardButton("BTC 10min", callback_data='btc_10')],
        [InlineKeyboardButton("BTC 15min", callback_data='btc_15')],
        [InlineKeyboardButton("Probo Question", callback_data='probo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to Probo Predictor Bot! Choose a prediction option:", reply_markup=reply_markup)

def handle_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    if data.startswith("btc_"):
        interval = data.split("_")[1]
        result = get_btc_prediction(interval)
        query.edit_message_text(text=result)
    elif data == "probo":
        query.edit_message_text(text="Please ask your question like:\n\nWill BTC cross 68k tonight?")

def get_btc_prediction(interval):
    # Dummy logic — Replace with actual RSI/TA logic
    interval = int(interval)
    return f"📈 BTC {interval}-minute prediction:\nDirection: UP\n% Change: 0.35%\nConfidence: 78%\n(RSI below 30 — likely rebound)"

def handle_probo(update: Update, context: CallbackContext):
    question = " ".join(context.args)
    if not question:
        update.message.reply_text("Please enter a question after /probo like:\n/probo Will BTC cross 68k tonight?")
        return
    # Dummy response — Add NLP + TA logic here
    update.message.reply_text(f"🤖 Your question: *{question}*\n\nPrediction: YES\nDirection: Up\nConfidence: 72%", parse_mode='Markdown')

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("probo", handle_probo))
    dp.add_handler(CallbackQueryHandler(handle_button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
