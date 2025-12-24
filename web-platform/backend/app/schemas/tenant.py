from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class TenantBase(BaseModel):
    name: str
    slug: str
    custom_domain: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: bool = True


class TenantCreate(TenantBase):
    pass


class TenantRead(TenantBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
