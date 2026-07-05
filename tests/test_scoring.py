"""Scoring tests — exact golden values for the normalization maps and composites."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from imd.domain import BiasLabel, NewsItem
from imd.scoring import SwingScorer, build_context, score_market
from imd.scoring.fear_greed import FearGreedScorer
from imd.scoring.normalize import (
    breadth_to_score,
    fear_greed_label,
    momentum_to_score,
    pcr_to_score,
    sentiment_to_score,
    vix_to_score,
)


# ── normalization (golden values) ─────────────────────────
def test_vix_to_score() -> None:
    assert vix_to_score(10) == 100.0
    assert vix_to_score(25) == 0.0
    assert vix_to_score(17.5) == 50.0
    assert vix_to_score(5) == 100.0  # clamped


def test_breadth_to_score() -> None:
    assert breadth_to_score(30, 10) == 75.0
    assert breadth_to_score(0, 0) == 50.0  # no data → neutral


def test_sentiment_to_score() -> None:
    assert sentiment_to_score(0.0) == 50.0
    assert sentiment_to_score(1.0) == 100.0
    assert sentiment_to_score(-1.0) == 0.0


def test_momentum_to_score() -> None:
    assert momentum_to_score(100, 100, 100) == 50.0
    # +3% over both MAs → 50 + 8*(0.4*3 + 0.6*3) = 74
    assert momentum_to_score(103, 100, 100) == 74.0


def test_pcr_to_score() -> None:
    assert pcr_to_score(0.7) == 100.0
    assert pcr_to_score(1.3) == 0.0
    assert pcr_to_score(1.0) == 50.0


def test_fear_greed_label_bands() -> None:
    assert fear_greed_label(20) == "Extreme Fear"
    assert fear_greed_label(40) == "Fear"
    assert fear_greed_label(50) == "Neutral"
    assert fear_greed_label(60) == "Greed"
    assert fear_greed_label(90) == "Extreme Greed"


# ── Fear/Greed composite ──────────────────────────────────
def _news(score: float) -> NewsItem:
    return NewsItem("t", "s", "u", datetime.now(UTC), sentiment_score=score)


def test_fear_greed_composite_golden() -> None:
    ctx = build_context(
        market={
            "vix": 17.5,                                   # → 50
            "breadth": {"advances": 30, "declines": 10},   # → 75
            "nifty_close": 100, "nifty_sma20": 100, "nifty_sma50": 100,  # momentum → 50
            "pcr": 1.0,                                     # → 50
        },
        news=[_news(0.5), _news(0.5)],                      # → 75
    )
    res = FearGreedScorer().compute(ctx)
    # weights .25/.20/.20/.20/.15 → 50*.25+75*.20+50*.20+50*.15+75*.20 = 60
    assert res.value == 60.0
    assert res.label == "Greed"
    assert set(res.breakdown) == {"vix", "breadth", "news", "momentum", "pcr"}


def test_fear_greed_renormalizes_on_missing_inputs() -> None:
    ctx = build_context(market={"vix": 17.5, "nifty_close": 100,
                                "nifty_sma20": 100, "nifty_sma50": 100})
    res = FearGreedScorer().compute(ctx)
    assert res.value == 50.0  # (50*.25 + 50*.20) / .45
    assert set(res.breakdown) == {"vix", "momentum"}


def test_fear_greed_no_inputs_is_neutral() -> None:
    res = FearGreedScorer().compute(build_context())
    assert res.value == 50.0
    assert res.label == "Neutral"


# ── Bias ──────────────────────────────────────────────────
def test_bias_bullish() -> None:
    scores = score_market(build_context(
        market={"vix": 12, "nifty_close": 110, "nifty_sma20": 105, "nifty_sma50": 100},
        flows={"FII": -1240, "DII": 2010},          # net +770 → buying
        global_cues={"gap_pct": 0.3},
    ))
    assert scores.bias.label is BiasLabel.BULLISH
    assert scores.bias.confidence > 0.4
    assert scores.bias.reasons  # explanations present


def test_bias_bearish() -> None:
    scores = score_market(build_context(
        market={"vix": 24, "nifty_close": 90, "nifty_sma20": 95, "nifty_sma50": 100},
        flows={"FII": -2000, "DII": -500},
        global_cues={"gap_pct": -0.5},
    ))
    assert scores.bias.label is BiasLabel.BEARISH


# ── Swing ─────────────────────────────────────────────────
def _uptrend(n: int = 60) -> pd.DataFrame:
    close = [100 + i for i in range(n)]
    return pd.DataFrame({
        "Open": [c - 0.5 for c in close],
        "High": [c + 1 for c in close],
        "Low": [c - 1 for c in close],
        "Close": close,
        "Volume": [1000] * (n - 1) + [2500],  # closing volume spike
    })


def test_swing_uptrend_scores_and_plan() -> None:
    swing = SwingScorer().score(_uptrend(), sector_strength=80, news_score=70)
    assert 0 <= swing.value <= 100
    assert swing.value > 60  # strong uptrend + volume + breakout
    assert swing.entry > swing.stop  # stop below entry
    assert swing.target > swing.entry  # target above entry
    assert swing.risk_reward == 2.0  # 2:1 by construction
    assert set(swing.breakdown) == {"trend", "momentum", "volume", "breakout", "sector", "news"}


def test_swing_handles_short_history() -> None:
    df = _uptrend(10)  # fewer than 50 rows → SMAs fall back gracefully
    swing = SwingScorer().score(df)
    assert 0 <= swing.value <= 100
    assert swing.entry > 0
