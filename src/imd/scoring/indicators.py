"""Technical indicators in pure pandas/numpy.

Self-contained (no pandas-ta) so we stay Python-3.11 compatible and deterministic
for golden-file tests. All functions are pure: DataFrame/Series in, values out.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI in [0, 100]."""
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    # Wilder smoothing == EWM with alpha = 1/period
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100 - (100 / (1 + rs))
    # when avg_loss == 0 → no losses → RSI 100
    return out.fillna(100.0).clip(0, 100)


def macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> dict[str, pd.Series]:
    """Return MACD line, signal line, and histogram."""
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return {"macd": macd_line, "signal": signal_line, "hist": macd_line - signal_line}


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range (Wilder). Expects columns High, Low, Close."""
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    true_range = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def volume_spike(volume: pd.Series, window: int = 20) -> float:
    """Latest volume relative to its trailing average (1.0 == average)."""
    if len(volume) < 2:
        return 1.0
    avg = volume.tail(window).mean()
    last = float(volume.iloc[-1])
    return round(last / avg, 3) if avg else 1.0


def is_breakout(df: pd.DataFrame, lookback: int = 20) -> bool:
    """True if the latest close exceeds the prior `lookback` highs (new high)."""
    if len(df) < lookback + 1:
        return False
    prior_high = df["High"].iloc[-(lookback + 1):-1].max()
    return bool(df["Close"].iloc[-1] > prior_high)
