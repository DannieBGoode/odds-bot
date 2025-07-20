from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from texts import TEXTS

async def show_accepted_bets(query, context, safe_edit):
    accepted_bets = context.user_data.get("accepted_bets", [
        {"desc": "EPL: Chelsea vs Arsenal, Home Win, 2.10, 100 EUR"},
        {"desc": "La Liga: Real Madrid vs Barca, Draw, 3.20, 50 EUR"},
    ])
    text = TEXTS["accepted_bets_title"]
    if accepted_bets:
        for bet in accepted_bets:
            text += f"- {bet['desc']}\n"
    else:
        text += TEXTS["no_accepted_bets"]
    keyboard = [[InlineKeyboardButton(TEXTS["back"], callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(text, reply_markup=reply_markup) 