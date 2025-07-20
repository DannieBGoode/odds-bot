from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import BadRequest
from odds_api import fetch_sports, fetch_events, fetch_odds
from texts import TEXTS

async def start_menu(chat, context):
    keyboard = [
        [InlineKeyboardButton(TEXTS["choose_sport"], callback_data="choose_sport")],
        [InlineKeyboardButton(TEXTS["accepted_bets"], callback_data="accepted_bets")],
        [InlineKeyboardButton(TEXTS["pending_bets"], callback_data="pending_bets")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await chat.send_message(TEXTS["welcome"], reply_markup=reply_markup)

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
        text = TEXTS["accepted_bets_title"]
        if accepted_bets:
            for bet in accepted_bets:
                text += f"- {bet['desc']}\n"
        else:
            text += TEXTS["no_accepted_bets"]
        keyboard = [[InlineKeyboardButton(TEXTS["back"], callback_data="cancel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(text, reply_markup=reply_markup)
        return
    if query.data == "pending_bets":
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
        return
    if query.data.startswith("cancel_pending|") and not query.data.startswith("cancel_pending_confirm|"):
        bet_id = query.data.split("|", 1)[1]
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
        return
    if query.data.startswith("cancel_pending_confirm|"):
        bet_id = query.data.split("|", 1)[1]
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
        return
    if query.data == "back_to_sports":
        sports = fetch_sports()
        keyboard = [
            [InlineKeyboardButton(s["title"], callback_data=f"sport|{s['key']}")] for s in sports
        ]
        keyboard.append([InlineKeyboardButton(TEXTS["cancel"], callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(TEXTS["choose_sport"], reply_markup=reply_markup)
        return
    if query.data.startswith("back_to_events|"):
        _, sport_key = query.data.split("|", 1)
        events = fetch_events(sport_key)
        keyboard = [
            [InlineKeyboardButton(f"{e['home_team']} vs {e['away_team']}", callback_data=f"event|{sport_key}|{e['id']}")] for e in events
        ]
        keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data="back_to_sports")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(TEXTS["choose_event"], reply_markup=reply_markup)
        return
    if query.data == "choose_sport":
        context.user_data.clear()
        sports = fetch_sports()
        if not sports:
            await safe_edit(TEXTS["error_sports"])
            return
        keyboard = [
            [InlineKeyboardButton(s["title"], callback_data=f"sport|{s['key']}")] for s in sports
        ]
        keyboard.append([InlineKeyboardButton(TEXTS["cancel"], callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(TEXTS["choose_sport"], reply_markup=reply_markup)
    elif query.data.startswith("sport|"):
        _, sport_key = query.data.split("|", 1)
        context.user_data["sport_key"] = sport_key
        events = fetch_events(sport_key)
        if not events:
            await safe_edit(TEXTS["error_events"])
            return
        keyboard = [
            [InlineKeyboardButton(f"{e['home_team']} vs {e['away_team']}", callback_data=f"event|{sport_key}|{e['id']}")] for e in events
        ]
        keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data="back_to_sports")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(TEXTS["choose_event"], reply_markup=reply_markup)
    elif query.data.startswith("event|"):
        _, sport_key, event_id = query.data.split("|", 2)
        context.user_data["sport_key"] = sport_key
        context.user_data["event_id"] = event_id
        odds = fetch_odds(event_id, sport_key)
        if not odds or not odds["outcomes"]:
            await safe_edit(TEXTS["error_odds"])
            return
        keyboard = [
            [InlineKeyboardButton(f"{o['name']} ({o['price']})", callback_data=f"odds|{sport_key}|{event_id}|{i}")] for i, o in enumerate(odds["outcomes"])
        ]
        keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data=f"back_to_events|{sport_key}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(TEXTS["choose_outcome"].format(bookmaker=odds['bookmaker']), reply_markup=reply_markup)
    elif query.data.startswith("odds|"):
        _, sport_key, event_id, outcome_idx = query.data.split("|", 3)
        odds = fetch_odds(event_id, sport_key)
        if not odds or not odds["outcomes"]:
            await safe_edit(TEXTS["error_odds"])
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
        keyboard = [[InlineKeyboardButton(TEXTS["back"], callback_data=f"event|{sport_key}|{event_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await safe_edit(TEXTS["chosen_outcome"].format(outcome=o['name'], odds=o['price']), reply_markup=reply_markup)
    elif query.data == "confirm_bet":
        draft = context.user_data.get('pending_bet_draft')
        if not draft:
            await safe_edit(TEXTS["error_odds"])
            return
        sport_key = draft['sport_key']
        event_id = draft['event_id']
        outcome_name = draft['outcome_name']
        odds = draft['odds']
        amount = draft['amount']
        events = fetch_events(sport_key)
        event = next((e for e in events if str(e.get('id')) == str(event_id)), None)
        if event:
            event_name = f"{event.get('home_team', '?')} vs {event.get('away_team', '?')}"
        else:
            event_name = f"{sport_key}"
        pending_bets = context.user_data.get("pending_bets", [])
        bet_id = str(len(pending_bets) + 1)
        bet_desc = f"{event_name}: {outcome_name}, Odds: {odds}, Amount: {amount} EUR"
        pending_bets.append({"desc": bet_desc, "id": bet_id})
        context.user_data["pending_bets"] = pending_bets
        context.user_data["pending_bet_draft"] = None
        await safe_edit(TEXTS["bet_confirmed"])
        await start_menu(query.message.chat, context)
        return
    elif query.data == "edit_bet":
        draft = context.user_data.get('pending_bet_draft')
        if draft:
            sport_key = draft['sport_key']
            event_id = draft['event_id']
            odds = fetch_odds(event_id, sport_key)
            if not odds or not odds["outcomes"]:
                await safe_edit(TEXTS["error_odds"])
                return
            keyboard = [[InlineKeyboardButton(TEXTS["back"], callback_data=f"event|{sport_key}|{event_id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.user_data["awaiting_bet_amount"] = True
            await safe_edit(TEXTS["chosen_outcome"].format(outcome=draft['outcome_name'], odds=draft['odds']), reply_markup=reply_markup)
        return
    else:
        await safe_edit(TEXTS["clicked"].format(data=query.data))

async def bet_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_bet_amount"):
        if update.message.text.strip().lower() == "/back":
            sport_key = context.user_data.get("sport_key")
            event_id = context.user_data.get("event_id")
            odds = fetch_odds(event_id, sport_key)
            if not odds or not odds["outcomes"]:
                await update.message.reply_text(TEXTS["error_odds"])
                return
            keyboard = [
                [InlineKeyboardButton(f"{o['name']} ({o['price']})", callback_data=f"odds|{sport_key}|{event_id}|{i}")] for i, o in enumerate(odds["outcomes"])
            ]
            keyboard.append([InlineKeyboardButton(TEXTS["back"], callback_data=f"back_to_events|{sport_key}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(TEXTS["choose_outcome"].format(bookmaker=odds['bookmaker']), reply_markup=reply_markup)
            context.user_data["awaiting_bet_amount"] = False
            return
        try:
            amount = float(update.message.text.strip())
            if amount <= 0:
                raise ValueError
        except Exception:
            await update.message.reply_text(TEXTS["invalid_amount"])
            return
        selection = context.user_data.get("bet_selection", {})
        sport_key = context.user_data.get("sport_key", "?")
        event_id = context.user_data.get("event_id", "?")
        outcome_name = selection.get("outcome_name", "?")
        odds = selection.get("odds", "?")
        # Show confirmation window before placing bet
        context.user_data['pending_bet_draft'] = {
            'sport_key': sport_key,
            'event_id': event_id,
            'outcome_name': outcome_name,
            'odds': odds,
            'amount': amount
        }
        # Fetch event details for human-readable name
        events = fetch_events(sport_key)
        event = next((e for e in events if str(e.get('id')) == str(event_id)), None)
        if event:
            event_name = f"{event.get('home_team', '?')} vs {event.get('away_team', '?')}"
        else:
            event_name = f"{sport_key}"
        keyboard = [
            [InlineKeyboardButton(TEXTS["confirm_bet_button"], callback_data="confirm_bet")],
            [InlineKeyboardButton(TEXTS["edit_bet_button"], callback_data="edit_bet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            TEXTS["confirm_bet"].format(event=event_name, outcome=outcome_name, odds=odds, amount=amount),
            reply_markup=reply_markup
        )
        return
    # In button_handler, handle confirm_bet and edit_bet callback_data
    if query.data == "confirm_bet":
        draft = context.user_data.get('pending_bet_draft')
        if not draft:
            await safe_edit(TEXTS["error_odds"])
            return
        sport_key = draft['sport_key']
        event_id = draft['event_id']
        outcome_name = draft['outcome_name']
        odds = draft['odds']
        amount = draft['amount']
        events = fetch_events(sport_key)
        event = next((e for e in events if str(e.get('id')) == str(event_id)), None)
        if event:
            event_name = f"{event.get('home_team', '?')} vs {event.get('away_team', '?')}"
        else:
            event_name = f"{sport_key}"
        pending_bets = context.user_data.get("pending_bets", [])
        bet_id = str(len(pending_bets) + 1)
        bet_desc = f"{event_name}: {outcome_name}, Odds: {odds}, Amount: {amount} EUR"
        pending_bets.append({"desc": bet_desc, "id": bet_id})
        context.user_data["pending_bets"] = pending_bets
        context.user_data["pending_bet_draft"] = None
        await safe_edit(TEXTS["bet_confirmed"])
        await start_menu(query.message.chat, context)
        return
    if query.data == "edit_bet":
        context.user_data["awaiting_bet_amount"] = True
        await safe_edit(TEXTS["invalid_amount"])
        return 