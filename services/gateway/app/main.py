"""
Gateway Service Entry Point.

Cross-cutting concerns only:
- JWT / API Key authentication
- Redis-backed rate limiting
- Request validation
- Structured logging + tracing
"""

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import health

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
        "name": "health",
        "description": "Liveness and readiness probes.",
    },
]


def create_app() -> FastAPI:
    """Create and configure the FastAPI gateway application."""
    _docs = settings.APP_ENV != "production"
    app = FastAPI(
        title="AI Event Platform – Gateway",
        summary="API Gateway: authentication, rate-limiting, and request routing.",
        description=(
            "The **Gateway** is the single entry-point for all client traffic.\n\n"
            "It enforces:\n"
            "- JWT / API-Key **authentication**\n"
            "- Redis-backed **rate limiting** (`X-RateLimit-*` headers)\n"
            "- Propagation of `X-Correlation-ID` for distributed tracing\n\n"
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

    # Middleware (order matters – outermost runs first)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)

    @app.on_event("startup")
    async def startup() -> None:
        log.info("gateway.startup", env=settings.APP_ENV)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        log.info("gateway.shutdown")

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_ENV == "development",
    )
