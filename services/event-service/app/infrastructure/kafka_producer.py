"""Async Kafka event producer."""

from __future__ import annotations

import json

import structlog
from aiokafka import AIOKafkaProducer

from app.config import settings
from app.domain.event import Event

log: structlog.BoundLogger = structlog.get_logger()


class KafkaEventProducer:
    """
    Async Kafka producer for publishing domain events.

    Responsibilities:
    - Serialize Event domain objects to JSON
    - Publish to the configured Kafka topic
    - Handle connection lifecycle (start/stop)
    """

    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Initialize and start the Kafka producer."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self._producer.start()
        log.info("kafka_producer.started")

    async def stop(self) -> None:
        """Flush and stop the Kafka producer."""
        if self._producer:
            await self._producer.stop()
            log.info("kafka_producer.stopped")

    async def publish_event(self, event: Event) -> None:
        """
        Publish an Event to the events Kafka topic.

        Uses event.id as the partition key for idempotency.
        """
        if self._producer is None:
            raise RuntimeError("Kafka producer is not started")

        message = {
            "id": event.id,
            "type": event.type,
            "payload": event.payload,
            "status": event.status.value,
            "created_at": event.created_at.isoformat(),
        }

        await self._producer.send_and_wait(
            topic=settings.KAFKA_EVENTS_TOPIC,
            key=event.id,
            value=message,
        )

        log.info(
            "kafka_producer.event_published",
            event_id=event.id,
            topic=settings.KAFKA_EVENTS_TOPIC,
        )
