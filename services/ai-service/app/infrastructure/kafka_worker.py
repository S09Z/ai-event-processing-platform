"""Kafka consumer for the AI worker – reads events and runs inference."""

from __future__ import annotations

import asyncio
import json

import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.config import settings
from app.services.inference_service import InferenceService

log: structlog.BoundLogger = structlog.get_logger()

MAX_RETRIES = 3


class AIKafkaWorker:
    """
    Kafka consumer worker for AI event processing.

    Responsibilities:
    - Consume events from the events topic
    - Run AI inference via InferenceService
    - Publish results to ai-results topic
    - Route failed events to the dead-letter queue
    - Implements retry mechanism (up to MAX_RETRIES)
    """

    def __init__(self, inference_service: InferenceService) -> None:
        self._service = inference_service
        self._consumer: AIOKafkaConsumer | None = None
        self._producer: AIOKafkaProducer | None = None
        self._running = False

    async def start(self) -> None:
        """Start the Kafka consumer and producer."""
        self._consumer = AIOKafkaConsumer(
            settings.KAFKA_EVENTS_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self._consumer.start()
        await self._producer.start()
        self._running = True
        log.info("ai_worker.started")

    async def stop(self) -> None:
        """Stop the consumer and producer gracefully."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        log.info("ai_worker.stopped")

    async def run(self) -> None:
        """Main processing loop – consume, infer, publish."""
        if not self._consumer or not self._producer:
            raise RuntimeError("Worker not started")

        async for msg in self._consumer:
            event_data = msg.value
            await self._process_with_retry(event_data)
            await self._consumer.commit()

    async def _process_with_retry(self, event_data: dict, attempt: int = 1) -> None:
        """Process an event with retry logic. Route to DLQ after MAX_RETRIES."""
        try:
            prediction = await self._service.infer(
                event_id=event_data["id"],
                event_type=event_data["type"],
                payload=event_data.get("payload", {}),
            )

            result_message = {
                "event_id": prediction.event_id,
                "label": prediction.label,
                "score": prediction.score,
                "model_version": prediction.model_version,
                "created_at": prediction.created_at.isoformat(),
            }

            if self._producer:
                await self._producer.send_and_wait(
                    topic=settings.KAFKA_AI_RESULTS_TOPIC,
                    key=event_data["id"].encode("utf-8"),
                    value=result_message,
                )

            log.info(
                "ai_worker.processed",
                event_id=event_data["id"],
                label=prediction.label,
            )

        except Exception as exc:
            log.warning(
                "ai_worker.processing_failed",
                event_id=event_data.get("id"),
                attempt=attempt,
                error=str(exc),
            )
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2**attempt)  # Exponential backoff
                await self._process_with_retry(event_data, attempt + 1)
            else:
                await self._send_to_dlq(event_data, str(exc))

    async def _send_to_dlq(self, event_data: dict, error: str) -> None:
        """Route a failed event to the dead-letter queue."""
        if self._producer:
            dlq_message = {**event_data, "error": error, "dlq": True}
            await self._producer.send_and_wait(
                topic=settings.KAFKA_DLQ_TOPIC,
                value=dlq_message,
            )
            log.error("ai_worker.sent_to_dlq", event_id=event_data.get("id"))
