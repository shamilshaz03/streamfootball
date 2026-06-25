from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.tournament import TeamOut


class StandingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tournament_id: int
    group_id: int | None = None
    team: TeamOut
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    position: int | None = None


class StandingUpsert(BaseModel):
    """Used by the FIFA data sync service and by manual admin edits."""

    tournament_id: int
    group_id: int | None = None
    team_id: int
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0
    position: int | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    is_blocked: bool
    created_at: datetime


class UserUpsert(BaseModel):
    """Used by the bot to register/update a Telegram user on every interaction."""

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language_code: str | None = None


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    match_id: int
    is_active: bool
    created_at: datetime


class NotificationSubscribe(BaseModel):
    telegram_id: int
    match_id: int


class HighlightBase(BaseModel):
    youtube_url: str
    title: str | None = None
    thumbnail_url: str | None = None


class HighlightCreate(HighlightBase):
    match_id: int


class HighlightUpdate(BaseModel):
    youtube_url: str | None = None
    title: str | None = None
    thumbnail_url: str | None = None


class HighlightOut(HighlightBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    match_id: int
    created_at: datetime


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    admin_id: int | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    details: dict | None = None
    ip_address: str | None = None
    created_at: datetime


class DashboardMetrics(BaseModel):
    total_users: int
    live_matches: int
    upcoming_matches_today: int
    active_notifications: int
    total_streams: int
    total_tournaments: int


class SettingOut(BaseModel):
    key: str
    value: str


class SettingUpdate(BaseModel):
    value: str
