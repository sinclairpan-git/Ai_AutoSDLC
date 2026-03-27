"""Integration tests for `ai-sdlc doctor`."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project
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
