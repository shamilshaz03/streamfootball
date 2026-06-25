"""
Redis connection and lightweight JSON cache helpers.

Used to cache read-heavy, frequently polled endpoints (today's matches,
live matches, standings) so the bot can poll without hammering Postgres.
"""
import json
from typing import Any, Optional

import redis

from app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def cache_get(key: str) -> Optional[Any]:
    raw = redis_client.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def cache_set(key: str, value: Any, ttl_seconds: int = 30) -> None:
    redis_client.set(key, json.dumps(value, default=str), ex=ttl_seconds)


def cache_delete(*keys: str) -> None:
    if keys:
        redis_client.delete(*keys)


def cache_delete_prefix(prefix: str) -> None:
    """Delete all keys matching a prefix (used to bust caches after writes)."""
    cursor = 0
    while True:
        cursor, found_keys = redis_client.scan(cursor=cursor, match=f"{prefix}*", count=100)
        if found_keys:
            redis_client.delete(*found_keys)
        if cursor == 0:
            break
