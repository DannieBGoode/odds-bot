from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from texts import TEXTS
from datetime import datetime

PAGE_SIZE = 5

def format_bet_row(bet):
    # Example: '✅ 2024-06-01 Chelsea vs Arsenal Win +100 EUR'
    date = bet.get("date", "2024-06-01")
    event = bet["event"]
    outcome = bet["outcome"]
    amount = bet["amount"]
    pl = bet["pl"]
    if bet["result"] == "win":
        emoji = "✅"
        pl_str = f"+{pl} EUR"
    elif bet["result"] == "loss":
        emoji = "❌"
        pl_str = f"-{abs(pl)} EUR"
    else:
        emoji = "➖"
        pl_str = "0 EUR"
    return f"{emoji} {date} {event} {outcome} {pl_str}"

def format_bet_detail(bet):
    date = bet.get("date_time", bet.get("date", "2024-06-01 12:00"))
    event = bet["event"]
    outcome = bet["outcome"]
    odds = bet["odds"]
    amount = bet["amount"]
    if bet["result"] == "win":
        result = TEXTS["bet_win"]
        pl = TEXTS["bet_profit"].format(amount=bet["pl"])
    elif bet["result"] == "loss":
        result = TEXTS["bet_loss"]
        pl = TEXTS["bet_loss_amt"].format(amount=abs(bet["pl"]))
    else:
        result = TEXTS["bet_push"]
        pl = "0 EUR"
    return (
        f"{TEXTS['bet_detail_date'].format(date=date)}\n"
        f"{TEXTS['bet_detail_event'].format(event=event)}\n"
        f"{TEXTS['bet_detail_outcome'].format(outcome=outcome)}\n"
        f"{TEXTS['bet_detail_odds'].format(odds=odds)}\n"
        f"{TEXTS['bet_detail_amount'].format(amount=amount)}\n"
        f"{TEXTS['bet_detail_result'].format(result=result, pl=pl)}"
    )

async def show_bet_history(query, context, safe_edit):
    # Placeholder data for past bets (add 'date' and 'date_time')
    bet_history = context.user_data.get("bet_history", [
        {"id": "1", "date": "2024-06-01", "date_time": "2024-06-01 18:00", "event": "Chelsea vs Arsenal", "outcome": "Home Win", "odds": 2.10, "amount": 100, "result": "win", "pl": 110},
        {"id": "2", "date": "2024-05-30", "date_time": "2024-05-30 21:00", "event": "Real Madrid vs Barca", "outcome": "Draw", "odds": 3.20, "amount": 50, "result": "loss", "pl": -50},
        {"id": "3", "date": "2024-05-28", "date_time": "2024-05-28 20:00", "event": "Inter vs Milan", "outcome": "Away Win", "odds": 2.80, "amount": 75, "result": "push", "pl": 0},
        {"id": "4", "date": "2024-05-25", "date_time": "2024-05-25 19:00", "event": "Bayern vs Dortmund", "outcome": "Home Win", "odds": 1.90, "amount": 120, "result": "win", "pl": 108},
        {"id": "5", "date": "2024-05-22", "date_time": "2024-05-22 17:00", "event": "PSG vs Lyon", "outcome": "Away Win", "odds": 2.50, "amount": 60, "result": "loss", "pl": -60},
        {"id": "6", "date": "2024-05-20", "date_time": "2024-05-20 16:00", "event": "Juventus vs Napoli", "outcome": "Draw", "odds": 3.00, "amount": 80, "result": "win", "pl": 160},
    ])
    page = int(context.user_data.get("bet_history_page", 0))
    total = len(bet_history)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    bets = bet_history[start:end]
    text = TEXTS["bet_history_title"]
    if not bets:
        text += TEXTS["bet_history_no_bets"]
    keyboard = []
    for bet in bets:
        label = format_bet_row(bet)
        keyboard.append([InlineKeyboardButton(label, callback_data=f"bet_detail|{bet['id']}|{page}")])
    # Pagination
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(TEXTS["bet_history_prev"], callback_data=f"bet_history_page|{page-1}"))
    if end < total:
        nav_row.append(InlineKeyboardButton(TEXTS["bet_history_next"], callback_data=f"bet_history_page|{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data="cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(text, reply_markup=reply_markup)

async def show_bet_detail(query, context, safe_edit, bet_id, page):
    bet_history = context.user_data.get("bet_history", [
        {"id": "1", "date": "2024-06-01", "date_time": "2024-06-01 18:00", "event": "Chelsea vs Arsenal", "outcome": "Home Win", "odds": 2.10, "amount": 100, "result": "win", "pl": 110},
        {"id": "2", "date": "2024-05-30", "date_time": "2024-05-30 21:00", "event": "Real Madrid vs Barca", "outcome": "Draw", "odds": 3.20, "amount": 50, "result": "loss", "pl": -50},
        {"id": "3", "date": "2024-05-28", "date_time": "2024-05-28 20:00", "event": "Inter vs Milan", "outcome": "Away Win", "odds": 2.80, "amount": 75, "result": "push", "pl": 0},
        {"id": "4", "date": "2024-05-25", "date_time": "2024-05-25 19:00", "event": "Bayern vs Dortmund", "outcome": "Home Win", "odds": 1.90, "amount": 120, "result": "win", "pl": 108},
        {"id": "5", "date": "2024-05-22", "date_time": "2024-05-22 17:00", "event": "PSG vs Lyon", "outcome": "Away Win", "odds": 2.50, "amount": 60, "result": "loss", "pl": -60},
        {"id": "6", "date": "2024-05-20", "date_time": "2024-05-20 16:00", "event": "Juventus vs Napoli", "outcome": "Draw", "odds": 3.00, "amount": 80, "result": "win", "pl": 160},
    ])
    bet = next((b for b in bet_history if str(b["id"]) == str(bet_id)), None)
    if not bet:
        await safe_edit(TEXTS["bet_history_no_bets"])
        return
    text = format_bet_detail(bet)
    keyboard = [
        [InlineKeyboardButton(TEXTS["bet_history_back"], callback_data=f"bet_history_page|{page}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(text, reply_markup=reply_markup) 