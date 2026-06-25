from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"))
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(10), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tournament = relationship("Tournament", back_populates="teams")
    group = relationship("Group", back_populates="teams")
    standing = relationship("Standing", back_populates="team", uselist=False, cascade="all, delete-orphan")

    home_matches = relationship(
        "Match", foreign_keys="Match.home_team_id", back_populates="home_team"
    )
    away_matches = relationship(
        "Match", foreign_keys="Match.away_team_id", back_populates="away_team"
    )

    def __repr__(self) -> str:
        return f"<Team {self.name}>"
