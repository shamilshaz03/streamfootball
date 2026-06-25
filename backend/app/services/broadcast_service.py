"""
Fires whenever an admin changes a match's status to LIVE, HALFTIME or
FINISHED. Two things happen:

1. Every user who subscribed ("Notify Me") gets a personal DM, once per
   status, tracked via the `sent_started` / `sent_halftime` / `sent_finished`
   flags on Notification so it is never sent twice.
2. If a public broadcast chat is configured (TELEGRAM_BROADCAST_CHAT_ID),
   the previous status-update message for this match is deleted and a
   fresh one is posted, so the channel always shows one current message
   per match instead of accumulating clutter.
"""
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models.enums import BroadcastType, MatchStatus
from app.models.highlight import BroadcastMessage
from app.models.match import Match
from app.models.notification import Notification
from app.services import telegram_client

_STATUS_TO_BROADCAST = {
    MatchStatus.LIVE: (BroadcastType.MATCH_STARTED, "sent_started", "\u26BD Kicked off!"),
    MatchStatus.HALFTIME: (BroadcastType.HALF_TIME, "sent_halftime", "\u23F8 Half time."),
    MatchStatus.FINISHED: (BroadcastType.MATCH_FINISHED, "sent_finished", "\u2705 Full time."),
}


def _format_text(match: Match, headline: str) -> str:
    score = ""
    if match.home_score is not None and match.away_score is not None:
        score = f" ({match.home_score} - {match.away_score})"
    return f"{headline}\n<b>{match.home_team.name}{score} {match.away_team.name}</b>"


async def broadcast_match_status(db: Session, match: Match) -> None:
    mapping = _STATUS_TO_BROADCAST.get(match.status)
    if mapping is None:
        return
    broadcast_type, flag_name, headline = mapping
    text = _format_text(match, headline)

    # 1. Personal DMs to subscribers who haven't received this status update yet.
    notifications = (
        db.query(Notification)
        .options(joinedload(Notification.user))
        .filter(
            Notification.match_id == match.id,
            Notification.is_active.is_(True),
            getattr(Notification, flag_name).is_(False),
        )
        .all()
    )
    for notification in notifications:
        await telegram_client.send_message(notification.user.telegram_id, text)
        setattr(notification, flag_name, True)
    if notifications:
        db.commit()

    # 2. Public channel broadcast: delete the previous one for this match, post new.
    if not settings.TELEGRAM_BROADCAST_CHAT_ID:
        return

    previous = (
        db.query(BroadcastMessage)
        .filter(BroadcastMessage.match_id == match.id)
        .order_by(BroadcastMessage.id.desc())
        .first()
    )
    if previous:
        await telegram_client.delete_message(previous.telegram_chat_id, previous.telegram_message_id)

    sent = await telegram_client.send_message(settings.TELEGRAM_BROADCAST_CHAT_ID, text)
    if sent:
        db.add(
            BroadcastMessage(
                match_id=match.id,
                broadcast_type=broadcast_type,
                telegram_chat_id=sent["chat"]["id"],
                telegram_message_id=sent["message_id"],
            )
        )
        db.commit()
