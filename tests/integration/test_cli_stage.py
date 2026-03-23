"""Integration tests for ai-sdlc stage CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()

IDE_ENV_KEYS = [
    "CURSOR_TRACE_ID",
    "CURSOR_AGENT",
    "VSCODE_IPC_HOOK_CLI",
    "TERM_PROGRAM",
    "OPENAI_CODEX",
    "CODEX_CLI_READY",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDECODE",
]


@pytest.fixture(autouse=True)
def _clear_ide_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in IDE_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


class TestStageCommand:
    def test_stage_help(self) -> None:
        result = runner.invoke(app, ["stage", "--help"])
        assert result.exit_code == 0
        assert "show" in result.output
        assert "run" in result.output
        assert "status" in result.output

    def test_stage_show_outside_project(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["stage", "show", "init"])
        assert result.exit_code == 1

    def test_stage_show_init_inside_project(
        self, initialized_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(initialized_project_dir)
        result = runner.invoke(app, ["stage", "show", "init"])
        assert result.exit_code == 0
        assert "init" in result.output
        assert "命令清单" in result.output or "steps" in result.output.lower()

    def test_stage_status_inside_project(
        self, initialized_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(initialized_project_dir)
        result = runner.invoke(app, ["stage", "status"])
        assert result.exit_code == 0
        assert "init" in result.output

    def test_stage_run_dry_run(
        self, initialized_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(initialized_project_dir)
        result = runner.invoke(app, ["stage", "run", "init", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry-run" in result.output or "dry" in result.output.lower()

    def test_stage_show_triggers_ide_adapter_after_claude_marker(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".claude").mkdir()
        assert runner.invoke(app, ["stage", "show", "init"]).exit_code == 0
        doc = tmp_path / ".claude" / "AI-SDLC.md"
        assert doc.is_file()
