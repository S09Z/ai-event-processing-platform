"""Unit tests for gateway middleware."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    """Create a test client with a fresh app instance."""
    return TestClient(create_app(), raise_server_exceptions=False)


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_ok(self, client: TestClient) -> None:
        """Health check should return 200 with status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["service"] == "gateway"


class TestAuthMiddleware:
    """Tests for JWT authentication middleware."""

    def test_request_without_auth_returns_401(self, client: TestClient) -> None:
        """Unauthenticated requests to protected paths should return 401."""
        response = client.get("/api/events")
        assert response.status_code == 401

    def test_request_with_invalid_token_returns_401(self, client: TestClient) -> None:
        """Requests with an invalid JWT should return 401."""
        response = client.get(
            "/api/events",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_health_is_public(self, client: TestClient) -> None:
        """Health endpoint should be accessible without authentication."""
        response = client.get("/health")
        assert response.status_code == 200


class TestCorrelationIdMiddleware:
    """Tests for correlation ID injection."""

    def test_response_contains_correlation_id(self, client: TestClient) -> None:
        """Every response should include an X-Correlation-ID header."""
        response = client.get("/health")
        assert "x-correlation-id" in response.headers

    def test_propagates_existing_correlation_id(self, client: TestClient) -> None:
        """If client sends a Correlation ID it should be reflected back."""
        cid = "test-correlation-id-123"
        response = client.get("/health", headers={"X-Correlation-ID": cid})
        assert response.headers.get("x-correlation-id") == cid
