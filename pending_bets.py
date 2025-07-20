from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from texts import TEXTS

async def show_pending_bets(query, context, safe_edit):
    pending_bets = context.user_data.get("pending_bets", [
        {"desc": "Serie A: Inter vs Milan, Away Win, 2.80, 75 EUR", "id": "1"},
        {"desc": "Bundesliga: Bayern vs Dortmund, Home Win, 1.90, 120 EUR", "id": "2"},
    ])
    text = TEXTS["pending_bets_title"]
    keyboard = []
    if pending_bets:
        for bet in pending_bets:
            text += f"- {bet['desc']}\n"
            keyboard.append([InlineKeyboardButton(TEXTS["cancel_pending"].format(desc=bet['desc'][:20]), callback_data=f"cancel_pending|{bet['id']}")])
    else:
        text += TEXTS["no_pending_bets"]
    keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(text, reply_markup=reply_markup)

async def show_pending_cancel_confirm(query, context, safe_edit, bet_id):
    pending_bets = context.user_data.get("pending_bets", [
        {"desc": "Serie A: Inter vs Milan, Away Win, 2.80, 75 EUR", "id": "1"},
        {"desc": "Bundesliga: Bayern vs Dortmund, Home Win, 1.90, 120 EUR", "id": "2"},
    ])
    bet = next((b for b in pending_bets if b["id"] == bet_id), None)
    if not bet:
        await safe_edit(TEXTS["no_pending_bets"])
        return
    keyboard = [
        [InlineKeyboardButton(TEXTS["yes-cancel"], callback_data=f"cancel_pending_confirm|{bet_id}"),
         InlineKeyboardButton(TEXTS["no"], callback_data="pending_bets")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(f"{TEXTS['confirm_cancel_pending']}\n\n{bet['desc']}", reply_markup=reply_markup)

async def handle_pending_cancel_confirm(query, context, safe_edit, bet_id):
    pending_bets = context.user_data.get("pending_bets", [
        {"desc": "Serie A: Inter vs Milan, Away Win, 2.80, 75 EUR", "id": "1"},
        {"desc": "Bundesliga: Bayern vs Dortmund, Home Win, 1.90, 120 EUR", "id": "2"},
    ])
    pending_bets = [b for b in pending_bets if b["id"] != bet_id]
    context.user_data["pending_bets"] = pending_bets
    text = TEXTS["pending_bets_title"]
    keyboard = []
    if pending_bets:
        for bet in pending_bets:
            text += f"- {bet['desc']}\n"
            keyboard.append([InlineKeyboardButton(TEXTS["cancel_pending"].format(desc=bet['desc'][:20]), callback_data=f"cancel_pending|{bet['id']}")])
    else:
        text += TEXTS["no_pending_bets"]
    keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(text, reply_markup=reply_markup) 