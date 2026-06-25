from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Standing(Base):
    """One row of a points table for a team within a tournament (and optional group)."""

    __tablename__ = "standings"

    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"), index=True)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id", ondelete="SET NULL"), nullable=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), unique=True)

    played: Mapped[int] = mapped_column(Integer, default=0)
    won: Mapped[int] = mapped_column(Integer, default=0)
    drawn: Mapped[int] = mapped_column(Integer, default=0)
    lost: Mapped[int] = mapped_column(Integer, default=0)
    goals_for: Mapped[int] = mapped_column(Integer, default=0)
    goals_against: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tournament = relationship("Tournament", back_populates="standings")
    group = relationship("Group", back_populates="standings")
    team = relationship("Team", back_populates="standing")

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    def __repr__(self) -> str:
        return f"<Standing team_id={self.team_id} pts={self.points}>"
