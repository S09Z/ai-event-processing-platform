"""AI service configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI service application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_EVENTS_TOPIC: str = "events"
    KAFKA_AI_RESULTS_TOPIC: str = "ai-results"
    KAFKA_DLQ_TOPIC: str = "events-dlq"
    KAFKA_CONSUMER_GROUP: str = "ai-workers"

    # AI / ML
    AI_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    AI_MODEL_VERSION: str = "v1"
    AI_MODEL_DIR: str = "./models"


settings = Settings()
