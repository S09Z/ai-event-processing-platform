"""Abstract repository interface for metric persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.metric import EventMetric


class MetricRepository(ABC):
    """
    Abstract repository for EventMetric persistence.

    All concrete implementations must implement these methods.
    """

    @abstractmethod
    async def save(self, metric: EventMetric) -> EventMetric:
        """Upsert a metric record."""
        ...

    @abstractmethod
    async def get_by_type(self, event_type: str) -> list[EventMetric]:
        """Return all metric windows for an event type."""
        ...

    @abstractmethod
    async def list_all(self) -> list[EventMetric]:
        """Return all metric records."""
        ...
