from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import MatchStatus
from app.schemas.stream import StreamOut
from app.schemas.tournament import TeamOut


class MatchBase(BaseModel):
    tournament_id: int
    home_team_id: int
    away_team_id: int
    match_date: datetime
    venue: str | None = None
    stage: str | None = None
    thumbnail_url: str | None = None


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    tournament_id: int | None = None
    home_team_id: int | None = None
    away_team_id: int | None = None
    match_date: datetime | None = None
    venue: str | None = None
    stage: str | None = None
    thumbnail_url: str | None = None
    status: MatchStatus | None = None
    home_score: int | None = None
    away_score: int | None = None


class MatchStatusUpdate(BaseModel):
    status: MatchStatus
    home_score: int | None = None
    away_score: int | None = None


class MatchOut(MatchBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: MatchStatus
    home_score: int | None = None
    away_score: int | None = None
    created_at: datetime
    updated_at: datetime


class MatchDetailOut(MatchOut):
    """Used for the bot's 'Match Details' view: includes teams and streams."""

    home_team: TeamOut
    away_team: TeamOut
    streams: list[StreamOut] = []
    has_highlight: bool = False
