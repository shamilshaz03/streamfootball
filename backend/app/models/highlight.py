from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import BroadcastType


class Highlight(Base):
    """A YouTube highlight link for a finished match."""

    __tablename__ = "highlights"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), unique=True)
    youtube_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="highlight")

    def __repr__(self) -> str:
        return f"<Highlight match_id={self.match_id}>"


class BroadcastMessage(Base):
    """
    Tracks the last Telegram message sent for a given match + broadcast type
    so that, when a newer update is broadcast (e.g. status changes again),
    the bot can delete the previous message before posting the new one
    instead of letting the chat fill up with stale updates.
    """

    __tablename__ = "broadcast_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), index=True)
    broadcast_type: Mapped[BroadcastType] = mapped_column(Enum(BroadcastType, name="broadcast_type"))
    telegram_chat_id: Mapped[int] = mapped_column(BigInteger)
    telegram_message_id: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="broadcast_messages")

    def __repr__(self) -> str:
        return f"<BroadcastMessage match_id={self.match_id} type={self.broadcast_type}>"
