"""Adversarial beginner-path tests for the default CLI UX."""

from __future__ import annotations

import sys
from pathlib import Path

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()
_REPO_ROOT = Path(__file__).resolve().parents[2]

_BEGINNER_COMMANDS = {
    "adopt",
    "init",
    "recover",
    "run",
    "self-update",
    "status",
}
_ADVANCED_COMMANDS = {
    "adapter",
    "agentops",
    "doctor",
    "enterprise",
    "gate",
    "handoff",
    "host-runtime",
    "index",
    "loop",
    "pr-review",
    "program",
    "provenance",
    "refresh",
    "rules",
    "scan",
    "stage",
    "studio",
    "telemetry",
    "trace",
    "verify",
    "workitem",
}


def _single_space(text: str) -> str:
    return " ".join(text.split())


def test_root_help_only_exposes_six_beginner_commands() -> None:
    import typer.main

    root = typer.main.get_command(app)
    visible = {
        name for name, command in root.commands.items() if not command.hidden
    }
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert visible == _BEGINNER_COMMANDS
    assert set(root.commands) == _BEGINNER_COMMANDS | _ADVANCED_COMMANDS
    assert (
        "Common commands are shown here; advanced commands remain directly callable."
        in _single_space(result.output)
    )


def test_advanced_command_help_remains_directly_callable(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    for command in sorted(_ADVANCED_COMMANDS):
        monkeypatch.setattr(sys, "argv", ["ai-sdlc", command, "--help"])
        result = runner.invoke(app, [command, "--help"])
        assert result.exit_code == 0, f"{command}: {result.output}"


def test_readme_indexes_every_command_hidden_from_root_help() -> None:
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    _, advanced_section = readme.split("### Advanced Command Index", maxsplit=1)
    advanced_section, _ = advanced_section.split("### Requirement Loop", maxsplit=1)

    for command in _ADVANCED_COMMANDS:
        assert f"`ai-sdlc {command}`" in advanced_section


def test_user_guide_distinguishes_compact_and_detailed_status() -> None:
    guide = (_REPO_ROOT / "USER_GUIDE.zh-CN.md").read_text(encoding="utf-8")

    assert "`ai-sdlc status` | 紧凑查看 Current Loop、Result、Next 和 Blockers" in guide
    assert "`ai-sdlc status --details` | 查看完整项目、阶段、治理和交接诊断面" in guide


def test_vibe_coder_can_initialize_without_reading_internal_state(
    tmp_path: Path,
) -> None:
    """A non-technical user should finish setup from the init output alone."""

    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--agent-target", "codex", "--shell", "zsh"],
    )

    assert result.exit_code == 0
    assert (tmp_path / ".ai-sdlc").is_dir()
    assert (tmp_path / "AGENTS.md").is_file()
    assert "当前结果 / Result" in result.output
    assert "初始化完成" in result.output
    assert "Initialization complete" in result.output
    assert "不用再手动执行初始化命令" in result.output
    assert "No more CLI setup commands are needed" in result.output
    assert "请先读取 AGENTS.md" in result.output
    assert "在 AI 对话里先发送上面这句话" in result.output
    plain = _single_space(result.output)
    assert "send the line above in the AI chat" in plain
    assert "then describe the requirement directly" in plain

    assert "ai-sdlc adapter status" not in result.output
    assert "ai-sdlc host-runtime plan" not in result.output
    assert "python -m ai_sdlc" not in result.output
    assert "verified_loaded" not in result.output
    assert "governance_activation" not in result.output


def test_adapter_status_default_is_beginner_safe_but_json_keeps_truth(
    tmp_path: Path,
    monkeypatch,
) -> None:
    assert (
        runner.invoke(
            app,
            ["init", str(tmp_path), "--agent-target", "codex", "--shell", "zsh"],
        ).exit_code
        == 0
    )

    monkeypatch.chdir(tmp_path)

    status = runner.invoke(app, ["adapter", "status"])

    assert status.exit_code == 0
    assert "当前结果 / Result" in status.output
    assert "下一步 / Next" in status.output
    assert "ai-sdlc run --dry-run" not in status.output
    assert "请先读取 AGENTS.md" in status.output
    assert "直接输入需求" in status.output
    assert "governance_activation" not in status.output
    assert "adapter_canonical_content_digest" not in status.output
    assert "materialized" not in status.output
    assert "unverified" not in status.output
    assert "ingress" not in status.output.lower()

    machine = runner.invoke(app, ["adapter", "status", "--json"])

    assert machine.exit_code == 0
    assert "governance_activation_state" in machine.output
    assert "adapter_canonical_content_digest" in machine.output


def test_run_dry_run_materialized_adapter_explains_upgrade_is_not_failed(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Upgrade users should not have to decode adapter ingress internals."""

    assert (
        runner.invoke(
            app,
            ["init", str(tmp_path), "--agent-target", "codex", "--shell", "zsh"],
        ).exit_code
        == 0
    )

    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["run", "--dry-run"])

    assert result.exit_code == 0
    assert "当前结果 / Result" in result.output
    assert "安全预演已完成" in result.output
    assert "adapter ingress truth not yet verified" not in result.output
    assert "Current ingress truth is not yet verified" not in result.output
    assert "ai-sdlc host-runtime plan" not in result.output
    assert "governance_activation" not in result.output
    assert "materialized_unverified" not in result.output
    assert "materialized" not in result.output
    assert "unverified" not in result.output
    assert "ingress" not in result.output.lower()


def test_adapter_status_generic_recovery_does_not_reselect_generic(
    tmp_path: Path,
    monkeypatch,
) -> None:
    assert (
        runner.invoke(app, ["init", str(tmp_path), "--agent-target", "generic"]).exit_code
        == 0
    )

    monkeypatch.chdir(tmp_path)

    status = runner.invoke(app, ["adapter", "status"])

    assert status.exit_code == 0
    assert "ai-sdlc adapter select" in status.output
    assert "--agent-target generic" not in status.output
