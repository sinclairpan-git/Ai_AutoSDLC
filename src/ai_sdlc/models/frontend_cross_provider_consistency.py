"""Frontend cross-provider consistency baseline models for work item 150."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_page_ui_schema import (
    FrontendPageUiSchemaSet,
    UiSchemaDefinition,
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    FrontendQualityPlatformSet,
    QualityVerdictEnvelope,
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    InstallStrategy,
    build_builtin_install_strategies,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceSet,
    build_p2_frontend_theme_token_governance_baseline,
)

FinalVerdict = Literal["consistent", "drifted"]
ComparabilityState = Literal["comparable", "coverage-gap", "not-comparable"]
BlockingState = Literal["ready", "upstream-blocked"]
EvidenceState = Literal["fresh", "advisory", "needs-recheck"]
CertificationGateState = Literal["ready", "conditional", "blocked"]
DiffSeverity = Literal["info", "low", "medium", "high"]
TruthLayer = Literal["runtime-truth", "release-gate-input"]
UxClauseKind = Literal[
    "task-outcome",
    "information-architecture",
    "interaction-feedback",
    "provider-native-advisory",
]
GapKind = Literal["coverage-gap", "not-comparable"]

_ARTIFACT_ROOT = "governance/frontend/cross-provider-consistency"
_CANONICAL_FILES = [
    "consistency.manifest.yaml",
    "handoff.schema.yaml",
    "truth-surfacing.yaml",
    "readiness-gate.yaml",
]
_REQUIRED_PROGRAM_SERVICE_FIELDS = {
    "pair_id",
    "baseline_provider_id",
    "candidate_provider_id",
    "final_verdict",
    "comparability_state",
    "blocking_state",
    "evidence_state",
    "certification_gate",
}
_REQUIRED_CLI_FIELDS = {
    "pair_id",
    "final_verdict",
    "comparability_state",
    "certification_gate",
}
_REQUIRED_VERIFY_FIELDS = {
    "pair_id",
    "page_schema_id",
    "baseline_provider_id",
    "candidate_provider_id",
    "final_verdict",
    "comparability_state",
    "blocking_state",
    "evidence_state",
    "certification_gate",
    "diff_refs",
}


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _derive_gate_from_state_vector(
    state_vector: ConsistencyStateVector,
) -> CertificationGateState:
    if (
        state_vector.final_verdict == "drifted"
        or state_vector.blocking_state == "upstream-blocked"
        or state_vector.evidence_state == "needs-recheck"
        or state_vector.comparability_state == "not-comparable"
    ):
        return "blocked"
    if (
        state_vector.comparability_state == "coverage-gap"
        or state_vector.evidence_state == "advisory"
    ):
        return "conditional"
    return "ready"


class FrontendCrossProviderConsistencyModel(BaseModel):
    """Base model for structured cross-provider consistency artifacts."""

    model_config = ConfigDict(extra="forbid")


class ConsistencyStateVector(FrontendCrossProviderConsistencyModel):
    """Explicit four-axis consistency state contract for Track D."""

    final_verdict: FinalVerdict
    comparability_state: ComparabilityState
    blocking_state: BlockingState
    evidence_state: EvidenceState


class UxEquivalenceClause(FrontendCrossProviderConsistencyModel):
    """One explicit UX equivalence rule carried by Track D."""

    clause_id: str
    clause_kind: UxClauseKind
    description: str
    required_journey_ids: list[str] = Field(default_factory=list)
    required_schema_slot_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_clause(self) -> UxEquivalenceClause:
        if not self.description.strip():
            raise ValueError("description must not be empty")
        return self


class ConsistencyDiffRecord(FrontendCrossProviderConsistencyModel):
    """Structured pair-level diff record, not a screenshot list."""

    diff_id: str
    pair_id: str
    journey_id: str
    page_schema_id: str
    schema_slot_id: str | None = None
    theme_token_id: str | None = None
    quality_dimension: str
    severity: DiffSeverity
    summary: str
    evidence_refs: list[str] = Field(default_factory=list)
    remediation_hint: str | None = None

    @model_validator(mode="after")
    def _validate_diff(self) -> ConsistencyDiffRecord:
        if not self.summary.strip():
            raise ValueError("summary must not be empty")
        if not self.evidence_refs:
            raise ValueError("evidence_refs must not be empty")
        if any(not ref.startswith("artifact:") for ref in self.evidence_refs):
            raise ValueError("evidence_refs must use artifact: references")
        return self


class CoverageGapRecord(FrontendCrossProviderConsistencyModel):
    """Explicit coverage-gap / not-comparable payload."""

    gap_id: str
    pair_id: str
    gap_kind: GapKind
    journey_id: str
    page_schema_id: str
    schema_slot_ids: list[str] = Field(default_factory=list)
    quality_dimension: str | None = None
    detail: str
    upstream_truth_refs: list[str] = Field(default_factory=list)
    remediation_hint: str | None = None

    @model_validator(mode="after")
    def _validate_gap(self) -> CoverageGapRecord:
        if not self.detail.strip():
            raise ValueError("detail must not be empty")
        if not self.upstream_truth_refs:
            raise ValueError("upstream_truth_refs must not be empty")
        return self


class ProviderPairCertificationBundle(FrontendCrossProviderConsistencyModel):
    """Pair-centric certification bundle consumed by Track E later on."""

    pair_id: str
    baseline_provider_id: str
    candidate_provider_id: str
    page_schema_id: str
    compared_style_pack_id: str
    required_journey_ids: list[str] = Field(default_factory=list)
    state_vector: ConsistencyStateVector
    diff_record_ids: list[str] = Field(default_factory=list)
    coverage_gap_ids: list[str] = Field(default_factory=list)
    certification_gate: CertificationGateState | None = None

    @model_validator(mode="after")
    def _validate_and_derive_gate(self) -> ProviderPairCertificationBundle:
        if not self.required_journey_ids:
            raise ValueError("required_journey_ids must not be empty")
        derived_gate = _derive_gate_from_state_vector(self.state_vector)
        if self.certification_gate and self.certification_gate != derived_gate:
            raise ValueError("certification_gate must match state_vector")
        self.certification_gate = derived_gate
        return self


class ProviderPairTruthSurfacingRecord(FrontendCrossProviderConsistencyModel):
    """Stable truth surface payload for program truth and Track E."""

    pair_id: str
    truth_layer: TruthLayer
    final_verdict: FinalVerdict
    comparability_state: ComparabilityState
    blocking_state: BlockingState
    evidence_state: EvidenceState
    certification_gate: CertificationGateState
    artifact_root_ref: str
    certification_ref: str

    @model_validator(mode="after")
    def _validate_truth_surface(self) -> ProviderPairTruthSurfacingRecord:
        if not self.artifact_root_ref.startswith(_ARTIFACT_ROOT):
            raise ValueError("artifact_root_ref must stay inside governance/frontend/cross-provider-consistency")
        if not self.certification_ref.startswith("artifact:"):
            raise ValueError("certification_ref must use artifact: references")
        return self


class ReadinessGateRule(FrontendCrossProviderConsistencyModel):
    """One explicit readiness-gate rule."""

    gate_state: CertificationGateState
    allowed_final_verdicts: list[FinalVerdict] = Field(default_factory=list)
    allowed_comparability_states: list[ComparabilityState] = Field(default_factory=list)
    allowed_blocking_states: list[BlockingState] = Field(default_factory=list)
    allowed_evidence_states: list[EvidenceState] = Field(default_factory=list)
    description: str

    @model_validator(mode="after")
    def _validate_rule(self) -> ReadinessGateRule:
        if not self.allowed_final_verdicts:
            raise ValueError("allowed_final_verdicts must not be empty")
        if not self.allowed_comparability_states:
            raise ValueError("allowed_comparability_states must not be empty")
        if not self.allowed_blocking_states:
            raise ValueError("allowed_blocking_states must not be empty")
        if not self.allowed_evidence_states:
            raise ValueError("allowed_evidence_states must not be empty")
        if not self.description.strip():
            raise ValueError("description must not be empty")
        return self


def _default_readiness_gate_rules() -> list[ReadinessGateRule]:
    return [
        ReadinessGateRule(
            gate_state="ready",
            allowed_final_verdicts=["consistent"],
            allowed_comparability_states=["comparable"],
            allowed_blocking_states=["ready"],
            allowed_evidence_states=["fresh"],
            description="Required journeys, slots, and quality dimensions are fully comparable with fresh evidence.",
        ),
        ReadinessGateRule(
            gate_state="conditional",
            allowed_final_verdicts=["consistent"],
            allowed_comparability_states=["comparable", "coverage-gap"],
            allowed_blocking_states=["ready"],
            allowed_evidence_states=["fresh", "advisory"],
            description="Consistency holds, but limited coverage gaps or advisory-only evidence remain.",
        ),
        ReadinessGateRule(
            gate_state="blocked",
            allowed_final_verdicts=["consistent", "drifted"],
            allowed_comparability_states=["comparable", "coverage-gap", "not-comparable"],
            allowed_blocking_states=["ready", "upstream-blocked"],
            allowed_evidence_states=["fresh", "advisory", "needs-recheck"],
            description="Any drift, upstream block, not-comparable scope, or recheck requirement blocks Track E admission.",
        ),
    ]


class ConsistencyReadinessGate(FrontendCrossProviderConsistencyModel):
    """Gate matrix carried by Track D artifacts."""

    gate_id: str = "track-e-readiness"
    rules: list[ReadinessGateRule] = Field(default_factory=_default_readiness_gate_rules)
    required_coverage_scope: list[str] = Field(
        default_factory=lambda: [
            "required-journeys",
            "required-schema-slots",
            "required-quality-dimensions",
        ]
    )
    optional_coverage_scope: list[str] = Field(
        default_factory=lambda: [
            "provider-native-visual-advisories",
            "non-blocking-theme-token-polish",
        ]
    )
    ux_equivalence_clause_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_gate(self) -> ConsistencyReadinessGate:
        duplicate_gate_states = _find_duplicates([rule.gate_state for rule in self.rules])
        if duplicate_gate_states:
            joined = ", ".join(duplicate_gate_states)
            raise ValueError(f"duplicate readiness gate states: {joined}")
        known_gate_states = {rule.gate_state for rule in self.rules}
        if known_gate_states != {"ready", "conditional", "blocked"}:
            raise ValueError("readiness gate must define ready/conditional/blocked rules")
        return self


class ConsistencyHandoffContract(FrontendCrossProviderConsistencyModel):
    """Versioned handoff schema and minimum consumer field contract."""

    schema_family: str
    current_version: str
    compatible_versions: list[str] = Field(default_factory=list)
    artifact_root: str
    canonical_files: list[str] = Field(default_factory=list)
    program_service_fields: list[str] = Field(default_factory=list)
    cli_fields: list[str] = Field(default_factory=list)
    verify_fields: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_contract(self) -> ConsistencyHandoffContract:
        if self.current_version not in self.compatible_versions:
            raise ValueError("current_version must be included in compatible_versions")
        if not self.canonical_files:
            raise ValueError("canonical_files must not be empty")
        if not _REQUIRED_PROGRAM_SERVICE_FIELDS.issubset(self.program_service_fields):
            raise ValueError("program_service_fields missing required fields")
        if not _REQUIRED_CLI_FIELDS.issubset(self.cli_fields):
            raise ValueError("cli_fields missing required fields")
        if not _REQUIRED_VERIFY_FIELDS.issubset(self.verify_fields):
            raise ValueError("verify_fields missing required fields")
        return self


class FrontendCrossProviderConsistencySet(FrontendCrossProviderConsistencyModel):
    """Top-level pair-centric Track D baseline."""

    work_item_id: str
    source_work_item_ids: list[str] = Field(default_factory=list)
    ux_equivalence_clauses: list[UxEquivalenceClause] = Field(default_factory=list)
    diff_records: list[ConsistencyDiffRecord] = Field(default_factory=list)
    coverage_gaps: list[CoverageGapRecord] = Field(default_factory=list)
    certification_bundles: list[ProviderPairCertificationBundle] = Field(default_factory=list)
    truth_surfacing_records: list[ProviderPairTruthSurfacingRecord] = Field(
        default_factory=list
    )
    readiness_gate: ConsistencyReadinessGate
    handoff_contract: ConsistencyHandoffContract

    @model_validator(mode="after")
    def _validate_set(self) -> FrontendCrossProviderConsistencySet:
        duplicate_clause_ids = _find_duplicates(
            [clause.clause_id for clause in self.ux_equivalence_clauses]
        )
        if duplicate_clause_ids:
            joined = ", ".join(duplicate_clause_ids)
            raise ValueError(f"duplicate clause ids: {joined}")

        duplicate_diff_ids = _find_duplicates([record.diff_id for record in self.diff_records])
        if duplicate_diff_ids:
            joined = ", ".join(duplicate_diff_ids)
            raise ValueError(f"duplicate diff record ids: {joined}")

        duplicate_gap_ids = _find_duplicates([gap.gap_id for gap in self.coverage_gaps])
        if duplicate_gap_ids:
            joined = ", ".join(duplicate_gap_ids)
            raise ValueError(f"duplicate coverage gap ids: {joined}")

        duplicate_pair_ids = _find_duplicates(
            [bundle.pair_id for bundle in self.certification_bundles]
        )
        if duplicate_pair_ids:
            joined = ", ".join(duplicate_pair_ids)
            raise ValueError(f"duplicate pair ids: {joined}")

        known_diff_ids = {record.diff_id for record in self.diff_records}
        unknown_diff_ids = sorted(
            {
                diff_id
                for bundle in self.certification_bundles
                for diff_id in bundle.diff_record_ids
                if diff_id not in known_diff_ids
            }
        )
        if unknown_diff_ids:
            joined = ", ".join(unknown_diff_ids)
            raise ValueError(f"unknown diff record ids: {joined}")

        known_gap_ids = {gap.gap_id for gap in self.coverage_gaps}
        unknown_gap_ids = sorted(
            {
                gap_id
                for bundle in self.certification_bundles
                for gap_id in bundle.coverage_gap_ids
                if gap_id not in known_gap_ids
            }
        )
        if unknown_gap_ids:
            joined = ", ".join(unknown_gap_ids)
            raise ValueError(f"unknown coverage gap ids: {joined}")

        clause_ids = {clause.clause_id for clause in self.ux_equivalence_clauses}
        unknown_gate_clause_ids = [
            clause_id
            for clause_id in self.readiness_gate.ux_equivalence_clause_ids
            if clause_id not in clause_ids
        ]
        if unknown_gate_clause_ids:
            joined = ", ".join(sorted(set(unknown_gate_clause_ids)))
            raise ValueError(f"readiness gate references unknown ux clause ids: {joined}")

        known_pair_ids = {bundle.pair_id for bundle in self.certification_bundles}
        unknown_truth_pair_ids = [
            record.pair_id
            for record in self.truth_surfacing_records
            if record.pair_id not in known_pair_ids
        ]
        if unknown_truth_pair_ids:
            joined = ", ".join(sorted(set(unknown_truth_pair_ids)))
            raise ValueError(f"truth surfacing references unknown pair ids: {joined}")

        return self


def _select_ui_schema(
    page_ui_schema: FrontendPageUiSchemaSet,
    page_schema_id: str,
) -> UiSchemaDefinition:
    for ui_schema in page_ui_schema.ui_schemas:
        if ui_schema.page_schema_id == page_schema_id:
            return ui_schema
    raise ValueError(f"missing required ui schema for 150 baseline: {page_schema_id}")


def _require_slot_id(ui_schema: UiSchemaDefinition, slot_id: str) -> str:
    for slot in ui_schema.render_slots:
        if slot.slot_id == slot_id:
            return slot_id
    raise ValueError(
        f"missing required render slot for 150 baseline: {ui_schema.page_schema_id}/{slot_id}"
    )


def _select_style_pack(
    theme_governance: FrontendThemeTokenGovernanceSet,
    style_pack_id: str,
) -> str:
    if style_pack_id not in theme_governance.style_pack_ids:
        raise ValueError(f"missing required style pack for 150 baseline: {style_pack_id}")
    return style_pack_id


def _release_eligible_provider_ids(
    install_strategies: list[InstallStrategy],
) -> list[str]:
    provider_ids = sorted({strategy.provider_id for strategy in install_strategies})
    if len(provider_ids) < 2:
        raise ValueError("150 baseline requires at least two release-eligible providers")
    return provider_ids[:2]


def _quality_verdict_by_id(
    quality_platform: FrontendQualityPlatformSet,
    verdict_id: str,
) -> QualityVerdictEnvelope:
    for verdict in quality_platform.verdict_envelopes:
        if verdict.verdict_id == verdict_id:
            return verdict
    raise ValueError(f"missing required quality verdict for 150 baseline: {verdict_id}")


def build_p2_frontend_cross_provider_consistency_baseline(
    *,
    page_ui_schema: FrontendPageUiSchemaSet | None = None,
    theme_governance: FrontendThemeTokenGovernanceSet | None = None,
    quality_platform: FrontendQualityPlatformSet | None = None,
) -> FrontendCrossProviderConsistencySet:
    """Build the Track D pair-centric consistency baseline defined by work item 150."""

    effective_page_ui_schema = page_ui_schema or build_p2_frontend_page_ui_schema_baseline()
    effective_theme_governance = (
        theme_governance or build_p2_frontend_theme_token_governance_baseline()
    )
    effective_quality_platform = (
        quality_platform or build_p2_frontend_quality_platform_baseline()
    )
    baseline_provider_id, candidate_provider_id = _release_eligible_provider_ids(
        build_builtin_install_strategies()
    )

    search_ui_schema = _select_ui_schema(effective_page_ui_schema, "search-list-workspace")
    dashboard_ui_schema = _select_ui_schema(
        effective_page_ui_schema,
        "dashboard-workspace",
    )
    wizard_ui_schema = _select_ui_schema(effective_page_ui_schema, "wizard-workspace")
    search_result_summary = _require_slot_id(search_ui_schema, "result-summary")
    dashboard_main_insight = _require_slot_id(dashboard_ui_schema, "main-insight")
    wizard_step_content = _require_slot_id(wizard_ui_schema, "step-content")
    enterprise_default = _select_style_pack(
        effective_theme_governance,
        "enterprise-default",
    )
    modern_saas = _select_style_pack(effective_theme_governance, "modern-saas")
    high_clarity = _select_style_pack(effective_theme_governance, "high-clarity")

    search_interaction = _quality_verdict_by_id(
        effective_quality_platform,
        "search-interaction-pass",
    )
    dashboard_a11y = _quality_verdict_by_id(
        effective_quality_platform,
        "dashboard-a11y-advisory",
    )
    dashboard_visual = _quality_verdict_by_id(
        effective_quality_platform,
        "dashboard-visual-pass",
    )

    search_pair_id = f"{baseline_provider_id}__{candidate_provider_id}__search-list-workspace"
    dashboard_pair_id = f"{baseline_provider_id}__{candidate_provider_id}__dashboard-workspace"
    wizard_pair_id = f"{baseline_provider_id}__{candidate_provider_id}__wizard-workspace"

    ux_equivalence_clauses = [
        UxEquivalenceClause(
            clause_id="required-task-outcome",
            clause_kind="task-outcome",
            description="Required journeys must end with the same user-visible task outcome across providers.",
            required_journey_ids=[
                "search-filter-flow",
                "dashboard-review-flow",
                "wizard-submit-flow",
            ],
        ),
        UxEquivalenceClause(
            clause_id="required-information-architecture",
            clause_kind="information-architecture",
            description="Required schema slots and structural anchors must remain present and non-drifting.",
            required_schema_slot_ids=[
                search_result_summary,
                dashboard_main_insight,
                wizard_step_content,
            ],
        ),
        UxEquivalenceClause(
            clause_id="required-interaction-feedback",
            clause_kind="interaction-feedback",
            description="Critical feedback timing, focus continuity, and state transitions must stay aligned.",
            required_journey_ids=[
                "search-filter-flow",
                "dashboard-review-flow",
            ],
        ),
        UxEquivalenceClause(
            clause_id="allowed-provider-native-advisory",
            clause_kind="provider-native-advisory",
            description="Non-blocking provider-native visual polish may differ when task outcome, structure, and feedback remain intact.",
        ),
    ]

    diff_records = [
        ConsistencyDiffRecord(
            diff_id="search-enterprise-vs-public",
            pair_id=search_pair_id,
            journey_id="search-filter-flow",
            page_schema_id="search-list-workspace",
            schema_slot_id=search_result_summary,
            theme_token_id="accent_mode",
            quality_dimension="interaction-quality",
            severity="info",
            summary="Search result summary timing stays aligned across both providers.",
            evidence_refs=list(search_interaction.evidence_refs),
            remediation_hint="Preserve existing result summary timing contract.",
        ),
        ConsistencyDiffRecord(
            diff_id="dashboard-enterprise-vs-public",
            pair_id=dashboard_pair_id,
            journey_id="dashboard-review-flow",
            page_schema_id="dashboard-workspace",
            schema_slot_id=dashboard_main_insight,
            theme_token_id="surface_mode",
            quality_dimension="complete-a11y",
            severity="medium",
            summary="Dashboard insight panel keeps the same task outcome, but mobile semantics still require advisory review.",
            evidence_refs=[dashboard_a11y.evidence_refs[0], dashboard_visual.evidence_refs[0]],
            remediation_hint="Tighten mobile semantics and preserve insight-panel structure parity.",
        ),
    ]

    coverage_gaps = [
        CoverageGapRecord(
            gap_id="dashboard-mobile-gap",
            pair_id=dashboard_pair_id,
            gap_kind="coverage-gap",
            journey_id="dashboard-review-flow",
            page_schema_id="dashboard-workspace",
            schema_slot_ids=[dashboard_main_insight],
            quality_dimension="complete-a11y",
            detail="Dashboard mobile parity remains advisory because required mobile semantics are only partially evidenced.",
            upstream_truth_refs=[dashboard_a11y.evidence_refs[0]],
            remediation_hint="Backfill mobile a11y evidence for the dashboard insight panel.",
        ),
        CoverageGapRecord(
            gap_id="wizard-upstream-blocked",
            pair_id=wizard_pair_id,
            gap_kind="not-comparable",
            journey_id="wizard-submit-flow",
            page_schema_id="wizard-workspace",
            schema_slot_ids=[wizard_step_content],
            quality_dimension="interaction-quality",
            detail="Wizard pair remains upstream-blocked because Track C quality evidence does not yet cover wizard-required journeys.",
            upstream_truth_refs=[
                "specs/149-frontend-p2-quality-platform-baseline/spec.md",
                "specs/147-frontend-p2-page-ui-schema-baseline/spec.md",
            ],
            remediation_hint="Materialize wizard quality-platform coverage before attempting pair certification.",
        ),
    ]

    certification_bundles = [
        ProviderPairCertificationBundle(
            pair_id=search_pair_id,
            baseline_provider_id=baseline_provider_id,
            candidate_provider_id=candidate_provider_id,
            page_schema_id="search-list-workspace",
            compared_style_pack_id=enterprise_default,
            required_journey_ids=["search-filter-flow"],
            state_vector=ConsistencyStateVector(
                final_verdict="consistent",
                comparability_state="comparable",
                blocking_state="ready",
                evidence_state="fresh",
            ),
            diff_record_ids=["search-enterprise-vs-public"],
            coverage_gap_ids=[],
        ),
        ProviderPairCertificationBundle(
            pair_id=dashboard_pair_id,
            baseline_provider_id=baseline_provider_id,
            candidate_provider_id=candidate_provider_id,
            page_schema_id="dashboard-workspace",
            compared_style_pack_id=modern_saas,
            required_journey_ids=["dashboard-review-flow"],
            state_vector=ConsistencyStateVector(
                final_verdict="consistent",
                comparability_state="coverage-gap",
                blocking_state="ready",
                evidence_state="advisory",
            ),
            diff_record_ids=["dashboard-enterprise-vs-public"],
            coverage_gap_ids=["dashboard-mobile-gap"],
        ),
        ProviderPairCertificationBundle(
            pair_id=wizard_pair_id,
            baseline_provider_id=baseline_provider_id,
            candidate_provider_id=candidate_provider_id,
            page_schema_id="wizard-workspace",
            compared_style_pack_id=high_clarity,
            required_journey_ids=["wizard-submit-flow"],
            state_vector=ConsistencyStateVector(
                final_verdict="consistent",
                comparability_state="not-comparable",
                blocking_state="upstream-blocked",
                evidence_state="needs-recheck",
            ),
            diff_record_ids=[],
            coverage_gap_ids=["wizard-upstream-blocked"],
        ),
    ]

    truth_surfacing_records: list[ProviderPairTruthSurfacingRecord] = []
    for bundle in certification_bundles:
        certification_ref = (
            "artifact:"
            f"{_ARTIFACT_ROOT}/provider-pairs/{bundle.pair_id}/certification.yaml"
        )
        for truth_layer in ("runtime-truth", "release-gate-input"):
            truth_surfacing_records.append(
                ProviderPairTruthSurfacingRecord(
                    pair_id=bundle.pair_id,
                    truth_layer=truth_layer,
                    final_verdict=bundle.state_vector.final_verdict,
                    comparability_state=bundle.state_vector.comparability_state,
                    blocking_state=bundle.state_vector.blocking_state,
                    evidence_state=bundle.state_vector.evidence_state,
                    certification_gate=bundle.certification_gate,
                    artifact_root_ref=_ARTIFACT_ROOT,
                    certification_ref=certification_ref,
                )
            )

    return FrontendCrossProviderConsistencySet(
        work_item_id="150",
        source_work_item_ids=["073", "147", "148", "149"],
        ux_equivalence_clauses=ux_equivalence_clauses,
        diff_records=diff_records,
        coverage_gaps=coverage_gaps,
        certification_bundles=certification_bundles,
        truth_surfacing_records=truth_surfacing_records,
        readiness_gate=ConsistencyReadinessGate(
            ux_equivalence_clause_ids=[clause.clause_id for clause in ux_equivalence_clauses]
        ),
        handoff_contract=ConsistencyHandoffContract(
            schema_family="frontend-cross-provider-consistency",
            current_version="1.0",
            compatible_versions=["1.0"],
            artifact_root=_ARTIFACT_ROOT,
            canonical_files=list(_CANONICAL_FILES),
            program_service_fields=sorted(_REQUIRED_PROGRAM_SERVICE_FIELDS),
            cli_fields=sorted(_REQUIRED_CLI_FIELDS),
            verify_fields=sorted(_REQUIRED_VERIFY_FIELDS),
        ),
    )


__all__ = [
    "BlockingState",
    "CertificationGateState",
    "ComparabilityState",
    "ConsistencyDiffRecord",
    "ConsistencyHandoffContract",
    "ConsistencyReadinessGate",
    "ConsistencyStateVector",
    "CoverageGapRecord",
    "DiffSeverity",
    "EvidenceState",
    "FinalVerdict",
    "FrontendCrossProviderConsistencySet",
    "ProviderPairCertificationBundle",
    "ProviderPairTruthSurfacingRecord",
    "ReadinessGateRule",
    "TruthLayer",
    "UxClauseKind",
    "UxEquivalenceClause",
    "build_p2_frontend_cross_provider_consistency_baseline",
]
