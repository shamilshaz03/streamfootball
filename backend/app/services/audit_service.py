"""
Audit logging helper. Call this after any create/update/delete performed
by an admin so every change is traceable.
"""
from typing import Any, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    admin_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[Any] = None,
    details: Optional[dict] = None,
    request: Optional[Request] = None,
) -> None:
    entry = AuditLog(
        admin_id=admin_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details,
        ip_address=request.client.host if request and request.client else None,
    )
    db.add(entry)
    db.commit()
