"""Global cues that set the morning tone for Indian markets (via yfinance)."""

from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

from imd.data.base import Cache, DataProvider

logger = logging.getLogger(__name__)

# label -> yfinance symbol
CUE_SYMBOLS: dict[str, str] = {
    "Dow Jones": "^DJI",
    "Nasdaq": "^IXIC",
    "Brent Crude": "BZ=F",
    "USD/INR": "INR=X",
    "Gold": "GC=F",
}


class GlobalCuesProvider(DataProvider):
    """Latest close + % change for global tone-setters."""

    name = "global_cues"

    def __init__(self, cache: Cache | None = None) -> None:
        self._cache = cache

    def fetch(self, **_: Any) -> dict[str, dict[str, float]]:
        """Return {label: {"price": float, "change_pct": float}}."""
        if self._cache and (hit := self._cache.get(self.name)) is not None:
            return hit

        out: dict[str, dict[str, float]] = {}
        symbols = list(CUE_SYMBOLS.values())
        try:
            data = yf.download(
                symbols, period="5d", interval="1d",
                group_by="ticker", auto_adjust=False, progress=False, threads=True,
            )
        except Exception:  # noqa: BLE001
            logger.exception("global cues download failed")
            return {}

        import pandas as pd  # local import keeps module import light

        multi = isinstance(data.columns, pd.MultiIndex)
        for label, sym in CUE_SYMBOLS.items():
            try:
                df = (data[sym] if multi else data).dropna()
                last, prev = float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
                out[label] = {
                    "price": round(last, 2),
                    "change_pct": round((last - prev) / prev * 100, 2) if prev else 0.0,
                }
            except (KeyError, IndexError, ValueError):
                logger.debug("no data for cue %s", label)

        if self._cache:
            self._cache.set(self.name, out, ttl=900)
        return out
