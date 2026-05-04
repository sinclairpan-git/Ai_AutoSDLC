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


def _single_space(text: str) -> str:
    return " ".join(text.split())


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


def test_host_runtime_plan_never_tells_beginner_to_manually_install_python(
    initialized_project_dir: Path,
) -> None:
    bootstrap = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version=None,
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
        )
    )

    with patch(
        "ai_sdlc.cli.host_runtime_cmd.find_project_root",
        return_value=initialized_project_dir,
    ), patch(
        "ai_sdlc.cli.host_runtime_cmd.evaluate_current_host_runtime",
        return_value=bootstrap,
    ):
        text_result = runner.invoke(app, ["host-runtime", "plan"])
        json_result = runner.invoke(app, ["host-runtime", "plan", "--json"])

    assert text_result.exit_code == 1
    assert "不要手动拼装 Python/Node 环境" in text_result.output
    assert "instead of assembling Python/Node manually" in _single_space(
        text_result.output
    )
    assert "install Python 3.11" not in text_result.output

    assert json_result.exit_code == 1
    payload = json.loads(json_result.output)
    assert (
        payload["bootstrap_acquisition"]["handoff_kind"]
        == "managed_runtime_bootstrap_required"
    )
    manual_steps = " ".join(payload["bootstrap_acquisition"]["manual_steps"])
    assert "managed Python runtime" in manual_steps
    assert "install Python 3.11" not in manual_steps


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
    assert "当前结果 / Result" in result.output
    assert "运行环境已就绪" in result.output
    assert "the runtime is ready" in result.output
    assert "ai-sdlc run --dry-run" in result.output
    assert "Host Runtime Plan" not in result.output
    assert "surface: installed_cli / bound" not in result.output


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
    assert "node_runtime, playwright_browsers" in result.output
    assert "node_runtime, node_runtime" not in result.output
    assert "框架会把这些依赖放在托管运行时目录中处理" in result.output
    assert (
        "instead of asking you to change the system environment manually"
        in _single_space(result.output)
    )


def test_host_runtime_plan_details_keeps_diagnostic_table(
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
        result = runner.invoke(app, ["host-runtime", "plan", "--details"])

    assert result.exit_code == 0
    assert "Host Runtime Plan" in result.output
    assert "status: ready" in result.output
    assert "surface: installed_cli / bound" in result.output
