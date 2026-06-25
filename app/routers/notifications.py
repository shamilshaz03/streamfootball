from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin
from app.models.admin import AdminUser
from app.models.match import Match
from app.models.notification import Notification
from app.models.user import User
from app.schemas.misc import NotificationOut, NotificationSubscribe

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _get_or_create_user(db: Session, telegram_id: int) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.flush()
    return user


@router.post("/subscribe", response_model=NotificationOut, status_code=201)
def subscribe(payload: NotificationSubscribe, db: Session = Depends(get_db)):
    """Called by the bot when a user taps 'Notify Me'."""
    if not db.get(Match, payload.match_id):
        raise HTTPException(status_code=404, detail="Match not found")

    user = _get_or_create_user(db, payload.telegram_id)
    existing = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.match_id == payload.match_id)
        .one_or_none()
    )
    if existing:
        existing.is_active = True
        db.commit()
        return existing

    notification = Notification(user_id=user.id, match_id=payload.match_id)
    db.add(notification)
    db.commit()
    return notification


@router.delete("/unsubscribe", status_code=204)
def unsubscribe(telegram_id: int, match_id: int, db: Session = Depends(get_db)):
    """Called by the bot when a user taps 'Cancel Notification'."""
    user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()
    if not user:
        return
    notification = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.match_id == match_id)
        .one_or_none()
    )
    if notification:
        notification.is_active = False
        db.commit()


@router.get("/status")
def subscription_status(telegram_id: int, match_id: int, db: Session = Depends(get_db)):
    """Lets the bot show 'Notify Me' vs 'Cancel Notification' correctly."""
    user = db.query(User).filter(User.telegram_id == telegram_id).one_or_none()
    if not user:
        return {"subscribed": False}
    notification = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.match_id == match_id,
            Notification.is_active.is_(True),
        )
        .one_or_none()
    )
    return {"subscribed": notification is not None}


@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), admin: AdminUser = Depends(get_current_admin)):
    """Admin dashboard's Notifications page: view active subscriptions."""
    return db.query(Notification).filter(Notification.is_active.is_(True)).all()
