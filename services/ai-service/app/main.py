"""AI Service entry point."""

from __future__ import annotations

import asyncio

import structlog
import uvicorn
from fastapi import FastAPI

from app.api.v1.inference import router as inference_router
from app.config import settings
from app.infrastructure.kafka_worker import AIKafkaWorker
from app.infrastructure.transformers_engine import TransformersInferenceEngine
from app.services.inference_service import InferenceService

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

log: structlog.BoundLogger = structlog.get_logger()

# Shared worker instance
_worker: AIKafkaWorker | None = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI AI service application."""
    application = FastAPI(
        title="AI Event Platform – AI Service",
        version="1.0.0",
        docs_url="/docs" if settings.APP_ENV != "production" else None,
    )

    application.include_router(inference_router)

    @application.get("/health", tags=["health"])
    async def health() -> dict:
        """Health check endpoint."""
        return {"status": "ok", "service": "ai-service"}

    @application.on_event("startup")
    async def startup() -> None:
        global _worker  # noqa: PLW0603
        engine = TransformersInferenceEngine()
        svc = InferenceService(engine=engine)
        _worker = AIKafkaWorker(inference_service=svc)
        await _worker.start()
        asyncio.create_task(_worker.run())
        log.info("ai_service.startup", env=settings.APP_ENV)

    @application.on_event("shutdown")
    async def shutdown() -> None:
        if _worker:
            await _worker.stop()
        log.info("ai_service.shutdown")

    return application


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.APP_ENV == "development",
    )
