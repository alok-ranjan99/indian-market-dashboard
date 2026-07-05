"""Service-layer tests with injected fakes — no network."""

from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from imd.domain import NewsItem, Quote, SectorPerf
from imd.sentiment import VaderModel
from imd.service import (
    NewsView,
    assemble_market,
    assemble_swing,
    score_news,
)


def _hist(n: int, start: float, step: float) -> pd.DataFrame:
    close = [start + step * i for i in range(n)]
    return pd.DataFrame({
        "Open": close, "High": [c + 1 for c in close], "Low": [c - 1 for c in close],
        "Close": close, "Volume": [1000] * n,
    })


class _FakePrices:
    def __init__(self) -> None:
        self.quotes = {
            "A.NS": Quote("A.NS", 100, 101, 99, 102, 1000),   # up
            "B.NS": Quote("B.NS", 100, 101, 99, 98, 1000),    # down
        }

    def history(self, symbol, period="4mo"):  # noqa: ARG002
        return _hist(60, 100, 1.0)

    def fetch(self, symbols=None):  # noqa: ARG002
        return self.quotes

    def histories(self, symbols, period="6mo"):  # noqa: ARG002
        return {s: _hist(60, 100, 1.0) for s in symbols}

    def index_quote(self, key):
        return Quote(key, 100, 101, 99, 100, 0)


class _FakeNSE:
    def fetch_fii_dii(self):
        return {"FII": 500.0, "DII": 800.0}

    def fetch_pcr(self):
        return 0.9

    def fetch_sectors(self):
        return [SectorPerf("NIFTY IT", 1.5, 90)]


class _FakeCues:
    def fetch(self):
        return {"Dow Jones": {"price": 40000, "change_pct": 0.4}}


def test_score_news_populates_sentiment() -> None:
    items = [NewsItem("Stocks rally on strong profits", "s", "u", datetime.now(UTC))]
    scored = score_news(items, VaderModel())
    assert scored[0].sentiment_score > 0


def test_assemble_market_with_fakes() -> None:
    view = assemble_market(
        news=NewsView(items=[]),
        prices=_FakePrices(), nse=_FakeNSE(), cues=_FakeCues(),
    )
    assert view.fear_greed.value >= 0
    assert view.breadth == {"advances": 1, "declines": 1}
    assert view.flows["FII"] == 500.0
    assert "Nifty 50" in view.indices
    assert view.bias is not None


def test_assemble_swing_with_fakes() -> None:
    from imd.service import SectorView

    view = assemble_swing(
        prices=_FakePrices(),
        sectors=SectorView(sectors=[SectorPerf("NIFTY IT", 1.5, 90)]),
        universe=["A.NS", "B.NS", "C.NS"],
        limit=10,
    )
    assert len(view.candidates) == 3
    # scores are sorted descending
    values = [c.swing.value for c in view.candidates]
    assert values == sorted(values, reverse=True)
