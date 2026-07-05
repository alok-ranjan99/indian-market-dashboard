"""VADER sentiment model — lightweight default (no torch).

Good enough for headline-level polarity and always available. The FinBERT model
(optional [ml] extra) implements the same `SentimentModel` interface and can be swapped
in without touching callers.
"""

from __future__ import annotations

from functools import lru_cache

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from imd.sentiment.base import SentimentModel


@lru_cache
def _analyzer() -> SentimentIntensityAnalyzer:
    return SentimentIntensityAnalyzer()


class VaderModel(SentimentModel):
    name = "vader"

    def score(self, text: str) -> float:
        if not text:
            return 0.0
        # compound is already normalized to [-1, 1]
        return float(_analyzer().polarity_scores(text)["compound"])
