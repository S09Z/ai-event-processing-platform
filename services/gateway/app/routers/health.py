"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description='Returns `{"status": "ok"}` when the service is healthy. Used by load-balancers and orchestrators.',
    operation_id="health_check",
    responses={
        200: {"description": "Service is healthy"},
    },
)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", service="gateway")
