"""Unit tests for deterministic telemetry collectors."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.telemetry.collectors import DeterministicCollectors
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.runtime import RuntimeTelemetry


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _step_root(tmp_path: Path, trace) -> Path:
    return (
        telemetry_local_root(tmp_path)
        / "sessions"
        / trace.goal_session_id
        / "runs"
        / trace.workflow_run_id
        / "steps"
        / trace.step_id
    )


def test_collect_command_records_tool_fact_and_raw_output_evidence(tmp_path: Path) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    collectors = DeterministicCollectors(telemetry)

    trace = collectors.collect_command(
        command=("python", "-c", "print('ok')"),
        returncode=0,
        stdout="ok\n",
        stderr="",
    )

    step_root = _step_root(tmp_path, trace)
    events = _read_ndjson(step_root / "events.ndjson")
    evidence = _read_ndjson(step_root / "evidence.ndjson")

    assert any(
        payload["trace_layer"] == "tool" and payload["status"] == "succeeded"
        for payload in events
    )
    assert any(
        payload["locator"].startswith("ccp:v1:command_completed:event:")
        for payload in evidence
    )
    assert any(
        payload["locator"].startswith("trace://command/stdout-stderr/")
        for payload in evidence
    )


def test_collect_test_records_test_result_fact_without_governance_objects(
    tmp_path: Path,
) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    collectors = DeterministicCollectors(telemetry)

    trace = collectors.collect_test_result(
        command=("python", "-m", "pytest", "-q"),
        returncode=1,
        stdout="1 failed\n",
        stderr="",
    )

    step_root = _step_root(tmp_path, trace)
    events = _read_ndjson(step_root / "events.ndjson")
    evidence = _read_ndjson(step_root / "evidence.ndjson")

    assert any(
        payload["trace_layer"] == "tool" and payload["status"] == "failed"
        for payload in events
    )
    assert any(
        payload["locator"].startswith("ccp:v1:test_result_recorded:event:")
        for payload in evidence
    )
    assert not list(step_root.glob("evaluations/*.json"))
    assert not list(step_root.glob("violations/*.json"))
    assert not list(step_root.glob("artifacts/*.json"))


def test_collect_patch_records_patch_and_derived_file_write_facts(tmp_path: Path) -> None:
    telemetry = RuntimeTelemetry(tmp_path)
    collectors = DeterministicCollectors(telemetry)
    written_file = tmp_path / "src" / "demo.py"
    written_file.parent.mkdir(parents=True, exist_ok=True)
    written_file.write_text("print('demo')\n", encoding="utf-8")

    trace = collectors.collect_patch(
        command=("apply_patch", "demo.patch"),
        returncode=0,
        stdout="applied\n",
        stderr="",
        written_paths=(written_file,),
    )

    step_root = _step_root(tmp_path, trace)
    evidence = _read_ndjson(step_root / "evidence.ndjson")

    assert any(
        payload["locator"].startswith("ccp:v1:patch_applied:event:")
        for payload in evidence
    )
    assert any(
        payload["locator"].startswith("ccp:v1:file_written:event:")
        for payload in evidence
    )
    assert any(
        payload["locator"] == "trace://file-write/src/demo.py"
        for payload in evidence
    )

