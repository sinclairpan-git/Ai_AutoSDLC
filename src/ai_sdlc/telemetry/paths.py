"""Filesystem path helpers for the telemetry V1 storage layout."""

from __future__ import annotations

from pathlib import Path


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
    return telemetry_local_root(repo_root) / "sessions" / goal_session_id


def run_root(repo_root: Path, goal_session_id: str, workflow_run_id: str) -> Path:
    """Return the filesystem root for a workflow run."""
    return session_root(repo_root, goal_session_id) / "runs" / workflow_run_id


def step_root(
    repo_root: Path, goal_session_id: str, workflow_run_id: str, step_id: str
) -> Path:
    """Return the filesystem root for a workflow step."""
    return run_root(repo_root, goal_session_id, workflow_run_id) / "steps" / step_id
