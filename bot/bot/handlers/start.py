from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes
from bot import api_client
from bot.keyboards import home_keyboard

WELCOME = (
    "🏟️ <b>Welcome to StreamFootball!</b>\n\n"
    "⚽ Watch live matches, get scores,\n"
    "🔔 set reminders & stream in your language.\n\n"
    "<i>Choose an option below to get started:</i>"
)

PHOTO_URL = "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800&q=80"

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
        except Exception:
            pass

    try:
        await update.message.reply_photo(
            photo=PHOTO_URL,
            caption=WELCOME,
            parse_mode="HTML",
            reply_markup=home_keyboard(),
        )
    except Exception:
        await update.message.reply_text(WELCOME, parse_mode="HTML", reply_markup=home_keyboard())
