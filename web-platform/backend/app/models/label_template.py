from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel


class LabelTemplate(SQLModel, table=True):
    __tablename__ = "label_templates"

    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id", nullable=False, index=True)
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    top_left: Optional[str] = Field(default=None)
    top_right: Optional[str] = Field(default=None)
    bottom_left: Optional[str] = Field(default=None)
    bottom_right: Optional[str] = Field(default=None)

    font_size: Optional[int] = Field(default=None)
    font_color: Optional[str] = Field(default="#000000")

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    tenant: "Tenant" = Relationship(
        sa_relationship=relationship("Tenant", back_populates="label_templates")
    )
