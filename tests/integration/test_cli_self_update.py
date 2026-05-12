"""Integration tests for self-update/update-advisor CLI."""

from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

import ai_sdlc.cli.self_update_cmd as self_update_cmd
from ai_sdlc import __version__
from ai_sdlc.cli.main import app

runner = CliRunner()


def _env(tmp_path, *, channel: str = "github-archive") -> dict[str, str]:
    return {
        "AI_SDLC_UPDATE_ADVISOR_TEST_INSTALLED": "1",
        "AI_SDLC_UPDATE_ADVISOR_TEST_VERSION": "0.7.0",
        "AI_SDLC_UPDATE_ADVISOR_TEST_CHANNEL": channel,
        "AI_SDLC_UPDATE_ADVISOR_TEST_LATEST_VERSION": "v0.7.4",
        "AI_SDLC_UPDATE_ADVISOR_CACHE_DIR": str(tmp_path),
        "PYTHONUTF8": "1",
        "PYTHONIOENCODING": "utf-8",
    }


def test_global_version_option_prints_installed_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == __version__


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


def test_self_update_commands_do_not_trigger_project_adapter_hook(tmp_path) -> None:
    with runner.isolated_filesystem():
        Path(".ai-sdlc").mkdir()
        Path(".cursor/rules").mkdir(parents=True)
        result = runner.invoke(
            app,
            ["self-update", "identity", "--json"],
            env=_env(tmp_path),
        )

        assert result.exit_code == 0
        assert "IDE adapter" not in result.output
        assert not Path(".cursor/rules/ai-sdlc.mdc").exists()


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
    assert payload["upstream_latest_version"] == "0.7.4"
    assert payload["channel_latest_version"] == "0.7.4"
    assert "light_upstream_release_notice" in payload["eligible_notice_classes"]
    assert "actionable_cli_update_notice" in payload["eligible_notice_classes"]
    assert payload["upgrade_command"] == "ai-sdlc self-update check"


