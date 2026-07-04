"""Sentiment model interface.

Implementations: FinBertModel (transformers, optional [ml] extra) and VaderModel
(lightweight default). The scoring layer depends on this interface, never on a
concrete model, so we can upgrade the model without touching callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class SentimentModel(ABC):
    """Scores financial text into a continuous value in [-1, 1]."""

    name: str = "sentiment"

    @abstractmethod
    def score(self, text: str) -> float:
        """Return sentiment for a single text in [-1, 1]."""
        raise NotImplementedError

    def score_batch(self, texts: list[str]) -> list[float]:
        """Default batch impl; override for vectorized models."""
        return [self.score(t) for t in texts]
