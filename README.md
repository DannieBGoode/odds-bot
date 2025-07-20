# Odds Bot MVP

A simple Telegram bot that lets users browse sports odds using the-odds-api and Telegram buttons.

## Features
- Telegram button navigation
- Choose sport, event, and odds
- Confirmation of user selection

## Setup
1. Clone this repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with:
   ```env
   TELEGRAM_TOKEN=your-telegram-bot-token-here
   ODDS_API_KEY=your-odds-api-key-here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Notes
- Get your Telegram bot token from @BotFather
- Get your odds API key from https://the-odds-api.com/ 