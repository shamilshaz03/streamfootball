from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole, MatchStatus
from app.models.highlight import Highlight
from app.models.match import Match
from app.models.tournament import Tournament
from app.models.team import Team
from app.redis_client import cache_delete_prefix
from app.schemas.match import MatchCreate, MatchDetailOut, MatchOut, MatchStatusUpdate, MatchUpdate
from app.services.audit_service import log_action
from app.services.broadcast_service import broadcast_match_status

router = APIRouter(prefix="/matches", tags=["Matches"])


def _with_relations(query):
    return query.options(
        joinedload(Match.home_team), joinedload(Match.away_team), joinedload(Match.highlight)
    )


def _to_detail(match: Match) -> MatchDetailOut:
    return MatchDetailOut(
        **MatchOut.model_validate(match).model_dump(),
        home_team=match.home_team,
        away_team=match.away_team,
        streams=[s for s in match.streams if s.is_active],
        has_highlight=match.highlight is not None,
    )


@router.get("/today", response_model=list[MatchDetailOut])
def today_matches(db: Session = Depends(get_db)):
    """Used by the bot's 'Today's Matches' menu item."""
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    matches = (
        _with_relations(db.query(Match))
        .filter(Match.match_date >= start, Match.match_date < end)
        .order_by(Match.match_date)
        .all()
    )
    return [_to_detail(m) for m in matches]


@router.get("/upcoming", response_model=list[MatchDetailOut])
def upcoming_matches(db: Session = Depends(get_db)):
    """Used by the bot's 'Upcoming Matches' menu item (future, not today)."""
    now = datetime.now(timezone.utc)
    matches = (
        _with_relations(db.query(Match))
        .filter(Match.match_date > now, Match.status == MatchStatus.SCHEDULED)
        .order_by(Match.match_date)
        .limit(50)
        .all()
    )
    return [_to_detail(m) for m in matches]


@router.get("/live", response_model=list[MatchDetailOut])
def live_matches(db: Session = Depends(get_db)):
    """Used by the bot's 'Live Matches' menu item."""
    matches = (
        _with_relations(db.query(Match))
        .filter(Match.status.in_([MatchStatus.LIVE, MatchStatus.HALFTIME]))
        .order_by(Match.match_date)
        .all()
    )
    return [_to_detail(m) for m in matches]


@router.get("", response_model=list[MatchDetailOut])
def list_matches(
    tournament_id: int | None = None,
    status_filter: MatchStatus | None = None,
    db: Session = Depends(get_db),
):
    """General-purpose listing used by the admin dashboard's Matches page."""
    query = _with_relations(db.query(Match))
    if tournament_id:
        query = query.filter(Match.tournament_id == tournament_id)
    if status_filter:
        query = query.filter(Match.status == status_filter)
    matches = query.order_by(Match.match_date.desc()).all()
    return [_to_detail(m) for m in matches]


@router.get("/{match_id}", response_model=MatchDetailOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """Used by the bot's 'Match Details' view."""
    match = _with_relations(db.query(Match)).filter(Match.id == match_id).one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return _to_detail(match)


@router.post("", response_model=MatchOut, status_code=201)
def create_match(
    payload: MatchCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    if not db.get(Tournament, payload.tournament_id):
        raise HTTPException(status_code=404, detail="Tournament not found")
    for team_id in (payload.home_team_id, payload.away_team_id):
        if not db.get(Team, team_id):
            raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    match = Match(**payload.model_dump())
    db.add(match)
    db.commit()
    cache_delete_prefix("matches:")
    log_action(db, admin.id, "create", "match", match.id, request=request)
    return match


@router.put("/{match_id}", response_model=MatchOut)
def update_match(
    match_id: int,
    payload: MatchUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(match, field, value)
    db.commit()
    cache_delete_prefix("matches:")
    log_action(db, admin.id, "update", "match", match_id, request=request)
    return match


@router.patch("/{match_id}/status", response_model=MatchOut)
def update_match_status(
    match_id: int,
    payload: MatchStatusUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MODERATOR)),
):
    """
    Dedicated endpoint for the common "set status" action (Live / Half Time /
    Finished / Postponed / Cancelled). Triggers subscriber notifications and
    the public channel broadcast in the background so the API responds fast.
    """
    match = (
        db.query(Match)
        .options(joinedload(Match.home_team), joinedload(Match.away_team))
        .filter(Match.id == match_id)
        .one_or_none()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match.status = payload.status
    if payload.home_score is not None:
        match.home_score = payload.home_score
    if payload.away_score is not None:
        match.away_score = payload.away_score
    db.commit()
    cache_delete_prefix("matches:")
    log_action(
        db, admin.id, "status_update", "match", match_id,
        details={"status": payload.status.value}, request=request,
    )

    background_tasks.add_task(_broadcast_in_background, match_id)
    return match


def _broadcast_in_background(match_id: int) -> None:
    import asyncio

    from app.database import SessionLocal

    async def _run():
        db = SessionLocal()
        try:
            match = (
                db.query(Match)
                .options(joinedload(Match.home_team), joinedload(Match.away_team))
                .filter(Match.id == match_id)
                .one_or_none()
            )
            if match:
                await broadcast_match_status(db, match)
        finally:
            db.close()

    asyncio.run(_run())


@router.delete("/{match_id}", status_code=204)
def delete_match(
    match_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
    cache_delete_prefix("matches:")
    log_action(db, admin.id, "delete", "match", match_id, request=request)
