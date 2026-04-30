"""Filesystem path helpers for the telemetry V1 storage layout."""

from __future__ import annotations

import hashlib
from pathlib import Path

from ai_sdlc.telemetry.ids import TELEMETRY_ID_RE

_MAX_SCOPE_DIRNAME_LENGTH = 24
_COMPACT_SCOPE_SEPARATOR = "~"
_COMPACT_SCOPE_HASH_LENGTH = 12
_COMPACT_SCOPE_IDS: dict[str, str] = {}


def _scope_dir_name(identifier: str) -> str:
    """Return a Windows-safe filesystem directory name for a telemetry scope id."""
    normalized = str(identifier).strip()
    if TELEMETRY_ID_RE.fullmatch(normalized):
        if len(normalized) > _MAX_SCOPE_DIRNAME_LENGTH:
            prefix, suffix = normalized.split("_", 1)
            digest = hashlib.sha1(suffix.encode("ascii")).hexdigest()[
                :_COMPACT_SCOPE_HASH_LENGTH
            ]
            compact = f"{prefix}{_COMPACT_SCOPE_SEPARATOR}{digest}"
            _COMPACT_SCOPE_IDS[compact] = normalized
            return compact
        return normalized
    if len(normalized) <= _MAX_SCOPE_DIRNAME_LENGTH:
        return normalized
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    head = normalized[:12].rstrip("-_")
    if not head:
        head = normalized[:12]
    return f"{head}-{digest}"


def scope_id_from_dir_name(dirname: str) -> str:
    """Return the telemetry ID represented by a scope directory name."""
    normalized = str(dirname).strip()
    if _COMPACT_SCOPE_SEPARATOR not in normalized:
        return normalized
    if normalized in _COMPACT_SCOPE_IDS:
        return _COMPACT_SCOPE_IDS[normalized]
    prefix, digest = normalized.split(_COMPACT_SCOPE_SEPARATOR, 1)
    if not prefix or not digest:
        return normalized
    return normalized


def telemetry_local_root(repo_root: Path) -> Path:
    """Return the local telemetry trace root."""
    return repo_root / ".ai-sdlc" / "local" / "telemetry"


def telemetry_reports_root(repo_root: Path) -> Path:
    """Return the project-report telemetry root."""
    return repo_root / ".ai-sdlc" / "project" / "reports" / "telemetry"


def telemetry_manifest_path(repo_root: Path) -> Path:
    """Return the telemetry manifest path."""
    return telemetry_local_root(repo_root) / "manifest.json"


def telemetry_indexes_root(repo_root: Path) -> Path:
    """Return the telemetry index directory path."""
    return telemetry_local_root(repo_root) / "indexes"


def session_root(repo_root: Path, goal_session_id: str) -> Path:
    """Return the filesystem root for a goal session."""
    return telemetry_local_root(repo_root) / "sessions" / _scope_dir_name(goal_session_id)


def run_root(repo_root: Path, goal_session_id: str, workflow_run_id: str) -> Path:
    """Return the filesystem root for a workflow run."""
    return session_root(repo_root, goal_session_id) / "runs" / _scope_dir_name(workflow_run_id)


def step_root(
    repo_root: Path, goal_session_id: str, workflow_run_id: str, step_id: str
) -> Path:
    """Return the filesystem root for a workflow step."""
    return run_root(repo_root, goal_session_id, workflow_run_id) / "steps" / _scope_dir_name(
        step_id
    )


def provenance_root(scope_root: Path) -> Path:
    """Return the provenance subtree for a telemetry scope."""
    return scope_root / "provenance"
