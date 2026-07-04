"""NSE public data — sector indices, FII/DII flows, put-call ratio.

NSE actively blocks naive requests, so we use a session that first primes cookies by
hitting the homepage with browser-like headers, then calls the JSON endpoints. Every
method degrades gracefully (returns empty / None) rather than crashing the dashboard —
a later phase can add a Playwright fallback for when the JSON API is fully blocked.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from imd.data.base import Cache, DataProvider
from imd.domain import SectorPerf

logger = logging.getLogger(__name__)

_BASE = "https://www.nseindia.com"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{_BASE}/",
}

# NSE sector index names as the API expects them.
SECTOR_INDICES: list[str] = [
    "NIFTY IT", "NIFTY BANK", "NIFTY AUTO", "NIFTY FMCG", "NIFTY PHARMA",
    "NIFTY METAL", "NIFTY ENERGY", "NIFTY REALTY", "NIFTY PSU BANK",
    "NIFTY FIN SERVICE", "NIFTY MEDIA", "NIFTY PVT BANK",
]


class NSEProvider(DataProvider):
    """Best-effort access to NSE public JSON endpoints."""

    name = "nse"

    def __init__(self, cache: Cache | None = None, timeout: float = 8.0) -> None:
        self._cache = cache
        self._timeout = timeout
        self._session: requests.Session | None = None

    def fetch(self, what: str = "sectors", **kwargs: Any) -> Any:
        """Dispatch to a specific dataset: sectors | fii_dii | pcr."""
        dispatch = {
            "sectors": self.fetch_sectors,
            "fii_dii": self.fetch_fii_dii,
            "pcr": self.fetch_pcr,
        }
        if what not in dispatch:
            raise ValueError(f"Unknown NSE dataset {what!r}. Known: {list(dispatch)}")
        return dispatch[what](**kwargs)

    def fetch_sectors(self) -> list[SectorPerf]:
        data = self._get_json("/api/allIndices")
        if not data:
            return []
        wanted = set(SECTOR_INDICES)
        out: list[SectorPerf] = []
        for row in data.get("data", []):
            if row.get("index") in wanted:
                out.append(
                    SectorPerf(
                        name=row["index"],
                        change_pct=float(row.get("percentChange", 0.0)),
                        # relative_strength refined in scoring; seed with a bounded proxy.
                        relative_strength=_clamp(50 + float(row.get("percentChange", 0.0)) * 10),
                    )
                )
        out.sort(key=lambda s: s.change_pct, reverse=True)
        return out

    def fetch_fii_dii(self) -> dict[str, float]:
        """Net FII/DII cash-market flows in ₹ crore (best effort)."""
        data = self._get_json("/api/fiidiiTradeReact")
        if not data:
            return {}
        out: dict[str, float] = {}
        for row in data if isinstance(data, list) else []:
            cat = str(row.get("category", "")).upper()
            net = _to_float(row.get("netValue"))
            if "FII" in cat or "FPI" in cat:
                out["FII"] = net
            elif "DII" in cat:
                out["DII"] = net
        return out

    def fetch_pcr(self, symbol: str = "NIFTY") -> float | None:
        """Put-Call Ratio from the option chain (open interest)."""
        data = self._get_json(f"/api/option-chain-indices?symbol={symbol}")
        if not data:
            return None
        try:
            rows = data["records"]["data"]
            ce = sum(r["CE"]["openInterest"] for r in rows if "CE" in r)
            pe = sum(r["PE"]["openInterest"] for r in rows if "PE" in r)
            return round(pe / ce, 3) if ce else None
        except (KeyError, TypeError, ZeroDivisionError):
            logger.debug("could not compute PCR for %s", symbol)
            return None

    # ── internal ──────────────────────────────────────────────
    def _ensure_session(self) -> requests.Session:
        if self._session is None:
            s = requests.Session()
            s.headers.update(_HEADERS)
            try:
                s.get(_BASE, timeout=self._timeout)  # prime cookies
            except requests.RequestException:
                logger.warning("could not prime NSE session cookies")
            self._session = s
        return self._session

    def _get_json(self, path: str) -> Any:
        cache_key = f"{self.name}:{path}"
        if self._cache and (hit := self._cache.get(cache_key)) is not None:
            return hit
        try:
            resp = self._ensure_session().get(f"{_BASE}{path}", timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError):
            logger.warning("NSE request failed: %s (endpoint may be blocked)", path)
            return None
        if self._cache:
            self._cache.set(cache_key, data, ttl=600)
        return data


def _to_float(value: Any) -> float:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


def _clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))
