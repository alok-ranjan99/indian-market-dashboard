"""Indicator tests — exact values where deterministic, properties otherwise."""

from __future__ import annotations

import numpy as np
import pandas as pd

from imd.scoring import indicators as ind


def _ramp(n: int, start: float = 100.0, step: float = 1.0) -> pd.Series:
    return pd.Series([start + step * i for i in range(n)])


def test_sma_exact() -> None:
    s = pd.Series([1, 2, 3, 4, 5], dtype=float)
    assert ind.sma(s, 3).iloc[-1] == 4.0  # mean(3,4,5)


def test_ema_first_value_equals_series() -> None:
    s = pd.Series([10, 20, 30], dtype=float)
    assert ind.ema(s, 3).iloc[0] == 10.0


def test_rsi_all_gains_is_100() -> None:
    rsi = ind.rsi(_ramp(30), period=14)
    assert rsi.iloc[-1] == 100.0  # monotonic rise → no losses → RSI 100


def test_rsi_all_losses_is_low() -> None:
    rsi = ind.rsi(_ramp(30, start=200, step=-1), period=14)
    assert rsi.iloc[-1] < 5.0


def test_rsi_bounded() -> None:
    rng = np.random.default_rng(0)
    s = pd.Series(100 + rng.standard_normal(100).cumsum())
    rsi = ind.rsi(s)
    assert rsi.dropna().between(0, 100).all()


def test_macd_hist_positive_on_uptrend() -> None:
    hist = ind.macd(_ramp(60))["hist"]
    assert hist.iloc[-1] > 0


def test_atr_positive() -> None:
    df = pd.DataFrame({
        "High": _ramp(30) + 2, "Low": _ramp(30) - 2, "Close": _ramp(30),
    })
    assert ind.atr(df).iloc[-1] > 0


def test_volume_spike_ratio() -> None:
    vol = pd.Series([100] * 19 + [200])  # last is 2x the ~100 average
    assert ind.volume_spike(vol) > 1.8


def test_is_breakout_true_on_new_high() -> None:
    df = pd.DataFrame({
        "High": [10] * 20 + [12], "Low": [8] * 21, "Close": [9] * 20 + [11.5],
    })
    assert ind.is_breakout(df) is True


def test_is_breakout_false_within_range() -> None:
    df = pd.DataFrame({
        "High": [12] * 21, "Low": [8] * 21, "Close": [9] * 21,
    })
    assert ind.is_breakout(df) is False
