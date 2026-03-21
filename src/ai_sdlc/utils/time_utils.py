"""Time and timestamp utilities."""

from __future__ import annotations

from datetime import datetime, timezone


def now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(s: str) -> datetime:
    """Parse an ISO 8601 timestamp string."""
    return datetime.fromisoformat(s)
