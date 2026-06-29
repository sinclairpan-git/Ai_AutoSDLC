"""Artifact store helpers for Loop Engine and local PR review runs."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]
from pydantic import BaseModel

from ai_sdlc.utils.helpers import AI_SDLC_DIR

_IS_WINDOWS = os.name == "nt"
_WINDOWS_REPLACE_DELAYS = (0.05, 0.1, 0.2)


class LoopArtifactStore:
    """Small persistence boundary for durable loop/review artifacts."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def loop_run_dir(self, loop_id: str, *, loop_type: str = "local-pr-review") -> Path:
        """Return the stable directory for one loop run."""

        loop_type_dir = _artifact_child_dir(
            self.root / AI_SDLC_DIR / "loops",
            loop_type,
        )
        return _artifact_child_dir(loop_type_dir, loop_id)

    def review_run_dir(self, review_id: str) -> Path:
        """Return the stable directory for one local PR review run."""

        return _artifact_child_dir(self.root / AI_SDLC_DIR / "reviews" / "pr", review_id)

    def create_loop_run_dir(
        self,
        loop_id: str,
        *,
        loop_type: str = "local-pr-review",
    ) -> Path:
        """Create and return ``.ai-sdlc/loops/<loop-type>/<loop-id>``."""

        path = self.loop_run_dir(loop_id, loop_type=loop_type)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_review_run_dir(self, review_id: str) -> Path:
        """Create and return ``.ai-sdlc/reviews/pr/<review-id>``."""

        path = self.review_run_dir(review_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_json_artifact(self, path: Path, payload: BaseModel | dict[str, Any]) -> Path:
        """Atomically write a JSON artifact."""

        data = _payload_to_data(payload)
        serialized = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            sort_keys=False,
        )
        return _atomic_write_text(path, serialized + "\n")

    def write_yaml_artifact(self, path: Path, payload: BaseModel | dict[str, Any]) -> Path:
        """Atomically write a YAML artifact."""

        data = _payload_to_data(payload)
        serialized = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
        return _atomic_write_text(path, serialized)

    def write_markdown_artifact(self, path: Path, content: str) -> Path:
        """Atomically write a Markdown artifact."""

        text = content if content.endswith("\n") else f"{content}\n"
        return _atomic_write_text(path, text)

    def read_json_artifact(self, path: Path) -> dict[str, Any]:
        """Read a JSON artifact as a mapping."""

        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON artifact root must be an object")
        return data


def _payload_to_data(payload: BaseModel | dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload, BaseModel):
        data = payload.model_dump(mode="json")
    else:
        data = payload
    return dict(data)


def _artifact_child_dir(base: Path, identifier: str) -> Path:
    text = identifier.strip()
    if (
        not text
        or text in {".", ".."}
        or "/" in text
        or "\\" in text
        or ":" in text
    ):
        raise ValueError(f"Unsafe artifact identifier: {identifier!r}")
    path = base / text
    base_resolved = base.resolve(strict=False)
    path_resolved = path.resolve(strict=False)
    try:
        path_resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError(f"Unsafe artifact identifier: {identifier!r}") from exc
    return path


def _atomic_write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return path

    temp_path = path.with_name(f".{path.name}.{os.getpid()}.{time.monotonic_ns()}.tmp")
    try:
        try:
            temp_path.write_text(content, encoding="utf-8")
        except PermissionError:
            path.write_text(content, encoding="utf-8")
            return path
        _replace_with_retry(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return path


def _replace_with_retry(source: Path, destination: Path) -> None:
    try:
        source.replace(destination)
        return
    except PermissionError:
        if not _IS_WINDOWS:
            raise

    for delay in _WINDOWS_REPLACE_DELAYS:
        time.sleep(delay)
        try:
            source.replace(destination)
            return
        except PermissionError:
            continue

    source.replace(destination)


__all__ = ["LoopArtifactStore"]
