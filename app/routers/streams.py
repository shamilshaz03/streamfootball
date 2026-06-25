from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.models.match import Match
from app.models.stream import Stream
from app.redis_client import cache_delete_prefix
from app.schemas.stream import StreamCreate, StreamOut, StreamUpdate
from app.services.audit_service import log_action

router = APIRouter(tags=["Streams"])


@router.get("/streams", response_model=list[StreamOut])
def list_all_streams(db: Session = Depends(get_db)):
    """Global flat list, used by the admin dashboard's Streams page."""
    return db.query(Stream).options(joinedload(Stream.match)).order_by(Stream.match_id, Stream.sort_order).all()


@router.get("/matches/{match_id}/streams", response_model=list[StreamOut])
def list_match_streams(match_id: int, db: Session = Depends(get_db)):
    """Used by the bot's 'Watch Now' button to build the language/quality keyboard."""
    return (
        db.query(Stream)
        .filter(Stream.match_id == match_id, Stream.is_active.is_(True))
        .order_by(Stream.sort_order)
        .all()
    )


@router.post("/matches/{match_id}/streams", response_model=StreamOut, status_code=201)
def add_stream(
    match_id: int,
    payload: StreamCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    if not db.get(Match, match_id):
        raise HTTPException(status_code=404, detail="Match not found")
    stream = Stream(match_id=match_id, **payload.model_dump())
    db.add(stream)
    db.commit()
    cache_delete_prefix("matches:")
    log_action(db, admin.id, "create", "stream", stream.id, request=request)
    return stream


@router.put("/streams/{stream_id}", response_model=StreamOut)
def update_stream(
    stream_id: int,
    payload: StreamUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    stream = db.get(Stream, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(stream, field, value)
    db.commit()
    cache_delete_prefix("matches:")
    log_action(db, admin.id, "update", "stream", stream_id, request=request)
    return stream


@router.delete("/streams/{stream_id}", status_code=204)
def delete_stream(
    stream_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    stream = db.get(Stream, stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")
    db.delete(stream)
    db.commit()
    cache_delete_prefix("matches:")
    log_action(db, admin.id, "delete", "stream", stream_id, request=request)
