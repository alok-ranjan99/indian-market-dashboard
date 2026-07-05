"""Per-stock Swing scorer (0-100) + ATR-based entry / stop / target.

Unlike Fear/Greed and Bias (market-wide, implement ``Scorer.compute(ctx)``), the swing
score is per-instrument, so this is a standalone scorer taking one stock's OHLCV history
plus its sector strength and news score. It returns a ``SwingScore`` with a transparent
breakdown and a risk-first trade plan (stop below entry by 1.5·ATR, target at 2:1).
"""

from __future__ import annotations

import math

import pandas as pd

from imd.config import SwingWeights, get_settings
from imd.domain import SwingScore
from imd.scoring import indicators as ind
from imd.scoring.normalize import clamp, momentum_to_score

_ATR_STOP_MULT = 1.5
_REWARD_MULT = 2.0  # target distance = 2 × risk (2:1 R:R)


class SwingScorer:
    name = "swing"

    def __init__(self, weights: SwingWeights | None = None) -> None:
        self.weights = weights or get_settings().swing_weights

    def score(
        self, ohlcv: pd.DataFrame, *, sector_strength: float = 50.0, news_score: float = 50.0
    ) -> SwingScore:
        """Score a single stock. `ohlcv` needs Open/High/Low/Close/Volume, oldest→newest."""
        close = float(ohlcv["Close"].iloc[-1])
        sma20 = _safe_last(ind.sma(ohlcv["Close"], 20), close)
        sma50 = _safe_last(ind.sma(ohlcv["Close"], 50), close)

        subs = {
            "trend": momentum_to_score(close, sma20, sma50),
            "momentum": self._momentum(ohlcv),
            "volume": self._volume(ohlcv),
            "breakout": self._breakout(ohlcv, close),
            "sector": clamp(sector_strength),
            "news": clamp(news_score),
        }
        value = self._weighted(subs)
        entry, stop, target = self._trade_plan(ohlcv, close)
        return SwingScore(
            value=value, entry=round(entry, 2), stop=round(stop, 2),
            target=round(target, 2), breakdown={k: round(v, 2) for k, v in subs.items()},
        )

    # ── sub-scores ────────────────────────────────────────────
    def _momentum(self, ohlcv: pd.DataFrame) -> float:
        rsi = _safe_last(ind.rsi(ohlcv["Close"]), 50.0)
        hist = _safe_last(ind.macd(ohlcv["Close"])["hist"], 0.0)
        macd_comp = 100.0 if hist > 0 else 40.0
        return round(clamp(0.6 * rsi + 0.4 * macd_comp), 2)

    def _volume(self, ohlcv: pd.DataFrame) -> float:
        ratio = ind.volume_spike(ohlcv["Volume"])
        return round(clamp(50 + (ratio - 1) * 35), 2)

    def _breakout(self, ohlcv: pd.DataFrame, close: float) -> float:
        if ind.is_breakout(ohlcv):
            return 100.0
        if len(ohlcv) < 21:
            return 50.0
        prior_high = float(ohlcv["High"].iloc[-21:-1].max())
        pct_below = (prior_high - close) / close * 100 if close else 100.0
        return round(clamp(100 - pct_below * 10), 2)

    def _weighted(self, subs: dict[str, float]) -> float:
        w = self.weights
        total = sum(vars(w).values())
        acc = (
            subs["trend"] * w.trend + subs["momentum"] * w.momentum
            + subs["volume"] * w.volume + subs["breakout"] * w.breakout
            + subs["sector"] * w.sector + subs["news"] * w.news
        )
        return round(acc / total, 2) if total else 0.0

    # ── trade plan ────────────────────────────────────────────
    def _trade_plan(self, ohlcv: pd.DataFrame, close: float) -> tuple[float, float, float]:
        atr_val = _safe_last(ind.atr(ohlcv), 0.0)
        if not atr_val or math.isnan(atr_val):
            atr_val = close * 0.02  # fallback: 2% of price
        entry = close
        stop = entry - _ATR_STOP_MULT * atr_val
        target = entry + _REWARD_MULT * (entry - stop)
        return entry, stop, target


def _safe_last(series: pd.Series, default: float) -> float:
    try:
        val = float(series.dropna().iloc[-1])
        return default if math.isnan(val) else val
    except (IndexError, ValueError):
        return default
