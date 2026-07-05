"""Price & index data via yfinance.

PriceProvider is the reference DataProvider implementation. It returns domain
`Quote` objects so downstream code never touches yfinance types directly — swapping
in a broker feed later means writing one new provider, nothing else changes.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import yfinance as yf

from imd.data.base import Cache, DataProvider
from imd.data.universe import INDEX_SYMBOLS, get_universe
from imd.domain import Quote

logger = logging.getLogger(__name__)


class PriceProvider(DataProvider):
    """Fetches OHLCV quotes for symbols and indices from Yahoo Finance."""

    name = "prices"

    def __init__(self, cache: Cache | None = None) -> None:
        self._cache = cache

    def fetch(self, symbols: list[str] | None = None, **_: Any) -> dict[str, Quote]:
        """Return latest daily `Quote` per symbol (defaults to the configured universe)."""
        symbols = symbols or get_universe("NIFTY50")
        cache_key = f"{self.name}:{','.join(sorted(symbols))}"
        if self._cache and (hit := self._cache.get(cache_key)) is not None:
            return hit

        quotes = self._download(symbols)

        if self._cache:
            self._cache.set(cache_key, quotes, ttl=900)
        return quotes

    def index_quote(self, key: str) -> Quote | None:
        """Convenience for a named index (NIFTY50 / BANKNIFTY / INDIA_VIX)."""
        symbol = INDEX_SYMBOLS.get(key.upper())
        if symbol is None:
            raise ValueError(f"Unknown index {key!r}. Known: {list(INDEX_SYMBOLS)}")
        return self._download([symbol]).get(symbol)

    def history(self, symbol: str, period: str = "3mo") -> pd.DataFrame:
        """OHLCV history for one symbol (oldest→newest). Empty frame on failure."""
        try:
            df = yf.download(symbol, period=period, interval="1d",
                             auto_adjust=False, progress=False)
        except Exception:  # noqa: BLE001
            logger.exception("history download failed for %s", symbol)
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]  # flatten single-ticker frame
        return df

    def histories(self, symbols: list[str], period: str = "6mo") -> dict[str, pd.DataFrame]:
        """Batched OHLCV history for many symbols (one network round-trip)."""
        try:
            data = yf.download(symbols, period=period, interval="1d", group_by="ticker",
                               auto_adjust=False, progress=False, threads=True)
        except Exception:  # noqa: BLE001
            logger.exception("batch history download failed (%d symbols)", len(symbols))
            return {}
        out: dict[str, pd.DataFrame] = {}
        multi = isinstance(data.columns, pd.MultiIndex)
        for sym in symbols:
            try:
                df = (data[sym] if multi else data).dropna(how="all")
                if not df.empty:
                    out[sym] = df
            except KeyError:
                logger.debug("no history for %s", sym)
        return out

    # ── internal ──────────────────────────────────────────────
    def _download(self, symbols: list[str]) -> dict[str, Quote]:
        try:
            data = yf.download(
                symbols, period="5d", interval="1d",
                group_by="ticker", auto_adjust=False, progress=False, threads=True,
            )
        except Exception:  # noqa: BLE001 — network/parse issues shouldn't crash the app
            logger.exception("yfinance download failed for %d symbols", len(symbols))
            return {}
        return self._to_quotes(symbols, data)

    @staticmethod
    def _to_quotes(symbols: list[str], data: pd.DataFrame) -> dict[str, Quote]:
        quotes: dict[str, Quote] = {}
        multi = isinstance(data.columns, pd.MultiIndex)
        for sym in symbols:
            try:
                df = data[sym] if multi else data
                row = df.dropna().iloc[-1]
                quotes[sym] = Quote(
                    symbol=sym,
                    open=float(row["Open"]), high=float(row["High"]),
                    low=float(row["Low"]), close=float(row["Close"]),
                    volume=float(row.get("Volume", 0) or 0),
                    ts=df.dropna().index[-1].to_pydatetime(),
                )
            except (KeyError, IndexError, ValueError):
                logger.debug("no usable data for %s", sym)
        return quotes
