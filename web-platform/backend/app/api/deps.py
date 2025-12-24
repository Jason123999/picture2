from __future__ import annotations

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.config import get_settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models import Tenant, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    request: Request = None,  # type: ignore[assignment]
    session: AsyncSession = Depends(get_db_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
    except (ValueError, JWTError):
        raise credentials_exception

    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    if user_id is None or tenant_id is None:
        raise credentials_exception

    user = await session.get(User, int(user_id))
    if user is None or user.tenant_id != int(tenant_id):
        raise credentials_exception

    # If request is scoped to a tenant by Host/header, enforce it.
    if request is not None:
        scoped = await resolve_request_tenant(session=session, request=request)
        if scoped is not None and scoped.id != user.tenant_id:
            raise credentials_exception
    return user


def _extract_host(request: Request) -> str:
    host = request.headers.get("host", "").strip().lower()
    # remove port
    if ":" in host:
        host = host.split(":", 1)[0]
    return host


def _extract_origin_host(request: Request) -> str:
    origin = (request.headers.get("origin") or request.headers.get("referer") or "").strip()
    if not origin:
        return ""
    # origin like https://tenant.example.com or https://tenant.example.com/path
    if "//" in origin:
        origin = origin.split("//", 1)[1]
    origin = origin.split("/", 1)[0]
    origin = origin.strip().lower()
    if ":" in origin:
        origin = origin.split(":", 1)[0]
    return origin


def _extract_tenant_slug_from_host(host: str, root_domain: str, app_subdomain: str, api_subdomain: str) -> Optional[str]:
    if not host or not root_domain:
        return None

    root_domain = root_domain.strip().lower()
    if host == root_domain:
        return None

    # Ignore app/api subdomains
    if host == f"{app_subdomain}.{root_domain}" or host == f"{api_subdomain}.{root_domain}":
        return None

    suffix = f".{root_domain}"
    if host.endswith(suffix):
        sub = host[: -len(suffix)]
        # take left-most label as tenant slug
        if sub and "." not in sub:
            return sub
    return None


async def resolve_request_tenant(*, session: AsyncSession, request: Request) -> Optional[Tenant]:
    settings = get_settings()

    # 1) Header override (useful for local dev / API calls)
    header_name = settings.tenant_header_name
    tenant_slug = request.headers.get(header_name) or request.headers.get(header_name.lower())
    if tenant_slug:
        result = await session.exec(select(Tenant).where(Tenant.slug == tenant_slug))
        return result.first()

    # 2) Try infer from Origin/Referer (important when API is hosted on api.<root_domain>)
    origin_host = _extract_origin_host(request)
    if settings.platform_root_domain and origin_host:
        slug = _extract_tenant_slug_from_host(
            origin_host,
            settings.platform_root_domain,
            settings.platform_app_subdomain,
            settings.platform_api_subdomain,
        )
        if slug:
            result = await session.exec(select(Tenant).where(Tenant.slug == slug))
            return result.first()

    host = _extract_host(request)

    # 2) Custom domain
    result = await session.exec(select(Tenant).where(Tenant.custom_domain == host))
    tenant = result.first()
    if tenant is not None:
        return tenant

    # 3) Wildcard subdomain <slug>.<root_domain>
    if settings.platform_root_domain:
        slug = _extract_tenant_slug_from_host(
            host,
            settings.platform_root_domain,
            settings.platform_app_subdomain,
            settings.platform_api_subdomain,
        )
        if slug:
            result = await session.exec(select(Tenant).where(Tenant.slug == slug))
            return result.first()

    return None


async def get_current_tenant(
    user: User = Depends(get_current_user),
    request: Request = None,  # type: ignore[assignment]
    session: AsyncSession = Depends(get_db_session),
) -> Tenant:
    if request is not None:
        scoped = await resolve_request_tenant(session=session, request=request)
        if scoped is not None:
            if scoped.id != user.tenant_id:
                raise HTTPException(status_code=403, detail="Invalid tenant scope")
            return scoped

    tenant = await session.get(Tenant, user.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant
