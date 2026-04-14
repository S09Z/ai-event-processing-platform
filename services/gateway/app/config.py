"""Gateway service configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Gateway application settings.

    Loaded from environment variables / .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # JWT
    JWT_SECRET_KEY: str = "changeme"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Upstream services (reverse proxy targets)
    EVENT_SERVICE_URL: str = "http://event-service:8001"
    AI_SERVICE_URL: str = "http://ai-service:8002"
    ANALYTICS_SERVICE_URL: str = "http://analytics-service:8003"


settings = Settings()
