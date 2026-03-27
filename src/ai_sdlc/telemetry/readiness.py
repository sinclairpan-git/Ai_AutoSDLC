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
_MAX_RESOLVER_SCOPE_PROBES = 32


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
                    repo_root,
                    manifest.get("sessions", {}),
                    "latest_goal_session_id",
                ),
                "runs": _current_bucket_summary(
                    repo_root,
                    manifest.get("runs", {}),
                    "latest_workflow_run_id",
                ),
                "steps": _current_bucket_summary(
                    repo_root,
                    manifest.get("steps", {}),
                    "latest_step_id",
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


def _current_bucket_summary(
    repo_root: Path,
    values: dict[str, Any],
    latest_key_name: str,
) -> dict[str, Any]:
    latest_id = _latest_bucket_id(repo_root, values)
    return {"count": len(values), latest_key_name: latest_id}


def _latest_bucket_id(repo_root: Path, values: dict[str, Any]) -> str | None:
    if not values:
        return None
    scored: list[tuple[str, int]] = []
    local_root = telemetry_local_root(repo_root)
    for object_id, entry in values.items():
        if not isinstance(object_id, str) or not isinstance(entry, dict):
            continue
        path_value = entry.get("path")
        if not isinstance(path_value, str):
            continue
        scope_root = local_root / path_value
        scored.append((object_id, _path_mtime_ns(scope_root)))
    if not scored:
        return None
    # Prefer most recently touched scope root; tie-break by id for stable output.
    return max(scored, key=lambda item: (item[1], item[0]))[0]


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
            "sample_ids": artifact_ids[:_SAMPLE_LIMIT],
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
    candidates = _resolver_event_probe_candidates(repo_root)
    if not candidates:
        return {
            "name": "resolver health",
            "state": "warn",
            "detail": "no supported source fixture found",
        }
    first_error: Exception | None = None
    for events_path, source_ref in candidates:
        resolver = SourceResolver(
            _BoundedEventResolverStore(events_path=events_path, source_ref=source_ref)
        )
        try:
            resolver.resolve("event", source_ref)
        except Exception as exc:
            if first_error is None:
                first_error = exc
            continue
        return {
            "name": "resolver health",
            "state": "ok",
            "detail": "supported source kind resolved: event",
        }
    if first_error is not None:
        return {
            "name": "resolver health",
            "state": "error",
            "detail": str(first_error),
        }
    return {
        "name": "resolver health",
        "state": "warn",
        "detail": "no supported source fixture found",
    }


def _resolver_event_probe_candidates(repo_root: Path) -> list[tuple[Path, str]]:
    manifest_state = _load_manifest_state(repo_root)
    if manifest_state["state"] != "loaded":
        return []

    manifest = manifest_state["manifest"]
    timeline_payload = _read_json_file(telemetry_indexes_root(repo_root) / "timeline-cursor.json")
    timeline_event_id = None
    if isinstance(timeline_payload, dict):
        value = timeline_payload.get("last_event_id")
        if isinstance(value, str):
            timeline_event_id = value

    if timeline_event_id is None:
        return []

    candidate_paths = _manifest_events_paths(repo_root, manifest)[:_MAX_RESOLVER_SCOPE_PROBES]
    candidates: list[tuple[Path, str]] = []
    for events_path in candidate_paths:
        if _path_has_trace_content(events_path):
            candidates.append((events_path, timeline_event_id))
    return candidates


def _manifest_events_paths(repo_root: Path, manifest: dict[str, Any]) -> list[Path]:
    local_root = telemetry_local_root(repo_root)
    scored_paths: list[tuple[int, Path]] = []
    seen: set[str] = set()
    for field_name in ("steps", "runs", "sessions"):
        bucket = manifest.get(field_name)
        if not isinstance(bucket, dict):
            continue
        for entry in bucket.values():
            if not isinstance(entry, dict):
                continue
            path_value = entry.get("path")
            if not isinstance(path_value, str):
                continue
            events_path = local_root / path_value / "events.ndjson"
            path_key = events_path.as_posix()
            if path_key in seen:
                continue
            seen.add(path_key)
            scored_paths.append((_path_mtime_ns(events_path), events_path))
    scored_paths.sort(key=lambda item: (item[0], item[1].as_posix()), reverse=True)
    return [path for _, path in scored_paths]


class _BoundedEventResolverStore:
    """Store adapter for bounded resolver-health probes on one events stream."""

    def __init__(self, *, events_path: Path, source_ref: str) -> None:
        self._events_path = events_path
        self._source_ref = source_ref

    def find_append_only_payload(self, kind: str, source_ref: str) -> tuple[Path, dict[str, Any]] | None:
        if kind != "telemetry_event" or source_ref != self._source_ref:
            return None
        if not _path_has_trace_content(self._events_path):
            return None
        return self._events_path, {"event_id": source_ref}


def _path_has_trace_content(path: Path) -> bool:
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def _first_event_id_in_file(path: Path) -> str | None:
    for payload in _iter_ndjson_dicts(path):
        event_id = payload.get("event_id")
        if isinstance(event_id, str) and event_id.startswith("evt_"):
            return event_id
    return None


def _iter_ndjson_dicts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payloads: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if isinstance(payload, dict):
                    payloads.append(payload)
    except Exception:
        return payloads
    return payloads


def _path_mtime_ns(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return -1


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
