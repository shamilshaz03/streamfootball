"""
APScheduler wiring. One recurring job polls for due reminders every
30 seconds and sends them. Status-driven notifications (started, half
time, finished) are NOT scheduled here - they fire immediately from
`broadcast_service` when an admin updates the match status via the API,
since they are event-driven, not time-driven.
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import SessionLocal
from app.services.notification_service import process_time_based_reminders

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _run_reminder_job() -> None:
    db = SessionLocal()
    try:
        sent = await process_time_based_reminders(db)
        if sent:
            logger.info("Sent %s match reminders", sent)
    except Exception:  # pragma: no cover - defensive, scheduler must never crash
        logger.exception("Reminder job failed")
    finally:
        db.close()


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.add_job(_run_reminder_job, "interval", seconds=30, id="match_reminders", replace_existing=True)
        scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
