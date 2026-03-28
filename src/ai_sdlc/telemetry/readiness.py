"""Bounded telemetry readiness surfaces for status/doctor commands."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
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
_EVENT_TAIL_PROBE_BYTES = 65_536


def build_status_json_surface(repo_root: Path) -> dict[str, Any]:
    """Return bounded telemetry status JSON without implicit init/rebuild."""
    manifest_state = _load_manifest_state(repo_root)
    store = TelemetryStore(repo_root)
    derived_indexes: dict[str, dict[str, Any]] | None = None

    def _derived_index_payloads() -> dict[str, dict[str, Any]]:
        nonlocal derived_indexes
        if derived_indexes is None:
            derived_indexes = store.derive_index_payloads()
        return derived_indexes

    timeline_payload = _read_json_file(telemetry_indexes_root(repo_root) / "timeline-cursor.json")
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
    derived_timeline_payload: dict[str, Any] | None = None

    def _resolved_latest_id(field_name: str, values: dict[str, Any]) -> str | None:
        nonlocal derived_timeline_payload
        latest_id = _timeline_latest_id(timeline_payload, field_name)
        if latest_id in values:
            return latest_id
        if derived_timeline_payload is None:
            derived_timeline_payload = _derived_index_payloads()["timeline_cursor"]
        latest_id = _timeline_latest_id(derived_timeline_payload, field_name)
        return latest_id if latest_id in values else None

    return {
        "telemetry": {
            "state": "ready",
            "current": {
                "manifest_version": manifest.get("version"),
                "sessions": _current_bucket_summary(
                    manifest.get("sessions", {}),
                    "latest_goal_session_id",
                    _resolved_latest_id(
                        "latest_goal_session_id",
                        manifest.get("sessions", {}),
                    ),
                ),
                "runs": _current_bucket_summary(
                    manifest.get("runs", {}),
                    "latest_workflow_run_id",
                    _resolved_latest_id(
                        "latest_workflow_run_id",
                        manifest.get("runs", {}),
                    ),
                ),
                "steps": _current_bucket_summary(
                    manifest.get("steps", {}),
                    "latest_step_id",
                    _resolved_latest_id(
                        "latest_step_id",
                        manifest.get("steps", {}),
                    ),
                ),
            },
            "latest": _load_latest_index_summaries(
                repo_root,
                derived_index_payloads=_derived_index_payloads,
            ),
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
    values: dict[str, Any],
    latest_key_name: str,
    latest_id: str | None,
) -> dict[str, Any]:
    if latest_id not in values:
        latest_id = None
    return {"count": len(values), latest_key_name: latest_id}


def _timeline_latest_id(payload: Any, field_name: str) -> str | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get(field_name)
    if not isinstance(value, str):
        return None
    return value


def _load_latest_index_summaries(
    repo_root: Path,
    *,
    derived_index_payloads: Callable[[], dict[str, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    indexes_root = telemetry_indexes_root(repo_root)
    artifacts_payload = _read_json_file(indexes_root / "latest-artifacts.json")
    violations_payload = _read_json_file(indexes_root / "open-violations.json")
    timeline_payload = _read_json_file(indexes_root / "timeline-cursor.json")

    derived_payloads: dict[str, dict[str, Any]] | None = None

    def _derived_payload(name: str) -> dict[str, Any]:
        nonlocal derived_payloads
        if derived_payloads is None:
            if derived_index_payloads is None:
                derived_payloads = TelemetryStore(repo_root).derive_index_payloads()
            else:
                derived_payloads = derived_index_payloads()
        return derived_payloads[name]

    artifact_ids, artifacts_valid = _coerce_id_list(artifacts_payload, "artifact_ids")
    if not artifacts_valid:
        artifact_ids, _ = _coerce_id_list(_derived_payload("latest_artifacts"), "artifact_ids")

    violation_ids, violations_valid = _coerce_id_list(violations_payload, "violation_ids")
    if not violations_valid:
        violation_ids, _ = _coerce_id_list(_derived_payload("open_violations"), "violation_ids")

    timeline_cursor = _coerce_timeline_cursor(timeline_payload)
    if timeline_cursor is None:
        timeline_cursor = _coerce_timeline_cursor(_derived_payload("timeline_cursor"))

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


def _coerce_id_list(payload: Any, field_name: str) -> tuple[list[str], bool]:
    if not isinstance(payload, dict):
        return [], False
    value = payload.get(field_name)
    if not isinstance(value, list):
        return [], False
    if not all(isinstance(item, str) for item in value):
        return [], False
    return list(value), True


def _coerce_timeline_cursor(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    event_count = payload.get("event_count")
    last_event_id = payload.get("last_event_id")
    last_timestamp = payload.get("last_timestamp")
    if event_count is not None and not isinstance(event_count, int):
        return None
    if last_event_id is not None and not isinstance(last_event_id, str):
        return None
    if last_timestamp is not None and not isinstance(last_timestamp, str):
        return None
    return {
        "event_count": event_count,
        "last_event_id": last_event_id,
        "last_timestamp": last_timestamp,
    }


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
        if _events_tail_contains_event_id(events_path, timeline_event_id):
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


def _events_tail_contains_event_id(path: Path, event_id: str) -> bool:
    try:
        if not path.is_file():
            return False
        size = path.stat().st_size
        if size <= 0:
            return False
        read_size = min(size, _EVENT_TAIL_PROBE_BYTES)
        with path.open("rb") as handle:
            handle.seek(max(size - read_size, 0))
            chunk = handle.read(read_size)
    except OSError:
        return False

    raw_id = event_id.encode("utf-8")
    return (
        (b'"event_id":"' + raw_id + b'"') in chunk
        or (b'"event_id": "' + raw_id + b'"') in chunk
    )


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
