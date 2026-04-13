"""Integration tests for ai-sdlc host-runtime CLI commands."""

from __future__ import annotations

import json
from pathlib import Path
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
