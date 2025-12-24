from fastapi import APIRouter

from app.schemas.health import HealthStatus

router = APIRouter()


@router.get("/", summary="Health check", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")
