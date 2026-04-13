"""Unit tests for Host Runtime Manager contract truth."""

from __future__ import annotations

from ai_sdlc.core.host_runtime_manager import HostRuntimeProbe, build_host_runtime_plan


def test_build_host_runtime_plan_blocks_unknown_platform() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="solaris",
            platform_arch="sparc",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
        )
    )

    assert plan.status == "blocked"
    assert plan.minimal_executable_host is False
    assert plan.reason_codes == ["unsupported_platform"]
    assert plan.installer_profile_ids == []
    assert plan.bootstrap_acquisition is not None
    assert plan.bootstrap_acquisition.handoff_kind == "unsupported_platform"
    assert plan.remediation_fragment is None


def test_build_host_runtime_plan_fail_closed_when_installed_runtime_unknown() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="unknown",
        )
    )

    assert plan.status == "blocked"
    assert plan.minimal_executable_host is False
    assert plan.reason_codes == ["installed_cli_runtime_unknown"]
    assert plan.readiness.installed_cli_runtime_status == "unknown_evidence"
    assert plan.bootstrap_acquisition is not None
    assert plan.bootstrap_acquisition.handoff_kind == "installed_runtime_binding_required"


def test_build_host_runtime_plan_bootstraps_when_surface_unbound() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="linux",
            platform_arch="x86_64",
            python_version="3.11.9",
            surface_kind="uv_run",
            surface_binding_state="unbound",
            installed_runtime_status="missing",
        )
    )

    assert plan.status == "bootstrap_required"
    assert plan.minimal_executable_host is False
    assert plan.reason_codes == ["surface_binding_unbound"]
    assert plan.readiness.installed_cli_runtime_status == "bootstrap_required"
    assert plan.bootstrap_acquisition is not None
    assert plan.bootstrap_acquisition.handoff_kind == "installed_runtime_binding_required"
    assert "installed_cli_runtime" in plan.bootstrap_acquisition.required_targets


def test_build_host_runtime_plan_emits_remediation_fragment_for_mainline_gaps() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            node_runtime_available=False,
            package_manager_available=True,
            playwright_browsers_available=False,
        )
    )

    assert plan.status == "remediation_required"
    assert plan.minimal_executable_host is True
    assert plan.reason_codes == [
        "node_runtime_missing",
        "playwright_browsers_missing",
    ]
    assert plan.bootstrap_acquisition is None
    assert plan.remediation_fragment is not None
    assert plan.remediation_fragment.reason_codes == [
        "node_runtime_missing",
        "playwright_browsers_missing",
    ]
    assert plan.remediation_fragment.will_download == [
        "node_runtime",
        "playwright_browsers",
    ]
    assert plan.remediation_fragment.will_install == [
        "node_runtime",
        "playwright_browsers",
    ]
    assert plan.remediation_fragment.will_modify == ["managed_runtime_root"]
    assert "system_python" in plan.remediation_fragment.will_not_touch
    payload = plan.model_dump(mode="json")
    assert payload["remediation_fragment"]["will_download"] == [
        "node_runtime",
        "playwright_browsers",
    ]


def test_build_host_runtime_plan_ready_when_all_requirements_present() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="windows",
            platform_arch="amd64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            node_runtime_available=True,
            package_manager_available=True,
            playwright_browsers_available=True,
        )
    )

    assert plan.status == "ready"
    assert plan.minimal_executable_host is True
    assert plan.installed_runtime_ready is True
    assert plan.reason_codes == []
    assert plan.bootstrap_acquisition is None
    assert plan.remediation_fragment is None
    assert plan.readiness.node_runtime_status == "ready"
    assert plan.readiness.package_manager_status == "ready"
    assert plan.readiness.playwright_browsers_status == "ready"


def test_build_host_runtime_plan_blocks_when_offline_bundle_missing() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="linux",
            platform_arch="x86_64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="missing",
            offline_bundle_available=False,
        )
    )

    assert plan.status == "blocked"
    assert plan.reason_codes == ["offline_bundle_missing"]
    assert plan.bootstrap_acquisition is not None
    assert plan.bootstrap_acquisition.handoff_kind == "offline_bundle_required"


def test_build_host_runtime_plan_blocks_when_install_target_not_writable() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            node_runtime_available=False,
            install_target_writable=False,
        )
    )

    assert plan.status == "blocked"
    assert plan.reason_codes == ["permission_denied"]
    assert plan.remediation_fragment is None


def test_build_host_runtime_plan_blocks_when_disk_space_insufficient() -> None:
    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="windows",
            platform_arch="amd64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            package_manager_available=False,
            disk_space_sufficient=False,
        )
    )

    assert plan.status == "blocked"
    assert plan.reason_codes == ["disk_space_insufficient"]
    assert plan.remediation_fragment is None
