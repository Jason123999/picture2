from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.core.config import get_settings
from app.models import User
from app.schemas.provisioning import ProvisionTenantRequest, ProvisionTenantResponse
from app.services.provisioning.service import provision_tenant_with_admin
from app.services.vercel.client import VercelClient, VercelError

router = APIRouter()


@router.get("/deploy-check", status_code=status.HTTP_200_OK)
async def deploy_check(
    current_user: User = Depends(get_current_user),
) -> dict:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")

    settings = get_settings()
    missing: list[str] = []

    # Effective CORS regex (app.main has a default for production)
    cors_effective_regex: str | None = settings.cors_allow_origin_regex
    if settings.env != "local" and not cors_effective_regex:
        cors_effective_regex = r"^https://([a-z0-9-]+\.)*vercel\.app$"
    cors_ok = settings.env == "local" or bool(cors_effective_regex)

    # Core
    if not settings.jwt_secret_key or settings.jwt_secret_key == "change-me":
        missing.append("JWT_SECRET_KEY")

    # DB
    if not settings.database_url or "REPLACE_WITH" in str(settings.database_url):
        missing.append("DATABASE_URL")

    # Storage (Supabase)
    if settings.storage_backend == "supabase":
        if not settings.supabase_url:
            missing.append("SUPABASE_URL")
        if not settings.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if not settings.supabase_storage_bucket:
            missing.append("SUPABASE_STORAGE_BUCKET")
        # SUPABASE_PUBLIC_URL can be derived from SUPABASE_URL + bucket
        if settings.supabase_url and settings.supabase_storage_bucket:
            supabase_public_url_effective = (
                settings.supabase_public_url
                or f"{str(settings.supabase_url).rstrip('/')}/storage/v1/object/public/{settings.supabase_storage_bucket}"
            )
        else:
            supabase_public_url_effective = settings.supabase_public_url
        if not supabase_public_url_effective:
            missing.append("SUPABASE_PUBLIC_URL")

    # Vercel provisioning (Option 1)
    if settings.vercel_token:
        if not settings.vercel_git_repo:
            missing.append("VERCEL_GIT_REPO")
        elif "/" not in str(settings.vercel_git_repo):
            missing.append("VERCEL_GIT_REPO (format: <org>/<repo>)")
        if not settings.vercel_frontend_api_base_url:
            missing.append("VERCEL_FRONTEND_API_BASE_URL")
        elif not str(settings.vercel_frontend_api_base_url).rstrip("/").endswith("/api"):
            missing.append("VERCEL_FRONTEND_API_BASE_URL (must include /api)")

    ok = len(missing) == 0

    return {
        "ok": ok,
        "missing": missing,
        "env": settings.env,
        "storage_backend": settings.storage_backend,
        "cors_allow_origin_regex": settings.cors_allow_origin_regex,
        "cors_effective_origin_regex": cors_effective_regex,
        "cors_ok": cors_ok,
        "vercel_enabled": bool(settings.vercel_token),
        "vercel_git_repo": settings.vercel_git_repo,
        "vercel_frontend_api_base_url": settings.vercel_frontend_api_base_url,
        "supabase_url": str(settings.supabase_url) if settings.supabase_url else None,
        "supabase_storage_bucket": settings.supabase_storage_bucket,
        "supabase_public_url": settings.supabase_public_url,
        "supabase_public_url_effective": supabase_public_url_effective,
    }


@router.post("/provision", response_model=ProvisionTenantResponse, status_code=status.HTTP_201_CREATED)
async def provision_tenant(
    payload: ProvisionTenantRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> ProvisionTenantResponse:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser required")

    try:
        tenant, admin_user = await provision_tenant_with_admin(
            session=session,
            tenant_name=payload.tenant_name,
            tenant_slug=payload.tenant_slug,
            admin_email=str(payload.admin_email),
            admin_password=payload.admin_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    settings = get_settings()
    site_url: str | None = None
    site_url_stable: str | None = None
    site_url_immediate: str | None = None
    vercel_project_id: str | None = None
    deployment_url: str | None = None

    # Option 1: auto create a per-tenant Vercel site (<tenant>.vercel.app)
    if settings.vercel_token and not (settings.vercel_git_repo and settings.vercel_frontend_api_base_url):
        raise HTTPException(
            status_code=400,
            detail="Vercel provisioning config incomplete: require VERCEL_GIT_REPO and VERCEL_FRONTEND_API_BASE_URL",
        )

    if settings.vercel_token and settings.vercel_git_repo and settings.vercel_frontend_api_base_url:
        if not str(settings.vercel_frontend_api_base_url).rstrip("/").endswith("/api"):
            raise HTTPException(
                status_code=400,
                detail="VERCEL_FRONTEND_API_BASE_URL must include '/api'",
            )

        project_name = f"{payload.tenant_slug}".lower()
        # Vercel project names have length limits; keep it short.
        project_name = project_name[:80]

        client = VercelClient(
            token=settings.vercel_token,
            team_id=settings.vercel_team_id,
            team_slug=settings.vercel_team_slug,
        )

        try:
            try:
                project = await client.create_project(
                    name=project_name,
                    framework="nextjs",
                    git_repo=settings.vercel_git_repo,
                    git_provider=settings.vercel_git_provider,
                    root_directory=settings.vercel_frontend_root_dir,
                )
            except VercelError as exc:
                if exc.status_code in (400, 409):
                    project = await client.get_project(id_or_name=project_name)
                else:
                    raise
            vercel_project_id = project.id

            await client.upsert_env_vars(
                project_id_or_name=project.id,
                variables={
                    "NEXT_PUBLIC_API_BASE_URL": settings.vercel_frontend_api_base_url,
                    "NEXT_PUBLIC_TENANT_SLUG": payload.tenant_slug,
                },
                target=["production", "preview"],
                var_type="plain",
            )

            if "/" in settings.vercel_git_repo:
                git_org, git_repo = settings.vercel_git_repo.split("/", 1)
            else:
                raise VercelError("VERCEL_GIT_REPO must be in the form <org>/<repo>")

            deployment = await client.create_deployment_from_git(
                project_name=project.name,
                project_id=project.id,
                git_org=git_org,
                git_repo=git_repo,
                git_ref=settings.vercel_git_ref,
                git_provider=settings.vercel_git_provider,
                target="production",
            )
            deployment_url = f"https://{deployment.url}"
            site_url = f"https://{project.name}.vercel.app"
            site_url_stable = site_url
            site_url_immediate = deployment_url
        except VercelError as exc:
            raise HTTPException(status_code=502, detail=str(exc))
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Vercel provisioning failed: {exc}")

    return ProvisionTenantResponse(
        tenant_id=tenant.id,
        admin_user_id=admin_user.id,
        login_email=payload.admin_email,
        site_url=site_url,
        site_url_stable=site_url_stable,
        site_url_immediate=site_url_immediate,
        vercel_project_id=vercel_project_id,
        deployment_url=deployment_url,
    )
