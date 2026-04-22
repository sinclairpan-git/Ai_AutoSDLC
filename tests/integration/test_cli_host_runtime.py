"""Integration tests for ai-sdlc host-runtime CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.host_runtime_manager import HostRuntimeProbe, build_host_runtime_plan

runner = CliRunner()


def test_host_runtime_plan_json_reports_blocked_status(
    initialized_project_dir: Path,
) -> None:
    blocked = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="linux",
            platform_arch="x86_64",
            python_version="3.11.9",
            surface_kind="uv_run",
            surface_binding_state="unbound",
            installed_runtime_status="missing",
        )
    )

    with patch(
        "ai_sdlc.cli.host_runtime_cmd.find_project_root",
        return_value=initialized_project_dir,
    ), patch(
        "ai_sdlc.cli.host_runtime_cmd.evaluate_current_host_runtime",
        return_value=blocked,
    ):
        result = runner.invoke(app, ["host-runtime", "plan", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "bootstrap_required"
    assert payload["reason_codes"] == ["surface_binding_unbound"]
    assert payload["bootstrap_acquisition"]["handoff_kind"] == "installed_runtime_binding_required"


def test_host_runtime_plan_text_reports_ready_status(
    initialized_project_dir: Path,
) -> None:
    ready = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            node_runtime_available=True,
            package_manager_available=True,
            playwright_browsers_available=True,
        )
    )

    with patch(
        "ai_sdlc.cli.host_runtime_cmd.find_project_root",
        return_value=initialized_project_dir,
    ), patch(
        "ai_sdlc.cli.host_runtime_cmd.evaluate_current_host_runtime",
        return_value=ready,
    ):
        result = runner.invoke(app, ["host-runtime", "plan"])

    assert result.exit_code == 0
    assert "Host Runtime Plan" in result.output
    assert "status: ready" in result.output
    assert "surface: installed_cli / bound" in result.output
    assert "当前状态 / Current status" in result.output
    assert "宿主运行时已就绪" in result.output
    assert "Host runtime is ready" in result.output
    assert "下一步命令 / Next command" in result.output
    assert "ai-sdlc adapter status" in result.output
    assert "命令作用 / What this command does" in result.output


def test_host_runtime_plan_text_deduplicates_reason_codes_and_remediation_targets(
    initialized_project_dir: Path,
) -> None:
    plan = SimpleNamespace(
        status="remediation_required",
        surface_kind="installed_cli",
        surface_binding_state="bound",
        platform_os="darwin",
        platform_arch="arm64",
        reason_codes=[
            "node_runtime_missing",
            "node_runtime_missing",
            "playwright_browsers_missing",
        ],
        bootstrap_acquisition=None,
        remediation_fragment=SimpleNamespace(
            will_install=[
                "node_runtime",
                "node_runtime",
                "playwright_browsers",
            ]
        ),
    )

    with patch(
        "ai_sdlc.cli.host_runtime_cmd.find_project_root",
        return_value=initialized_project_dir,
    ), patch(
        "ai_sdlc.cli.host_runtime_cmd.evaluate_current_host_runtime",
        return_value=plan,
    ):
        result = runner.invoke(app, ["host-runtime", "plan"])

    assert result.exit_code == 0
    assert "node_runtime_missing, playwright_browsers_missing" in result.output
    assert "node_runtime_missing, node_runtime_missing" not in result.output
    assert "node_runtime, playwright_browsers" in result.output
    assert "node_runtime, node_runtime" not in result.output
