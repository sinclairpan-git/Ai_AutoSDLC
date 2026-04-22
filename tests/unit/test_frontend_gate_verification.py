"""Unit tests for frontend gate verification helpers."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import ai_sdlc.core.frontend_gate_verification as frontend_gate_verification_module
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT,
)
from ai_sdlc.core.frontend_contract_verification import (
    build_frontend_contract_verification_report,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_CHECK_OBJECTS,
    FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
    FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
    FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
    FRONTEND_GATE_SOURCE_NAME,
    FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
    FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT,
    FrontendGateVerificationReport,
    build_frontend_browser_gate_execute_decision,
    build_frontend_gate_execute_decision,
    build_frontend_gate_verification_context,
    build_frontend_gate_verification_report,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceArtifact,
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserProbeExecutionReceipt,
    BrowserQualityBundleMaterializationInput,
    BrowserQualityGateExecutionContext,
)
from ai_sdlc.models.frontend_gate_policy import (
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


def _write_minimal_frontend_contract_page_artifacts(
    root: Path,
    *,
    page_id: str = "orders.form",
    recipe_id: str = "FormPage",
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


def _matching_observation(
    *, page_id: str = "orders.form", recipe_id: str = "FormPage"
) -> PageImplementationObservation:
    return PageImplementationObservation(
        page_id=page_id,
        recipe_id=recipe_id,
        i18n_keys=[],
        validation_fields=[],
        new_legacy_usages=[],
    )


def _visual_a11y_evidence_artifact(
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
) -> FrontendVisualA11yEvidenceArtifact:
    return build_frontend_visual_a11y_evidence_artifact(
        evaluations=evaluations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T13:00:00Z",
    )


def test_frontend_gate_verification_report_flags_missing_gate_policy_artifacts(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_gate_policy_artifacts" in report.coverage_gaps
    assert any("gate policy artifacts unavailable" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_report_flags_missing_generation_artifacts(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_generation_governance_artifacts" in report.coverage_gaps
    assert any(
        "generation governance artifacts unavailable" in blocker
        for blocker in report.blockers
    )


def test_frontend_gate_verification_report_flags_unclear_contract_prerequisite(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [],
        observation_artifact_status=(
            FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT
        ),
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_contract_observations" in report.coverage_gaps
    assert any("contract verification not clear" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_report_distinguishes_valid_empty_contract_artifact(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [],
        observation_artifact_status=FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert report.coverage_gaps == ()
    assert any("declared empty" in blocker for blocker in report.blockers)
    assert report.upstream_contract_verification["observation_artifact_status"] == "attached"
    assert report.upstream_contract_verification["observation_count"] == 0


def test_frontend_gate_verification_report_uses_projection_to_keep_valid_empty_out_of_gaps(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    upstream_report = build_frontend_contract_verification_report(
        tmp_path / "contracts" / "frontend",
        [],
        observation_artifact_status=FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
    )
    stale_gap_report = replace(
        upstream_report,
        coverage_gaps=("frontend_contract_observations",),
    )
    monkeypatch.setattr(
        frontend_gate_verification_module,
        "build_frontend_contract_verification_report",
        lambda *args, **kwargs: stale_gap_report,
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert report.coverage_gaps == ()
    assert any("declared empty" in blocker for blocker in report.blockers)
    assert (
        report.upstream_contract_verification["diagnostic"]["diagnostic_status"]
        == "valid_empty"
    )


def test_frontend_gate_verification_context_passes_when_prerequisites_are_ready(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )
    context = build_frontend_gate_verification_context(
        tmp_path,
        [_matching_observation()],
    )

    assert report.blockers == ()
    assert report.coverage_gaps == ()
    assert report.check_objects == FRONTEND_GATE_CHECK_OBJECTS
    assert context["verification_sources"] == (FRONTEND_GATE_SOURCE_NAME,)
    assert context["verification_check_objects"] == FRONTEND_GATE_CHECK_OBJECTS


def test_frontend_gate_execute_decision_runtime_object_canonicalizes_lists() -> None:
    decision = frontend_gate_verification_module.FrontendGateExecuteDecision(
        execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
        decision_reason="evidence_missing",
        blockers=("browser gate blocker", "browser gate blocker"),
        recheck_required=True,
        recheck_reason_codes=(
            "frontend_visual_a11y_evidence_input",
            "frontend_visual_a11y_evidence_input",
        ),
        remediation_hints=(
            "materialize shared Playwright runtime evidence",
            "materialize shared Playwright runtime evidence",
        ),
        remediation_reason_codes=(
            "frontend_visual_a11y_policy_artifacts",
            "frontend_visual_a11y_policy_artifacts",
        ),
    )

    assert decision.blockers == ("browser gate blocker",)
    assert decision.recheck_reason_codes == ("frontend_visual_a11y_evidence_input",)
    assert decision.remediation_hints == (
        "materialize shared Playwright runtime evidence",
    )
    assert decision.remediation_reason_codes == (
        "frontend_visual_a11y_policy_artifacts",
    )


def test_frontend_gate_verification_report_to_json_dict_deduplicates_lists() -> None:
    payload = FrontendGateVerificationReport(
        gate_policy_root="governance/frontend/gates",
        generation_root="governance/frontend/generation",
        source_name="frontend gate verification",
        check_objects=("frontend_gate_policy_artifacts", "frontend_gate_policy_artifacts"),
        blockers=("gate blocker", "gate blocker"),
        coverage_gaps=("frontend_contract_observations", "frontend_contract_observations"),
        advisory_checks=("advisory", "advisory"),
        gate_result=GateResult(
            stage="verify",
            verdict=GateVerdict.RETRY,
            checks=[
                GateCheck(name="gate", passed=False, message="missing"),
                GateCheck(name="gate", passed=False, message="missing"),
            ],
        ),
        upstream_contract_verification={"gate_verdict": "RETRY"},
    ).to_json_dict()

    assert payload["check_objects"] == ["frontend_gate_policy_artifacts"]
    assert payload["blockers"] == ["gate blocker"]
    assert payload["coverage_gaps"] == ["frontend_contract_observations"]
    assert payload["advisory_checks"] == ["advisory"]
    assert payload["gate_checks"] == [
        {"name": "gate", "passed": False, "message": "missing"}
    ]


def test_frontend_gate_verification_report_runtime_object_canonicalizes_lists() -> None:
    report = FrontendGateVerificationReport(
        gate_policy_root="governance/frontend/gates",
        generation_root="governance/frontend/generation",
        source_name="frontend gate verification",
        check_objects=("frontend_gate_policy_artifacts", "frontend_gate_policy_artifacts"),
        blockers=("gate blocker", "gate blocker"),
        coverage_gaps=("frontend_contract_observations", "frontend_contract_observations"),
        advisory_checks=("advisory", "advisory"),
        gate_result=GateResult(
            stage="verify",
            verdict=GateVerdict.RETRY,
            checks=(GateCheck(name="gate", passed=False, message="missing"),),
        ),
        upstream_contract_verification={"gate_verdict": "RETRY"},
    )

    assert report.check_objects == ("frontend_gate_policy_artifacts",)
    assert report.blockers == ("gate blocker",)
    assert report.coverage_gaps == ("frontend_contract_observations",)
    assert report.advisory_checks == ("advisory",)


def test_frontend_gate_execute_decision_maps_missing_visual_a11y_evidence_to_recheck_required(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )
    decision = build_frontend_gate_execute_decision(
        attachment_status="attached",
        gate_report=report,
    )

    assert decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED
    assert decision.decision_reason == "evidence_missing"
    assert decision.recheck_required is True
    assert "frontend_visual_a11y_evidence_input" in decision.recheck_reason_codes


def test_frontend_gate_execute_decision_blocks_missing_visual_a11y_policy_artifacts(
    tmp_path: Path,
) -> None:
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

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )
    decision = build_frontend_gate_execute_decision(
        attachment_status="attached",
        gate_report=report,
    )

    assert decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED
    assert decision.decision_reason == "result_inconsistency"
    assert decision.recheck_required is False
    assert "frontend_visual_a11y_policy_artifacts" in decision.remediation_reason_codes


def test_frontend_gate_execute_decision_maps_visual_a11y_issue_to_needs_remediation(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
        visual_a11y_evidence_artifact=_visual_a11y_evidence_artifact(
            [
                FrontendVisualA11yEvidenceEvaluation(
                    evaluation_id="visual-issue",
                    target_id="orders.form",
                    surface_id="success-feedback",
                    outcome="issue",
                    report_type="violation-report",
                    severity="medium",
                    location_anchor="feedback.banner",
                    quality_hint="review success feedback visibility and semantics",
                    changed_scope_explanation="issue fixture",
                )
            ]
        ),
    )
    decision = build_frontend_gate_execute_decision(
        attachment_status="attached",
        gate_report=report,
    )

    assert (
        decision.execute_gate_state
        == FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION
    )
    assert decision.decision_reason == "actual_quality_blocker"
    assert decision.recheck_required is False
    assert "frontend_visual_a11y_issue_review" in decision.remediation_reason_codes


def test_frontend_gate_execute_decision_fails_closed_when_attachment_missing() -> None:
    decision = build_frontend_gate_execute_decision(
        attachment_status="missing_artifact",
        attachment_blockers=(
            "frontend contract runtime attachment unavailable: missing canonical observation artifact",
        ),
        attachment_coverage_gaps=("frontend_contract_observations",),
        gate_report=None,
    )

    assert decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED
    assert decision.decision_reason == "scope_or_linkage_invalid"
    assert decision.recheck_required is False
    assert "frontend_contract_observations" in decision.remediation_reason_codes


def test_frontend_gate_execute_decision_allows_framework_capability_when_attachment_missing() -> None:
    decision = build_frontend_gate_execute_decision(
        attachment_status="missing_artifact",
        attachment_blockers=(
            "frontend contract runtime attachment unavailable: missing canonical observation artifact",
        ),
        attachment_coverage_gaps=("frontend_contract_observations",),
        gate_report=None,
        frontend_evidence_class="framework_capability",
    )

    assert decision.execute_gate_state == "ready"
    assert decision.decision_reason == "advisory_only"
    assert decision.recheck_required is False
    assert decision.blockers == ()
    assert decision.remediation_reason_codes == ()
    assert (
        decision.source_linkage_refs["frontend_attachment_requirement"]
        == "waived_for_framework_capability"
    )


def test_frontend_browser_gate_execute_decision_maps_incomplete_bundle_to_recheck_required() -> None:
    context = BrowserQualityGateExecutionContext(
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="snapshot-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        readiness_subject_id="001-auth",
        effective_provider="public-primevue",
        effective_style_pack="modern-saas",
        style_fidelity_status="full",
        required_probe_set=["playwright_smoke"],
        browser_entry_ref="managed/frontend",
    )
    bundle = BrowserQualityBundleMaterializationInput(
        bundle_id="bundle-001",
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="snapshot-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        source_artifact_ref=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        readiness_subject_id="001-auth",
        check_receipts=[
            BrowserProbeExecutionReceipt(
                check_name="playwright_smoke",
                started_at="2026-04-14T04:05:00Z",
                finished_at="2026-04-14T04:05:00Z",
                runtime_status="incomplete",
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=["materialize shared Playwright runtime evidence"],
                blocking_reason_codes=["playwright_probe_evidence_missing"],
            )
        ],
        smoke_verdict="evidence_missing",
        visual_verdict="pass",
        a11y_verdict="pass",
        interaction_anti_pattern_verdict="pass",
        overall_gate_status="incomplete",
        blocking_reason_codes=["playwright_probe_evidence_missing"],
        generated_at="2026-04-14T04:05:00Z",
    )

    decision = build_frontend_browser_gate_execute_decision(
        execution_context=context,
        bundle=bundle,
        artifact_path=".ai-sdlc/memory/frontend-browser-gate/latest.yaml",
    )

    assert decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED
    assert decision.decision_reason == "evidence_missing"
    assert decision.recheck_required is True
    assert "playwright_probe_evidence_missing" in decision.recheck_reason_codes
    assert (
        decision.source_linkage_refs["frontend_browser_gate_gate_run_id"] == "gate-run-001"
    )


def test_frontend_browser_gate_execute_decision_fails_closed_on_scope_mismatch() -> None:
    context = BrowserQualityGateExecutionContext(
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="snapshot-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        readiness_subject_id="001-auth",
        effective_provider="public-primevue",
        effective_style_pack="modern-saas",
        style_fidelity_status="full",
        required_probe_set=["playwright_smoke"],
        browser_entry_ref="managed/frontend",
    )
    bundle = BrowserQualityBundleMaterializationInput(
        bundle_id="bundle-001",
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="snapshot-001",
        spec_dir="specs/002-course",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        source_artifact_ref=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        readiness_subject_id="001-auth",
        check_receipts=[],
        smoke_verdict="pass",
        visual_verdict="pass",
        a11y_verdict="pass",
        interaction_anti_pattern_verdict="pass",
        overall_gate_status="passed",
        generated_at="2026-04-14T04:05:00Z",
    )

    decision = build_frontend_browser_gate_execute_decision(
        execution_context=context,
        bundle=bundle,
        artifact_path=".ai-sdlc/memory/frontend-browser-gate/latest.yaml",
    )

    assert decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED
    assert decision.decision_reason == "scope_or_linkage_invalid"


def test_frontend_browser_gate_execute_decision_blocks_when_required_probe_receipts_missing() -> None:
    context = BrowserQualityGateExecutionContext(
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="snapshot-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        readiness_subject_id="001-auth",
        effective_provider="public-primevue",
        effective_style_pack="modern-saas",
        style_fidelity_status="full",
        required_probe_set=["playwright_smoke", "visual_expectation"],
        browser_entry_ref="managed/frontend",
    )
    bundle = BrowserQualityBundleMaterializationInput(
        bundle_id="bundle-001",
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="snapshot-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        source_artifact_ref=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        readiness_subject_id="001-auth",
        check_receipts=[],
        smoke_verdict="pass",
        visual_verdict="pass",
        a11y_verdict="pass",
        interaction_anti_pattern_verdict="pass",
        overall_gate_status="passed",
        generated_at="2026-04-14T04:05:00Z",
    )

    decision = build_frontend_browser_gate_execute_decision(
        execution_context=context,
        bundle=bundle,
        artifact_path=".ai-sdlc/memory/frontend-browser-gate/latest.yaml",
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
    )

    assert decision.execute_gate_state == FRONTEND_GATE_EXECUTE_STATE_BLOCKED
    assert decision.decision_reason == "result_inconsistency"


def test_frontend_gate_verification_report_flags_missing_visual_a11y_extension_artifacts(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-feedback-boundary.yaml"
    ).unlink()

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_visual_a11y_policy_artifacts" in report.coverage_gaps
    assert report.check_objects == (
        *FRONTEND_GATE_CHECK_OBJECTS,
        FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
        FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT,
    )
    assert any("visual / a11y policy artifacts unavailable" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_report_flags_missing_visual_a11y_evidence_input(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert "frontend_visual_a11y_evidence_input" in report.coverage_gaps
    assert report.check_objects == (
        *FRONTEND_GATE_CHECK_OBJECTS,
        FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
        FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT,
    )
    assert any("missing explicit evidence input" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_report_flags_stable_empty_visual_a11y_evidence(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    evidence = _visual_a11y_evidence_artifact([])

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
        visual_a11y_evidence_artifact=evidence,
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert report.coverage_gaps == ("frontend_visual_a11y_evidence_stable_empty",)
    assert any("stable empty evidence" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_report_flags_visual_a11y_issue_review_gap(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    evidence = _visual_a11y_evidence_artifact(
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="success-feedback",
                outcome="issue",
                report_type="violation-report",
                severity="medium",
                location_anchor="feedback.banner",
            )
        ]
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
        visual_a11y_evidence_artifact=evidence,
    )

    assert report.gate_result.verdict.value == "RETRY"
    assert report.coverage_gaps == ("frontend_visual_a11y_issue_review",)
    assert any("visual / a11y issues detected" in blocker for blocker in report.blockers)


def test_frontend_gate_verification_context_passes_with_visual_a11y_extension_ready(
    tmp_path: Path,
) -> None:
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    evidence = _visual_a11y_evidence_artifact(
        [
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-pass",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="pass",
            )
        ]
    )

    report = build_frontend_gate_verification_report(
        tmp_path,
        [_matching_observation()],
        visual_a11y_evidence_artifact=evidence,
    )
    context = build_frontend_gate_verification_context(
        tmp_path,
        [_matching_observation()],
        visual_a11y_evidence_artifact=evidence,
    )

    assert report.blockers == ()
    assert report.coverage_gaps == ()
    assert report.check_objects == (
        *FRONTEND_GATE_CHECK_OBJECTS,
        FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
        FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT,
    )
    assert context["frontend_gate_verification"]["gate_verdict"] == "PASS"


def test_contract_prerequisite_message_deduplicates_surface_lists() -> None:
    message = frontend_gate_verification_module._contract_prerequisite_message(
        SimpleNamespace(
            blockers=["same blocker", "same blocker"],
            coverage_gaps=["gap-a", "gap-a", "gap-b"],
        )
    )
    assert message == "same blocker"

    message = frontend_gate_verification_module._contract_prerequisite_message(
        SimpleNamespace(
            blockers=[],
            coverage_gaps=["gap-a", "gap-a", "gap-b"],
        )
    )
    assert message == "coverage gaps: gap-a, gap-b"


def test_browser_gate_blockers_deduplicate_receipt_hint_sources() -> None:
    blockers = frontend_gate_verification_module._browser_gate_blockers(
        [
            BrowserProbeExecutionReceipt(
                check_name="playwright_smoke",
                started_at="2026-04-14T04:05:00Z",
                finished_at="2026-04-14T04:05:00Z",
                runtime_status="incomplete",
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=[
                    "materialize shared Playwright runtime evidence",
                    "materialize shared Playwright runtime evidence",
                ],
                blocking_reason_codes=[
                    "playwright_probe_evidence_missing",
                    "playwright_probe_evidence_missing",
                ],
            )
        ],
        (
            "materialize shared Playwright runtime evidence",
            "materialize shared Playwright runtime evidence",
        ),
    )

    assert blockers == [
        "browser gate check playwright_smoke: materialize shared Playwright runtime evidence"
    ]


def test_required_artifacts_present_deduplicates_missing_artifact_names(
    tmp_path: Path,
) -> None:
    ok, detail = frontend_gate_verification_module._required_artifacts_present(
        tmp_path,
        ("missing.yaml", "missing.yaml", "other.yaml"),
    )

    assert ok is False
    assert detail == "missing required artifacts: missing.yaml, other.yaml"
