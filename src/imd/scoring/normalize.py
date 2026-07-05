"""Map raw market metrics onto a common 0-100 sub-score scale.

Every mapping is a small, documented, pure function so the composite scores are fully
explainable and each rule is independently unit-tested (these are our golden values).
Higher sub-score == more bullish / greedy, consistently across all metrics.
"""

from __future__ import annotations


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def vix_to_score(vix: float, low: float = 10.0, high: float = 25.0) -> float:
    """Low VIX (calm) → greed (100); high VIX (fear) → 0. Inverted, clamped."""
    return round(clamp((high - vix) / (high - low) * 100), 2)


def breadth_to_score(advances: int, declines: int) -> float:
    """Share of advancing stocks → 0-100 (50 == flat breadth)."""
    total = advances + declines
    if total <= 0:
        return 50.0
    return round(advances / total * 100, 2)


def sentiment_to_score(avg_sentiment: float) -> float:
    """Average news sentiment in [-1, 1] → 0-100 (50 == neutral)."""
    return round(clamp((avg_sentiment + 1) / 2 * 100), 2)


def momentum_to_score(price: float, sma20: float, sma50: float, scale: float = 8.0) -> float:
    """Price vs its 20/50-day averages → 0-100 (50 == at the averages).

    Weighted blend of % distance above each MA; `scale` sets sensitivity
    (≈ +3% over both MAs → ~80). Clamped.
    """
    if sma20 <= 0 or sma50 <= 0:
        return 50.0
    d20 = (price / sma20 - 1) * 100  # percent above the 20DMA
    d50 = (price / sma50 - 1) * 100
    return round(clamp(50 + scale * (0.4 * d20 + 0.6 * d50)), 2)


def pcr_to_score(pcr: float, greed: float = 0.7, fear: float = 1.3) -> float:
    """Put-Call Ratio → 0-100 (straightforward reading: high PCR == fear).

    Low PCR (few puts) → greed (100); high PCR → fear (0). Clamped.
    """
    return round(clamp((fear - pcr) / (fear - greed) * 100), 2)


def fear_greed_label(value: float) -> str:
    if value < 25:
        return "Extreme Fear"
    if value < 45:
        return "Fear"
    if value < 55:
        return "Neutral"
    if value < 75:
        return "Greed"
    return "Extreme Greed"
