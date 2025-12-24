from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AssetBase(BaseModel):
    original_path: str
    processed_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    status: str = "uploaded"
    meta_json: Optional[str] = None


class AssetCreate(AssetBase):
    tenant_id: int


class AssetRead(AssetBase):
    id: int
    tenant_id: int
    uploaded_by_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
