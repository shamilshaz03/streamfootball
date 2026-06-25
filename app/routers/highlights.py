from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.models.highlight import Highlight
from app.models.match import Match
from app.schemas.misc import HighlightCreate, HighlightOut, HighlightUpdate
from app.services.audit_service import log_action

router = APIRouter(tags=["Highlights"])


@router.get("/highlights", response_model=list[HighlightOut])
def list_highlights(db: Session = Depends(get_db)):
    return db.query(Highlight).order_by(Highlight.created_at.desc()).all()


@router.get("/matches/{match_id}/highlight", response_model=HighlightOut)
def get_match_highlight(match_id: int, db: Session = Depends(get_db)):
    """Used by the bot's 'Highlights' button on a finished match."""
    highlight = db.query(Highlight).filter(Highlight.match_id == match_id).one_or_none()
    if not highlight:
        raise HTTPException(status_code=404, detail="No highlight available for this match yet")
    return highlight


@router.post("/highlights", response_model=HighlightOut, status_code=201)
def create_highlight(
    payload: HighlightCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MODERATOR)),
):
    if not db.get(Match, payload.match_id):
        raise HTTPException(status_code=404, detail="Match not found")
    if db.query(Highlight).filter(Highlight.match_id == payload.match_id).first():
        raise HTTPException(status_code=400, detail="This match already has a highlight")
    highlight = Highlight(**payload.model_dump())
    db.add(highlight)
    db.commit()
    log_action(db, admin.id, "create", "highlight", highlight.id, request=request)
    return highlight


@router.put("/highlights/{highlight_id}", response_model=HighlightOut)
def update_highlight(
    highlight_id: int,
    payload: HighlightUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MODERATOR)),
):
    highlight = db.get(Highlight, highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(highlight, field, value)
    db.commit()
    log_action(db, admin.id, "update", "highlight", highlight_id, request=request)
    return highlight


@router.delete("/highlights/{highlight_id}", status_code=204)
def delete_highlight(
    highlight_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MODERATOR)),
):
    highlight = db.get(Highlight, highlight_id)
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    db.delete(highlight)
    db.commit()
    log_action(db, admin.id, "delete", "highlight", highlight_id, request=request)
