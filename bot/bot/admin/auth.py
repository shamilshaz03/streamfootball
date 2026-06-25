"""Admin session management."""
import httpx
from bot.config import ADMIN_TELEGRAM_IDS, ADMIN_PASSWORD, API_BASE_URL, BACKEND_ADMIN_USERNAME, BACKEND_ADMIN_PASSWORD

_sessions: set[int] = set()
_jwt_token: str | None = None

def is_admin(telegram_id: int) -> bool:
    return telegram_id in _sessions or telegram_id in ADMIN_TELEGRAM_IDS

def check_password(password: str) -> bool:
    return password.strip() == ADMIN_PASSWORD

def add_session(telegram_id: int) -> None:
    _sessions.add(telegram_id)

def remove_session(telegram_id: int) -> None:
    _sessions.discard(telegram_id)

async def get_jwt() -> str:
    global _jwt_token
    if _jwt_token:
        return _jwt_token
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10) as client:
        r = await client.post("/auth/login", json={
            "username": BACKEND_ADMIN_USERNAME,
            "password": BACKEND_ADMIN_PASSWORD
        })
        r.raise_for_status()
        _jwt_token = r.json()["access_token"]
        return _jwt_token

async def reset_jwt() -> None:
    global _jwt_token
    _jwt_token = None
