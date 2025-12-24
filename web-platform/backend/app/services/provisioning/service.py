from __future__ import annotations

import json
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import get_password_hash
from app.models import Tenant, User
from app.services.storage import get_storage_backend


async def provision_tenant_with_admin(
    *,
    session: AsyncSession,
    tenant_name: str,
    tenant_slug: str,
    admin_email: str,
    admin_password: str,
) -> tuple[Tenant, User]:
    existing = await session.exec(select(Tenant).where(Tenant.slug == tenant_slug))
    tenant = existing.first()
    if tenant is None:
        tenant = Tenant(
            name=tenant_name,
            slug=tenant_slug,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)

    existing_user_same_tenant = await session.exec(
        select(User).where(User.email == admin_email, User.tenant_id == tenant.id)
    )
    user = existing_user_same_tenant.first()
    if user is None:
        existing_any = await session.exec(select(User).where(User.email == admin_email))
        any_user = existing_any.first()
        if any_user is not None and any_user.tenant_id != tenant.id:
            raise ValueError("Email already belongs to another tenant")
    if user is None:
        user = User(
            tenant_id=tenant.id,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name="Tenant Admin",
            is_active=True,
            is_superuser=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    # Initialize tenant folders & default config in storage
    storage = get_storage_backend()

    default_config = {
        "crop_settings": {
            "auto_detect": False,
            "uniform_crop": {"left": 0, "top": 0, "width": 1000, "height": 1000},
            "allow_resize_all": False,
        },
        "image_settings": {
            "size_cm": 5.41,
            "dpi": 300,
        },
        "label_settings": {
            "sample_labels": {
                "top_left": "标签1",
                "top_right": "标签2",
                "bottom_left": "标签3",
                "bottom_right": "标签4",
            },
            "font_size": 13,
            "font_color": "#FFFFFF",
        },
        "ppt_settings": {
            "columns": 4,
            "rows": 2,
            "column_spacing_cm": 0.17,
            "row_spacing_cm": 0.17,
        },
    }

    await storage.upload_file(
        key=f"tenants/{tenant.id}/config/config.json",
        data=json.dumps(default_config, ensure_ascii=False, indent=2).encode("utf-8"),
        content_type="application/json",
    )

    # Create a placeholder marker so folders exist in object storage UIs
    await storage.upload_file(
        key=f"tenants/{tenant.id}/.init",
        data=b"ok",
        content_type="text/plain",
    )

    return tenant, user
