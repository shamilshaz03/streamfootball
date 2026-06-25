from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.admin import AdminUser
from app.models.enums import MatchStatus
from app.models.match import Match
from app.models.notification import Notification
from app.models.stream import Stream
from app.models.tournament import Tournament
from app.models.user import User
from app.schemas.misc import DashboardMetrics
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db), admin: AdminUser = Depends(get_current_admin)):
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    return DashboardMetrics(
        total_users=db.query(func.count(User.id)).scalar() or 0,
        live_matches=db.query(func.count(Match.id))
        .filter(Match.status.in_([MatchStatus.LIVE, MatchStatus.HALFTIME]))
        .scalar()
        or 0,
        upcoming_matches_today=db.query(func.count(Match.id))
        .filter(Match.match_date >= start_of_day, Match.match_date < end_of_day)
        .scalar()
        or 0,
        active_notifications=db.query(func.count(Notification.id))
        .filter(Notification.is_active.is_(True))
        .scalar()
        or 0,
        total_streams=db.query(func.count(Stream.id)).scalar() or 0,
        total_tournaments=db.query(func.count(Tournament.id)).filter(Tournament.is_active.is_(True)).scalar()
        or 0,
    )
