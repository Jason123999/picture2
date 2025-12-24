from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    tenant_id: int
    email: EmailStr
    full_name: str | None = None
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
