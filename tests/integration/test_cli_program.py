"""Integration tests for ai-sdlc program CLI commands."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import yaml
from typer.testing import CliRunner

import ai_sdlc.core.program_service as program_service_module
from ai_sdlc.cli.main import app
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
from ai_sdlc.models.project import ProjectConfig

runner = CliRunner()
SAMPLE_FIXTURE_SOURCE_REF = "tests/fixtures/frontend-contract-sample-src/match"


def _write_manifest(root: Path) -> None:
    (root / "specs" / "001-auth").mkdir(parents=True)
    (root / "specs" / "002-course").mkdir(parents=True)
    (root / "specs" / "003-enroll").mkdir(parents=True)
    (root / "program-manifest.yaml").write_text(
        """
schema_version: "1"
specs:
  - id: "001-auth"
    path: "specs/001-auth"
    depends_on: []
  - id: "002-course"
    path: "specs/002-course"
    depends_on: []
  - id: "003-enroll"
    path: "specs/003-enroll"
    depends_on: ["001-auth", "002-course"]
""".strip()
        + "\n",
        encoding="utf-8",
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


def _write_frontend_solution_confirmation_artifacts(root: Path, *, snapshot=None) -> None:
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


def test_program_page_ui_schema_handoff_blocks_without_solution_snapshot(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "page-ui-schema-handoff"])

    assert result.exit_code == 1
    assert "Frontend Page/UI Schema Handoff" in result.output
    assert "state: blocked" in result.output
    assert "frontend_solution_snapshot_missing" in result.output


def test_program_page_ui_schema_handoff_surfaces_provider_style_and_schema_entries(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    _write_frontend_solution_confirmation_artifacts(root)

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "page-ui-schema-handoff"])

    assert result.exit_code == 0
    assert "Frontend Page/UI Schema Handoff" in result.output
    assert "state: ready" in result.output
    assert "provider: public-primevue" in result.output
    assert "style pack: modern-saas" in result.output
    assert "dashboard-workspace" in result.output
    assert "search-list-workspace" in result.output


def test_program_theme_token_governance_handoff_blocks_without_solution_snapshot(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "theme-token-governance-handoff"])

    assert result.exit_code == 1
    assert "Frontend Theme Token Governance Handoff" in result.output
    assert "state: blocked" in result.output
    assert "frontend_solution_snapshot_missing" in result.output


def test_program_theme_token_governance_handoff_surfaces_requested_effective_theme_and_override_diagnostics(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    _write_builtin_delivery_truth(
        root,
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

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "theme-token-governance-handoff"])

    assert result.exit_code == 0
    assert "Frontend Theme Token Governance Handoff" in result.output
    assert "state: ready" in result.output
    assert "provider: enterprise-vue2" in result.output
    assert "requested style pack: enterprise-default" in result.output
    assert "effective style pack: enterprise-default" in result.output
    assert "dashboard-workspace" in result.output
    assert "dashboard-page-header-accent-proposal" in result.output
    assert "requested: brand-accent" in result.output


def test_program_quality_platform_handoff_blocks_without_solution_snapshot(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "quality-platform-handoff"])

    assert result.exit_code == 1
    assert "Frontend Quality Platform Handoff" in result.output
    assert "state: blocked" in result.output
    assert "frontend_solution_snapshot_missing" in result.output


def test_program_quality_platform_handoff_surfaces_matrix_and_quality_diagnostics(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    _write_builtin_delivery_truth(
        root,
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
        root,
        platform=build_p2_frontend_quality_platform_baseline(),
    )

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "quality-platform-handoff"])

    assert result.exit_code == 0
    assert "Frontend Quality Platform Handoff" in result.output
    assert "state: ready" in result.output
    assert "provider: public-primevue" in result.output
    assert "requested style pack: modern-saas" in result.output
    assert "effective style pack: modern-saas" in result.output
    assert "matrix coverage: 3" in result.output
    assert "page schema: dashboard-workspace" in result.output
    assert "page schema: search-list-workspace" in result.output
    assert "quality diagnostic: dashboard-modern-saas-desktop-chromium" in result.output


def test_program_provider_expansion_handoff_blocks_without_solution_snapshot(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "provider-expansion-handoff"])

    assert result.exit_code == 1
    assert "Frontend Provider Expansion Handoff" in result.output
    assert "state: blocked" in result.output
    assert "frontend_solution_snapshot_missing" in result.output


def test_program_provider_expansion_handoff_surfaces_provider_and_react_visibility_diagnostics(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    _write_builtin_delivery_truth(
        root,
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
        root,
        expansion=build_p3_frontend_provider_expansion_baseline(),
    )

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "provider-expansion-handoff"])

    assert result.exit_code == 0
    assert "Frontend Provider Expansion Handoff" in result.output
    assert "state: ready" in result.output
    assert "provider: public-primevue" in result.output
    assert "requested frontend stack: vue3" in result.output
    assert "effective frontend stack: vue3" in result.output
    assert "react stack visibility: hidden" in result.output
    assert "react binding visibility: hidden" in result.output
    assert "provider diagnostic: public-primevue" in result.output
    assert "provider diagnostic: react-nextjs-shadcn" in result.output


def test_program_provider_runtime_adapter_handoff_blocks_without_solution_snapshot(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "provider-runtime-adapter-handoff"])

    assert result.exit_code == 1
    assert "Frontend Provider Runtime Adapter Handoff" in result.output
    assert "state: blocked" in result.output
    assert "frontend_solution_snapshot_missing" in result.output


def test_program_provider_runtime_adapter_handoff_surfaces_scaffold_and_delivery_state(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir
    _write_builtin_delivery_truth(
        root,
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
        root,
        runtime_adapter=build_p3_target_project_adapter_scaffold_baseline(),
    )

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "provider-runtime-adapter-handoff"])

    assert result.exit_code == 0
    assert "Frontend Provider Runtime Adapter Handoff" in result.output
    assert "state: ready" in result.output
    assert "provider: public-primevue" in result.output
    assert "requested frontend stack: vue3" in result.output
    assert "effective frontend stack: vue3" in result.output
    assert "carrier mode: target-project-adapter-layer" in result.output
    assert "runtime delivery state: scaffolded" in result.output
    assert "evidence return state: missing" in result.output
    assert "provider diagnostic: public-primevue" in result.output
    assert "provider diagnostic: react-nextjs-shadcn" in result.output


def test_program_cross_provider_consistency_handoff_surfaces_pair_truth(
    initialized_project_dir: Path,
) -> None:
    root = initialized_project_dir

    with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
        result = runner.invoke(app, ["program", "cross-provider-consistency-handoff"])

    assert result.exit_code == 1
    assert "Frontend Cross Provider Consistency Handoff" in result.output
    assert "state: blocked" in result.output
    assert "pair count: 3" in result.output
    assert "ready pairs: 1" in result.output
    assert "conditional pairs: 1" in result.output
    assert "blocked pairs: 1" in result.output
    assert (
        "pair diagnostic: enterprise-vue2__public-primevue__dashboard-workspace"
        in result.output
    )
    assert (
        "pair diagnostic: enterprise-vue2__public-primevue__wizard-workspace"
        in result.output
    )
    assert "certification gate remains blocked" in result.output


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


def _build_host_runtime_plan_for_tests(
    *,
    node_runtime_available: bool | None,
    package_manager_available: bool | None,
    playwright_browsers_available: bool | None,
):
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


def _write_program_truth_fixture(root: Path) -> None:
    spec_dir = root / "specs" / "001-auth"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text("- [ ] pending\n", encoding="utf-8")
    _write_manifest_yaml(
        root,
        """
schema_version: "2"
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
      - "001-auth"
    required_evidence:
      truth_check_refs:
        - "specs/001-auth"
      close_check_refs:
        - "specs/001-auth"
      verify_refs:
        - "uv run ai-sdlc verify constraints"
capability_closure_audit:
  reviewed_at: "2026-04-14T12:00:00Z"
  open_clusters:
    - cluster_id: "frontend-mainline-delivery"
      title: "Frontend Mainline Delivery"
      closure_state: "capability_open"
      summary: "Delivery capability is still open."
      source_refs:
        - "001-auth"
specs:
  - id: "001-auth"
    path: "specs/001-auth"
    depends_on: []
    roles:
      - "runtime_carrier"
    capability_refs:
      - "frontend-mainline-delivery"
