"""File system, text processing, and time utilities."""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# ── filesystem constants ──

AI_SDLC_DIR = ".ai-sdlc"
PROJECT_STATE_PATH = Path(AI_SDLC_DIR) / "project" / "config" / "project-state.yaml"
PROJECT_CONFIG_PATH = Path(AI_SDLC_DIR) / "project" / "config" / "project-config.yaml"

PROJECT_MARKERS = (
    "package.json",
    "pom.xml",
    "build.gradle",
    "go.mod",
    "Cargo.toml",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "Gemfile",
)
PROJECT_DIRS = ("src", "app")


# ── filesystem helpers ──


def ensure_dir(path: Path) -> Path:
    """Create directory and parents if needed, return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_project_root(start: Path | None = None) -> Path | None:
    """Walk up from start looking for .ai-sdlc/ directory. Return None if not found."""
    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / AI_SDLC_DIR).is_dir():
            return parent
    return None


def is_git_repo(path: Path) -> bool:
    """Check if path is inside a git repository."""
    current = path.resolve()
    return any((parent / ".git").exists() for parent in [current, *current.parents])


def has_project_markers(path: Path) -> bool:
    """Check if path contains common project marker files or directories."""
    for marker in PROJECT_MARKERS:
        if (path / marker).exists():
            return True
    for dir_name in PROJECT_DIRS:
        if (path / dir_name).is_dir():
            return True
    return bool(list(path.glob("*.csproj")))


# ── text helpers ──


def slugify(text: str) -> str:
    """Convert text to a URL/filename-safe slug."""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text to max_len, adding ellipsis if truncated."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


# ── time helpers ──


def now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def parse_iso(s: str) -> datetime:
    """Parse an ISO 8601 timestamp string."""
    return datetime.fromisoformat(s)
