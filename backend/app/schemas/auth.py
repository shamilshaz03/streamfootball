from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import AdminRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminUserBase(BaseModel):
    username: str
    email: EmailStr
    role: AdminRole = AdminRole.MODERATOR
    is_active: bool = True


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    role: AdminRole | None = None
    is_active: bool | None = None
    password: str | None = None


class AdminUserOut(AdminUserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    last_login_at: datetime | None = None
