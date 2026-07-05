"""Sentiment scoring layer (VADER default; FinBERT optional via [ml] extra)."""

from imd.sentiment.base import SentimentModel
from imd.sentiment.vader import VaderModel


def default_model() -> SentimentModel:
    """Return the best available sentiment model (FinBERT if installed, else VADER)."""
    try:
        from imd.sentiment.finbert import FinBertModel  # noqa: PLC0415

        return FinBertModel()
    except Exception:  # noqa: BLE001 — transformers/torch not installed or model load failed
        return VaderModel()


__all__ = ["SentimentModel", "VaderModel", "default_model"]
