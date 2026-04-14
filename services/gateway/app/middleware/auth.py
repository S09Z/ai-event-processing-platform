"""JWT / API Key authentication middleware."""

from __future__ import annotations

import structlog
from fastapi import status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

log: structlog.BoundLogger = structlog.get_logger()

# Paths that bypass authentication
PUBLIC_PATHS: frozenset[str] = frozenset({"/health", "/docs", "/openapi.json"})


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware.

    Responsibilities:
    - Validate JWT Bearer tokens
    - Validate API Keys (X-API-Key header)
    - Reject unauthenticated requests with 401
    - No business logic – cross-cutting concern only
    """

    async def dispatch(self, request: Request, call_next: any) -> Response:
        """Validate auth token on every non-public request."""
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        token = self._extract_bearer_token(request)
        api_key = request.headers.get("X-API-Key")

        if token:
            try:
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM],
                )
                request.state.user_id = payload.get("sub")
            except JWTError:
                log.warning("auth.jwt_invalid", path=request.url.path)
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired token"},
                )
        elif api_key:
            # TODO: validate against stored API keys
            request.state.user_id = "api_key_user"
        else:
            log.warning("auth.missing_credentials", path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"},
            )

        return await call_next(request)

    @staticmethod
    def _extract_bearer_token(request: Request) -> str | None:
        """Extract Bearer token from Authorization header."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[len("Bearer "):]
        return None
