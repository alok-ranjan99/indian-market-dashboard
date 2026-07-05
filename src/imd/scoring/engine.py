"""Scoring engine — orchestrates the market-wide scorers.

Thin, deterministic glue: build a ScoringContext, run Fear/Greed, feed it into Bias.
Per-stock swing scoring lives in SwingScorer and is driven by the screener (Phase 6),
which supplies per-symbol OHLCV histories.
"""

from __future__ import annotations

from dataclasses import dataclass

from imd.config import Settings, get_settings
from imd.domain import Bias, ScoreResult
from imd.scoring.base import ScoringContext
from imd.scoring.bias import BiasScorer
from imd.scoring.fear_greed import FearGreedScorer


@dataclass
class MarketScores:
    fear_greed: ScoreResult
    bias: Bias


def score_market(ctx: ScoringContext) -> MarketScores:
    """Compute the market-wide scores. Bias consumes the Fear/Greed value."""
    fg = FearGreedScorer().compute(ctx)
    bias = BiasScorer(fear_greed=fg.value).compute(ctx)
    return MarketScores(fear_greed=fg, bias=bias)


def build_context(
    *,
    market: dict | None = None,
    news: list | None = None,
    sectors: list | None = None,
    flows: dict | None = None,
    global_cues: dict | None = None,
    settings: Settings | None = None,
) -> ScoringContext:
    """Convenience constructor with defaults (keeps call sites tidy)."""
    return ScoringContext(
        settings=settings or get_settings(),
        market=market or {},
        news=news or [],
        sectors=sectors or [],
        flows=flows or {},
        global_cues=global_cues or {},
    )
