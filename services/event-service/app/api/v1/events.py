"""FastAPI router for /api/v1/events endpoints."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.event_repository import EventRepository
from app.infrastructure.database import get_db_session
from app.infrastructure.kafka_producer import KafkaEventProducer
from app.infrastructure.postgres_event_repository import PostgresEventRepository
from app.schemas.event_schema import (
    CreateEventRequest,
    EventListResponse,
    EventResponse,
)
from app.services.event_service import EventService

log: structlog.BoundLogger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/events", tags=["events"])

# Shared Kafka producer instance (lifecycle managed in main.py)
_kafka_producer = KafkaEventProducer()


def get_kafka_producer() -> KafkaEventProducer:
    """FastAPI dependency returning the shared Kafka producer."""
    return _kafka_producer


def get_event_service(
    db: AsyncSession = Depends(get_db_session),
    kafka: KafkaEventProducer = Depends(get_kafka_producer),
) -> EventService:
    """FastAPI dependency that wires up EventService with its dependencies."""
    repo: EventRepository = PostgresEventRepository(db)
    return EventService(repo=repo, kafka_producer=kafka)


@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
)
async def create_event(
    body: CreateEventRequest,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Ingest a new event, persist it, and publish to Kafka."""
    event = await service.create_event({"type": body.type, "payload": body.payload})
    return EventResponse(
        id=event.id,
        type=event.type,
        payload=event.payload,
        status=event.status,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID",
)
async def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    """Retrieve a single event by its ID."""
    event = await service.get_event(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found",
        )
    return EventResponse(
        id=event.id,
        type=event.type,
        payload=event.payload,
        status=event.status,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.get(
    "/",
    response_model=EventListResponse,
    summary="List events",
)
async def list_events(
    limit: int = 50,
    offset: int = 0,
    service: EventService = Depends(get_event_service),
) -> EventListResponse:
    """Return a paginated list of events."""
    events = await service.list_events(limit=limit, offset=offset)
    return EventListResponse(
        items=[
            EventResponse(
                id=e.id,
                type=e.type,
                payload=e.payload,
                status=e.status,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in events
        ],
        total=len(events),
        limit=limit,
        offset=offset,
    )
