"""Data-layer tests — fully mocked, no network (safe for CI)."""

from __future__ import annotations

import pandas as pd

from imd.data import get_universe
from imd.data.base import InMemoryCache
from imd.data.news import NewsProvider
from imd.data.prices import PriceProvider
from imd.data.store import SQLiteStore
from imd.domain import Quote


# ── universe ──────────────────────────────────────────────
def test_universe_nifty50() -> None:
    yf = get_universe("NIFTY50")
    assert len(yf) == 50
    assert all(s.endswith(".NS") for s in yf)
    bare = get_universe("NIFTY50", yf_suffix=False)
    assert "RELIANCE" in bare and all(not s.endswith(".NS") for s in bare)


# ── cache ─────────────────────────────────────────────────
def test_inmemory_cache_ttl() -> None:
    c = InMemoryCache()
    c.set("k", 42, ttl=None)
    assert c.get("k") == 42
    assert c.get("missing") is None


# ── prices (mock yfinance frame) ──────────────────────────
def _fake_frame() -> pd.DataFrame:
    idx = pd.to_datetime(["2026-07-01", "2026-07-02"])
    cols = pd.MultiIndex.from_product([["RELIANCE.NS"], ["Open", "High", "Low", "Close", "Volume"]])
    return pd.DataFrame(
        [[100, 105, 99, 104, 1000], [104, 110, 103, 108, 1200]], index=idx, columns=cols
    )


def test_price_provider_parses_quotes() -> None:
    quotes = PriceProvider._to_quotes(["RELIANCE.NS"], _fake_frame())
    q = quotes["RELIANCE.NS"]
    assert isinstance(q, Quote)
    assert q.close == 108.0
    assert q.change_pct == round((108 - 104) / 104 * 100, 2)


def test_price_provider_uses_cache() -> None:
    cache = InMemoryCache()
    cache.set("prices:RELIANCE.NS", {"RELIANCE.NS": "cached"}, ttl=None)
    p = PriceProvider(cache)
    assert p.fetch(["RELIANCE.NS"]) == {"RELIANCE.NS": "cached"}


# ── news (mock feedparser) ────────────────────────────────
class _FakeEntry:
    def __init__(self, title: str) -> None:
        self.title = title
        self.link = "http://x"
        self.published_parsed = (2026, 7, 2, 9, 0, 0, 0, 0, 0)


class _FakeParsed:
    def __init__(self, titles: list[str]) -> None:
        self.entries = [_FakeEntry(t) for t in titles]


def test_news_dedupes_and_limits(monkeypatch) -> None:
    def fake_parse(url: str) -> _FakeParsed:
        return _FakeParsed(["Nifty up", "Nifty up", "IT rallies"])  # dup on purpose

    monkeypatch.setattr("imd.data.news.feedparser.parse", fake_parse)
    provider = NewsProvider(feeds={"A": "u1", "B": "u2"})
    items = provider.fetch(limit=10)
    titles = [i.title for i in items]
    assert titles.count("Nifty up") == 1  # deduped across feeds
    assert "IT rallies" in titles


# ── store ─────────────────────────────────────────────────
def test_sqlite_store_roundtrip(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    store.save_snapshot("daily", {"a": 1}, day="2026-07-01")
    store.save_snapshot("daily", {"a": 2}, day="2026-07-02")
    hist = store.load_history("daily")
    assert len(hist) == 2
    assert hist[0]["day"] == "2026-07-02"  # newest first
    assert hist[0]["a"] == 2


def test_sqlite_store_upsert(tmp_path) -> None:
    store = SQLiteStore(tmp_path / "t.db")
    store.save_snapshot("daily", {"v": 1}, day="2026-07-01")
    store.save_snapshot("daily", {"v": 99}, day="2026-07-01")  # same day -> upsert
    hist = store.load_history("daily")
    assert len(hist) == 1 and hist[0]["v"] == 99
