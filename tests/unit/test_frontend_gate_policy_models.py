"""Unit tests for frontend gate policy and report models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_gate_policy import (
    CompatibilityExecutionPolicy,
    FrontendCompatibilityFeedbackBoundary,
    FrontendA11yFoundationCoverageEntry,
    FrontendCoverageGap,
    FrontendCoverageReport,
    FrontendDiagnosticsCoverageEntry,
    FrontendDriftClassification,
    FrontendDriftFinding,
    FrontendDriftReport,
    FrontendGatePolicySet,
    FrontendGateRule,
    FrontendLegacyExpansionFinding,
    FrontendLegacyExpansionReport,
    FrontendViolation,
    FrontendViolationReport,
    FrontendVisualA11yEvidenceBoundary,
    FrontendVisualA11yFeedbackBoundary,
    FrontendVisualFoundationCoverageEntry,
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_diagnostics_drift_expansion,
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)


def test_build_mvp_frontend_gate_policy_contains_expected_gate_matrix_and_priority() -> None:
    policy = build_mvp_frontend_gate_policy()

    assert policy.work_item_id == "018"
    assert policy.execution_priority == [
        "ui-kernel-standard",
        "non-exempt-hard-rules",
        "declared-rules",
        "structured-exceptions",
        "implementation-code",
    ]
    assert [rule.rule_id for rule in policy.gate_matrix] == [
        "i18n-contract-completeness",
        "validation-contract-coverage",
        "recipe-declaration-compliance",
        "whitelist-entry-compliance",
        "token-rule-compliance",
        "vue2-hard-rule-compliance",
    ]
    assert [policy.mode for policy in policy.compatibility_policies] == [
        "strict",
        "incremental",
        "compatibility",
    ]
    assert policy.report_types == [
        "violation-report",
        "coverage-report",
        "drift-report",
        "legacy-expansion-report",
    ]


def test_build_mvp_frontend_gate_policy_aligns_hard_rule_and_changed_scope_semantics() -> None:
    policy = build_mvp_frontend_gate_policy()
    constraints = build_mvp_frontend_generation_constraints()

    hard_rule_check = next(
        rule for rule in policy.gate_matrix if rule.rule_id == "vue2-hard-rule-compliance"
    )
    compatibility_mode = next(
        entry for entry in policy.compatibility_policies if entry.mode == "compatibility"
    )

    assert hard_rule_check.source_rule_refs == [
        rule.rule_id for rule in constraints.hard_rules.rules
    ]
    assert compatibility_mode.scope_mode == "changed-scope"
    assert compatibility_mode.block_new_violations is True
    assert compatibility_mode.record_existing_debt is True
    assert compatibility_mode.advisory_only_for_existing_debt is True
    assert compatibility_mode.require_legacy_expansion_report is True


def test_build_p1_frontend_gate_policy_diagnostics_drift_expansion_preserves_shared_gate_truth() -> None:
    policy = build_p1_frontend_gate_policy_diagnostics_drift_expansion()

    assert policy.work_item_id == "069"
    assert policy.execution_priority == build_mvp_frontend_gate_policy().execution_priority
    assert [rule.rule_id for rule in policy.gate_matrix] == [
        "i18n-contract-completeness",
        "validation-contract-coverage",
        "recipe-declaration-compliance",
        "whitelist-entry-compliance",
        "token-rule-compliance",
        "vue2-hard-rule-compliance",
    ]
    assert [entry.mode for entry in policy.compatibility_feedback_boundary] == [
        "strict",
        "incremental",
        "compatibility",
    ]
    assert [entry.coverage_id for entry in policy.diagnostics_coverage_matrix] == [
        "semantic-component-coverage",
        "page-recipe-coverage",
        "state-coverage",
        "whitelist-coverage",
        "token-rule-coverage",
    ]
    assert [entry.classification_id for entry in policy.drift_classification] == [
        "input-gap",
        "stable-empty-observation",
        "recipe-structure-drift",
        "state-expectation-drift",
        "whitelist-leakage",
        "token-leakage",
    ]

    semantic_component_coverage = next(
        entry
        for entry in policy.diagnostics_coverage_matrix
        if entry.coverage_id == "semantic-component-coverage"
    )
    compatibility_feedback = next(
        entry
        for entry in policy.compatibility_feedback_boundary
        if entry.mode == "compatibility"
    )
    whitelist_leakage = next(
        entry
        for entry in policy.drift_classification
        if entry.classification_id == "whitelist-leakage"
    )

    assert semantic_component_coverage.coverage_type == "semantic-component"
    assert semantic_component_coverage.governed_targets == [
        "UiTabs",
        "UiSearchBar",
        "UiFilterBar",
        "UiResult",
        "UiSection",
        "UiToolbar",
        "UiPagination",
        "UiCard",
    ]
    assert semantic_component_coverage.source_truth_refs == ["067", "018"]
    assert compatibility_feedback.allowed_feedback_surfaces == [
        "report-severity",
        "changed-scope-explanation",
        "remediation-hint",
        "legacy-expansion-context",
    ]
    assert "second-gate-system" in compatibility_feedback.forbidden_truth_mutations
    assert whitelist_leakage.report_type == "violation-report"
    assert whitelist_leakage.source_truth_refs == ["017", "067", "068", "018"]


def test_build_p1_frontend_gate_policy_visual_a11y_foundation_preserves_069_truth() -> None:
    policy = build_p1_frontend_gate_policy_visual_a11y_foundation()

    assert policy.work_item_id == "071"
    assert [entry.coverage_id for entry in policy.diagnostics_coverage_matrix] == [
        "semantic-component-coverage",
        "page-recipe-coverage",
        "state-coverage",
        "whitelist-coverage",
        "token-rule-coverage",
    ]
    assert [entry.classification_id for entry in policy.drift_classification] == [
        "input-gap",
        "stable-empty-observation",
        "recipe-structure-drift",
        "state-expectation-drift",
        "whitelist-leakage",
        "token-leakage",
    ]
    assert [entry.coverage_id for entry in policy.visual_foundation_coverage_matrix] == [
        "state-visual-presence",
        "required-area-visual-presence",
        "controlled-container-visual-continuity",
    ]
    assert [entry.coverage_id for entry in policy.a11y_foundation_coverage_matrix] == [
        "error-status-perceivability",
        "accessible-naming-semantics",
        "keyboard-reachability",
        "focus-continuity",
    ]
    assert [entry.boundary_id for entry in policy.visual_a11y_evidence_boundary] == [
        "explicit-evidence-only",
    ]
    assert [entry.boundary_id for entry in policy.visual_a11y_feedback_boundary] == [
        "shared-report-family-reuse",
    ]

    state_visual_presence = next(
        entry
        for entry in policy.visual_foundation_coverage_matrix
        if entry.coverage_id == "state-visual-presence"
    )
    accessible_naming = next(
        entry
        for entry in policy.a11y_foundation_coverage_matrix
        if entry.coverage_id == "accessible-naming-semantics"
    )
    evidence_boundary = policy.visual_a11y_evidence_boundary[0]
    feedback_boundary = policy.visual_a11y_feedback_boundary[0]

    assert state_visual_presence.quality_surface == "state-visual-presence"
    assert state_visual_presence.governed_targets == [
        "refreshing",
        "submitting",
        "no-results",
        "partial-error",
        "success-feedback",
    ]
    assert accessible_naming.governed_targets == [
        "UiInput",
        "UiFormItem",
        "UiTabs",
        "UiSearchBar",
        "UiFilterBar",
        "UiToolbar",
        "UiPagination",
        "UiResult",
    ]
    assert evidence_boundary.allowed_evidence_sources == ["explicit-input-artifact"]
    assert "workspace-root-discovery" in evidence_boundary.forbidden_implicit_sources
    assert feedback_boundary.allowed_feedback_surfaces == [
        "report-severity",
        "location-anchor",
        "quality-hint",
        "changed-scope-explanation",
    ]
    assert feedback_boundary.report_types == [
        "violation-report",
        "coverage-report",
        "drift-report",
        "legacy-expansion-report",
    ]


def test_frontend_gate_reports_are_machine_consumable() -> None:
    violation = FrontendViolation(
        rule_id="token-rule-compliance",
        severity="high",
        scope="page",
        owner="orders.list",
        source_ref="contracts/frontend/pages/orders.list/page-contract.yaml",
        target_file="src/pages/orders/list.vue",
        target_block="<template>",
        message="inline color token detected",
        expected_fix_type="replace-inline-value",
        related_contract_ref="contracts/frontend/pages/orders.list/token-rules.yaml",
    )
    coverage_gap = FrontendCoverageGap(
        check_object="validation-contract",
        severity="medium",
        scope="page",
        owner="orders.form",
        source_ref="contracts/frontend/pages/orders.form/page-contract.yaml",
        target_file="src/pages/orders/form.vue",
        target_block="validation rules",
        message="declared validation contract missing in implementation",
        expected_fix_type="add-validation-binding",
        related_contract_ref="contracts/frontend/pages/orders.form/validation.yaml",
    )
    drift = FrontendDriftFinding(
        rule_id="recipe-declaration-compliance",
        severity="high",
        scope="page",
        owner="orders.detail",
        source_ref="contracts/frontend/pages/orders.detail/page-contract.yaml",
        target_file="src/pages/orders/detail.vue",
        target_block="detail-body",
        message="implementation drifted from declared recipe regions",
        expected_fix_type="restore-recipe-regions",
        related_contract_ref="contracts/frontend/pages/orders.detail/recipe.yaml",
    )
    expansion = FrontendLegacyExpansionFinding(
        rule_id="vue2-hard-rule-compliance",
        severity="high",
        scope="changed-scope",
        owner="orders.form",
        source_ref="specs/018-frontend-gate-compatibility-baseline",
        target_file="src/pages/orders/form.vue",
        target_block="created()",
        message="new legacy dependency introduced in changed scope",
        expected_fix_type="route-through-adapter",
        related_contract_ref="contracts/frontend/pages/orders.form/page-contract.yaml",
    )

    violation_report = FrontendViolationReport(violations=[violation])
    coverage_report = FrontendCoverageReport(gaps=[coverage_gap])
    drift_report = FrontendDriftReport(drifts=[drift])
    expansion_report = FrontendLegacyExpansionReport(expansions=[expansion])

    assert violation_report.model_dump()["violations"][0]["expected_fix_type"] == (
        "replace-inline-value"
    )
    assert coverage_report.model_dump()["gaps"][0]["check_object"] == "validation-contract"
    assert drift_report.model_dump()["drifts"][0]["rule_id"] == (
        "recipe-declaration-compliance"
    )
    assert expansion_report.model_dump()["expansions"][0]["scope"] == "changed-scope"


def test_frontend_gate_policy_set_rejects_duplicate_rule_ids_and_policy_modes() -> None:
    with pytest.raises(ValueError, match="duplicate gate rule ids"):
        FrontendGatePolicySet(
            work_item_id="018",
            execution_priority=["ui-kernel-standard", "implementation-code"],
            gate_matrix=[
                FrontendGateRule(
                    rule_id="i18n-contract-completeness",
                    family="i18n",
                    severity="high",
                    required_sources=["contract", "implementation-code"],
                ),
                FrontendGateRule(
                    rule_id="i18n-contract-completeness",
                    family="i18n",
                    severity="high",
                    required_sources=["contract", "implementation-code"],
                ),
            ],
            compatibility_policies=[
                CompatibilityExecutionPolicy(
                    mode="strict",
                    scope_mode="entire-scope",
                    block_new_violations=True,
                    record_existing_debt=True,
                ),
            ],
            report_types=["violation-report"],
        )


def test_frontend_gate_policy_set_rejects_unknown_diagnostics_targets_report_types_and_modes() -> None:
    base_policy = build_mvp_frontend_gate_policy()

    with pytest.raises(
        ValueError,
        match="diagnostics_coverage_matrix references unknown governed_targets",
    ):
        FrontendGatePolicySet(
            work_item_id="069",
            execution_priority=base_policy.execution_priority,
            gate_matrix=base_policy.gate_matrix,
            compatibility_policies=base_policy.compatibility_policies,
            report_types=base_policy.report_types,
            diagnostics_coverage_matrix=[
                FrontendDiagnosticsCoverageEntry(
                    coverage_id="semantic-component-coverage",
                    coverage_type="semantic-component",
                    governed_targets=["UiGhost"],
                    source_truth_refs=["067", "018"],
                    diagnostic_focus="should fail",
                )
            ],
        )

    with pytest.raises(
        ValueError,
        match="visual_foundation_coverage_matrix references unknown governed_targets",
    ):
        FrontendGatePolicySet(
            work_item_id="071",
            execution_priority=base_policy.execution_priority,
            gate_matrix=base_policy.gate_matrix,
            compatibility_policies=base_policy.compatibility_policies,
            report_types=base_policy.report_types,
            visual_foundation_coverage_matrix=[
                FrontendVisualFoundationCoverageEntry(
                    coverage_id="state-visual-presence",
                    quality_surface="state-visual-presence",
                    governed_targets=["UnknownVisualTarget"],
                    source_truth_refs=["067", "068", "069", "018"],
                    expectation="state should remain visible",
                )
            ],
        )

    with pytest.raises(
        ValueError,
        match="visual_a11y_feedback_boundary references unknown report_types",
    ):
        FrontendGatePolicySet(
            work_item_id="071",
            execution_priority=base_policy.execution_priority,
            gate_matrix=base_policy.gate_matrix,
            compatibility_policies=base_policy.compatibility_policies,
            report_types=base_policy.report_types,
            visual_a11y_feedback_boundary=[
                FrontendVisualA11yFeedbackBoundary(
                    boundary_id="shared-report-family-reuse",
                    allowed_feedback_surfaces=["report-severity"],
                    report_types=["visual-report"],
                    forbidden_expansions=["second-visual-gate-system"],
                    source_truth_refs=["018", "069", "070"],
                )
            ],
        )

    with pytest.raises(
        ValueError,
        match="drift_classification references unknown report_types",
    ):
        FrontendGatePolicySet(
            work_item_id="069",
            execution_priority=base_policy.execution_priority,
            gate_matrix=base_policy.gate_matrix,
            compatibility_policies=base_policy.compatibility_policies,
            report_types=base_policy.report_types,
            drift_classification=[
                FrontendDriftClassification(
                    classification_id="input-gap",
                    trigger_condition="missing artifact",
                    report_type="ghost-report",
                    severity_floor="medium",
                    source_truth_refs=["065", "018"],
                )
            ],
        )

    with pytest.raises(
        ValueError,
        match="compatibility_feedback_boundary references unknown modes",
    ):
        FrontendGatePolicySet(
            work_item_id="069",
            execution_priority=base_policy.execution_priority,
            gate_matrix=base_policy.gate_matrix,
            compatibility_policies=base_policy.compatibility_policies,
            report_types=base_policy.report_types,
            compatibility_feedback_boundary=[
                FrontendCompatibilityFeedbackBoundary(
                    mode="shadow",
                    allowed_feedback_surfaces=["report-severity"],
                    forbidden_truth_mutations=["kernel-truth"],
                )
            ],
        )

    with pytest.raises(ValueError, match="duplicate compatibility modes"):
        FrontendGatePolicySet(
            work_item_id="018",
            execution_priority=["ui-kernel-standard", "implementation-code"],
            gate_matrix=[
                FrontendGateRule(
                    rule_id="i18n-contract-completeness",
                    family="i18n",
                    severity="high",
                    required_sources=["contract", "implementation-code"],
                )
            ],
            compatibility_policies=[
                CompatibilityExecutionPolicy(
                    mode="strict",
                    scope_mode="entire-scope",
                    block_new_violations=True,
                    record_existing_debt=True,
                ),
                CompatibilityExecutionPolicy(
                    mode="strict",
                    scope_mode="changed-scope",
                    block_new_violations=True,
                    record_existing_debt=True,
                ),
            ],
            report_types=["violation-report"],
        )
