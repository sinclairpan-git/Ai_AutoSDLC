"""Adversarial beginner-path tests for the default CLI UX."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


def _single_space(text: str) -> str:
    return " ".join(text.split())


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
    assert "No more setup commands are needed" in result.output
    assert "切换到 Codex/AI 对话中输入你的需求" in result.output
    plain = _single_space(result.output)
    assert "switch to Codex/AI chat and describe" in plain
    assert "your requirement" in plain

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
    assert "ai-sdlc run --dry-run" in status.output
    assert "governance_activation" not in status.output
    assert "adapter_canonical_content_digest" not in status.output

    machine = runner.invoke(app, ["adapter", "status", "--json"])

    assert machine.exit_code == 0
    assert "governance_activation_state" in machine.output
    assert "adapter_canonical_content_digest" in machine.output
