"""
SQLite storage layer.

Used for:
  - Deduplication (one submission per Telegram user)
  - Stats for the /admin command
  - Survives restarts so Google Sheets stays the authoritative copy

The schema is intentionally minimal — Sheets is the primary record store.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import aiosqlite
from loguru import logger


SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    user_id      INTEGER PRIMARY KEY,
    username     TEXT,
    full_name    TEXT NOT NULL,
    email        TEXT NOT NULL,
    phone        TEXT NOT NULL,
    message      TEXT,
    submitted_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_submitted_at ON submissions(submitted_at);
"""


class Storage:
    """Async SQLite wrapper for submission deduplication and stats."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Ensure parent directory exists, open connection, create schema."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(SCHEMA)
        await self._db.commit()
        logger.info("SQLite ready at {}", self._db_path)

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    async def has_submission(self, user_id: int) -> bool:
        """True if this user already submitted the form."""
        if self._db is None:
            raise RuntimeError("Storage not initialized")
        async with self._db.execute(
            "SELECT 1 FROM submissions WHERE user_id = ? LIMIT 1",
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    async def save_submission(self, submission: dict[str, Any]) -> None:
        """Insert a new submission. Raises if a row for this user already exists."""
        if self._db is None:
            raise RuntimeError("Storage not initialized")
        await self._db.execute(
            """
            INSERT INTO submissions
                (user_id, username, full_name, email, phone, message, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submission["user_id"],
                submission.get("username") or None,
                submission["full_name"],
                submission["email"],
                submission["phone"],
                submission.get("message") or None,
                submission["timestamp"],
            ),
        )
        await self._db.commit()

    async def get_stats(self) -> dict[str, int]:
        """Return submission counts: today, this week, all time (UTC)."""
        if self._db is None:
            raise RuntimeError("Storage not initialized")

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        week_start = (now - timedelta(days=7)).isoformat()

        async with self._db.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE submitted_at >= ?) AS today,
                COUNT(*) FILTER (WHERE submitted_at >= ?) AS week,
                COUNT(*) AS total
            FROM submissions
            """,
            (today_start, week_start),
        ) as cursor:
            row = await cursor.fetchone()

        return {
            "today": row[0] if row else 0,
            "week": row[1] if row else 0,
            "total": row[2] if row else 0,
        }
