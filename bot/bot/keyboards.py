"""
Reusable InlineKeyboardMarkup builders and message text formatters.

Having these in one place means every handler produces identical-looking
messages and keyboards without duplicating formatting logic.
"""
from datetime import datetime, timezone
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ── Callback data constants ────────────────────────────────────────────────

def cb_match(match_id: int) -> str:
    return f"match:{match_id}"

def cb_streams(match_id: int) -> str:
    return f"streams:{match_id}"

def cb_stream_url(stream_id: int) -> str:
    return f"stream:{stream_id}"

def cb_notify(match_id: int) -> str:
    return f"notify:{match_id}"

def cb_unnotify(match_id: int) -> str:
    return f"unnotify:{match_id}"

def cb_highlight(match_id: int) -> str:
    return f"highlight:{match_id}"

def cb_standings(tournament_id: int) -> str:
    return f"standings:{tournament_id}"

CB_TODAY      = "menu:today"
CB_UPCOMING   = "menu:upcoming"
CB_LIVE       = "menu:live"
CB_STANDINGS  = "menu:standings"
CB_TOURNEY    = "menu:tournaments"
CB_HIGHLIGHTS = "menu:highlights"
CB_BACK_HOME  = "menu:home"


# ── Home menu ─────────────────────────────────────────────────────────────

def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Today's Matches",    callback_data=CB_TODAY)],
        [InlineKeyboardButton("⏭ Upcoming Matches",   callback_data=CB_UPCOMING)],
        [InlineKeyboardButton("🔴 Live Now",           callback_data=CB_LIVE)],
        [InlineKeyboardButton("🏆 Points Table",       callback_data=CB_STANDINGS)],
        [InlineKeyboardButton("ℹ️ Tournaments",         callback_data=CB_TOURNEY)],
        [InlineKeyboardButton("🎬 Highlights",          callback_data=CB_HIGHLIGHTS)],
    ])


def back_home_button() -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton("⬅️ Back to Menu", callback_data=CB_BACK_HOME)]


# ── Match list ────────────────────────────────────────────────────────────

def _match_label(m: dict) -> str:
    home = m.get("home_team", {}).get("name", "?")
    away = m.get("away_team", {}).get("name", "?")
    dt   = _fmt_time(m.get("match_date", ""))
    status = m.get("status", "scheduled")
    badge = {"live": "🔴 LIVE  ", "halftime": "⏸ HT  ", "finished": "✅ FT  "}.get(status, "")
    return f"{badge}{home} vs {away}  {dt}"


def match_list_keyboard(matches: list[dict], back_cb: str) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(_match_label(m), callback_data=cb_match(m["id"]))]
            for m in matches]
    rows.append(back_home_button())
    return InlineKeyboardMarkup(rows)


# ── Match detail ──────────────────────────────────────────────────────────

def match_detail_text(m: dict) -> str:
    home = m.get("home_team", {}).get("name", "?")
    away = m.get("away_team", {}).get("name", "?")
    status = m.get("status", "scheduled").replace("_", " ").upper()
    dt = _fmt_time(m.get("match_date", ""))
    venue = m.get("venue") or "—"
    stage = m.get("stage") or "—"
    score = ""
    if m.get("home_score") is not None:
        score = f"\n⚽ Score: <b>{m['home_score']} – {m['away_score']}</b>"
    return (
        f"<b>{home} vs {away}</b>\n"
        f"📅 {dt}  |  🏟 {venue}\n"
        f"🎯 Stage: {stage}  |  {status}"
        f"{score}"
    )


def match_detail_keyboard(m: dict, subscribed: bool) -> InlineKeyboardMarkup:
    match_id = m["id"]
    has_streams = bool(m.get("streams"))
    has_highlight = m.get("has_highlight", False)
    status = m.get("status", "scheduled")

    rows: list[list[InlineKeyboardButton]] = []
    if has_streams and status in ("live", "halftime", "scheduled"):
        rows.append([InlineKeyboardButton("▶️ Watch Now", callback_data=cb_streams(match_id))])

    notify_btn = (
        InlineKeyboardButton("🔕 Cancel Notification", callback_data=cb_unnotify(match_id))
        if subscribed
        else InlineKeyboardButton("🔔 Notify Me", callback_data=cb_notify(match_id))
    )
    rows.append([notify_btn])

    if has_highlight:
        rows.append([InlineKeyboardButton("🎬 Highlights", callback_data=cb_highlight(match_id))])

    rows.append(back_home_button())
    return InlineKeyboardMarkup(rows)


# ── Streams keyboard ──────────────────────────────────────────────────────

def streams_keyboard(streams: list[dict], match_id: int) -> InlineKeyboardMarkup:
    """
    One button per stream — label is 'Language Quality', e.g. 'English 1080p'.
    For HLS/MP4/webapp types the callback opens the URL; for external links
    we embed the URL directly as a url-button.
    """
    rows: list[list[InlineKeyboardButton]] = []
    for s in streams:
        label = s.get("label") or f"{s.get('language','')} {s.get('quality','')}"
        stream_type = s.get("stream_type", "external")
        url = s.get("url", "")

        if stream_type in ("external", "webapp"):
            rows.append([InlineKeyboardButton(f"📺 {label}", url=url)])
        else:
            # hls/mp4: open via our mini webapp or deep link
            rows.append([InlineKeyboardButton(f"📺 {label}", url=url)])

    rows.append([InlineKeyboardButton("⬅️ Back to Match", callback_data=cb_match(match_id))])
    return InlineKeyboardMarkup(rows)


# ── Standings / tournaments ───────────────────────────────────────────────

def tournaments_keyboard(tournaments: list[dict]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t["name"], callback_data=cb_standings(t["id"]))]
        for t in tournaments if t.get("is_active")
    ]
    rows.append(back_home_button())
    return InlineKeyboardMarkup(rows)


def standings_text(standings: list[dict], tournament_name: str) -> str:
    if not standings:
        return f"<b>{tournament_name}</b>\n\nNo standings data yet."
    header = f"<b>🏆 {tournament_name} — Points Table</b>\n\n"
    header += "<code>#   Team             P  W  D  L  GF GA GD Pts</code>\n"
    rows = []
    for i, s in enumerate(standings, 1):
        team = s.get("team", {}).get("short_name") or s.get("team", {}).get("name", "?")
        team = team[:16].ljust(16)
        p, w, d, l = s["played"], s["won"], s["drawn"], s["lost"]
        gf, ga, gd, pts = s["goals_for"], s["goals_against"], s["goal_difference"], s["points"]
        rows.append(f"<code>{i:<3} {team} {p:<2} {w:<2} {d:<2} {l:<2} {gf:<2} {ga:<2} {gd:+3} {pts:<3}</code>")
    return header + "\n".join(rows)


# ── Helpers ───────────────────────────────────────────────────────────────

def _fmt_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d %b %H:%M UTC")
    except Exception:
        return iso
