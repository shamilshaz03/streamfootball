from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.schemas.auth import AdminUserCreate, AdminUserOut, AdminUserUpdate
from app.security import hash_password
from app.services.audit_service import log_action

router = APIRouter(prefix="/admin-users", tags=["Admin Users"])


@router.get("", response_model=list[AdminUserOut])
def list_admin_users(
    db: Session = Depends(get_db), admin: AdminUser = Depends(require_role(AdminRole.SUPER_ADMIN))
):
    return db.query(AdminUser).order_by(AdminUser.created_at).all()


@router.post("", response_model=AdminUserOut, status_code=201)
def create_admin_user(
    payload: AdminUserCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.SUPER_ADMIN)),
):
    if db.query(AdminUser).filter(AdminUser.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    new_admin = AdminUser(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        is_active=payload.is_active,
        hashed_password=hash_password(payload.password),
    )
    db.add(new_admin)
    db.commit()
    log_action(db, admin.id, "create", "admin_user", new_admin.id, request=request)
    return new_admin


@router.put("/{admin_id}", response_model=AdminUserOut)
def update_admin_user(
    admin_id: int,
    payload: AdminUserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.SUPER_ADMIN)),
):
    target = db.get(AdminUser, admin_id)
    if not target:
        raise HTTPException(status_code=404, detail="Admin user not found")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        target.hashed_password = hash_password(data.pop("password"))
    for field, value in data.items():
        setattr(target, field, value)
    db.commit()
    log_action(db, admin.id, "update", "admin_user", admin_id, request=request)
    return target


@router.delete("/{admin_id}", status_code=204)
def delete_admin_user(
    admin_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.SUPER_ADMIN)),
):
    if admin_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    target = db.get(AdminUser, admin_id)
    if not target:
        raise HTTPException(status_code=404, detail="Admin user not found")
    db.delete(target)
    db.commit()
    log_action(db, admin.id, "delete", "admin_user", admin_id, request=request)
