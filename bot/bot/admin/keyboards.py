from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ADM_MENU        = "adm:menu"
ADM_DASHBOARD   = "adm:dashboard"
ADM_MATCHES     = "adm:matches"
ADM_ADD_MATCH   = "adm:add_match"
ADM_STREAMS     = "adm:streams"
ADM_HIGHLIGHTS  = "adm:highlights"
ADM_TOURNAMENTS = "adm:tournaments"
ADM_ADD_TOUR    = "adm:add_tournament"
ADM_USERS       = "adm:users"
ADM_BROADCAST   = "adm:broadcast"
ADM_LOGOUT      = "adm:logout"
ADM_PAYMENT     = "adm:payment"
ADM_PAY_TOGGLE  = "adm:pay_toggle"
ADM_PAY_AMOUNT  = "adm:pay_amount"
ADM_PAY_UPI     = "adm:pay_upi"
ADM_PAY_QR      = "adm:pay_qr"
ADM_PENDING     = "adm:pending"

def admin_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Dashboard",       callback_data=ADM_DASHBOARD)],
        [InlineKeyboardButton("⚽ Matches",          callback_data=ADM_MATCHES),
         InlineKeyboardButton("➕ Add Match",        callback_data=ADM_ADD_MATCH)],
        [InlineKeyboardButton("🏆 Tournaments",      callback_data=ADM_TOURNAMENTS),
         InlineKeyboardButton("➕ Add",              callback_data=ADM_ADD_TOUR)],
        [InlineKeyboardButton("📺 Add Stream",       callback_data=ADM_STREAMS)],
        [InlineKeyboardButton("🎬 Add Highlight",    callback_data=ADM_HIGHLIGHTS)],
        [InlineKeyboardButton("👥 Users",            callback_data=ADM_USERS)],
        [InlineKeyboardButton("💳 Payment Settings", callback_data=ADM_PAYMENT)],
        [InlineKeyboardButton("📢 Broadcast",        callback_data=ADM_BROADCAST)],
        [InlineKeyboardButton("🚪 Logout",           callback_data=ADM_LOGOUT)],
    ])

def payment_keyboard(paid_mode: bool) -> InlineKeyboardMarkup:
    toggle_label = "🔴 Turn OFF Paid Mode" if paid_mode else "🟢 Turn ON Paid Mode"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_label,          callback_data=ADM_PAY_TOGGLE)],
        [InlineKeyboardButton("💰 Set Amount",       callback_data=ADM_PAY_AMOUNT)],
        [InlineKeyboardButton("📱 Set UPI ID",       callback_data=ADM_PAY_UPI)],
        [InlineKeyboardButton("📷 Upload QR Code",   callback_data=ADM_PAY_QR)],
        [InlineKeyboardButton("⏳ Pending Payments", callback_data=ADM_PENDING)],
        [InlineKeyboardButton("⬅️ Admin Menu",       callback_data=ADM_MENU)],
    ])

def back_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Admin Menu", callback_data=ADM_MENU)]])

def cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=ADM_MENU)]])

def approve_reject_keyboard(tid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve",  callback_data=f"adm:approve:{tid}"),
         InlineKeyboardButton("❌ Reject",   callback_data=f"adm:reject:{tid}")],
    ])
