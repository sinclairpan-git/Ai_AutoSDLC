"""Integration tests for ai-sdlc init CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_config
from ai_sdlc.integrations.agent_target import PreferredShell

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
        assert "当前状态 / Current status" in result.output
        assert "接入真值尚未确认；先检查 adapter 状态" in result.output
        assert "Adapter ingress truth is not yet confirmed" in result.output
        assert "下一步命令 / Next command" in result.output
        assert "ai-sdlc adapter status" in result.output
        assert "命令作用 / What this command does" in result.output
        assert "安全预演" in result.output
        assert "safe startup rehearsal only" in result.output
        assert "ai-sdlc run --dry-run" in result.output
        assert "not verified host-ingress proof" in result.output
        assert "python -m ai_sdlc adapter status" in result.output
        assert "python -m ai_sdlc run --dry-run" in result.output
        assert "ai-sdlc adapter activate" not in result.output
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell != ""

    def test_init_already_initialized(self, initialized_project_dir: Path) -> None:
        result = runner.invoke(app, ["init", str(initialized_project_dir)])
        assert result.exit_code == 0
        assert "already initialized" in result.output
        assert "当前状态 / Current status" in result.output
        assert "下一步命令 / Next command" in result.output
        assert "ai-sdlc adapter status" in result.output
        assert "命令作用 / What this command does" in result.output
        assert "safe startup rehearsal only" in result.output
        assert "ai-sdlc run --dry-run" in result.output
        assert "not verified host-ingress proof" in result.output
        assert "python -m ai_sdlc adapter status" in result.output
        assert "python -m ai_sdlc run --dry-run" in result.output
        assert "ai-sdlc adapter activate" not in result.output

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
        rule = tmp_path / ".cursor" / "rules" / "ai-sdlc.mdc"
        assert rule.is_file()
        assert "cursor" in result.output.lower()

    def test_init_with_codex_marker_prefers_codex_target(self, tmp_path: Path) -> None:
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".codex").mkdir()
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "AGENTS.md").is_file()
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == "codex"
        assert cfg.preferred_shell != ""

    def test_init_generic_hint_without_ide_dirs(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        hint = tmp_path / ".ai-sdlc" / "memory" / "ide-adapter-hint.md"
        assert hint.is_file()

    def test_init_interactive_shell_selector_persists_user_choice(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ai_sdlc.cli.commands._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_agent_target",
            lambda _default: _default,
        )
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_preferred_shell",
            lambda _default: PreferredShell.POWERSHELL,
        )

        result = runner.invoke(app, ["init", str(tmp_path)])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell == PreferredShell.POWERSHELL.value
