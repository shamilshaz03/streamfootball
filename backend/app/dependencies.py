"""
FastAPI dependencies: DB session re-exported, current authenticated admin,
and a role-requirement factory used to protect sensitive endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdminUser
from app.models.enums import AdminRole
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Role hierarchy: super_admin > manager > moderator
_ROLE_RANK = {AdminRole.MODERATOR: 0, AdminRole.MANAGER: 1, AdminRole.SUPER_ADMIN: 2}


def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    admin_id = payload.get("sub")
    if admin_id is None:
        raise credentials_exception

    admin = db.get(AdminUser, int(admin_id))
    if admin is None or not admin.is_active:
        raise credentials_exception
    return admin


def require_role(minimum_role: AdminRole):
    """Dependency factory: require the current admin to hold at least this role."""

    def _checker(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
        if _ROLE_RANK[admin.role] < _ROLE_RANK[minimum_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {minimum_role.value} role or higher",
            )
        return admin

    return _checker
