"""Integration tests for self-update/update-advisor CLI."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


def _env(tmp_path, *, channel: str = "github-archive") -> dict[str, str]:
    return {
        "AI_SDLC_UPDATE_ADVISOR_TEST_INSTALLED": "1",
        "AI_SDLC_UPDATE_ADVISOR_TEST_VERSION": "0.7.0",
        "AI_SDLC_UPDATE_ADVISOR_TEST_CHANNEL": channel,
        "AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION": "v0.7.3",
        "AI_SDLC_UPDATE_ADVISOR_CACHE_DIR": str(tmp_path),
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }


def test_self_update_identity_json_exposes_machine_contract(tmp_path) -> None:
    result = runner.invoke(
        app,
        ["self-update", "identity", "--json"],
        env=_env(tmp_path),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["protocol_version"] == "1"
    assert payload["installed_runtime"] is True
    assert payload["binding_verified"] is True
    assert payload["installed_version"] == "0.7.0"
    assert payload["install_channel"] == "github-archive"


def test_self_update_evaluate_json_reports_actionable_github_archive(
    tmp_path,
) -> None:
    result = runner.invoke(
        app,
        ["self-update", "evaluate", "--json"],
        env=_env(tmp_path),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["refresh_result"] == "success"
    assert payload["upstream_latest_version"] == "0.7.3"
    assert payload["channel_latest_version"] == "0.7.3"
    assert "light_upstream_release_notice" in payload["eligible_notice_classes"]
    assert "actionable_cli_update_notice" in payload["eligible_notice_classes"]
    assert payload["upgrade_command"] == (
        "ai-sdlc self-update instructions --version 0.7.3"
    )


def test_self_update_evaluate_unknown_channel_stays_light_notice(tmp_path) -> None:
    result = runner.invoke(
        app,
        ["self-update", "evaluate", "--json"],
        env=_env(tmp_path, channel="unknown"),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["eligible_notice_classes"] == ["light_upstream_release_notice"]
    assert payload["channel_latest_version"] is None
    assert payload["upgrade_command"] is None


def test_interactive_cli_renders_update_notice_once(tmp_path) -> None:
    env = _env(tmp_path)
    env["AI_SDLC_UPDATE_ADVISOR_FORCE_TTY"] = "1"

    first = runner.invoke(app, ["status"], env=env)
    second = runner.invoke(app, ["status"], env=env)

    assert first.exit_code == 0
    assert "AI-SDLC Update Advisor" in first.output
    assert "ai-sdlc self-update instructions --version 0.7.3" in first.output
    assert second.exit_code == 0
    assert "AI-SDLC Update Advisor" not in second.output


def test_python_module_style_runtime_can_disable_update_notice(tmp_path) -> None:
    env = _env(tmp_path)
    env.pop("AI_SDLC_UPDATE_ADVISOR_TEST_INSTALLED")
    env["AI_SDLC_SOURCE_RUNTIME"] = "1"
    env["AI_SDLC_UPDATE_ADVISOR_FORCE_TTY"] = "1"

    result = runner.invoke(app, ["status"], env=env)

    assert result.exit_code == 0
    assert "AI-SDLC Update Advisor" not in result.output
