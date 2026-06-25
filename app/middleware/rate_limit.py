"""
Rate limiting setup using slowapi (Redis-aware, key by client IP).

Applied as a global default in main.py, with a stricter override on the
login endpoint to slow down credential brute-forcing.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
)
