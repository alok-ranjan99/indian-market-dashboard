"""Daily market Bias scorer → Bullish / Neutral / Bearish with reasons.

Combines trend, institutional flows, the Fear/Greed reading, and the overnight global
gap into a signed score, normalized against the weight that actually had data, then maps
to a label with a confidence and a human-readable reason per contributor (so a thin-data
day reads as low-confidence Neutral rather than a falsely strong call — never a black box).
"""

from __future__ import annotations

from imd.domain import Bias, BiasLabel
from imd.scoring.base import Scorer, ScoringContext

# Signed weights (points) each factor can contribute to the bias score.
_TREND_PTS = 40.0
_FLOWS_PTS = 25.0
_FG_PTS = 20.0
_GAP_PTS = 15.0

# Neutral band: a directional label requires ≥20% net conviction (of available weight),
# so borderline/thin-data days read as low-confidence Neutral, not a contradictory call.
_BULL_THRESHOLD = 20.0
_BEAR_THRESHOLD = -20.0


class BiasScorer(Scorer):
    name = "bias"

    def __init__(self, fear_greed: float | None = None) -> None:
        # Fear/Greed is an upstream score; pass it in to avoid recomputation.
        self._fear_greed = fear_greed

    def compute(self, ctx: ScoringContext) -> Bias:
        m = ctx.market
        score = 0.0
        budget = 0.0  # sum of max points from factors that actually had data
        reasons: list[str] = []

        # 1) Trend vs 20/50 DMA
        close, sma20, sma50 = m.get("nifty_close"), m.get("nifty_sma20"), m.get("nifty_sma50")
        if close and sma20 and sma50:
            budget += _TREND_PTS
            if close > sma20 > sma50:
                score += _TREND_PTS
                reasons.append("Nifty above 20 & 50 DMA — uptrend ▲")
            elif close < sma20 < sma50:
                score -= _TREND_PTS
                reasons.append("Nifty below 20 & 50 DMA — downtrend ▼")
            else:
                reasons.append("Nifty between key DMAs — mixed trend ▬")

        # 2) Institutional flows (FII + DII net, ₹ cr)
        if ctx.flows:
            budget += _FLOWS_PTS
            net = ctx.flows.get("FII", 0.0) + ctx.flows.get("DII", 0.0)
            if net > 0:
                score += _FLOWS_PTS
                reasons.append(f"Net institutional buying (₹{net:,.0f} cr) ▲")
            elif net < 0:
                score -= _FLOWS_PTS
                reasons.append(f"Net institutional selling (₹{net:,.0f} cr) ▼")

        # 3) Fear/Greed tilt
        fg = self._fear_greed
        if fg is not None:
            budget += _FG_PTS
            tilt = (fg - 50) / 50 * _FG_PTS  # -20..+20
            score += tilt
            mood = "greed" if fg > 55 else "fear" if fg < 45 else "neutral"
            arrow = "▲" if tilt > 1 else "▼" if tilt < -1 else "▬"
            reasons.append(f"Fear/Greed {fg:.0f} ({mood}) {arrow}")

        # 4) Overnight global gap (e.g. GIFT Nifty / Dow % change)
        gap = ctx.global_cues.get("gap_pct")
        if gap is not None:
            budget += _GAP_PTS
            score += max(-_GAP_PTS, min(_GAP_PTS, gap * 10))
            arrow = "▲" if gap > 0 else "▼" if gap < 0 else "▬"
            reasons.append(f"Global cues gap {gap:+.2f}% {arrow}")

        return self._to_bias(score, budget, reasons)

    @staticmethod
    def _to_bias(score: float, budget: float, reasons: list[str]) -> Bias:
        if budget <= 0:
            return Bias(label=BiasLabel.NEUTRAL, confidence=0.0, reasons=reasons)
        # Normalize to [-100, 100] against the weight that actually contributed, so a
        # thin-data day yields low confidence rather than a falsely strong label.
        normalized = score / budget * 100
        if normalized >= _BULL_THRESHOLD:
            label = BiasLabel.BULLISH
        elif normalized <= _BEAR_THRESHOLD:
            label = BiasLabel.BEARISH
        else:
            label = BiasLabel.NEUTRAL
        confidence = round(min(1.0, abs(score) / budget), 2)
        return Bias(label=label, confidence=confidence, reasons=reasons)
