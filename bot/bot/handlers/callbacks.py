"""
Central callback query handler.

Every inline button in the bot sends a callback_data string.  This module
dispatches those strings to the right async function.  The routing is
deliberately simple — a series of startswith() checks — which is easy to
read and extend without a full FSM.
"""
from telegram import Update
from telegram.ext import ContextTypes

from bot import api_client
from bot.keyboards import (
    CB_BACK_HOME, CB_HIGHLIGHTS, CB_LIVE, CB_STANDINGS, CB_TODAY, CB_TOURNEY, CB_UPCOMING,
    cb_match, home_keyboard, match_detail_keyboard, match_detail_text,
    match_list_keyboard, standings_text, streams_keyboard, tournaments_keyboard,
)

# ── helpers ────────────────────────────────────────────────────────────────

async def _edit(update: Update, text: str, markup=None) -> None:
    msg = update.callback_query.message
    await msg.edit_text(text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)


async def _answer(update: Update, text: str = "") -> None:
    await update.callback_query.answer(text)


# ── dispatcher ────────────────────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data: str = query.data or ""
    user = update.effective_user

    try:
        if data == CB_BACK_HOME:
            await _edit(update, "🏠 <b>Main Menu</b>", home_keyboard())

        elif data == CB_TODAY:
            await _handle_match_list(update, await api_client.get_today_matches(), "📅 Today's Matches")

        elif data == CB_UPCOMING:
            await _handle_match_list(update, await api_client.get_upcoming_matches(), "⏭ Upcoming Matches")

        elif data == CB_LIVE:
            await _handle_match_list(update, await api_client.get_live_matches(), "🔴 Live Now")

        elif data == CB_TOURNEY:
            tournaments = await api_client.get_tournaments()
            if not tournaments:
                await _edit(update, "No active tournaments at the moment.", _back_kb())
            else:
                await _edit(update, "🏆 <b>Tournaments</b>\n\nSelect a tournament to see standings:",
                            tournaments_keyboard(tournaments))

        elif data == CB_STANDINGS:
            tournaments = await api_client.get_tournaments()
            if not tournaments:
                await _edit(update, "No active tournaments.", _back_kb())
            else:
                await _edit(update, "📊 Select a tournament:", tournaments_keyboard(tournaments))

        elif data == CB_HIGHLIGHTS:
            await _edit(update, "🎬 <b>Highlights</b>\n\nPick a match from Today or Recent to see its highlight button.", _back_kb())

        elif data.startswith("match:"):
            match_id = int(data.split(":")[1])
            await _handle_match_detail(update, match_id, user.id if user else 0)

        elif data.startswith("streams:"):
            match_id = int(data.split(":")[1])
            await _handle_streams(update, match_id)

        elif data.startswith("notify:"):
            match_id = int(data.split(":")[1])
            if user:
                await api_client.subscribe_notification(user.id, match_id)
                await query.answer("🔔 You'll be notified before this match!", show_alert=True)
                # Refresh the detail view with updated button
                await _handle_match_detail(update, match_id, user.id)

        elif data.startswith("unnotify:"):
            match_id = int(data.split(":")[1])
            if user:
                await api_client.unsubscribe_notification(user.id, match_id)
                await query.answer("🔕 Notification cancelled.", show_alert=True)
                await _handle_match_detail(update, match_id, user.id)

        elif data.startswith("highlight:"):
            match_id = int(data.split(":")[1])
            await _handle_highlight(update, match_id)

        elif data.startswith("standings:"):
            tournament_id = int(data.split(":")[1])
            await _handle_standings(update, tournament_id)

    except RuntimeError as exc:
        await _edit(update, f"⚠️ Something went wrong: {exc}\n\nPlease try again.", _back_kb())


# ── sub-handlers ──────────────────────────────────────────────────────────

def _back_kb():
    from bot.keyboards import back_home_button, InlineKeyboardMarkup  # local to avoid circular
    from telegram import InlineKeyboardMarkup as IKM
    return IKM([back_home_button()])


async def _handle_match_list(update: Update, matches: list, title: str) -> None:
    if not matches:
        from telegram import InlineKeyboardMarkup
        from bot.keyboards import back_home_button
        await _edit(update, f"{title}\n\nNo matches found.", InlineKeyboardMarkup([back_home_button()]))
        return
    await _edit(update, f"<b>{title}</b>", match_list_keyboard(matches, CB_BACK_HOME))


async def _handle_match_detail(update: Update, match_id: int, telegram_id: int) -> None:
    match = await api_client.get_match(match_id)
    subscribed = await api_client.subscription_status(telegram_id, match_id) if telegram_id else False
    text = match_detail_text(match)
    kb = match_detail_keyboard(match, subscribed)
    await _edit(update, text, kb)


async def _handle_streams(update: Update, match_id: int) -> None:
    streams = await api_client.get_streams(match_id)
    if not streams:
        await update.callback_query.answer("⚠️ No streams available yet.", show_alert=True)
        return
    await _edit(update, "📺 <b>Watch Now</b>\n\nSelect language & quality:", streams_keyboard(streams, match_id))


async def _handle_highlight(update: Update, match_id: int) -> None:
    highlight = await api_client.get_highlight(match_id)
    if not highlight:
        await update.callback_query.answer("⚠️ No highlight available yet.", show_alert=True)
        return
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    title = highlight.get("title") or "Official Highlights"
    url = highlight["youtube_url"]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"▶️ {title}", url=url)],
        [InlineKeyboardButton("⬅️ Back to Match", callback_data=cb_match(match_id))],
    ])
    await _edit(update, f"🎬 <b>Highlights available!</b>", kb)


async def _handle_standings(update: Update, tournament_id: int) -> None:
    tournaments = await api_client.get_tournaments()
    t = next((t for t in tournaments if t["id"] == tournament_id), None)
    name = t["name"] if t else "Tournament"
    standings = await api_client.get_standings(tournament_id)
    from telegram import InlineKeyboardMarkup
    from bot.keyboards import back_home_button
    await _edit(update, standings_text(standings, name),
                InlineKeyboardMarkup([back_home_button()]))
