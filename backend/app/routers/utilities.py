from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.admin import AdminUser
from app.models.audit_log import AuditLog
from app.models.enums import AdminRole
from app.models.setting import SystemSetting
from app.schemas.misc import AuditLogOut, SettingOut, SettingUpdate

router = APIRouter(tags=["Admin Utilities"])


# ── Audit Logs ──────────────────────────────────────────────────────────────

@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    entity_type: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    return query.order_by(AuditLog.id.desc()).limit(limit).all()


# ── Settings ────────────────────────────────────────────────────────────────

@router.get("/settings", response_model=list[SettingOut])
def list_settings(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.MANAGER)),
):
    return db.query(SystemSetting).all()


@router.put("/settings/{key}", response_model=SettingOut)
def upsert_setting(
    key: str,
    payload: SettingUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_role(AdminRole.SUPER_ADMIN)),
):
    setting = db.get(SystemSetting, key)
    if setting is None:
        setting = SystemSetting(key=key, value=payload.value)
        db.add(setting)
    else:
        setting.value = payload.value
    db.commit()
    return setting
