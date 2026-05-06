"""Integration tests for ai-sdlc init CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli import commands
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
        assert "当前结果 / Result" in result.output
        assert "初始化完成" in result.output
        assert "Initialization complete" in result.output
        assert "安全预演已自动执行" in result.output
        assert "Safe rehearsal ran automatically" in result.output
        assert "不用再手动执行初始化命令" in result.output
        assert "No more setup commands are needed" in result.output
        assert "ai-sdlc adapter status" not in result.output
        assert "python -m ai_sdlc adapter status" not in result.output
        assert "python -m ai_sdlc run --dry-run" not in result.output
        assert "ai-sdlc adapter activate" not in result.output
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell != ""

    def test_init_fails_when_automatic_dry_run_crashes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def crash_dry_run(*_args: object, **_kwargs: object) -> None:
            raise RuntimeError("runtime exploded")

        monkeypatch.setattr(commands.SDLCRunner, "run", crash_dry_run)

        result = runner.invoke(app, ["init", str(tmp_path)])

        assert result.exit_code == 1
        assert "初始化未完成" in result.output
        assert "Initialization is not complete" in result.output
        assert "ai-sdlc doctor" in result.output
        assert "runtime exploded" in result.output
        assert "初始化完成" not in result.output
        assert "Initialization complete" not in result.output

    def test_init_already_initialized(self, initialized_project_dir: Path) -> None:
        result = runner.invoke(app, ["init", str(initialized_project_dir)])
        assert result.exit_code == 0
        assert "already initialized" in result.output
        assert "当前结果 / Result" in result.output
        assert "初始化完成" in result.output
        assert "Initialization complete" in result.output
        assert "不用再手动执行初始化命令" in result.output
        assert "No more setup commands are needed" in result.output
        assert "ai-sdlc adapter status" not in result.output
        assert "python -m ai_sdlc adapter status" not in result.output
        assert "python -m ai_sdlc run --dry-run" not in result.output
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

    def test_init_live_codex_env_wins_over_stale_cursor_marker(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (tmp_path / ".cursor").mkdir()
        monkeypatch.setenv("OPENAI_CODEX", "1")

        result = runner.invoke(app, ["init", str(tmp_path)])

        assert result.exit_code == 0
        assert (tmp_path / "AGENTS.md").is_file()
        cfg = load_project_config(tmp_path)
        assert cfg.detected_ide == "codex"
        assert cfg.agent_target == "codex"
        assert cfg.adapter_ingress_state == "verified_loaded"
        assert cfg.adapter_verification_result == "verified"

    def test_init_with_codex_marker_prefers_codex_target(self, tmp_path: Path) -> None:
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".codex").mkdir()
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "AGENTS.md").is_file()
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == "codex"
        assert cfg.preferred_shell != ""

    def test_init_with_explicit_shell_persists_shell_and_first_adapter_render(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        (tmp_path / ".codex").mkdir()
        monkeypatch.setattr("ai_sdlc.cli.commands._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_agent_target",
            lambda _default: _default,
        )

        result = runner.invoke(app, ["init", str(tmp_path), "--shell", "powershell"])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell == PreferredShell.POWERSHELL.value
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "Project preferred shell is not configured yet" not in text
        assert "Project preferred shell: PowerShell." in text

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

    def test_init_explicit_shell_skips_interactive_shell_selector(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ai_sdlc.cli.commands._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_agent_target",
            lambda _default: _default,
        )
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_preferred_shell",
            lambda _default: (_ for _ in ()).throw(AssertionError("selector should not run")),
        )

        result = runner.invoke(app, ["init", str(tmp_path), "--shell", "zsh"])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell == PreferredShell.ZSH.value
