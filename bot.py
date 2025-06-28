import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Load the .env file
load_dotenv("key.env")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # ✅ Ensure this matches your .env variable name

# --- START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("BTC 5 min", callback_data='/btc_5')],
        [InlineKeyboardButton("BTC 10 min", callback_data='/btc_10')],
        [InlineKeyboardButton("BTC 15 min", callback_data='/btc_15')],
        [InlineKeyboardButton("Ask Probo Style", callback_data='/probo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to Probo Predictor Bot!\nChoose an option:", reply_markup=reply_markup)

# --- BUTTON HANDLER ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == '/btc_5':
        await query.edit_message_text("⏳ Predicting BTC price movement for next 5 minutes...")
        # Integrate BTC prediction logic here
    elif query.data == '/btc_10':
        await query.edit_message_text("⏳ Predicting BTC price movement for next 10 minutes...")
    elif query.data == '/btc_15':
        await query.edit_message_text("⏳ Predicting BTC price movement for next 15 minutes...")
    elif query.data == '/probo':
        await query.edit_message_text("🧠 Ask me a yes/no BTC question like:\nWill BTC cross 68k tonight?")

# --- MESSAGE HANDLER FOR PROBO STYLE QUESTIONS ---
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    if "btc" in user_question.lower():
        # Placeholder logic for now
        await update.message.reply_text(f"🔍 Analyzing your question: {user_question}\nPrediction: Yes\nConfidence: 72%\n📉 RSI: 41.2")
    else:
        await update.message.reply_text("❗Please ask a BTC-related question.")

# --- MAIN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    print("🤖 Bot is running...")
    app.run_polling()
