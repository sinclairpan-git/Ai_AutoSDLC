"""Unit tests for program manifest service."""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import yaml

import ai_sdlc.core.program_service as program_service_module
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.close_check import CloseCheckResult
from ai_sdlc.core.config import save_project_config
from ai_sdlc.core.frontend_browser_gate_runtime import (
    BrowserGateInteractionProbeCapture,
    BrowserGateProbeRunnerResult,
    BrowserGateSharedRuntimeCapture,
)
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    observation_artifact_path,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
    write_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.core.host_runtime_manager import HostRuntimeProbe, build_host_runtime_plan
from ai_sdlc.core.program_service import (
    ProgramFrontendRemediationCommandResult,
    ProgramFrontendRemediationExecutionResult,
    ProgramService,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.generators.frontend_provider_expansion_artifacts import (
    materialize_frontend_provider_expansion_artifacts,
)
from ai_sdlc.generators.frontend_provider_profile_artifacts import (
    materialize_builtin_frontend_provider_profile_artifacts,
)
from ai_sdlc.generators.frontend_provider_runtime_adapter_artifacts import (
    materialize_frontend_provider_runtime_adapter_artifacts,
)
from ai_sdlc.generators.frontend_quality_platform_artifacts import (
    materialize_frontend_quality_platform_artifacts,
)
from ai_sdlc.generators.frontend_solution_confirmation_artifacts import (
    materialize_frontend_solution_confirmation_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_provider_expansion import (
    build_p3_frontend_provider_expansion_baseline,
)
from ai_sdlc.models.frontend_provider_runtime_adapter import (
    build_p3_target_project_adapter_scaffold_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_install_strategies,
    build_builtin_style_pack_manifests,
    build_mvp_solution_snapshot,
)
from ai_sdlc.models.program import ProgramManifest, ProgramSpecRef
from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.models.state import Checkpoint, FeatureInfo

SAMPLE_FIXTURE_SOURCE_REF = "tests/fixtures/frontend-contract-sample-src/match"


def _manifest() -> ProgramManifest:
    return ProgramManifest(
        schema_version="1",
        prd_path="PRD.md",
        specs=[
            ProgramSpecRef(id="001-auth", path="specs/001-auth", depends_on=[]),
            ProgramSpecRef(
                id="002-course",
                path="specs/002-course",
                depends_on=[],
            ),
            ProgramSpecRef(
                id="003-enroll",
                path="specs/003-enroll",
                depends_on=["001-auth", "002-course"],
            ),
        ],
    )


def _write_frontend_evidence_class_spec(
    root: Path,
    *,
    spec_rel: str,
    frontend_evidence_class: str,
) -> None:
    spec_dir = root / spec_rel
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        "---\n"
        f'frontend_evidence_class: "{frontend_evidence_class}"\n'
        "---\n",
        encoding="utf-8",
    )


def _write_manifest_yaml(root: Path, text: str) -> None:
    (root / "program-manifest.yaml").write_text(
        text.strip() + "\n",
        encoding="utf-8",
    )


def _init_truth_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _commit_truth_repo(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


def _write_truth_ledger_manifest(
    root: Path,
    *,
    frontend_evidence_class: str = "framework_capability",
) -> None:
    _write_manifest_yaml(
        root,
        f"""
schema_version: "2"
prd_path: "PRD.md"
program:
  goal: "Demo truth ledger"
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "082-frontend-example"
    required_evidence:
      truth_check_refs:
        - "specs/082-frontend-example"
      close_check_refs:
        - "specs/082-frontend-example"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
    frontend_evidence_class: "{frontend_evidence_class}"
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
""",
    )


def _write_managed_delivery_apply_request(root: Path, *, fingerprint: str = "fp-001") -> Path:
    payload = {
        "execution_view": {
            "action_plan_id": "plan-001",
            "confirmation_surface_id": "surface-001",
            "plan_fingerprint": fingerprint,
            "protocol_version": "1",
            "managed_target_ref": "managed://frontend/app",
            "managed_target_path": "managed/frontend",
            "attachment_scope_ref": "scope://001-auth",
            "readiness_subject_id": "001-auth",
            "spec_dir": "specs/001-auth",
            "action_items": [
                {
                    "action_id": "a1",
                    "effect_kind": "mutate",
                    "action_type": "runtime_remediation",
                    "required": True,
                    "selected": True,
                    "default_selected": True,
                    "depends_on_action_ids": [],
                    "rollback_ref": "rollback:a1",
                    "retry_ref": "retry:a1",
                    "cleanup_ref": "cleanup:a1",
                    "risk_flags": [],
                    "source_linkage_refs": {"spec": "specs/001-auth"},
                    "executor_payload": {
                        "managed_runtime_root": ".ai-sdlc/runtime",
                        "required_runtime_entries": ["node_runtime"],
                        "install_profile_id": "offline_bundle_darwin_shell",
                        "acquisition_mode": "managed_runtime_install",
                        "will_download": ["node_runtime"],
                        "will_install": [],
                        "will_modify": [".ai-sdlc/runtime"],
                        "manual_prerequisites": [],
                        "reentry_condition": "rerun managed delivery apply",
                    },
                }
            ],
            "will_not_touch": ["legacy-root"],
        },
        "decision_receipt": {
            "decision_receipt_id": "receipt-001",
            "action_plan_id": "plan-001",
            "confirmation_surface_id": "surface-001",
            "decision": "continue",
            "selected_action_ids": ["a1"],
            "deselected_optional_action_ids": [],
            "risk_acknowledgement_ids": [],
            "second_confirmation_acknowledged": True,
            "confirmed_plan_fingerprint": fingerprint,
            "created_at": "2026-04-13T13:30:00Z",
        },
    }
    request_path = root / ".ai-sdlc" / "memory" / "frontend-managed-delivery" / "apply-request.yaml"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return request_path


def _write_frontend_solution_confirmation_artifacts(
    root: Path,
    *,
    snapshot=None,
) -> None:
    materialize_frontend_solution_confirmation_artifacts(
        root,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=snapshot
        or build_mvp_solution_snapshot(
            project_id="001-auth",
            effective_provider_id="public-primevue",
            effective_style_pack_id="modern-saas",
            requested_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            recommended_provider_id="public-primevue",
            recommended_style_pack_id="modern-saas",
            recommended_frontend_stack="vue3",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )


def _write_builtin_delivery_truth(root: Path, *, snapshot=None) -> None:
    _write_frontend_solution_confirmation_artifacts(root, snapshot=snapshot)
    materialize_builtin_frontend_provider_profile_artifacts(
        root,
        provider_id="enterprise-vue2",
    )
    materialize_builtin_frontend_provider_profile_artifacts(
        root,
        provider_id="public-primevue",
    )


def _write_151_truth_checkpoint(root: Path) -> None:
    cp = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="151",
            spec_dir="specs/151-frontend-p3-modern-provider-expansion-baseline",
            design_branch="d",
            feature_branch="f",
            current_branch="main",
        ),
    )
    save_checkpoint(root, cp)


def test_build_frontend_page_ui_schema_handoff_blocks_when_solution_snapshot_missing(
    tmp_path: Path,
) -> None:
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_page_ui_schema_handoff()

    assert handoff.state == "blocked"
    assert "frontend_solution_snapshot_missing" in handoff.blockers
    assert handoff.effective_provider_id == ""
    assert handoff.effective_style_pack_id == ""


def test_build_frontend_page_ui_schema_handoff_uses_latest_solution_snapshot(
    tmp_path: Path,
) -> None:
    _write_frontend_solution_confirmation_artifacts(
        tmp_path,
        snapshot=build_mvp_solution_snapshot(
            project_id="147-demo",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            style_fidelity_status="full",
        ),
    )
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_page_ui_schema_handoff()

    assert handoff.state == "ready"
    assert handoff.schema_version == "1.0"
    assert handoff.effective_provider_id == "public-primevue"
    assert handoff.effective_style_pack_id == "modern-saas"
    assert [entry.page_schema_id for entry in handoff.entries] == [
        "dashboard-workspace",
        "search-list-workspace",
        "wizard-workspace",
    ]


def test_build_frontend_theme_token_governance_handoff_blocks_when_solution_snapshot_missing(
    tmp_path: Path,
) -> None:
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_theme_token_governance_handoff()

    assert handoff.state == "blocked"
    assert "frontend_solution_snapshot_missing" in handoff.blockers
    assert handoff.effective_provider_id == ""
    assert handoff.requested_style_pack_id == ""
    assert handoff.effective_style_pack_id == ""


def test_build_frontend_theme_token_governance_handoff_uses_latest_solution_snapshot_and_page_schema_handoff(
    tmp_path: Path,
) -> None:
    _write_builtin_delivery_truth(
        tmp_path,
        snapshot=build_mvp_solution_snapshot(
            project_id="148-demo",
            requested_provider_id="enterprise-vue2",
            effective_provider_id="enterprise-vue2",
            recommended_provider_id="enterprise-vue2",
            requested_style_pack_id="enterprise-default",
            effective_style_pack_id="enterprise-default",
            recommended_style_pack_id="enterprise-default",
            requested_frontend_stack="vue2",
            effective_frontend_stack="vue2",
            recommended_frontend_stack="vue2",
            style_fidelity_status="full",
        ),
    )
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_theme_token_governance_handoff()

    assert handoff.state == "ready"
    assert handoff.schema_version == "1.0"
    assert handoff.effective_provider_id == "enterprise-vue2"
    assert handoff.requested_style_pack_id == "enterprise-default"
    assert handoff.effective_style_pack_id == "enterprise-default"
    assert handoff.page_schema_ids == [
        "dashboard-workspace",
        "search-list-workspace",
        "wizard-workspace",
    ]
    assert handoff.token_mapping_count > 0
    assert handoff.override_diagnostics[0].override_id == (
        "dashboard-page-header-accent-proposal"
    )
    assert handoff.override_diagnostics[0].requested_value == "brand-accent"
    assert handoff.override_diagnostics[0].effective_value == (
        "style-pack:enterprise-default:accent_mode"
    )


def test_build_frontend_quality_platform_handoff_blocks_when_solution_snapshot_missing(
    tmp_path: Path,
) -> None:
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_quality_platform_handoff()

    assert handoff.state == "blocked"
    assert "frontend_solution_snapshot_missing" in handoff.blockers


def test_build_frontend_quality_platform_handoff_uses_latest_solution_snapshot_and_surfaces_matrix_diagnostics(
    tmp_path: Path,
) -> None:
    materialize_frontend_solution_confirmation_artifacts(
        tmp_path,
        style_packs=build_builtin_style_pack_manifests(),
        install_strategies=build_builtin_install_strategies(),
        snapshot=build_mvp_solution_snapshot(
            project_id="149-demo",
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )
    materialize_frontend_quality_platform_artifacts(
        tmp_path,
        platform=build_p2_frontend_quality_platform_baseline(),
    )
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_quality_platform_handoff()

    assert handoff.state == "ready"
    assert handoff.effective_provider_id == "public-primevue"
    assert handoff.requested_style_pack_id == "modern-saas"
    assert handoff.effective_style_pack_id == "modern-saas"
    assert handoff.matrix_coverage_count == 3
    assert handoff.evidence_contract_ids == [
        "a11y-matrix-evidence",
        "interaction-quality-evidence",
        "visual-regression-evidence",
    ]
    assert handoff.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]
    assert {item.matrix_id for item in handoff.quality_diagnostics} == {
        "dashboard-modern-saas-desktop-chromium",
        "dashboard-modern-saas-mobile-webkit",
        "search-enterprise-default-desktop-chromium",
    }


def test_build_frontend_provider_expansion_handoff_blocks_when_solution_snapshot_missing(
    tmp_path: Path,
) -> None:
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_provider_expansion_handoff()

    assert handoff.state == "blocked"
    assert "frontend_solution_snapshot_missing" in handoff.blockers
    assert handoff.effective_provider_id == ""
    assert handoff.requested_frontend_stack == ""
    assert handoff.effective_frontend_stack == ""


def test_build_frontend_provider_expansion_handoff_uses_latest_solution_snapshot_and_provider_diagnostics(
    tmp_path: Path,
) -> None:
    _write_builtin_delivery_truth(
        tmp_path,
        snapshot=build_mvp_solution_snapshot(
            project_id="151-demo",
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )
    materialize_frontend_provider_expansion_artifacts(
        tmp_path,
        expansion=build_p3_frontend_provider_expansion_baseline(),
    )
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_provider_expansion_handoff()

    assert handoff.state == "ready"
    assert handoff.schema_version == "1.0"
    assert handoff.effective_provider_id == "public-primevue"
    assert handoff.requested_frontend_stack == "vue3"
    assert handoff.effective_frontend_stack == "vue3"
    assert handoff.react_stack_visibility == "hidden"
    assert handoff.react_binding_visibility == "hidden"
    assert [entry.provider_id for entry in handoff.provider_diagnostics] == [
        "public-primevue",
        "react-nextjs-shadcn",
    ]
    assert handoff.provider_diagnostics[0].certification_gate == "ready"
    assert handoff.provider_diagnostics[0].choice_surface_visibility == (
        "simple-default-eligible"
    )


def test_build_frontend_provider_runtime_adapter_handoff_blocks_when_solution_snapshot_missing(
    tmp_path: Path,
) -> None:
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_provider_runtime_adapter_handoff()

    assert handoff.state == "blocked"
    assert "frontend_solution_snapshot_missing" in handoff.blockers
    assert handoff.effective_provider_id == ""
    assert handoff.requested_frontend_stack == ""
    assert handoff.effective_frontend_stack == ""


def test_build_frontend_provider_runtime_adapter_handoff_surfaces_scaffold_and_delivery_state(
    tmp_path: Path,
) -> None:
    _write_builtin_delivery_truth(
        tmp_path,
        snapshot=build_mvp_solution_snapshot(
            project_id="153-demo",
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )
    materialize_frontend_provider_runtime_adapter_artifacts(
        tmp_path,
        runtime_adapter=build_p3_target_project_adapter_scaffold_baseline(),
    )
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_provider_runtime_adapter_handoff()

    assert handoff.state == "ready"
    assert handoff.schema_version == "1.0"
    assert handoff.effective_provider_id == "public-primevue"
    assert handoff.requested_frontend_stack == "vue3"
    assert handoff.effective_frontend_stack == "vue3"
    assert handoff.carrier_mode == "target-project-adapter-layer"
    assert handoff.runtime_delivery_state == "scaffolded"
    assert handoff.evidence_return_state == "missing"
    assert [entry.provider_id for entry in handoff.provider_diagnostics] == [
        "public-primevue",
        "react-nextjs-shadcn",
    ]
    assert handoff.provider_diagnostics[0].scaffold_file_count == 4


def test_build_frontend_cross_provider_consistency_handoff_surfaces_pair_truth_and_release_blockers(
    tmp_path: Path,
) -> None:
    svc = ProgramService(tmp_path)

    handoff = svc.build_frontend_cross_provider_consistency_handoff()

    assert handoff.state == "blocked"
    assert handoff.schema_version == "1.0"
    assert handoff.artifact_root == "governance/frontend/cross-provider-consistency"
    assert handoff.pair_count == 3
    assert handoff.ready_pair_count == 1
    assert handoff.conditional_pair_count == 1
    assert handoff.blocked_pair_count == 1
    assert handoff.page_schema_ids == [
        "dashboard-workspace",
        "search-list-workspace",
        "wizard-workspace",
    ]
    assert [entry.pair_id for entry in handoff.pair_diagnostics] == [
        "enterprise-vue2__public-primevue__search-list-workspace",
        "enterprise-vue2__public-primevue__dashboard-workspace",
        "enterprise-vue2__public-primevue__wizard-workspace",
    ]
    assert handoff.pair_diagnostics[0].certification_gate == "ready"
    assert handoff.pair_diagnostics[1].comparability_state == "coverage-gap"
    assert handoff.pair_diagnostics[2].blocking_state == "upstream-blocked"
    assert any(
        "certification gate remains blocked" in blocker for blocker in handoff.blockers
    )
    assert any(
        "certification gate remains conditional" in warning for warning in handoff.warnings
    )


def _build_host_runtime_plan_for_tests(
    *,
    node_runtime_available: bool | None,
    package_manager_available: bool | None,
    playwright_browsers_available: bool | None,
) :
    return build_host_runtime_plan(
        HostRuntimeProbe(
            platform_os="darwin",
            platform_arch="arm64",
            python_version="3.11.9",
            surface_kind="installed_cli",
            surface_binding_state="bound",
            installed_runtime_status="ready",
            node_runtime_available=node_runtime_available,
            package_manager_available=package_manager_available,
            playwright_browsers_available=playwright_browsers_available,
            offline_bundle_available=True,
            bundle_platform_matches=True,
            install_target_writable=True,
            disk_space_sufficient=True,
        )
    )


def _write_blocked_managed_delivery_apply_request(root: Path) -> Path:
    payload = {
        "execution_view": {
            "action_plan_id": "plan-001",
            "confirmation_surface_id": "surface-001",
            "plan_fingerprint": "fp-001",
            "protocol_version": "1",
            "managed_target_ref": "managed://frontend/app",
            "managed_target_path": "managed/frontend",
            "attachment_scope_ref": "scope://001-auth",
            "readiness_subject_id": "001-auth",
            "spec_dir": "specs/001-auth",
            "action_items": [
                {
                    "action_id": "a1",
                    "effect_kind": "mutate",
                    "action_type": "artifact_generate",
                    "required": True,
                    "selected": True,
                    "default_selected": True,
                    "depends_on_action_ids": [],
                    "rollback_ref": "rollback:a1",
                    "retry_ref": "retry:a1",
                    "cleanup_ref": "cleanup:a1",
                    "risk_flags": [],
                    "source_linkage_refs": {"spec": "specs/001-auth"},
                    "executor_payload": {
                        "files": [
                            {
                                "path": "../legacy-root/Blocked.vue",
                                "content": "<template>blocked</template>\n",
                            }
                        ]
                    },
                }
            ],
            "will_not_touch": ["legacy-root"],
        },
        "decision_receipt": {
            "decision_receipt_id": "receipt-001",
            "action_plan_id": "plan-001",
            "confirmation_surface_id": "surface-001",
            "decision": "continue",
            "selected_action_ids": ["a1"],
            "deselected_optional_action_ids": [],
            "risk_acknowledgement_ids": [],
            "second_confirmation_acknowledged": True,
            "confirmed_plan_fingerprint": "fp-001",
            "created_at": "2026-04-13T13:30:00Z",
        },
    }
    request_path = root / ".ai-sdlc" / "memory" / "frontend-managed-delivery" / "apply-request-blocked.yaml"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return request_path


def _write_artifact_generate_apply_request(root: Path) -> Path:
    payload = {
        "execution_view": {
            "action_plan_id": "plan-001",
            "confirmation_surface_id": "surface-001",
            "plan_fingerprint": "fp-001",
            "protocol_version": "1",
            "managed_target_ref": "managed://frontend/app",
            "managed_target_path": "managed/frontend",
            "attachment_scope_ref": "scope://001-auth",
            "readiness_subject_id": "001-auth",
            "spec_dir": "specs/001-auth",
            "action_items": [
                {
                    "action_id": "a1",
                    "effect_kind": "mutate",
                    "action_type": "artifact_generate",
                    "required": True,
                    "selected": True,
                    "default_selected": True,
                    "depends_on_action_ids": [],
                    "rollback_ref": "rollback:a1",
                    "retry_ref": "retry:a1",
                    "cleanup_ref": "cleanup:a1",
                    "risk_flags": [],
                    "source_linkage_refs": {"spec": "specs/001-auth"},
                    "executor_payload": {
                        "directories": ["src"],
                        "files": [
                            {
                                "path": "src/App.vue",
                                "content": "<template>generated</template>\n",
                            }
                        ],
                    },
                }
            ],
            "will_not_touch": ["legacy-root"],
        },
        "decision_receipt": {
            "decision_receipt_id": "receipt-001",
            "action_plan_id": "plan-001",
            "confirmation_surface_id": "surface-001",
            "decision": "continue",
            "selected_action_ids": ["a1"],
            "deselected_optional_action_ids": [],
            "risk_acknowledgement_ids": [],
            "second_confirmation_acknowledged": True,
            "confirmed_plan_fingerprint": "fp-001",
            "created_at": "2026-04-13T13:30:00Z",
        },
    }
    request_path = root / ".ai-sdlc" / "memory" / "frontend-managed-delivery" / "apply-request-artifact.yaml"
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return request_path


def test_validate_manifest_ok(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    svc = ProgramService(tmp_path)
    res = svc.validate_manifest(_manifest())
    assert res.valid is True
    assert res.errors == []


def test_program_manifest_v2_preserves_truth_ledger_fields() -> None:
    manifest = ProgramManifest.model_validate(
        {
            "schema_version": "2",
            "prd_path": "PRD.md",
            "program": {"goal": "AI-SDLC automated framework"},
            "release_targets": ["frontend-mainline-delivery"],
            "capabilities": [
                {
                    "id": "frontend-mainline-delivery",
                    "title": "Frontend Mainline Delivery",
                    "goal": "ship the managed frontend mainline",
                    "release_required": True,
                    "spec_refs": ["001-auth"],
                    "required_evidence": {
                        "truth_check_refs": ["specs/001-auth"],
                        "close_check_refs": ["specs/001-auth"],
                        "verify_refs": ["uv run ai-sdlc verify constraints"],
                    },
                }
            ],
            "specs": [
                {
                    "id": "001-auth",
                    "path": "specs/001-auth",
                    "depends_on": [],
                    "roles": ["runtime_carrier"],
                    "capability_refs": ["frontend-mainline-delivery"],
                }
            ],
            "truth_snapshot": {
                "generated_at": "2026-04-14T12:00:00Z",
                "generated_by": "ai-sdlc program truth sync",
                "generator_version": "1",
                "repo_revision": "abc123",
                "authoring_hash": "authoring-hash",
                "source_hashes": {"program-manifest.yaml": "src-hash"},
                "snapshot_hash": "snapshot-hash",
                "computed_capabilities": [
                    {
                        "capability_id": "frontend-mainline-delivery",
                        "closure_state": "partial",
                        "audit_state": "blocked",
                        "blocking_refs": ["canonical_conflict"],
                        "stale_reason": "",
                    }
                ],
                "state": "blocked",
            },
        }
    )

    assert manifest.schema_version == "2"
    assert manifest.program is not None
    assert manifest.program.goal == "AI-SDLC automated framework"
    assert manifest.release_targets == ["frontend-mainline-delivery"]
    assert manifest.capabilities[0].id == "frontend-mainline-delivery"
    assert manifest.capabilities[0].required_evidence.truth_check_refs == [
        "specs/001-auth"
    ]
    assert manifest.specs[0].roles == ["runtime_carrier"]
    assert manifest.specs[0].capability_refs == ["frontend-mainline-delivery"]
    assert manifest.truth_snapshot is not None
    assert manifest.truth_snapshot.authoring_hash == "authoring-hash"
    assert manifest.truth_snapshot.computed_capabilities[0].audit_state == "blocked"


def test_validate_manifest_rejects_unknown_release_target(tmp_path: Path) -> None:
    (tmp_path / "specs" / "001-auth").mkdir(parents=True)
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest.model_validate(
        {
            "schema_version": "2",
            "prd_path": "PRD.md",
            "program": {"goal": "AI-SDLC automated framework"},
            "release_targets": ["missing-capability"],
            "capabilities": [
                {
                    "id": "frontend-mainline-delivery",
                    "title": "Frontend Mainline Delivery",
                    "goal": "ship the managed frontend mainline",
                    "release_required": True,
                    "spec_refs": ["001-auth"],
                    "required_evidence": {
                        "truth_check_refs": ["specs/001-auth"],
                        "close_check_refs": ["specs/001-auth"],
                        "verify_refs": ["uv run ai-sdlc verify constraints"],
                    },
                }
            ],
            "specs": [
                {
                    "id": "001-auth",
                    "path": "specs/001-auth",
                    "depends_on": [],
                    "roles": ["runtime_carrier"],
                    "capability_refs": ["frontend-mainline-delivery"],
                }
            ],
        }
    )

    res = svc.validate_manifest(manifest)

    assert res.valid is False
    assert any("unknown release target" in err for err in res.errors)


def test_validate_manifest_rejects_release_scope_spec_without_roles_and_capability_refs(
    tmp_path: Path,
) -> None:
    (tmp_path / "specs" / "001-auth").mkdir(parents=True)
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest.model_validate(
        {
            "schema_version": "2",
            "prd_path": "PRD.md",
            "program": {"goal": "AI-SDLC automated framework"},
            "release_targets": ["frontend-mainline-delivery"],
            "capabilities": [
                {
                    "id": "frontend-mainline-delivery",
                    "title": "Frontend Mainline Delivery",
                    "goal": "ship the managed frontend mainline",
                    "release_required": True,
                    "spec_refs": ["001-auth"],
                    "required_evidence": {
                        "truth_check_refs": ["specs/001-auth"],
                        "close_check_refs": ["specs/001-auth"],
                        "verify_refs": ["uv run ai-sdlc verify constraints"],
                    },
                }
            ],
            "specs": [
                {
                    "id": "001-auth",
                    "path": "specs/001-auth",
                    "depends_on": [],
                }
            ],
        }
    )

    res = svc.validate_manifest(manifest)

    assert res.valid is False
    assert any("release-scope spec 001-auth: roles must not be empty" in err for err in res.errors)
    assert any(
        "release-scope spec 001-auth: capability_refs must not be empty" in err
        for err in res.errors
    )


def test_validate_manifest_warns_for_non_release_scope_spec_dir_missing_entry_in_v2(
    tmp_path: Path,
) -> None:
    (tmp_path / "specs" / "001-auth").mkdir(parents=True)
    (tmp_path / "specs" / "001-auth" / "spec.md").write_text(
        "# auth\n", encoding="utf-8"
    )
    (tmp_path / "specs" / "999-legacy").mkdir(parents=True)
    (tmp_path / "specs" / "999-legacy" / "spec.md").write_text(
        "# legacy\n", encoding="utf-8"
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest.model_validate(
        {
            "schema_version": "2",
            "prd_path": "PRD.md",
            "program": {"goal": "AI-SDLC automated framework"},
            "release_targets": ["frontend-mainline-delivery"],
            "capabilities": [
                {
                    "id": "frontend-mainline-delivery",
                    "title": "Frontend Mainline Delivery",
                    "goal": "ship the managed frontend mainline",
                    "release_required": True,
                    "spec_refs": ["001-auth"],
                    "required_evidence": {
                        "truth_check_refs": ["specs/001-auth"],
                        "close_check_refs": ["specs/001-auth"],
                        "verify_refs": ["uv run ai-sdlc verify constraints"],
                    },
                }
            ],
            "specs": [
                {
                    "id": "001-auth",
                    "path": "specs/001-auth",
                    "depends_on": [],
                    "roles": ["runtime_carrier"],
                    "capability_refs": ["frontend-mainline-delivery"],
                }
            ],
        }
    )

    res = svc.validate_manifest(manifest)

    assert res.valid is True
    assert any(
        "migration_pending: manifest entry missing for specs/999-legacy" in warning
        for warning in res.warnings
    )


def test_validate_manifest_warns_for_unmapped_truth_sources_in_v2(
    tmp_path: Path,
) -> None:
    (tmp_path / "specs" / "001-auth").mkdir(parents=True)
    (tmp_path / "specs" / "001-auth" / "spec.md").write_text(
        "# auth\n", encoding="utf-8"
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    (tmp_path / "docs" / "superpowers" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "superpowers" / "specs" / "2026-04-02-design.md").write_text(
        "# Design\n\nP2 modern provider\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "releases").mkdir(parents=True)
    (tmp_path / "docs" / "releases" / "v0.9.0.md").write_text(
        "# v0.9.0\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "framework-defect-backlog.zh-CN.md").write_text(
        "# backlog\n\n后续治理\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "requirements-gap-reconciliation.zh-CN.md").write_text(
        "# requirements\n\n第二期能力\n",
        encoding="utf-8",
    )
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest.model_validate(
        {
            "schema_version": "2",
            "prd_path": "PRD.md",
            "program": {"goal": "AI-SDLC automated framework"},
            "release_targets": ["frontend-mainline-delivery"],
            "capabilities": [
                {
                    "id": "frontend-mainline-delivery",
                    "title": "Frontend Mainline Delivery",
                    "goal": "ship the managed frontend mainline",
                    "release_required": True,
                    "spec_refs": ["001-auth"],
                    "required_evidence": {
                        "truth_check_refs": ["specs/001-auth"],
                        "close_check_refs": ["specs/001-auth"],
                        "verify_refs": ["uv run ai-sdlc verify constraints"],
                    },
                }
            ],
            "specs": [
                {
                    "id": "001-auth",
                    "path": "specs/001-auth",
                    "depends_on": [],
                    "roles": ["runtime_carrier"],
                    "capability_refs": ["frontend-mainline-delivery"],
                }
            ],
        }
    )

    res = svc.validate_manifest(manifest)

    assert res.valid is True
    assert any(
        "migration_pending: truth source unmapped for docs/superpowers/specs/2026-04-02-design.md"
        in warning
        for warning in res.warnings
    )
    assert any(
        "migration_pending: truth source unmapped for docs/releases/v0.9.0.md"
        in warning
        for warning in res.warnings
    )
    assert any(
        "migration_pending: truth source unmapped for docs/framework-defect-backlog.zh-CN.md"
        in warning
        for warning in res.warnings
    )
    assert any(
        "migration_pending: truth source unmapped for docs/requirements-gap-reconciliation.zh-CN.md"
        in warning
        for warning in res.warnings
    )


def test_build_truth_snapshot_includes_source_inventory_and_layer_counts(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [ ] pending\n", encoding="utf-8")
    (tmp_path / "docs" / "superpowers" / "specs").mkdir(parents=True)
    (tmp_path / "docs" / "superpowers" / "specs" / "2026-04-02-design.md").write_text(
        "# Design\n\nP2 modern provider\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "releases").mkdir(parents=True)
    (tmp_path / "docs" / "releases" / "v0.9.0.md").write_text(
        "# v0.9.0\n", encoding="utf-8"
    )
    (tmp_path / "docs" / "framework-defect-backlog.zh-CN.md").write_text(
        "# backlog\n\n后续治理\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "requirements-gap-reconciliation.zh-CN.md").write_text(
        "# requirements\n\n第二期能力\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "2"
prd_path: "PRD.md"
program:
  goal: "Demo truth ledger"
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "082-frontend-example"
    required_evidence:
      truth_check_refs:
        - "specs/082-frontend-example"
      close_check_refs:
        - "specs/082-frontend-example"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
    frontend_evidence_class: "framework_capability"
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
source_registry:
  - path: "docs/superpowers/specs/2026-04-02-design.md"
    source_type: "design_doc"
    truth_layer: "design"
  - path: "docs/releases/v0.9.0.md"
    source_type: "release_doc"
    truth_layer: "release"
  - path: "docs/framework-defect-backlog.zh-CN.md"
    source_type: "defect_backlog"
    truth_layer: "defect"
  - path: "docs/requirements-gap-reconciliation.zh-CN.md"
    source_type: "requirement_doc"
    truth_layer: "requirements"
""",
    )
    _commit_truth_repo(tmp_path, "seed truth ledger source inventory fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    validation = svc.validate_manifest(manifest)
    snapshot = svc.build_truth_snapshot(manifest, validation_result=validation)

    inventory = snapshot.source_inventory
    assert inventory is not None
    assert inventory.state == "complete"
    assert inventory.total_sources == 10
    assert inventory.mapped_sources == 10
    assert inventory.unmapped_sources == 0
    assert inventory.missing_sources == 2
    assert inventory.layer_totals == {
        "blueprint": 1,
        "spec": 1,
        "plan": 1,
        "tasks": 1,
        "execution": 1,
        "close": 1,
        "design": 1,
        "release": 1,
        "defect": 1,
        "requirements": 1,
    }
    assert inventory.layer_materialized == {
        "blueprint": 1,
        "spec": 1,
        "plan": 1,
        "tasks": 1,
        "execution": 0,
        "close": 0,
        "design": 1,
        "release": 1,
        "defect": 1,
        "requirements": 1,
    }
    assert inventory.phase_signal_count >= 2
    assert inventory.deferred_signal_count >= 2


def test_build_truth_snapshot_maps_frontend_canonical_conflict_to_blocked(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(
        tmp_path,
        frontend_evidence_class="consumer_adoption",
    )
    _commit_truth_repo(tmp_path, "seed truth ledger conflict fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    validation = svc.validate_manifest(manifest)
    snapshot = svc.build_truth_snapshot(manifest, validation_result=validation)

    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in error
        for error in validation.errors
    )
    capability = snapshot.computed_capabilities[0]
    assert capability.audit_state == "blocked"
    assert any(
        blocker == "canonical_conflict:frontend-mainline-delivery"
        for blocker in capability.blocking_refs
    )


def test_build_truth_snapshot_blocks_release_scope_on_151_provider_expansion_verify_gap(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "151-frontend-p3-modern-provider-expansion-baseline"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (spec_dir / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "2"
prd_path: "PRD.md"
program:
  goal: "Demo truth ledger"
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "151-frontend-p3-modern-provider-expansion-baseline"
    required_evidence:
      truth_check_refs:
        - "specs/151-frontend-p3-modern-provider-expansion-baseline"
      close_check_refs:
        - "specs/151-frontend-p3-modern-provider-expansion-baseline"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
specs:
  - id: "151-frontend-p3-modern-provider-expansion-baseline"
    path: "specs/151-frontend-p3-modern-provider-expansion-baseline"
    depends_on: []
    frontend_evidence_class: "framework_capability"
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
""",
    )
    _write_151_truth_checkpoint(tmp_path)
    _commit_truth_repo(tmp_path, "seed 151 truth ledger fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)

    capability = snapshot.computed_capabilities[0]
    assert capability.audit_state == "blocked"
    assert "verify:uv run ai-sdlc verify constraints" in capability.blocking_refs


def test_build_truth_snapshot_blocks_release_scope_on_149_quality_platform_verify_gap(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "149-frontend-p2-quality-platform-baseline"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (spec_dir / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "2"
prd_path: "PRD.md"
program:
  goal: "Demo truth ledger"
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "149-frontend-p2-quality-platform-baseline"
    required_evidence:
      truth_check_refs:
        - "specs/149-frontend-p2-quality-platform-baseline"
      close_check_refs:
        - "specs/149-frontend-p2-quality-platform-baseline"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
specs:
  - id: "149-frontend-p2-quality-platform-baseline"
    path: "specs/149-frontend-p2-quality-platform-baseline"
    depends_on: []
    frontend_evidence_class: "framework_capability"
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
""",
    )
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="149",
                spec_dir="specs/149-frontend-p2-quality-platform-baseline",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )
    _commit_truth_repo(tmp_path, "seed 149 truth ledger fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)

    capability = snapshot.computed_capabilities[0]
    assert capability.audit_state == "blocked"
    assert "verify:uv run ai-sdlc verify constraints" in capability.blocking_refs


def test_build_truth_snapshot_keeps_canonical_conflict_blocked_when_structural_errors_exist(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "2"
prd_path: "PRD.md"
program:
  goal: "Demo truth ledger"
release_targets:
  - "frontend-mainline-delivery"
capabilities:
  - id: "frontend-mainline-delivery"
    title: "Frontend Mainline Delivery"
    goal: "Demo release target"
    release_required: true
    spec_refs:
      - "082-frontend-example"
    required_evidence:
      truth_check_refs:
        - "specs/082-frontend-example"
      close_check_refs:
        - "specs/082-frontend-example"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
    frontend_evidence_class: "consumer_adoption"
""",
    )
    _commit_truth_repo(tmp_path, "seed truth ledger conflict plus invalid fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)

    capability = snapshot.computed_capabilities[0]
    assert capability.audit_state == "blocked"
    assert "canonical_conflict:frontend-mainline-delivery" in capability.blocking_refs
    assert "manifest_validation:frontend-mainline-delivery" in capability.blocking_refs


def test_build_truth_ledger_surface_marks_stale_when_authoring_hash_changes(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(tmp_path)
    payload = yaml.safe_load((tmp_path / "program-manifest.yaml").read_text(encoding="utf-8"))
    payload["capability_closure_audit"] = {
        "reviewed_at": "2026-04-18T08:00:00Z",
        "open_clusters": [],
    }
    (tmp_path / "program-manifest.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    _commit_truth_repo(tmp_path, "seed truth ledger stale fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    with (
        patch.object(
            ProgramService,
            "_run_close_check_ref",
            return_value={"ok": True, "blockers": [], "checks": [], "error": None},
        ),
        patch.object(
            ProgramService,
            "_run_verify_ref",
            return_value={
                "ok": True,
                "command": "uv run ai-sdlc verify constraints",
                "blockers": [],
                "warnings": [],
            },
        ),
    ):
        snapshot = svc.build_truth_snapshot(manifest)
        svc.write_truth_snapshot(snapshot)

        payload = yaml.safe_load(
            (tmp_path / "program-manifest.yaml").read_text(encoding="utf-8")
        )
        payload["program"]["goal"] = "Updated goal after sync"
        (tmp_path / "program-manifest.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

        updated_manifest = svc.load_manifest()
        surface = svc.build_truth_ledger_surface(updated_manifest)

    assert surface is not None
    assert surface["snapshot_state"] == "stale"
    assert surface["state"] == "stale"
    assert surface["release_capabilities"] == [
        {
            "capability_id": "frontend-mainline-delivery",
            "closure_state": "closed",
            "audit_state": "ready",
            "blocking_refs": [],
        }
    ]
    assert (
        surface["detail"]
        == "persisted truth snapshot is stale; current recompute is ready. "
        "Refresh the snapshot as the terminal close-out step, then rerun program truth audit."
    )


def test_build_truth_ledger_surface_stays_fresh_for_truth_snapshot_only_drift(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(tmp_path)
    _commit_truth_repo(tmp_path, "seed truth ledger sync fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)
    svc.write_truth_snapshot(snapshot)

    updated_manifest = svc.load_manifest()
    surface = svc.build_truth_ledger_surface(updated_manifest)

    assert surface is not None
    assert surface["snapshot_state"] == "fresh"
    assert surface["state"] == snapshot.state


def test_build_truth_snapshot_reuses_manifest_context_for_close_check_refs(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(tmp_path)
    _commit_truth_repo(tmp_path, "seed truth ledger close-check context fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    validation = svc.validate_manifest(manifest)
    seen: list[tuple[str, object | None, object | None]] = []

    def _fake_close_check_ref(
        self,
        ref: str,
        *,
        manifest=None,
        validation_result=None,
    ) -> dict[str, object]:
        seen.append((ref, manifest, validation_result))
        return {"ok": True, "blockers": [], "checks": [], "error": None}

    monkeypatch.setattr(ProgramService, "_run_close_check_ref", _fake_close_check_ref)
    monkeypatch.setattr(
        ProgramService,
        "_run_truth_check_ref",
        lambda self, ref: {
            "ok": True,
            "classification": "merged_implemented",
            "detail": "",
            "error": None,
        },
    )
    monkeypatch.setattr(
        ProgramService,
        "_run_verify_ref",
        lambda self, ref, *, constraint_report: {
            "ok": True,
            "command": ref,
            "blockers": [],
            "warnings": [],
        },
    )

    svc.build_truth_snapshot(manifest, validation_result=validation)

    assert seen
    assert all(ref for ref, _, _ in seen)
    assert all(passed_manifest is manifest for _, passed_manifest, _ in seen)
    assert all(passed_validation is validation for _, _, passed_validation in seen)


def test_build_truth_ledger_surface_ignores_ephemeral_close_check_drift(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(tmp_path)
    _commit_truth_repo(tmp_path, "seed truth ledger ephemeral close-check fixture")

    dirty_git = True

    def _fake_run_close_check(**_: object) -> CloseCheckResult:
        if dirty_git:
            return CloseCheckResult(
                ok=False,
                blockers=[
                    "BLOCKER: git close-out verification failed: git working tree has uncommitted changes; close-out is not fully committed"
                ],
                checks=[
                    {
                        "name": "tasks_completion",
                        "ok": True,
                        "detail": "all checklist items done",
                    },
                    {
                        "name": "git_closure",
                        "ok": False,
                        "detail": "git working tree has uncommitted changes; close-out is not fully committed",
                    },
                    {
                        "name": "done_gate",
                        "ok": False,
                        "detail": "completion still blocked",
                    },
                ],
                wi_dir=spec_dir,
            )
        return CloseCheckResult(
            ok=True,
            blockers=[],
            checks=[
                {
                    "name": "tasks_completion",
                    "ok": True,
                    "detail": "all checklist items done",
                },
                {
                    "name": "git_closure",
                    "ok": True,
                    "detail": "latest batch marked committed and working tree clean",
                },
                {
                    "name": "done_gate",
                    "ok": True,
                    "detail": "all close checks passed",
                },
            ],
            wi_dir=spec_dir,
        )

    monkeypatch.setattr("ai_sdlc.core.close_check.run_close_check", _fake_run_close_check)
    monkeypatch.setattr(
        ProgramService,
        "_run_truth_check_ref",
        lambda self, ref: {
            "ok": True,
            "classification": "merged_implemented",
            "detail": "",
            "error": None,
        },
    )
    monkeypatch.setattr(
        ProgramService,
        "_run_verify_ref",
        lambda self, ref, *, constraint_report: {
            "ok": True,
            "command": ref,
            "blockers": [],
            "warnings": [],
        },
    )

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)
    svc.write_truth_snapshot(snapshot)

    dirty_git = False
    updated_manifest = svc.load_manifest()
    surface = svc.build_truth_ledger_surface(updated_manifest)

    assert surface is not None
    assert surface["snapshot_state"] == "fresh"
    assert surface["state"] == snapshot.state


def test_build_truth_ledger_surface_ignores_truth_check_revision_metadata_drift(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(tmp_path)
    _commit_truth_repo(tmp_path, "seed truth ledger revision metadata drift fixture")

    base_truth_result = {
        "ok": True,
        "classification": "branch_only_implemented",
        "detail": "requested revision contains execution evidence or implementation changes, but it is not yet contained in main",
        "requested_revision": "HEAD",
        "resolved_revision": "abc1234",
        "head_revision": "abc1234",
        "current_branch": "feature/truth-sync",
        "head_matches_revision": True,
        "contained_in_main": False,
        "ahead_of_main": 1,
        "behind_of_main": 0,
        "wi_path": "specs/082-frontend-example",
        "formal_docs": {
            "spec_md": True,
            "plan_md": True,
            "tasks_md": True,
            "task_execution_log_md": True,
        },
        "execution_started": True,
        "changed_paths": [
            "specs/082-frontend-example/task-execution-log.md",
            "src/app.py",
        ],
        "code_paths": ["src/app.py"],
        "test_paths": [],
        "doc_paths": ["specs/082-frontend-example/task-execution-log.md"],
        "other_paths": [],
        "error": None,
    }

    svc = ProgramService(tmp_path)
    monkeypatch.setattr(
        svc,
        "_run_truth_check_ref",
        lambda ref: dict(base_truth_result),
    )
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)
    svc.write_truth_snapshot(snapshot)

    drifted_truth_result = dict(base_truth_result)
    drifted_truth_result.update(
        {
            "resolved_revision": "def5678",
            "head_revision": "def5678",
            "current_branch": "codex/truth-sync",
            "head_matches_revision": False,
            "ahead_of_main": 2,
            "changed_paths": [
                "program-manifest.yaml",
                "specs/082-frontend-example/task-execution-log.md",
                "src/app.py",
            ],
            "other_paths": ["program-manifest.yaml"],
        }
    )
    monkeypatch.setattr(
        svc,
        "_run_truth_check_ref",
        lambda ref: dict(drifted_truth_result),
    )

    updated_manifest = svc.load_manifest()
    surface = svc.build_truth_ledger_surface(updated_manifest)

    assert surface is not None
    assert surface["snapshot_state"] == "fresh"
    assert surface["state"] == snapshot.state


def test_build_truth_snapshot_blocks_release_scope_when_closure_audit_missing(
    tmp_path: Path,
) -> None:
    _init_truth_git_repo(tmp_path)
    (tmp_path / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
    (tmp_path / ".ai-sdlc" / "project" / "config" / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n---\nfrontend_evidence_class: \"framework_capability\"\n---\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (spec_dir / "task-execution-log.md").write_text(
        "# Log\n\n统一验证命令\n代码审查\n任务/计划同步状态\n",
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir(parents=True)
    (tmp_path / "src" / "app.py").write_text("print('demo')\n", encoding="utf-8")
    _write_truth_ledger_manifest(tmp_path)
    _commit_truth_repo(tmp_path, "seed truth ledger missing closure audit fixture")

    svc = ProgramService(tmp_path)
    manifest = svc.load_manifest()
    snapshot = svc.build_truth_snapshot(manifest)

    capability = snapshot.computed_capabilities[0]
    assert capability.audit_state == "blocked"
    assert "capability_closure_audit:missing" in capability.blocking_refs


def test_build_frontend_managed_delivery_apply_request_blocks_on_host_ingress(
    initialized_project_dir: Path,
) -> None:
    save_project_config(
        initialized_project_dir,
        ProjectConfig(adapter_ingress_state="materialized"),
    )
    request_path = _write_managed_delivery_apply_request(initialized_project_dir)
    svc = ProgramService(initialized_project_dir)

    request = svc.build_frontend_managed_delivery_apply_request(request_path)

    assert request.required is True
    assert request.apply_state == "blocked_before_start"
    assert "host_ingress_below_mutate_threshold" in request.remaining_blockers


def test_build_frontend_managed_delivery_apply_request_materializes_public_bundle_from_truth(
    initialized_project_dir: Path,
    monkeypatch,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_builtin_delivery_truth(root)
    monkeypatch.setattr(
        program_service_module,
        "evaluate_current_host_runtime",
        lambda project_root: _build_host_runtime_plan_for_tests(
            node_runtime_available=True,
            package_manager_available=True,
            playwright_browsers_available=True,
        ),
    )
    svc = ProgramService(root)

    request = svc.build_frontend_managed_delivery_apply_request()

    assert request.request_source_path == ".ai-sdlc/memory/frontend-managed-delivery/latest.yaml"
    assert request.apply_state == "ready_to_execute"
    assert request.execution_view is not None
    dependency_action = next(
        action
        for action in request.execution_view.action_items
        if action.action_type == "dependency_install"
    )
    assert dependency_action.executor_payload["install_strategy_id"] == "public-primevue-default"
    assert dependency_action.executor_payload["package_manager"] == "pnpm"
    assert dependency_action.executor_payload["packages"] == [
        "primevue",
        "@primeuix/themes",
    ]
    workspace_action = next(
        action
        for action in request.execution_view.action_items
        if action.action_type == "workspace_integration"
    )
    assert workspace_action.required is False
    assert workspace_action.default_selected is False


def test_build_frontend_managed_delivery_apply_request_uses_builtin_provider_truth_when_artifacts_missing(
    initialized_project_dir: Path,
    monkeypatch,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    monkeypatch.setattr(
        program_service_module,
        "evaluate_current_host_runtime",
        lambda project_root: _build_host_runtime_plan_for_tests(
            node_runtime_available=True,
            package_manager_available=True,
            playwright_browsers_available=True,
        ),
    )
    svc = ProgramService(root)

    request = svc.build_frontend_managed_delivery_apply_request()

    assert request.apply_state == "ready_to_execute"
    assert request.execution_view is not None
    dependency_action = next(
        action
        for action in request.execution_view.action_items
        if action.action_type == "dependency_install"
    )
    assert dependency_action.executor_payload["packages"] == [
        "primevue",
        "@primeuix/themes",
    ]


def test_build_frontend_managed_delivery_apply_request_blocks_enterprise_private_registry_prereq_from_truth(
    initialized_project_dir: Path,
    monkeypatch,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    snapshot = build_mvp_solution_snapshot(
        project_id="001-auth",
        effective_provider_id="enterprise-vue2",
        effective_style_pack_id="enterprise-default",
        requested_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        recommended_provider_id="enterprise-vue2",
        recommended_style_pack_id="enterprise-default",
        recommended_frontend_stack="vue2",
        requested_frontend_stack="vue2",
        effective_frontend_stack="vue2",
        availability_summary={
            "overall_status": "attention",
            "passed_check_ids": ["company-registry-network"],
            "failed_check_ids": ["company-registry-token"],
            "blocking_reason_codes": [],
        },
        availability_reason_text="Registry token missing.",
        preflight_status="warning",
        preflight_reason_codes=["company-registry-token"],
        style_fidelity_status="full",
    )
    _write_builtin_delivery_truth(root, snapshot=snapshot)
    monkeypatch.setattr(
        program_service_module,
        "evaluate_current_host_runtime",
        lambda project_root: _build_host_runtime_plan_for_tests(
            node_runtime_available=True,
            package_manager_available=True,
            playwright_browsers_available=True,
        ),
    )
    svc = ProgramService(root)

    request = svc.build_frontend_managed_delivery_apply_request()

    assert request.apply_state == "blocked_before_start"
    assert "private_registry_prerequisite_missing:company-registry-token" in request.remaining_blockers


def test_execute_frontend_managed_delivery_apply_returns_pending_browser_gate_success(
    initialized_project_dir: Path,
) -> None:
    save_project_config(
        initialized_project_dir,
        ProjectConfig(adapter_ingress_state="verified_loaded"),
    )
    request_path = _write_artifact_generate_apply_request(initialized_project_dir)
    svc = ProgramService(initialized_project_dir)
    request = svc.build_frontend_managed_delivery_apply_request(request_path)

    result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=request,
        confirmed=True,
    )

    assert result.passed is True
    assert result.result_status == "apply_succeeded_pending_browser_gate"
    assert "delivery is not complete" in result.headline.lower()
    assert "browser gate has not run" in result.headline.lower()
    assert (
        initialized_project_dir / "managed" / "frontend" / "src" / "App.vue"
    ).read_text(encoding="utf-8") == "<template>generated</template>\n"


def test_build_frontend_managed_delivery_apply_request_surfaces_executor_preflight_blockers(
    initialized_project_dir: Path,
) -> None:
    save_project_config(
        initialized_project_dir,
        ProjectConfig(adapter_ingress_state="verified_loaded"),
    )
    request_path = _write_blocked_managed_delivery_apply_request(initialized_project_dir)
    svc = ProgramService(initialized_project_dir)

    request = svc.build_frontend_managed_delivery_apply_request(request_path)

    assert request.apply_state == "blocked_before_start"
    assert "artifact_generate_outside_managed_target" in request.remaining_blockers


def test_write_frontend_managed_delivery_apply_artifact_persists_browser_gate_handoff_input(
    initialized_project_dir: Path,
) -> None:
    save_project_config(
        initialized_project_dir,
        ProjectConfig(adapter_ingress_state="verified_loaded"),
    )
    request_path = _write_artifact_generate_apply_request(initialized_project_dir)
    svc = ProgramService(initialized_project_dir)
    request = svc.build_frontend_managed_delivery_apply_request(request_path)
    result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=request,
        result=result,
        generated_at="2026-04-14T04:00:00Z",
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))

    assert payload["result_status"] == "apply_succeeded_pending_browser_gate"
    assert payload["browser_gate_required"] is True
    assert payload["execution_view"]["spec_dir"] == "specs/001-auth"
    assert (
        payload["source_linkage"]["managed_delivery_apply_artifact_path"]
        == ".ai-sdlc/memory/frontend-managed-delivery-apply/latest.yaml"
    )


def test_write_frontend_managed_delivery_apply_artifact_keeps_materialized_request_schema_separate(
    initialized_project_dir: Path,
    monkeypatch,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_builtin_delivery_truth(root)
    monkeypatch.setattr(
        program_service_module,
        "evaluate_current_host_runtime",
        lambda project_root: _build_host_runtime_plan_for_tests(
            node_runtime_available=True,
            package_manager_available=True,
            playwright_browsers_available=True,
        ),
    )
    svc = ProgramService(root)
    request = svc.build_frontend_managed_delivery_apply_request()
    result = svc.execute_frontend_managed_delivery_apply(
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_managed_delivery_apply_artifact(
        request=request,
        result=result,
        generated_at="2026-04-14T04:00:00Z",
    )

    request_path = root / ".ai-sdlc" / "memory" / "frontend-managed-delivery" / "latest.yaml"
    request_payload = yaml.safe_load(request_path.read_text(encoding="utf-8"))
    apply_payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))

    assert artifact_path != request_path
    assert "request_id" in request_payload
    assert "result_status" not in request_payload
    assert apply_payload["request_source_path"] == ".ai-sdlc/memory/frontend-managed-delivery/latest.yaml"
    assert (
        artifact_path
        == root / ".ai-sdlc" / "memory" / "frontend-managed-delivery-apply" / "latest.yaml"
    )


def test_build_frontend_browser_gate_probe_request_requires_apply_artifact(
    initialized_project_dir: Path,
) -> None:
    svc = ProgramService(initialized_project_dir)

    request = svc.build_frontend_browser_gate_probe_request()

    assert request.probe_state == "missing_apply_artifact"
    assert "managed_delivery_apply_artifact_missing" in request.remaining_blockers


def test_build_frontend_browser_gate_probe_request_accepts_legacy_apply_artifact_path_for_upgrade_compat(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    legacy_apply_artifact_path = root / ".ai-sdlc" / "memory" / "frontend-managed-delivery" / "latest.yaml"
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        output_path=legacy_apply_artifact_path,
        generated_at="2026-04-14T04:00:00Z",
    )

    probe_request = svc.build_frontend_browser_gate_probe_request()

    assert probe_request.probe_state == "ready_to_execute"
    assert probe_request.apply_artifact_path == ".ai-sdlc/memory/frontend-managed-delivery/latest.yaml"


def test_execute_frontend_browser_gate_probe_materializes_gate_run_bundle(
    initialized_project_dir: Path,
) -> None:
    save_project_config(
        initialized_project_dir,
        ProjectConfig(adapter_ingress_state="verified_loaded"),
    )
    _write_frontend_solution_confirmation_artifacts(initialized_project_dir)
    _write_frontend_visual_a11y_evidence(
        initialized_project_dir / "specs" / "001-auth",
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-visual-pass",
                target_id="user-create",
                surface_id="page:user-create",
                outcome="pass",
                report_type="coverage-report",
                severity="info",
            )
        ],
    )
    request_path = _write_artifact_generate_apply_request(initialized_project_dir)
    svc = ProgramService(initialized_project_dir)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )

    probe_request = svc.build_frontend_browser_gate_probe_request()
    preview_root = (
        initialized_project_dir
        / ".ai-sdlc"
        / "artifacts"
        / "frontend-browser-gate"
        / "gate-run-preview"
    )
    probe_result = svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )

    assert probe_request.probe_state == "ready_to_execute"
    assert probe_request.overall_gate_status_preview == "incomplete"
    assert not preview_root.exists()
    assert probe_result.passed is True
    assert probe_result.overall_gate_status == "incomplete"
    artifact_path = initialized_project_dir / probe_result.artifact_path
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    gate_run_id = payload["gate_run_id"]
    assert gate_run_id.startswith("gate-run-")
    assert payload["runtime_session"]["artifact_root_ref"].endswith(gate_run_id)
    assert all(
        gate_run_id in record["artifact_ref"] for record in payload["artifact_records"]
    )
    assert (
        payload["bundle_input"]["gate_run_id"] == gate_run_id
    )
    assert payload["bundle_input"]["overall_gate_status"] == "incomplete"


def test_build_integration_dry_run_uses_browser_gate_recheck_command_when_gate_artifact_exists(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )

    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_recheck_handoff is None
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert remediation.state == "required"
    assert "visual_expectation_evidence_missing" in remediation.fix_inputs
    assert "basic_a11y_evidence_missing" in remediation.fix_inputs
    assert (
        "materialize browser gate visual / a11y probe evidence"
        in remediation.suggested_actions
    )
    assert remediation.recommended_commands == [
        "uv run ai-sdlc program browser-gate-probe --execute",
        "uv run ai-sdlc verify constraints",
    ]


def test_build_status_fails_closed_when_browser_gate_artifact_scope_drift_detected(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    probe_result = svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )
    artifact_path = root / probe_result.artifact_path
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    payload["bundle_input"]["spec_dir"] = "specs/002-course"
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "scope_or_linkage_invalid"


def test_build_status_fails_closed_when_browser_gate_latest_artifact_is_invalid_yaml(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    latest_path = (
        root / ".ai-sdlc" / "memory" / "frontend-browser-gate" / "latest.yaml"
    )
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text("not: [valid\n", encoding="utf-8")

    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "scope_or_linkage_invalid"
    assert any("frontend_browser_gate_artifact_invalid" in blocker for blocker in readiness.blockers)


def test_build_status_fails_closed_when_current_apply_truth_drift_detected(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    apply_artifact_path = svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )

    apply_payload = yaml.safe_load(apply_artifact_path.read_text(encoding="utf-8"))
    apply_payload["apply_result_id"] = "apply-result-drifted"
    apply_artifact_path.write_text(
        yaml.safe_dump(apply_payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "scope_or_linkage_invalid"
    assert any("current_truth_drift" in blocker for blocker in readiness.blockers)


def test_build_integration_dry_run_surfaces_browser_gate_remediation_follow_up_command(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    _write_frontend_visual_a11y_evidence(
        root / "specs" / "001-auth",
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-visual-a11y-issue",
                target_id="user-create",
                surface_id="success-feedback",
                outcome="issue",
                report_type="violation-report",
                severity="medium",
                location_anchor="feedback.banner",
                quality_hint="review success feedback visibility and semantics",
                changed_scope_explanation="071 issue fixture",
            )
        ],
    )
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    probe_result = svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )
    artifact_path = root / probe_result.artifact_path
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    payload["overall_gate_status"] = "blocked"
    payload["bundle_input"]["overall_gate_status"] = "blocked"
    for receipt in payload["bundle_input"]["check_receipts"]:
        if receipt["check_name"] in {"playwright_smoke", "interaction_anti_pattern_checks"}:
            receipt["classification_candidate"] = "pass"
            receipt["recheck_required"] = False
            receipt["blocking_reason_codes"] = []
            receipt["remediation_hints"] = []
            receipt["runtime_status"] = "completed"
        else:
            receipt["classification_candidate"] = "actual_quality_blocker"
            receipt["blocking_reason_codes"] = ["visual_a11y_quality_blocker"]
            receipt["remediation_hints"] = [
                "review frontend visual / a11y issue findings"
            ]
    payload["bundle_input"]["blocking_reason_codes"] = ["visual_a11y_quality_blocker"]
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_issue_review" in remediation.fix_inputs
    assert "uv run ai-sdlc program browser-gate-probe --execute" in remediation.recommended_commands
    assert remediation.recommended_commands[-1] == "uv run ai-sdlc verify constraints"


def test_build_integration_dry_run_skips_browser_gate_recheck_handoff_when_artifact_is_ready(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    _write_frontend_visual_a11y_evidence(
        root / "specs" / "001-auth",
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-visual-a11y-pass",
                target_id="user-create",
                surface_id="page:user-create",
                outcome="pass",
                report_type="coverage-report",
                severity="info",
                location_anchor="specs",
                quality_hint="fixture evidence",
                changed_scope_explanation="071 pass fixture",
            )
        ],
    )
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    probe_result = svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )
    artifact_path = root / probe_result.artifact_path
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    payload["overall_gate_status"] = "passed"
    payload["bundle_input"]["overall_gate_status"] = "passed"
    for receipt in payload["bundle_input"]["check_receipts"]:
        receipt["classification_candidate"] = "pass"
        receipt["recheck_required"] = False
        receipt["blocking_reason_codes"] = []
        receipt["remediation_hints"] = []
        receipt["runtime_status"] = "completed"
    payload["bundle_input"]["blocking_reason_codes"] = []
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_recheck_handoff is None


def test_execute_frontend_remediation_runbook_stays_incomplete_when_browser_gate_recheck_remains(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    _write_frontend_visual_a11y_evidence(
        root / "specs" / "001-auth",
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-visual-a11y-issue",
                target_id="user-create",
                surface_id="success-feedback",
                outcome="issue",
                report_type="violation-report",
                severity="medium",
                location_anchor="feedback.banner",
                quality_hint="review success feedback visibility and semantics",
                changed_scope_explanation="071 issue fixture",
            )
        ],
    )
    request_path = _write_artifact_generate_apply_request(root)
    svc = ProgramService(root)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T04:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    probe_result = svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T04:05:00Z",
    )
    artifact_path = root / probe_result.artifact_path
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    payload["overall_gate_status"] = "blocked"
    payload["bundle_input"]["overall_gate_status"] = "blocked"
    for receipt in payload["bundle_input"]["check_receipts"]:
        if receipt["check_name"] in {"playwright_smoke", "interaction_anti_pattern_checks"}:
            receipt["classification_candidate"] = "pass"
            receipt["recheck_required"] = False
            receipt["blocking_reason_codes"] = []
            receipt["remediation_hints"] = []
            receipt["runtime_status"] = "completed"
        else:
            receipt["classification_candidate"] = "actual_quality_blocker"
            receipt["blocking_reason_codes"] = ["visual_a11y_quality_blocker"]
            receipt["remediation_hints"] = [
                "review frontend visual / a11y issue findings"
            ]
    payload["bundle_input"]["blocking_reason_codes"] = ["visual_a11y_quality_blocker"]
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    result = svc.execute_frontend_remediation_runbook(_manifest())

    assert result.passed is False
    assert result.blockers


def test_execute_frontend_browser_gate_probe_treats_runner_success_with_missing_artifact_as_recheck_required(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
    _write_frontend_solution_confirmation_artifacts(root)
    _write_frontend_visual_a11y_evidence(
        root / "specs" / "001-auth",
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-visual-a11y-pass",
                target_id="page:user-create",
                surface_id="page:user-create",
                outcome="pass",
                report_type="coverage-report",
                severity="info",
                location_anchor="specs",
                quality_hint="fixture evidence",
                changed_scope_explanation="143 pass fixture",
            )
        ],
    )
    request_path = _write_artifact_generate_apply_request(root)

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult(
            runtime_status="completed",
            shared_capture=BrowserGateSharedRuntimeCapture(
                gate_run_id=execution_context.gate_run_id,
                trace_artifact_ref=str(
                    (artifact_root / "shared-runtime" / "playwright-trace.zip").relative_to(
                        root
                    )
                ),
                navigation_screenshot_ref=str(screenshot_path.relative_to(root)),
                capture_status="captured",
                final_url="http://localhost:4173/",
                anchor_refs=["page:landing"],
                diagnostic_codes=[],
            ),
            interaction_capture=BrowserGateInteractionProbeCapture(
                gate_run_id=execution_context.gate_run_id,
                interaction_probe_id="primary-action",
                artifact_refs=[str(interaction_path.relative_to(root))],
                capture_status="captured",
                classification_candidate="pass",
                blocking_reason_codes=[],
                anchor_refs=["interaction:primary-action"],
            ),
            diagnostic_codes=[],
            warnings=[],
        )

    svc = ProgramService(root, browser_gate_probe_runner=_runner)
    apply_request = svc.build_frontend_managed_delivery_apply_request(request_path)
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request_path,
        request=apply_request,
        confirmed=True,
    )
    svc.write_frontend_managed_delivery_apply_artifact(
        request_path,
        request=apply_request,
        result=apply_result,
        generated_at="2026-04-14T15:00:00Z",
    )
    probe_request = svc.build_frontend_browser_gate_probe_request()
    probe_result = svc.execute_frontend_browser_gate_probe(
        request=probe_request,
        generated_at="2026-04-14T15:05:00Z",
    )

    assert probe_result.execute_gate_state == "recheck_required"
    assert probe_result.decision_reason == "evidence_missing"


def test_validate_manifest_cycle(tmp_path: Path) -> None:
    (tmp_path / "specs" / "a").mkdir(parents=True)
    (tmp_path / "specs" / "b").mkdir(parents=True)
    mf = ProgramManifest(
        specs=[
            ProgramSpecRef(id="a", path="specs/a", depends_on=["b"]),
            ProgramSpecRef(id="b", path="specs/b", depends_on=["a"]),
        ]
    )
    svc = ProgramService(tmp_path)
    res = svc.validate_manifest(mf)
    assert res.valid is False
    assert any("cycle" in e for e in res.errors)


def test_validate_manifest_frontend_evidence_class_mirror_missing(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                )
            ]
        )
    )

    assert res.valid is False
    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in err
        and "error_kind=mirror_missing" in err
        for err in res.errors
    )


def test_validate_manifest_frontend_evidence_class_mirror_invalid_value(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                    frontend_evidence_class="framework",
                )
            ]
        )
    )

    assert res.valid is False
    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in err
        and "error_kind=mirror_invalid_value" in err
        for err in res.errors
    )


def test_validate_manifest_frontend_evidence_class_mirror_stale(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                    frontend_evidence_class="consumer_adoption",
                )
            ]
        )
    )

    assert res.valid is False
    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in err
        and "error_kind=mirror_stale" in err
        for err in res.errors
    )


