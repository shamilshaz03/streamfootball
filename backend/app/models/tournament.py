from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import TournamentType


class Tournament(Base):
    """A competition, e.g. 'FIFA World Cup 2026'."""

    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    season: Mapped[str | None] = mapped_column(String(32), nullable=True)
    type: Mapped[TournamentType] = mapped_column(
        Enum(TournamentType, name="tournament_type"), default=TournamentType.GROUP_KNOCKOUT
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    groups = relationship("Group", back_populates="tournament", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="tournament", cascade="all, delete-orphan")
    standings = relationship("Standing", back_populates="tournament", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tournament {self.name}>"


class Group(Base):
    """A group within a group-stage tournament, e.g. 'Group A'."""

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(32), nullable=False)

    tournament = relationship("Tournament", back_populates="groups")
    teams = relationship("Team", back_populates="group")
    standings = relationship("Standing", back_populates="group")

    def __repr__(self) -> str:
        return f"<Group {self.name}>"
