"""Tradable universe definitions.

Nifty 50 constituents (yfinance symbols use the ``.NS`` suffix). The list is a
constant for now — config-driven and easy to refresh; a later phase can fetch it
live from NSE. Designed so swapping to NIFTY500 or a custom watchlist is a one-liner.
"""

from __future__ import annotations

# Index tickers (yfinance)
INDEX_SYMBOLS: dict[str, str] = {
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "INDIA_VIX": "^INDIAVIX",
}

# Nifty 50 constituents (review periodically — NSE rebalances semi-annually).
NIFTY_50: list[str] = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "ITC", "HINDUNILVR", "LT",
    "SBIN", "BHARTIARTL", "KOTAKBANK", "AXISBANK", "BAJFINANCE", "ASIANPAINT",
    "MARUTI", "HCLTECH", "M&M", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NTPC",
    "NESTLEIND", "POWERGRID", "TATAMOTORS", "TATASTEEL", "WIPRO", "ADANIENT",
    "ADANIPORTS", "COALINDIA", "BAJAJFINSV", "JSWSTEEL", "HINDALCO", "ONGC",
    "GRASIM", "TECHM", "BRITANNIA", "CIPLA", "DRREDDY", "EICHERMOT",
    "APOLLOHOSP", "DIVISLAB", "BPCL", "HEROMOTOCO", "BAJAJ-AUTO", "TATACONSUM",
    "SBILIFE", "HDFCLIFE", "SHRIRAMFIN", "LTIM", "TRENT",
]


def _to_yf(symbol: str) -> str:
    return f"{symbol}.NS"


def get_universe(name: str = "NIFTY50", *, yf_suffix: bool = True) -> list[str]:
    """Return the list of symbols for a named universe.

    Args:
        name: universe key (currently only ``NIFTY50``; extend here for NIFTY500).
        yf_suffix: append ``.NS`` for yfinance. Set False for bare NSE symbols.
    """
    key = name.upper()
    if key == "NIFTY50":
        symbols = NIFTY_50
    else:
        raise ValueError(f"Unknown universe: {name!r}. Known: NIFTY50")
    return [_to_yf(s) for s in symbols] if yf_suffix else list(symbols)
