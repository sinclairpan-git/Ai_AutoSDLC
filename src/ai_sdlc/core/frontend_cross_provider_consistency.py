"""Validation helpers for frontend cross-provider consistency baseline."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_sdlc.models.frontend_cross_provider_consistency import (
    FrontendCrossProviderConsistencySet,
)
from ai_sdlc.models.frontend_page_ui_schema import FrontendPageUiSchemaSet
from ai_sdlc.models.frontend_quality_platform import FrontendQualityPlatformSet
from ai_sdlc.models.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceSet,
)


def _dedupe_text_items(items: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


@dataclass(frozen=True, slots=True)
class FrontendCrossProviderConsistencyValidationResult:
    """Structured validation result for Track D pair-centric consistency truth."""

    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact_root: str = ""
    pair_count: int = 0
    certification_gates: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "blockers", _dedupe_text_items(self.blockers))
        object.__setattr__(self, "warnings", _dedupe_text_items(self.warnings))


def validate_frontend_cross_provider_consistency(
    consistency: FrontendCrossProviderConsistencySet,
    *,
    page_ui_schema: FrontendPageUiSchemaSet,
    theme_governance: FrontendThemeTokenGovernanceSet,
    quality_platform: FrontendQualityPlatformSet,
) -> FrontendCrossProviderConsistencyValidationResult:
    """Validate Track D pair contracts against 147/148/149 upstream truth."""

    blockers: list[str] = []
    warnings: list[str] = []
    known_page_schema_ids = {
        page_schema.page_schema_id for page_schema in page_ui_schema.page_schemas
    }
    known_style_pack_ids = set(theme_governance.style_pack_ids)
    known_quality_evidence_refs = {
        ref
        for verdict in quality_platform.verdict_envelopes
        for ref in verdict.evidence_refs
    }
    truth_layers_by_pair: dict[str, set[str]] = {}
    diff_records_by_id = {record.diff_id: record for record in consistency.diff_records}
    gap_ids = {gap.gap_id for gap in consistency.coverage_gaps}

    for record in consistency.truth_surfacing_records:
        truth_layers_by_pair.setdefault(record.pair_id, set()).add(record.truth_layer)

    for bundle in consistency.certification_bundles:
        if bundle.page_schema_id not in known_page_schema_ids:
            blockers.append(
                f"unknown page schema in pair bundle: {bundle.page_schema_id}"
            )
        if bundle.compared_style_pack_id not in known_style_pack_ids:
            blockers.append(
                f"unknown style pack in pair bundle: {bundle.compared_style_pack_id}"
            )

        if bundle.state_vector.comparability_state == "coverage-gap" and not bundle.coverage_gap_ids:
            blockers.append(
                "coverage-gap pair bundle missing coverage_gap_ids: "
                f"{bundle.pair_id}"
            )
        if bundle.state_vector.comparability_state == "not-comparable" and not bundle.coverage_gap_ids:
            blockers.append(
                "not-comparable pair bundle missing coverage_gap_ids: "
                f"{bundle.pair_id}"
            )
        if bundle.state_vector.comparability_state == "comparable" and bundle.coverage_gap_ids:
            blockers.append(
                "comparable pair bundle must not carry coverage_gap_ids: "
                f"{bundle.pair_id}"
            )
        if bundle.state_vector.blocking_state == "upstream-blocked":
            warnings.append(f"upstream-blocked pair bundle: {bundle.pair_id}")

        for diff_id in bundle.diff_record_ids:
            diff_record = diff_records_by_id.get(diff_id)
            if diff_record is None:
                continue
            unknown_evidence_refs = [
                ref for ref in diff_record.evidence_refs if ref not in known_quality_evidence_refs
            ]
            if unknown_evidence_refs:
                joined = ", ".join(sorted(set(unknown_evidence_refs)))
                blockers.append(
                    f"diff record references unknown quality evidence: {joined}"
                )

        unknown_gap_refs = [gap_id for gap_id in bundle.coverage_gap_ids if gap_id not in gap_ids]
        if unknown_gap_refs:
            joined = ", ".join(sorted(set(unknown_gap_refs)))
            blockers.append(f"pair bundle references unknown coverage gaps: {joined}")

        pair_truth_layers = truth_layers_by_pair.get(bundle.pair_id, set())
        if pair_truth_layers != {"runtime-truth", "release-gate-input"}:
            blockers.append(
                f"truth surfacing missing required layers for pair: {bundle.pair_id}"
            )

    return FrontendCrossProviderConsistencyValidationResult(
        passed=not blockers,
        blockers=_dedupe_text_items(blockers),
        warnings=_dedupe_text_items(warnings),
        artifact_root=consistency.handoff_contract.artifact_root,
        pair_count=len(consistency.certification_bundles),
        certification_gates={
            bundle.pair_id: bundle.certification_gate
            for bundle in consistency.certification_bundles
        },
    )


__all__ = [
    "FrontendCrossProviderConsistencyValidationResult",
    "validate_frontend_cross_provider_consistency",
]
