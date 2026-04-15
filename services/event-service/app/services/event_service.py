"""EventService – business logic for event processing."""

from __future__ import annotations

import structlog

from app.domain.event import Event
from app.domain.event_repository import EventRepository
from app.infrastructure.kafka_producer import KafkaEventProducer

log: structlog.BoundLogger = structlog.get_logger()


class EventService:
    """
    Handles business logic for event processing.

    Responsibilities:
    - Validate input
    - Persist event via repository
    - Publish to Kafka
    """

    def __init__(
        self,
        repo: EventRepository,
        kafka_producer: KafkaEventProducer,
    ) -> None:
        self._repo = repo
        self._kafka = kafka_producer

    async def create_event(self, data: dict) -> Event:
        """
        Create and persist a new event, then publish it to Kafka.

        Args:
            data: Dict containing at minimum 'type' and optional 'payload'.

        Returns:
            The persisted Event domain object.

        Raises:
            ValueError: If required fields are missing or invalid.
        """
        log.info("event_service.create", event_type=data.get("type"))

        event = Event(
            type=data["type"],
            payload=data.get("payload", {}),
        )

        saved = await self._repo.save(event)

        await self._kafka.publish_event(saved)

        log.info("event_service.created", event_id=saved.id, event_type=saved.type)

        return saved

    async def get_event(self, event_id: str) -> Event | None:
        """
        Retrieve an event by ID.

        Returns:
            The Event domain object, or None if not found.
        """
        return await self._repo.get_by_id(event_id)

    async def list_events(self, limit: int = 50, offset: int = 0) -> list[Event]:
        """
        Return a paginated list of events.

        Args:
            limit: Max number of events to return.
            offset: Number of events to skip.

        Returns:
            List of Event domain objects.
        """
        return await self._repo.list_events(limit=limit, offset=offset)
