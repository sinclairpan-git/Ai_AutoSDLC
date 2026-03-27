"""Telemetry-specific UTC clock helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime

UTC_Z_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T"
    r"\d{2}:\d{2}:\d{2}"
    r"(?:\.\d{1,6})?Z$"
)


def utc_now_z() -> str:
    """Return the current UTC timestamp in RFC3339 format with trailing Z."""
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def validate_utc_z_timestamp(value: str) -> str:
    """Validate an RFC3339 UTC timestamp that uses a trailing Z suffix."""
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    if not UTC_Z_TIMESTAMP_RE.fullmatch(value):
        raise ValueError(f"invalid UTC Z timestamp: {value!r}")
    # Ensure the value is parseable as UTC.
    datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    return value
