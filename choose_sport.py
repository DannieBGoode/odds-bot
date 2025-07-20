from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from texts import TEXTS
from odds_api import fetch_sports, fetch_events, fetch_odds

async def show_sports_menu(query, context, safe_edit):
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

async def show_events_menu(query, context, safe_edit, sport_key):
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

async def show_odds_menu(query, context, safe_edit, sport_key, event_id):
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

async def show_bet_amount_input(query, context, safe_edit, sport_key, event_id, outcome_idx):
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

async def show_bet_confirmation(query, context, safe_edit):
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
    keyboard = [
        [InlineKeyboardButton(TEXTS["confirm_bet_button"], callback_data="confirm_bet")],
        [InlineKeyboardButton(TEXTS["edit_bet_button"], callback_data="edit_bet")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await safe_edit(
        TEXTS["confirm_bet"].format(event=event_name, outcome=outcome_name, odds=odds, amount=amount),
        reply_markup=reply_markup
    )

async def handle_bet_edit(query, context, safe_edit):
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

async def handle_bet_amount_input(update, context):
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

async def handle_confirm_bet(query, context, safe_edit, start_menu):
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