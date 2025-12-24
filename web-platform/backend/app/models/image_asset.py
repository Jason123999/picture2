from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.processing_task import ProcessingTask
    from app.models.tenant import Tenant
    from app.models.user import User


class ImageAsset(SQLModel, table=True):
    __tablename__ = "image_assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", nullable=False, index=True)
    uploaded_by_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    original_path: str = Field(nullable=False)
    processed_path: Optional[str] = Field(default=None)
    thumbnail_path: Optional[str] = Field(default=None)

    status: str = Field(default="uploaded", index=True)
    meta_json: Optional[str] = Field(default=None, description="JSON metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    tenant: "Tenant" = Relationship(
        sa_relationship=relationship("Tenant", back_populates="image_assets")
    )
    uploaded_by: "User" = Relationship(sa_relationship=relationship("User"))
    tasks: list["ProcessingTask"] = Relationship(
        sa_relationship=relationship("ProcessingTask", back_populates="image_asset")
    )
