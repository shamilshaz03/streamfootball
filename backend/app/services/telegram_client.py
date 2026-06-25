"""
Minimal async wrapper around the raw Telegram Bot HTTP API.

The backend uses this only to push reminders/broadcasts; all interactive
bot logic (menus, callbacks) lives in the separate `bot` service which
uses python-telegram-bot. Keeping this thin avoids coupling the two.
"""
import httpx

from app.config import settings

_BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_message(chat_id: int | str, text: str, reply_markup: dict | None = None) -> dict | None:
    payload: dict = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{_BASE_URL}/sendMessage", json=payload)
        data = resp.json()
        return data.get("result") if data.get("ok") else None


async def delete_message(chat_id: int | str, message_id: int) -> bool:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            f"{_BASE_URL}/deleteMessage", json={"chat_id": chat_id, "message_id": message_id}
        )
        data = resp.json()
        return bool(data.get("ok"))
