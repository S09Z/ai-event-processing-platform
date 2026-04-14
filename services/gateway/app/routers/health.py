"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", service="gateway")
