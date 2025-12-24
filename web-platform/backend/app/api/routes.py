from fastapi import APIRouter

from app.api.endpoints import health
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.assets import router as assets_router
from app.api.endpoints.tasks import router as tasks_router
from app.api.endpoints.uploads import router as uploads_router
from app.api.endpoints.tenants import router as tenants_router

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
api_router.include_router(assets_router, prefix="/assets", tags=["assets"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(uploads_router, prefix="/uploads", tags=["uploads"])
