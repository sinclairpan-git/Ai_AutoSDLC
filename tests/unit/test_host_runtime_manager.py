"""Unit tests for Host Runtime Manager contract truth."""

from __future__ import annotations

from ai_sdlc.core import host_runtime_manager
from ai_sdlc.core.host_runtime_manager import HostRuntimeProbe, build_host_runtime_plan
from ai_sdlc.models.host_runtime_plan import (
    BootstrapAcquisitionFacet,
    HostRuntimePlan,
    HostRuntimeReadiness,
    InstallerProfileRef,
    RemediationFragmentFacet,
)


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


def test_bootstrap_missing_entries_deduplicates_required_runtime_entries(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        host_runtime_manager,
        "_REQUIRED_RUNTIME_ENTRIES",
        [
            "python_runtime",
            "python_runtime",
            "installed_cli_runtime",
        ],
    )

    result = host_runtime_manager._bootstrap_missing_entries(
        "unsupported_platform",
        probe=HostRuntimeProbe(
            platform_os="solaris",
            platform_arch="sparc",
            python_version=None,
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="missing",
        ),
        python_status="missing",
        installed_runtime_status="missing",
    )

    assert result == ["python_runtime", "installed_cli_runtime"]


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


def test_build_host_runtime_plan_deduplicates_repeated_plan_lists(monkeypatch) -> None:
    monkeypatch.setattr(
        host_runtime_manager,
        "_mainline_reason_codes",
        lambda **_: [
            "node_runtime_missing",
            "node_runtime_missing",
            "playwright_browsers_missing",
        ],
    )

    plan = build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            node_runtime_available=False,
            playwright_browsers_available=False,
        )
    )

    assert plan.reason_codes == [
        "node_runtime_missing",
        "playwright_browsers_missing",
    ]
    assert plan.missing_runtime_entries == [
        "node_runtime",
        "playwright_browsers",
    ]
    assert plan.remediation_fragment is not None
    assert plan.remediation_fragment.reason_codes == [
        "node_runtime_missing",
        "playwright_browsers_missing",
    ]
    assert plan.remediation_fragment.required_actions == [
        "plan_node_runtime_acquisition",
        "plan_playwright_browsers_acquisition",
    ]
    assert plan.remediation_fragment.will_download == [
        "node_runtime",
        "playwright_browsers",
    ]


def test_host_runtime_plan_models_deduplicate_set_like_lists() -> None:
    profile = InstallerProfileRef(
        profile_id="darwin-arm64-default",
        target_os="darwin",
        target_arch="arm64",
        channel_kind="default",
        writes_scope="managed_runtime_root",
        rollback_capability="best_effort",
    )
    plan = HostRuntimePlan(
        plan_id="host-runtime-plan-001",
        platform_os="darwin",
        platform_arch="arm64",
        surface_kind="installed_cli",
        surface_binding_state="bound",
        minimal_executable_host=False,
        installed_runtime_ready=False,
        required_runtime_entries=["python_runtime", "python_runtime", "node_runtime"],
        missing_runtime_entries=["node_runtime", "node_runtime"],
        installer_profile_ids=["darwin-arm64-default", "darwin-arm64-default"],
        install_target_root=".ai-sdlc/runtime",
        requires_network=True,
        requires_credentials=False,
        status="remediation_required",
        reason_codes=["node_runtime_missing", "node_runtime_missing"],
        evidence_refs=["probe:node", "probe:node", "probe:python"],
        readiness=HostRuntimeReadiness(
            python_runtime_status="ready",
            installed_cli_runtime_status="ready",
            node_runtime_status="remediation_required",
            package_manager_status="ready",
            playwright_browsers_status="ready",
            candidate_installer_profiles=[profile],
        ),
        bootstrap_acquisition=BootstrapAcquisitionFacet(
            handoff_kind="bootstrap",
            required_targets=["node_runtime", "node_runtime"],
            recommended_profile_ref=profile,
            manual_steps=["download", "download", "install"],
            operator_decisions_needed=["confirm", "confirm"],
            blocking_reason_codes=["network_missing", "network_missing"],
            expected_reentry_condition="host-ready",
        ),
        remediation_fragment=RemediationFragmentFacet(
            readiness_subject_id="node_runtime",
            managed_runtime_root=".ai-sdlc/runtime",
            required_actions=["install_node", "install_node", "verify_node"],
            optional_actions=["cache_browsers", "cache_browsers"],
            will_download=["node_runtime", "node_runtime"],
            will_install=["node_runtime", "node_runtime"],
            will_modify=["managed_runtime_root", "managed_runtime_root"],
            will_not_touch=["system_python", "system_python"],
            rollback_units=["node_runtime", "node_runtime"],
            cleanup_units=["node_cache", "node_cache"],
            non_rollbackable_effects=["system_env", "system_env"],
            manual_recovery_required=["clear_cache", "clear_cache"],
            reason_codes=["node_runtime_missing", "node_runtime_missing"],
        ),
    )

    assert plan.required_runtime_entries == ["python_runtime", "node_runtime"]
    assert plan.missing_runtime_entries == ["node_runtime"]
    assert plan.installer_profile_ids == ["darwin-arm64-default"]
    assert plan.reason_codes == ["node_runtime_missing"]
    assert plan.evidence_refs == ["probe:node", "probe:python"]
    assert plan.bootstrap_acquisition is not None
    assert plan.bootstrap_acquisition.required_targets == ["node_runtime"]
    assert plan.bootstrap_acquisition.manual_steps == ["download", "download", "install"]
    assert plan.bootstrap_acquisition.operator_decisions_needed == ["confirm", "confirm"]
    assert plan.bootstrap_acquisition.blocking_reason_codes == ["network_missing"]
    assert plan.remediation_fragment is not None
    assert plan.remediation_fragment.required_actions == ["install_node", "verify_node"]
    assert plan.remediation_fragment.optional_actions == ["cache_browsers"]
    assert plan.remediation_fragment.will_download == ["node_runtime"]
    assert plan.remediation_fragment.will_install == ["node_runtime"]
    assert plan.remediation_fragment.will_modify == ["managed_runtime_root"]
    assert plan.remediation_fragment.will_not_touch == ["system_python"]
    assert plan.remediation_fragment.rollback_units == ["node_runtime"]
    assert plan.remediation_fragment.cleanup_units == ["node_cache"]
    assert plan.remediation_fragment.non_rollbackable_effects == ["system_env"]
    assert plan.remediation_fragment.manual_recovery_required == ["clear_cache"]
    assert plan.remediation_fragment.reason_codes == ["node_runtime_missing"]


def test_mainline_missing_entries_deduplicates_reason_code_expansion() -> None:
    from ai_sdlc.core.host_runtime_manager import _mainline_missing_entries

    assert _mainline_missing_entries(
        [
            "node_runtime_missing",
            "node_runtime_missing",
            "package_manager_missing",
        ]
    ) == ["node_runtime", "package_manager"]