""",
    )


def _write_managed_delivery_apply_request(root: Path, *, fingerprint: str = "fp-001") -> str:
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
    rel = ".ai-sdlc/memory/frontend-managed-delivery/apply-request.yaml"
    request_path = root / rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return rel


def _write_artifact_generate_apply_request(root: Path) -> str:
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
                                "content": "<template>cli generated</template>\n",
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
    rel = ".ai-sdlc/memory/frontend-managed-delivery/apply-request-artifact.yaml"
    request_path = root / rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return rel


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
        generated_at="2026-04-03T15:30:00Z",
        source_ref=source_ref,
        source_digest="sha256:cli-program",
        source_revision="rev-cli-program",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_frontend_visual_a11y_evidence(spec_dir: Path) -> None:
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id=f"{spec_dir.name}-visual-a11y-pass",
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
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T15:30:00Z",
    )
    write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)


def _write_frontend_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


def _write_p1_frontend_gate_artifacts(root: Path) -> None:
    materialize_frontend_gate_policy_artifacts(
        root,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        root,
        build_mvp_frontend_generation_constraints(),
    )


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


class TestCliProgram:
    def test_program_managed_delivery_apply_dry_run_blocks_on_host_ingress(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="materialized"))
        request_rel = _write_managed_delivery_apply_request(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "managed-delivery-apply", "--request", request_rel, "--dry-run"],
            )

        assert result.exit_code == 1
        assert "Program Managed Delivery Apply Dry-Run" in result.output
        assert "host_ingress_below_mutate_threshold" in result.output

    def test_program_managed_delivery_apply_execute_surfaces_honest_headline(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        request_rel = _write_managed_delivery_apply_request(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "managed-delivery-apply",
                    "--request",
                    request_rel,
                    "--execute",
                    "--yes",
                ],
            )

        assert result.exit_code == 0
        assert "Program Managed Delivery Apply Execute" in result.output
        assert "delivery is not complete" in result.output.lower()
        assert "browser gate has not run" in result.output.lower()
        assert "delivery complete: false" in result.output.lower()
        assert "next required gate: browser_gate" in result.output.lower()
        assert "selected managed-target actions from the confirmed plan" in result.output.lower()

    def test_program_managed_delivery_apply_execute_writes_managed_artifacts(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        request_rel = _write_artifact_generate_apply_request(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "managed-delivery-apply",
                    "--request",
                    request_rel,
                    "--execute",
                    "--yes",
                ],
            )

        assert result.exit_code == 0
        assert "selected action types: artifact_generate" in result.output
        assert "managed target path: managed/frontend" in result.output
        assert "apply artifact: .ai-sdlc/memory/frontend-managed-delivery-apply/latest.yaml" in result.output
        assert (
            root / "managed" / "frontend" / "src" / "App.vue"
        ).read_text(encoding="utf-8") == "<template>cli generated</template>\n"

    def test_program_managed_delivery_apply_dry_run_materializes_request_from_truth_when_request_omitted(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        _write_builtin_delivery_truth(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root), patch.object(
            program_service_module,
            "evaluate_current_host_runtime",
            return_value=_build_host_runtime_plan_for_tests(
                node_runtime_available=True,
                package_manager_available=True,
                playwright_browsers_available=True,
            ),
        ):
            result = runner.invoke(app, ["program", "managed-delivery-apply", "--dry-run"])

        assert result.exit_code == 0
        assert "Program Managed Delivery Apply Dry-Run" in result.output
        assert "request source: .ai-sdlc/memory/frontend-managed-delivery/latest.yaml" in result.output
        assert "selected action types: managed_target_prepare, dependency_install" in result.output

    def test_program_managed_delivery_apply_dry_run_surfaces_private_registry_blocker_from_truth_when_request_omitted(
        self, initialized_project_dir: Path
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

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root), patch.object(
            program_service_module,
            "evaluate_current_host_runtime",
            return_value=_build_host_runtime_plan_for_tests(
                node_runtime_available=True,
                package_manager_available=True,
                playwright_browsers_available=True,
            ),
        ):
            result = runner.invoke(app, ["program", "managed-delivery-apply", "--dry-run"])

        assert result.exit_code == 1
        assert "private_registry_prerequisite_missing:company-registry-token" in result.output
        assert "Enterprise package access is not ready" in result.output
        assert "provide company-registry-token and rerun" in result.output

    def test_program_browser_gate_probe_execute_materializes_gate_run_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        _write_frontend_solution_confirmation_artifacts(root)
        _write_frontend_visual_a11y_evidence(root / "specs" / "001-auth")
        request_rel = _write_artifact_generate_apply_request(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            apply_result = runner.invoke(
                app,
                [
                    "program",
                    "managed-delivery-apply",
                    "--request",
                    request_rel,
                    "--execute",
                    "--yes",
                ],
            )
            probe_result = runner.invoke(app, ["program", "browser-gate-probe", "--execute"])

        assert apply_result.exit_code == 0
        assert probe_result.exit_code == 0
        assert "Program Browser Gate Probe Execute" in probe_result.output
        assert "overall gate status: incomplete" in probe_result.output
        assert "execute gate state: recheck_required" in probe_result.output
        assert "next command: uv run ai-sdlc program browser-gate-probe --execute" in probe_result.output
        latest_artifact = (
            root / ".ai-sdlc" / "memory" / "frontend-browser-gate" / "latest.yaml"
        )
        payload = yaml.safe_load(latest_artifact.read_text(encoding="utf-8"))
        gate_run_id = payload["gate_run_id"]
        assert payload["bundle_input"]["gate_run_id"] == gate_run_id
        assert all(gate_run_id in record["artifact_ref"] for record in payload["artifact_records"])

    def test_program_browser_gate_probe_dry_run_does_not_materialize_preview_artifacts(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        _write_frontend_solution_confirmation_artifacts(root)
        _write_frontend_visual_a11y_evidence(root / "specs" / "001-auth")
        request_rel = _write_artifact_generate_apply_request(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            runner.invoke(
                app,
                [
                    "program",
                    "managed-delivery-apply",
                    "--request",
                    request_rel,
                    "--execute",
                    "--yes",
                ],
            )
            probe_result = runner.invoke(app, ["program", "browser-gate-probe", "--dry-run"])

        assert probe_result.exit_code == 0
        assert not (
            root
            / ".ai-sdlc"
            / "artifacts"
            / "frontend-browser-gate"
            / "gate-run-preview"
        ).exists()

    def test_program_browser_gate_probe_execute_surfaces_plain_language_runner_failure(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        _write_frontend_solution_confirmation_artifacts(root)
        _write_frontend_visual_a11y_evidence(root / "specs" / "001-auth")
        request_rel = _write_artifact_generate_apply_request(root)

        def _runner(*, artifact_root: Path, execution_context, generated_at: str):
            return BrowserGateProbeRunnerResult(
                runtime_status="failed_transient",
                shared_capture=BrowserGateSharedRuntimeCapture(
                    gate_run_id=execution_context.gate_run_id,
                    trace_artifact_ref="",
                    navigation_screenshot_ref="",
                    capture_status="capture_failed",
                    final_url="",
                    anchor_refs=[],
                    diagnostic_codes=["playwright_runtime_unavailable"],
                ),
                interaction_capture=BrowserGateInteractionProbeCapture(
                    gate_run_id=execution_context.gate_run_id,
                    interaction_probe_id="primary-action",
                    artifact_refs=[],
                    capture_status="capture_failed",
                    classification_candidate="transient_run_failure",
                    blocking_reason_codes=["playwright_runtime_unavailable"],
                    anchor_refs=[],
                ),
                diagnostic_codes=["playwright_runtime_unavailable"],
                warnings=["Playwright runtime is not available on this host."],
            )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root), patch(
            "ai_sdlc.core.frontend_browser_gate_runtime.run_default_browser_gate_probe",
            side_effect=_runner,
        ):
            apply_result = runner.invoke(
                app,
                [
                    "program",
                    "managed-delivery-apply",
                    "--request",
                    request_rel,
                    "--execute",
                    "--yes",
                ],
            )
            probe_result = runner.invoke(app, ["program", "browser-gate-probe", "--execute"])

        assert apply_result.exit_code == 0
        assert probe_result.exit_code == 0
        assert "execute gate state: recheck_required" in probe_result.output
        assert "Playwright runtime is not available on this host." in probe_result.output
        assert "next command: uv run ai-sdlc program browser-gate-probe --execute" in probe_result.output

    def test_program_remediate_dry_run_surfaces_browser_gate_follow_up_command(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        save_project_config(root, ProjectConfig(adapter_ingress_state="verified_loaded"))
        _write_frontend_solution_confirmation_artifacts(root)
        issue_artifact = build_frontend_visual_a11y_evidence_artifact(
            evaluations=[
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
            provider_kind="manual",
            provider_name="test-fixture",
            generated_at="2026-04-07T15:30:00Z",
        )
        write_frontend_visual_a11y_evidence_artifact(
            root / "specs" / "001-auth",
            issue_artifact,
        )
        request_rel = _write_artifact_generate_apply_request(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            apply_result = runner.invoke(
                app,
                [
                    "program",
                    "managed-delivery-apply",
                    "--request",
                    request_rel,
                    "--execute",
                    "--yes",
                ],
            )
            probe_result = runner.invoke(app, ["program", "browser-gate-probe", "--execute"])
            payload = yaml.safe_load(
                (
                    root
                    / ".ai-sdlc"
                    / "memory"
                    / "frontend-browser-gate"
                    / "latest.yaml"
                ).read_text(encoding="utf-8")
            )
            payload["overall_gate_status"] = "blocked"
            payload["bundle_input"]["overall_gate_status"] = "blocked"
            for receipt in payload["bundle_input"]["check_receipts"]:
                if receipt["check_name"] in {
                    "playwright_smoke",
                    "interaction_anti_pattern_checks",
                }:
                    receipt["classification_candidate"] = "pass"
                    receipt["recheck_required"] = False
                    receipt["blocking_reason_codes"] = []
                    receipt["remediation_hints"] = []
                    receipt["runtime_status"] = "completed"
                else:
                    receipt["classification_candidate"] = "actual_quality_blocker"
                    receipt["blocking_reason_codes"] = [
                        "visual_a11y_quality_blocker"
                    ]
                    receipt["remediation_hints"] = [
                        "review frontend visual / a11y issue findings"
                    ]
            payload["bundle_input"]["blocking_reason_codes"] = [
                "visual_a11y_quality_blocker"
            ]
            (
                root
                / ".ai-sdlc"
                / "memory"
                / "frontend-browser-gate"
                / "latest.yaml"
            ).write_text(
                yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            remediate_result = runner.invoke(app, ["program", "remediate", "--dry-run"])

        assert apply_result.exit_code == 0
        assert probe_result.exit_code == 0
        assert remediate_result.exit_code == 0
        assert "uv run ai-sdlc program browser-gate-probe --execute" in remediate_result.output

    def test_program_validate_pass(self, initialized_project_dir: Path) -> None:
        _write_manifest(initialized_project_dir)
        with patch(
            "ai_sdlc.cli.program_cmd.find_project_root",
            return_value=initialized_project_dir,
        ):
            result = runner.invoke(app, ["program", "validate"])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_program_validate_fail_cycle(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        (root / "specs" / "a").mkdir(parents=True)
        (root / "specs" / "b").mkdir(parents=True)
        (root / "program-manifest.yaml").write_text(
            """
