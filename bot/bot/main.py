import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from bot.config import BOT_TOKEN
from bot.handlers.callbacks import callback_handler
from bot.handlers.start import start
from bot.admin.handlers import build_admin_conversation, adm_callback
import bot.payment as pay

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger(__name__)

async def cmd_pay(update: Update, ctx):
    """User notifies admin about payment."""
    uid = update.effective_user.id
    if not pay.is_paid_mode():
        await update.message.reply_text("ℹ️ Paid mode is currently OFF. All features are free!")
        return
    if pay.is_user_paid(uid):
        await update.message.reply_text("✅ You already have full access!")
        return
    user = update.effective_user
    pay.add_pending(uid, {
        "name": user.full_name,
        "username": user.username or "",
    })
    await update.message.reply_text(
        "⏳ <b>Payment request sent!</b>\n\nAdmin will verify and approve your access shortly.",
        parse_mode="HTML")

async def _post_init(application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start",  "🏠 Open main menu"),
        BotCommand("live",   "🔴 Live matches"),
        BotCommand("today",  "📅 Today's matches"),
        BotCommand("pay",    "💳 Notify payment"),
        BotCommand("admin",  "🛡️ Admin panel"),
    ])

def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).build()
    app.add_handler(build_admin_conversation())
    app.add_handler(CallbackQueryHandler(adm_callback, pattern="^adm:"))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", start))
    app.add_handler(CommandHandler("live",  start))
    app.add_handler(CommandHandler("pay",   cmd_pay))
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("Bot polling started …")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
