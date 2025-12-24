from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:  # pragma: no cover
    from app.models.image_asset import ImageAsset
    from app.models.label_template import LabelTemplate
    from app.models.processing_task import ProcessingTask
    from app.models.user import User


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False)
    slug: str = Field(index=True, unique=True, nullable=False)
    custom_domain: Optional[str] = Field(default=None, unique=True, index=True)

    contact_email: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    users: list["User"] = Relationship(
        sa_relationship=relationship("User", back_populates="tenant")
    )
    image_assets: list["ImageAsset"] = Relationship(
        sa_relationship=relationship("ImageAsset", back_populates="tenant")
    )
    processing_tasks: list["ProcessingTask"] = Relationship(
        sa_relationship=relationship("ProcessingTask", back_populates="tenant")
    )
    label_templates: list["LabelTemplate"] = Relationship(
        sa_relationship=relationship("LabelTemplate", back_populates="tenant")
    )
