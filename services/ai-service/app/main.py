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


_TAGS_METADATA = [
    {
        "name": "ai",
        "description": (
            "Run **ML inference** on event payloads using a DistilBERT-based classifier. "
            "The worker also consumes Kafka events automatically."
        ),
    },
    {
        "name": "health",
        "description": "Liveness and readiness probes.",
    },
]


def create_app() -> FastAPI:
    """Create and configure the FastAPI AI service application."""
    _docs = settings.APP_ENV != "production"
    application = FastAPI(
        title="AI Event Platform – AI Service",
        summary="Serve ML predictions and consume Kafka events for async inference.",
        description=(
            "The **AI Service** provides:\n\n"
            "- `POST /api/v1/ai/infer` – synchronous inference endpoint\n"
            "- A background **Kafka worker** that consumes the `events` topic "
            "and publishes predictions to `ai-results`\n\n"
            f"Model: `{settings.AI_MODEL_NAME}` · Version: `{settings.AI_MODEL_VERSION}`\n\n"
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

    application.include_router(inference_router)

    @application.get(
        "/health",
        tags=["health"],
        summary="Health check",
        description='Returns `{"status": "ok"}` when the service is healthy.',
        operation_id="health_check",
        responses={200: {"description": "Service is healthy"}},
    )
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
