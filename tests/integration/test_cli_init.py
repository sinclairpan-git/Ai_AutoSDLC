"""Integration tests for ai-sdlc init CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_config

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


class TestCliInit:
    def test_init_empty_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / ".ai-sdlc").is_dir()
        assert "Initialized" in result.output
        assert "adapter activate" in result.output
        assert "ai-sdlc run --dry-run" in result.output
        assert "python -m ai_sdlc run --dry-run" in result.output

    def test_init_already_initialized(self, initialized_project_dir: Path) -> None:
        result = runner.invoke(app, ["init", str(initialized_project_dir)])
        assert result.exit_code == 0
        assert "already initialized" in result.output
        assert "adapter activate" in result.output
        assert "ai-sdlc run --dry-run" in result.output
        assert "python -m ai_sdlc run --dry-run" in result.output

    def test_init_nonexistent_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path / "nope")])
        assert result.exit_code == 2

    def test_init_default_project_name(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert tmp_path.name in result.output

    def test_init_with_cursor_dir_installs_rule(self, tmp_path: Path) -> None:
        (tmp_path / ".cursor").mkdir()
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        rule = tmp_path / ".cursor" / "rules" / "ai-sdlc.md"
        assert rule.is_file()
        assert "cursor" in result.output.lower()

    def test_init_with_codex_marker_prefers_codex_target(self, tmp_path: Path) -> None:
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".codex").mkdir()
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / ".codex" / "AI-SDLC.md").is_file()
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == "codex"

    def test_init_generic_hint_without_ide_dirs(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        hint = tmp_path / ".ai-sdlc" / "memory" / "ide-adapter-hint.md"
        assert hint.is_file()
