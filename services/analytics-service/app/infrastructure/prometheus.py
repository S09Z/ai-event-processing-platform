"""Prometheus metrics registry for the analytics service."""

from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

# Use default registry
REGISTRY = CollectorRegistry(auto_describe=True)

events_total = Counter(
    "events_total",
    "Total number of events ingested",
    ["event_type"],
    registry=REGISTRY,
)

events_processing_duration_seconds = Histogram(
    "events_processing_duration_seconds",
    "Event processing duration in seconds",
    ["event_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    registry=REGISTRY,
)

ai_predictions_total = Counter(
    "ai_predictions_total",
    "Total number of AI predictions produced",
    ["label"],
    registry=REGISTRY,
)

ai_prediction_score = Gauge(
    "ai_prediction_score_latest",
    "Score of the most recent AI prediction per label",
    ["label"],
    registry=REGISTRY,
)
