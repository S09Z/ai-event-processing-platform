"""Event Service entry point."""

from __future__ import annotations

import structlog
import uvicorn
from fastapi import FastAPI

from app.api.v1.events import _kafka_producer
from app.api.v1.events import router as events_router
from app.config import settings

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log: structlog.BoundLogger = structlog.get_logger()


_TAGS_METADATA = [
    {
        "name": "events",
        "description": (
            "CRUD operations for **Events**. "
            "Each created event is persisted to PostgreSQL and published to Kafka."
        ),
    },
]


def create_app() -> FastAPI:
    """Create and configure the FastAPI event service application."""
    _docs = settings.APP_ENV != "production"
    application = FastAPI(
        title="AI Event Platform – Event Service",
        summary="Ingest, persist, and stream events to downstream consumers.",
        description=(
            "The **Event Service** is responsible for:\n\n"
            "- Accepting inbound events via REST (`POST /api/v1/events`)\n"
            "- Persisting them to **PostgreSQL**\n"
            "- Publishing them to **Kafka** for async AI processing\n\n"
            "Swagger UI: `/docs` · ReDoc: `/redoc` · OpenAPI JSON: `/openapi.json`"
        ),
        version="1.0.0",
        contact={"name": "Platform Team", "email": "platform@example.com"},
        license_info={"name": "MIT"},
        openapi_tags=_TAGS_METADATA,
        docs_url="/docs" if _docs else None,
        redoc_url="/redoc" if _docs else None,
        openapi_url="/openapi.json" if _docs else None,
    )

    application.include_router(events_router)

    @application.on_event("startup")
    async def startup() -> None:
        await _kafka_producer.start()
        log.info("event_service.startup", env=settings.APP_ENV)

    @application.on_event("shutdown")
    async def shutdown() -> None:
        await _kafka_producer.stop()
        log.info("event_service.shutdown")

    return application


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.APP_ENV == "development",
    )
