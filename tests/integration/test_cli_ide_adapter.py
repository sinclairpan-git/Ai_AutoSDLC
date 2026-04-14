"""Integration: IDE adapter runs on init and on subsequent commands."""

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


class TestCliIdeAdapterHook:
    def test_status_installs_vscode_file_after_marker_added(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".vscode").mkdir()
        assert runner.invoke(app, ["status"]).exit_code == 0
        vs = tmp_path / ".github" / "copilot-instructions.md"
        assert vs.is_file()

    def test_status_json_does_not_install_vscode_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".vscode").mkdir()

        result = runner.invoke(app, ["status", "--json"])

        assert result.exit_code == 0
        vs = tmp_path / ".github" / "copilot-instructions.md"
        assert vs.exists() is False
