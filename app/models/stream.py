from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import StreamType


class Stream(Base):
    """
    A single watchable stream for a match: one language + one quality + one URL.

    A match can have any number of these, e.g.:
        English 1080p, English 720p, Arabic 1080p, Malayalam 720p, Hindi 720p
    The bot auto-generates one button per row, ordered by sort_order.
    """

    __tablename__ = "streams"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), index=True)

    language: Mapped[str] = mapped_column(String(64), nullable=False)  # unlimited, free text
    quality: Mapped[str] = mapped_column(String(16), nullable=False)  # e.g. 1080p, 720p, 480p
    stream_type: Mapped[StreamType] = mapped_column(Enum(StreamType, name="stream_type"), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    match = relationship("Match", back_populates="streams")

    @property
    def label(self) -> str:
        """Button label shown in the bot, e.g. 'English 1080p'."""
        return f"{self.language} {self.quality}"

    def __repr__(self) -> str:
        return f"<Stream {self.label} match_id={self.match_id}>"
