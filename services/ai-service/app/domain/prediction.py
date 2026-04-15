"""Prediction domain model – pure OOP, zero framework dependency."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Prediction:
    """
    Core domain entity representing an AI inference result.

    Invariants:
    - id is always a valid UUID
    - event_id references the source event
    - label and score are always set after inference
    """

    event_id: str
    label: str
    score: float
    model_version: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate domain invariants."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")
        if not self.label.strip():
            raise ValueError("Prediction label must be a non-empty string")
