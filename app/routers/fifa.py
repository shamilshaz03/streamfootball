from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.models.tournament import Tournament
from app.services.audit_service import log_action
from app.services.fifa_provider.mock_provider import get_provider
from app.services.fifa_provider.sync_service import sync_tournament_data

router = APIRouter(prefix="/fifa", tags=["FIFA Data"])


@router.post("/sync/{tournament_id}")
def sync_fifa_data(
    tournament_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    """
    Pull teams, fixtures, results and standings from the active FIFA data
    provider into the database.  Idempotent — safe to run repeatedly.
    """
    tournament = db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    provider = get_provider()
    result = sync_tournament_data(db, tournament, provider)
    log_action(db, admin.id, "fifa_sync", "tournament", tournament_id, details=result, request=request)
    return {"status": "ok", "synced": result}