def test_validate_manifest_frontend_evidence_class_mirror_valid(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                    frontend_evidence_class="framework_capability",
                )
            ]
        )
    )

    assert res.valid is True
    assert res.errors == []


def test_validate_manifest_ignores_frontend_evidence_class_drift_for_non_frontend_spec(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/050-non-frontend",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="050-non-frontend",
                    path="specs/050-non-frontend",
                    depends_on=[],
                )
            ]
        )
    )

    assert res.valid is True
    assert res.errors == []


def test_validate_manifest_rejects_spec_path_outside_project_root(
    tmp_path: Path,
) -> None:
    legacy_dir = tmp_path.parent / "legacy-spec"
    legacy_dir.mkdir(exist_ok=True)
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path=f"../{legacy_dir.name}",
                    depends_on=[],
                )
            ]
        )
    )

    assert res.valid is False
    assert any("path outside project root" in err for err in res.errors)


def test_sync_frontend_evidence_class_manifest_execute_targeted(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
    owner: "team-a"
  - id: "050-non-frontend"
    path: "specs/050-non-frontend"
    depends_on: []
    owner: "team-b"
""",
    )
    (tmp_path / "specs" / "050-non-frontend").mkdir(parents=True, exist_ok=True)
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        spec_id="082-frontend-example",
        confirmed=True,
    )

    assert result.passed is True
    assert result.sync_result == "updated"
    assert result.updated_specs == ["082-frontend-example"]

    payload = yaml.safe_load((tmp_path / "program-manifest.yaml").read_text(encoding="utf-8"))
    specs = {item["id"]: item for item in payload["specs"]}
    assert specs["082-frontend-example"]["frontend_evidence_class"] == "framework_capability"
    assert specs["082-frontend-example"]["owner"] == "team-a"
    assert "frontend_evidence_class" not in specs["050-non-frontend"]
    assert specs["050-non-frontend"]["owner"] == "team-b"


def test_sync_frontend_evidence_class_manifest_execute_bulk(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/083-frontend-adoption",
        frontend_evidence_class="consumer_adoption",
    )
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
  - id: "083-frontend-adoption"
    path: "specs/083-frontend-adoption"
    depends_on: []
    frontend_evidence_class: "framework_capability"
""",
    )
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        confirmed=True,
    )

    assert result.passed is True
    assert result.sync_result == "updated"
    assert result.updated_specs == [
        "082-frontend-example",
        "083-frontend-adoption",
    ]

    payload = yaml.safe_load((tmp_path / "program-manifest.yaml").read_text(encoding="utf-8"))
    specs = {item["id"]: item for item in payload["specs"]}
    assert specs["082-frontend-example"]["frontend_evidence_class"] == "framework_capability"
    assert specs["083-frontend-adoption"]["frontend_evidence_class"] == "consumer_adoption"


