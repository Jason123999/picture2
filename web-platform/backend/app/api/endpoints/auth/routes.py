from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db_session, resolve_request_tenant
from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import Tenant, User
from app.schemas.auth import TokenResponse, UserCreate, UserRead

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    existing_user = await session.exec(select(User).where(User.email == payload.email))
    if existing_user.first():
        raise HTTPException(status_code=400, detail="Email already registered")

    tenant = await session.get(Tenant, payload.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    user = User(
        tenant_id=payload.tenant_id,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        is_active=True,
        is_superuser=payload.is_superuser or False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return UserRead.model_validate(user)


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    settings = get_settings()

    # Resolve tenant from Host/header first.
    tenant = await resolve_request_tenant(session=session, request=request)

    # If not found, allow tenant_slug as extra form field.
    if tenant is None:
        form = await request.form()
        tenant_slug = form.get("tenant_slug")
        if tenant_slug:
            result = await session.exec(select(Tenant).where(Tenant.slug == str(tenant_slug)))
            tenant = result.first()

    user: User | None = None

    if tenant is not None:
        result = await session.exec(
            select(User).where(User.email == form_data.username, User.tenant_id == tenant.id)
        )
        user = result.first()
    elif settings.env == "local":
        # Local convenience: if tenant is not provided, infer from the email.
        result = await session.exec(select(User).where(User.email == form_data.username))
        user = result.first()
        if user is not None:
            tenant = await session.get(Tenant, user.tenant_id)

    if tenant is None or user is None:
        raise HTTPException(status_code=400, detail="Tenant is required")

    if not tenant.is_active:
        raise HTTPException(status_code=403, detail="Tenant is inactive")

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token(
        subject=str(user.id),
        extra_claims={"tenant_id": user.tenant_id, "tenant_slug": tenant.slug, "email": user.email},
    )
    return TokenResponse(access_token=token, token_type="bearer")
