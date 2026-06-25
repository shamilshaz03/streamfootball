from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Admin callback constants
ADM_MENU       = "adm:menu"
ADM_DASHBOARD  = "adm:dashboard"
ADM_MATCHES    = "adm:matches"
ADM_ADD_MATCH  = "adm:add_match"
ADM_STREAMS    = "adm:streams"
ADM_HIGHLIGHTS = "adm:highlights"
ADM_TOURNAMENTS= "adm:tournaments"
ADM_ADD_TOUR   = "adm:add_tournament"
ADM_USERS      = "adm:users"
ADM_BROADCAST  = "adm:broadcast"
ADM_LOGOUT     = "adm:logout"

def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Dashboard",        callback_data=ADM_DASHBOARD)],
        [InlineKeyboardButton("⚽ Matches",           callback_data=ADM_MATCHES),
         InlineKeyboardButton("➕ Add Match",         callback_data=ADM_ADD_MATCH)],
        [InlineKeyboardButton("🏆 Tournaments",       callback_data=ADM_TOURNAMENTS),
         InlineKeyboardButton("➕ Add Tournament",    callback_data=ADM_ADD_TOUR)],
        [InlineKeyboardButton("📺 Add Stream",        callback_data=ADM_STREAMS)],
        [InlineKeyboardButton("🎬 Add Highlight",     callback_data=ADM_HIGHLIGHTS)],
        [InlineKeyboardButton("👥 Users",             callback_data=ADM_USERS)],
        [InlineKeyboardButton("📢 Broadcast",         callback_data=ADM_BROADCAST)],
        [InlineKeyboardButton("🚪 Logout",            callback_data=ADM_LOGOUT)],
    ])

def back_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Admin Menu", callback_data=ADM_MENU)]])

def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=ADM_MENU)]])
