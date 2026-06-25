"""
Handles the time-based reminder side of notifications:
1 hour / 30 minutes / 15 minutes before kickoff.

The "match started / half time / finished" notifications are sent from
`broadcast_service` at the moment an admin changes the match status,
since those are event-driven rather than time-driven.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, joinedload

from app.models.match import Match
from app.models.notification import Notification
from app.models.user import User
from app.services import telegram_client

# (offset from kickoff, sent-flag column name, human label)
_REMINDER_WINDOWS = [
    (timedelta(hours=1), "sent_1h", "starts in 1 hour"),
    (timedelta(minutes=30), "sent_30m", "starts in 30 minutes"),
    (timedelta(minutes=15), "sent_15m", "starts in 15 minutes"),
]

# How wide the matching window is, to tolerate the scheduler's polling interval.
_TOLERANCE = timedelta(minutes=1)


async def process_time_based_reminders(db: Session) -> int:
    """Find due reminders, send them, and mark them as sent. Returns count sent."""
    now = datetime.now(timezone.utc)
    sent_count = 0

    upcoming_matches = (
        db.query(Match)
        .filter(Match.match_date > now, Match.match_date <= now + timedelta(hours=1, minutes=2))
        .all()
    )

    for match in upcoming_matches:
        time_to_kickoff = match.match_date - now
        for offset, flag_name, label in _REMINDER_WINDOWS:
            if abs(time_to_kickoff - offset) > _TOLERANCE:
                continue

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
            if not notifications:
                continue

            text = (
                f"\u23F0 Reminder: <b>{match.home_team.name} vs {match.away_team.name}</b> "
                f"{label}.\nUse /start \u2192 Today's Matches to open it and watch."
            )
            for notification in notifications:
                user: User = notification.user
                await telegram_client.send_message(user.telegram_id, text)
                setattr(notification, flag_name, True)
                sent_count += 1
            db.commit()

    return sent_count
