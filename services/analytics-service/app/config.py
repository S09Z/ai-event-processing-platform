"""Analytics service configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Analytics service application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://app_user:changeme@localhost:5432/events_db"
    )

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EVENTS_TOPIC: str = "events"
    KAFKA_AI_RESULTS_TOPIC: str = "ai-results"
    KAFKA_CONSUMER_GROUP: str = "analytics-workers"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Prometheus
    PROMETHEUS_PORT: int = 9090


settings = Settings()
