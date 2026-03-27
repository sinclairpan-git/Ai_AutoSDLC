"""Bounded telemetry readiness surfaces for status/doctor commands."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ai_sdlc.telemetry.contracts import ScopeLevel
from ai_sdlc.telemetry.paths import (
    telemetry_indexes_root,
    telemetry_local_root,
    telemetry_manifest_path,
)
from ai_sdlc.telemetry.registry import build_default_ccp_registry
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore

_SAMPLE_LIMIT = 3


def build_status_json_surface(repo_root: Path) -> dict[str, Any]:
    """Return bounded telemetry status JSON without implicit init/rebuild."""
    manifest_state = _load_manifest_state(repo_root)
    if manifest_state["state"] == "not_initialized":
        return {
            "telemetry": {
                "state": "not_initialized",
                "current": None,
                "latest": None,
            }
        }
    if manifest_state["state"] != "loaded":
        return {
            "telemetry": {
                "state": "invalid_manifest",
                "current": None,
                "latest": None,
                "error": manifest_state.get("error"),
            }
        }

    manifest = manifest_state["manifest"]
    return {
        "telemetry": {
            "state": "ready",
            "current": {
                "manifest_version": manifest.get("version"),
                "sessions": _current_bucket_summary(
                    manifest.get("sessions", {}), "latest_goal_session_id"
                ),
                "runs": _current_bucket_summary(
                    manifest.get("runs", {}), "latest_workflow_run_id"
                ),
                "steps": _current_bucket_summary(
                    manifest.get("steps", {}), "latest_step_id"
                ),
            },
            "latest": _load_latest_index_summaries(repo_root),
        }
    }


def build_doctor_readiness_items(repo_root: Path | None) -> list[dict[str, str]]:
    """Return read-only telemetry readiness diagnostics for doctor output."""
    if repo_root is None:
        return [
            {
                "name": "telemetry root writable",
                "state": "unavailable",
                "detail": "not inside an AI-SDLC project",
            },
            {
                "name": "manifest state",
                "state": "unavailable",
                "detail": "not inside an AI-SDLC project",
            },
            {
                "name": "registry parseability",
                "state": "unavailable",
                "detail": "not inside an AI-SDLC project",
            },
            {
                "name": "writer path validity",
                "state": "unavailable",
                "detail": "not inside an AI-SDLC project",
            },
            {
                "name": "resolver health",
                "state": "unavailable",
                "detail": "not inside an AI-SDLC project",
            },
            {
                "name": "status --json surface",
                "state": "unavailable",
                "detail": "not inside an AI-SDLC project",
            },
        ]

    root_check = _telemetry_root_writable(repo_root)
    manifest_state = _load_manifest_state(repo_root)
    manifest_check = _manifest_check(manifest_state, root_check["state"])
    registry_check = _registry_check()
    writer_path_check = _writer_path_check(repo_root)
    resolver_check = _resolver_check(repo_root)
    status_surface_check = _status_surface_check(repo_root)
    return [
        root_check,
        manifest_check,
        registry_check,
        writer_path_check,
        resolver_check,
        status_surface_check,
    ]


def _current_bucket_summary(values: dict[str, Any], latest_key_name: str) -> dict[str, Any]:
    ids = list(values.keys())
    latest_id = ids[-1] if ids else None
    return {"count": len(ids), latest_key_name: latest_id}


def _load_latest_index_summaries(repo_root: Path) -> dict[str, Any]:
    indexes_root = telemetry_indexes_root(repo_root)
    artifacts_payload = _read_json_file(indexes_root / "latest-artifacts.json")
    violations_payload = _read_json_file(indexes_root / "open-violations.json")
    timeline_payload = _read_json_file(indexes_root / "timeline-cursor.json")

    artifact_ids = _coerce_id_list(artifacts_payload, "artifact_ids")
    violation_ids = _coerce_id_list(violations_payload, "violation_ids")

    timeline_cursor: dict[str, Any] | None = None
    if isinstance(timeline_payload, dict):
        timeline_cursor = {
            "event_count": timeline_payload.get("event_count"),
            "last_event_id": timeline_payload.get("last_event_id"),
            "last_timestamp": timeline_payload.get("last_timestamp"),
        }

    return {
        "artifacts": {
            "count": len(artifact_ids),
            "sample_ids": artifact_ids[-_SAMPLE_LIMIT:],
        },
        "open_violations": {
            "count": len(violation_ids),
            "sample_ids": violation_ids[-_SAMPLE_LIMIT:],
        },
        "timeline_cursor": timeline_cursor,
    }


def _coerce_id_list(payload: Any, field_name: str) -> list[str]:
    if not isinstance(payload, dict):
        return []
    value = payload.get(field_name)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]


def _telemetry_root_writable(repo_root: Path) -> dict[str, str]:
    local_root = telemetry_local_root(repo_root)
    target = local_root if local_root.exists() else _nearest_existing_parent(local_root)
    writable = os.access(target, os.W_OK)
    return {
        "name": "telemetry root writable",
        "state": "ok" if writable else "error",
        "detail": (
            f"{local_root} writable"
            if writable
            else f"{local_root} not writable via parent {target}"
        ),
    }


def _nearest_existing_parent(path: Path) -> Path:
    current = path
    while not current.exists():
        current = current.parent
    return current


def _manifest_check(
    manifest_state: dict[str, Any],
    root_state: str,
) -> dict[str, str]:
    state = manifest_state["state"]
    if state == "loaded":
        return {
            "name": "manifest state",
            "state": "ok",
            "detail": "loaded",
        }
    if state == "not_initialized":
        if root_state == "ok":
            return {
                "name": "manifest state",
                "state": "warn",
                "detail": "not_initialized (can initialize)",
            }
        return {
            "name": "manifest state",
            "state": "error",
            "detail": "not_initialized (root not writable)",
        }
    return {
        "name": "manifest state",
        "state": "error",
        "detail": f"invalid ({manifest_state.get('error', 'unknown')})",
    }


def _registry_check() -> dict[str, str]:
    try:
        build_default_ccp_registry()
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "name": "registry parseability",
            "state": "error",
            "detail": str(exc),
        }
    return {
        "name": "registry parseability",
        "state": "ok",
        "detail": "loaded",
    }


def _writer_path_check(repo_root: Path) -> dict[str, str]:
    store = TelemetryStore(repo_root)
    local_root = telemetry_local_root(repo_root)
    try:
        event_path = store.event_stream_path(
            scope_level=ScopeLevel.SESSION,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
        )
        evidence_path = store.evidence_stream_path(
            scope_level=ScopeLevel.SESSION,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
        )
        valid = event_path.is_relative_to(local_root) and evidence_path.is_relative_to(local_root)
    except Exception as exc:
        return {
            "name": "writer path validity",
            "state": "error",
            "detail": str(exc),
        }
    if not valid:
        return {
            "name": "writer path validity",
            "state": "error",
            "detail": "paths escaped telemetry local root",
        }
    return {
        "name": "writer path validity",
        "state": "ok",
        "detail": "event/evidence paths are under local telemetry root",
    }


def _resolver_check(repo_root: Path) -> dict[str, str]:
    resolver = SourceResolver(TelemetryStore(repo_root))
    try:
        resolver.resolve("unsupported", "evt_0123456789abcdef0123456789abcdef")
    except ValueError:
        return {
            "name": "resolver health",
            "state": "ok",
            "detail": "resolver callable",
        }
    except Exception as exc:
        return {
            "name": "resolver health",
            "state": "error",
            "detail": str(exc),
        }
    return {
        "name": "resolver health",
        "state": "ok",
        "detail": "resolved",
    }


def _status_surface_check(repo_root: Path) -> dict[str, str]:
    try:
        payload = build_status_json_surface(repo_root)
        state = payload["telemetry"]["state"]
    except Exception as exc:  # pragma: no cover - defensive
        return {
            "name": "status --json surface",
            "state": "error",
            "detail": str(exc),
        }
    return {
        "name": "status --json surface",
        "state": "ok",
        "detail": state,
    }


def _load_manifest_state(repo_root: Path) -> dict[str, Any]:
    manifest_path = telemetry_manifest_path(repo_root)
    if not manifest_path.exists():
        return {"state": "not_initialized"}

    payload = _read_json_file(manifest_path)
    if not isinstance(payload, dict):
        return {"state": "invalid", "error": "manifest must be a JSON object"}

    sessions = payload.get("sessions")
    runs = payload.get("runs")
    steps = payload.get("steps")
    if not isinstance(sessions, dict) or not isinstance(runs, dict) or not isinstance(steps, dict):
        return {
            "state": "invalid",
            "error": "manifest missing sessions/runs/steps maps",
        }
    return {"state": "loaded", "manifest": payload}


def _read_json_file(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
