"""Pydantic schemas for the Event API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.event import EventStatus


class CreateEventRequest(BaseModel):
    """Request body for creating a new event."""

    type: str = Field(..., min_length=1, max_length=100, examples=["click", "purchase"])
    payload: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    """Response schema for a single event."""

    id: str
    type: str
    payload: dict[str, Any]
    status: EventStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Response schema for a paginated list of events."""

    items: list[EventResponse]
    total: int
    limit: int
    offset: int
