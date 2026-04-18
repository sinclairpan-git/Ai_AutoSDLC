"""Console/stdin helpers for bilingual CLI output."""

from __future__ import annotations

import os
import sys


def _reconfigure_stream(stream: object) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")


def configure_stdio_for_bilingual_cli() -> None:
    """Force UTF-8 stdio on Windows before Rich consoles are created."""

    if not sys.platform.startswith("win"):
        return

    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    _reconfigure_stream(sys.stdin)
    _reconfigure_stream(sys.stdout)
    _reconfigure_stream(sys.stderr)
