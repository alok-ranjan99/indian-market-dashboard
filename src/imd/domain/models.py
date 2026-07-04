"""Immutable-ish domain models shared across layers.

These mirror the "domain models" package in the LLD. Kept as plain dataclasses
(no framework coupling) so they are trivial to construct in tests and serialize.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

    @classmethod
    def from_score(cls, score: float, band: float = 0.15) -> Sentiment:
        """Map a continuous score in [-1, 1] to a discrete label."""
        if score > band:
            return cls.POSITIVE
        if score < -band:
            return cls.NEGATIVE
        return cls.NEUTRAL


class BiasLabel(StrEnum):
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BULLISH = "bullish"


class SignalKind(StrEnum):
    BIAS = "bias"
    SECTOR = "sector"
    SWING = "swing"


@dataclass(frozen=True)
class Quote:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    ts: datetime | None = None

    @property
    def change_pct(self) -> float | None:
        if self.open == 0:
            return None
        return round((self.close - self.open) / self.open * 100, 2)


@dataclass(frozen=True)
class NewsItem:
    title: str
    source: str
    url: str
    published: datetime
    sentiment_score: float = 0.0  # [-1, 1]

    @property
    def sentiment(self) -> Sentiment:
        return Sentiment.from_score(self.sentiment_score)


@dataclass(frozen=True)
class SectorPerf:
    name: str
    change_pct: float
    relative_strength: float  # 0-100
    news_sentiment: float = 0.0


@dataclass(frozen=True)
class ScoreResult:
    """A score plus the transparent breakdown of how it was computed."""

    value: float  # typically 0-100
    breakdown: dict[str, float] = field(default_factory=dict)
    label: str | None = None

    def explain(self) -> str:
        parts = [f"{k}={v:.1f}" for k, v in self.breakdown.items()]
        return f"{self.value:.1f} ({', '.join(parts)})"


@dataclass(frozen=True)
class Bias:
    label: BiasLabel
    confidence: float  # 0-1
    reasons: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SwingScore:
    value: float  # 0-100
    entry: float
    stop: float
    target: float
    breakdown: dict[str, float] = field(default_factory=dict)

    @property
    def risk_reward(self) -> float | None:
        risk = abs(self.entry - self.stop)
        if risk == 0:
            return None
        return round(abs(self.target - self.entry) / risk, 2)


@dataclass(frozen=True)
class Candidate:
    symbol: str
    ltp: float
    swing: SwingScore
    sector: str
    signals: dict[str, str] = field(default_factory=dict)  # e.g. {"rsi": "61", "setup": "Breakout"}


@dataclass(frozen=True)
class Signal:
    """Something worth alerting on (feeds AlertDispatcher)."""

    kind: SignalKind
    title: str
    strength: float  # 0-100
    payload: dict = field(default_factory=dict)
    ts: datetime | None = None
