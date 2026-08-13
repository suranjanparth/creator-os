from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Confirm that the API process is accepting requests."""
    return HealthResponse(status="ok", service="creator-os-api")
