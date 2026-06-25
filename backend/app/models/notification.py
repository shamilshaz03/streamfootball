from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Notification(Base):
    """
    A user's subscription to alerts for a specific match ('Notify Me').

    Each boolean flag tracks whether that particular alert has already been
    sent, so the scheduler never sends the same reminder twice.
    """

    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("user_id", "match_id", name="uq_user_match_notification"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sent_1h: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_30m: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_15m: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_started: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_halftime: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_finished: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")
    match = relationship("Match", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification user_id={self.user_id} match_id={self.match_id}>"
