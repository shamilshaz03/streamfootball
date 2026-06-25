from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.models.standing import Standing
from app.models.tournament import Tournament
from app.schemas.misc import StandingOut, StandingUpsert
from app.services.audit_service import log_action

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("", response_model=list[StandingOut])
def get_standings(tournament_id: int, group_id: int | None = None, db: Session = Depends(get_db)):
    """Used by the bot's 'Points Table' / 'Team Standings' menu items."""
    query = (
        db.query(Standing)
        .options(joinedload(Standing.team))
        .filter(Standing.tournament_id == tournament_id)
    )
    if group_id:
        query = query.filter(Standing.group_id == group_id)
    standings = query.all()
    standings.sort(key=lambda s: (-s.points, -(s.goals_for - s.goals_against), s.team.name))
    return standings


@router.put("", response_model=StandingOut)
def upsert_standing(
    payload: StandingUpsert,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    """Manual admin edit of a single team's row (in addition to FIFA data sync)."""
    if not db.get(Tournament, payload.tournament_id):
        raise HTTPException(status_code=404, detail="Tournament not found")

    standing = db.query(Standing).filter(Standing.team_id == payload.team_id).one_or_none()
    if standing is None:
        standing = Standing(team_id=payload.team_id)
        db.add(standing)
    for field, value in payload.model_dump().items():
        setattr(standing, field, value)
    db.commit()
    log_action(db, admin.id, "upsert", "standing", standing.id, request=request)
    return standing
