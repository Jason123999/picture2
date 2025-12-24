from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models import Tenant, User
from app.schemas import TenantCreate, TenantRead

router = APIRouter()


@router.post("/", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TenantRead:
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Only superusers can create tenants")
    existing_slug = await session.exec(select(Tenant).where(Tenant.slug == tenant_in.slug))
    if existing_slug.first():
        raise HTTPException(status_code=400, detail="Slug already exists")

    if tenant_in.custom_domain:
        existing_domain = await session.exec(
            select(Tenant).where(Tenant.custom_domain == tenant_in.custom_domain)
        )
        if existing_domain.first():
            raise HTTPException(status_code=400, detail="Custom domain already in use")

    tenant = Tenant(**tenant_in.model_dump())
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return TenantRead.model_validate(tenant)


@router.get("/", response_model=List[TenantRead])
async def list_tenants(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[TenantRead]:
    if user.is_superuser:
        result = await session.exec(select(Tenant))
        tenants = result.all()
    else:
        tenant = await session.get(Tenant, user.tenant_id)
        tenants = [tenant] if tenant is not None else []
    return [TenantRead.model_validate(t) for t in tenants]
