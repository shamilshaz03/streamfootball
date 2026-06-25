from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.misc import UserOut, UserUpsert

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/upsert", response_model=UserOut)
def upsert_user(payload: UserUpsert, db: Session = Depends(get_db)):
    """Called by the bot on every /start so we always have current user info."""
    user = db.query(User).filter(User.telegram_id == payload.telegram_id).one_or_none()
    if user:
        user.username = payload.username
        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.language_code = payload.language_code
    else:
        user = User(**payload.model_dump())
        db.add(user)
    db.commit()
    return user
