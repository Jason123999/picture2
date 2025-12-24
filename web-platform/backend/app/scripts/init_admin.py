from __future__ import annotations

import asyncio
import os

from sqlmodel import select
from sqlalchemy import text

from app.core.security import get_password_hash
from app.db.session import async_engine, async_session
from app.models import Tenant, User


async def main() -> None:
    tenant_slug = os.getenv("INIT_TENANT_SLUG", "demo-tenant")
    tenant_name = os.getenv("INIT_TENANT_NAME", "Demo Tenant")
    admin_email = os.getenv("INIT_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("INIT_ADMIN_PASSWORD", "admin123456")

    from sqlmodel import SQLModel

    async with async_engine.begin() as conn:  # type: ignore[call-arg]
        await conn.run_sync(SQLModel.metadata.create_all)

        try:
            result = await conn.execute(text("PRAGMA table_info(image_assets)"))
            columns = [row[1] for row in result.fetchall()]
            if "metadata" in columns and "meta_json" not in columns:
                await conn.execute(
                    text("ALTER TABLE image_assets RENAME COLUMN metadata TO meta_json")
                )
        except Exception:
            pass

    try:
        async with async_session() as session:  # type: ignore[call-arg]
            existing = await session.exec(select(Tenant).where(Tenant.slug == tenant_slug))
            tenant = existing.first()
            if tenant is None:
                tenant = Tenant(name=tenant_name, slug=tenant_slug, is_active=True)
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
                    raise RuntimeError("INIT_ADMIN_EMAIL already belongs to another tenant")
            if user is None:
                user = User(
                    tenant_id=tenant.id,
                    email=admin_email,
                    hashed_password=get_password_hash(admin_password),
                    full_name="Admin",
                    is_active=True,
                    is_superuser=True,
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                # Always refresh password hash to match current hashing scheme
                # (e.g. migrating from bcrypt to pbkdf2_sha256)
                user.hashed_password = get_password_hash(admin_password)
                await session.commit()
                await session.refresh(user)

            print("初始化完成")
            print(f"Tenant: id={tenant.id} slug={tenant.slug}")
            print(f"Admin: id={user.id} email={user.email}")
    finally:
        # Ensure connections/worker threads are released so the process can exit.
        await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
