"""Central callback handler with paid access check."""
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from bot import api_client
import bot.payment as pay
from bot.keyboards import (
    CB_BACK_HOME, CB_HIGHLIGHTS, CB_LIVE, CB_STANDINGS, CB_TODAY, CB_TOURNEY, CB_UPCOMING,
    cb_match, home_keyboard, match_detail_keyboard, match_detail_text,
    match_list_keyboard, standings_text, streams_keyboard, tournaments_keyboard,
)

async def _edit(update, text, markup=None):
    await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

async def _check_paid(update: Update) -> bool:
    """Returns True if user can access paid content."""
    if not pay.is_paid_mode():
        return True
    uid = update.effective_user.id
    if pay.is_user_paid(uid):
        return True
    # Show payment wall
    amount = pay.get_amount()
    upi = pay.get_upi()
    qr = pay.get_qr_file_id()
    msg = (f"💳 <b>Premium Content</b>\n\n"
           f"This feature requires a subscription.\n\n"
           f"💰 Amount: <b>₹{amount:.0f}</b>\n"
           f"📱 UPI: <b>{upi or 'Contact admin'}</b>\n\n"
           f"After payment, send /pay to notify admin.")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=CB_BACK_HOME)]])
    q = update.callback_query
    if qr:
        await q.message.reply_photo(photo=qr, caption=msg, parse_mode="HTML", reply_markup=kb)
        await q.message.delete()
    else:
        await _edit(update, msg, kb)
    return False

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data or ""
    user = update.effective_user
    try:
        if data == CB_BACK_HOME:
            await _edit(update, "🏠 <b>Main Menu</b>", home_keyboard())

        elif data == CB_TODAY:
            matches = await api_client.get_today_matches()
            await _handle_match_list(update, matches, "📅 Today's Matches")

        elif data == CB_UPCOMING:
            matches = await api_client.get_upcoming_matches()
            await _handle_match_list(update, matches, "⏭ Upcoming Matches")

        elif data == CB_LIVE:
            matches = await api_client.get_live_matches()
            await _handle_match_list(update, matches, "🔴 Live Now")

        elif data == CB_TOURNEY:
            tournaments = await api_client.get_tournaments()
            if not tournaments:
                await _edit(update, "No active tournaments.", _back_kb())
            else:
                await _edit(update, "🏆 <b>Tournaments</b>\n\nSelect to see standings:", tournaments_keyboard(tournaments))

        elif data == CB_STANDINGS:
            tournaments = await api_client.get_tournaments()
            if not tournaments:
                await _edit(update, "No active tournaments.", _back_kb())
            else:
                await _edit(update, "📊 Select a tournament:", tournaments_keyboard(tournaments))

        elif data == CB_HIGHLIGHTS:
            await _edit(update, "🎬 <b>Highlights</b>\n\nSelect a match to see highlights.", _back_kb())

        elif data.startswith("match:"):
            match_id = int(data.split(":")[1])
            await _handle_match_detail(update, match_id, user.id if user else 0)

        elif data.startswith("streams:"):
            if not await _check_paid(update):
                return
            match_id = int(data.split(":")[1])
            await _handle_streams(update, match_id)

        elif data.startswith("notify:"):
            match_id = int(data.split(":")[1])
            if user:
                await api_client.subscribe_notification(user.id, match_id)
                await q.answer("🔔 You'll be notified before this match!", show_alert=True)
                await _handle_match_detail(update, match_id, user.id)

        elif data.startswith("unnotify:"):
            match_id = int(data.split(":")[1])
            if user:
                await api_client.unsubscribe_notification(user.id, match_id)
                await q.answer("🔕 Notification cancelled.", show_alert=True)
                await _handle_match_detail(update, match_id, user.id)

        elif data.startswith("highlight:"):
            if not await _check_paid(update):
                return
            match_id = int(data.split(":")[1])
            await _handle_highlight(update, match_id)

        elif data.startswith("standings:"):
            tournament_id = int(data.split(":")[1])
            await _handle_standings(update, tournament_id)

    except RuntimeError as exc:
        await _edit(update, f"⚠️ Something went wrong: {exc}\n\nPlease try again.", _back_kb())

def _back_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=CB_BACK_HOME)]])

async def _handle_match_list(update, matches, title):
    if not matches:
        await _edit(update, f"{title}\n\nNo matches found.", _back_kb())
        return
    await _edit(update, f"<b>{title}</b>", match_list_keyboard(matches, CB_BACK_HOME))

async def _handle_match_detail(update, match_id, telegram_id):
    match = await api_client.get_match(match_id)
    subscribed = await api_client.subscription_status(telegram_id, match_id) if telegram_id else False
    await _edit(update, match_detail_text(match), match_detail_keyboard(match, subscribed))

async def _handle_streams(update, match_id):
    streams = await api_client.get_streams(match_id)
    if not streams:
        await update.callback_query.answer("⚠️ No streams available yet.", show_alert=True)
        return
    await _edit(update, "📺 <b>Watch Now</b>\n\nSelect language & quality:", streams_keyboard(streams, match_id))

async def _handle_highlight(update, match_id):
    highlight = await api_client.get_highlight(match_id)
    if not highlight:
        await update.callback_query.answer("⚠️ No highlight available yet.", show_alert=True)
        return
    title = highlight.get("title") or "Official Highlights"
    url = highlight["youtube_url"]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"▶️ {title}", url=url)],
        [InlineKeyboardButton("⬅️ Back", callback_data=cb_match(match_id))],
    ])
    await _edit(update, "🎬 <b>Highlights available!</b>", kb)

async def _handle_standings(update, tournament_id):
    tournaments = await api_client.get_tournaments()
    t = next((t for t in tournaments if t["id"] == tournament_id), None)
    name = t["name"] if t else "Tournament"
    standings = await api_client.get_standings(tournament_id)
    await _edit(update, standings_text(standings, name), _back_kb())
