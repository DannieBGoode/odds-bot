import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers import start, button_handler, bet_amount_handler, cancel

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bet_amount_handler))
    print("Bot is running...")
    app.run_polling() 