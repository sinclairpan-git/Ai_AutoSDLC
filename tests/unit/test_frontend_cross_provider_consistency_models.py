"""Unit tests for frontend cross-provider consistency models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_cross_provider_consistency import (
    ConsistencyDiffRecord,
    ConsistencyHandoffContract,
    ConsistencyReadinessGate,
    ConsistencyStateVector,
    FrontendCrossProviderConsistencySet,
    ProviderPairCertificationBundle,
    ProviderPairTruthSurfacingRecord,
    UxEquivalenceClause,
    build_p2_frontend_cross_provider_consistency_baseline,
)


def _handoff() -> ConsistencyHandoffContract:
    return ConsistencyHandoffContract(
        schema_family="frontend-cross-provider-consistency",
        current_version="1.0",
        compatible_versions=["1.0"],
        artifact_root="governance/frontend/cross-provider-consistency",
        canonical_files=[
            "consistency.manifest.yaml",
            "handoff.schema.yaml",
            "truth-surfacing.yaml",
            "readiness-gate.yaml",
        ],
        program_service_fields=[
            "pair_id",
            "baseline_provider_id",
            "candidate_provider_id",
            "final_verdict",
            "comparability_state",
            "blocking_state",
            "evidence_state",
            "certification_gate",
        ],
        cli_fields=[
            "pair_id",
            "final_verdict",
            "comparability_state",
            "certification_gate",
        ],
        verify_fields=[
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
        ],
    )


def _ux_clause() -> UxEquivalenceClause:
    return UxEquivalenceClause(
        clause_id="required-task-outcome",
        clause_kind="task-outcome",
        description="Required task outcomes must stay equivalent across providers.",
        required_journey_ids=["search-filter-flow"],
    )


def _state_vector() -> ConsistencyStateVector:
    return ConsistencyStateVector(
        final_verdict="consistent",
        comparability_state="comparable",
        blocking_state="ready",
        evidence_state="fresh",
    )


def test_build_p2_frontend_cross_provider_consistency_baseline_materializes_pair_centric_truth() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()

    assert consistency.work_item_id == "150"
    assert consistency.source_work_item_ids == ["073", "147", "148", "149"]
    assert consistency.handoff_contract.artifact_root == (
        "governance/frontend/cross-provider-consistency"
    )
    assert [bundle.pair_id for bundle in consistency.certification_bundles] == [
        "enterprise-vue2__public-primevue__search-list-workspace",
        "enterprise-vue2__public-primevue__dashboard-workspace",
        "enterprise-vue2__public-primevue__wizard-workspace",
    ]
    assert {bundle.certification_gate for bundle in consistency.certification_bundles} == {
        "ready",
        "conditional",
        "blocked",
    }
    assert {record.truth_layer for record in consistency.truth_surfacing_records} == {
        "runtime-truth",
        "release-gate-input",
    }
    assert {clause.clause_kind for clause in consistency.ux_equivalence_clauses} == {
        "task-outcome",
        "information-architecture",
        "interaction-feedback",
        "provider-native-advisory",
    }


def test_provider_pair_certification_bundle_derives_gate_from_state_vector() -> None:
    ready_bundle = ProviderPairCertificationBundle(
        pair_id="enterprise-vue2__public-primevue__search-list-workspace",
        baseline_provider_id="enterprise-vue2",
        candidate_provider_id="public-primevue",
        page_schema_id="search-list-workspace",
        compared_style_pack_id="enterprise-default",
        required_journey_ids=["search-filter-flow"],
        state_vector=_state_vector(),
        diff_record_ids=["search-enterprise-vs-public"],
        coverage_gap_ids=[],
    )
    conditional_bundle = ProviderPairCertificationBundle(
        pair_id="enterprise-vue2__public-primevue__dashboard-workspace",
        baseline_provider_id="enterprise-vue2",
        candidate_provider_id="public-primevue",
        page_schema_id="dashboard-workspace",
        compared_style_pack_id="modern-saas",
        required_journey_ids=["dashboard-review-flow"],
        state_vector=ConsistencyStateVector(
            final_verdict="consistent",
            comparability_state="coverage-gap",
            blocking_state="ready",
            evidence_state="advisory",
        ),
        diff_record_ids=["dashboard-enterprise-vs-public"],
        coverage_gap_ids=["dashboard-mobile-gap"],
    )
    blocked_bundle = ProviderPairCertificationBundle(
        pair_id="enterprise-vue2__public-primevue__wizard-workspace",
        baseline_provider_id="enterprise-vue2",
        candidate_provider_id="public-primevue",
        page_schema_id="wizard-workspace",
        compared_style_pack_id="high-clarity",
        required_journey_ids=["wizard-submit-flow"],
        state_vector=ConsistencyStateVector(
            final_verdict="consistent",
            comparability_state="not-comparable",
            blocking_state="upstream-blocked",
            evidence_state="needs-recheck",
        ),
        diff_record_ids=[],
        coverage_gap_ids=["wizard-upstream-blocked"],
    )

    assert ready_bundle.certification_gate == "ready"
    assert conditional_bundle.certification_gate == "conditional"
    assert blocked_bundle.certification_gate == "blocked"


def test_consistency_diff_record_requires_artifact_evidence_refs() -> None:
    with pytest.raises(ValueError, match="evidence_refs must use artifact: references"):
        ConsistencyDiffRecord(
            diff_id="dashboard-enterprise-vs-public",
            pair_id="enterprise-vue2__public-primevue__dashboard-workspace",
            journey_id="dashboard-review-flow",
            page_schema_id="dashboard-workspace",
            schema_slot_id="main-insight",
            theme_token_id="surface_mode",
            quality_dimension="interaction-quality",
            severity="medium",
            summary="Provider-native loading treatment diverges on async insight panel.",
            evidence_refs=["tmp/dashboard.png"],
            remediation_hint="Normalize async feedback timing for insight panel.",
        )


def test_frontend_cross_provider_consistency_set_rejects_unknown_diff_refs() -> None:
    with pytest.raises(ValueError, match="unknown diff record ids"):
        FrontendCrossProviderConsistencySet(
            work_item_id="150",
            source_work_item_ids=["073", "147", "148", "149"],
            ux_equivalence_clauses=[_ux_clause()],
            diff_records=[],
            certification_bundles=[
                ProviderPairCertificationBundle(
                    pair_id="enterprise-vue2__public-primevue__search-list-workspace",
                    baseline_provider_id="enterprise-vue2",
                    candidate_provider_id="public-primevue",
                    page_schema_id="search-list-workspace",
                    compared_style_pack_id="enterprise-default",
                    required_journey_ids=["search-filter-flow"],
                    state_vector=_state_vector(),
                    diff_record_ids=["missing-diff"],
                    coverage_gap_ids=[],
                )
            ],
            truth_surfacing_records=[
                ProviderPairTruthSurfacingRecord(
                    pair_id="enterprise-vue2__public-primevue__search-list-workspace",
                    truth_layer="runtime-truth",
                    final_verdict="consistent",
                    comparability_state="comparable",
                    blocking_state="ready",
                    evidence_state="fresh",
                    certification_gate="ready",
                    artifact_root_ref="governance/frontend/cross-provider-consistency",
                    certification_ref=(
                        "artifact:governance/frontend/cross-provider-consistency/"
                        "provider-pairs/enterprise-vue2__public-primevue__search-list-workspace/"
                        "certification.yaml"
                    ),
                )
            ],
            readiness_gate=ConsistencyReadinessGate(),
            handoff_contract=_handoff(),
        )