def test_sync_frontend_evidence_class_manifest_blocks_when_footer_missing(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
""",
    )
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.sync_result == "blocked"
    assert result.updated_specs == []
    assert any("082-frontend-example" in blocker for blocker in result.remaining_blockers)


def test_sync_frontend_evidence_class_manifest_uses_only_terminal_footer(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        "Example body block:\n\n"
        "```md\n"
        "---\n"
        'example_frontend_evidence_class: "framework_capability"\n'
        "---\n"
        "```\n\n"
        "Terminal footer is canonical.\n\n"
        "---\n"
        'frontend_evidence_class: "consumer_adoption"\n'
        "---\n",
        encoding="utf-8",
    )
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
""",
    )
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        confirmed=True,
    )

    assert result.passed is True
    assert result.sync_result == "updated"
    assert result.updated_specs == ["082-frontend-example"]

    payload = yaml.safe_load((tmp_path / "program-manifest.yaml").read_text(encoding="utf-8"))
    specs = {item["id"]: item for item in payload["specs"]}
    assert specs["082-frontend-example"]["frontend_evidence_class"] == "consumer_adoption"


def test_sync_frontend_evidence_class_manifest_blocks_bulk_invalid_non_checkpoint_spec(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-checkpoint",
        frontend_evidence_class="framework_capability",
    )
    spec_dir = tmp_path / "specs" / "083-frontend-invalid"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        "---\n"
        'frontend_evidence_class: "framework_capability"\n'
        'frontend_evidence_class: "consumer_adoption"\n'
        "---\n",
        encoding="utf-8",
    )
    save_checkpoint(
        tmp_path,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id="082",
                spec_dir="specs/082-frontend-checkpoint",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        ),
    )
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-checkpoint"
    path: "specs/082-frontend-checkpoint"
    depends_on: []
  - id: "083-frontend-invalid"
    path: "specs/083-frontend-invalid"
    depends_on: []
