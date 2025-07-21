import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers import start, button_handler, cancel
from choose_sport import handle_bet_amount_input
from threading import Thread
from oddsbot.wake_up_server import run_flask

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bet_amount_input))
    print("Bot is running...")
    app.run_polling() 