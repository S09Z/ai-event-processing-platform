"""Event service unit tests – TDD first."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.domain.event import Event, EventStatus
from app.services.event_service import EventService


@pytest.fixture()
def mock_repo() -> AsyncMock:
    """Return a mock EventRepository."""
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.list_events = AsyncMock()
    return repo


@pytest.fixture()
def mock_kafka() -> AsyncMock:
    """Return a mock KafkaEventProducer."""
    kafka = AsyncMock()
    kafka.publish_event = AsyncMock()
    return kafka


@pytest.fixture()
def service(mock_repo: AsyncMock, mock_kafka: AsyncMock) -> EventService:
    """Return an EventService wired with mocks."""
    return EventService(repo=mock_repo, kafka_producer=mock_kafka)


class TestCreateEvent:
    """TDD tests for EventService.create_event."""

    async def test_create_event_returns_event(
        self, service: EventService, mock_repo: AsyncMock
    ) -> None:
        """create_event should return a persisted Event with correct type."""
        expected = Event(type="click", payload={"button": "submit"})
        mock_repo.save.return_value = expected

        result = await service.create_event(
            {"type": "click", "payload": {"button": "submit"}}
        )

        assert result.type == "click"
        assert result.status == EventStatus.PENDING

    async def test_create_event_calls_repo_save(
        self, service: EventService, mock_repo: AsyncMock
    ) -> None:
        """create_event should call repo.save exactly once."""
        saved_event = Event(type="purchase", payload={})
        mock_repo.save.return_value = saved_event

        await service.create_event({"type": "purchase"})

        mock_repo.save.assert_awaited_once()

    async def test_create_event_publishes_to_kafka(
        self, service: EventService, mock_repo: AsyncMock, mock_kafka: AsyncMock
    ) -> None:
        """create_event should publish the saved event to Kafka."""
        saved_event = Event(type="click", payload={})
        mock_repo.save.return_value = saved_event

        await service.create_event({"type": "click"})

        mock_kafka.publish_event.assert_awaited_once_with(saved_event)

    async def test_create_event_raises_on_empty_type(
        self, service: EventService
    ) -> None:
        """create_event should raise ValueError when type is empty."""
        with pytest.raises((ValueError, KeyError)):
            await service.create_event({"type": ""})

    async def test_create_event_uses_empty_payload_by_default(
        self, service: EventService, mock_repo: AsyncMock
    ) -> None:
        """create_event should default payload to an empty dict."""
        saved_event = Event(type="view", payload={})
        mock_repo.save.return_value = saved_event

        result = await service.create_event({"type": "view"})

        assert result.payload == {}


class TestGetEvent:
    """TDD tests for EventService.get_event."""

    async def test_get_event_returns_event(
        self, service: EventService, mock_repo: AsyncMock
    ) -> None:
        """get_event should return the event when found."""
        event = Event(type="click", payload={}, id="abc-123")
        mock_repo.get_by_id.return_value = event

        result = await service.get_event("abc-123")

        assert result is not None
        assert result.id == "abc-123"

    async def test_get_event_returns_none_when_not_found(
        self, service: EventService, mock_repo: AsyncMock
    ) -> None:
        """get_event should return None when event does not exist."""
        mock_repo.get_by_id.return_value = None

        result = await service.get_event("nonexistent-id")

        assert result is None


class TestEventDomain:
    """TDD tests for the Event domain model."""

    def test_event_has_pending_status_by_default(self) -> None:
        """New events should start in PENDING status."""
        event = Event(type="click", payload={})
        assert event.status == EventStatus.PENDING

    def test_mark_processed_changes_status(self) -> None:
        """mark_processed should transition event to PROCESSED."""
        event = Event(type="click", payload={})
        event.mark_processed()
        assert event.status == EventStatus.PROCESSED

    def test_mark_failed_changes_status(self) -> None:
        """mark_failed should transition event to FAILED."""
        event = Event(type="click", payload={})
        event.mark_failed()
        assert event.status == EventStatus.FAILED

    def test_empty_type_raises_value_error(self) -> None:
        """Event with empty type should raise ValueError."""
        with pytest.raises(ValueError, match="non-empty"):
            Event(type="", payload={})

    def test_is_terminal_for_processed(self) -> None:
        """Processed events should be in terminal state."""
        event = Event(type="click", payload={})
        event.mark_processed()
        assert event.is_terminal() is True

    def test_is_not_terminal_for_pending(self) -> None:
        """Pending events should not be in terminal state."""
        event = Event(type="click", payload={})
        assert event.is_terminal() is False
