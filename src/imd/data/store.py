"""SQLite implementation of the Store interface — daily history for backtesting.

Snapshots are stored as JSON blobs keyed by (kind, date) so the schema never needs
to change as payloads evolve. Swapping to Postgres later means one new Store subclass.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

from imd.data.base import Store

DEFAULT_DB = Path("data/imd.db")


class SQLiteStore(Store):
    def __init__(self, path: Path | str = DEFAULT_DB) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind    TEXT NOT NULL,
                    day     TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created TEXT NOT NULL DEFAULT (datetime('now')),
                    UNIQUE(kind, day)
                )
                """
            )

    def save_snapshot(self, kind: str, payload: dict, *, day: str | None = None) -> None:
        day = day or date.today().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO snapshots(kind, day, payload) VALUES (?,?,?) "
                "ON CONFLICT(kind, day) DO UPDATE SET payload=excluded.payload, "
                "created=datetime('now')",
                (kind, day, json.dumps(payload, default=str)),
            )

    def load_history(self, kind: str, limit: int | None = None) -> list[dict]:
        sql = "SELECT day, payload FROM snapshots WHERE kind=? ORDER BY day DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"
        with self._connect() as conn:
            rows = conn.execute(sql, (kind,)).fetchall()
        return [{"day": r["day"], **json.loads(r["payload"])} for r in rows]
