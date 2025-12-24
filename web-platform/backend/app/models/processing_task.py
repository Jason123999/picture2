from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.image_asset import ImageAsset
    from app.models.tenant import Tenant


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingTask(SQLModel, table=True):
    __tablename__ = "processing_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", nullable=False, index=True)
    image_asset_id: int = Field(foreign_key="image_assets.id", nullable=False, index=True)

    status: TaskStatus = Field(default=TaskStatus.PENDING, nullable=False, index=True)
    error_message: Optional[str] = Field(default=None)
    result_path: Optional[str] = Field(default=None)
    config_path: Optional[str] = Field(default=None)
    output_dir: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    tenant: "Tenant" = Relationship(
        sa_relationship=relationship("Tenant", back_populates="processing_tasks")
    )
    image_asset: "ImageAsset" = Relationship(
        sa_relationship=relationship("ImageAsset", back_populates="tasks")
    )
