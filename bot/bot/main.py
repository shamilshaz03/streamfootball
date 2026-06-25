"""
Telegram bot entry point.

Run directly:
    python -m bot.main

In Docker: see docker-compose.yml (service: bot).
"""
import logging

from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.config import BOT_TOKEN
from bot.handlers.callbacks import callback_handler
from bot.handlers.start import start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


async def _post_init(application) -> None:
    """Set the bot's command menu shown in Telegram clients."""
    await application.bot.set_my_commands([
        BotCommand("start", "🏠 Open main menu"),
        BotCommand("live",  "🔴 Show live matches"),
        BotCommand("today", "📅 Today's matches"),
    ])


def main() -> None:
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", start))   # convenience alias
    app.add_handler(CommandHandler("live",  start))   # convenience alias
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("Bot polling started …")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
