from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_current_tenant, get_current_user
from app.models import Tenant, User
from app.schemas.upload import UploadResponse
from app.services.storage import get_storage_backend

router = APIRouter()


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    user: User = Depends(get_current_user),
) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename required")

    data = await file.read()
    storage = get_storage_backend()

    storage_key = f"tenants/{tenant.id}/uploads/{user.id}/{file.filename}"
    stored = await storage.upload_file(
        key=storage_key,
        data=data,
        content_type=file.content_type or "application/octet-stream",
    )

    return UploadResponse(
        storage_key=stored.key,
        url=stored.url,
        local_path=stored.url,
        filename=file.filename,
    )
