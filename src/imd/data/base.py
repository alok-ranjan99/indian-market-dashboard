"""Data layer interfaces — the seam that lets us swap free sources for a broker API later.

Add a new source by subclassing DataProvider; nothing downstream changes.
Storage/cache are abstracted so we can move SQLite -> Postgres without touching callers.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Cache(Protocol):
    """Minimal cache contract (Streamlit cache, disk, or Redis can satisfy this)."""

    def get(self, key: str) -> Any | None: ...

    def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...


class InMemoryCache:
    """Default process-local cache with TTL. Fine for a single Streamlit process."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[float | None, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if expires_at is not None and time.monotonic() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = time.monotonic() + ttl if ttl else None
        self._store[key] = (expires_at, value)


class DataProvider(ABC):
    """A source of market data. Implementations: Price, NSE, News, GlobalCues, ...

    Contract: `fetch()` returns provider-specific data (often a DataFrame) and is
    responsible for its own retry/rate-limit handling. Wrap with a Cache upstream.
    """

    #: stable identifier used for cache keys and logging
    name: str = "provider"

    @abstractmethod
    def fetch(self, **kwargs: Any) -> Any:
        """Fetch fresh data. Raise on unrecoverable failure; return best-effort otherwise."""
        raise NotImplementedError


class Store(ABC):
    """Durable storage for daily history (enables backtesting)."""

    @abstractmethod
    def save_snapshot(self, kind: str, payload: dict) -> None: ...

    @abstractmethod
    def load_history(self, kind: str, limit: int | None = None) -> list[dict]: ...
