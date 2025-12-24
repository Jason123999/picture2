from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.processing_task import TaskStatus


class TaskCreate(BaseModel):
    tenant_id: int
    image_asset_id: int
    config_path: str | None = None
    output_dir: str | None = None


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    error_message: Optional[str] = None
    result_path: Optional[str] = None


class TaskRead(BaseModel):
    id: int
    tenant_id: int
    image_asset_id: int
    status: TaskStatus
    error_message: Optional[str]
    result_path: Optional[str]
    config_path: Optional[str]
    output_dir: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
