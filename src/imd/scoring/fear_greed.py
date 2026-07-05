"""Fear & Greed composite scorer (0-100).

Blends five sub-scores by configurable weights. Missing inputs are skipped and the
remaining weights are renormalized (fail-soft), so a blocked PCR feed still yields a
usable score. Always returns a transparent breakdown of every component that fed in.
"""

from __future__ import annotations

from imd.domain import ScoreResult
from imd.scoring.base import Scorer, ScoringContext
from imd.scoring.normalize import (
    breadth_to_score,
    fear_greed_label,
    momentum_to_score,
    pcr_to_score,
    sentiment_to_score,
    vix_to_score,
)


class FearGreedScorer(Scorer):
    name = "fear_greed"

    def compute(self, ctx: ScoringContext) -> ScoreResult:
        w = ctx.settings.fear_greed_weights
        m = ctx.market

        components: dict[str, tuple[float, float]] = {}  # name -> (subscore, weight)

        if (vix := m.get("vix")) is not None:
            components["vix"] = (vix_to_score(float(vix)), w.vix)

        breadth = m.get("breadth")
        if breadth and (breadth.get("advances", 0) + breadth.get("declines", 0)) > 0:
            components["breadth"] = (
                breadth_to_score(breadth["advances"], breadth["declines"]), w.breadth
            )

        if ctx.news:
            avg = sum(getattr(n, "sentiment_score", 0.0) for n in ctx.news) / len(ctx.news)
            components["news"] = (sentiment_to_score(avg), w.news)

        close, sma20, sma50 = m.get("nifty_close"), m.get("nifty_sma20"), m.get("nifty_sma50")
        if close and sma20 and sma50:
            components["momentum"] = (
                momentum_to_score(float(close), float(sma20), float(sma50)), w.momentum
            )

        if (pcr := m.get("pcr")) is not None:
            components["pcr"] = (pcr_to_score(float(pcr)), w.pcr)

        return self._composite(components)

    @staticmethod
    def _composite(components: dict[str, tuple[float, float]]) -> ScoreResult:
        breakdown = {name: round(sub, 2) for name, (sub, _) in components.items()}
        total_weight = sum(weight for _, weight in components.values())
        if total_weight <= 0:
            return ScoreResult(value=50.0, breakdown=breakdown, label=fear_greed_label(50.0))
        value = sum(sub * weight for sub, weight in components.values()) / total_weight
        value = round(value, 2)
        return ScoreResult(value=value, breakdown=breakdown, label=fear_greed_label(value))
