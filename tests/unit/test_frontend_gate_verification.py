"""Unit tests for frontend gate verification helpers."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

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
from ai_sdlc.models.frontend_gate_policy import (
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)


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
    assert context["frontend_gate_verification"]["gate_verdict"] == "PASS"


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
