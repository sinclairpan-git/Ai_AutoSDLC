"""Integration tests for `ai-sdlc doctor`."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry import readiness
from ai_sdlc.telemetry.paths import (
    telemetry_indexes_root,
    telemetry_local_root,
    telemetry_manifest_path,
)

runner = CliRunner()


def _seed_bounded_event_fixture(root: Path) -> str:
    session_id = "gs_0123456789abcdef0123456789abcdef"
    event_id = "evt_0123456789abcdef0123456789abcdef"
    local_root = telemetry_local_root(root)
    local_root.mkdir(parents=True, exist_ok=True)
    telemetry_manifest_path(root).write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {
                    session_id: {"path": f"sessions/{session_id}"},
                },
                "runs": {},
                "steps": {},
            }
        ),
        encoding="utf-8",
    )
    events_path = local_root / "sessions" / session_id / "events.ndjson"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text(
        json.dumps({"event_id": event_id}) + "\n",
        encoding="utf-8",
    )
    indexes_root = telemetry_indexes_root(root)
    indexes_root.mkdir(parents=True, exist_ok=True)
    (indexes_root / "timeline-cursor.json").write_text(
        json.dumps(
            {
                "event_count": 1,
                "last_event_id": event_id,
                "last_timestamp": "2026-03-27T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    return event_id


def test_doctor_runs_and_prints_python() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python executable" in result.output
    assert "sys.prefix" in result.output
    assert "python -m ai_sdlc" in result.output


def test_doctor_reports_telemetry_readiness_without_initializing_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    telemetry_root = telemetry_local_root(tmp_path)
    assert telemetry_root.exists() is False
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "Telemetry readiness" in result.output
    assert "telemetry root writable" in result.output
    assert "manifest state" in result.output
    assert "registry parseability" in result.output
    assert "writer path validity" in result.output
    assert "resolver health" in result.output
    assert "status --json surface" in result.output
    assert "not_initialized" in result.output
    assert telemetry_root.exists() is False


def test_doctor_real_cli_path_does_not_mutate_project_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    config_path = (
        tmp_path
        / ".ai-sdlc"
        / "project"
        / "config"
        / "project-config.yaml"
    )
    before = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    time.sleep(1.2)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    after = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    assert result.exit_code == 0
    assert after == before


def test_doctor_resolver_health_exercises_supported_source_resolution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "resolver health" in result.output
    assert "supported source kind resolved" in result.output


def test_doctor_resolver_health_probe_is_bounded_without_recursive_store_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)

    def _raise_deep_scan(*_args, **_kwargs):
        raise AssertionError("recursive store scan is forbidden")

    monkeypatch.setattr(
        "ai_sdlc.telemetry.store.TelemetryStore.find_append_only_payload",
        _raise_deep_scan,
    )

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "supported source kind resolved" in result.output


def test_doctor_resolver_health_checks_multiple_manifest_listed_scope_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    local_root = telemetry_local_root(tmp_path)
    local_root.mkdir(parents=True, exist_ok=True)

    gs_valid = "gs_00000000000000000000000000000000"
    gs_empty = "gs_ffffffffffffffffffffffffffffffff"
    event_id = "evt_0123456789abcdef0123456789abcdef"

    telemetry_manifest_path(tmp_path).write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {
                    gs_valid: {"path": f"sessions/{gs_valid}"},
                    gs_empty: {"path": f"sessions/{gs_empty}"},
                },
                "runs": {},
                "steps": {},
            }
        ),
        encoding="utf-8",
    )

    valid_events = local_root / "sessions" / gs_valid / "events.ndjson"
    valid_events.parent.mkdir(parents=True, exist_ok=True)
    valid_events.write_text(json.dumps({"event_id": event_id}) + "\n", encoding="utf-8")

    empty_events = local_root / "sessions" / gs_empty / "events.ndjson"
    empty_events.parent.mkdir(parents=True, exist_ok=True)
    empty_events.write_text("", encoding="utf-8")

    indexes_root = telemetry_indexes_root(tmp_path)
    indexes_root.mkdir(parents=True, exist_ok=True)
    (indexes_root / "timeline-cursor.json").write_text(
        json.dumps(
            {
                "event_count": 1,
                "last_event_id": event_id,
                "last_timestamp": "2026-03-27T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "resolver health" in result.output
    assert "supported source kind resolved" in result.output


def test_doctor_resolver_health_does_not_parse_trace_payloads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    _seed_bounded_event_fixture(tmp_path)
    events_path = (
        telemetry_local_root(tmp_path)
        / "sessions"
        / "gs_0123456789abcdef0123456789abcdef"
        / "events.ndjson"
    )
    # Make the stream larger than the probe budget so unbounded reads are detectable.
    large_payload = (json.dumps({"event_id": "evt_0123456789abcdef0123456789abcdef"}) + "\n") * 4000
    events_path.write_text(large_payload, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    original_open = Path.open
    read_sizes: list[int] = []

    class _BoundedReadGuard:
        def __init__(self, handle, max_bytes: int) -> None:
            self._handle = handle
            self._max_bytes = max_bytes

        def __enter__(self):
            self._handle.__enter__()
            return self

        def __exit__(self, exc_type, exc, tb):
            return self._handle.__exit__(exc_type, exc, tb)

        def seek(self, *args, **kwargs):
            return self._handle.seek(*args, **kwargs)

        def read(self, size: int = -1):
            if size < 0 or size > self._max_bytes:
                raise AssertionError("resolver tail probe performed an unbounded read")
            read_sizes.append(size)
            return self._handle.read(size)

        def __getattr__(self, name: str):
            return getattr(self._handle, name)

    def _guarded_open(self: Path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        handle = original_open(self, *args, **kwargs)
        if self == events_path and "b" in mode:
            return _BoundedReadGuard(handle, readiness._EVENT_TAIL_PROBE_BYTES)
        return handle

    monkeypatch.setattr(Path, "open", _guarded_open)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "supported source kind resolved" in result.output
    assert read_sizes
    assert max(read_sizes) <= readiness._EVENT_TAIL_PROBE_BYTES


def test_doctor_resolver_health_is_not_ok_when_timeline_event_id_is_absent_from_candidate_stream(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    local_root = telemetry_local_root(tmp_path)
    local_root.mkdir(parents=True, exist_ok=True)
    session_id = "gs_0123456789abcdef0123456789abcdef"
    present_event_id = "evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    stale_event_id = "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    telemetry_manifest_path(tmp_path).write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {session_id: {"path": f"sessions/{session_id}"}},
                "runs": {},
                "steps": {},
            }
        ),
        encoding="utf-8",
    )
    events_path = local_root / "sessions" / session_id / "events.ndjson"
    events_path.parent.mkdir(parents=True, exist_ok=True)
    events_path.write_text(
        json.dumps({"event_id": present_event_id}) + "\n",
        encoding="utf-8",
    )

    indexes_root = telemetry_indexes_root(tmp_path)
    indexes_root.mkdir(parents=True, exist_ok=True)
    (indexes_root / "timeline-cursor.json").write_text(
        json.dumps(
            {
                "event_count": 1,
                "last_event_id": stale_event_id,
                "last_timestamp": "2026-03-27T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert result.exit_code == 0
    assert "resolver health" in result.output
    assert "supported source kind resolved" not in result.output
    assert "no supported source fixture found" in result.output
