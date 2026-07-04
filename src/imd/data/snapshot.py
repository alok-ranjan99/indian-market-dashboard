"""Orchestrate a full daily data pull and persist it.

Run:  python -m imd.data.snapshot         # pull + save + print summary
This is what the Phase 8 cron job will call pre-market.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from imd.data.base import InMemoryCache
from imd.data.global_cues import GlobalCuesProvider
from imd.data.news import NewsProvider
from imd.data.nse import NSEProvider
from imd.data.prices import PriceProvider
from imd.data.store import SQLiteStore
from imd.data.universe import INDEX_SYMBOLS

logger = logging.getLogger(__name__)


@dataclass
class Snapshot:
    """A full day's market picture — the input the scoring engine will consume."""

    indices: dict[str, Any] = field(default_factory=dict)
    quotes: dict[str, Any] = field(default_factory=dict)
    sectors: list[Any] = field(default_factory=list)
    fii_dii: dict[str, float] = field(default_factory=dict)
    pcr: float | None = None
    global_cues: dict[str, Any] = field(default_factory=dict)
    news: list[Any] = field(default_factory=list)

    def summary(self) -> dict[str, int]:
        return {
            "indices": len(self.indices),
            "quotes": len(self.quotes),
            "sectors": len(self.sectors),
            "fii_dii": len(self.fii_dii),
            "pcr": 1 if self.pcr is not None else 0,
            "global_cues": len(self.global_cues),
            "news": len(self.news),
        }


def collect(*, cache: InMemoryCache | None = None) -> Snapshot:
    """Pull every dataset. Each provider fails soft, so a partial snapshot is normal."""
    cache = cache or InMemoryCache()
    prices = PriceProvider(cache)
    nse = NSEProvider(cache)
    cues = GlobalCuesProvider(cache)
    news = NewsProvider(cache)

    indices = {name: prices.index_quote(name) for name in INDEX_SYMBOLS}
    return Snapshot(
        indices={k: v for k, v in indices.items() if v is not None},
        quotes=prices.fetch(),
        sectors=nse.fetch_sectors(),
        fii_dii=nse.fetch_fii_dii(),
        pcr=nse.fetch_pcr(),
        global_cues=cues.fetch(),
        news=news.fetch(),
    )


def _serialize(snap: Snapshot) -> dict[str, Any]:
    return {"summary": snap.summary()}  # full payload serialization firms up in Phase 5


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    snap = collect()
    summary = snap.summary()
    SQLiteStore().save_snapshot("daily", _serialize(snap))
    print("Snapshot collected:")
    for k, v in summary.items():
        print(f"  {k:12} {v}")


if __name__ == "__main__":
    main()