""",
    )
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.sync_result == "blocked"
    assert result.updated_specs == []
    assert any("083-frontend-invalid/spec.md" in blocker for blocker in result.remaining_blockers)
    assert any("error_kind=duplicate_key" in blocker for blocker in result.remaining_blockers)


def test_topo_tiers(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    svc = ProgramService(tmp_path)
    tiers = svc.topo_tiers(_manifest())
    assert tiers[0] == ["001-auth", "002-course"]
    assert tiers[1] == ["003-enroll"]


def test_build_status_counts_and_blockers(tmp_path: Path) -> None:
    auth = tmp_path / "specs" / "001-auth"
    course = tmp_path / "specs" / "002-course"
    enroll = tmp_path / "specs" / "003-enroll"
    for p in (auth, course, enroll):
        p.mkdir(parents=True)

    (auth / "spec.md").write_text("# spec\n", encoding="utf-8")
    (auth / "plan.md").write_text("# plan\n", encoding="utf-8")
    (auth / "tasks.md").write_text("- [x] done\n- [ ] todo\n", encoding="utf-8")

    (course / "development-summary.md").write_text("ok\n", encoding="utf-8")

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    assert by["001-auth"].completed_tasks == 1
    assert by["001-auth"].total_tasks == 2
    assert by["002-course"].stage_hint == "close"
    assert by["003-enroll"].blocked_by == ["001-auth"]


def test_build_status_surfaces_frontend_evidence_class_bounded_summary(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest(
        specs=[
            ProgramSpecRef(
                id="082-frontend-example",
                path="specs/082-frontend-example",
                depends_on=[],
            )
        ]
    )

    rows = svc.build_status(
        manifest,
        validation_result=svc.validate_manifest(manifest),
    )

    assert len(rows) == 1
    summary = rows[0].frontend_evidence_class_status
    assert summary is not None
    assert summary.has_blocker is True
    assert summary.problem_family == "frontend_evidence_class_mirror_drift"
    assert summary.detection_surface == "program validate"
    assert summary.summary_token == "mirror_missing"


def test_build_status_scans_each_manifest_spec_for_frontend_evidence_authoring_blockers(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-valid",
        frontend_evidence_class="framework_capability",
    )
    invalid_spec_dir = tmp_path / "specs" / "083-frontend-invalid"
    invalid_spec_dir.mkdir(parents=True, exist_ok=True)
    (invalid_spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        'frontend_evidence_class: "framework_capability"\n\n'
        "---\n"
        'frontend_evidence_class: "consumer_adoption"\n'
        "---\n",
        encoding="utf-8",
    )
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest(
        specs=[
            ProgramSpecRef(
                id="082-frontend-valid",
                path="specs/082-frontend-valid",
                depends_on=[],
                frontend_evidence_class="framework_capability",
            ),
            ProgramSpecRef(
                id="083-frontend-invalid",
                path="specs/083-frontend-invalid",
                depends_on=[],
                frontend_evidence_class="consumer_adoption",
            ),
        ]
    )

    rows = svc.build_status(manifest)
    by_id = {row.spec_id: row for row in rows}

    assert by_id["082-frontend-valid"].frontend_evidence_class_status is None
    invalid_summary = by_id["083-frontend-invalid"].frontend_evidence_class_status
    assert invalid_summary is not None
    assert invalid_summary.has_blocker is True
    assert (
        invalid_summary.problem_family
        == "frontend_evidence_class_authoring_malformed"
    )
    assert invalid_summary.detection_surface == "verify constraints"
    assert invalid_summary.summary_token == "body_footer_conflict"


def test_build_status_surfaces_shared_spec_path_blockers_for_all_manifest_rows(
    tmp_path: Path,
) -> None:
    invalid_spec_dir = tmp_path / "specs" / "082-frontend-shared"
    invalid_spec_dir.mkdir(parents=True, exist_ok=True)
    (invalid_spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        'frontend_evidence_class: "framework_capability"\n\n'
        "---\n"
        'frontend_evidence_class: "consumer_adoption"\n'
        "---\n",
        encoding="utf-8",
    )
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest(
        specs=[
            ProgramSpecRef(
                id="082-frontend-shared-a",
                path="specs/082-frontend-shared",
                depends_on=[],
                frontend_evidence_class="framework_capability",
            ),
            ProgramSpecRef(
                id="082-frontend-shared-b",
                path="specs/082-frontend-shared",
                depends_on=[],
                frontend_evidence_class="framework_capability",
            ),
        ]
    )

    rows = svc.build_status(manifest)
    by_id = {row.spec_id: row for row in rows}

    for spec_id in ("082-frontend-shared-a", "082-frontend-shared-b"):
        summary = by_id[spec_id].frontend_evidence_class_status
        assert summary is not None
        assert summary.has_blocker is True
        assert (
            summary.problem_family
            == "frontend_evidence_class_authoring_malformed"
        )
        assert summary.detection_surface == "verify constraints"
        assert summary.summary_token == "body_footer_conflict"


def test_build_status_treats_spec_path_outside_project_root_as_missing(
    tmp_path: Path,
) -> None:
    legacy_dir = tmp_path.parent / "legacy-spec"
    legacy_dir.mkdir(exist_ok=True)
    svc = ProgramService(tmp_path)
    manifest = ProgramManifest(
        specs=[
            ProgramSpecRef(
                id="082-frontend-example",
                path=f"../{legacy_dir.name}",
                depends_on=[],
            )
        ]
    )

    rows = svc.build_status(
        manifest,
        validation_result=svc.validate_manifest(manifest),
    )

    assert len(rows) == 1
    assert rows[0].exists is False
    assert rows[0].stage_hint == "missing"


def test_build_integration_dry_run(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    (tmp_path / "specs" / "001-auth" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    (tmp_path / "specs" / "002-course" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())
    assert len(plan.steps) == 3
    assert plan.steps[0].tier == 0
    assert plan.steps[2].spec_id == "003-enroll"
    assert plan.steps[2].tier == 1


def test_build_integration_dry_run_surfaces_frontend_recheck_handoff_when_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    handoff = step.frontend_recheck_handoff
    assert handoff is not None
    assert handoff.required is True
    assert "re-run frontend verification after execute" in handoff.reason
    assert handoff.recommended_commands == ["uv run ai-sdlc verify constraints"]
    assert handoff.source_linkage["frontend_gate_verdict"] == "PASS"


def test_build_integration_dry_run_skips_frontend_recheck_handoff_when_not_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_recheck_handoff is None


def test_build_integration_dry_run_surfaces_frontend_remediation_input_when_not_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert remediation.state == "required"
    assert "frontend_contract_observations" in remediation.fix_inputs
    assert "materialize frontend contract observations" in remediation.suggested_actions
    assert (
        "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
        in remediation.recommended_commands
    )
    assert remediation.recommended_commands[-1] == "uv run ai-sdlc verify constraints"
    assert remediation.source_linkage["runtime_attachment_status"] == "missing_artifact"


def test_build_integration_dry_run_skips_frontend_remediation_input_when_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_remediation_input is None


def test_build_integration_dry_run_binds_governance_materialization_command_when_gaps_present(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_gate_policy_artifacts" in remediation.fix_inputs
    assert (
        "uv run ai-sdlc rules materialize-frontend-mvp"
        in remediation.recommended_commands
    )
    assert remediation.recommended_commands[-1] == "uv run ai-sdlc verify constraints"


def test_build_frontend_remediation_runbook_collects_action_commands_and_follow_up_verify(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_frontend_contract_source_annotation(tmp_path)
    for spec in ("002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    runbook = svc.build_frontend_remediation_runbook(_manifest())

    assert [step.spec_id for step in runbook.steps] == [
        "001-auth",
        "002-course",
        "003-enroll",
    ]
    assert (
        "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
        in runbook.action_commands
    )
    assert "uv run ai-sdlc rules materialize-frontend-mvp" in runbook.action_commands
    assert runbook.follow_up_commands == ["uv run ai-sdlc verify constraints"]


def test_build_frontend_remediation_runbook_keeps_visual_a11y_policy_artifact_gaps_in_remediation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).unlink()
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    runbook = svc.build_frontend_remediation_runbook(_manifest())

    assert [step.spec_id for step in runbook.steps] == [
        "001-auth",
        "002-course",
        "003-enroll",
    ]
    assert all(
        "frontend_visual_a11y_policy_artifacts" in step.fix_inputs
        for step in runbook.steps
    )
    assert runbook.action_commands == ["uv run ai-sdlc rules materialize-frontend-mvp"]
    assert runbook.follow_up_commands == ["uv run ai-sdlc verify constraints"]


def test_execute_frontend_remediation_runbook_materializes_bounded_commands_and_verifies(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_constitution(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_frontend_contract_source_annotation(tmp_path)
    for spec in ("002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_remediation_runbook(
        _manifest(),
        generated_at="2026-04-03T17:30:00Z",
    )

    assert result.passed is False
    assert not observation_artifact_path(tmp_path / "specs" / "001-auth").is_file()
    assert (tmp_path / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).is_file()
    assert (
        tmp_path / "governance" / "frontend" / "generation" / "generation.manifest.yaml"
    ).is_file()
    assert any(
        item.command
        == "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
        and item.status == "failed"
        and "explicit <frontend-source-root> required" in item.summary
        for item in result.command_results
    )
    assert any(
        item.command == "uv run ai-sdlc rules materialize-frontend-mvp"
        and item.status == "executed"
        for item in result.command_results
    )
    assert all(
        item.command != "uv run ai-sdlc verify constraints"
        for item in result.command_results
    )
    assert any(
        "explicit <frontend-source-root> required" in blocker
        for blocker in result.blockers
    )


def test_execute_frontend_remediation_runbook_passes_when_only_visual_a11y_policy_artifact_gap_remains(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_constitution(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).unlink()
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        spec_dir = tmp_path / "specs" / spec
        _write_frontend_contract_observations(spec_dir)
        _write_frontend_visual_a11y_evidence(
            spec_dir,
            [
                FrontendVisualA11yEvidenceEvaluation(
                    evaluation_id=f"{spec}-visual-a11y-pass",
                    target_id="user-create",
                    surface_id="page:user-create",
                    outcome="pass",
                    report_type="coverage-report",
                    severity="info",
                    location_anchor="specs",
                    quality_hint="fixture evidence",
                    changed_scope_explanation="071 pass fixture",
                )
            ],
        )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_remediation_runbook(
        _manifest(),
        generated_at="2026-04-07T16:00:00Z",
    )

    assert result.passed is True
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).is_file()
    assert any(
        item.command == "uv run ai-sdlc rules materialize-frontend-mvp"
        and item.status == "executed"
        for item in result.command_results
    )
    assert any(
        item.command == "uv run ai-sdlc verify constraints"
        and item.status == "passed"
        for item in result.command_results
    )
    assert result.blockers == []


def test_write_frontend_remediation_writeback_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_constitution(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_frontend_contract_source_annotation(tmp_path)
    for spec in ("002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    runbook = svc.build_frontend_remediation_runbook(_manifest())
    execution = svc.execute_frontend_remediation_runbook(
        _manifest(),
        generated_at="2026-04-03T16:00:00Z",
    )

    writeback_path = svc.write_frontend_remediation_writeback_artifact(
        _manifest(),
        runbook=runbook,
        execution_result=execution,
        generated_at="2026-04-03T16:00:00Z",
    )

    assert writeback_path == (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
    )
    payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
    assert payload["generated_at"] == "2026-04-03T16:00:00Z"
    assert payload["passed"] is False
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert any(
        "explicit <frontend-source-root> required" in blocker
        for blocker in payload["remaining_blockers"]
    )
    assert payload["follow_up_commands"] == ["uv run ai-sdlc verify constraints"]
    assert payload["written_paths"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert any(
        item["command"]
        == "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
        and item["status"] == "failed"
        for item in payload["command_results"]
    )


def test_write_frontend_remediation_writeback_artifact_reuses_provided_execution_result(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    execution = ProgramFrontendRemediationExecutionResult(
        passed=False,
        command_results=[
            ProgramFrontendRemediationCommandResult(
                command="sentinel-command",
                status="passed",
                written_paths=["sentinel/path.yaml"],
                summary="sentinel summary",
            )
        ],
        blockers=["sentinel blocker"],
    )

    writeback_path = svc.write_frontend_remediation_writeback_artifact(
        _manifest(),
        execution_result=execution,
        generated_at="2026-04-03T16:05:00Z",
    )

    payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
    assert payload["command_results"] == [
        {
            "command": "sentinel-command",
            "status": "passed",
            "written_paths": ["sentinel/path.yaml"],
            "blockers": [],
            "summary": "sentinel summary",
        }
    ]
    assert payload["remaining_blockers"] == ["sentinel blocker"]


def test_build_frontend_provider_handoff_packages_pending_inputs_from_writeback_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is True
    assert handoff.provider_execution_state == "not_started"
    assert (
        handoff.writeback_artifact_path
        == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    )
    assert handoff.writeback_generated_at == "2026-04-03T18:00:00Z"
    assert handoff.remaining_blockers == ["spec 001-auth remediation still required"]
    assert [step.spec_id for step in handoff.steps] == ["001-auth", "002-course"]
    assert handoff.steps[0].pending_inputs == ["frontend_contract_observations"]
    assert (
        handoff.steps[0].source_linkage["writeback_artifact_path"]
        == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    )
    assert (
        handoff.steps[0].source_linkage["provider_execution_state"] == "not_started"
    )


def test_build_frontend_provider_handoff_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "stable_empty_artifact",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert handoff.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert (
        handoff.steps[0].source_linkage["runtime_attachment_status"]
        == "stable_empty_artifact"
    )


def test_build_frontend_provider_handoff_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "artifact_attached",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert handoff.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert handoff.steps[0].source_linkage["runtime_attachment_status"] == (
        "artifact_attached"
    )


def test_build_frontend_provider_handoff_is_not_required_when_writeback_is_clean(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=True,
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is False
    assert handoff.provider_execution_state == "not_started"
    assert handoff.steps == []
    assert handoff.remaining_blockers == []


def test_build_frontend_provider_runtime_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.provider_execution_state == "not_started"
    assert request.handoff_source_path == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    assert request.handoff_generated_at == "2026-04-03T18:00:00Z"
    assert request.remaining_blockers == ["spec 001-auth remediation still required"]
    assert [step.spec_id for step in request.steps] == ["001-auth", "002-course"]
    assert request.steps[0].pending_inputs == ["frontend_contract_observations"]
    assert (
        request.steps[0].source_linkage["provider_runtime_state"] == "not_started"
    )


def test_build_frontend_provider_runtime_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "stable_empty_artifact",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert (
        request.steps[0].source_linkage["provider_runtime_state"] == "not_started"
    )


def test_build_frontend_provider_runtime_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "artifact_attached",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert (
        request.steps[0].source_linkage["provider_runtime_state"] == "not_started"
    )


def test_execute_frontend_provider_runtime_generates_patch_summaries_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_runtime(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.provider_execution_state == "completed"
    assert result.invocation_result == "patches_generated"
    assert result.patch_summaries == [
        "generated provider patch plan for 001-auth (pending_inputs=frontend_contract_observations)",
        "generated provider patch plan for 002-course (pending_inputs=frontend_gate_policy_artifacts)",
    ]
    assert result.remaining_blockers == []
    assert result.source_linkage["provider_runtime_state"] == "completed"


def test_write_frontend_provider_runtime_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())
    result = svc.execute_frontend_provider_runtime(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_provider_runtime_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["handoff_source_path"]
        == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    )
    assert payload["provider_execution_state"] == "completed"
    assert payload["invocation_result"] == "patches_generated"
    assert payload["confirmed"] is True
    assert payload["patch_summaries"] == [
        "generated provider patch plan for 001-auth (pending_inputs=frontend_contract_observations)",
        "generated provider patch plan for 002-course (pending_inputs=frontend_gate_policy_artifacts)",
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["provider_runtime_artifact_path"]
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )


def test_execute_frontend_provider_runtime_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_runtime(_manifest(), confirmed=True)

    assert result.provider_execution_state == "completed"
    assert not (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    ).exists()


def test_build_frontend_provider_patch_handoff_packages_runtime_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is True
    assert handoff.patch_availability_state == "patches_generated"
    assert (
        handoff.runtime_artifact_path
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )
    assert handoff.runtime_generated_at == "2026-04-03T19:00:00Z"
    assert handoff.patch_summaries == [
        "generated provider patch plan for 001-auth (pending_inputs=frontend_contract_observations)"
    ]
    assert handoff.remaining_blockers == []
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == ["frontend_contract_observations"]
    assert (
        handoff.steps[0].source_linkage["provider_patch_handoff_state"]
        == "patches_generated"
    )
    assert (
        handoff.source_linkage["provider_runtime_artifact_path"]
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )


def test_build_frontend_provider_patch_handoff_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert handoff.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert handoff.steps[0].patch_availability_state == "patches_generated"


def test_build_frontend_provider_patch_handoff_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert handoff.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert handoff.steps[0].patch_availability_state == "patches_generated"


def test_build_frontend_provider_patch_handoff_warns_when_runtime_artifact_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is False
    assert handoff.patch_availability_state == "missing_artifact"
    assert handoff.steps == []
    assert handoff.runtime_generated_at == ""
    assert "missing provider runtime artifact" in handoff.warnings[0]


def test_build_frontend_provider_patch_apply_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.patch_apply_state == "not_started"
    assert (
        request.handoff_source_path
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )
    assert request.handoff_generated_at == "2026-04-03T19:00:00Z"
    assert request.patch_availability_state == "patches_generated"
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].patch_availability_state == "patches_generated"
    assert (
        request.steps[0].source_linkage["patch_apply_state"] == "not_started"
    )


def test_build_frontend_provider_patch_apply_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].patch_availability_state == "patches_generated"


def test_build_frontend_provider_patch_apply_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].patch_availability_state == "patches_generated"


def test_execute_frontend_provider_patch_apply_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_patch_apply(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.patch_apply_state == "completed"
    assert result.apply_result == "applied"
    assert result.apply_summaries == [
        "applied 1 provider patch file(s) from readonly patch handoff"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["patch_apply_state"] == "completed"


def test_write_frontend_provider_patch_apply_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())
    result = svc.execute_frontend_provider_patch_apply(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_provider_patch_apply_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["handoff_source_path"]
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )
    assert payload["patch_apply_state"] == "completed"
    assert payload["apply_result"] == "applied"
    assert payload["confirmed"] is True
    assert payload["apply_summaries"] == [
        "applied 1 provider patch file(s) from readonly patch handoff"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["provider_patch_apply_artifact_path"]
        == ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
    )


def test_execute_frontend_provider_patch_apply_rejects_non_simple_spec_ids(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "../escape",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_contract_observations"],
                "suggested_next_actions": ["review generated provider patch plan"],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_patch_apply(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.patch_apply_state == "blocked"
    assert result.apply_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "provider patch apply step ../escape is not a simple spec identifier; apply skipped"
    ]
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "steps"
        / "escape.md"
    ).exists()


def test_execute_frontend_provider_patch_apply_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="patches_generated",
        provider_execution_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_patch_apply(_manifest(), confirmed=True)

    assert result.patch_apply_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "latest.yaml"
    ).exists()
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "steps"
        / "001-auth.md"
    ).is_file()


def test_build_frontend_cross_spec_writeback_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.writeback_state == "not_started"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T20:00:00Z"
    assert request.apply_result == "applied"
    assert request.written_paths == [
        ".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"
    ]
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].writeback_state == "not_started"
    assert (
        request.steps[0].source_linkage["cross_spec_writeback_state"] == "not_started"
    )


def test_build_frontend_cross_spec_writeback_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "patches_generated",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].writeback_state == "not_started"


def test_build_frontend_cross_spec_writeback_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "patches_generated",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].writeback_state == "not_started"


def test_execute_frontend_cross_spec_writeback_writes_spec_receipts_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_cross_spec_writeback(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.writeback_state == "completed"
    assert result.orchestration_result == "completed"
    assert result.orchestration_summaries == [
        "wrote 1 cross-spec writeback file(s) from canonical patch apply artifact"
    ]
    assert result.written_paths == ["specs/001-auth/frontend-provider-writeback.md"]
    assert (tmp_path / "specs" / "001-auth" / "frontend-provider-writeback.md").is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["cross_spec_writeback_state"] == "completed"


def test_execute_frontend_cross_spec_writeback_blocks_until_patch_apply_is_applied(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_cross_spec_writeback(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.writeback_state == "blocked"
    assert result.orchestration_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "cross-spec writeback requires applied patch artifact (apply_result=deferred)",
    ]
    assert not (tmp_path / "specs" / "001-auth" / "frontend-provider-writeback.md").exists()


def test_execute_frontend_cross_spec_writeback_rejects_non_manifest_spec_paths(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": ".ai-sdlc/memory",
                "patch_availability_state": "patches_generated",
                "pending_inputs": ["frontend_contract_observations"],
                "suggested_next_actions": ["review generated provider patch plan"],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_cross_spec_writeback(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.writeback_state == "blocked"
    assert result.orchestration_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "cross-spec writeback step 001-auth path does not match manifest spec path: .ai-sdlc/memory"
    ]
    assert not (tmp_path / ".ai-sdlc" / "memory" / "frontend-provider-writeback.md").exists()


def test_write_frontend_cross_spec_writeback_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())
    result = svc.execute_frontend_cross_spec_writeback(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_cross_spec_writeback_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-cross-spec-writeback"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
    )
    assert payload["writeback_state"] == "completed"
    assert payload["orchestration_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["orchestration_summaries"] == [
        "wrote 1 cross-spec writeback file(s) from canonical patch apply artifact"
    ]
    assert payload["existing_written_paths"] == [
        ".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"
    ]
    assert payload["written_paths"] == ["specs/001-auth/frontend-provider-writeback.md"]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["cross_spec_writeback_artifact_path"]
        == ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
    )


def test_write_frontend_cross_spec_writeback_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "patches_generated",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())
    result = svc.execute_frontend_cross_spec_writeback(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_cross_spec_writeback_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_cross_spec_writeback_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "patches_generated",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "completed",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())
    result = svc.execute_frontend_cross_spec_writeback(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_cross_spec_writeback_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_cross_spec_writeback_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="applied",
        patch_apply_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_cross_spec_writeback(_manifest(), confirmed=True)

    assert result.writeback_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-cross-spec-writeback"
        / "latest.yaml"
    ).exists()
    assert (tmp_path / "specs" / "001-auth" / "frontend-provider-writeback.md").is_file()


def test_build_frontend_guarded_registry_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.registry_state == "not_started"
    assert request.writeback_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T21:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].registry_state == "not_started"
    assert request.steps[0].source_linkage["registry_state"] == "not_started"


def test_build_frontend_guarded_registry_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].registry_state == "not_started"


def test_build_frontend_guarded_registry_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].registry_state == "not_started"


def test_execute_frontend_guarded_registry_blocks_until_writeback_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.registry_state == "blocked"
    assert result.registry_result == "blocked"
    assert result.registry_summaries == [
        "guarded registry requires completed cross-spec writeback artifact (writeback_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "guarded registry requires completed cross-spec writeback artifact (writeback_state=deferred)",
    ]
    assert result.source_linkage["registry_state"] == "blocked"


def test_execute_frontend_guarded_registry_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="completed",
        writeback_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.registry_state == "completed"
    assert result.registry_result == "completed"
    assert result.registry_summaries == [
        "materialized 1 guarded registry step file(s) from canonical cross-spec writeback artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-guarded-registry/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-guarded-registry"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["registry_state"] == "completed"


def test_execute_frontend_guarded_registry_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="completed",
        writeback_state="completed",
        remaining_blockers=["spec 001-auth receipt still requires review"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.registry_state == "blocked"
    assert result.registry_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth receipt still requires review",
        "guarded registry requires blocker-free cross-spec writeback artifact",
    ]


def test_execute_frontend_guarded_registry_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="completed",
        writeback_state="completed",
        remaining_blockers=["spec 001-auth receipt still requires review"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_guarded_registry_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_guarded_registry(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.registry_state == "blocked"
    assert result.registry_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth receipt still requires review",
        "guarded registry requires blocker-free cross-spec writeback artifact",
    ]


def test_execute_frontend_guarded_registry_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.registry_state == "blocked"
    assert result.registry_result == "blocked"
    assert result.written_paths == []


def test_write_frontend_guarded_registry_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="completed",
        writeback_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())
    result = svc.execute_frontend_guarded_registry(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_guarded_registry_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-guarded-registry"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
    )
    assert payload["registry_state"] == "completed"
    assert payload["registry_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["registry_summaries"] == [
        "materialized 1 guarded registry step file(s) from canonical cross-spec writeback artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-guarded-registry/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["guarded_registry_artifact_path"]
        == ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
    )


def test_write_frontend_guarded_registry_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())
    result = svc.execute_frontend_guarded_registry(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_guarded_registry_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_guarded_registry_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())
    result = svc.execute_frontend_guarded_registry(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_guarded_registry_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_guarded_registry_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="completed",
        writeback_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.registry_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-guarded-registry"
        / "latest.yaml"
    ).exists()


def test_build_frontend_broader_governance_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.governance_state == "not_started"
    assert request.registry_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T22:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].governance_state == "not_started"
    assert request.steps[0].source_linkage["governance_state"] == "not_started"


def test_build_frontend_broader_governance_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].governance_state == "not_started"


def test_build_frontend_broader_governance_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].governance_state == "not_started"


def test_execute_frontend_broader_governance_blocks_until_registry_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.governance_state == "blocked"
    assert result.governance_result == "blocked"
    assert result.governance_summaries == [
        "broader governance requires completed guarded registry artifact (registry_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "broader governance requires completed guarded registry artifact (registry_state=deferred)",
    ]
    assert result.source_linkage["governance_state"] == "blocked"


def test_execute_frontend_broader_governance_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="completed",
        registry_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.governance_state == "completed"
    assert result.governance_result == "completed"
    assert result.governance_summaries == [
        "materialized 1 broader governance step file(s) from canonical guarded registry artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-broader-governance/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-broader-governance"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["governance_state"] == "completed"


def test_execute_frontend_broader_governance_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="completed",
        registry_state="completed",
        remaining_blockers=["spec 001-auth registry update still requires review"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.governance_state == "blocked"
    assert result.governance_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth registry update still requires review",
        "broader governance requires blocker-free guarded registry artifact",
    ]


def test_execute_frontend_broader_governance_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="completed",
        registry_state="completed",
        remaining_blockers=["spec 001-auth registry update still requires review"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_broader_governance_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_broader_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.governance_state == "blocked"
    assert result.governance_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth registry update still requires review",
        "broader governance requires blocker-free guarded registry artifact",
    ]


def test_execute_frontend_broader_governance_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.governance_state == "blocked"
    assert result.governance_result == "blocked"
    assert result.written_paths == []


def test_write_frontend_broader_governance_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="completed",
        registry_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())
    result = svc.execute_frontend_broader_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_broader_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-broader-governance"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
    )
    assert payload["governance_state"] == "completed"
    assert payload["governance_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["governance_summaries"] == [
        "materialized 1 broader governance step file(s) from canonical guarded registry artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-broader-governance/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["broader_governance_artifact_path"]
        == ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
    )


def test_write_frontend_broader_governance_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())
    result = svc.execute_frontend_broader_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_broader_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_broader_governance_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())
    result = svc.execute_frontend_broader_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_broader_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_broader_governance_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="completed",
        registry_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.governance_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-broader-governance"
        / "latest.yaml"
    ).exists()


def test_build_frontend_final_governance_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.final_governance_state == "not_started"
    assert request.governance_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T23:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].final_governance_state == "not_started"
    assert request.steps[0].source_linkage["final_governance_state"] == "not_started"


def test_execute_frontend_final_governance_blocks_until_broader_governance_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.final_governance_state == "blocked"
    assert result.final_governance_result == "blocked"
    assert result.final_governance_summaries == [
        "final governance requires completed broader governance artifact (governance_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final governance requires completed broader governance artifact (governance_state=deferred)",
    ]
    assert result.source_linkage["final_governance_state"] == "blocked"


def test_execute_frontend_final_governance_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="completed",
        governance_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.final_governance_state == "completed"
    assert result.final_governance_result == "completed"
    assert result.final_governance_summaries == [
        "materialized 1 final governance step file(s) from canonical broader governance artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-final-governance/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-governance"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["final_governance_state"] == "completed"


def test_execute_frontend_final_governance_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="completed",
        governance_state="completed",
        remaining_blockers=["spec 001-auth broader governance still requires review"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.final_governance_state == "blocked"
    assert result.final_governance_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth broader governance still requires review",
        "final governance requires blocker-free broader governance artifact",
    ]


def test_execute_frontend_final_governance_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="completed",
        governance_state="completed",
        remaining_blockers=["spec 001-auth broader governance still requires review"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_final_governance_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_final_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.final_governance_state == "blocked"
    assert result.final_governance_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth broader governance still requires review",
        "final governance requires blocker-free broader governance artifact",
    ]


def test_execute_frontend_final_governance_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.final_governance_state == "blocked"
    assert result.final_governance_result == "blocked"
    assert result.written_paths == []


def test_write_frontend_final_governance_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="completed",
        governance_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())
    result = svc.execute_frontend_final_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-governance"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
    )
    assert payload["final_governance_state"] == "completed"
    assert payload["final_governance_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["final_governance_summaries"] == [
        "materialized 1 final governance step file(s) from canonical broader governance artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-final-governance/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["final_governance_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
    )


def test_execute_frontend_final_governance_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="completed",
        governance_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.final_governance_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-governance"
        / "latest.yaml"
    ).exists()


def test_build_frontend_final_governance_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_governance_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())
    result = svc.execute_frontend_final_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_governance_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_governance_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())
    result = svc.execute_frontend_final_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_writeback_persistence_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.persistence_state == "not_started"
    assert request.final_governance_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T00:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].persistence_state == "not_started"
    assert request.steps[0].source_linkage["persistence_state"] == "not_started"


def test_execute_frontend_writeback_persistence_blocks_until_final_governance_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.persistence_state == "blocked"
    assert result.persistence_result == "blocked"
    assert result.persistence_summaries == [
        "writeback persistence requires completed final governance artifact (final_governance_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "writeback persistence requires completed final governance artifact (final_governance_state=deferred)",
    ]
    assert result.source_linkage["persistence_state"] == "blocked"


def test_execute_frontend_writeback_persistence_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="completed",
        final_governance_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.persistence_state == "completed"
    assert result.persistence_result == "completed"
    assert result.persistence_summaries == [
        "materialized 1 writeback persistence step file(s) from canonical final governance artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-writeback-persistence/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-writeback-persistence"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["persistence_state"] == "completed"


def test_execute_frontend_writeback_persistence_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="completed",
        final_governance_state="completed",
        remaining_blockers=["spec 001-auth final governance still requires review"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.persistence_state == "blocked"
    assert result.persistence_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth final governance still requires review",
        "writeback persistence requires blocker-free final governance artifact",
    ]


def test_execute_frontend_writeback_persistence_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="completed",
        final_governance_state="completed",
        remaining_blockers=["spec 001-auth final governance still requires review"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_writeback_persistence_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_writeback_persistence(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.persistence_state == "blocked"
    assert result.persistence_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth final governance still requires review",
        "writeback persistence requires blocker-free final governance artifact",
    ]


def test_execute_frontend_writeback_persistence_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.persistence_state == "blocked"
    assert result.persistence_result == "blocked"
    assert result.written_paths == []


def test_write_frontend_writeback_persistence_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="completed",
        final_governance_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())
    result = svc.execute_frontend_writeback_persistence(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_writeback_persistence_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-writeback-persistence"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
    )
    assert payload["persistence_state"] == "completed"
    assert payload["persistence_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["persistence_summaries"] == [
        "materialized 1 writeback persistence step file(s) from canonical final governance artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-writeback-persistence/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["writeback_persistence_artifact_path"]
        == ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
    )


def test_build_frontend_writeback_persistence_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_writeback_persistence_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())
    result = svc.execute_frontend_writeback_persistence(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_writeback_persistence_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_writeback_persistence_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_writeback_persistence_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())
    result = svc.execute_frontend_writeback_persistence(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_writeback_persistence_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_writeback_persistence_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="completed",
        final_governance_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.persistence_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-writeback-persistence"
        / "latest.yaml"
    ).exists()


def test_build_frontend_persisted_write_proof_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.proof_state == "not_started"
    assert request.persistence_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T01:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].proof_state == "not_started"
    assert request.steps[0].source_linkage["proof_state"] == "not_started"


def test_execute_frontend_persisted_write_proof_blocks_until_writeback_persistence_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_persisted_write_proof(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.proof_state == "blocked"
    assert result.proof_result == "blocked"
    assert result.proof_summaries == [
        "persisted write proof requires completed writeback persistence artifact (persistence_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "persisted write proof requires completed writeback persistence artifact (persistence_state=deferred)",
    ]
    assert result.source_linkage["proof_state"] == "blocked"


def test_execute_frontend_persisted_write_proof_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="completed",
        persistence_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_persisted_write_proof(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.proof_state == "blocked"
    assert result.proof_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "persisted write proof requires blocker-free writeback persistence artifact",
    ]


def test_execute_frontend_persisted_write_proof_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="completed",
        persistence_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_persisted_write_proof_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.proof_state == "blocked"
    assert result.proof_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "persisted write proof requires blocker-free writeback persistence artifact",
    ]


def test_execute_frontend_persisted_write_proof_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert request.required is False
    assert request.steps == []
    assert result.proof_state == "blocked"
    assert result.proof_result == "blocked"
    assert result.written_paths == []


def test_execute_frontend_persisted_write_proof_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="completed",
        persistence_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_persisted_write_proof(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.proof_state == "completed"
    assert result.proof_result == "completed"
    assert result.proof_summaries == [
        "materialized 1 persisted write proof step file(s) from canonical writeback persistence artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-persisted-write-proof/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-persisted-write-proof"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["proof_state"] == "completed"


def test_execute_frontend_persisted_write_proof_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="completed",
        persistence_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_persisted_write_proof(_manifest(), confirmed=True)

    assert result.proof_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-persisted-write-proof"
        / "latest.yaml"
    ).exists()


def test_write_frontend_persisted_write_proof_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="completed",
        persistence_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_persisted_write_proof_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-persisted-write-proof"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
    )
    assert payload["proof_state"] == "completed"
    assert payload["proof_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["proof_summaries"] == [
        "materialized 1 persisted write proof step file(s) from canonical writeback persistence artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-persisted-write-proof/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["persisted_write_proof_artifact_path"]
        == ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
    )


def test_build_frontend_persisted_write_proof_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_persisted_write_proof_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_persisted_write_proof_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_persisted_write_proof_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_persisted_write_proof_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_persisted_write_proof_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_publication_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_publication_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_publication_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_publication_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_publication_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_publication_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_publication_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.publication_state == "not_started"
    assert request.proof_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T02:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].publication_state == "not_started"
    assert request.steps[0].source_linkage["publication_state"] == "not_started"


def test_execute_frontend_final_proof_publication_blocks_until_persisted_write_proof_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_publication(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.publication_state == "blocked"
    assert result.publication_result == "blocked"
    assert result.publication_summaries == [
        "final proof publication requires completed persisted write proof artifact (proof_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof publication requires completed persisted write proof artifact (proof_state=deferred)",
    ]
    assert result.source_linkage["publication_state"] == "blocked"


def test_execute_frontend_final_proof_publication_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="completed",
        proof_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_publication(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.publication_state == "blocked"
    assert result.publication_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof publication requires blocker-free persisted write proof artifact",
    ]


def test_execute_frontend_final_proof_publication_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="completed",
        proof_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_final_proof_publication_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.publication_state == "blocked"
    assert result.publication_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof publication requires blocker-free persisted write proof artifact",
    ]


def test_execute_frontend_final_proof_publication_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert request.required is False
    assert request.steps == []
    assert result.publication_state == "blocked"
    assert result.publication_result == "blocked"
    assert result.written_paths == []


def test_execute_frontend_final_proof_publication_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="completed",
        proof_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_publication(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.publication_state == "completed"
    assert result.publication_result == "completed"
    assert result.publication_summaries == [
        "materialized 1 final proof publication step file(s) from canonical persisted write proof artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-final-proof-publication/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-publication"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["publication_state"] == "completed"


def test_execute_frontend_final_proof_publication_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="completed",
        proof_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_publication(_manifest(), confirmed=True)

    assert result.publication_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-publication"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_publication_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="completed",
        proof_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_publication_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-publication"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
    )
    assert payload["publication_state"] == "completed"
    assert payload["publication_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["publication_summaries"] == [
        "materialized 1 final proof publication step file(s) from canonical persisted write proof artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-final-proof-publication/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["final_proof_publication_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )


def test_build_frontend_final_proof_closure_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_closure_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_closure_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_closure_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_closure_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_closure_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_closure_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.closure_state == "not_started"
    assert request.publication_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T03:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].closure_state == "not_started"
    assert request.steps[0].source_linkage["closure_state"] == "not_started"


def test_execute_frontend_final_proof_closure_blocks_until_final_proof_publication_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_closure(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.closure_state == "blocked"
    assert result.closure_result == "blocked"
    assert result.closure_summaries == [
        "final proof closure requires completed final proof publication artifact (publication_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof closure requires completed final proof publication artifact (publication_state=deferred)",
    ]
    assert result.source_linkage["closure_state"] == "blocked"


def test_execute_frontend_final_proof_closure_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="completed",
        publication_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_closure(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.closure_state == "blocked"
    assert result.closure_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof closure requires blocker-free final proof publication artifact",
    ]


def test_execute_frontend_final_proof_closure_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="completed",
        publication_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_final_proof_closure_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.closure_state == "blocked"
    assert result.closure_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof closure requires blocker-free final proof publication artifact",
    ]


def test_execute_frontend_final_proof_closure_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert request.required is False
    assert request.steps == []
    assert result.closure_state == "blocked"
    assert result.closure_result == "blocked"
    assert result.written_paths == []


def test_execute_frontend_final_proof_closure_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="completed",
        publication_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_closure(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.closure_state == "completed"
    assert result.closure_result == "completed"
    assert result.closure_summaries == [
        "materialized 1 final proof closure step file(s) from canonical final proof publication artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-final-proof-closure/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-closure"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["closure_state"] == "completed"


def test_execute_frontend_final_proof_closure_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="completed",
        publication_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_closure(_manifest(), confirmed=True)

    assert result.closure_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-closure"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_closure_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="completed",
        publication_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_closure_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-closure"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )
    assert payload["artifact_generated_at"] == "2026-04-04T03:00:00Z"
    assert payload["publication_state"] == "completed"
    assert payload["closure_state"] == "completed"
    assert payload["closure_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["closure_summaries"] == [
        "materialized 1 final proof closure step file(s) from canonical final proof publication artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-final-proof-closure/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert payload["steps"][0]["closure_state"] == "not_started"
    assert (
        payload["source_linkage"]["final_proof_publication_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )
    assert (
        payload["source_linkage"]["final_proof_closure_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )


def test_build_frontend_final_proof_archive_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_archive_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_archive_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.archive_state == "not_started"
    assert request.closure_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T04:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].archive_state == "not_started"
    assert request.steps[0].source_linkage["archive_state"] == "not_started"


def test_execute_frontend_final_proof_archive_blocks_until_final_proof_closure_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.archive_state == "blocked"
    assert result.archive_result == "blocked"
    assert result.archive_summaries == [
        "final proof archive requires completed final proof closure artifact (closure_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof archive requires completed final proof closure artifact (closure_state=deferred)",
    ]
    assert result.source_linkage["archive_state"] == "blocked"


def test_execute_frontend_final_proof_archive_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="completed",
        closure_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.archive_state == "blocked"
    assert result.archive_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof archive requires blocker-free final proof closure artifact",
    ]


def test_execute_frontend_final_proof_archive_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="completed",
        closure_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_final_proof_archive_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.archive_state == "blocked"
    assert result.archive_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof archive requires blocker-free final proof closure artifact",
    ]


def test_execute_frontend_final_proof_archive_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert request.required is False
    assert request.steps == []
    assert result.archive_state == "blocked"
    assert result.archive_result == "blocked"
    assert result.written_paths == []


def test_execute_frontend_final_proof_archive_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="completed",
        closure_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive(_manifest(), confirmed=True)

    assert result.passed is True
    assert result.confirmed is True
    assert result.archive_state == "completed"
    assert result.archive_result == "completed"
    assert result.archive_summaries == [
        "materialized 1 final proof archive step file(s) from canonical final proof closure artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-final-proof-archive/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["archive_state"] == "completed"


def test_build_frontend_final_proof_archive_thread_archive_request_uses_archive_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.thread_archive_state == "not_started"
    assert request.archive_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T05:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].thread_archive_state == "not_started"
    assert (
        request.steps[0].source_linkage["final_proof_archive_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )


def test_build_frontend_final_proof_archive_thread_archive_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_thread_archive_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_final_proof_archive_thread_archive_blocks_until_final_proof_archive_is_completed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_thread_archive(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.confirmed is True
    assert result.thread_archive_state == "blocked"
    assert result.thread_archive_result == "blocked"
    assert result.thread_archive_summaries == [
        "final proof archive thread archive requires completed final proof archive artifact (archive_state=deferred)"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof archive thread archive requires completed final proof archive artifact (archive_state=deferred)",
    ]
    assert result.source_linkage["thread_archive_state"] == "blocked"
    assert "project_cleanup_state" not in result.source_linkage


def test_execute_frontend_final_proof_archive_thread_archive_blocks_completed_artifact_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="completed",
        archive_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_thread_archive(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.thread_archive_state == "blocked"
    assert result.thread_archive_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof archive thread archive requires blocker-free final proof archive artifact",
    ]


def test_execute_frontend_final_proof_archive_thread_archive_blocks_manual_skip_request_with_blockers(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="completed",
        archive_state="completed",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_final_proof_archive_thread_archive_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_final_proof_archive_thread_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.thread_archive_state == "blocked"
    assert result.thread_archive_result == "blocked"
    assert result.written_paths == []
    assert result.remaining_blockers == [
        "spec 001-auth remediation still required",
        "final proof archive thread archive requires blocker-free final proof archive artifact",
    ]


def test_execute_frontend_final_proof_archive_thread_archive_blocks_empty_non_completed_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=[],
        steps=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive_thread_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert request.required is False
    assert request.steps == []
    assert result.thread_archive_state == "blocked"
    assert result.thread_archive_result == "blocked"
    assert result.written_paths == []


def test_execute_frontend_final_proof_archive_thread_archive_writes_step_files_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="completed",
        archive_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_thread_archive(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is True
    assert result.confirmed is True
    assert result.thread_archive_state == "completed"
    assert result.thread_archive_result == "completed"
    assert result.thread_archive_summaries == [
        "materialized 1 final proof archive thread archive step file(s) from canonical final proof archive artifact"
    ]
    assert result.written_paths == [
        ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive/steps/001-auth.md"
    ]
    assert (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive-thread-archive"
        / "steps"
        / "001-auth.md"
    ).is_file()
    assert result.remaining_blockers == []
    assert result.source_linkage["thread_archive_state"] == "completed"
    assert "project_cleanup_state" not in result.source_linkage


def test_build_frontend_final_proof_archive_project_cleanup_request_uses_thread_archive_execute_truth(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.project_cleanup_state == "not_started"
    assert request.thread_archive_state == "blocked"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T05:00:00Z"
    assert request.written_paths == []
    assert request.cleanup_targets_state == "missing"
    assert request.cleanup_targets == []
    assert request.cleanup_target_eligibility_state == "missing"
    assert request.cleanup_target_eligibility == []
    assert request.cleanup_preview_plan_state == "missing"
    assert request.cleanup_preview_plan == []
    assert request.cleanup_mutation_proposal_state == "missing"
    assert request.cleanup_mutation_proposal == []
    assert request.cleanup_mutation_proposal_approval_state == "missing"
    assert request.cleanup_mutation_proposal_approval == []
    assert request.cleanup_mutation_execution_gating_state == "missing"
    assert request.cleanup_mutation_execution_gating == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].project_cleanup_state == "not_started"
    assert request.steps[0].source_linkage["thread_archive_result"] == "blocked"
    assert (
        request.steps[0].source_linkage["final_proof_archive_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )
    assert request.source_linkage["cleanup_targets_state"] == "missing"
    assert request.source_linkage["cleanup_target_eligibility_state"] == "missing"
    assert request.source_linkage["cleanup_preview_plan_state"] == "missing"
    assert request.source_linkage["cleanup_mutation_proposal_state"] == "missing"
    assert (
        request.source_linkage["cleanup_mutation_proposal_approval_state"] == "missing"
    )
    assert (
        request.source_linkage["cleanup_mutation_execution_gating_state"] == "missing"
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_does_not_materialize_thread_archive_steps(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="completed",
        archive_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.thread_archive_state == "completed"
    assert request.steps[0].source_linkage["thread_archive_result"] == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive-thread-archive"
        / "steps"
        / "001-auth.md"
    ).exists()


def test_build_frontend_final_proof_archive_project_cleanup_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_project_cleanup_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_project_cleanup_request_uses_explicit_empty_cleanup_targets(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[],
        cleanup_mutation_proposal_approval=[],
        cleanup_mutation_execution_gating=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_targets_state == "empty"
    assert request.cleanup_targets == []
    assert request.cleanup_target_eligibility_state == "empty"
    assert request.cleanup_target_eligibility == []
    assert request.cleanup_preview_plan_state == "empty"
    assert request.cleanup_preview_plan == []
    assert request.cleanup_mutation_proposal_state == "empty"
    assert request.cleanup_mutation_proposal == []
    assert request.cleanup_mutation_proposal_approval_state == "empty"
    assert request.cleanup_mutation_proposal_approval == []
    assert request.cleanup_mutation_execution_gating_state == "empty"
    assert request.cleanup_mutation_execution_gating == []
    assert request.warnings == [
        "final proof archive baseline defers thread archive and cleanup actions",
    ]


def test_build_frontend_final_proof_archive_project_cleanup_request_preserves_listed_cleanup_targets(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    cleanup_targets = [
        {
            "target_id": "cleanup-thread-archive-report",
            "path": "specs/001-auth/threads/archive-001.md",
            "kind": "thread_archive",
        },
        {
            "target_id": "cleanup-spec-dir",
            "path": "specs/002-course",
            "kind": "spec_dir",
        },
    ]
    cleanup_target_eligibility = [
        {
            "target_id": "cleanup-thread-archive-report",
            "eligibility": "eligible",
            "reason": "thread archive report may proceed to preview planning truth",
        },
        {
            "target_id": "cleanup-spec-dir",
            "eligibility": "eligible",
            "reason": "explicit cleanup target may proceed to future planning truth",
        },
    ]
    cleanup_preview_plan = [
        {
            "target_id": "cleanup-thread-archive-report",
            "planned_action": "archive_thread_report",
            "reason": "preview canonical archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "planned_action": "remove_spec_dir",
            "reason": "preview canonical spec cleanup action",
        },
    ]
    cleanup_mutation_proposal = [
        {
            "target_id": "cleanup-thread-archive-report",
            "proposed_action": "archive_thread_report",
            "reason": "proposal mirrors previewed archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "proposed_action": "remove_spec_dir",
            "reason": "proposal mirrors previewed spec cleanup action",
        },
    ]
    cleanup_mutation_proposal_approval = [
        {
            "target_id": "cleanup-thread-archive-report",
            "approved_action": "archive_thread_report",
            "reason": "explicit approval matches the proposed archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "approved_action": "remove_spec_dir",
            "reason": "explicit approval matches the proposed spec cleanup action",
        },
    ]
    cleanup_mutation_execution_gating = [
        {
            "target_id": "cleanup-thread-archive-report",
            "gated_action": "archive_thread_report",
            "reason": "execution gating matches the approved archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "gated_action": "remove_spec_dir",
            "reason": "execution gating matches the approved spec cleanup action",
        },
    ]
    cleanup_targets[0]["cleanup_action"] = "archive_thread_report"
    cleanup_targets[1]["cleanup_action"] = "remove_spec_dir"
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=cleanup_targets,
        cleanup_target_eligibility=cleanup_target_eligibility,
        cleanup_preview_plan=cleanup_preview_plan,
        cleanup_mutation_proposal=cleanup_mutation_proposal,
        cleanup_mutation_proposal_approval=cleanup_mutation_proposal_approval,
        cleanup_mutation_execution_gating=cleanup_mutation_execution_gating,
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_targets_state == "listed"
    assert request.cleanup_targets == cleanup_targets
    assert request.cleanup_target_eligibility_state == "listed"
    assert request.cleanup_target_eligibility == cleanup_target_eligibility
    assert request.cleanup_preview_plan_state == "listed"
    assert request.cleanup_preview_plan == cleanup_preview_plan
    assert request.cleanup_mutation_proposal_state == "listed"
    assert request.cleanup_mutation_proposal == cleanup_mutation_proposal
    assert request.cleanup_mutation_proposal_approval_state == "listed"
    assert (
        request.cleanup_mutation_proposal_approval
        == cleanup_mutation_proposal_approval
    )
    assert request.cleanup_mutation_execution_gating_state == "listed"
    assert (
        request.cleanup_mutation_execution_gating
        == cleanup_mutation_execution_gating
    )
    assert request.source_linkage["cleanup_target_eligibility_state"] == "listed"
    assert request.source_linkage["cleanup_preview_plan_state"] == "listed"
    assert request.source_linkage["cleanup_mutation_proposal_state"] == "listed"
    assert (
        request.source_linkage["cleanup_mutation_proposal_approval_state"] == "listed"
    )
    assert (
        request.source_linkage["cleanup_mutation_execution_gating_state"] == "listed"
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_target_eligibility_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_target_eligibility_state == "missing"
    assert request.cleanup_target_eligibility == []
    assert any(
        "cleanup_target_eligibility must be a list" in item for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_misaligned_cleanup_target_eligibility(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-spec-dir",
                "eligibility": "eligible",
                "reason": "wrong target id",
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_target_eligibility_state == "listed"
    assert len(request.cleanup_target_eligibility) == 1
    assert any(
        "cleanup_target_eligibility target_id set does not match cleanup_targets"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_preview_plan_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_preview_plan_state == "missing"
    assert request.cleanup_preview_plan == []
    assert any(
        "cleanup_preview_plan must be a list" in item for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_preview_plan_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-thread-archive-report",
                "planned_action": "remove_spec_dir",
                "reason": "preview incorrectly proposes destructive cleanup",
            },
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_preview_plan_state == "listed"
    assert len(request.cleanup_preview_plan) == 2
    assert any(
        "cleanup_preview_plan target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_preview_plan target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_preview_plan target_id=cleanup-thread-archive-report planned_action does not match cleanup_action"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_state == "missing"
    assert request.cleanup_mutation_proposal == []
    assert any(
        "cleanup_mutation_proposal must be a list" in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            }
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal incorrectly changes cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_state == "listed"
    assert len(request.cleanup_mutation_proposal) == 2
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-thread-archive-report proposed_action does not match cleanup_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_approval_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[],
        cleanup_mutation_proposal_approval="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_approval_state == "missing"
    assert request.cleanup_mutation_proposal_approval == []
    assert any(
        "cleanup_mutation_proposal_approval must be a list" in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_approval_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            }
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "remove_spec_dir",
                "reason": "approval incorrectly changes cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "approved_action": "remove_spec_dir",
                "reason": "approval references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_approval_state == "listed"
    assert len(request.cleanup_mutation_proposal_approval) == 2
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report approved_action does not match cleanup_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report approved_action does not match proposed_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-spec-dir does not appear in cleanup_mutation_proposal"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_execution_gating_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[],
        cleanup_mutation_proposal_approval=[],
        cleanup_mutation_execution_gating="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_execution_gating_state == "missing"
    assert request.cleanup_mutation_execution_gating == []
    assert any(
        "cleanup_mutation_execution_gating must be a list" in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_execution_gating_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            }
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "approval mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating incorrectly changes cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_execution_gating_state == "listed"
    assert len(request.cleanup_mutation_execution_gating) == 2
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report gated_action does not match cleanup_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report gated_action does not match approved_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-spec-dir does not appear in cleanup_mutation_proposal_approval"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_targets_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets="specs/001-auth",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_targets_state == "missing"
    assert request.cleanup_targets == []
    assert request.cleanup_target_eligibility_state == "missing"
    assert request.cleanup_target_eligibility == []
    assert any(
        "cleanup_targets must be a list" in item for item in request.warnings
    )


def test_execute_frontend_final_proof_archive_project_cleanup_executes_canonical_gated_targets_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    archive_report = tmp_path / "specs" / "001-auth" / "threads" / "archive-001.md"
    archive_report.parent.mkdir(parents=True, exist_ok=True)
    archive_report.write_text("# archived thread\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "002-course"
    (spec_dir / "notes").mkdir(parents=True, exist_ok=True)
    (spec_dir / "notes" / "todo.md").write_text("cleanup me\n", encoding="utf-8")
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            },
            {
                "target_id": "cleanup-spec-dir",
                "path": "specs/002-course",
                "kind": "spec_dir",
                "cleanup_action": "remove_spec_dir",
            },
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "eligible",
                "reason": "thread archive report may proceed to preview planning truth",
            },
            {
                "target_id": "cleanup-spec-dir",
                "eligibility": "eligible",
                "reason": "explicit cleanup target may proceed to future planning truth",
            },
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-thread-archive-report",
                "planned_action": "archive_thread_report",
                "reason": "preview canonical archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview canonical spec cleanup action",
            },
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors previewed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal mirrors previewed spec cleanup action",
            },
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "explicit approval matches the proposed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "approved_action": "remove_spec_dir",
                "reason": "explicit approval matches the proposed spec cleanup action",
            },
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "archive_thread_report",
                "reason": "execution gating matches the approved archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating matches the approved spec cleanup action",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is True
    assert result.confirmed is True
    assert result.project_cleanup_state == "completed"
    assert result.project_cleanup_result == "completed"
    assert result.project_cleanup_summaries == [
        "executed 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
    ]
    assert result.cleanup_targets_state == "listed"
    assert len(result.cleanup_targets) == 2
    assert result.cleanup_target_eligibility_state == "listed"
    assert len(result.cleanup_target_eligibility) == 2
    assert result.cleanup_preview_plan_state == "listed"
    assert len(result.cleanup_preview_plan) == 2
    assert result.cleanup_mutation_proposal_state == "listed"
    assert len(result.cleanup_mutation_proposal) == 2
    assert result.cleanup_mutation_proposal_approval_state == "listed"
    assert len(result.cleanup_mutation_proposal_approval) == 2
    assert result.cleanup_mutation_execution_gating_state == "listed"
    assert len(result.cleanup_mutation_execution_gating) == 2
    assert result.written_paths == [
        "specs/001-auth/threads/archive-001.md",
        "specs/002-course",
    ]
    assert result.remaining_blockers == []
    assert result.source_linkage["thread_archive_state"] == "blocked"
    assert result.source_linkage["project_cleanup_state"] == "completed"
    assert result.source_linkage["project_cleanup_result"] == "completed"
    assert result.source_linkage["cleanup_targets_state"] == "listed"
    assert result.source_linkage["cleanup_target_eligibility_state"] == "listed"
    assert result.source_linkage["cleanup_preview_plan_state"] == "listed"
    assert result.source_linkage["cleanup_mutation_proposal_state"] == "listed"
    assert (
        result.source_linkage["cleanup_mutation_proposal_approval_state"] == "listed"
    )
    assert (
        result.source_linkage["cleanup_mutation_execution_gating_state"] == "listed"
    )
    assert result.warnings == []
    assert not archive_report.exists()
    assert not spec_dir.exists()


def test_execute_frontend_final_proof_archive_project_cleanup_returns_partial_result_when_a_target_is_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    spec_dir = tmp_path / "specs" / "002-course"
    (spec_dir / "notes").mkdir(parents=True, exist_ok=True)
    (spec_dir / "notes" / "todo.md").write_text("cleanup me\n", encoding="utf-8")
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            },
            {
                "target_id": "cleanup-spec-dir",
                "path": "specs/002-course",
                "kind": "spec_dir",
                "cleanup_action": "remove_spec_dir",
            },
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "eligible",
                "reason": "thread archive report may proceed to preview planning truth",
            },
            {
                "target_id": "cleanup-spec-dir",
                "eligibility": "eligible",
                "reason": "explicit cleanup target may proceed to future planning truth",
            },
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-thread-archive-report",
                "planned_action": "archive_thread_report",
                "reason": "preview canonical archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview canonical spec cleanup action",
            },
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors previewed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal mirrors previewed spec cleanup action",
            },
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "explicit approval matches the proposed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "approved_action": "remove_spec_dir",
                "reason": "explicit approval matches the proposed spec cleanup action",
            },
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "archive_thread_report",
                "reason": "execution gating matches the approved archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating matches the approved spec cleanup action",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.confirmed is True
    assert result.project_cleanup_state == "partial"
    assert result.project_cleanup_result == "partial"
    assert result.project_cleanup_summaries == [
        "executed 1 of 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
    ]
    assert result.written_paths == ["specs/002-course"]
    assert result.remaining_blockers == ["cleanup-thread-archive-report"]
    assert result.source_linkage["project_cleanup_state"] == "partial"
    assert result.source_linkage["project_cleanup_result"] == "partial"
    assert any(
        "cleanup target cleanup-thread-archive-report is missing at specs/001-auth/threads/archive-001.md"
        in item
        for item in result.warnings
    )
    assert not spec_dir.exists()


def test_execute_frontend_final_proof_archive_project_cleanup_blocks_invalid_execution_gating_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    archive_report = tmp_path / "specs" / "001-auth" / "threads" / "archive-001.md"
    archive_report.parent.mkdir(parents=True, exist_ok=True)
    archive_report.write_text("# archived thread\n", encoding="utf-8")
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "approval mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "archive_thread_report",
                "reason": "execution gating matches the canonical cleanup action",
            }
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.confirmed is True
    assert result.project_cleanup_state == "blocked"
    assert result.project_cleanup_result == "blocked"
    assert result.written_paths == []
    assert archive_report.exists()
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in result.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in result.warnings
    )


def test_execute_frontend_final_proof_archive_project_cleanup_blocks_manual_skip_request_with_invalid_cleanup_truth(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    archive_report = tmp_path / "specs" / "001-auth" / "threads" / "archive-001.md"
    archive_report.parent.mkdir(parents=True, exist_ok=True)
    archive_report.write_text("# archived thread\n", encoding="utf-8")
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "approval mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "archive_thread_report",
                "reason": "execution gating matches the canonical cleanup action",
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = replace(
        svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest()),
        required=False,
    )
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    assert result.passed is False
    assert result.project_cleanup_state == "blocked"
    assert result.project_cleanup_result == "blocked"
    assert result.written_paths == []
    assert archive_report.exists()


def test_execute_frontend_final_proof_archive_project_cleanup_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.project_cleanup_state == "blocked"
    assert result.project_cleanup_result == "blocked"
    assert result.project_cleanup_summaries == [
        "no cleanup mutations listed in canonical cleanup_mutation_execution_gating"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == []
    assert result.warnings == []
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive-project-cleanup"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_archive_project_cleanup_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_project_cleanup_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive-project-cleanup"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["project_cleanup_result"] == "blocked"
    assert payload["project_cleanup_state"] == "blocked"
    assert payload["project_cleanup_summaries"] == [
        "no cleanup mutations listed in canonical cleanup_mutation_execution_gating"
    ]
    assert payload["thread_archive_state"] == "blocked"
    assert payload["cleanup_targets_state"] == "missing"
    assert payload["cleanup_targets"] == []
    assert payload["cleanup_target_eligibility_state"] == "missing"
    assert payload["cleanup_target_eligibility"] == []
    assert payload["cleanup_preview_plan_state"] == "missing"
    assert payload["cleanup_preview_plan"] == []
    assert payload["cleanup_mutation_proposal_state"] == "missing"
    assert payload["cleanup_mutation_proposal"] == []
    assert payload["cleanup_mutation_proposal_approval_state"] == "missing"
    assert payload["cleanup_mutation_proposal_approval"] == []
    assert payload["cleanup_mutation_execution_gating_state"] == "missing"
    assert payload["cleanup_mutation_execution_gating"] == []
    assert payload["confirmed"] is True
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == []
    assert (
        payload["source_linkage"]["final_proof_archive_project_cleanup_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml"
    )
    assert payload["source_linkage"]["project_cleanup_state"] == "blocked"
    assert payload["source_linkage"]["project_cleanup_result"] == "blocked"


def test_write_frontend_final_proof_archive_project_cleanup_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_project_cleanup_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_archive_project_cleanup_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_project_cleanup_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_final_proof_archive_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="completed",
        closure_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive(_manifest(), confirmed=True)

    assert result.archive_state == "completed"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_archive_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="completed",
        closure_state="completed",
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )
    assert payload["artifact_generated_at"] == "2026-04-04T04:00:00Z"
    assert payload["closure_state"] == "completed"
    assert payload["archive_state"] == "completed"
    assert payload["archive_result"] == "completed"
    assert payload["confirmed"] is True
    assert payload["archive_summaries"] == [
        "materialized 1 final proof archive step file(s) from canonical final proof closure artifact"
    ]
    assert payload["written_paths"] == [
        ".ai-sdlc/memory/frontend-final-proof-archive/steps/001-auth.md"
    ]
    assert payload["remaining_blockers"] == []
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert payload["steps"][0]["archive_state"] == "not_started"
    assert (
        payload["source_linkage"]["final_proof_closure_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )
    assert (
        payload["source_linkage"]["final_proof_archive_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )


def test_build_status_surfaces_ready_frontend_readiness_per_spec(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    _write_frontend_contract_observations(tmp_path / "specs" / "001-auth")

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "ready"
    assert readiness.execute_gate_state == "ready"
    assert readiness.decision_reason == "all_checks_passed"
    assert readiness.coverage_gaps == []
    assert readiness.blockers == []
    assert readiness.source_linkage["runtime_attachment_status"] == "attached"
    assert readiness.source_linkage["frontend_gate_verdict"] == "PASS"


def test_build_status_surfaces_frontend_readiness_gap_when_attachment_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "missing_artifact"
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "scope_or_linkage_invalid"
    assert "frontend_contract_observations" in readiness.coverage_gaps
    assert "missing canonical observation artifact" in readiness.blockers[0]
    assert readiness.source_linkage["runtime_attachment_status"] == "missing_artifact"
    assert readiness.source_linkage["frontend_gate_verdict"] == "UNRESOLVED"


def test_build_status_waives_observation_gap_for_framework_capability(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/001-auth",
        frontend_evidence_class="framework_capability",
    )

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "ready"
    assert readiness.execute_gate_state == "ready"
    assert readiness.decision_reason == "advisory_only"
    assert readiness.coverage_gaps == []
    assert readiness.blockers == []
    assert readiness.source_linkage["runtime_attachment_status"] == "missing_artifact"
    assert (
        readiness.source_linkage["frontend_attachment_requirement"]
        == "waived_for_framework_capability"
    )


def test_build_status_blocks_sample_selfcheck_observation_artifact_for_general_spec(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    _write_frontend_contract_observations(
        tmp_path / "specs" / "001-auth",
        provider_kind="scanner",
        provider_name="frontend_contract_scanner",
        source_ref=SAMPLE_FIXTURE_SOURCE_REF,
    )

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "retry"
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "result_inconsistency"
    assert "frontend_contract_observations" in readiness.coverage_gaps
    assert any(
        "sample self-check observation artifact cannot satisfy this spec"
        in blocker
        for blocker in readiness.blockers
    )
    assert (
        readiness.source_linkage["frontend_contract_observation_source_profile"]
        == "sample_selfcheck"
    )


def test_build_status_keeps_observation_gap_for_consumer_adoption(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/001-auth",
        frontend_evidence_class="consumer_adoption",
    )

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "missing_artifact"
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "scope_or_linkage_invalid"
    assert "frontend_contract_observations" in readiness.coverage_gaps
    assert "missing canonical observation artifact" in readiness.blockers[0]


def test_build_status_surfaces_frontend_readiness_gap_when_071_visual_a11y_evidence_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    _write_frontend_contract_observations(tmp_path / "specs" / "001-auth")

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "retry"
    assert readiness.execute_gate_state == "recheck_required"
    assert readiness.decision_reason == "evidence_missing"
    assert "frontend_visual_a11y_evidence_input" in readiness.coverage_gaps
    assert any("missing explicit evidence input" in blocker for blocker in readiness.blockers)
    assert readiness.source_linkage["frontend_gate_verdict"] == "RETRY"


def test_build_status_surfaces_frontend_blocked_when_visual_a11y_policy_artifacts_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).unlink()
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    _write_frontend_contract_observations(tmp_path / "specs" / "001-auth")

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "retry"
    assert readiness.execute_gate_state == "blocked"
    assert readiness.decision_reason == "result_inconsistency"
    assert "frontend_visual_a11y_policy_artifacts" in readiness.coverage_gaps
    assert any("policy artifacts unavailable" in blocker for blocker in readiness.blockers)


def test_build_status_surfaces_frontend_needs_remediation_when_visual_a11y_issue_detected(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    spec_dir = tmp_path / "specs" / "001-auth"
    _write_frontend_contract_observations(spec_dir)
    _write_frontend_visual_a11y_evidence(
        spec_dir,
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-visual-a11y-issue",
                target_id="user-create",
                surface_id="success-feedback",
                outcome="issue",
                report_type="violation-report",
                severity="medium",
                location_anchor="feedback.banner",
                quality_hint="review success feedback visibility and semantics",
                changed_scope_explanation="071 issue fixture",
            )
        ],
    )

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "retry"
    assert readiness.execute_gate_state == "needs_remediation"
    assert readiness.decision_reason == "actual_quality_blocker"
    assert "frontend_visual_a11y_issue_review" in readiness.coverage_gaps


def test_build_integration_dry_run_surfaces_visual_a11y_evidence_recheck_handoff_when_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_recheck_handoff is None
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_evidence_input" in remediation.fix_inputs
    assert (
        "materialize frontend visual / a11y evidence input"
        in remediation.suggested_actions
    )
    assert remediation.recommended_commands == ["uv run ai-sdlc verify constraints"]


def test_build_integration_dry_run_surfaces_stable_empty_visual_a11y_evidence_recheck_handoff(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        spec_dir = tmp_path / "specs" / spec
        _write_frontend_contract_observations(spec_dir)
        _write_frontend_visual_a11y_evidence(spec_dir, [])

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_recheck_handoff is None
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_evidence_stable_empty" in remediation.fix_inputs
    assert (
        "review stable empty frontend visual / a11y evidence"
        in remediation.suggested_actions
    )
    assert (
        "materialize frontend visual / a11y evidence input"
        not in remediation.suggested_actions
    )
    assert remediation.recommended_commands == ["uv run ai-sdlc verify constraints"]


def test_build_integration_dry_run_surfaces_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        spec_dir = tmp_path / "specs" / spec
        _write_frontend_contract_observations(spec_dir)
        _write_frontend_visual_a11y_evidence(
            spec_dir,
            [
                FrontendVisualA11yEvidenceEvaluation(
                    evaluation_id=f"{spec}-visual-a11y-issue",
                    target_id="user-create",
                    surface_id="success-feedback",
                    outcome="issue",
                    report_type="violation-report",
                    severity="medium",
                    location_anchor="feedback.banner",
                    quality_hint="review success feedback visibility and semantics",
                    changed_scope_explanation="071 issue fixture",
                )
            ],
        )

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_issue_review" in remediation.fix_inputs
    assert (
        "review frontend visual / a11y issue findings"
        in remediation.suggested_actions
    )
    assert "frontend_visual_a11y_evidence_stable_empty" not in remediation.fix_inputs
    assert remediation.recommended_commands == ["uv run ai-sdlc verify constraints"]


def test_build_integration_dry_run_surfaces_visual_a11y_policy_artifact_remediation_input_when_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).unlink()
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_policy_artifacts" in remediation.fix_inputs
    assert (
        "materialize frontend visual / a11y policy artifacts"
        in remediation.suggested_actions
    )
    assert remediation.recommended_commands == [
        "uv run ai-sdlc rules materialize-frontend-mvp",
        "uv run ai-sdlc verify constraints",
    ]


def test_execution_gates_require_all_specs_closed(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    (tmp_path / "specs" / "001-auth" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    (tmp_path / "specs" / "002-course" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)
    assert gates.passed is False
    assert any("not closed" in item for item in gates.failed)


def test_execution_gates_pass_when_closed(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)
    assert gates.passed is True


def test_execution_gates_fail_when_frontend_readiness_not_clear(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )

    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)

    assert gates.passed is False
    assert any("frontend execute gate not clear" in item for item in gates.failed)
    assert any("missing_artifact" in item for item in gates.failed)


def test_execution_gates_pass_when_closed_and_frontend_ready(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)

    assert gates.passed is True
    assert not any("frontend execute gate not clear" in item for item in gates.failed)


def test_execution_gates_pass_for_closed_framework_capability_without_observations(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
        _write_frontend_evidence_class_spec(
            tmp_path,
            spec_rel=f"specs/{p.split('/')[-1]}",
            frontend_evidence_class="framework_capability",
        )
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )

    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)

    assert gates.passed is True
    assert not any("frontend execute gate not clear" in item for item in gates.failed)


def test_build_frontend_solution_confirmation_recommends_enterprise_defaults_in_simple_mode(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(_manifest())

    assert snapshot.decision_status == "recommended"
    assert snapshot.preflight_status == "ready"
    assert snapshot.recommended_frontend_stack == "vue2"
    assert snapshot.recommended_provider_id == "enterprise-vue2"
    assert snapshot.recommended_style_pack_id == "enterprise-default"
    assert snapshot.requested_frontend_stack == "vue2"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.requested_style_pack_id == "enterprise-default"
    assert snapshot.effective_frontend_stack == "vue2"
    assert snapshot.effective_provider_id == "enterprise-vue2"
    assert snapshot.effective_style_pack_id == "enterprise-default"
    assert snapshot.recommended_backend_stack == "fastapi"
    assert snapshot.recommended_api_collab_mode == "typed-bff"
    assert snapshot.style_fidelity_status == "full"
    assert snapshot.provider_mode == "normal"


def test_build_frontend_solution_confirmation_recommends_public_fallback_in_simple_mode_when_enterprise_not_eligible(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
    )

    assert snapshot.decision_status == "recommended"
    assert snapshot.preflight_status == "ready"
    assert snapshot.recommended_frontend_stack == "vue3"
    assert snapshot.recommended_provider_id == "public-primevue"
    assert snapshot.recommended_style_pack_id == "modern-saas"
    assert snapshot.requested_frontend_stack == "vue3"
    assert snapshot.requested_provider_id == "public-primevue"
    assert snapshot.requested_style_pack_id == "modern-saas"
    assert snapshot.effective_frontend_stack == "vue3"
    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_style_pack_id == "modern-saas"
    assert snapshot.availability_summary.failed_check_ids == [
        "company-registry-token"
    ]
    assert snapshot.style_fidelity_status == "full"
    assert snapshot.provider_mode == "normal"


def test_build_frontend_solution_confirmation_preserves_failed_preflight_checks_when_enterprise_marked_eligible(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        enterprise_provider_eligible=True,
        failed_preflight_check_ids=["company-registry-token"],
    )

    assert snapshot.decision_status == "recommended"
    assert snapshot.preflight_status == "warning"
    assert snapshot.preflight_reason_codes == ["enterprise_provider_preflight_warning"]
    assert snapshot.recommended_provider_id == "enterprise-vue2"
    assert snapshot.effective_provider_id == "enterprise-vue2"
    assert snapshot.availability_summary.overall_status == "attention"
    assert snapshot.availability_summary.passed_check_ids == ["company-registry-network"]
    assert snapshot.availability_summary.failed_check_ids == [
        "company-registry-token"
    ]
    assert snapshot.availability_summary.blocking_reason_codes == []


def test_build_frontend_solution_confirmation_blocks_when_defaulted_public_fallback_is_unavailable(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
        fallback_candidate_available=False,
    )

    assert snapshot.decision_status == "blocked"
    assert snapshot.preflight_status == "blocked"
    assert snapshot.recommended_frontend_stack == "vue3"
    assert snapshot.recommended_provider_id == "public-primevue"
    assert snapshot.recommended_style_pack_id == "modern-saas"
    assert snapshot.requested_frontend_stack == "vue3"
    assert snapshot.requested_provider_id == "public-primevue"
    assert snapshot.requested_style_pack_id == "modern-saas"
    assert snapshot.effective_frontend_stack == "vue3"
    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_style_pack_id == "modern-saas"
    assert snapshot.provider_mode == "normal"
    assert snapshot.fallback_reason_code == "enterprise_provider_unavailable"
    assert snapshot.preflight_reason_codes == ["enterprise_provider_unavailable"]
    assert snapshot.availability_summary.overall_status == "blocked"
    assert snapshot.availability_summary.failed_check_ids == [
        "company-registry-token"
    ]


def test_build_frontend_solution_confirmation_requires_explicit_cross_stack_fallback_for_enterprise_request(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_frontend_stack="vue2",
        requested_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
    )

    assert snapshot.decision_status == "fallback_required"
    assert snapshot.preflight_status == "warning"
    assert snapshot.requested_frontend_stack == "vue2"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.requested_style_pack_id == "enterprise-default"
    assert snapshot.effective_frontend_stack == "vue3"
    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_style_pack_id == "modern-saas"
    assert snapshot.provider_mode == "cross_stack_fallback"
    assert snapshot.fallback_reason_code == "enterprise_provider_unavailable"
    assert snapshot.availability_summary.failed_check_ids == [
        "company-registry-token"
    ]


def test_build_frontend_solution_confirmation_blocks_when_enterprise_unavailable_and_no_fallback_candidate(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_frontend_stack="vue2",
        requested_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
        fallback_candidate_available=False,
    )

    assert snapshot.decision_status == "blocked"
    assert snapshot.preflight_status == "blocked"
    assert snapshot.requested_frontend_stack == "vue2"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.requested_style_pack_id == "enterprise-default"
    assert snapshot.effective_frontend_stack == "vue2"
    assert snapshot.effective_provider_id == "enterprise-vue2"
    assert snapshot.effective_style_pack_id == "enterprise-default"
    assert snapshot.provider_mode == "normal"
    assert snapshot.fallback_reason_code == "enterprise_provider_unavailable"


def test_build_frontend_solution_confirmation_requires_fallback_when_enterprise_provider_is_requested_without_explicit_stack(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_provider_id="enterprise-vue2",
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
    )

    assert snapshot.decision_status == "fallback_required"
    assert snapshot.preflight_status == "warning"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_frontend_stack == "vue3"
    assert snapshot.fallback_reason_code == "enterprise_provider_unavailable"
    assert snapshot.provider_mode == "cross_stack_fallback"


def test_build_frontend_solution_confirmation_marks_unknown_provider_style_fidelity_unsupported(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_provider_id="foo-provider",
        requested_style_pack_id="enterprise-default",
    )

    assert snapshot.effective_provider_id == "foo-provider"
    assert snapshot.effective_style_pack_id == "enterprise-default"
    assert snapshot.style_fidelity_status == "unsupported"
    assert snapshot.style_degradation_reason_codes == [
        "provider-not-supported-for-style-fidelity"
    ]


def test_build_frontend_solution_confirmation_marks_unknown_public_style_pack_unsupported(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_provider_id="public-primevue",
        requested_style_pack_id="custom-pack",
    )

    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_style_pack_id == "custom-pack"
    assert snapshot.style_fidelity_status == "unsupported"
    assert snapshot.style_degradation_reason_codes == [
        "style-pack-not-supported-by-provider"
    ]


def _write_minimal_frontend_contract_page_artifacts(
    root: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    page_dir = root / "contracts" / "frontend" / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "page.metadata.yaml").write_text(
        f"page_id: {page_id}\npage_type: form\n",
        encoding="utf-8",
    )
    (page_dir / "page.recipe.yaml").write_text(
        f"recipe_id: {recipe_id}\nrequired_regions:\n  - form\n",
        encoding="utf-8",
    )


def _write_frontend_contract_observations(
    spec_dir: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
    provider_kind: str = "manual",
    provider_name: str = "test-fixture",
    source_ref: str | None = None,
) -> None:
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id=page_id,
                recipe_id=recipe_id,
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ],
        provider_kind=provider_kind,
        provider_name=provider_name,
        generated_at="2026-04-03T15:00:00Z",
        source_ref=source_ref,
        source_digest="sha256:program-service",
        source_revision="rev-program-service",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_frontend_visual_a11y_evidence(
    spec_dir: Path,
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
) -> None:
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=evaluations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T15:00:00Z",
    )
    write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)


def _write_frontend_contract_source_annotation(
    root: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    src_dir = root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "UserCreate.vue").write_text(
        f"""
        <!-- ai-sdlc:frontend-contract-observation
        {{
          "page_id": "{page_id}",
          "recipe_id": "{recipe_id}",
          "i18n_keys": ["user.create.submit"],
          "validation_fields": ["username"]
        }}
        -->
        """,
        encoding="utf-8",
    )


def _write_minimal_constitution(root: Path) -> None:
    memory_dir = root / ".ai-sdlc" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "constitution.md").write_text("# Constitution\n", encoding="utf-8")


def _write_frontend_remediation_writeback_artifact(
    root: Path,
    *,
    passed: bool,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "state": "required",
            "fix_inputs": ["frontend_contract_observations"],
            "suggested_actions": [
                "materialize frontend contract observations",
                "re-run ai-sdlc verify constraints",
            ],
            "action_commands": [
                "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
            ],
            "source_linkage": {
                "runtime_attachment_status": "missing_artifact",
                "frontend_gate_verdict": "UNRESOLVED",
            },
        },
        {
            "spec_id": "002-course",
            "path": "specs/002-course",
            "state": "required",
            "fix_inputs": ["frontend_gate_policy_artifacts"],
            "suggested_actions": ["materialize frontend gate policy artifacts"],
            "action_commands": ["uv run ai-sdlc rules materialize-frontend-mvp"],
            "source_linkage": {
                "runtime_attachment_status": "attached",
                "frontend_gate_verdict": "RETRY",
            },
        },
    ]
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T18:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "passed": passed,
                "source_linkage": {
                    "runbook_source": "program frontend remediation runbook",
                    "execution_source": "program frontend remediation execution",
                },
                "steps": list(steps or default_steps),
                "action_commands": [
                    "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
                ],
                "follow_up_commands": ["uv run ai-sdlc verify constraints"],
                "command_results": [
                    {
                        "command": "uv run ai-sdlc verify constraints",
                        "status": "failed" if remaining_blockers else "passed",
                        "written_paths": [],
                        "blockers": list(remaining_blockers),
                        "summary": "verify constraints result",
                    }
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_provider_runtime_artifact(
    root: Path,
    *,
    invocation_result: str,
    provider_execution_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize frontend contract observations",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                "provider_runtime_state": provider_execution_state,
            },
        }
    ]
    patch_summaries = (
        ["generated provider patch plan for 001-auth (pending_inputs=frontend_contract_observations)"]
        if invocation_result == "patches_generated"
        else ["no patches generated in guarded provider runtime baseline"]
    )
    warnings = (
        []
        if invocation_result == "patches_generated"
        else ["guarded provider runtime baseline does not invoke provider yet"]
    )
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T19:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "handoff_source_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                "handoff_generated_at": "2026-04-03T18:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "provider_execution_state": provider_execution_state,
                "invocation_result": invocation_result,
                "patch_summaries": patch_summaries,
                "remaining_blockers": list(remaining_blockers),
                "warnings": warnings,
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": provider_execution_state,
                    "invocation_result": invocation_result,
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_provider_patch_apply_artifact(
    root: Path,
    *,
    apply_result: str,
    patch_apply_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "patch_availability_state": "deferred",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize frontend contract observations",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                "patch_apply_state": patch_apply_state,
            },
        }
    ]
    written_paths = (
        [".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"]
        if apply_result == "applied"
        else []
    )
    apply_summaries = (
        ["applied 1 provider patch file(s) from readonly patch handoff"]
        if apply_result == "applied"
        else ["no files written in guarded patch apply baseline"]
    )
    warnings = (
        []
        if apply_result == "applied"
        else ["guarded patch apply baseline does not apply patches yet"]
    )
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-provider-patch-apply" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T20:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "handoff_source_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                "handoff_generated_at": "2026-04-03T19:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "patch_availability_state": (
                    "patches_generated" if apply_result == "applied" else "deferred"
                ),
                "patch_apply_state": patch_apply_state,
                "apply_result": apply_result,
                "apply_summaries": apply_summaries,
                "written_paths": written_paths,
                "remaining_blockers": list(remaining_blockers),
                "warnings": warnings,
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": patch_apply_state,
                    "apply_result": apply_result,
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_cross_spec_writeback_artifact(
    root: Path,
    *,
    orchestration_result: str,
    writeback_state: str,
    remaining_blockers: list[str],
    apply_result: str | None = None,
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "writeback_state": writeback_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize frontend contract observations",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "cross_spec_writeback_state": writeback_state,
                "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
            },
        }
    ]
    effective_apply_result = (
        apply_result
        if apply_result is not None
        else ("applied" if orchestration_result == "completed" else "deferred")
    )
    orchestration_summaries = (
        ["wrote 1 cross-spec writeback file(s) from canonical patch apply artifact"]
        if orchestration_result == "completed"
        else ["no cross-spec writes executed in guarded writeback baseline"]
    )
    written_paths = (
        ["specs/001-auth/frontend-provider-writeback.md"]
        if orchestration_result == "completed"
        else []
    )
    existing_written_paths = (
        [".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"]
        if effective_apply_result == "applied"
        else []
    )
    warnings = (
        []
        if orchestration_result == "completed"
        else ["guarded cross-spec writeback baseline does not execute writes yet"]
    )
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-cross-spec-writeback" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T21:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                "artifact_generated_at": "2026-04-03T20:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "apply_result": effective_apply_result,
                "writeback_state": writeback_state,
                "orchestration_result": orchestration_result,
                "orchestration_summaries": orchestration_summaries,
                "existing_written_paths": existing_written_paths,
                "written_paths": written_paths,
                "remaining_blockers": list(remaining_blockers),
                "warnings": warnings,
                "steps": list(effective_steps),
                "source_linkage": {
                    "cross_spec_writeback_state": writeback_state,
                    "orchestration_result": orchestration_result,
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_guarded_registry_artifact(
    root: Path,
    *,
    registry_result: str,
    registry_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "registry_state": registry_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize frontend contract observations",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "registry_state": registry_state,
                "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
            },
        }
    ]
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-guarded-registry" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T22:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                "artifact_generated_at": "2026-04-03T21:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "writeback_state": "deferred",
                "registry_state": registry_state,
                "registry_result": registry_result,
                "registry_summaries": [
                    "no registry updates executed in guarded registry baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded registry baseline does not update registries yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "registry_state": registry_state,
                    "registry_result": registry_result,
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_broader_governance_artifact(
    root: Path,
    *,
    governance_result: str,
    governance_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-broader-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "governance_state": governance_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize broader governance review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "governance_state": governance_state,
                "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T23:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                "artifact_generated_at": "2026-04-03T22:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "registry_state": "deferred",
                "governance_state": governance_state,
                "governance_result": governance_result,
                "governance_summaries": [
                    "no broader governance actions executed in broader governance baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "broader governance baseline does not execute final governance actions yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "registry_state": "deferred",
                    "governance_state": governance_state,
                    "governance_result": governance_result,
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_governance_artifact(
    root: Path,
    *,
    final_governance_result: str,
    final_governance_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "final_governance_state": final_governance_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize writeback persistence review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "final_governance_state": final_governance_state,
                "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T00:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                "artifact_generated_at": "2026-04-03T23:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "governance_state": "deferred",
                "final_governance_state": final_governance_state,
                "final_governance_result": final_governance_result,
                "final_governance_summaries": [
                    "no final governance actions executed in final governance baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final governance baseline does not execute code rewrite persistence yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "governance_state": "deferred",
                    "final_governance_state": final_governance_state,
                    "final_governance_result": final_governance_result,
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_writeback_persistence_artifact(
    root: Path,
    *,
    persistence_result: str,
    persistence_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-writeback-persistence" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "persistence_state": persistence_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize persisted write proof review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "persistence_state": persistence_state,
                "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T01:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                "artifact_generated_at": "2026-04-04T00:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "final_governance_state": "deferred",
                "persistence_state": persistence_state,
                "persistence_result": persistence_result,
                "persistence_summaries": [
                    "no writeback persistence actions executed in writeback persistence baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "writeback persistence baseline does not produce persisted write proof yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "persistence_state": persistence_state,
                    "persistence_result": persistence_result,
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_persisted_write_proof_artifact(
    root: Path,
    *,
    proof_result: str,
    proof_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-persisted-write-proof" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "proof_state": proof_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof publication review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "proof_state": proof_state,
                "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T02:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                "artifact_generated_at": "2026-04-04T01:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "persistence_state": "deferred",
                "proof_state": proof_state,
                "proof_result": proof_result,
                "proof_summaries": [
                    "no persisted write proof actions executed in persisted write proof baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "persisted write proof baseline does not persist proof artifacts yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "persistence_state": "deferred",
                    "proof_state": proof_state,
                    "proof_result": proof_result,
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_publication_artifact(
    root: Path,
    *,
    publication_result: str,
    publication_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-publication" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "publication_state": publication_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof closure review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "publication_state": publication_state,
                "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T03:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                "artifact_generated_at": "2026-04-04T02:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "proof_state": "deferred",
                "publication_state": publication_state,
                "publication_result": publication_result,
                "publication_summaries": [
                    "no final proof publication actions executed in final proof publication baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof publication baseline does not persist publication artifacts yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "proof_state": "deferred",
                    "publication_state": publication_state,
                    "publication_result": publication_result,
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_closure_artifact(
    root: Path,
    *,
    closure_result: str,
    closure_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-closure" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "closure_state": "not_started",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof archive review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "closure_state": closure_state,
                "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T04:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                "artifact_generated_at": "2026-04-04T03:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "publication_state": "deferred",
                "closure_state": closure_state,
                "closure_result": closure_result,
                "closure_summaries": [
                    "no final proof closure actions executed in final proof closure baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof closure baseline does not persist closure artifacts yet"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "publication_state": "deferred",
                    "closure_state": closure_state,
                    "closure_result": closure_result,
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_archive_artifact(
    root: Path,
    *,
    archive_result: str,
    archive_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-archive" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "archive_state": "not_started",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize bounded thread archive context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "archive_state": archive_state,
                "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
            },
        }
    ]
    effective_steps = default_steps if steps is None else steps
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T05:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                "artifact_generated_at": "2026-04-04T04:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "closure_state": "deferred",
                "archive_state": archive_state,
                "archive_result": archive_result,
                "archive_summaries": [
                    "no final proof archive actions executed in final proof archive baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof archive baseline defers thread archive and cleanup actions"
                ],
                "steps": list(effective_steps),
                "source_linkage": {
                    "closure_state": "deferred",
                    "archive_state": archive_state,
                    "archive_result": archive_result,
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                    "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
    root: Path,
    *,
    cleanup_targets: object,
    cleanup_target_eligibility: object | None = None,
    cleanup_preview_plan: object | None = None,
    cleanup_mutation_proposal: object | None = None,
    cleanup_mutation_proposal_approval: object | None = None,
    cleanup_mutation_execution_gating: object | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-archive-project-cleanup" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": "2026-04-04T07:00:00Z",
        "manifest_path": "program-manifest.yaml",
        "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
        "artifact_generated_at": "2026-04-04T05:00:00Z",
        "required": True,
        "confirmation_required": True,
        "confirmed": True,
        "thread_archive_state": "deferred",
        "thread_archive_result": "deferred",
        "project_cleanup_state": "deferred",
        "project_cleanup_result": "deferred",
        "cleanup_targets_state": "seeded",
        "cleanup_targets": cleanup_targets,
        "project_cleanup_summaries": [
            "seeded cleanup target truth for consumption tests"
        ],
        "written_paths": [],
        "remaining_blockers": ["spec 001-auth remediation still required"],
        "warnings": [],
        "steps": [],
        "source_linkage": {
            "thread_archive_state": "deferred",
            "thread_archive_result": "deferred",
            "project_cleanup_state": "deferred",
            "project_cleanup_result": "deferred",
            "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
            "final_proof_archive_project_cleanup_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml",
        },
    }
    if cleanup_target_eligibility is not None:
        payload["cleanup_target_eligibility"] = cleanup_target_eligibility
    if cleanup_preview_plan is not None:
        payload["cleanup_preview_plan"] = cleanup_preview_plan
    if cleanup_mutation_proposal is not None:
        payload["cleanup_mutation_proposal"] = cleanup_mutation_proposal
    if cleanup_mutation_proposal_approval is not None:
        payload["cleanup_mutation_proposal_approval"] = (
            cleanup_mutation_proposal_approval
        )
    if cleanup_mutation_execution_gating is not None:
        payload["cleanup_mutation_execution_gating"] = (
            cleanup_mutation_execution_gating
        )
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
