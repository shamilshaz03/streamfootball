import logging
from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler
from bot.config import BOT_TOKEN
from bot.handlers.callbacks import callback_handler
from bot.handlers.start import start
from bot.admin.handlers import build_admin_conversation, adm_callback

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger(__name__)

async def _post_init(application) -> None:
    await application.bot.set_my_commands([
        BotCommand("start",  "🏠 Open main menu"),
        BotCommand("live",   "🔴 Live matches"),
        BotCommand("today",  "📅 Today's matches"),
        BotCommand("admin",  "🛡️ Admin panel"),
    ])

def main() -> None:
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).build()

    # Admin conversation (must be first — higher priority)
    app.add_handler(build_admin_conversation())

    # Admin inline callbacks (for buttons inside admin panel)
    app.add_handler(CallbackQueryHandler(adm_callback, pattern="^adm:"))

    # User handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", start))
    app.add_handler(CommandHandler("live",  start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("Bot polling started …")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
