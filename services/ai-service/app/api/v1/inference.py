"""FastAPI router for /api/v1/ai endpoints."""

from __future__ import annotations

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.infrastructure.transformers_engine import TransformersInferenceEngine
from app.schemas.inference_schema import InferenceRequest, PredictionResponse
from app.services.inference_service import InferenceService

log: structlog.BoundLogger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

_engine = TransformersInferenceEngine()


def get_inference_service() -> InferenceService:
    """FastAPI dependency that returns the InferenceService."""
    return InferenceService(engine=_engine)


@router.post(
    "/infer",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Run AI inference on an event",
    description=(
        "Submit an event payload for synchronous ML inference.\n\n"
        "The model classifies the event and returns a `label` with a confidence `score`.\n\n"
        "*Note:* High-throughput workloads should use the async Kafka pipeline instead."
    ),
    operation_id="infer",
    responses={
        200: {"description": "Inference result returned successfully"},
        422: {"description": "Validation error – check request body"},
        500: {"description": "Inference failed – see logs for details"},
    },
)
async def infer(
    body: InferenceRequest,
    service: InferenceService = Depends(get_inference_service),
) -> PredictionResponse:
    """Run AI inference and return a prediction."""
    try:
        prediction = await service.infer(
            event_id=body.event_id,
            event_type=body.event_type,
            payload=body.payload,
        )
    except Exception as exc:
        log.error("ai_api.inference_error", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Inference failed",
        ) from exc

    return PredictionResponse(
        id=prediction.id,
        event_id=prediction.event_id,
        label=prediction.label,
        score=prediction.score,
        model_version=prediction.model_version,
        created_at=prediction.created_at,
        metadata=prediction.metadata,
    )
