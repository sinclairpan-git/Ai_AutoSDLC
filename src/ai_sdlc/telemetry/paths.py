"""Filesystem path helpers for the telemetry V1 storage layout."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from ai_sdlc.telemetry.ids import TELEMETRY_ID_RE

_MAX_SCOPE_DIRNAME_LENGTH = 24
_COMPACT_SCOPE_SEPARATOR = "~"


def _scope_dir_name(identifier: str) -> str:
    """Return a Windows-safe filesystem directory name for a telemetry scope id."""
    normalized = str(identifier).strip()
    if TELEMETRY_ID_RE.fullmatch(normalized):
        if len(normalized) > _MAX_SCOPE_DIRNAME_LENGTH:
            prefix, suffix = normalized.split("_", 1)
            encoded = base64.urlsafe_b64encode(bytes.fromhex(suffix)).decode("ascii")
            return f"{prefix}{_COMPACT_SCOPE_SEPARATOR}{encoded.rstrip('=')}"
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
    prefix, encoded = normalized.split(_COMPACT_SCOPE_SEPARATOR, 1)
    if not prefix or not encoded:
        return normalized
    padded = encoded + ("=" * (-len(encoded) % 4))
    try:
        suffix = base64.urlsafe_b64decode(padded.encode("ascii")).hex()
    except (ValueError, TypeError):
        return normalized
    candidate = f"{prefix}_{suffix}"
    if TELEMETRY_ID_RE.fullmatch(candidate):
        return candidate
    return normalized


def _scope_container(long_name: str, short_name: str, identifier: str) -> str:
    if _scope_dir_name(identifier) != identifier:
        return short_name
    return long_name


def telemetry_id_file_name(identifier: str, extension: str = ".json") -> str:
    """Return a Windows-safe file name for a telemetry object id."""
    return f"{_scope_dir_name(identifier)}{extension}"


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
    return (
        telemetry_local_root(repo_root)
        / _scope_container("sessions", "s", goal_session_id)
        / _scope_dir_name(goal_session_id)
    )


def run_root(repo_root: Path, goal_session_id: str, workflow_run_id: str) -> Path:
    """Return the filesystem root for a workflow run."""
    return (
        session_root(repo_root, goal_session_id)
        / _scope_container("runs", "r", workflow_run_id)
        / _scope_dir_name(workflow_run_id)
    )


def step_root(
    repo_root: Path, goal_session_id: str, workflow_run_id: str, step_id: str
) -> Path:
    """Return the filesystem root for a workflow step."""
    return (
        run_root(repo_root, goal_session_id, workflow_run_id)
        / _scope_container("steps", "t", step_id)
        / _scope_dir_name(step_id)
    )


def provenance_root(scope_root: Path) -> Path:
    """Return the provenance subtree for a telemetry scope."""
    if any(part in {"s", "r", "t"} for part in scope_root.parts):
        return scope_root / "p"
    return scope_root / "provenance"
