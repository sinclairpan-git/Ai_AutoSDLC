"""Execution logger — append task and batch results to execution-log.md."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)


class ExecutionLogger:
    """Append-only logger writing execution results to a Markdown file."""

    def __init__(self, log_path: Path) -> None:
        self._path = log_path
        self._last_timestamp = ""
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text("# Execution Log\n\n", encoding="utf-8")

    def log_task(self, task_id: str, status: str, details: str = "") -> str:
        """Append a task execution record.

        Args:
            task_id: Task identifier.
            status: Task status string.
            details: Optional details or notes.

        Returns:
            ISO timestamp of the log entry.
        """
        ts = now_iso()
        self._last_timestamp = ts
        line = f"- [{ts}] **{task_id}**: {status}"
        if details:
            line += f" — {details}"
        line += "\n"
        self._append(line)
        return ts

    def log_batch(self, batch_id: int, summary: str) -> str:
        """Append a batch summary record.

        Args:
            batch_id: Batch identifier.
            summary: Batch completion summary.

        Returns:
            ISO timestamp of the log entry.
        """
        ts = now_iso()
        self._last_timestamp = ts
        self._append(f"\n### Batch {batch_id}\n\n{summary}\n\n")
        return ts

    def get_last_log_timestamp(self) -> str:
        """Return the timestamp of the most recent log entry."""
        return self._last_timestamp

    def _append(self, text: str) -> None:
        """Append text to the log file."""
        with self._path.open("a", encoding="utf-8") as f:
            f.write(text)
