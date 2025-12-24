from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_tenant, get_current_user, get_db_session
from app.models import ImageAsset, Tenant, User
from app.schemas.asset import AssetCreate, AssetRead

router = APIRouter()


@router.post("/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
    user: User = Depends(get_current_user),
) -> AssetRead:
    if payload.tenant_id != tenant.id:
        raise HTTPException(status_code=403, detail="Invalid tenant scope")

    asset = ImageAsset(
        tenant_id=tenant.id,
        uploaded_by_id=user.id,
        original_path=payload.original_path,
        processed_path=payload.processed_path,
        thumbnail_path=payload.thumbnail_path,
        status=payload.status,
        meta_json=payload.meta_json,
    )
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    return AssetRead.model_validate(asset)


@router.get("/", response_model=List[AssetRead])
async def list_assets(
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
) -> List[AssetRead]:
    result = await session.exec(
        select(ImageAsset).where(ImageAsset.tenant_id == tenant.id)
    )
    assets = result.all()
    return [AssetRead.model_validate(a) for a in assets]


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
) -> AssetRead:
    asset = await session.get(ImageAsset, asset_id)
    if asset is None or asset.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetRead.model_validate(asset)
