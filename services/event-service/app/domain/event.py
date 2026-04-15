"""Event domain model – pure OOP, zero framework dependency."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class EventStatus(str, Enum):
    """Lifecycle status of an event."""

    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass
class Event:
    """
    Core domain entity representing a user-generated event.

    Invariants:
    - id is always a valid UUID
    - created_at is always UTC
    - type must be a non-empty string
    """

    type: str
    payload: dict
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: EventStatus = EventStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate domain invariants."""
        if not self.type or not self.type.strip():
            raise ValueError("Event type must be a non-empty string")

    def mark_processed(self) -> None:
        """Transition event to PROCESSED state."""
        self.status = EventStatus.PROCESSED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Transition event to FAILED state."""
        self.status = EventStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)

    def is_terminal(self) -> bool:
        """Return True if the event is in a terminal (non-retryable) state."""
        return self.status in (EventStatus.PROCESSED, EventStatus.FAILED)