specs:
  - id: a
    path: specs/a
    depends_on: [b]
  - id: b
    path: specs/b
    depends_on: [a]
""".strip()
            + "\n",
            encoding="utf-8",
        )
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "validate"])
        assert result.exit_code == 1
        assert "cycle" in result.output.lower()

    def test_program_validate_fail_frontend_evidence_class_mirror_missing(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_frontend_evidence_class_spec(
            root,
            spec_rel="specs/082-frontend-example",
            frontend_evidence_class="framework_capability",
        )
        (root / "program-manifest.yaml").write_text(
            """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
""".strip()
            + "\n",
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "validate"])

        assert result.exit_code == 1
        assert "frontend_evidence_class_mirror_drift" in result.output
        assert "mirror_missing" in result.output

    def test_program_frontend_evidence_class_sync_execute_updates_manifest(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_frontend_evidence_class_spec(
            root,
            spec_rel="specs/082-frontend-example",
            frontend_evidence_class="framework_capability",
        )
        _write_manifest_yaml(
            root,
            """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
""",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "frontend-evidence-class-sync", "--execute", "--yes"],
            )

        assert result.exit_code == 0
        assert "updated" in result.output
        payload = yaml.safe_load((root / "program-manifest.yaml").read_text(encoding="utf-8"))
        assert payload["specs"][0]["frontend_evidence_class"] == "framework_capability"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            validate = runner.invoke(app, ["program", "validate"])
        assert validate.exit_code == 0

    def test_program_frontend_evidence_class_sync_targeted_updates_only_selected_spec(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_frontend_evidence_class_spec(
            root,
            spec_rel="specs/082-frontend-example",
            frontend_evidence_class="framework_capability",
        )
        _write_frontend_evidence_class_spec(
            root,
            spec_rel="specs/083-frontend-adoption",
            frontend_evidence_class="consumer_adoption",
        )
        _write_manifest_yaml(
            root,
            """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
  - id: "083-frontend-adoption"
    path: "specs/083-frontend-adoption"
    depends_on: []
""",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "frontend-evidence-class-sync",
                    "--spec-id",
                    "082-frontend-example",
                    "--execute",
                    "--yes",
                ],
            )

        assert result.exit_code == 0
        payload = yaml.safe_load((root / "program-manifest.yaml").read_text(encoding="utf-8"))
        specs = {item["id"]: item for item in payload["specs"]}
        assert specs["082-frontend-example"]["frontend_evidence_class"] == "framework_capability"
        assert "frontend_evidence_class" not in specs["083-frontend-adoption"]

    def test_program_status_and_plan(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        (root / "specs" / "001-auth" / "tasks.md").write_text(
            "- [x] done\n- [ ] todo\n", encoding="utf-8"
        )
        (root / "specs" / "002-course" / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            status = runner.invoke(app, ["program", "status"])
            plan = runner.invoke(app, ["program", "plan"])

        assert status.exit_code == 0
        assert "Program Status" in status.output
        assert "001-auth" in status.output
        assert "003-enroll" in status.output

        assert plan.exit_code == 0
        assert "Program Plan" in plan.output
        assert "003-enroll" in plan.output

    def test_program_truth_sync_and_audit_surface_blocked_release_state(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _init_truth_git_repo(root)
        _write_program_truth_fixture(root)
        _commit_truth_repo(root, "docs: seed truth ledger fixture")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            sync = runner.invoke(
                app,
                ["program", "truth", "sync", "--execute", "--yes"],
            )
            audit = runner.invoke(app, ["program", "truth", "audit"])
            status = runner.invoke(app, ["program", "status"])

        assert sync.exit_code == 0, sync.output
        assert "Program Truth Sync Execute" in sync.output
        payload = yaml.safe_load((root / "program-manifest.yaml").read_text(encoding="utf-8"))
        snapshot = payload["truth_snapshot"]
        assert snapshot["state"] == "blocked"
        assert snapshot["computed_capabilities"] == [
            {
                "capability_id": "frontend-mainline-delivery",
                "closure_state": "capability_open",
                "audit_state": "blocked",
                "blocking_refs": snapshot["computed_capabilities"][0]["blocking_refs"],
                "stale_reason": "",
            }
        ]
        assert any(
            "capability_closure_audit:capability_open" in blocker
            for blocker in snapshot["computed_capabilities"][0]["blocking_refs"]
        )

        assert audit.exit_code == 1, audit.output
        assert "Program Truth Audit" in audit.output
        assert "state: blocked" in audit.output.lower()
        assert "snapshot state: fresh" in audit.output.lower()
        assert "frontend-mainline-delivery" in audit.output

        assert status.exit_code == 0, status.output
        assert "Truth Ledger" in status.output
        assert "blocked" in status.output.lower()

    def test_program_truth_sync_and_audit_surface_exposes_source_inventory_migration(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _init_truth_git_repo(root)
        _write_program_truth_fixture(root)
        (root / "docs" / "superpowers" / "specs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "superpowers" / "specs" / "2026-04-02-design.md").write_text(
            "# Design\n\nP2 modern provider\n",
            encoding="utf-8",
        )
        (root / "docs" / "framework-defect-backlog.zh-CN.md").write_text(
            "# backlog\n\n后续治理\n",
            encoding="utf-8",
        )
        _commit_truth_repo(root, "docs: seed truth ledger source inventory fixture")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            sync = runner.invoke(
                app,
                ["program", "truth", "sync", "--execute", "--yes"],
            )
            audit = runner.invoke(app, ["program", "truth", "audit"])

        assert sync.exit_code == 0, sync.output
        assert "source inventory: incomplete" in sync.output.lower()
        assert "unmapped sources: 2" in sync.output.lower()

        assert audit.exit_code == 1, audit.output
        assert "source inventory: incomplete" in audit.output.lower()
        assert "unmapped sources: 2" in audit.output.lower()
        assert "docs/superpowers/specs/2026-04-02-design.md" in audit.output

    def test_program_status_exposes_next_required_truth_action_when_snapshot_is_stale(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _init_truth_git_repo(root)
        _write_program_truth_fixture(root)
        _commit_truth_repo(root, "docs: seed truth ledger fixture")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            sync = runner.invoke(
                app,
                ["program", "truth", "sync", "--execute", "--yes"],
            )

        assert sync.exit_code == 0, sync.output

        payload = yaml.safe_load((root / "program-manifest.yaml").read_text(encoding="utf-8"))
        payload["program"]["goal"] = "Changed after truth sync"
        (root / "program-manifest.yaml").write_text(
            yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            status = runner.invoke(app, ["program", "status"])

        assert status.exit_code == 0, status.output
        assert "Truth Ledger" in status.output
        assert "snapshot state: stale" in status.output.lower()
        assert "next action" in status.output.lower()
        assert "python -m ai_sdlc program truth sync --execute --yes" in status.output

    def test_program_status_exposes_terminal_truth_sync_guidance_when_snapshot_is_stale_but_current_recompute_is_ready(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _init_truth_git_repo(root)
        _write_program_truth_fixture(root)
        _commit_truth_repo(root, "docs: seed truth ledger fixture")

        with (
            patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root),
            patch.object(
                program_service_module.ProgramService,
                "build_truth_ledger_surface",
                return_value={
                    "state": "stale",
                    "snapshot_state": "stale",
                    "detail": (
                        "persisted truth snapshot is stale; current recompute is ready. "
                        "Refresh the snapshot as the terminal close-out step, then rerun program truth audit."
                    ),
                    "next_required_actions": [
                        "python -m ai_sdlc program truth sync --execute --yes"
                    ],
                    "next_required_action": "python -m ai_sdlc program truth sync --execute --yes",
                    "snapshot_hash": "abc123",
                    "release_targets": ["frontend-mainline-delivery"],
                    "release_capabilities": [
                        {
                            "capability_id": "frontend-mainline-delivery",
                            "closure_state": "closed",
                            "audit_state": "ready",
                            "blocking_refs": [],
                        }
                    ],
                    "migration_pending_count": 0,
                    "migration_pending_specs": [],
                    "migration_pending_sources": [],
                    "migration_suggestions": [],
                    "source_inventory": None,
                    "validation_errors": [],
                    "validation_warnings": [],
                },
            ),
        ):
            status = runner.invoke(app, ["program", "status"])

        assert status.exit_code == 0, status.output
        assert "Truth Ledger" in status.output
        assert "snapshot state: stale" in status.output.lower()
        assert "current recompute is ready" in status.output
        assert "terminal close-out step" in status.output
        assert "python -m ai_sdlc program truth sync --execute --yes" in status.output

    def test_program_status_exposes_frontend_readiness(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        _write_frontend_contract_observations(root / "specs" / "001-auth")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 0
        assert "Frontend" in result.output
        assert "ready" in result.output
        assert "missing_artifact" in result.output
        assert "scope_or_linkage_invalid" in result.output

    def test_program_status_waives_observation_gap_for_framework_capability(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_evidence_class_spec(
            root,
            spec_rel="specs/001-auth",
            frontend_evidence_class="framework_capability",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 0
        assert "001-auth" in result.output
        assert "advisory_only" in result.output
        assert "001-auth: ready / advisory_only" in result.output

    def test_program_status_exposes_frontend_execute_gate_recheck_required(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        _write_frontend_contract_observations(root / "specs" / "001-auth")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 0
        assert "retry / recheck_required" in result.output
        assert "evidence_missing" in result.output
        assert "frontend_visual_a11y_evidence_input" in result.output

    def test_program_status_exposes_frontend_execute_gate_blocked_for_policy_artifact_gap(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).unlink()
        _write_frontend_contract_observations(root / "specs" / "001-auth")

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 0
        assert "retry / blocked" in result.output
        assert "result_inconsistency" in result.output
        assert "frontend_visual_a11y_policy_artifacts" in result.output
        assert "recheck_required" not in result.output

    def test_program_status_exposes_frontend_execute_gate_needs_remediation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        spec_dir = root / "specs" / "001-auth"
        _write_frontend_contract_observations(spec_dir)
        artifact = build_frontend_visual_a11y_evidence_artifact(
            evaluations=[
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
            provider_kind="manual",
            provider_name="test-fixture",
            generated_at="2026-04-07T17:15:00Z",
        )
        write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 0
        assert "retry / needs_remediation" in result.output
        assert "actual_quality_blocker" in result.output
        assert "frontend_visual_a11y_issue_review" in result.output

    def test_program_status_exposes_bounded_frontend_evidence_class_summary(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_frontend_evidence_class_spec(
            root,
            spec_rel="specs/082-frontend-example",
            frontend_evidence_class="framework_capability",
        )
        _write_manifest_yaml(
            root,
            """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
