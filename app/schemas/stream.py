from pydantic import BaseModel, ConfigDict

from app.models.enums import StreamType


class StreamBase(BaseModel):
    language: str
    quality: str
    stream_type: StreamType
    url: str
    is_active: bool = True
    sort_order: int = 0


class StreamCreate(StreamBase):
    pass


class StreamUpdate(BaseModel):
    language: str | None = None
    quality: str | None = None
    stream_type: StreamType | None = None
    url: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class StreamOut(StreamBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    match_id: int
    label: str
