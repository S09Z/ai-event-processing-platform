"""Transformers-backed inference engine – HuggingFace text classification."""

from __future__ import annotations

import asyncio
from functools import lru_cache

import structlog

from app.config import settings
from app.domain.inference_engine import InferenceEngine
from app.domain.prediction import Prediction

log: structlog.BoundLogger = structlog.get_logger()


@lru_cache(maxsize=1)
def _load_pipeline():  # type: ignore[return]
    """
    Load and cache the HuggingFace pipeline.

    The pipeline is loaded once and reused across requests
    (stateless per-request, shared model in memory).
    """
    try:
        from transformers import pipeline  # type: ignore[import]

        log.info(
            "transformers_engine.loading_model",
            model=settings.AI_MODEL_NAME,
            version=settings.AI_MODEL_VERSION,
        )
        return pipeline(
            "text-classification",
            model=settings.AI_MODEL_NAME,
            device=-1,  # CPU; set to 0 for first GPU
        )
    except Exception as exc:
        log.error("transformers_engine.load_failed", error=str(exc))
        raise


class TransformersInferenceEngine(InferenceEngine):
    """
    HuggingFace Transformers-backed inference engine.

    Runs text-classification pipeline on event type + payload.
    Model is loaded once and cached (stateless design).
    """

    async def predict(self, event_type: str, payload: dict) -> Prediction:
        """
        Run text classification on the serialized event.

        Inference is run in a thread pool to avoid blocking the event loop.
        """
        text = f"{event_type}: {payload}"
        pipe = _load_pipeline()

        # Run blocking inference in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: pipe(text)[0])

        return Prediction(
            event_id="",  # Will be set by InferenceService
            label=result["label"],
            score=float(result["score"]),
            model_version=settings.AI_MODEL_VERSION,
            metadata={"input_text": text},
        )
