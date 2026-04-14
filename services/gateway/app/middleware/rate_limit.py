"""Redis-backed rate limiting middleware."""

from __future__ import annotations

import time

import structlog
from fastapi import status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

log: structlog.BoundLogger = structlog.get_logger()

_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """Return a lazily-initialized Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.

    Responsibilities:
    - Count requests per client IP within a rolling window
    - Reject excess requests with 429
    - Uses Redis for distributed rate limit state
    """

    async def dispatch(self, request: Request, call_next: any) -> Response:
        """Apply rate limit check before forwarding the request."""
        client_ip = request.client.host if request.client else "unknown"
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.RATE_LIMIT_REQUESTS

        key = f"rate_limit:{client_ip}:{int(time.time()) // window}"

        try:
            redis = await get_redis()
            count: int = await redis.incr(key)
            if count == 1:
                await redis.expire(key, window)

            if count > limit:
                log.warning(
                    "rate_limit.exceeded",
                    client_ip=client_ip,
                    count=count,
                    limit=limit,
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Try again later."},
                    headers={"Retry-After": str(window)},
                )
        except Exception as exc:
            # Fail open – do not block traffic if Redis is unavailable
            log.error("rate_limit.redis_error", error=str(exc))

        return await call_next(request)
