"""Integration tests for adapter selection / activation CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_config
from ai_sdlc.integrations.ide_adapter import IDEKind
from ai_sdlc.models.project import ActivationState, AdapterSupportTier

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


class TestCliAdapter:
    def test_init_interactive_selector_persists_user_choice(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ai_sdlc.cli.commands._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_agent_target",
            lambda _default: IDEKind.CLAUDE_CODE,
        )

        result = runner.invoke(app, ["init", str(tmp_path)])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == IDEKind.CLAUDE_CODE.value
        assert (tmp_path / ".claude" / "AI-SDLC.md").is_file()

    def test_init_with_explicit_agent_target_persists_target(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            ["init", str(tmp_path), "--agent-target", "codex"],
        )
        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == "codex"
        assert cfg.adapter_activation_state == ActivationState.INSTALLED.value
        assert (tmp_path / ".codex" / "AI-SDLC.md").is_file()

    def test_adapter_activate_marks_project_acknowledged(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            ["adapter", "activate", "--agent-target", "codex"],
        )

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == "codex"
        assert cfg.adapter_activation_state == ActivationState.ACKNOWLEDGED.value
        assert (
            cfg.adapter_support_tier
            == AdapterSupportTier.ACKNOWLEDGED_ACTIVATION.value
        )
        assert cfg.adapter_activation_source == "operator_cli"
        assert cfg.adapter_activation_evidence == "ai-sdlc adapter activate"
        assert cfg.adapter_activated_at != ""

    def test_adapter_select_without_flag_uses_interactive_selector(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert runner.invoke(app, ["init", str(tmp_path)]).exit_code == 0
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ai_sdlc.cli.adapter_cmd._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.adapter_cmd.interactive_select_agent_target",
            lambda _default: IDEKind.CODEX,
        )

        result = runner.invoke(app, ["adapter", "select"])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == IDEKind.CODEX.value
        assert (tmp_path / ".codex" / "AI-SDLC.md").is_file()

    def test_adapter_status_json_exposes_target_and_activation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["adapter", "status", "--json"])
        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["agent_target"] == "codex"
        assert payload["adapter_activation_state"] == ActivationState.INSTALLED.value
        assert payload["adapter_support_tier"] == AdapterSupportTier.SOFT_INSTALLED.value
        assert payload["adapter_activation_source"] == ""
        assert payload["adapter_activation_evidence"] == ""
