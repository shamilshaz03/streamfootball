"""
Async HTTP client that wraps every backend API call made by the bot.
All network errors are caught and re-raised as RuntimeError so handlers
can show a friendly "Something went wrong, please try again." message.
"""
import httpx
from bot.config import API_BASE_URL

_CLIENT = httpx.AsyncClient(base_url=API_BASE_URL, timeout=10)


async def _get(path: str, **params) -> dict | list:
    try:
        r = await _CLIENT.get(path, params={k: v for k, v in params.items() if v is not None})
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"API error: {exc}") from exc


async def _post(path: str, json: dict) -> dict:
    try:
        r = await _CLIENT.post(path, json=json)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"API error: {exc}") from exc


async def _delete(path: str, **params) -> None:
    try:
        r = await _CLIENT.delete(path, params=params)
        r.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"API error: {exc}") from exc


# ── Convenience wrappers ──────────────────────────────────────────────────

async def upsert_user(telegram_id: int, username: str | None,
                      first_name: str | None, last_name: str | None,
                      language_code: str | None) -> None:
    await _post("/users/upsert", {
        "telegram_id": telegram_id, "username": username,
        "first_name": first_name, "last_name": last_name, "language_code": language_code,
    })


async def get_today_matches() -> list:
    return await _get("/matches/today")  # type: ignore[return-value]


async def get_upcoming_matches() -> list:
    return await _get("/matches/upcoming")  # type: ignore[return-value]


async def get_live_matches() -> list:
    return await _get("/matches/live")  # type: ignore[return-value]


async def get_match(match_id: int) -> dict:
    return await _get(f"/matches/{match_id}")  # type: ignore[return-value]


async def get_streams(match_id: int) -> list:
    return await _get(f"/matches/{match_id}/streams")  # type: ignore[return-value]


async def get_highlight(match_id: int) -> dict | None:
    try:
        return await _get(f"/matches/{match_id}/highlight")  # type: ignore[return-value]
    except RuntimeError:
        return None


async def get_standings(tournament_id: int) -> list:
    return await _get("/standings", tournament_id=tournament_id)  # type: ignore[return-value]


async def get_tournaments() -> list:
    return await _get("/tournaments")  # type: ignore[return-value]


async def subscribe_notification(telegram_id: int, match_id: int) -> dict:
    return await _post("/notifications/subscribe", {"telegram_id": telegram_id, "match_id": match_id})


async def unsubscribe_notification(telegram_id: int, match_id: int) -> None:
    await _delete("/notifications/unsubscribe", telegram_id=telegram_id, match_id=match_id)


async def subscription_status(telegram_id: int, match_id: int) -> bool:
    data = await _get("/notifications/status", telegram_id=telegram_id, match_id=match_id)
    return data.get("subscribed", False)  # type: ignore[union-attr]
