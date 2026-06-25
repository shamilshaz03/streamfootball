"""Bot-based admin panel — full control via Telegram."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ContextTypes, ConversationHandler,
                           CommandHandler, MessageHandler, CallbackQueryHandler, filters)
from bot.admin.auth import is_admin, check_password, add_session, remove_session, get_jwt, reset_jwt
from bot.admin.keyboards import (admin_menu_keyboard, back_admin_keyboard, cancel_keyboard,
                                  ADM_MENU, ADM_DASHBOARD, ADM_MATCHES, ADM_ADD_MATCH,
                                  ADM_STREAMS, ADM_HIGHLIGHTS, ADM_TOURNAMENTS, ADM_ADD_TOUR,
                                  ADM_USERS, ADM_BROADCAST, ADM_LOGOUT)
import httpx
from bot.config import API_BASE_URL

# ConversationHandler states
(ASK_PASS, ADD_MATCH_TOUR, ADD_MATCH_HOME, ADD_MATCH_AWAY, ADD_MATCH_DATE,
 ADD_MATCH_VENUE, ADD_MATCH_STAGE, ADD_TOUR_NAME, ADD_TOUR_COUNTRY,
 ADD_STREAM_MATCH, ADD_STREAM_URL, ADD_STREAM_LANG, ADD_STREAM_QUAL,
 ADD_HL_MATCH, ADD_HL_URL, ADD_BROADCAST_MSG) = range(16)

CANCEL_TEXT = "❌ Cancelled."

async def _api(method: str, path: str, **kwargs):
    token = await get_jwt()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=15) as c:
        r = await getattr(c, method)(path, headers=headers, **kwargs)
        if r.status_code == 401:
            await reset_jwt()
            token = await get_jwt()
            headers = {"Authorization": f"Bearer {token}"}
            r = await getattr(c, method)(path, headers=headers, **kwargs)
        r.raise_for_status()
        return r.json() if r.content else {}

async def cmd_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_admin(uid):
        await _show_admin_menu(update)
        return ConversationHandler.END
    await update.message.reply_text("🔐 <b>Admin Login</b>\n\nEnter admin password:", parse_mode="HTML")
    return ASK_PASS

async def _show_admin_menu(update: Update):
    text = "🛡️ <b>Admin Panel</b>\n\nSelect an option:"
    kb = admin_menu_keyboard()
    if update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

async def ask_pass(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if check_password(update.message.text or ""):
        add_session(update.effective_user.id)
        await update.message.delete()
        await update.message.reply_text("✅ <b>Logged in!</b>", parse_mode="HTML")
        await _show_admin_menu(update)
    else:
        await update.message.delete()
        await update.message.reply_text("❌ Wrong password. /admin to try again.")
    return ConversationHandler.END

async def adm_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = update.effective_user.id
    if not is_admin(uid):
        await q.message.edit_text("❌ Not authorized. Use /admin to login.")
        return ConversationHandler.END

    data = q.data

    if data == ADM_MENU:
        await q.message.edit_text("🛡️ <b>Admin Panel</b>\n\nSelect an option:", parse_mode="HTML", reply_markup=admin_menu_keyboard())

    elif data == ADM_LOGOUT:
        remove_session(uid)
        await q.message.edit_text("👋 Logged out.")

    elif data == ADM_DASHBOARD:
        try:
            stats = await _api("get", "/dashboard")
            msg = (f"📊 <b>Dashboard</b>\n\n"
                   f"⚽ Total Matches: <b>{stats.get('total_matches', 0)}</b>\n"
                   f"🔴 Live Now: <b>{stats.get('live_matches', 0)}</b>\n"
                   f"🏆 Tournaments: <b>{stats.get('total_tournaments', 0)}</b>\n"
                   f"👥 Users: <b>{stats.get('total_users', 0)}</b>\n"
                   f"📺 Streams: <b>{stats.get('total_streams', 0)}</b>\n"
                   f"🎬 Highlights: <b>{stats.get('total_highlights', 0)}</b>")
        except Exception as e:
            msg = f"⚠️ Could not load stats: {e}"
        await q.message.edit_text(msg, parse_mode="HTML", reply_markup=back_admin_keyboard())

    elif data == ADM_MATCHES:
        try:
            matches = await _api("get", "/matches/today")
            if not matches:
                matches = await _api("get", "/matches/upcoming")
            if matches:
                lines = []
                for m in matches[:15]:
                    home = m.get("home_team", {}).get("name", "?")
                    away = m.get("away_team", {}).get("name", "?")
                    status = m.get("status", "")
                    badge = {"live": "🔴", "finished": "✅", "halftime": "⏸"}.get(status, "📅")
                    lines.append(f"{badge} <b>{home}</b> vs <b>{away}</b> (ID: {m['id']})")
                msg = "⚽ <b>Matches</b>\n\n" + "\n".join(lines)
            else:
                msg = "⚽ No matches found."
        except Exception as e:
            msg = f"⚠️ Error: {e}"
        await q.message.edit_text(msg, parse_mode="HTML", reply_markup=back_admin_keyboard())

    elif data == ADM_TOURNAMENTS:
        try:
            tours = await _api("get", "/tournaments")
            if tours:
                lines = [f"🏆 <b>{t['name']}</b> (ID: {t['id']}) {'✅' if t.get('is_active') else '❌'}" for t in tours[:15]]
                msg = "🏆 <b>Tournaments</b>\n\n" + "\n".join(lines)
            else:
                msg = "🏆 No tournaments found."
        except Exception as e:
            msg = f"⚠️ Error: {e}"
        await q.message.edit_text(msg, parse_mode="HTML", reply_markup=back_admin_keyboard())

    elif data == ADM_USERS:
        try:
            users = await _api("get", "/users")
            count = len(users) if isinstance(users, list) else users.get("total", "?")
            msg = f"👥 <b>Users</b>\n\nTotal registered: <b>{count}</b>"
        except Exception as e:
            msg = f"⚠️ Error: {e}"
        await q.message.edit_text(msg, parse_mode="HTML", reply_markup=back_admin_keyboard())

    elif data == ADM_ADD_MATCH:
        await q.message.edit_text(
            "⚽ <b>Add Match</b> — Step 1/5\n\nEnter <b>Tournament ID</b>:\n(Use 🏆 Tournaments to find IDs)",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return ADD_MATCH_TOUR

    elif data == ADM_ADD_TOUR:
        await q.message.edit_text("🏆 <b>Add Tournament</b>\n\nEnter tournament <b>name</b>:",
                                   parse_mode="HTML", reply_markup=cancel_keyboard())
        return ADD_TOUR_NAME

    elif data == ADM_STREAMS:
        await q.message.edit_text(
            "📺 <b>Add Stream</b> — Step 1/4\n\nEnter <b>Match ID</b>:\n(Use ⚽ Matches to find IDs)",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return ADD_STREAM_MATCH

    elif data == ADM_HIGHLIGHTS:
        await q.message.edit_text(
            "🎬 <b>Add Highlight</b> — Step 1/2\n\nEnter <b>Match ID</b>:",
            parse_mode="HTML", reply_markup=cancel_keyboard())
        return ADD_HL_MATCH

    elif data == ADM_BROADCAST:
        await q.message.edit_text("📢 <b>Broadcast Message</b>\n\nType the message to send to all users:",
                                   parse_mode="HTML", reply_markup=cancel_keyboard())
        return ADD_BROADCAST_MSG

# ── Add Match flow ─────────────────────────────────────────────────────────
async def match_get_tour(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_tour"] = u.message.text
    await u.message.reply_text("Step 2/5 — Enter <b>Home Team</b> name:", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_MATCH_HOME

async def match_get_home(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_home"] = u.message.text
    await u.message.reply_text("Step 3/5 — Enter <b>Away Team</b> name:", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_MATCH_AWAY

async def match_get_away(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_away"] = u.message.text
    await u.message.reply_text("Step 4/5 — Enter <b>Match Date & Time</b>\nFormat: YYYY-MM-DD HH:MM (UTC)", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_MATCH_DATE

async def match_get_date(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_date"] = u.message.text.strip()
    await u.message.reply_text("Step 5/5 — Enter <b>Venue</b> (or skip with '-'):", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_MATCH_VENUE

async def match_get_venue(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["m_venue"] = u.message.text
    await u.message.reply_text("Enter <b>Stage</b> (e.g. Group Stage, Final) or '-':", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_MATCH_STAGE

async def match_get_stage(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d = ctx.user_data
    try:
        date_str = d["m_date"]
        if len(date_str) == 16:
            date_str += ":00"
        payload = {
            "tournament_id": int(d["m_tour"]),
            "home_team_name": d["m_home"],
            "away_team_name": d["m_away"],
            "match_date": date_str.replace(" ", "T") + "Z",
            "venue": None if d.get("m_venue") == "-" else d.get("m_venue"),
            "stage": None if u.message.text == "-" else u.message.text,
            "status": "scheduled"
        }
        result = await _api("post", "/matches", json=payload)
        await u.message.reply_text(
            f"✅ <b>Match created!</b>\nID: <b>{result.get('id')}</b>\n{d['m_home']} vs {d['m_away']}",
            parse_mode="HTML", reply_markup=back_admin_keyboard())
    except Exception as e:
        await u.message.reply_text(f"❌ Failed: {e}", reply_markup=back_admin_keyboard())
    ctx.user_data.clear()
    return ConversationHandler.END

# ── Add Tournament flow ────────────────────────────────────────────────────
async def tour_get_name(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["t_name"] = u.message.text
    await u.message.reply_text("Enter <b>Country/Region</b> (or '-'):", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_TOUR_COUNTRY

async def tour_get_country(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        result = await _api("post", "/tournaments", json={
            "name": ctx.user_data["t_name"],
            "country": None if u.message.text == "-" else u.message.text,
            "is_active": True
        })
        await u.message.reply_text(f"✅ <b>Tournament created!</b>\nID: <b>{result.get('id')}</b>",
                                    parse_mode="HTML", reply_markup=back_admin_keyboard())
    except Exception as e:
        await u.message.reply_text(f"❌ Failed: {e}", reply_markup=back_admin_keyboard())
    ctx.user_data.clear()
    return ConversationHandler.END

# ── Add Stream flow ────────────────────────────────────────────────────────
async def stream_get_match(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["s_match"] = u.message.text
    await u.message.reply_text("Step 2/4 — Enter <b>Stream URL</b>:", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_STREAM_URL

async def stream_get_url(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["s_url"] = u.message.text
    await u.message.reply_text("Step 3/4 — Enter <b>Language</b> (e.g. English, Malayalam):", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_STREAM_LANG

async def stream_get_lang(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["s_lang"] = u.message.text
    await u.message.reply_text("Step 4/4 — Enter <b>Quality</b> (e.g. HD, 1080p, SD):", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_STREAM_QUAL

async def stream_get_qual(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    d = ctx.user_data
    try:
        result = await _api("post", f"/matches/{d['s_match']}/streams", json={
            "url": d["s_url"],
            "language": d["s_lang"],
            "quality": u.message.text,
            "label": f"{d['s_lang']} {u.message.text}",
            "stream_type": "external",
            "is_active": True
        })
        await u.message.reply_text(f"✅ <b>Stream added!</b>", parse_mode="HTML", reply_markup=back_admin_keyboard())
    except Exception as e:
        await u.message.reply_text(f"❌ Failed: {e}", reply_markup=back_admin_keyboard())
    ctx.user_data.clear()
    return ConversationHandler.END

# ── Add Highlight flow ─────────────────────────────────────────────────────
async def hl_get_match(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["h_match"] = u.message.text
    await u.message.reply_text("Step 2/2 — Enter <b>YouTube URL</b>:", parse_mode="HTML", reply_markup=cancel_keyboard())
    return ADD_HL_URL

async def hl_get_url(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        await _api("post", f"/matches/{ctx.user_data['h_match']}/highlights", json={
            "youtube_url": u.message.text, "title": "Highlights", "is_published": True
        })
        await u.message.reply_text("✅ <b>Highlight added!</b>", parse_mode="HTML", reply_markup=back_admin_keyboard())
    except Exception as e:
        await u.message.reply_text(f"❌ Failed: {e}", reply_markup=back_admin_keyboard())
    ctx.user_data.clear()
    return ConversationHandler.END

# ── Broadcast flow ─────────────────────────────────────────────────────────
async def broadcast_send(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        await _api("post", "/notifications/broadcast", json={"message": u.message.text})
        await u.message.reply_text("✅ <b>Broadcast sent!</b>", parse_mode="HTML", reply_markup=back_admin_keyboard())
    except Exception as e:
        await u.message.reply_text(f"❌ Failed: {e}", reply_markup=back_admin_keyboard())
    return ConversationHandler.END

async def cancel(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    if u.message:
        await u.message.reply_text(CANCEL_TEXT, reply_markup=back_admin_keyboard())
    return ConversationHandler.END


def build_admin_conversation() -> ConversationHandler:
    txt = filters.TEXT & ~filters.COMMAND
    return ConversationHandler(
        entry_points=[CommandHandler("admin", cmd_admin)],
        states={
            ASK_PASS:        [MessageHandler(txt, ask_pass)],
            ADD_MATCH_TOUR:  [MessageHandler(txt, match_get_tour),  CallbackQueryHandler(adm_callback)],
            ADD_MATCH_HOME:  [MessageHandler(txt, match_get_home),  CallbackQueryHandler(adm_callback)],
            ADD_MATCH_AWAY:  [MessageHandler(txt, match_get_away),  CallbackQueryHandler(adm_callback)],
            ADD_MATCH_DATE:  [MessageHandler(txt, match_get_date),  CallbackQueryHandler(adm_callback)],
            ADD_MATCH_VENUE: [MessageHandler(txt, match_get_venue), CallbackQueryHandler(adm_callback)],
            ADD_MATCH_STAGE: [MessageHandler(txt, match_get_stage), CallbackQueryHandler(adm_callback)],
            ADD_TOUR_NAME:   [MessageHandler(txt, tour_get_name),   CallbackQueryHandler(adm_callback)],
            ADD_TOUR_COUNTRY:[MessageHandler(txt, tour_get_country),CallbackQueryHandler(adm_callback)],
            ADD_STREAM_MATCH:[MessageHandler(txt, stream_get_match),CallbackQueryHandler(adm_callback)],
            ADD_STREAM_URL:  [MessageHandler(txt, stream_get_url),  CallbackQueryHandler(adm_callback)],
            ADD_STREAM_LANG: [MessageHandler(txt, stream_get_lang), CallbackQueryHandler(adm_callback)],
            ADD_STREAM_QUAL: [MessageHandler(txt, stream_get_qual), CallbackQueryHandler(adm_callback)],
            ADD_HL_MATCH:    [MessageHandler(txt, hl_get_match),    CallbackQueryHandler(adm_callback)],
            ADD_HL_URL:      [MessageHandler(txt, hl_get_url),      CallbackQueryHandler(adm_callback)],
            ADD_BROADCAST_MSG:[MessageHandler(txt, broadcast_send), CallbackQueryHandler(adm_callback)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("admin", cmd_admin)],
        per_message=False,
        allow_reentry=True,
    )
