"""Index generator — scan .ai-sdlc/ and build project index."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from ai_sdlc.utils.fs import AI_SDLC_DIR

logger = logging.getLogger(__name__)


def generate_index(root: Path) -> dict[str, object]:
    """Scan the .ai-sdlc/ directory and build a structured index.

    Returns:
        Dictionary with directory structure, file counts, and key paths.
    """
    ai_sdlc = root / AI_SDLC_DIR
    if not ai_sdlc.is_dir():
        return {"error": ".ai-sdlc directory not found"}

    index: dict[str, object] = {
        "root": str(root),
        "directories": [],
        "files": [],
        "file_count": 0,
    }

    dirs: list[str] = []
    files: list[str] = []
    for item in sorted(ai_sdlc.rglob("*")):
        rel = str(item.relative_to(root))
        if item.is_dir():
            dirs.append(rel)
        elif item.is_file():
            files.append(rel)

    index["directories"] = dirs
    index["files"] = files
    index["file_count"] = len(files)
    return index


def save_index(root: Path, index: dict[str, object]) -> None:
    """Save index to .ai-sdlc/state/repo-facts.json."""
    output = root / AI_SDLC_DIR / "state" / "repo-facts.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(index, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
