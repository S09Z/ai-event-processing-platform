"""SQLAlchemy ORM model for Event persistence."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.event import Event, EventStatus


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class EventORM(Base):
    """
    SQLAlchemy ORM model for the events table.

    Maps to/from the Event domain entity.
    """

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=EventStatus.PENDING.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_domain(self) -> Event:
        """Convert ORM model to domain entity."""
        return Event(
            id=self.id,
            type=self.type,
            payload=self.payload,
            status=EventStatus(self.status),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_domain(cls, event: Event) -> "EventORM":
        """Create ORM model from domain entity."""
        return cls(
            id=event.id,
            type=event.type,
            payload=event.payload,
            status=event.status.value,
            created_at=event.created_at,
            updated_at=event.updated_at,
        )
