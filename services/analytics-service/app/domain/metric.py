"""Metric domain model – pure OOP, zero framework dependency."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EventMetric:
    """
    Aggregated metric for a given event type over a time window.

    Invariants:
    - count is always non-negative
    - window_start < window_end
    """

    event_type: str
    count: int
    window_start: datetime
    window_end: datetime
    avg_processing_ms: float = 0.0
    labels: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate domain invariants."""
        if self.count < 0:
            raise ValueError("count must be non-negative")
        if self.window_start >= self.window_end:
            raise ValueError("window_start must be before window_end")

    def increment(self, processing_ms: float = 0.0) -> None:
        """Increment count and update rolling average processing time."""
        new_count = self.count + 1
        self.avg_processing_ms = (
            self.avg_processing_ms * self.count + processing_ms
        ) / new_count
        self.count = new_count
