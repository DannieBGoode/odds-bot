from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.error import BadRequest
from odds_api import fetch_sports, fetch_events, fetch_odds
from texts import TEXTS
from bet_history import show_bet_history, show_bet_detail
from pending_bets import show_pending_bets, show_pending_cancel_confirm, handle_pending_cancel_confirm
from accepted_bets import show_accepted_bets
from choose_sport import show_sports_menu, show_events_menu, show_odds_menu, show_bet_amount_input, handle_bet_edit, show_bet_confirmation, handle_bet_amount_input, handle_confirm_bet

async def start_menu(chat, context):
    keyboard = [
        [InlineKeyboardButton(TEXTS["choose_sport"], callback_data="choose_sport")],
        [InlineKeyboardButton(TEXTS["accepted_bets"], callback_data="accepted_bets")],
        [InlineKeyboardButton(TEXTS["pending_bets"], callback_data="pending_bets")],
        [InlineKeyboardButton(TEXTS["bet_history"], callback_data="bet_history")],
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
        await show_accepted_bets(query, context, safe_edit)
        return
    if query.data == "pending_bets":
        await show_pending_bets(query, context, safe_edit)
        return
    if query.data.startswith("cancel_pending|") and not query.data.startswith("cancel_pending_confirm|"):
        bet_id = query.data.split("|", 1)[1]
        await show_pending_cancel_confirm(query, context, safe_edit, bet_id)
        return
    if query.data.startswith("cancel_pending_confirm|"):
        bet_id = query.data.split("|", 1)[1]
        await handle_pending_cancel_confirm(query, context, safe_edit, bet_id)
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
        await show_sports_menu(query, context, safe_edit)
        return
    elif query.data.startswith("sport|"):
        _, sport_key = query.data.split("|", 1)
        await show_events_menu(query, context, safe_edit, sport_key)
        return
    elif query.data.startswith("event|"):
        _, sport_key, event_id = query.data.split("|", 2)
        await show_odds_menu(query, context, safe_edit, sport_key, event_id)
        return
    elif query.data.startswith("odds|"):
        _, sport_key, event_id, outcome_idx = query.data.split("|", 3)
        await show_bet_amount_input(query, context, safe_edit, sport_key, event_id, outcome_idx)
        return
    elif query.data == "confirm_bet":
        await handle_confirm_bet(query, context, safe_edit, start_menu)
        return
    elif query.data == "edit_bet":
        await handle_bet_edit(query, context, safe_edit)
        return
    if query.data == "bet_history":
        context.user_data["bet_history_page"] = 0
        await show_bet_history(query, context, safe_edit)
        return
    if query.data.startswith("bet_history_page|"):
        page = int(query.data.split("|", 1)[1])
        context.user_data["bet_history_page"] = page
        await show_bet_history(query, context, safe_edit)
        return
    if query.data.startswith("bet_detail|"):
        _, bet_id, page = query.data.split("|", 2)
        await show_bet_detail(query, context, safe_edit, bet_id, page)
        return
    else:
        await safe_edit(TEXTS["clicked"].format(data=query.data)) 