"""InferenceService – orchestrates AI inference pipeline."""

from __future__ import annotations

import structlog

from app.domain.inference_engine import InferenceEngine
from app.domain.prediction import Prediction

log: structlog.BoundLogger = structlog.get_logger()


class InferenceService:
    """
    Handles AI inference orchestration.

    Responsibilities:
    - Accept event data from the API layer
    - Delegate inference to the InferenceEngine
    - Return Prediction domain objects
    - Stateless by design – no shared mutable state
    """

    def __init__(self, engine: InferenceEngine) -> None:
        self._engine = engine

    async def infer(self, event_id: str, event_type: str, payload: dict) -> Prediction:
        """
        Run AI inference on an event.

        Args:
            event_id: ID of the source event.
            event_type: The event type string.
            payload: Event payload dict.

        Returns:
            A Prediction domain object.
        """
        log.info("inference_service.infer", event_id=event_id, event_type=event_type)

        prediction = await self._engine.predict(
            event_type=event_type,
            payload=payload,
        )
        # Attach the originating event ID
        prediction.event_id = event_id

        log.info(
            "inference_service.done",
            event_id=event_id,
            label=prediction.label,
            score=prediction.score,
        )

        return prediction
