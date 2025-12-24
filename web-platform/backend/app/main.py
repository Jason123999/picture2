from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text

from app.api.routes import api_router
from app.core.logging import configure_logging
from app.core.config import get_settings
from app.db.session import async_engine
from app.models import *  # noqa: F401,F403


def create_app() -> FastAPI:
    """Application factory for the FastAPI backend."""
    configure_logging()
    settings = get_settings()

    app = FastAPI(title=settings.app_name, version="0.1.0")

    allow_origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
    allow_methods = [m.strip() for m in settings.cors_allow_methods.split(",") if m.strip()] or ["*"]
    allow_headers = [h.strip() for h in settings.cors_allow_headers.split(",") if h.strip()] or ["*"]

    allow_credentials = settings.cors_allow_credentials
    if settings.env == "local":
        allow_origins = ["*"]
        allow_credentials = False

    default_vercel_origin_regex = r"^https://([a-z0-9-]+\.)*vercel\.app$"
    allow_origin_regex = settings.cors_allow_origin_regex
    if settings.env != "local" and not allow_origin_regex:
        allow_origin_regex = default_vercel_origin_regex

    cors_kwargs = dict(
        allow_origins=allow_origins or ["*"],
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )
    if allow_origin_regex:
        cors_kwargs["allow_origin_regex"] = allow_origin_regex

    app.add_middleware(CORSMiddleware, **cors_kwargs)

    # Serve local storage folder for development (optional)
    # Make the directory absolute and stable regardless of process cwd.
    if settings.storage_backend == "local":
        backend_root = Path(__file__).resolve().parents[1]
        storage_dir = Path(settings.storage_local_root)
        if not storage_dir.is_absolute():
            storage_dir = (backend_root / storage_dir).resolve()
        storage_dir.mkdir(parents=True, exist_ok=True)
        app.mount(
            "/storage",
            StaticFiles(directory=str(storage_dir)),
            name="storage",
        )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    async def on_startup() -> None:
        from sqlmodel import SQLModel

        async with async_engine.begin() as conn:  # type: ignore[call-arg]
            await conn.run_sync(SQLModel.metadata.create_all)

            # Lightweight migration for SQLite dev DB:
            # rename reserved column name 'metadata' -> 'meta_json'
            try:
                result = await conn.execute(text("PRAGMA table_info(image_assets)"))
                columns = [row[1] for row in result.fetchall()]
                if "metadata" in columns and "meta_json" not in columns:
                    await conn.execute(
                        text("ALTER TABLE image_assets RENAME COLUMN metadata TO meta_json")
                    )
            except Exception:
                # Do not crash startup due to best-effort migration
                pass

    return app


app = create_app()
