from functools import lru_cache
from typing import Any, Literal, Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application configuration."""

    env: Literal["local", "staging", "production"] = Field(
        default="local", description="Runtime environment identifier"
    )

    app_name: str = Field(default="Photo Platform Backend")
    api_v1_prefix: str = Field(default="/api")

    # Database configuration (default to local SQLite for bootstrap)
    # NOTE: Use str instead of AnyUrl because SQLAlchemy DSNs may contain custom schemes
    # like sqlite+aiosqlite.
    database_url: str = Field(
        default="sqlite+aiosqlite:///./app.db",
        description="SQLAlchemy database DSN",
    )

    # JWT / Auth placeholders (will be wired later)
    jwt_secret_key: str = Field(default="change-me", repr=False)
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 24)

    # Redis / Queue placeholder
    redis_url: str = Field(default="redis://localhost:6379/0")

    # CORS
    cors_allow_origins: str = Field(default="http://localhost:3000,http://127.0.0.1:3000")
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: str = Field(default="*")
    cors_allow_headers: str = Field(default="*")
    cors_allow_origin_regex: Optional[str] = Field(default=None)

    # Multi-tenant (A mode: wildcard subdomain)
    # Example:
    #   PLATFORM_ROOT_DOMAIN=example.com
    #   tenant site: <tenant>.example.com
    #   app console: app.example.com
    #   api: api.example.com
    platform_root_domain: Optional[str] = Field(default=None)
    platform_app_subdomain: str = Field(default="app")
    platform_api_subdomain: str = Field(default="api")
    tenant_header_name: str = Field(default="x-tenant-slug")

    # Storage configuration
    storage_backend: Literal["local", "supabase"] = Field(default="local")
    storage_local_root: str = Field(default="./storage")
    storage_public_base_url: Optional[str] = Field(default=None)
    supabase_url: Optional[AnyUrl] = Field(default=None)
    supabase_anon_key: Optional[str] = Field(default=None, repr=False)
    supabase_service_role_key: Optional[str] = Field(default=None, repr=False)
    supabase_storage_bucket: Optional[str] = Field(default=None)
    supabase_public_url: Optional[str] = Field(default=None)

    # Vercel provisioning (Option 1: tenant.vercel.app)
    vercel_token: Optional[str] = Field(default=None, repr=False)
    vercel_team_id: Optional[str] = Field(default=None)
    vercel_team_slug: Optional[str] = Field(default=None)
    vercel_git_provider: str = Field(default="github")
    # format: <org>/<repo>
    vercel_git_repo: Optional[str] = Field(default=None)
    vercel_git_ref: str = Field(default="main")
    # monorepo root for the Next.js app
    vercel_frontend_root_dir: str = Field(default="web-platform/frontend")
    # deployed frontend will call this API base (must include /api)
    vercel_frontend_api_base_url: Optional[str] = Field(default=None)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()  # type: ignore[arg-type]
