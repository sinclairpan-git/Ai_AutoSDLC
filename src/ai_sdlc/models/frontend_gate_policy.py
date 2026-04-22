"""Frontend gate matrix, compatibility policy, and report models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_ui_kernel import (
    build_mvp_frontend_ui_kernel,
    build_p1_frontend_ui_kernel_page_recipe_expansion,
    build_p1_frontend_ui_kernel_semantic_expansion,
)

ALLOWED_GATE_POLICY_TRUTH_REFS = {
    "015",
    "017",
    "018",
    "065",
    "067",
    "068",
    "069",
    "070",
    "071",
}
ALLOWED_DIAGNOSTICS_COVERAGE_TYPES = {
    "semantic-component",
    "page-recipe",
    "state",
    "whitelist",
    "token-rule",
}
ALLOWED_VISUAL_FOUNDATION_SURFACES = {
    "state-visual-presence",
    "required-area-visual-presence",
    "controlled-container-visual-continuity",
}
ALLOWED_A11Y_FOUNDATION_SURFACES = {
    "error-status-perceivability",
    "accessible-naming-semantics",
    "keyboard-reachability",
    "focus-continuity",
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


def _dedupe_strings(value: object) -> list[str]:
    if value is None:
        return []
    unique: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


def _dedupe_model_items(value: object) -> list[BaseModel]:
    if value is None:
        return []
    unique: list[BaseModel] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, BaseModel):
            continue
        key = item.model_dump_json()
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


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

    @field_validator("required_sources", "source_rule_refs", mode="before")
    @classmethod
    def _dedupe_rule_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


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

    @field_validator("governed_targets", "source_truth_refs", mode="before")
    @classmethod
    def _dedupe_diagnostics_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class FrontendDriftClassification(FrontendGateModel):
    """P1 drift, gap, or leakage classification entry."""

    classification_id: str
    trigger_condition: str
    report_type: str
    severity_floor: str
    source_truth_refs: list[str] = Field(default_factory=list)
    boundary: str = ""

    @field_validator("source_truth_refs", mode="before")
    @classmethod
    def _dedupe_truth_refs(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class FrontendCompatibilityFeedbackBoundary(FrontendGateModel):
    """Compatibility feedback boundary for one shared gate mode."""

    mode: str
    allowed_feedback_surfaces: list[str] = Field(default_factory=list)
    forbidden_truth_mutations: list[str] = Field(default_factory=list)
    description: str = ""

    @field_validator("allowed_feedback_surfaces", "forbidden_truth_mutations", mode="before")
    @classmethod
    def _dedupe_feedback_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

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


class FrontendVisualFoundationCoverageEntry(FrontendGateModel):
    """P1 visual foundation coverage entry."""

    coverage_id: str
    quality_surface: str
    governed_targets: list[str] = Field(default_factory=list)
    source_truth_refs: list[str] = Field(default_factory=list)
    expectation: str
    boundary: str = ""

    @field_validator("governed_targets", "source_truth_refs", mode="before")
    @classmethod
    def _dedupe_coverage_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class FrontendA11yFoundationCoverageEntry(FrontendGateModel):
    """P1 accessibility foundation coverage entry."""

    coverage_id: str
    quality_surface: str
    governed_targets: list[str] = Field(default_factory=list)
    source_truth_refs: list[str] = Field(default_factory=list)
    expectation: str
    boundary: str = ""

    @field_validator("governed_targets", "source_truth_refs", mode="before")
    @classmethod
    def _dedupe_coverage_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)


class FrontendVisualA11yEvidenceBoundary(FrontendGateModel):
    """Boundary describing allowed evidence sources for visual/a11y feedback."""

    boundary_id: str
    allowed_evidence_sources: list[str] = Field(default_factory=list)
    forbidden_implicit_sources: list[str] = Field(default_factory=list)
    source_truth_refs: list[str] = Field(default_factory=list)
    description: str = ""

    @field_validator(
        "allowed_evidence_sources",
        "forbidden_implicit_sources",
        "source_truth_refs",
        mode="before",
    )
    @classmethod
    def _dedupe_evidence_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _enforce_unique_evidence_lists(self) -> FrontendVisualA11yEvidenceBoundary:
        duplicate_sources = _find_duplicates(self.allowed_evidence_sources)
        if duplicate_sources:
            joined = ", ".join(duplicate_sources)
            raise ValueError(
                f"duplicate visual_a11y allowed_evidence_sources: {joined}"
            )

        duplicate_implicit_sources = _find_duplicates(
            self.forbidden_implicit_sources
        )
        if duplicate_implicit_sources:
            joined = ", ".join(duplicate_implicit_sources)
            raise ValueError(
                f"duplicate visual_a11y forbidden_implicit_sources: {joined}"
            )
        return self


class FrontendVisualA11yFeedbackBoundary(FrontendGateModel):
    """Boundary describing report-family reuse for visual/a11y feedback."""

    boundary_id: str
    allowed_feedback_surfaces: list[str] = Field(default_factory=list)
    report_types: list[str] = Field(default_factory=list)
    forbidden_expansions: list[str] = Field(default_factory=list)
    source_truth_refs: list[str] = Field(default_factory=list)
    description: str = ""

    @field_validator(
        "allowed_feedback_surfaces",
        "report_types",
        "forbidden_expansions",
        "source_truth_refs",
        mode="before",
    )
    @classmethod
    def _dedupe_feedback_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _enforce_unique_feedback_lists(self) -> FrontendVisualA11yFeedbackBoundary:
        duplicate_surfaces = _find_duplicates(self.allowed_feedback_surfaces)
        if duplicate_surfaces:
            joined = ", ".join(duplicate_surfaces)
            raise ValueError(
                f"duplicate visual_a11y allowed_feedback_surfaces: {joined}"
            )

        duplicate_report_types = _find_duplicates(self.report_types)
        if duplicate_report_types:
            joined = ", ".join(duplicate_report_types)
            raise ValueError(f"duplicate visual_a11y report_types: {joined}")

        duplicate_expansions = _find_duplicates(self.forbidden_expansions)
        if duplicate_expansions:
            joined = ", ".join(duplicate_expansions)
            raise ValueError(f"duplicate visual_a11y forbidden_expansions: {joined}")
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

    @field_validator("violations", mode="after")
    @classmethod
    def _dedupe_violations(
        cls, value: object
    ) -> list[FrontendViolation]:
        return _dedupe_model_items(value)


class FrontendCoverageReport(FrontendGateModel):
    """Structured coverage report payload."""

    report_type: str = "coverage-report"
    gaps: list[FrontendCoverageGap] = Field(default_factory=list)

    @field_validator("gaps", mode="after")
    @classmethod
    def _dedupe_gaps(
        cls, value: object
    ) -> list[FrontendCoverageGap]:
        return _dedupe_model_items(value)


class FrontendDriftReport(FrontendGateModel):
    """Structured drift report payload."""

    report_type: str = "drift-report"
    drifts: list[FrontendDriftFinding] = Field(default_factory=list)

    @field_validator("drifts", mode="after")
    @classmethod
    def _dedupe_drifts(
        cls, value: object
    ) -> list[FrontendDriftFinding]:
        return _dedupe_model_items(value)


class FrontendLegacyExpansionReport(FrontendGateModel):
    """Structured legacy expansion report payload."""

    report_type: str = "legacy-expansion-report"
    expansions: list[FrontendLegacyExpansionFinding] = Field(default_factory=list)

    @field_validator("expansions", mode="after")
    @classmethod
    def _dedupe_expansions(
        cls, value: object
    ) -> list[FrontendLegacyExpansionFinding]:
        return _dedupe_model_items(value)


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
    visual_foundation_coverage_matrix: list[FrontendVisualFoundationCoverageEntry] = (
        Field(default_factory=list)
    )
    a11y_foundation_coverage_matrix: list[FrontendA11yFoundationCoverageEntry] = (
        Field(default_factory=list)
    )
    visual_a11y_evidence_boundary: list[FrontendVisualA11yEvidenceBoundary] = Field(
        default_factory=list
    )
    visual_a11y_feedback_boundary: list[FrontendVisualA11yFeedbackBoundary] = Field(
        default_factory=list
    )

    @field_validator("execution_priority", "report_types", mode="before")
    @classmethod
    def _dedupe_policy_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

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

        duplicate_visual_coverage_ids = _find_duplicates(
            [entry.coverage_id for entry in self.visual_foundation_coverage_matrix]
        )
        if duplicate_visual_coverage_ids:
            joined = ", ".join(duplicate_visual_coverage_ids)
            raise ValueError(f"duplicate visual foundation coverage ids: {joined}")

        duplicate_a11y_coverage_ids = _find_duplicates(
            [entry.coverage_id for entry in self.a11y_foundation_coverage_matrix]
        )
        if duplicate_a11y_coverage_ids:
            joined = ", ".join(duplicate_a11y_coverage_ids)
            raise ValueError(f"duplicate a11y foundation coverage ids: {joined}")

        duplicate_evidence_boundary_ids = _find_duplicates(
            [entry.boundary_id for entry in self.visual_a11y_evidence_boundary]
        )
        if duplicate_evidence_boundary_ids:
            joined = ", ".join(duplicate_evidence_boundary_ids)
            raise ValueError(f"duplicate visual a11y evidence boundary ids: {joined}")

        duplicate_feedback_boundary_ids = _find_duplicates(
            [entry.boundary_id for entry in self.visual_a11y_feedback_boundary]
        )
        if duplicate_feedback_boundary_ids:
            joined = ", ".join(duplicate_feedback_boundary_ids)
            raise ValueError(f"duplicate visual a11y feedback boundary ids: {joined}")

        unknown_coverage_types = _find_unknown_references(
            [entry.coverage_type for entry in self.diagnostics_coverage_matrix],
            ALLOWED_DIAGNOSTICS_COVERAGE_TYPES,
        )
        if unknown_coverage_types:
            joined = ", ".join(unknown_coverage_types)
            raise ValueError(f"unknown diagnostics coverage types: {joined}")

        unknown_visual_surfaces = _find_unknown_references(
            [entry.quality_surface for entry in self.visual_foundation_coverage_matrix],
            ALLOWED_VISUAL_FOUNDATION_SURFACES,
        )
        if unknown_visual_surfaces:
            joined = ", ".join(unknown_visual_surfaces)
            raise ValueError(f"unknown visual foundation quality surfaces: {joined}")

        unknown_a11y_surfaces = _find_unknown_references(
            [entry.quality_surface for entry in self.a11y_foundation_coverage_matrix],
            ALLOWED_A11Y_FOUNDATION_SURFACES,
        )
        if unknown_a11y_surfaces:
            joined = ", ".join(unknown_a11y_surfaces)
            raise ValueError(f"unknown a11y foundation quality surfaces: {joined}")

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

        known_visual_a11y_targets = _known_p1_visual_a11y_targets()

        unknown_visual_governed_targets = _find_unknown_references(
            [
                target
                for entry in self.visual_foundation_coverage_matrix
                for target in entry.governed_targets
            ],
            known_visual_a11y_targets,
        )
        if unknown_visual_governed_targets:
            joined = ", ".join(unknown_visual_governed_targets)
            raise ValueError(
                "visual_foundation_coverage_matrix references unknown "
                f"governed_targets: {joined}"
            )

        unknown_a11y_governed_targets = _find_unknown_references(
            [
                target
                for entry in self.a11y_foundation_coverage_matrix
                for target in entry.governed_targets
            ],
            known_visual_a11y_targets,
        )
        if unknown_a11y_governed_targets:
            joined = ", ".join(unknown_a11y_governed_targets)
            raise ValueError(
                "a11y_foundation_coverage_matrix references unknown "
                f"governed_targets: {joined}"
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

        unknown_visual_truth_refs = _find_unknown_references(
            [
                truth_ref
                for entry in self.visual_foundation_coverage_matrix
                for truth_ref in entry.source_truth_refs
            ],
            ALLOWED_GATE_POLICY_TRUTH_REFS,
        )
        if unknown_visual_truth_refs:
            joined = ", ".join(unknown_visual_truth_refs)
            raise ValueError(
                "visual_foundation_coverage_matrix references unknown "
                f"source_truth_refs: {joined}"
            )

        unknown_a11y_truth_refs = _find_unknown_references(
            [
                truth_ref
                for entry in self.a11y_foundation_coverage_matrix
                for truth_ref in entry.source_truth_refs
            ],
            ALLOWED_GATE_POLICY_TRUTH_REFS,
        )
        if unknown_a11y_truth_refs:
            joined = ", ".join(unknown_a11y_truth_refs)
            raise ValueError(
                "a11y_foundation_coverage_matrix references unknown "
                f"source_truth_refs: {joined}"
            )

        unknown_visual_evidence_truth_refs = _find_unknown_references(
            [
                truth_ref
                for entry in self.visual_a11y_evidence_boundary
                for truth_ref in entry.source_truth_refs
            ],
            ALLOWED_GATE_POLICY_TRUTH_REFS,
        )
        if unknown_visual_evidence_truth_refs:
            joined = ", ".join(unknown_visual_evidence_truth_refs)
            raise ValueError(
                "visual_a11y_evidence_boundary references unknown "
                f"source_truth_refs: {joined}"
            )

        unknown_visual_feedback_truth_refs = _find_unknown_references(
            [
                truth_ref
                for entry in self.visual_a11y_feedback_boundary
                for truth_ref in entry.source_truth_refs
            ],
            ALLOWED_GATE_POLICY_TRUTH_REFS,
        )
        if unknown_visual_feedback_truth_refs:
            joined = ", ".join(unknown_visual_feedback_truth_refs)
            raise ValueError(
                "visual_a11y_feedback_boundary references unknown "
                f"source_truth_refs: {joined}"
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

        unknown_visual_feedback_report_types = _find_unknown_references(
            [
                report_type
                for entry in self.visual_a11y_feedback_boundary
                for report_type in entry.report_types
            ],
            set(self.report_types),
        )
        if unknown_visual_feedback_report_types:
            joined = ", ".join(unknown_visual_feedback_report_types)
            raise ValueError(
                "visual_a11y_feedback_boundary references unknown report_types: "
                f"{joined}"
            )

        return self


def _known_p1_visual_a11y_targets() -> set[str]:
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()
    known_targets = {
        component.component_id for component in kernel.semantic_components
    }
    known_targets.update(recipe.recipe_id for recipe in kernel.page_recipes)
    known_targets.update(kernel.state_baseline.required_states)
    known_targets.update(
        area
        for recipe in kernel.page_recipes
        for area in [*recipe.required_areas, *recipe.optional_areas]
    )
    return known_targets


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


def build_p1_frontend_gate_policy_visual_a11y_foundation() -> FrontendGatePolicySet:
    """Build the P1 visual/a11y foundation truth on top of the 069 gate policy."""

    base_policy = build_p1_frontend_gate_policy_diagnostics_drift_expansion()

    return FrontendGatePolicySet(
        work_item_id="071",
        execution_priority=base_policy.execution_priority,
        gate_matrix=base_policy.gate_matrix,
        compatibility_policies=base_policy.compatibility_policies,
        report_types=base_policy.report_types,
        diagnostics_coverage_matrix=base_policy.diagnostics_coverage_matrix,
        drift_classification=base_policy.drift_classification,
        compatibility_feedback_boundary=base_policy.compatibility_feedback_boundary,
        visual_foundation_coverage_matrix=[
            FrontendVisualFoundationCoverageEntry(
                coverage_id="state-visual-presence",
                quality_surface="state-visual-presence",
                governed_targets=[
                    "refreshing",
                    "submitting",
                    "no-results",
                    "partial-error",
                    "success-feedback",
                ],
                source_truth_refs=["015", "067", "069", "071"],
                expectation="P1 extended states stay visually perceivable without erasing prior content context",
                boundary="covers only bounded state presence and does not introduce visual regression tooling",
            ),
            FrontendVisualFoundationCoverageEntry(
                coverage_id="required-area-visual-presence",
                quality_surface="required-area-visual-presence",
                governed_targets=[
                    "Main Insight Area",
                    "State / Validation Area",
                    "Result Summary Area",
                    "Step Progress Area",
                ],
                source_truth_refs=["068", "069", "071"],
                expectation="required P1 recipe areas remain explicitly present and visually distinguishable",
                boundary="reuses recipe area truth without redefining layout systems",
            ),
            FrontendVisualFoundationCoverageEntry(
                coverage_id="controlled-container-visual-continuity",
                quality_surface="controlled-container-visual-continuity",
                governed_targets=[
                    "UiDialog",
                    "UiDrawer",
                    "UiSection",
                    "UiCard",
                    "UiResult",
                ],
                source_truth_refs=["067", "068", "069", "071"],
                expectation="controlled containers preserve continuity cues across transitions and partial failures",
                boundary="stays within shared Ui* container semantics and does not add runtime probes",
            ),
        ],
        a11y_foundation_coverage_matrix=[
            FrontendA11yFoundationCoverageEntry(
                coverage_id="error-status-perceivability",
                quality_surface="error-status-perceivability",
                governed_targets=[
                    "error",
                    "partial-error",
                    "success-feedback",
                    "no-results",
                ],
                source_truth_refs=["015", "067", "069", "071"],
                expectation="critical feedback and result states remain perceivable without relying on one visual cue",
                boundary="extends minimum perceivability truth without adding browser automation",
            ),
            FrontendA11yFoundationCoverageEntry(
                coverage_id="accessible-naming-semantics",
                quality_surface="accessible-naming-semantics",
                governed_targets=[
                    "UiInput",
                    "UiFormItem",
                    "UiTabs",
                    "UiSearchBar",
                    "UiFilterBar",
                    "UiToolbar",
                    "UiPagination",
                    "UiResult",
                ],
                source_truth_refs=["015", "067", "069", "071"],
                expectation="interactive and result-bearing protocols keep explicit naming and semantic affordances",
                boundary="reuses shared component semantics without creating a separate accessibility contract family",
            ),
            FrontendA11yFoundationCoverageEntry(
                coverage_id="keyboard-reachability",
                quality_surface="keyboard-reachability",
                governed_targets=[
                    "UiButton",
                    "UiInput",
                    "UiSelect",
                    "UiTabs",
                    "UiSearchBar",
                    "UiFilterBar",
                    "UiPagination",
                    "UiDialog",
                    "UiDrawer",
                ],
                source_truth_refs=["015", "067", "071"],
                expectation="key interactive surfaces remain reachable in standard keyboard flows",
                boundary="captures minimum reachability expectations without adding runtime tab-order assertions",
            ),
            FrontendA11yFoundationCoverageEntry(
                coverage_id="focus-continuity",
                quality_surface="focus-continuity",
                governed_targets=[
                    "DialogFormPage",
                    "WizardPage",
                    "UiDialog",
                    "UiDrawer",
                    "UiTabs",
                ],
                source_truth_refs=["067", "068", "071"],
                expectation="focus handling remains continuous across overlays, step transitions, and segmented navigation",
                boundary="records continuity expectations only and does not define provider focus traps",
            ),
        ],
        visual_a11y_evidence_boundary=[
            FrontendVisualA11yEvidenceBoundary(
                boundary_id="explicit-evidence-only",
                allowed_evidence_sources=["explicit-input-artifact"],
                forbidden_implicit_sources=[
                    "workspace-root-discovery",
                    "ambient-screenshot-scan",
                    "runtime-dom-assumption",
                ],
                source_truth_refs=["069", "071"],
                description="visual and a11y feedback can only consume explicit artifacts handed into verification",
            )
        ],
        visual_a11y_feedback_boundary=[
            FrontendVisualA11yFeedbackBoundary(
                boundary_id="shared-report-family-reuse",
                allowed_feedback_surfaces=[
                    "report-severity",
                    "location-anchor",
                    "quality-hint",
                    "changed-scope-explanation",
                ],
                report_types=base_policy.report_types,
                forbidden_expansions=[
                    "second-visual-gate-system",
                    "runtime-browser-verifier",
                ],
                source_truth_refs=["018", "069", "070", "071"],
                description="visual and a11y findings reuse the shared report family instead of inventing a parallel gate output",
            )
        ],
    )


__all__ = [
    "CompatibilityExecutionPolicy",
    "FrontendCompatibilityFeedbackBoundary",
    "FrontendA11yFoundationCoverageEntry",
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
    "FrontendVisualA11yEvidenceBoundary",
    "FrontendVisualA11yFeedbackBoundary",
    "FrontendVisualFoundationCoverageEntry",
    "build_mvp_frontend_gate_policy",
    "build_p1_frontend_gate_policy_diagnostics_drift_expansion",
    "build_p1_frontend_gate_policy_visual_a11y_foundation",
]
