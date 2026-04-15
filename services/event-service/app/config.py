"""Event service configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Event service application settings.

    Loaded from environment variables / .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://app_user:changeme@localhost:5432/events_db"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EVENTS_TOPIC: str = "events"
    KAFKA_DLQ_TOPIC: str = "events-dlq"
    KAFKA_CONSUMER_GROUP: str = "event-workers"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"


settings = Settings()
