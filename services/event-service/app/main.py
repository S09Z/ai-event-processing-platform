"""Event Service entry point."""

from __future__ import annotations

import structlog
import uvicorn
from fastapi import FastAPI

from app.api.v1.events import _kafka_producer, router as events_router
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


def create_app() -> FastAPI:
    """Create and configure the FastAPI event service application."""
    application = FastAPI(
        title="AI Event Platform – Event Service",
        version="1.0.0",
        docs_url="/docs" if settings.APP_ENV != "production" else None,
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
