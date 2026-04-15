"""AI inference unit tests – TDD first."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.domain.prediction import Prediction
from app.services.inference_service import InferenceService


@pytest.fixture()
def mock_engine() -> AsyncMock:
    """Return a mock InferenceEngine."""
    engine = AsyncMock()
    engine.predict = AsyncMock()
    return engine


@pytest.fixture()
def service(mock_engine: AsyncMock) -> InferenceService:
    """Return InferenceService wired with a mock engine."""
    return InferenceService(engine=mock_engine)


class TestInferenceService:
    """TDD tests for InferenceService.infer."""

    async def test_infer_returns_prediction(
        self, service: InferenceService, mock_engine: AsyncMock
    ) -> None:
        """infer should return a Prediction with the correct event_id."""
        mock_prediction = Prediction(
            event_id="",  # Set by service
            label="POSITIVE",
            score=0.98,
            model_version="v1",
        )
        mock_engine.predict.return_value = mock_prediction

        result = await service.infer(
            event_id="evt-123",
            event_type="click",
            payload={"button": "buy"},
        )

        assert result.event_id == "evt-123"
        assert result.label == "POSITIVE"
        assert result.score == 0.98

    async def test_infer_delegates_to_engine(
        self, service: InferenceService, mock_engine: AsyncMock
    ) -> None:
        """infer should call engine.predict with event_type and payload."""
        mock_engine.predict.return_value = Prediction(
            event_id="", label="NEGATIVE", score=0.7, model_version="v1"
        )

        await service.infer(event_id="evt-456", event_type="view", payload={})

        mock_engine.predict.assert_awaited_once_with(event_type="view", payload={})


class TestPredictionDomain:
    """TDD tests for the Prediction domain model."""

    def test_prediction_score_must_be_between_0_and_1(self) -> None:
        """Score outside [0, 1] should raise ValueError."""
        with pytest.raises(ValueError, match="Score"):
            Prediction(event_id="x", label="A", score=1.5, model_version="v1")

    def test_prediction_label_cannot_be_empty(self) -> None:
        """Empty label should raise ValueError."""
        with pytest.raises(ValueError, match="label"):
            Prediction(event_id="x", label="  ", score=0.5, model_version="v1")

    def test_valid_prediction_creation(self) -> None:
        """Valid prediction should be created without errors."""
        p = Prediction(event_id="e1", label="POSITIVE", score=0.95, model_version="v1")
        assert p.label == "POSITIVE"
        assert p.score == 0.95
