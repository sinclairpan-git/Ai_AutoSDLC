"""Frontend gate matrix, compatibility policy, and report models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


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


__all__ = [
    "CompatibilityExecutionPolicy",
    "FrontendCoverageGap",
    "FrontendCoverageReport",
    "FrontendDriftFinding",
    "FrontendDriftReport",
    "FrontendGatePolicySet",
    "FrontendGateRule",
    "FrontendLegacyExpansionFinding",
    "FrontendLegacyExpansionReport",
    "FrontendViolation",
    "FrontendViolationReport",
    "build_mvp_frontend_gate_policy",
]
