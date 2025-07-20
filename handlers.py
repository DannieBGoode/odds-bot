from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import BadRequest
from odds_api import fetch_sports, fetch_events, fetch_odds

async def start_menu(chat, context):
    keyboard = [
        [InlineKeyboardButton("Choose Sport", callback_data="choose_sport")],
        [InlineKeyboardButton("Accepted Bets", callback_data="accepted_bets")],
        [InlineKeyboardButton("Pending Bets", callback_data="pending_bets")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await chat.send_message('Welcome to Odds Bot!\nClick below to get started:', reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_menu(update.effective_chat, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await start_menu(update.effective_chat, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    async def safe_edit(text, reply_markup=None):
        try:
            await query.edit_message_text(text, reply_markup=reply_markup)
        except BadRequest as e:
            if "Message is not modified" in str(e):
                return
            raise
    if query.data == "cancel":
        context.user_data.clear()
        try:
            await query.message.delete()
        except Exception:
            pass
        await start_menu(query.message.chat, context)
        return
    if query.data == "accepted_bets":
        accepted_bets = context.user_data.get("accepted_bets", [
            {"desc": "EPL: Chelsea vs Arsenal, Home Win, 2.10, 100 EUR"},
            {"desc": "La Liga: Real Madrid vs Barca, Draw, 3.20, 50 EUR"},
        ])
        text = "\U0001F4B0 Accepted Bets:\n\n"
        if accepted_bets:
            for bet in accepted_bets:
                text += f"- {bet['desc']}\n"
        else:
            text += "No accepted bets."
        keyboard = [[InlineKeyboardButton("Back", callback_data="cancel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(text, reply_markup=reply_markup)
        return
    if query.data == "pending_bets":
        pending_bets = context.user_data.get("pending_bets", [
            {"desc": "Serie A: Inter vs Milan, Away Win, 2.80, 75 EUR", "id": "1"},
            {"desc": "Bundesliga: Bayern vs Dortmund, Home Win, 1.90, 120 EUR", "id": "2"},
        ])
        text = "\u23F3 Pending Bets:\n\n"
        keyboard = []
        if pending_bets:
            for bet in pending_bets:
                text += f"- {bet['desc']}\n"
                keyboard.append([InlineKeyboardButton(f"Cancel: {bet['desc'][:20]}...", callback_data=f"cancel_pending|{bet['id']}")])
        else:
            text += "No pending bets."
        keyboard.append([InlineKeyboardButton("Back", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(text, reply_markup=reply_markup)
        return
    if query.data.startswith("cancel_pending|"):
        bet_id = query.data.split("|", 1)[1]
        pending_bets = context.user_data.get("pending_bets", [
            {"desc": "Serie A: Inter vs Milan, Away Win, 2.80, 75 EUR", "id": "1"},
            {"desc": "Bundesliga: Bayern vs Dortmund, Home Win, 1.90, 120 EUR", "id": "2"},
        ])
        pending_bets = [b for b in pending_bets if b["id"] != bet_id]
        context.user_data["pending_bets"] = pending_bets
        text = "\u23F3 Pending Bets:\n\n"
        keyboard = []
        if pending_bets:
            for bet in pending_bets:
                text += f"- {bet['desc']}\n"
                keyboard.append([InlineKeyboardButton(f"Cancel: {bet['desc'][:20]}...", callback_data=f"cancel_pending|{bet['id']}")])
        else:
            text += "No pending bets."
        keyboard.append([InlineKeyboardButton("Back", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(text, reply_markup=reply_markup)
        return
    if query.data == "back_to_sports":
        sports = fetch_sports()
        keyboard = [
            [InlineKeyboardButton(s["title"], callback_data=f"sport|{s['key']}")] for s in sports
        ]
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit("Choose a sport:", reply_markup=reply_markup)
        return
    if query.data.startswith("back_to_events|"):
        _, sport_key = query.data.split("|", 1)
        events = fetch_events(sport_key)
        keyboard = [
            [InlineKeyboardButton(f"{e['home_team']} vs {e['away_team']}", callback_data=f"event|{sport_key}|{e['id']}")] for e in events
        ]
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_sports")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit("Choose an event:", reply_markup=reply_markup)
        return
    if query.data == "choose_sport":
        context.user_data.clear()
        sports = fetch_sports()
        if not sports:
            await safe_edit("Sorry, could not load sports right now.")
            return
        keyboard = [
            [InlineKeyboardButton(s["title"], callback_data=f"sport|{s['key']}")] for s in sports
        ]
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit("Choose a sport:", reply_markup=reply_markup)
    elif query.data.startswith("sport|"):
        _, sport_key = query.data.split("|", 1)
        context.user_data["sport_key"] = sport_key
        events = fetch_events(sport_key)
        if not events:
            await safe_edit("Sorry, could not load events for this sport.")
            return
        keyboard = [
            [InlineKeyboardButton(f"{e['home_team']} vs {e['away_team']}", callback_data=f"event|{sport_key}|{e['id']}")] for e in events
        ]
        keyboard.append([InlineKeyboardButton("Back", callback_data="back_to_sports")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit("Choose an event:", reply_markup=reply_markup)
    elif query.data.startswith("event|"):
        _, sport_key, event_id = query.data.split("|", 2)
        context.user_data["sport_key"] = sport_key
        context.user_data["event_id"] = event_id
        odds = fetch_odds(event_id, sport_key)
        if not odds or not odds["outcomes"]:
            await safe_edit("Sorry, could not load odds for this event.")
            return
        keyboard = [
            [InlineKeyboardButton(f"{o['name']} ({o['price']})", callback_data=f"odds|{sport_key}|{event_id}|{i}")] for i, o in enumerate(odds["outcomes"])
        ]
        keyboard.append([InlineKeyboardButton("Back", callback_data=f"back_to_events|{sport_key}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(f"Choose an outcome (Bookmaker: {odds['bookmaker']}):", reply_markup=reply_markup)
    elif query.data.startswith("odds|"):
        _, sport_key, event_id, outcome_idx = query.data.split("|", 3)
        odds = fetch_odds(event_id, sport_key)
        if not odds or not odds["outcomes"]:
            await safe_edit("Sorry, could not load odds for this event.")
            return
        o = odds["outcomes"][int(outcome_idx)]
        context.user_data["bet_selection"] = {
            "sport_key": sport_key,
            "event_id": event_id,
            "outcome": o,
            "odds": o["price"],
            "outcome_name": o["name"]
        }
        context.user_data["awaiting_bet_amount"] = True
        keyboard = [[InlineKeyboardButton("Back", callback_data=f"event|{sport_key}|{event_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(f"You have chosen: {o['name']} at odds {o['price']}\n\nEnter your bet amount in EUR (e.g. 200):", reply_markup=reply_markup)
    else:
        await safe_edit(f"You clicked: {query.data}")

async def bet_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_bet_amount"):
        if update.message.text.strip().lower() == "/back":
            sport_key = context.user_data.get("sport_key")
            event_id = context.user_data.get("event_id")
            odds = fetch_odds(event_id, sport_key)
            if not odds or not odds["outcomes"]:
                await update.message.reply_text("Sorry, could not load odds for this event.")
                return
            keyboard = [
                [InlineKeyboardButton(f"{o['name']} ({o['price']})", callback_data=f"odds|{sport_key}|{event_id}|{i}")] for i, o in enumerate(odds["outcomes"])
            ]
            keyboard.append([InlineKeyboardButton("Back", callback_data=f"back_to_events|{sport_key}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Choose an outcome (Bookmaker: {odds['bookmaker']}):", reply_markup=reply_markup)
            context.user_data["awaiting_bet_amount"] = False
            return
        try:
            amount = float(update.message.text.strip())
            if amount <= 0:
                raise ValueError
        except Exception:
            await update.message.reply_text("Please enter a valid positive number for your bet amount in EUR, or type /back to go back.")
            return
        selection = context.user_data.get("bet_selection", {})
        sport_key = context.user_data.get("sport_key", "?")
        event_id = context.user_data.get("event_id", "?")
        outcome_name = selection.get("outcome_name", "?")
        odds = selection.get("odds", "?")
        # Add to pending bets
        pending_bets = context.user_data.get("pending_bets", [])
        bet_id = str(len(pending_bets) + 1)
        bet_desc = f"{sport_key}: {outcome_name}, Odds: {odds}, Amount: {amount} EUR"
        pending_bets.append({"desc": bet_desc, "id": bet_id})
        context.user_data["pending_bets"] = pending_bets
        try:
            potential_win = float(amount) * float(odds)
            win_str = f"Potential win: {potential_win:.2f} EUR"
        except Exception:
            win_str = ""
        await update.message.reply_text(
            f"Bet placed and pending!\nOutcome: {outcome_name}\nOdds: {odds}\nAmount: {amount} EUR\n{win_str}"
        )
        context.user_data["awaiting_bet_amount"] = False
        context.user_data["bet_selection"] = None
        await start_menu(update.effective_chat, context) 