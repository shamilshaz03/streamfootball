from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import MatchStatus


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))

    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    venue: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "Group A", "Quarter Final"

    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status"), default=MatchStatus.SCHEDULED, index=True
    )
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    tournament = relationship("Tournament", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")

    streams = relationship(
        "Stream", back_populates="match", cascade="all, delete-orphan", order_by="Stream.sort_order"
    )
    notifications = relationship("Notification", back_populates="match", cascade="all, delete-orphan")
    highlight = relationship("Highlight", back_populates="match", uselist=False, cascade="all, delete-orphan")
    broadcast_messages = relationship(
        "BroadcastMessage", back_populates="match", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Match {self.home_team_id} vs {self.away_team_id} @ {self.match_date}>"
