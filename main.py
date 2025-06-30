import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from prediction import handle_probo_question

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

user_context = {}

def start(update, context):
    update.message.reply_text("Welcome to Probo Predictor Bot! Use /btc_5, /btc_10, /btc_15 or /probo")

def btc(update, context, interval):
    from prediction import predict_btc_direction
    result = predict_btc_direction(interval)
    update.message.reply_text(result)

def btc_5(update, context): btc(update, context, '1m')
def btc_10(update, context): btc(update, context, '3m')
def btc_15(update, context): btc(update, context, '5m')

def probo(update, context):
    update.message.reply_text("Send your BTC question (e.g., 'Will BTC cross 68000 in 15 mins?')")
    user_context[update.message.chat_id] = "awaiting_probo"

def handle_text(update, context):
    if user_context.get(update.message.chat_id) == "awaiting_probo":
        result = handle_probo_question(update.message.text)
        update.message.reply_text(result)
        user_context[update.message.chat_id] = None

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("btc_5", btc_5))
    dp.add_handler(CommandHandler("btc_10", btc_10))
    dp.add_handler(CommandHandler("btc_15", btc_15))
    dp.add_handler(CommandHandler("probo", probo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()