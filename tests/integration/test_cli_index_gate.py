"""Integration tests for `ai-sdlc index` and gate alias contracts."""

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


class TestCliIndexAndGate:
    def test_index_rebuilds_base_and_extended_indexes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_app.py").write_text(
            "def test_ok():\n    assert True\n",
            encoding="utf-8",
        )

        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".ai-sdlc" / "project" / "generated" / "key-files.json").unlink(
            missing_ok=True
        )
        (tmp_path / ".ai-sdlc" / "state" / "repo-facts.json").unlink(missing_ok=True)

        result = runner.invoke(app, ["index"])

        assert result.exit_code == 0
        assert (tmp_path / ".ai-sdlc" / "state" / "repo-facts.json").exists()
        assert (
            tmp_path / ".ai-sdlc" / "project" / "generated" / "key-files.json"
        ).exists()

    def test_gate_alias_runs_without_check_subcommand(
        self, initialized_project_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(initialized_project_dir)

        result = runner.invoke(app, ["gate", "init"])

        assert result.exit_code == 0
        assert "Gate init" in result.output
