"""PostgreSQL implementation of EventRepository."""

from __future__ import annotations

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.event import Event
from app.domain.event_repository import EventRepository
from app.infrastructure.models import EventORM

log: structlog.BoundLogger = structlog.get_logger()


class PostgresEventRepository(EventRepository):
    """
    PostgreSQL-backed event repository.

    Uses SQLAlchemy async sessions for all DB operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: Event) -> Event:
        """Persist a new event to the database."""
        orm_event = EventORM.from_domain(event)
        self._session.add(orm_event)
        await self._session.commit()
        await self._session.refresh(orm_event)
        log.debug("repo.event_saved", event_id=event.id)
        return orm_event.to_domain()

    async def get_by_id(self, event_id: str) -> Event | None:
        """Fetch a single event by ID."""
        result = await self._session.execute(
            select(EventORM).where(EventORM.id == event_id)
        )
        orm_event = result.scalar_one_or_none()
        if orm_event is None:
            return None
        return orm_event.to_domain()

    async def list_events(self, limit: int = 50, offset: int = 0) -> list[Event]:
        """Return paginated events ordered by created_at descending."""
        result = await self._session.execute(
            select(EventORM)
            .order_by(EventORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [row.to_domain() for row in result.scalars().all()]

    async def update(self, event: Event) -> Event:
        """Update an existing event record."""
        result = await self._session.execute(
            select(EventORM).where(EventORM.id == event.id)
        )
        orm_event = result.scalar_one_or_none()
        if orm_event is None:
            raise ValueError(f"Event {event.id} not found")

        orm_event.status = event.status.value
        orm_event.updated_at = event.updated_at
        await self._session.commit()
        await self._session.refresh(orm_event)
        return orm_event.to_domain()
