"""Abstract inference engine interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.prediction import Prediction


class InferenceEngine(ABC):
    """
    Abstract interface for AI inference engines.

    Enables swapping model backends (Transformers, ONNX, TorchScript)
    without changing the service layer.
    """

    @abstractmethod
    async def predict(self, event_type: str, payload: dict) -> Prediction:
        """
        Run inference on an event and return a Prediction.

        Args:
            event_type: The type of the event (e.g. 'click', 'purchase').
            payload: The event payload dict.

        Returns:
            A Prediction domain object with label, score, and model version.
        """
        ...
