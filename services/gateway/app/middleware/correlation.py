"""Correlation ID middleware – injects a unique ID per request for tracing."""

from __future__ import annotations

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log: structlog.BoundLogger = structlog.get_logger()

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Correlation ID middleware.

    Responsibilities:
    - Generate or propagate a Correlation ID for every request
    - Bind the ID to the structlog context for all log entries
    - Forward the ID in the response headers
    """

    async def dispatch(self, request: Request, call_next: any) -> Response:
        """Attach correlation ID to request and response."""
        correlation_id = request.headers.get(CORRELATION_ID_HEADER, str(uuid.uuid4()))

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        request.state.correlation_id = correlation_id
        response: Response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response
