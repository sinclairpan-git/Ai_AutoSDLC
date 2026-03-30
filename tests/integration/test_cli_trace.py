"""Integration tests for `ai-sdlc trace` wrappers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry.paths import telemetry_local_root, telemetry_manifest_path

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _single_step_root(root: Path) -> Path:
    manifest = json.loads(telemetry_manifest_path(root).read_text(encoding="utf-8"))
    assert len(manifest["sessions"]) == 1
    assert len(manifest["runs"]) == 1
    assert len(manifest["steps"]) == 1
    session_id = next(iter(manifest["sessions"]))
    run_id = next(iter(manifest["runs"]))
    step_id = next(iter(manifest["steps"]))
    return (
        telemetry_local_root(root)
        / "sessions"
        / session_id
        / "runs"
        / run_id
        / "steps"
        / step_id
    )


class TestCliTrace:
    def test_trace_exec_runs_command_and_records_contextual_facts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            ["trace", "exec", "--", sys.executable, "-c", "print('trace-ok')"],
        )

        assert result.exit_code == 0
        step_root = _single_step_root(tmp_path)
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

    def test_trace_test_records_test_result_fact(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            ["trace", "test", "--", sys.executable, "-c", "print('tests-pass')"],
        )

        assert result.exit_code == 0
        step_root = _single_step_root(tmp_path)
        evidence = _read_ndjson(step_root / "evidence.ndjson")
        assert any(
            payload["locator"].startswith("ccp:v1:test_result_recorded:event:")
            for payload in evidence
        )

    def test_trace_patch_records_patch_and_file_write_facts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "trace",
                "patch",
                "--file",
                "src/demo.py",
                "--",
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "Path('src').mkdir(exist_ok=True); "
                    "Path('src/demo.py').write_text(\"print('demo')\\n\", encoding='utf-8')"
                ),
            ],
        )

        assert result.exit_code == 0
        step_root = _single_step_root(tmp_path)
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
