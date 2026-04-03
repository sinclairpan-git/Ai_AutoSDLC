"""Unit tests for frontend gate policy and report models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_gate_policy import (
    CompatibilityExecutionPolicy,
    FrontendCoverageGap,
    FrontendCoverageReport,
    FrontendDriftFinding,
    FrontendDriftReport,
    FrontendGatePolicySet,
    FrontendGateRule,
    FrontendLegacyExpansionFinding,
    FrontendLegacyExpansionReport,
    FrontendViolation,
    FrontendViolationReport,
    build_mvp_frontend_gate_policy,
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