def test_self_update_evaluate_unknown_installed_channel_is_actionable(tmp_path) -> None:
    result = runner.invoke(
        app,
        ["self-update", "evaluate", "--json"],
        env=_env(tmp_path, channel="unknown"),
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "light_upstream_release_notice" in payload["eligible_notice_classes"]
    assert "actionable_cli_update_notice" in payload["eligible_notice_classes"]
    assert payload["channel_latest_version"] == "0.7.4"
    assert payload["upgrade_command"] == "ai-sdlc self-update check"


def test_self_update_check_auto_installs_actionable_update(
    tmp_path, monkeypatch
) -> None:
    calls: list[str] = []

    def fake_install(*, version: str) -> None:
        calls.append(version)

    monkeypatch.setattr(self_update_cmd, "self_update_install", fake_install)

    result = runner.invoke(
        app,
        ["self-update", "check"],
        env=_env(tmp_path, channel="unknown"),
    )

    assert result.exit_code == 0
    assert calls == ["0.7.4"]
    assert "现在自动更新" in result.output
    assert "Updating now" in result.output
    assert "无需复制下一条命令" in result.output
    assert "ai-sdlc self-update install --version" not in result.output


def test_self_update_check_reports_retry_and_offline_rescue_on_refresh_failure(
    tmp_path, monkeypatch
) -> None:
    from ai_sdlc.core.update_advisor import (
        REFRESH_NETWORK_ERROR,
        RuntimeIdentity,
        UpdateEvaluation,
    )

    seen: dict[str, object] = {}

    def fake_evaluate(**kwargs):
        seen.update(kwargs)
        return UpdateEvaluation(
            runtime_identity=RuntimeIdentity(
                installed_runtime=True,
                binding_verified=True,
                runtime_identity="sha256:test",
                installed_version="0.7.7",
                install_channel="github-archive",
                executable_path="ai-sdlc",
                distribution_path=str(tmp_path),
                reason_code="installed_runtime",
            ),
            freshness="expired",
            refresh_attempted=True,
            refresh_result=REFRESH_NETWORK_ERROR,
            last_success_checked_at=None,
            failure_backoff_until=None,
            upstream_latest_version=None,
            channel_latest_version=None,
            release_url=None,
            eligible_notice_classes=(),
            reason_code="network_error",
            upgrade_command=None,
        )

    monkeypatch.setattr(self_update_cmd, "evaluate_update_advisor", fake_evaluate)

    result = runner.invoke(app, ["self-update", "check"], env=_env(tmp_path))

    assert result.exit_code == 1
    assert seen["ignore_failure_backoff"] is True
    assert seen["timeout_seconds"] == 20.0
    assert "当前安装尚未变化" in result.output
    assert "ai-sdlc self-update check" in result.output
    assert "./install_offline.sh --upgrade-existing" in result.output
    assert "install_offline.ps1 -UpgradeExisting" in result.output


def test_interactive_cli_renders_update_notice_once(tmp_path) -> None:
    env = _env(tmp_path)
    env["AI_SDLC_UPDATE_ADVISOR_FORCE_TTY"] = "1"

    first = runner.invoke(app, ["status"], env=env)
    second = runner.invoke(app, ["status"], env=env)

    assert first.exit_code == 0
    assert "AI-SDLC Update Advisor" in first.output
    assert "自动下载、安装并校验版本" in first.output
    assert "ai-sdlc self-update check" in first.output
    assert second.exit_code == 0
    assert "AI-SDLC Update Advisor" not in second.output


def test_self_update_install_completes_without_manual_followup(monkeypatch, tmp_path) -> None:
    calls: list[tuple[str, object]] = []

    def fake_download(asset_url, archive_path):
        calls.append(("download", asset_url))
        archive_path.write_text("archive", encoding="utf-8")

    def fake_extract(archive_path, extract_root, hint):
        calls.append(("extract", hint["filename"]))
        bundle = extract_root / "bundle"
        wheels = bundle / "wheels"
        wheels.mkdir(parents=True)
        (wheels / "ai_sdlc-0.7.4-py3-none-any.whl").write_text(
            "wheel", encoding="utf-8"
        )
        return bundle

    def fake_install(bundle_dir, release_version):
        calls.append(("install", f"{bundle_dir.name}:{release_version}"))

    monkeypatch.setattr(self_update_cmd, "_download_asset", fake_download)
    monkeypatch.setattr(self_update_cmd, "_extract_release_asset", fake_extract)
    monkeypatch.setattr(
        self_update_cmd, "_install_bundle_into_current_runtime", fake_install
    )
    monkeypatch.setattr(self_update_cmd, "_read_installed_version", lambda: "0.7.4")

    result = runner.invoke(
        app,
        ["self-update", "install", "--version", "0.7.4"],
        env=_env(tmp_path),
    )

    assert result.exit_code == 0
    assert [call[0] for call in calls] == ["download", "extract", "install"]
    assert "更新完成" in result.output
    assert "Update completed" in result.output
    assert "不需要继续执行升级命令" in result.output
    assert "执行下面整段命令" not in result.output
    assert "curl -L" not in result.output
    assert "install_offline" not in result.output


def test_self_update_installs_wheel_matching_requested_version(
    tmp_path, monkeypatch
) -> None:
    bundle = tmp_path / "bundle"
    wheels = bundle / "wheels"
    wheels.mkdir(parents=True)
    (wheels / "ai_sdlc-0.7.9-py3-none-any.whl").write_text("old", encoding="utf-8")
    target = wheels / "ai_sdlc-0.7.12-py3-none-any.whl"
    target.write_text("new", encoding="utf-8")

    commands: list[list[str]] = []

    def fake_run(command, **_kwargs):
        commands.append(command)

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(self_update_cmd.subprocess, "run", fake_run)

    self_update_cmd._install_bundle_into_current_runtime(bundle, "0.7.12")

    assert commands
    assert commands[0][-1] == str(target)


def test_self_update_reexecs_windows_launcher_only_once() -> None:
    assert self_update_cmd._should_reexec_windows_launcher(
        platform_name="win32",
        argv0=r"C:\venv\Scripts\ai-sdlc.exe",
        env={},
    )
    assert not self_update_cmd._should_reexec_windows_launcher(
        platform_name="win32",
        argv0=r"C:\venv\Scripts\ai-sdlc.exe",
        env={"AI_SDLC_SELF_UPDATE_REEXEC": "1"},
    )
    assert not self_update_cmd._should_reexec_windows_launcher(
        platform_name="win32",
        argv0=r"C:\Python311\python.exe",
        env={},
    )
    assert not self_update_cmd._should_reexec_windows_launcher(
        platform_name="darwin",
        argv0="/venv/bin/ai-sdlc",
        env={},
    )


def test_self_update_rejects_tar_link_members(tmp_path) -> None:
    archive_path = tmp_path / "bundle.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        root = tarfile.TarInfo("ai-sdlc-offline-0.7.4-macos-arm64")
        root.type = tarfile.DIRTYPE
        archive.addfile(root)

        link = tarfile.TarInfo("ai-sdlc-offline-0.7.4-macos-arm64/link")
        link.type = tarfile.SYMTYPE
        link.linkname = "/tmp"
        archive.addfile(link)

        payload = b"payload"
        member = tarfile.TarInfo("ai-sdlc-offline-0.7.4-macos-arm64/link/payload")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    with pytest.raises(self_update_cmd.SelfUpdateError, match="link member"):
        self_update_cmd._extract_release_asset(
            archive_path,
            tmp_path / "extract",
            {
                "archive": "tar.gz",
                "filename": "ai-sdlc-offline-0.7.4-macos-arm64.tar.gz",
            },
        )


def test_self_update_instructions_are_user_result_oriented(tmp_path) -> None:
    result = runner.invoke(
        app,
        ["self-update", "instructions", "--version", "0.7.4"],
        env=_env(tmp_path),
    )

    assert result.exit_code == 0
    assert "当前结果 / Result" in result.output
    assert "当前安装尚未变化" in result.output
    assert "下一步 / Next" in result.output
    assert "ai-sdlc self-update check" in result.output
    assert "自动检查最新" in result.output
    assert "curl -L" not in result.output
    assert "install_offline" not in result.output
    assert "does not silently modify your install" not in result.output
    assert "不会静默改写你的安装环境" not in result.output


def test_python_module_style_runtime_can_disable_update_notice(tmp_path) -> None:
    env = _env(tmp_path)
    env.pop("AI_SDLC_UPDATE_ADVISOR_TEST_INSTALLED")
    env["AI_SDLC_SOURCE_RUNTIME"] = "1"
    env["AI_SDLC_UPDATE_ADVISOR_FORCE_TTY"] = "1"

    result = runner.invoke(app, ["status"], env=env)

    assert result.exit_code == 0
    assert "AI-SDLC Update Advisor" not in result.output
