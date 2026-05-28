"""AgentOps reporter CLI integration tests."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.agentops_bridge import persist_agentops_outbox_batch

runner = CliRunner()


def _init_project(root: Path) -> None:
    (root / ".ai-sdlc" / "project" / "config").mkdir(parents=True, exist_ok=True)


def test_agentops_doctor_json_reports_ready_without_token_value(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["agentops", "doctor", "--json"],
        env={
            "AGENTOPS_INGESTION_ENDPOINT": "https://gateway.example",
            "AGENTOPS_INGESTION_TOKEN": "secret-token",
        },
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ready"] is True
    assert payload["config"]["token_present"] is True
    assert "secret-token" not in result.stdout


def test_agentops_doctor_json_fails_closed_when_gateway_token_missing(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["agentops", "doctor", "--json"],
        env={
            "AGENTOPS_INGESTION_ENDPOINT": "https://gateway.example",
            "AGENTOPS_INGESTION_TOKEN": "",
        },
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ready"] is False
    assert payload["checks"][0]["reason_code"] == "missing_token"
    assert "Bearer" not in result.stdout


def test_agentops_status_json_reports_latest_local_artifacts(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    persist_agentops_outbox_batch(
        tmp_path,
        {
            "schema_version": "runtime.ingestion.v1",
            "batch_id": "batch_status_cli",
            "outbox_id": "outbox_status_cli",
            "producer": "Ai_AutoSDLC",
            "events": [],
        },
    )

    result = runner.invoke(
        app,
        ["agentops", "status", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["latest_outbox"]["payload"]["outbox_id"] == "outbox_status_cli"
    assert payload["latest_receipt"] is None
    assert payload["latest_diagnostic"] is None


def test_agentops_retry_dry_run_validates_persisted_outbox_without_network(
    monkeypatch,
    tmp_path: Path,
) -> None:
    _init_project(tmp_path)
    monkeypatch.chdir(tmp_path)
    persist_agentops_outbox_batch(
        tmp_path,
        {
            "schema_version": "runtime.ingestion.v1",
            "batch_id": "batch_retry_cli",
            "outbox_id": "outbox_retry_cli",
            "producer": "Ai_AutoSDLC",
            "events": [],
        },
    )

    result = runner.invoke(
        app,
        [
            "agentops",
            "retry",
            "--outbox-id",
            "outbox_retry_cli",
            "--dry-run",
            "--json",
        ],
        env={
            "AGENTOPS_INGESTION_ENDPOINT": "https://gateway.example",
            "AGENTOPS_INGESTION_TOKEN": "secret-token",
        },
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["dry_run"] is True
    assert payload["config_ready"] is True
    assert payload["receipt_path"] == ""
    assert payload["diagnostic_path"] == ""
    assert "secret-token" not in result.stdout


def test_enterprise_configure_writes_profile_without_token_value(
    monkeypatch,
    tmp_path: Path,
) -> None:
    profile = tmp_path / "enterprise.yaml"
    monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile))

    result = runner.invoke(
        app,
        [
            "enterprise",
            "configure",
            "--endpoint",
            "https://ops.example",
            "--enterprise-id",
            "dept",
            "--token-env",
            "DEPT_AGENTOPS_TOKEN",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["profile_path"] == str(profile)
    assert payload["reporting_mode"] == "required"
    assert payload["token_written"] is False
    content = profile.read_text(encoding="utf-8")
    assert "agentops_reporting_mode: required" in content
    assert "agentops_ingestion_endpoint: https://ops.example" in content
    assert "secret" not in content.lower()


def test_enterprise_configure_allows_off_profile_without_endpoint(
    monkeypatch,
    tmp_path: Path,
) -> None:
    profile = tmp_path / "enterprise-off.yaml"
    monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile))

    result = runner.invoke(
        app,
        [
            "enterprise",
            "configure",
            "--reporting-mode",
            "off",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["profile_path"] == str(profile)
    assert payload["reporting_mode"] == "off"
    content = profile.read_text(encoding="utf-8")
    assert "agentops_reporting_mode: 'off'" in content or "agentops_reporting_mode: off" in content
    assert "agentops_ingestion_endpoint: ''" in content


def test_enterprise_configure_rejects_unsupported_ingestion_mode(
    monkeypatch,
    tmp_path: Path,
) -> None:
    profile = tmp_path / "enterprise.yaml"
    monkeypatch.setenv("AI_SDLC_ENTERPRISE_PROFILE", str(profile))

    result = runner.invoke(
        app,
        [
            "enterprise",
            "configure",
            "--endpoint",
            "https://ops.example",
            "--ingestion-mode",
            "gateawy",
            "--json",
        ],
    )

    assert result.exit_code != 0
    assert "ingestion-mode must be gateway or direct_local" in result.output
    assert not profile.exists()
