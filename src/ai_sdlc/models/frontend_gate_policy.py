"""Frontend gate matrix, compatibility policy, and report models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_ui_kernel import (
    build_mvp_frontend_ui_kernel,
    build_p1_frontend_ui_kernel_page_recipe_expansion,
    build_p1_frontend_ui_kernel_semantic_expansion,
)

ALLOWED_GATE_POLICY_TRUTH_REFS = {"017", "018", "065", "067", "068"}
ALLOWED_DIAGNOSTICS_COVERAGE_TYPES = {
    "semantic-component",
    "page-recipe",
    "state",
    "whitelist",
    "token-rule",
}


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _find_unknown_references(values: list[str], known_values: set[str]) -> list[str]:
    unknown: list[str] = []
    for value in values:
        if value not in known_values and value not in unknown:
            unknown.append(value)
    return unknown


class FrontendGateModel(BaseModel):
    """Base model for frontend gate policy payloads."""

    model_config = ConfigDict(extra="forbid")


class FrontendGateRule(FrontendGateModel):
    """Single gate matrix rule in the MVP frontend governance surface."""

    rule_id: str
    family: str
    severity: str
    required_sources: list[str] = Field(default_factory=list)
    description: str = ""
    source_rule_refs: list[str] = Field(default_factory=list)
    allow_structured_exceptions: bool = True


class CompatibilityExecutionPolicy(FrontendGateModel):
    """Compatibility execution intensity for the shared gate matrix."""

    mode: str
    scope_mode: str
    block_new_violations: bool = True
    record_existing_debt: bool = True
    advisory_only_for_existing_debt: bool = False
    require_legacy_expansion_report: bool = False
    description: str = ""


class FrontendDiagnosticsCoverageEntry(FrontendGateModel):
    """P1 diagnostics coverage expansion entry."""

    coverage_id: str
    coverage_type: str
    governed_targets: list[str] = Field(default_factory=list)
    source_truth_refs: list[str] = Field(default_factory=list)
    diagnostic_focus: str
    boundary: str = ""


class FrontendDriftClassification(FrontendGateModel):
    """P1 drift, gap, or leakage classification entry."""

    classification_id: str
    trigger_condition: str
    report_type: str
    severity_floor: str
    source_truth_refs: list[str] = Field(default_factory=list)
    boundary: str = ""


class FrontendCompatibilityFeedbackBoundary(FrontendGateModel):
    """Compatibility feedback boundary for one shared gate mode."""

    mode: str
    allowed_feedback_surfaces: list[str] = Field(default_factory=list)
    forbidden_truth_mutations: list[str] = Field(default_factory=list)
    description: str = ""

    @model_validator(mode="after")
    def _enforce_unique_feedback_lists(self) -> FrontendCompatibilityFeedbackBoundary:
        duplicate_surfaces = _find_duplicates(self.allowed_feedback_surfaces)
        if duplicate_surfaces:
            joined = ", ".join(duplicate_surfaces)
            raise ValueError(
                f"duplicate compatibility allowed_feedback_surfaces: {joined}"
            )

        duplicate_mutations = _find_duplicates(self.forbidden_truth_mutations)
        if duplicate_mutations:
            joined = ", ".join(duplicate_mutations)
            raise ValueError(
                f"duplicate compatibility forbidden_truth_mutations: {joined}"
            )
        return self


class FrontendViolation(FrontendGateModel):
    """Machine-consumable frontend violation item."""

    rule_id: str
    severity: str
    scope: str
    owner: str
    source_ref: str
    target_file: str
    target_block: str
    message: str
    expected_fix_type: str
    related_contract_ref: str


class FrontendCoverageGap(FrontendGateModel):
    """Machine-consumable coverage gap item."""

    check_object: str
    severity: str
    scope: str
    owner: str
    source_ref: str
    target_file: str
    target_block: str
    message: str
    expected_fix_type: str
    related_contract_ref: str


class FrontendDriftFinding(FrontendGateModel):
    """Machine-consumable contract drift item."""

    rule_id: str
    severity: str
    scope: str
    owner: str
    source_ref: str
    target_file: str
    target_block: str
    message: str
    expected_fix_type: str
    related_contract_ref: str


class FrontendLegacyExpansionFinding(FrontendGateModel):
    """Machine-consumable legacy expansion finding."""

    rule_id: str
    severity: str
    scope: str
    owner: str
    source_ref: str
    target_file: str
    target_block: str
    message: str
    expected_fix_type: str
    related_contract_ref: str


class FrontendViolationReport(FrontendGateModel):
    """Structured violation report payload."""

    report_type: str = "violation-report"
    violations: list[FrontendViolation] = Field(default_factory=list)


class FrontendCoverageReport(FrontendGateModel):
    """Structured coverage report payload."""

    report_type: str = "coverage-report"
    gaps: list[FrontendCoverageGap] = Field(default_factory=list)


class FrontendDriftReport(FrontendGateModel):
    """Structured drift report payload."""

    report_type: str = "drift-report"
    drifts: list[FrontendDriftFinding] = Field(default_factory=list)


class FrontendLegacyExpansionReport(FrontendGateModel):
    """Structured legacy expansion report payload."""

    report_type: str = "legacy-expansion-report"
    expansions: list[FrontendLegacyExpansionFinding] = Field(default_factory=list)


class FrontendGatePolicySet(FrontendGateModel):
    """Top-level shared gate matrix and compatibility policy set."""

    work_item_id: str
    execution_priority: list[str] = Field(default_factory=list)
    gate_matrix: list[FrontendGateRule] = Field(default_factory=list)
    compatibility_policies: list[CompatibilityExecutionPolicy] = Field(
        default_factory=list
    )
    report_types: list[str] = Field(default_factory=list)
    diagnostics_coverage_matrix: list[FrontendDiagnosticsCoverageEntry] = Field(
        default_factory=list
    )
    drift_classification: list[FrontendDriftClassification] = Field(default_factory=list)
    compatibility_feedback_boundary: list[FrontendCompatibilityFeedbackBoundary] = (
        Field(default_factory=list)
    )

    @model_validator(mode="after")
    def _enforce_unique_rule_ids_and_modes(self) -> FrontendGatePolicySet:
        duplicate_rule_ids = _find_duplicates([rule.rule_id for rule in self.gate_matrix])
        if duplicate_rule_ids:
            joined = ", ".join(duplicate_rule_ids)
            raise ValueError(f"duplicate gate rule ids: {joined}")

        duplicate_modes = _find_duplicates(
            [policy.mode for policy in self.compatibility_policies]
        )
        if duplicate_modes:
            joined = ", ".join(duplicate_modes)
            raise ValueError(f"duplicate compatibility modes: {joined}")

        duplicate_coverage_ids = _find_duplicates(
            [entry.coverage_id for entry in self.diagnostics_coverage_matrix]
        )
        if duplicate_coverage_ids:
            joined = ", ".join(duplicate_coverage_ids)
            raise ValueError(f"duplicate diagnostics coverage ids: {joined}")

        duplicate_classification_ids = _find_duplicates(
            [entry.classification_id for entry in self.drift_classification]
        )
        if duplicate_classification_ids:
            joined = ", ".join(duplicate_classification_ids)
            raise ValueError(f"duplicate drift classification ids: {joined}")

        duplicate_boundary_modes = _find_duplicates(
            [entry.mode for entry in self.compatibility_feedback_boundary]
        )
        if duplicate_boundary_modes:
            joined = ", ".join(duplicate_boundary_modes)
            raise ValueError(f"duplicate compatibility feedback boundary modes: {joined}")

        unknown_coverage_types = _find_unknown_references(
            [entry.coverage_type for entry in self.diagnostics_coverage_matrix],
            ALLOWED_DIAGNOSTICS_COVERAGE_TYPES,
        )
        if unknown_coverage_types:
            joined = ", ".join(unknown_coverage_types)
            raise ValueError(f"unknown diagnostics coverage types: {joined}")

        if self.diagnostics_coverage_matrix:
            kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()
            known_surface_ids = {
                component.component_id for component in kernel.semantic_components
            }
            known_surface_ids.update(
                recipe.recipe_id for recipe in kernel.page_recipes
            )
            known_surface_ids.update(kernel.state_baseline.required_states)

            unknown_governed_targets = _find_unknown_references(
                [
                    target
                    for entry in self.diagnostics_coverage_matrix
                    for target in entry.governed_targets
                ],
                known_surface_ids,
            )
            if unknown_governed_targets:
                joined = ", ".join(unknown_governed_targets)
                raise ValueError(
                    "diagnostics_coverage_matrix references unknown governed_targets: "
                    f"{joined}"
                )

        unknown_diagnostics_truth_refs = _find_unknown_references(
            [
                truth_ref
                for entry in self.diagnostics_coverage_matrix
                for truth_ref in entry.source_truth_refs
            ],
            ALLOWED_GATE_POLICY_TRUTH_REFS,
        )
        if unknown_diagnostics_truth_refs:
            joined = ", ".join(unknown_diagnostics_truth_refs)
            raise ValueError(
                "diagnostics_coverage_matrix references unknown source_truth_refs: "
                f"{joined}"
            )

        unknown_drift_truth_refs = _find_unknown_references(
            [
                truth_ref
                for entry in self.drift_classification
                for truth_ref in entry.source_truth_refs
            ],
            ALLOWED_GATE_POLICY_TRUTH_REFS,
        )
        if unknown_drift_truth_refs:
            joined = ", ".join(unknown_drift_truth_refs)
            raise ValueError(
                f"drift_classification references unknown source_truth_refs: {joined}"
            )

        unknown_report_types = _find_unknown_references(
            [entry.report_type for entry in self.drift_classification],
            set(self.report_types),
        )
        if unknown_report_types:
            joined = ", ".join(unknown_report_types)
            raise ValueError(
                f"drift_classification references unknown report_types: {joined}"
            )

        unknown_boundary_modes = _find_unknown_references(
            [entry.mode for entry in self.compatibility_feedback_boundary],
            {policy.mode for policy in self.compatibility_policies},
        )
        if unknown_boundary_modes:
            joined = ", ".join(unknown_boundary_modes)
            raise ValueError(
                f"compatibility_feedback_boundary references unknown modes: {joined}"
            )

        return self


def build_mvp_frontend_gate_policy() -> FrontendGatePolicySet:
    """Build the MVP gate/compatibility control plane defined by work item 018."""

    constraints = build_mvp_frontend_generation_constraints()

    return FrontendGatePolicySet(
        work_item_id="018",
        execution_priority=[
            "ui-kernel-standard",
            "non-exempt-hard-rules",
            "declared-rules",
            "structured-exceptions",
            "implementation-code",
        ],
        gate_matrix=[
            FrontendGateRule(
                rule_id="i18n-contract-completeness",
                family="i18n",
                severity="high",
                required_sources=[
                    "page-metadata",
                    "i18n-contract",
                    "implementation-code",
                ],
                description="declared i18n contract must match implementation usage",
            ),
            FrontendGateRule(
                rule_id="validation-contract-coverage",
                family="validation",
                severity="high",
                required_sources=[
                    "page-metadata",
                    "validation-contract",
                    "implementation-code",
                ],
                description="declared validation contract must be implemented",
            ),
            FrontendGateRule(
                rule_id="recipe-declaration-compliance",
                family="recipe",
                severity="high",
                required_sources=[
                    "recipe-declaration",
                    "ui-kernel",
                    "implementation-code",
                ],
                description="page implementation must respect declared recipe regions",
            ),
            FrontendGateRule(
                rule_id="whitelist-entry-compliance",
                family="whitelist",
                severity="high",
                required_sources=[
                    "provider-profile",
                    "generation-constraints",
                    "implementation-code",
                ],
                description="implementation must enter through whitelist-approved surfaces",
            ),
            FrontendGateRule(
                rule_id="token-rule-compliance",
                family="token-rules",
                severity="high",
                required_sources=[
                    "token-rules-ref",
                    "generation-constraints",
                    "implementation-code",
                ],
                description="implementation must avoid naked visual values",
            ),
            FrontendGateRule(
                rule_id="vue2-hard-rule-compliance",
                family="hard-rules",
                severity="high",
                required_sources=[
                    "hard-rules-set",
                    "provider-profile",
                    "implementation-code",
                ],
                description="non-exempt vue2 hard rules remain blocking in MVP",
                source_rule_refs=[
                    rule.rule_id for rule in constraints.hard_rules.rules
                ],
                allow_structured_exceptions=False,
            ),
        ],
        compatibility_policies=[
            CompatibilityExecutionPolicy(
                mode="strict",
                scope_mode="entire-scope",
                block_new_violations=True,
                record_existing_debt=True,
                advisory_only_for_existing_debt=False,
                require_legacy_expansion_report=True,
                description="new or standard pages run the full gate matrix over the whole scope",
            ),
            CompatibilityExecutionPolicy(
                mode="incremental",
                scope_mode="changed-scope",
                block_new_violations=True,
                record_existing_debt=True,
                advisory_only_for_existing_debt=True,
                require_legacy_expansion_report=True,
                description="changed scope is strict while unchanged debt stays recorded",
            ),
            CompatibilityExecutionPolicy(
                mode="compatibility",
                scope_mode="changed-scope",
                block_new_violations=True,
                record_existing_debt=True,
                advisory_only_for_existing_debt=True,
                require_legacy_expansion_report=True,
                description="stop new degradation and record debt without inventing a second gate system",
            ),
        ],
        report_types=[
            "violation-report",
            "coverage-report",
            "drift-report",
            "legacy-expansion-report",
        ],
    )


def build_p1_frontend_gate_policy_diagnostics_drift_expansion() -> FrontendGatePolicySet:
    """Build the P1 diagnostics/drift truth on top of the shared 018 gate policy."""

    base_policy = build_mvp_frontend_gate_policy()
    mvp_kernel = build_mvp_frontend_ui_kernel()
    semantic_expansion = build_p1_frontend_ui_kernel_semantic_expansion()
    recipe_expansion = build_p1_frontend_ui_kernel_page_recipe_expansion()

    mvp_component_ids = {
        component.component_id for component in mvp_kernel.semantic_components
    }
    p1_component_ids = [
        component.component_id
        for component in semantic_expansion.semantic_components
        if component.component_id not in mvp_component_ids
    ]

    mvp_state_ids = set(mvp_kernel.state_baseline.required_states)
    p1_state_ids = [
        state_id
        for state_id in semantic_expansion.state_baseline.required_states
        if state_id not in mvp_state_ids
    ]

    mvp_recipe_ids = {recipe.recipe_id for recipe in mvp_kernel.page_recipes}
    p1_recipe_ids = [
        recipe.recipe_id
        for recipe in recipe_expansion.page_recipes
        if recipe.recipe_id not in mvp_recipe_ids
    ]

    return FrontendGatePolicySet(
        work_item_id="069",
        execution_priority=base_policy.execution_priority,
        gate_matrix=base_policy.gate_matrix,
        compatibility_policies=base_policy.compatibility_policies,
        report_types=base_policy.report_types,
        diagnostics_coverage_matrix=[
            FrontendDiagnosticsCoverageEntry(
                coverage_id="semantic-component-coverage",
                coverage_type="semantic-component",
                governed_targets=p1_component_ids,
                source_truth_refs=["067", "018"],
                diagnostic_focus="validate P1 semantic component entry and structure role usage",
                boundary="consumes controlled Ui* semantics without defining provider APIs",
            ),
            FrontendDiagnosticsCoverageEntry(
                coverage_id="page-recipe-coverage",
                coverage_type="page-recipe",
                governed_targets=p1_recipe_ids,
                source_truth_refs=["068", "018"],
                diagnostic_focus="validate required areas, optional areas, and forbidden patterns",
                boundary="consumes recipe truth without redefining recipe bodies",
            ),
            FrontendDiagnosticsCoverageEntry(
                coverage_id="state-coverage",
                coverage_type="state",
                governed_targets=p1_state_ids,
                source_truth_refs=["067", "068", "018"],
                diagnostic_focus="validate P1 state expectations alongside MVP state baseline",
                boundary="extends coverage only and keeps MVP state semantics intact",
            ),
            FrontendDiagnosticsCoverageEntry(
                coverage_id="whitelist-coverage",
                coverage_type="whitelist",
                governed_targets=[*p1_component_ids, *p1_recipe_ids],
                source_truth_refs=["017", "067", "068", "018"],
                diagnostic_focus="detect bypasses of controlled Ui* entry points and recipe combinations",
                boundary="does not enlarge the default whitelist or provider exemptions",
            ),
            FrontendDiagnosticsCoverageEntry(
                coverage_id="token-rule-coverage",
                coverage_type="token-rule",
                governed_targets=p1_recipe_ids,
                source_truth_refs=["017", "068", "018"],
                diagnostic_focus="extend minimal token-rule checks into new P1 recipe structures",
                boundary="does not upgrade minimal token rules into a full token platform",
            ),
        ],
        drift_classification=[
            FrontendDriftClassification(
                classification_id="input-gap",
                trigger_condition="observation artifact missing for the target spec_dir",
                report_type="coverage-report",
                severity_floor="medium",
                source_truth_refs=["065", "018"],
                boundary="reports missing inputs without misclassifying them as drift",
            ),
            FrontendDriftClassification(
                classification_id="stable-empty-observation",
                trigger_condition="observation artifact exists but the observations list is empty",
                report_type="coverage-report",
                severity_floor="medium",
                source_truth_refs=["065", "018"],
                boundary="records a stable empty result without silently turning green",
            ),
            FrontendDriftClassification(
                classification_id="recipe-structure-drift",
                trigger_condition="implementation structure diverges from required areas or forbidden patterns",
                report_type="drift-report",
                severity_floor="high",
                source_truth_refs=["068", "018"],
                boundary="consumes recipe truth without redefining recipe bodies",
            ),
            FrontendDriftClassification(
                classification_id="state-expectation-drift",
                trigger_condition="required P1 state semantics are missing, misused, or conflict with recipe expectations",
                report_type="drift-report",
                severity_floor="high",
                source_truth_refs=["067", "068", "018"],
                boundary="evaluates state expectations without introducing new state vocabularies",
            ),
            FrontendDriftClassification(
                classification_id="whitelist-leakage",
                trigger_condition="implementation bypasses controlled Ui* entry points or leaks outside whitelist boundaries",
                report_type="violation-report",
                severity_floor="high",
                source_truth_refs=["017", "067", "068", "018"],
                boundary="reuses whitelist truth without widening exemptions",
            ),
            FrontendDriftClassification(
                classification_id="token-leakage",
                trigger_condition="implementation introduces naked values or token violations in P1 structures",
                report_type="violation-report",
                severity_floor="high",
                source_truth_refs=["017", "068", "018"],
                boundary="reuses minimal token truth without becoming a full token platform",
            ),
        ],
        compatibility_feedback_boundary=[
            FrontendCompatibilityFeedbackBoundary(
                mode="strict",
                allowed_feedback_surfaces=[
                    "report-severity",
                    "changed-scope-explanation",
                    "remediation-hint",
                ],
                forbidden_truth_mutations=[
                    "kernel-truth",
                    "recipe-truth",
                    "whitelist-truth",
                    "token-truth",
                ],
                description="strict mode keeps the full gate semantics and only shapes operator feedback",
            ),
            FrontendCompatibilityFeedbackBoundary(
                mode="incremental",
                allowed_feedback_surfaces=[
                    "report-severity",
                    "changed-scope-explanation",
                    "remediation-hint",
                ],
                forbidden_truth_mutations=[
                    "kernel-truth",
                    "recipe-truth",
                    "whitelist-truth",
                    "token-truth",
                ],
                description="incremental mode keeps changed-scope semantics without relaxing upstream truths",
            ),
            FrontendCompatibilityFeedbackBoundary(
                mode="compatibility",
                allowed_feedback_surfaces=[
                    "report-severity",
                    "changed-scope-explanation",
                    "remediation-hint",
                    "legacy-expansion-context",
                ],
                forbidden_truth_mutations=[
                    "kernel-truth",
                    "recipe-truth",
                    "whitelist-truth",
                    "token-truth",
                    "second-gate-system",
                ],
                description="compatibility mode can add debt context but cannot create a second gate system",
            ),
        ],
    )


__all__ = [
    "CompatibilityExecutionPolicy",
    "FrontendCompatibilityFeedbackBoundary",
    "FrontendCoverageGap",
    "FrontendCoverageReport",
    "FrontendDiagnosticsCoverageEntry",
    "FrontendDriftFinding",
    "FrontendDriftClassification",
    "FrontendDriftReport",
    "FrontendGatePolicySet",
    "FrontendGateRule",
    "FrontendLegacyExpansionFinding",
    "FrontendLegacyExpansionReport",
    "FrontendViolation",
    "FrontendViolationReport",
    "build_mvp_frontend_gate_policy",
    "build_p1_frontend_gate_policy_diagnostics_drift_expansion",
]
