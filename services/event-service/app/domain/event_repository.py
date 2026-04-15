"""Abstract repository interface for Event persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.event import Event


class EventRepository(ABC):
    """
    Abstract repository interface for Event persistence.

    All concrete implementations (Postgres, in-memory, etc.)
    must implement these methods.
    """

    @abstractmethod
    async def save(self, event: Event) -> Event:
        """Persist a new event and return it with any DB-generated fields."""
        ...

    @abstractmethod
    async def get_by_id(self, event_id: str) -> Event | None:
        """Return an event by ID, or None if not found."""
        ...

    @abstractmethod
    async def list_events(self, limit: int = 50, offset: int = 0) -> list[Event]:
        """Return a paginated list of events ordered by created_at desc."""
        ...

    @abstractmethod
    async def update(self, event: Event) -> Event:
        """Persist state changes on an existing event."""
        ...
