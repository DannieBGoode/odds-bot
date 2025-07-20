from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from texts import TEXTS

async def show_bet_history(query, context, safe_edit):
    # Placeholder data for past bets
    bet_history = context.user_data.get("bet_history", [
        {"event": "Chelsea vs Arsenal", "outcome": "Home Win", "odds": 2.10, "amount": 100, "result": "win", "pl": 110},
        {"event": "Real Madrid vs Barca", "outcome": "Draw", "odds": 3.20, "amount": 50, "result": "loss", "pl": -50},
        {"event": "Inter vs Milan", "outcome": "Away Win", "odds": 2.80, "amount": 75, "result": "push", "pl": 0},
    ])
    text = TEXTS["bet_history_title"]
    if bet_history:
        for bet in bet_history:
            if bet["result"] == "win":
                result = TEXTS["bet_win"]
                pl = TEXTS["bet_profit"].format(amount=bet["pl"])
            elif bet["result"] == "loss":
                result = TEXTS["bet_loss"]
                pl = TEXTS["bet_loss_amt"].format(amount=abs(bet["pl"]))
            else:
                result = TEXTS["bet_push"]
                pl = "0 EUR"
            text += f"\nEvent: {bet['event']}\nOutcome: {bet['outcome']}\nOdds: {bet['odds']}\nAmount: {bet['amount']} EUR\nResult: {result}  {pl}\n"
    else:
        text += TEXTS["bet_history_no_bets"]
    keyboard = [[InlineKeyboardButton(TEXTS["back"], callback_data="cancel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(text, reply_markup=reply_markup) 