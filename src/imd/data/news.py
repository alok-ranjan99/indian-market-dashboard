"""News acquisition — RSS-first (real-time, free, deploy-safe).

RSS is the primary source. NewsAPI is an optional local-dev enrichment (24h delay +
no-production terms), enabled only when a key is present. Sentiment is left at 0.0
here; the sentiment layer scores items in a later phase.
"""

from __future__ import annotations

import html
import logging
from datetime import UTC, datetime
from typing import Any

import feedparser

from imd.data.base import Cache, DataProvider
from imd.domain import NewsItem

logger = logging.getLogger(__name__)

# Free Indian market RSS feeds (no key, real-time).
RSS_FEEDS: dict[str, str] = {
    "Moneycontrol": "https://www.moneycontrol.com/rss/marketreports.xml",
    "ET Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Livemint": "https://www.livemint.com/rss/markets",
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
}


class NewsProvider(DataProvider):
    """Aggregates + de-duplicates market headlines from RSS feeds."""

    name = "news"

    def __init__(self, cache: Cache | None = None, feeds: dict[str, str] | None = None) -> None:
        self._cache = cache
        self._feeds = feeds or RSS_FEEDS

    def fetch(self, limit: int = 60, **_: Any) -> list[NewsItem]:
        cache_key = f"{self.name}:{limit}"
        if self._cache and (hit := self._cache.get(cache_key)) is not None:
            return hit

        items: list[NewsItem] = []
        for source, url in self._feeds.items():
            items.extend(self._parse_feed(source, url))

        deduped = self._dedupe(items)
        deduped.sort(key=lambda n: n.published, reverse=True)
        result = deduped[:limit]

        if self._cache:
            self._cache.set(cache_key, result, ttl=600)
        return result

    # ── internal ──────────────────────────────────────────────
    def _parse_feed(self, source: str, url: str) -> list[NewsItem]:
        try:
            parsed = feedparser.parse(url)
        except Exception:  # noqa: BLE001
            logger.exception("failed to parse feed %s", source)
            return []
        out: list[NewsItem] = []
        for entry in parsed.entries:
            title = html.unescape(getattr(entry, "title", "")).strip()
            if not title:
                continue
            out.append(
                NewsItem(
                    title=title,
                    source=source,
                    url=getattr(entry, "link", ""),
                    published=self._parse_date(entry),
                )
            )
        return out

    @staticmethod
    def _parse_date(entry: Any) -> datetime:
        for attr in ("published_parsed", "updated_parsed"):
            tm = getattr(entry, attr, None)
            if tm:
                return datetime(*tm[:6], tzinfo=UTC)
        return datetime.now(UTC)

    @staticmethod
    def _dedupe(items: list[NewsItem]) -> list[NewsItem]:
        seen: set[str] = set()
        out: list[NewsItem] = []
        for it in items:
            key = it.title.lower().strip()
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out
