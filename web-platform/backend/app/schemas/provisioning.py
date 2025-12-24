from __future__ import annotations

from pydantic import BaseModel, EmailStr


class ProvisionTenantRequest(BaseModel):
    tenant_name: str
    tenant_slug: str
    admin_email: EmailStr
    admin_password: str


class ProvisionTenantResponse(BaseModel):
    tenant_id: int
    admin_user_id: int
    login_email: EmailStr
    site_url: str | None = None
    site_url_stable: str | None = None
    site_url_immediate: str | None = None
    vercel_project_id: str | None = None
    deployment_url: str | None = None
