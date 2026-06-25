"""
/start handler — greets the user, upserts their record in the DB,
and shows the home menu.
"""
from telegram import Update
from telegram.ext import ContextTypes

from bot import api_client
from bot.keyboards import home_keyboard


WELCOME = (
    "👋 Welcome to <b>Football Streaming Platform</b>!\n\n"
    "Catch every match live, set reminders, and watch in your language.\n"
    "Pick an option below to get started:"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user:
        try:
            await api_client.upsert_user(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code,
            )
        except RuntimeError:
            pass  # registration failure is non-fatal

    await update.message.reply_html(WELCOME, reply_markup=home_keyboard())
