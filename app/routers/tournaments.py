from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_admin, require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.models.tournament import Group, Tournament
from app.models.team import Team
from app.redis_client import cache_delete_prefix
from app.schemas.tournament import (
    GroupCreate,
    GroupOut,
    TeamCreate,
    TeamOut,
    TeamUpdate,
    TournamentCreate,
    TournamentOut,
    TournamentUpdate,
)
from app.services.audit_service import log_action

router = APIRouter(tags=["Tournaments"])


@router.get("/tournaments", response_model=list[TournamentOut])
def list_tournaments(db: Session = Depends(get_db)):
    return db.query(Tournament).order_by(Tournament.start_date.desc().nullslast()).all()


@router.post("/tournaments", response_model=TournamentOut, status_code=201)
def create_tournament(
    payload: TournamentCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    if db.query(Tournament).filter(Tournament.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="A tournament with this slug already exists")
    tournament = Tournament(**payload.model_dump())
    db.add(tournament)
    db.commit()
    log_action(db, admin.id, "create", "tournament", tournament.id, request=request)
    return tournament


@router.get("/tournaments/{tournament_id}", response_model=TournamentOut)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.put("/tournaments/{tournament_id}", response_model=TournamentOut)
def update_tournament(
    tournament_id: int,
    payload: TournamentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    tournament = db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tournament, field, value)
    db.commit()
    log_action(db, admin.id, "update", "tournament", tournament_id, request=request)
    return tournament


@router.delete("/tournaments/{tournament_id}", status_code=204)
def delete_tournament(
    tournament_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.SUPER_ADMIN)),
):
    tournament = db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    db.delete(tournament)
    db.commit()
    log_action(db, admin.id, "delete", "tournament", tournament_id, request=request)


@router.post("/tournaments/{tournament_id}/groups", response_model=GroupOut, status_code=201)
def create_group(
    tournament_id: int,
    payload: GroupCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    if not db.get(Tournament, tournament_id):
        raise HTTPException(status_code=404, detail="Tournament not found")
    group = Group(tournament_id=tournament_id, name=payload.name)
    db.add(group)
    db.commit()
    return group


@router.get("/tournaments/{tournament_id}/groups", response_model=list[GroupOut])
def list_groups(tournament_id: int, db: Session = Depends(get_db)):
    return db.query(Group).filter(Group.tournament_id == tournament_id).all()


# ---- Teams ----


@router.get("/teams", response_model=list[TeamOut])
def list_teams(tournament_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Team)
    if tournament_id:
        query = query.filter(Team.tournament_id == tournament_id)
    return query.order_by(Team.name).all()


@router.post("/teams", response_model=TeamOut, status_code=201)
def create_team(
    payload: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    if not db.get(Tournament, payload.tournament_id):
        raise HTTPException(status_code=404, detail="Tournament not found")
    team = Team(**payload.model_dump())
    db.add(team)
    db.commit()
    log_action(db, admin.id, "create", "team", team.id, request=request)
    return team


@router.put("/teams/{team_id}", response_model=TeamOut)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    db.commit()
    log_action(db, admin.id, "update", "team", team_id, request=request)
    return team


@router.delete("/teams/{team_id}", status_code=204)
def delete_team(
    team_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    log_action(db, admin.id, "delete", "team", team_id, request=request)
