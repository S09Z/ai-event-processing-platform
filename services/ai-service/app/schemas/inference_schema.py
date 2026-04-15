"""Pydantic schemas for the AI inference API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class InferenceRequest(BaseModel):
    """Request body for the inference endpoint."""

    event_id: str
    event_type: str = Field(..., min_length=1, examples=["click", "purchase"])
    payload: dict = Field(default_factory=dict)


class PredictionResponse(BaseModel):
    """Response schema for an inference result."""

    id: str
    event_id: str
    label: str
    score: float
    model_version: str
    created_at: datetime
    metadata: dict