""",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 1
        assert "frontend_evidence_class_mirror_drift:mirror_missing" in result.output
        assert "source_of_truth_path=" not in result.output
        assert "human_remediation_hint=" not in result.output

    def test_program_status_best_effort_handles_spec_path_outside_project_root(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        legacy_dir = root.parent / "legacy-spec"
        legacy_dir.mkdir(exist_ok=True)
        (root / "program-manifest.yaml").write_text(
            f"""
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "../{legacy_dir.name}"
    depends_on: []
""".strip()
            + "\n",
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "status"])

        assert result.exit_code == 1, result.output
        assert "Manifest invalid; status shown with best-effort parsing." in result.output
        assert "outside project root" in result.output

    def test_program_integrate_dry_run_with_report(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        report_rel = ".ai-sdlc/memory/program-integration-plan.md"
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--dry-run",
                    "--report",
                    report_rel,
                ],
            )
        assert result.exit_code == 0
        assert "Program Integrate Dry-Run" in result.output
        assert (root / report_rel).is_file()

    def test_program_integrate_dry_run_exposes_frontend_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "integrate", "--dry-run"])

        assert result.exit_code == 0
        assert "Frontend Hint" in result.output
        assert "missing_artifact" in result.output
        assert "frontend_contract_observations" in result.output

    def test_program_integrate_execute_is_blocked(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "integrate", "--execute"])
        assert result.exit_code == 2
        assert "requires explicit confirmation" in result.output

    def test_program_integrate_execute_surfaces_frontend_preflight_failure(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        assert result.exit_code == 1
        assert "Frontend Execute Preflight" in result.output
        assert "missing_artifact" in result.output
        assert "frontend_contract_observations" in result.output

    def test_program_integrate_execute_surfaces_frontend_remediation_handoff(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "materialize frontend contract observations" in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
        )
        assert "re-run ai-sdlc verify constraints" in result.output

    def test_program_integrate_execute_surfaces_frontend_preflight_pass(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        assert result.exit_code == 0
        assert "Frontend Execute Preflight" in result.output
        assert "ready" in result.output
        assert "Execution gates passed" in result.output

    def test_program_integrate_execute_surfaces_visual_a11y_policy_artifact_remediation_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).unlink()
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            _write_frontend_contract_observations(root / "specs" / spec)
        report_rel = ".ai-sdlc/memory/program-integrate-visual-a11y-policy-artifacts.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--execute",
                    "--yes",
                    "--allow-dirty",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "Frontend Recheck Handoff" not in result.output
        assert "frontend_visual_a11y_policy_artifacts" in result.output
        assert "materialize frontend visual / a11y policy artifacts" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Recheck Handoff" not in report
        assert "frontend_visual_a11y_policy_artifacts" in report
        assert "materialize frontend visual / a11y policy artifacts" in report
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in report

    def test_program_integrate_execute_surfaces_stable_empty_visual_a11y_review_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            spec_dir = root / "specs" / spec
            _write_frontend_contract_observations(spec_dir)
            artifact = build_frontend_visual_a11y_evidence_artifact(
                evaluations=[],
                provider_kind="manual",
                provider_name="test-fixture",
                generated_at="2026-04-07T17:00:00Z",
            )
            write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)
        report_rel = ".ai-sdlc/memory/program-integrate-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--execute",
                    "--yes",
                    "--allow-dirty",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "Frontend Recheck Handoff" not in result.output
        assert "review stable empty frontend visual / a11y evidence" in result.output
        assert "materialize frontend visual / a11y evidence input" not in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" not in result.output
        assert "uv run ai-sdlc verify constraints" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Remediation Handoff" in report
        assert "Frontend Recheck Handoff" not in report
        assert "review stable empty frontend visual / a11y evidence" in report
        assert "uv run ai-sdlc verify constraints" in report

    def test_program_integrate_execute_surfaces_visual_a11y_issue_review_hint(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            spec_dir = root / "specs" / spec
            _write_frontend_contract_observations(spec_dir)
            artifact = build_frontend_visual_a11y_evidence_artifact(
                evaluations=[
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
                provider_kind="manual",
                provider_name="test-fixture",
                generated_at="2026-04-07T17:15:00Z",
            )
            write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)
        report_rel = ".ai-sdlc/memory/program-integrate-visual-a11y-issue.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--execute",
                    "--yes",
                    "--allow-dirty",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        assert "Frontend Remediation Handoff" in result.output
        assert "frontend_visual_a11y_issue_review" in result.output
        assert "review frontend visual / a11y issue findings" in result.output
        assert "frontend_visual_a11y_evidence_stable_empty" not in result.output
        assert "materialize frontend visual / a11y evidence input" not in result.output
        assert "uv run ai-sdlc verify constraints" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "uv run ai-sdlc verify constraints" in report

    def test_program_integrate_execute_surfaces_frontend_recheck_handoff(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )

        assert result.exit_code == 0
        assert "Frontend Recheck Handoff" in result.output
        assert "001-auth" in result.output
        assert "uv run ai-sdlc verify constraints" in result.output

    def test_program_integrate_execute_success(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
            _write_frontend_contract_observations(root / "specs" / spec)
        report_rel = ".ai-sdlc/memory/program-integrate-execute.md"
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--execute",
                    "--yes",
                    "--allow-dirty",
                    "--report",
                    report_rel,
                ],
            )
        assert result.exit_code == 0
        assert "Program Integrate Execute (Guarded)" in result.output
        assert (root / report_rel).is_file()
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Recheck Handoff" in report
        assert "uv run ai-sdlc verify constraints" in report

    def test_program_integrate_execute_failure_report_surfaces_remediation_handoff(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        for spec in ("001-auth", "002-course", "003-enroll"):
            (root / "specs" / spec / "development-summary.md").write_text(
                "done\n", encoding="utf-8"
            )
        report_rel = ".ai-sdlc/memory/program-integrate-execute-failure.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "integrate",
                    "--execute",
                    "--yes",
                    "--allow-dirty",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Remediation Handoff" in report
        assert "materialize frontend contract observations" in report
        assert (
            "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
            in report
        )
        assert "re-run ai-sdlc verify constraints" in report

    def test_program_integrate_execute_gate_fail_not_closed(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        (root / "specs" / "001-auth" / "development-summary.md").write_text(
            "done\n", encoding="utf-8"
        )
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "integrate", "--execute", "--yes", "--allow-dirty"],
            )
        assert result.exit_code == 1
        assert "Execution gates failed" in result.output

    def test_program_remediate_dry_run_surfaces_frontend_runbook(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_contract_source_annotation(root)
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "remediate", "--dry-run"])

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 0
        assert "Program Frontend Remediation Dry-Run" in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
        )
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output
        assert "uv run ai-sdlc verify constraints" in result.output

    def test_program_remediate_dry_run_rejects_sample_selfcheck_artifact_as_consumer_evidence(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_gate_artifacts(root)
        _write_frontend_contract_observations(
            root / "specs" / "001-auth",
            provider_kind="scanner",
            provider_name="frontend_contract_scanner",
            source_ref=SAMPLE_FIXTURE_SOURCE_REF,
        )
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "remediate", "--dry-run"])

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 0
        assert "No frontend remediation steps generated." not in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
        )
        assert "uv run ai-sdlc rules materialize-frontend-mvp" not in result.output

    def test_program_remediate_execute_runs_bounded_frontend_commands(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_contract_source_annotation(root)
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "remediate", "--execute", "--yes"],
            )

        normalized_output = "".join(result.output.split())
        assert result.exit_code == 1
        assert "Frontend remediation execute incomplete" in result.output
        assert (
            "uvrunai-sdlcscan<frontend-source-root>--frontend-contract-spec-dirspecs/001-auth"
            in normalized_output
        )
        assert "explicit <frontend-source-root> required" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp" in result.output
        assert "uv run ai-sdlc verify constraints ->" not in result.output
        assert not observation_artifact_path(root / "specs" / "001-auth").is_file()
        assert (root / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()

    def test_program_remediate_execute_passes_when_only_visual_a11y_policy_artifact_gap_remains(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_p1_frontend_gate_artifacts(root)
        (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).unlink()
        for spec in ("001-auth", "002-course", "003-enroll"):
            spec_dir = root / "specs" / spec
            _write_frontend_contract_observations(spec_dir)
            _write_frontend_visual_a11y_evidence(spec_dir)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "remediate", "--execute", "--yes"],
            )

        assert result.exit_code == 0
        assert "Frontend remediation execute completed" in result.output
        assert "uv run ai-sdlc rules materialize-frontend-mvp -> executed" in result.output
        assert "uv run ai-sdlc verify constraints -> passed" in result.output
        assert (
            root
            / "governance"
            / "frontend"
            / "gates"
            / "visual-a11y-evidence-boundary.yaml"
        ).is_file()

    def test_program_remediate_execute_writes_canonical_writeback_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_minimal_frontend_contract_page_artifacts(root)
        _write_frontend_contract_source_annotation(root)
        for spec in ("002-course", "003-enroll"):
            _write_frontend_contract_observations(root / "specs" / spec)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "remediate", "--execute", "--yes"],
            )

        writeback_path = (
            root / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
        )
        assert result.exit_code == 1
        assert "Frontend remediation writeback saved" in result.output
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in result.output
        assert writeback_path.is_file()
        payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
        assert payload["passed"] is False
        assert any(
            "explicit <frontend-source-root> required" in blocker
            for blocker in payload["remaining_blockers"]
        )
        assert any(
            item["command"]
            == "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
            and item["status"] == "failed"
            for item in payload["command_results"]
        )

    def test_program_provider_handoff_surfaces_pending_frontend_inputs(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "Program Frontend Provider Handoff" in result.output
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in result.output
        assert "frontend_contract_observations" in result.output
        assert "not_started" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Handoff" in report
        assert ".ai-sdlc/memory/frontend-remediation/latest.yaml" in report
        assert "materialize frontend contract observations" in report

    def test_program_provider_handoff_surfaces_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-provider-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "frontend_visual_a11y_evidence_stable_empty" in result.output
        assert "review stable empty frontend visual / a11y evidence" in result.output
        assert "materialize frontend visual / a11y evidence input" not in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_provider_handoff_surfaces_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-provider-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "frontend_visual_a11y_issue_review" in result.output
        assert "review frontend visual / a11y issue findings" in result.output
        assert "frontend_visual_a11y_evidence_stable_empty" not in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_provider_runtime_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-runtime", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_provider_runtime_execute_surfaces_generated_patch_summaries(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-runtime.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-runtime",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Provider Runtime Execute" in result.output
        assert "patches_generated" in result.output
        assert "generated provider patch plan for 001-auth" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Runtime Result" in report
        assert "patches_generated" in report
        assert "generated provider patch plan for 001-auth" in report

    def test_program_provider_runtime_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-provider-runtime.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-runtime",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
        )
        assert result.exit_code == 0
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_provider_runtime_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-provider-runtime.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-runtime",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
        )
        assert result.exit_code == 0
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "frontend_visual_a11y_evidence_stable_empty" not in report

    def test_program_provider_runtime_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-runtime"])

        assert result.exit_code == 0
        assert "Program Frontend Provider Runtime Dry-Run" in result.output
        assert not (
            root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
        ).exists()

    def test_program_provider_runtime_execute_writes_runtime_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_remediation_writeback_artifact(
            root,
            passed=False,
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-runtime.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-runtime",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
        )
        assert result.exit_code == 0
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["invocation_result"] == "patches_generated"
        assert payload["provider_execution_state"] == "completed"
        assert payload["confirmed"] is True
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Runtime Artifact" in report
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in report

    def test_program_solution_confirm_simple_mode_preview_shows_single_recommendation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "solution-confirm"])

        assert result.exit_code == 0
        assert "Program Frontend Solution Confirm Simple" in result.output
        assert "Recommended Solution" in result.output
        assert "recommended_frontend_stack: vue2" in result.output
        assert "recommended_provider_id: enterprise-vue2" in result.output
        assert "fallback_required: false" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-solution-confirmation"
            / "latest.yaml"
        ).exists()

    def test_program_solution_confirm_advanced_mode_surfaces_wizard_and_preflight(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "solution-confirm",
                    "--mode",
                    "advanced",
                    "--frontend-stack",
                    "vue2",
                    "--provider-id",
                    "enterprise-vue2",
                    "--style-pack-id",
                    "enterprise-default",
                    "--enterprise-provider-ineligible",
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Solution Confirm Advanced" in result.output
        assert "Step 1/7" in result.output
        assert "Step 7/7" in result.output
        assert "Final Preflight" in result.output
        assert "requested_frontend_stack: vue2" in result.output
        assert "effective_frontend_stack: vue3" in result.output
        assert "preflight_status: warning" in result.output
        assert (
            "will_change_on_confirm: frontend_stack, provider_id, style_pack_id"
            in result.output
        )
        assert "fallback_required: true" in result.output

    def test_program_solution_confirm_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "solution-confirm", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_solution_confirm_execute_writes_snapshot_without_preview_only_fields(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        report_rel = ".ai-sdlc/memory/frontend-solution-confirmation.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "solution-confirm",
                    "--mode",
                    "advanced",
                    "--frontend-stack",
                    "vue2",
                    "--provider-id",
                    "enterprise-vue2",
                    "--style-pack-id",
                    "enterprise-default",
                    "--enterprise-provider-ineligible",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-solution-confirmation"
            / "latest.yaml"
        )
        provider_manifest_path = (
            root
            / "providers"
            / "frontend"
            / "public-primevue"
            / "provider.manifest.yaml"
        )
        style_support_path = (
            root
            / "providers"
            / "frontend"
            / "public-primevue"
            / "style-support.yaml"
        )
        assert result.exit_code == 0
        assert artifact_path.is_file()
        assert provider_manifest_path.is_file()
        assert style_support_path.is_file()
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        provider_manifest = yaml.safe_load(provider_manifest_path.read_text(encoding="utf-8"))
        style_support = yaml.safe_load(style_support_path.read_text(encoding="utf-8"))
        assert payload["confirmed_by_mode"] == "advanced"
        assert payload["decision_status"] == "fallback_required"
        assert payload["requested_frontend_stack"] == "vue2"
        assert payload["effective_frontend_stack"] == "vue3"
        assert payload["effective_provider_id"] == "public-primevue"
        assert payload["preflight_status"] == "warning"
        assert "will_change_on_confirm" not in payload
        assert provider_manifest["provider_id"] == "public-primevue"
        assert provider_manifest["install_strategy_ids"] == ["public-primevue-default"]
        assert any(
            item["style_pack_id"] == "modern-saas"
            and item["fidelity_status"] == "full"
            for item in style_support["items"]
        )
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Solution Confirmation Artifact" in report
        assert ".ai-sdlc/memory/frontend-solution-confirmation/latest.yaml" in report

    def test_program_solution_confirm_execute_does_not_persist_blocked_snapshot(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "solution-confirm",
                    "--enterprise-provider-ineligible",
                    "--no-fallback-candidate",
                    "--execute",
                    "--yes",
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-solution-confirmation"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert "Frontend solution confirmation blocked" in result.output
        assert not artifact_path.exists()

    def test_program_solution_confirm_execute_blocks_unknown_provider_artifact_materialization(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "solution-confirm",
                    "--provider-id",
                    "foo-provider",
                    "--style-pack-id",
                    "modern-saas",
                    "--execute",
                    "--yes",
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-solution-confirmation"
            / "latest.yaml"
        )
        provider_root = root / "providers" / "frontend" / "foo-provider"
        assert result.exit_code == 1
        assert "Unsupported frontend provider profile artifacts" in result.output
        assert "Traceback" not in result.output
        assert not artifact_path.exists()
        assert not provider_root.exists()

    def test_program_provider_patch_handoff_surfaces_runtime_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="patches_generated",
            provider_execution_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-patch-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "Program Frontend Provider Patch Handoff" in result.output
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in result.output
        assert "patches_generated" in result.output
        assert "frontend_contract_observations" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Patch Handoff" in report
        assert ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml" in report
        assert "patches_generated" in report

    def test_program_provider_patch_handoff_surfaces_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
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
                        "provider_runtime_state": "deferred",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-patch-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "frontend_visual_a11y_evidence_stable_empty" in result.output
        assert "review stable empty frontend visual / a11y evidence" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_provider_patch_handoff_surfaces_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="deferred",
            provider_execution_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
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
                        "provider_runtime_state": "deferred",
                    },
                }
            ],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-handoff.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "provider-patch-handoff", "--report", report_rel],
            )

        assert result.exit_code == 0
        assert "frontend_visual_a11y_issue_review" in result.output
        assert "review frontend visual / a11y issue findings" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_provider_patch_handoff_fails_when_runtime_artifact_missing(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-patch-handoff"])

        assert result.exit_code == 1
        assert "missing provider runtime artifact" in result.output

    def test_program_provider_patch_apply_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="patches_generated",
            provider_execution_state="completed",
            remaining_blockers=[],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-patch-apply", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_provider_patch_apply_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="patches_generated",
            provider_execution_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-apply.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-patch-apply",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Provider Patch Apply Execute" in result.output
        assert "applied" in result.output
        assert "applied 1 provider patch file(s) from readonly patch handoff" in result.output
        assert ".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Patch Apply Result" in report
        assert "applied" in report
        assert "applied 1 provider patch file(s) from readonly patch handoff" in report

    def test_program_provider_patch_apply_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-apply.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-patch-apply",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-provider-patch-apply"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_provider_patch_apply_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-apply.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-patch-apply",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-provider-patch-apply"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "frontend_visual_a11y_evidence_stable_empty" not in report

    def test_program_provider_patch_apply_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="patches_generated",
            provider_execution_state="completed",
            remaining_blockers=[],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "provider-patch-apply"])

        assert result.exit_code == 0
        assert "Program Frontend Provider Patch Apply Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-provider-patch-apply"
            / "latest.yaml"
        ).exists()

    def test_program_provider_patch_apply_execute_writes_apply_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_runtime_artifact(
            root,
            invocation_result="patches_generated",
            provider_execution_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-provider-patch-apply.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "provider-patch-apply",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-provider-patch-apply"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["apply_result"] == "applied"
        assert payload["patch_apply_state"] == "completed"
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            ".ai-sdlc/memory/frontend-provider-patch-apply/steps/001-auth.md"
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Provider Patch Apply Artifact" in report
        assert ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml" in report

    def test_program_cross_spec_writeback_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="applied",
            patch_apply_state="completed",
            remaining_blockers=[],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "cross-spec-writeback", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_cross_spec_writeback_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="applied",
            patch_apply_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-cross-spec-writeback.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "cross-spec-writeback",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Cross-Spec Writeback Execute" in result.output
        assert "completed" in result.output
        assert "wrote 1 cross-spec writeback file(s) from canonical patch apply artifact" in result.output
        assert "specs/001-auth/frontend-provider-writeback.md" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Cross-Spec Writeback Result" in report
        assert "completed" in report
        assert "wrote 1 cross-spec writeback file(s) from canonical patch apply artifact" in report

    def test_program_cross_spec_writeback_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-cross-spec-writeback.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "cross-spec-writeback",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_cross_spec_writeback_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-cross-spec-writeback.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "cross-spec-writeback",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "frontend_visual_a11y_evidence_stable_empty" not in report

    def test_program_cross_spec_writeback_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="applied",
            patch_apply_state="completed",
            remaining_blockers=[],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "cross-spec-writeback"])

        assert result.exit_code == 0
        assert "Program Frontend Cross-Spec Writeback Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        ).exists()

    def test_program_cross_spec_writeback_execute_writes_writeback_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_provider_patch_apply_artifact(
            root,
            apply_result="deferred",
            patch_apply_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-cross-spec-writeback-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "cross-spec-writeback",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-cross-spec-writeback"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["orchestration_result"] == "blocked"
        assert payload["writeback_state"] == "blocked"
        assert payload["confirmed"] is True
        assert payload["written_paths"] == []
        assert payload["remaining_blockers"] == [
            "spec 001-auth remediation still required",
            "cross-spec writeback requires applied patch artifact (apply_result=deferred)",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Cross-Spec Writeback Artifact" in report
        assert ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml" in report

    def test_program_guarded_registry_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "guarded-registry", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_guarded_registry_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "guarded-registry"])

        assert result.exit_code == 0
        assert "Program Frontend Guarded Registry Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml" in result.output

    def test_program_guarded_registry_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="completed",
            writeback_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-guarded-registry.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "guarded-registry",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Guarded Registry Execute" in result.output
        assert "completed" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Guarded Registry Result" in report
        assert "completed" in report
        assert "materialized 1 guarded registry step file(s) from canonical cross-spec writeback artifact" in report

    def test_program_guarded_registry_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-guarded-registry.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "guarded-registry",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_guarded_registry_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-guarded-registry.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "guarded-registry",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "frontend_visual_a11y_evidence_stable_empty" not in report

    def test_program_guarded_registry_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "guarded-registry"])

        assert result.exit_code == 0
        assert "Program Frontend Guarded Registry Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        ).exists()

    def test_program_guarded_registry_execute_writes_registry_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_cross_spec_writeback_artifact(
            root,
            orchestration_result="deferred",
            writeback_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-guarded-registry-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "guarded-registry",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-guarded-registry"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["registry_result"] == "blocked"
        assert payload["registry_state"] == "blocked"
        assert payload["confirmed"] is True
        assert payload["remaining_blockers"] == [
            "spec 001-auth remediation still required",
            "guarded registry requires completed cross-spec writeback artifact (writeback_state=deferred)",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Guarded Registry Artifact" in report
        assert ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml" in report

    def test_program_broader_governance_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "broader-governance", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_broader_governance_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "broader-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Broader Governance Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml" in result.output

    def test_program_broader_governance_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="completed",
            registry_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-broader-governance.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "broader-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Broader Governance Execute" in result.output
        assert "completed" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Broader Governance Result" in report
        assert "completed" in report
        assert "materialized 1 broader governance step file(s) from canonical guarded registry artifact" in report

    def test_program_broader_governance_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-broader-governance.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "broader-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_broader_governance_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-broader-governance.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "broader-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "frontend_visual_a11y_evidence_stable_empty" not in report

    def test_program_broader_governance_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "broader-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Broader Governance Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        ).exists()

    def test_program_broader_governance_execute_writes_governance_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_guarded_registry_artifact(
            root,
            registry_result="deferred",
            registry_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-broader-governance-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "broader-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-broader-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-broader-governance/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["governance_result"] == "blocked"
        assert payload["governance_state"] == "blocked"
        assert payload["confirmed"] is True
        assert payload["remaining_blockers"] == [
            "spec 001-auth remediation still required",
            "broader governance requires completed guarded registry artifact (registry_state=deferred)",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Broader Governance Artifact" in report
        assert ".ai-sdlc/memory/frontend-broader-governance/latest.yaml" in report

    def test_program_final_governance_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-governance", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_governance_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Final Governance Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-broader-governance/latest.yaml" in result.output

    def test_program_final_governance_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="completed",
            governance_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-governance.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Governance Execute" in result.output
        assert "completed" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Governance Result" in report
        assert "completed" in report
        assert "materialized 1 final governance step file(s) from canonical broader governance artifact" in report

    def test_program_final_governance_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-governance"])

        assert result.exit_code == 0
        assert "Program Frontend Final Governance Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-governance"
            / "latest.yaml"
        ).exists()

    def test_program_final_governance_execute_writes_governance_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
            governance_result="deferred",
            governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-governance-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-governance/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["final_governance_result"] == "blocked"
        assert payload["final_governance_state"] == "blocked"
        assert payload["confirmed"] is True
        assert payload["remaining_blockers"] == [
            "spec 001-auth remediation still required",
            "final governance requires completed broader governance artifact (governance_state=deferred)",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Governance Artifact" in report
        assert ".ai-sdlc/memory/frontend-final-governance/latest.yaml" in report

    def test_program_final_governance_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-governance-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_final_governance_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_broader_governance_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-governance-visual-a11y-issue.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-governance",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-governance"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_writeback_persistence_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "writeback-persistence", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_writeback_persistence_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "writeback-persistence"])

        assert result.exit_code == 0
        assert "Program Frontend Writeback Persistence Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-governance/latest.yaml" in result.output

    def test_program_writeback_persistence_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="completed",
            final_governance_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-writeback-persistence.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Writeback Persistence Execute" in result.output
        assert "completed" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Writeback Persistence Result" in report
        assert "completed" in report
        assert "materialized 1 writeback persistence step file(s) from canonical final governance artifact" in report

    def test_program_writeback_persistence_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "writeback-persistence"])

        assert result.exit_code == 0
        assert "Program Frontend Writeback Persistence Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-writeback-persistence"
            / "latest.yaml"
        ).exists()

    def test_program_writeback_persistence_execute_writes_persistence_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
            final_governance_result="deferred",
            final_governance_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        report_rel = ".ai-sdlc/memory/frontend-writeback-persistence-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-writeback-persistence"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["persistence_result"] == "blocked"
        assert payload["persistence_state"] == "blocked"
        assert payload["confirmed"] is True
        assert payload["remaining_blockers"] == [
            "spec 001-auth remediation still required",
            "writeback persistence requires completed final governance artifact (final_governance_state=deferred)",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Writeback Persistence Artifact" in report
        assert ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml" in report

    def test_program_writeback_persistence_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-writeback-persistence-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-writeback-persistence"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_writeback_persistence_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_governance_artifact(
            root,
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
        report_rel = (
            ".ai-sdlc/memory/frontend-writeback-persistence-visual-a11y-issue.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "writeback-persistence",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-writeback-persistence"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_persisted_write_proof_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "persisted-write-proof", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_persisted_write_proof_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "persisted-write-proof"])

        assert result.exit_code == 0
        assert "Program Frontend Persisted Write Proof Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml" in result.output

    def test_program_persisted_write_proof_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="completed",
            persistence_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-persisted-write-proof.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "persisted-write-proof",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Persisted Write Proof Execute" in result.output
        assert "completed" in result.output
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Persisted Write Proof Result" in report
        assert "completed" in report
        assert (
            "materialized 1 persisted write proof step file(s) from canonical writeback persistence artifact"
            in report
        )

    def test_program_persisted_write_proof_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="deferred",
            persistence_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "persisted-write-proof"])

        assert result.exit_code == 0
        assert "Program Frontend Persisted Write Proof Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-persisted-write-proof"
            / "latest.yaml"
        ).exists()

    def test_program_persisted_write_proof_execute_writes_proof_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
            persistence_result="completed",
            persistence_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-persisted-write-proof-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "persisted-write-proof",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-persisted-write-proof"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["proof_result"] == "completed"
        assert payload["proof_state"] == "completed"
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            ".ai-sdlc/memory/frontend-persisted-write-proof/steps/001-auth.md"
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Persisted Write Proof Artifact" in report
        assert ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml" in report

    def test_program_persisted_write_proof_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-persisted-write-proof-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "persisted-write-proof",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-persisted-write-proof"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_persisted_write_proof_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_writeback_persistence_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-persisted-write-proof-visual-a11y-issue.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "persisted-write-proof",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-persisted-write-proof"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_final_proof_publication_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-publication"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_final_proof_publication_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication-visual-a11y-issue.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-publication"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_final_proof_publication_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app, ["program", "final-proof-publication", "--execute"]
            )

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_publication_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-publication"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Publication Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml" in result.output

    def test_program_final_proof_publication_execute_surfaces_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="completed",
            proof_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Publication Execute" in result.output
        assert "completed" in result.output
        assert (
            "materialized 1 final proof publication step file(s) from canonical persisted write proof artifact"
            in result.output
        )
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Publication Result" in report
        assert "completed" in report
        assert (
            "materialized 1 final proof publication step file(s) from canonical persisted write proof artifact"
            in report
        )

    def test_program_final_proof_publication_dry_run_does_not_write_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="deferred",
            proof_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-publication"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Publication Dry-Run" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-publication"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_publication_execute_writes_publication_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_persisted_write_proof_artifact(
            root,
            proof_result="completed",
            proof_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-publication-artifact.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-publication",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-publication"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["publication_result"] == "completed"
        assert payload["publication_state"] == "completed"
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            ".ai-sdlc/memory/frontend-final-proof-publication/steps/001-auth.md"
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Publication Artifact" in report
        assert ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml" in report

    def test_program_final_proof_closure_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-closure-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-closure",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-closure"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_final_proof_closure_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-closure-visual-a11y-issue.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-closure",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-closure"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_final_proof_closure_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="deferred",
            publication_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-closure", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_closure_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="deferred",
            publication_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-closure"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Closure Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-closure"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_closure_execute_writes_closure_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_publication_artifact(
            root,
            publication_result="completed",
            publication_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-closure.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-closure",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-closure"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert "Program Frontend Final Proof Closure Execute" in result.output
        assert "completed" in result.output
        assert (
            "materialized 1 final proof closure step file(s) from canonical final proof publication artifact"
            in result.output
        )
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["closure_result"] == "completed"
        assert payload["closure_state"] == "completed"
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            ".ai-sdlc/memory/frontend-final-proof-closure/steps/001-auth.md"
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Closure Result" in report
        assert "Frontend Final Proof Closure Artifact" in report
        assert "completed" in report
        assert (
            "materialized 1 final proof closure step file(s) from canonical final proof publication artifact"
            in report
        )
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in report

    def test_program_final_proof_archive_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-stable-empty.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report

    def test_program_final_proof_archive_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-visual-a11y-issue.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report

    def test_program_final_proof_archive_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="deferred",
            closure_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-archive", "--execute"])

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_archive_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="deferred",
            closure_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "final-proof-archive"])

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_execute_writes_archive_artifact(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_closure_artifact(
            root,
            closure_result="completed",
            closure_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Execute" in result.output
        assert "completed" in result.output
        assert (
            "materialized 1 final proof archive step file(s) from canonical final proof closure artifact"
            in result.output
        )
        assert artifact_path.is_file()
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in result.output
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["archive_result"] == "completed"
        assert payload["archive_state"] == "completed"
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            ".ai-sdlc/memory/frontend-final-proof-archive/steps/001-auth.md"
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Archive Result" in report
        assert "Frontend Final Proof Archive Artifact" in report
        assert "completed" in report
        assert (
            "materialized 1 final proof archive step file(s) from canonical final proof closure artifact"
            in report
        )
        assert ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml" in report
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in report

    def test_program_final_proof_archive_thread_archive_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-thread-archive", "--execute"],
            )

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_archive_thread_archive_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-thread-archive"],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Thread Archive Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in result.output
        assert "thread archive state: not_started" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-thread-archive"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_thread_archive_execute_reports_completed_result(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="completed",
            archive_state="completed",
            remaining_blockers=[],
        )
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-thread-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Thread Archive Execute" in result.output
        assert "Frontend Final Proof Archive Thread Archive Result" in result.output
        assert "completed" in result.output
        assert (
            "materialized 1 final proof archive thread archive step file(s) from canonical final proof archive artifact"
            in result.output
        )
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Archive Thread Archive Result" in report
        assert "Frontend Final Proof Archive Artifact" in report
        assert "completed" in report
        assert (
            "materialized 1 final proof archive thread archive step file(s) from canonical final proof archive artifact"
            in report
        )
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in report
        assert (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-thread-archive"
            / "steps"
            / "001-auth.md"
        ).is_file()
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-thread-archive"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_thread_archive_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
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
        report_rel = (
            ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive-stable-empty.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-thread-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report
        assert "re-run ai-sdlc verify constraints" in report

    def test_program_final_proof_archive_thread_archive_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
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
        report_rel = (
            ".ai-sdlc/memory/frontend-final-proof-archive-thread-archive-visual-a11y-issue.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-thread-archive",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        assert result.exit_code == 1
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "re-run ai-sdlc verify constraints" in report

    def test_program_final_proof_archive_project_cleanup_execute_requires_explicit_confirmation(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-project-cleanup", "--execute"],
            )

        assert result.exit_code == 2
        assert "--yes" in result.output

    def test_program_final_proof_archive_project_cleanup_dry_run_surfaces_preview(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-project-cleanup"],
            )

        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Project Cleanup Dry-Run" in result.output
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in result.output
        assert "project cleanup state: not_started" in result.output
        assert "thread archive state: blocked" in result.output
        assert "cleanup targets state: missing" in result.output
        assert "cleanup targets count: 0" in result.output
        assert "cleanup target eligibility state: missing" in result.output
        assert "cleanup target eligibility count: 0" in result.output
        assert "cleanup preview plan state: missing" in result.output
        assert "cleanup preview plan count: 0" in result.output
        assert "cleanup mutation proposal state: missing" in result.output
        assert "cleanup mutation proposal count: 0" in result.output
        assert "cleanup mutation proposal approval state: missing" in result.output
        assert "cleanup mutation proposal approval count: 0" in result.output
        assert "cleanup mutation execution gating state: missing" in result.output
        assert "cleanup mutation execution gating count: 0" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        ).exists()

    def test_program_final_proof_archive_project_cleanup_dry_run_does_not_materialize_thread_archive_steps(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="completed",
            archive_state="completed",
            remaining_blockers=[],
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                ["program", "final-proof-archive-project-cleanup"],
            )

        assert result.exit_code == 0
        assert "thread archive state: completed" in result.output
        assert not (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-thread-archive"
            / "steps"
            / "001-auth.md"
        ).exists()

    def test_program_final_proof_archive_project_cleanup_execute_runs_canonical_gated_cleanup_mutations(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        archive_report = root / "specs" / "001-auth" / "threads" / "archive-001.md"
        archive_report.parent.mkdir(parents=True, exist_ok=True)
        archive_report.write_text("# archived thread\n", encoding="utf-8")
        spec_dir = root / "specs" / "002-course"
        (spec_dir / "notes").mkdir(parents=True, exist_ok=True)
        (spec_dir / "notes" / "todo.md").write_text("cleanup me\n", encoding="utf-8")
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
            root,
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
                    "reason": "approval matches the proposed archive-only cleanup action",
                },
                {
                    "target_id": "cleanup-spec-dir",
                    "approved_action": "remove_spec_dir",
                    "reason": "approval matches the proposed spec cleanup action",
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
        report_rel = ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup.md"

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-project-cleanup",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        )
        assert result.exit_code == 0
        assert "Program Frontend Final Proof Archive Project Cleanup Execute" in result.output
        assert "Frontend Final Proof Archive Project Cleanup Result" in result.output
        assert "project cleanup result: completed" in result.output
        assert "project cleanup state: completed" in result.output
        assert "cleanup targets state: listed" in result.output
        assert "cleanup targets count: 2" in result.output
        assert "cleanup target eligibility state: listed" in result.output
        assert "cleanup target eligibility count: 2" in result.output
        assert "cleanup preview plan state: listed" in result.output
        assert "cleanup preview plan count: 2" in result.output
        assert "cleanup mutation proposal state: listed" in result.output
        assert "cleanup mutation proposal count: 2" in result.output
        assert "cleanup mutation proposal approval state: listed" in result.output
        assert "cleanup mutation proposal approval count: 2" in result.output
        assert "cleanup mutation execution gating state: listed" in result.output
        assert "cleanup mutation execution gating count: 2" in result.output
        assert (
            "executed 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
            in result.output
        )
        assert "wrote: specs/001-auth/threads/archive-001.md" in result.output
        assert "wrote: specs/002-course" in result.output
        assert artifact_path.is_file()
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["project_cleanup_result"] == "completed"
        assert payload["project_cleanup_state"] == "completed"
        assert payload["cleanup_targets_state"] == "listed"
        assert len(payload["cleanup_targets"]) == 2
        assert payload["cleanup_target_eligibility_state"] == "listed"
        assert len(payload["cleanup_target_eligibility"]) == 2
        assert payload["cleanup_preview_plan_state"] == "listed"
        assert len(payload["cleanup_preview_plan"]) == 2
        assert payload["cleanup_mutation_proposal_state"] == "listed"
        assert len(payload["cleanup_mutation_proposal"]) == 2
        assert payload["cleanup_mutation_proposal_approval_state"] == "listed"
        assert len(payload["cleanup_mutation_proposal_approval"]) == 2
        assert payload["cleanup_mutation_execution_gating_state"] == "listed"
        assert len(payload["cleanup_mutation_execution_gating"]) == 2
        assert payload["confirmed"] is True
        assert payload["written_paths"] == [
            "specs/001-auth/threads/archive-001.md",
            "specs/002-course",
        ]
        assert payload["remaining_blockers"] == []
        assert payload["warnings"] == []
        assert payload["source_linkage"]["project_cleanup_state"] == "completed"
        assert payload["source_linkage"]["project_cleanup_result"] == "completed"
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "Frontend Final Proof Archive Project Cleanup Result" in report
        assert "Frontend Final Proof Archive Project Cleanup Artifact" in report
        assert "Project cleanup result: `completed`" in report
        assert "Project cleanup state: `completed`" in report
        assert "Cleanup targets state: `listed`" in report
        assert "Cleanup targets count: `2`" in report
        assert "Cleanup target eligibility state: `listed`" in report
        assert "Cleanup target eligibility count: `2`" in report
        assert "Cleanup preview plan state: `listed`" in report
        assert "Cleanup preview plan count: `2`" in report
        assert "Cleanup mutation proposal state: `listed`" in report
        assert "Cleanup mutation proposal count: `2`" in report
        assert "Cleanup mutation proposal approval state: `listed`" in report
        assert "Cleanup mutation proposal approval count: `2`" in report
        assert "Cleanup mutation execution gating state: `listed`" in report
        assert "Cleanup mutation execution gating count: `2`" in report
        assert (
            "executed 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
            in report
        )
        assert "- Written paths:" in report
        assert "  - specs/001-auth/threads/archive-001.md" in report
        assert "  - specs/002-course" in report
        assert ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml" in report
        assert (
            ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml"
            in report
        )
        assert not archive_report.exists()
        assert not spec_dir.exists()

    def test_program_final_proof_archive_project_cleanup_execute_blocks_invalid_gating_alignment(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        archive_report = root / "specs" / "001-auth" / "threads" / "archive-001.md"
        archive_report.parent.mkdir(parents=True, exist_ok=True)
        archive_report.write_text("# archived thread\n", encoding="utf-8")
        _write_frontend_final_proof_archive_artifact(
            root,
            archive_result="deferred",
            archive_state="deferred",
            remaining_blockers=["spec 001-auth remediation still required"],
        )
        _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
            root,
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
                    "reason": "approval matches the canonical cleanup action",
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

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-project-cleanup",
                    "--execute",
                    "--yes",
                ],
            )

        assert result.exit_code == 1
        assert "project cleanup result: blocked" in result.output
        assert "project cleanup state: blocked" in result.output
        assert "is not eligible" in result.output
        assert "does not appear in cleanup_preview_plan" in result.output
        assert archive_report.exists()

    def test_program_final_proof_archive_project_cleanup_execute_preserves_stable_empty_visual_a11y_pending_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
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
        report_rel = (
            ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup-stable-empty.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-project-cleanup",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_evidence_stable_empty"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review stable empty frontend visual / a11y evidence",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_evidence_stable_empty" in report
        assert "review stable empty frontend visual / a11y evidence" in report
        assert "re-run ai-sdlc verify constraints" in report

    def test_program_final_proof_archive_project_cleanup_execute_preserves_visual_a11y_issue_review_input(
        self, initialized_project_dir: Path
    ) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        _write_frontend_final_proof_archive_artifact(
            root,
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
        report_rel = (
            ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup-visual-a11y-issue.md"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(
                app,
                [
                    "program",
                    "final-proof-archive-project-cleanup",
                    "--execute",
                    "--yes",
                    "--report",
                    report_rel,
                ],
            )

        artifact_path = (
            root
            / ".ai-sdlc"
            / "memory"
            / "frontend-final-proof-archive-project-cleanup"
            / "latest.yaml"
        )
        assert result.exit_code == 1
        payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
        assert payload["steps"][0]["pending_inputs"] == [
            "frontend_visual_a11y_issue_review"
        ]
        assert payload["steps"][0]["suggested_next_actions"] == [
            "review frontend visual / a11y issue findings",
            "re-run ai-sdlc verify constraints",
        ]
        report = (root / report_rel).read_text(encoding="utf-8")
        assert "frontend_visual_a11y_issue_review" in report
        assert "review frontend visual / a11y issue findings" in report
        assert "re-run ai-sdlc verify constraints" in report


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
        }
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
            "archive_state": archive_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof archive thread archive review context",
                "prepare bounded thread archive execution",
            ],
            "source_linkage": {
                "archive_state": archive_state,
                "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
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
                "existing_written_paths": [],
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
            "seeded cleanup target truth for CLI tests"
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
