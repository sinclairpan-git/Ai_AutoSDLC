"""Integration tests for adapter selection / activation CLI."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli import adapter_cmd
from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_config
from ai_sdlc.integrations.ide_adapter import IDEKind
from ai_sdlc.models.project import ActivationState, AdapterSupportTier, PreferredShell

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
    "AI_SDLC_ADAPTER_CANONICAL_SHA256",
    "AI_SDLC_ADAPTER_CANONICAL_PATH",
]


@pytest.fixture(autouse=True)
def _clear_ide_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in IDE_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def _digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


class TestCliAdapter:
    def test_adapter_help_surfaces_governance_language(self) -> None:
        result = runner.invoke(app, ["adapter", "--help"])

        assert result.exit_code == 0
        assert "Select, acknowledge, and inspect IDE adapters" not in result.output
        assert "ingress truth" in result.output
        assert "verification result" in result.output
        assert "compatibility/debug" in result.output

    def test_adapter_activate_help_describes_compatibility_acknowledgement(self) -> None:
        result = runner.invoke(app, ["adapter", "activate", "--help"])

        assert result.exit_code == 0
        assert "acknowledged by the user" not in result.output
        assert "compatibility/debug" in result.output
        assert "does" in result.output
        assert "ingress verification" in result.output

    def test_adapter_status_help_describes_ingress_and_verification_state(self) -> None:
        result = runner.invoke(app, ["adapter", "status", "--help"])

        assert result.exit_code == 0
        assert "ingress state" in result.output
        assert "verification result" in result.output

    def test_init_interactive_selector_persists_user_choice(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("ai_sdlc.cli.commands._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_agent_target",
            lambda _default: IDEKind.CLAUDE_CODE,
        )
        monkeypatch.setattr(
            "ai_sdlc.cli.commands.interactive_select_preferred_shell",
            lambda _default: PreferredShell.POWERSHELL,
        )

        result = runner.invoke(app, ["init", str(tmp_path)])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == IDEKind.CLAUDE_CODE.value
        assert (tmp_path / ".claude" / "CLAUDE.md").is_file()

    def test_init_with_explicit_agent_target_persists_target(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            ["init", str(tmp_path), "--agent-target", "codex"],
        )
        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.agent_target == "codex"
        assert cfg.adapter_ingress_state == "materialized"
        assert cfg.adapter_verification_result == "unverified"
        assert (tmp_path / "AGENTS.md").is_file()

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
        assert cfg.adapter_ingress_state == "materialized"
        assert cfg.adapter_verification_result == "unverified"

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
        assert (tmp_path / "AGENTS.md").is_file()

    def test_adapter_shell_select_with_explicit_shell_persists_and_rewrites_adapter_doc(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            ["adapter", "shell-select", "--shell", "powershell"],
        )

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell == PreferredShell.POWERSHELL.value
        text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "PowerShell" in text
        assert "Do not start with POSIX shell syntax" in text

    def test_adapter_shell_select_without_flag_uses_interactive_selector(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert runner.invoke(app, ["init", str(tmp_path)]).exit_code == 0
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("ai_sdlc.cli.adapter_cmd._is_interactive_terminal", lambda: True)
        monkeypatch.setattr(
            "ai_sdlc.cli.adapter_cmd.interactive_select_preferred_shell",
            lambda _default: PreferredShell.ZSH,
        )

        result = runner.invoke(app, ["adapter", "shell-select"])

        assert result.exit_code == 0
        cfg = load_project_config(tmp_path)
        assert cfg.preferred_shell == PreferredShell.ZSH.value

    def test_adapter_status_json_exposes_target_and_ingress_truth(
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
        assert payload["adapter_ingress_state"] == "materialized"
        assert payload["adapter_verification_result"] == "unverified"
        assert payload["adapter_canonical_path"] == "AGENTS.md"
        assert payload["adapter_canonical_content_digest"].startswith("sha256:")
        assert payload["adapter_canonical_consumption_result"] == "unverified"
        assert payload["adapter_canonical_consumption_evidence"] == ""
        assert payload["adapter_canonical_consumed_at"] == ""
        assert payload["adapter_degrade_reason"] == ""
        assert payload["preferred_shell"]
        assert payload["preferred_shell_configured"] is True
        assert payload["governance_activation_state"] == "materialized_unverified"
        assert payload["governance_activation_verifiable"] is False
        assert payload["governance_activation_mode"] == "materialized_only"
        assert "machine-verifiable evidence" in payload["governance_activation_detail"]

    def test_adapter_status_json_reports_shell_selection_migration_hint_for_legacy_project(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        cfg = load_project_config(tmp_path)
        cfg = cfg.model_copy(update={"preferred_shell": ""})
        from ai_sdlc.core.config import save_project_config

        save_project_config(tmp_path, cfg)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["adapter", "status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["preferred_shell"] == ""
        assert payload["preferred_shell_configured"] is False
        assert "adapter shell-select" in payload["preferred_shell_migration_hint"]

    def test_adapter_status_json_reports_verified_loaded_when_host_matches_target(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["adapter", "status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["adapter_ingress_state"] == "verified_loaded"
        assert payload["adapter_verification_result"] == "verified"
        assert payload["adapter_verification_evidence"] == "env:OPENAI_CODEX"
        assert payload["adapter_canonical_consumption_result"] == "unverified"
        assert payload["governance_activation_state"] == "verified_loaded"
        assert payload["governance_activation_verifiable"] is True
        assert payload["governance_activation_mode"] == "verified_loaded"

    def test_adapter_status_json_reports_verified_canonical_consumption_when_digest_matches(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        digest = _digest(tmp_path / "AGENTS.md")
        monkeypatch.setenv("AI_SDLC_ADAPTER_CANONICAL_SHA256", digest)
        monkeypatch.setenv("AI_SDLC_ADAPTER_CANONICAL_PATH", "AGENTS.md")
        monkeypatch.chdir(tmp_path)
        assert (
            runner.invoke(app, ["adapter", "select", "--agent-target", "codex"]).exit_code
            == 0
        )

        result = runner.invoke(app, ["adapter", "status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["adapter_ingress_state"] == "verified_loaded"
        assert payload["adapter_verification_result"] == "verified"
        assert payload["adapter_canonical_content_digest"] == digest
        assert payload["adapter_canonical_consumption_result"] == "verified"
        assert (
            payload["adapter_canonical_consumption_evidence"]
            == "env:AI_SDLC_ADAPTER_CANONICAL_SHA256"
        )
        assert payload["adapter_canonical_consumed_at"] != ""

    def test_adapter_status_json_keeps_acknowledgement_out_of_ingress_truth(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)
        assert (
            runner.invoke(app, ["adapter", "activate", "--agent-target", "codex"]).exit_code
            == 0
        )

        result = runner.invoke(app, ["adapter", "status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["adapter_activation_state"] == ActivationState.ACKNOWLEDGED.value
        assert (
            payload["adapter_support_tier"]
            == AdapterSupportTier.ACKNOWLEDGED_ACTIVATION.value
        )
        assert payload["adapter_ingress_state"] == "materialized"
        assert payload["adapter_verification_result"] == "unverified"
        assert payload["governance_activation_state"] == "materialized_unverified"
        assert payload["governance_activation_verifiable"] is False
        assert payload["governance_activation_mode"] == "materialized_only"
        assert "operator acknowledgement" in payload["governance_activation_detail"]

    def test_adapter_exec_requires_command_after_double_dash(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["adapter", "exec"])

        assert result.exit_code == 2
        assert "A command is required after '--'." in result.output

    def test_adapter_exec_injects_canonical_proof_for_child_command(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_CODEX", "1")
        assert (
            runner.invoke(app, ["init", str(tmp_path), "--agent-target", "codex"]).exit_code
            == 0
        )
        monkeypatch.chdir(tmp_path)

        plain = runner.invoke(app, ["adapter", "status", "--json"])
        assert plain.exit_code == 0
        plain_payload = json.loads(plain.output)
        assert plain_payload["adapter_canonical_consumption_result"] == "unverified"

        result = runner.invoke(
            app,
            [
                "adapter",
                "exec",
                "--",
                sys.executable,
                "-m",
                "ai_sdlc",
                "adapter",
                "status",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["adapter_ingress_state"] == "verified_loaded"
        assert payload["adapter_verification_result"] == "verified"
        assert payload["adapter_canonical_path"] == "AGENTS.md"
        assert payload["adapter_canonical_consumption_result"] == "verified"
        assert (
            payload["adapter_canonical_consumption_evidence"]
            == "env:AI_SDLC_ADAPTER_CANONICAL_SHA256"
        )

        after = runner.invoke(app, ["adapter", "status", "--json"])
        assert after.exit_code == 0
        after_payload = json.loads(after.output)
        assert after_payload["adapter_canonical_consumption_result"] == "unverified"

    def test_adapter_exec_times_out_stuck_child_command(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            timeout = kwargs.get("timeout")
            assert timeout == 120
            assert kwargs.get("encoding") == "utf-8"
            assert kwargs.get("errors") == "replace"
            raise subprocess.TimeoutExpired(
                cmd=args[0],
                timeout=timeout,
                output="partial stdout\n",
                stderr="partial stderr\n",
            )

        monkeypatch.setattr(adapter_cmd.subprocess, "run", fake_run)
        monkeypatch.setattr(adapter_cmd, "_require_project_root", lambda: Path.cwd())

        result = runner.invoke(
            app,
            [
                "adapter",
                "exec",
                "--",
                sys.executable,
                "-m",
                "ai_sdlc",
                "adapter",
                "select",
                "--agent-target",
                "codex",
            ],
        )

        assert result.exit_code == 124
        assert "partial stdout" in result.output
        assert "partial stderr" in result.output
        assert "timed out after 120 second(s)" in result.output
