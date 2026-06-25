from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TournamentType


class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    pass


class GroupOut(GroupBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tournament_id: int


class TournamentBase(BaseModel):
    name: str
    slug: str
    season: str | None = None
    type: TournamentType = TournamentType.GROUP_KNOCKOUT
    logo_url: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = True


class TournamentCreate(TournamentBase):
    pass


class TournamentUpdate(BaseModel):
    name: str | None = None
    season: str | None = None
    type: TournamentType | None = None
    logo_url: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class TournamentOut(TournamentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class TeamBase(BaseModel):
    name: str
    short_name: str | None = None
    country_code: str | None = None
    logo_url: str | None = None
    group_id: int | None = None


class TeamCreate(TeamBase):
    tournament_id: int


class TeamUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    country_code: str | None = None
    logo_url: str | None = None
    group_id: int | None = None


class TeamOut(TeamBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tournament_id: int
