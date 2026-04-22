"""Unit tests for frontend cross-provider consistency validation helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_cross_provider_consistency import (
    FrontendCrossProviderConsistencyValidationResult,
    validate_frontend_cross_provider_consistency,
)
from ai_sdlc.models.frontend_cross_provider_consistency import (
    ConsistencyDiffRecord,
    ConsistencyHandoffContract,
    ConsistencyReadinessGate,
    ConsistencyStateVector,
    CoverageGapRecord,
    FrontendCrossProviderConsistencySet,
    ProviderPairCertificationBundle,
    ReadinessGateRule,
    UxEquivalenceClause,
    build_p2_frontend_cross_provider_consistency_baseline,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)


def test_validate_frontend_cross_provider_consistency_passes_for_builtin_baseline() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.pair_count == 3
    assert result.certification_gates == {
        "enterprise-vue2__public-primevue__search-list-workspace": "ready",
        "enterprise-vue2__public-primevue__dashboard-workspace": "conditional",
        "enterprise-vue2__public-primevue__wizard-workspace": "blocked",
    }


def test_validate_frontend_cross_provider_consistency_blocks_unknown_page_schema_and_style_pack() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    bundles = list(consistency.certification_bundles)
    bundles[0] = bundles[0].model_copy(
        update={
            "page_schema_id": "unknown-page",
            "compared_style_pack_id": "unknown-pack",
        }
    )
    consistency = consistency.model_copy(update={"certification_bundles": bundles})

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert result.passed is False
    assert "unknown page schema in pair bundle: unknown-page" in result.blockers
    assert "unknown style pack in pair bundle: unknown-pack" in result.blockers


def test_validate_frontend_cross_provider_consistency_blocks_inconsistent_gap_and_truth_surface_contract() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    bundles = list(consistency.certification_bundles)
    bundles[1] = bundles[1].model_copy(update={"coverage_gap_ids": []})
    truth_records = [
        record
        for record in consistency.truth_surfacing_records
        if not (
            record.pair_id == "enterprise-vue2__public-primevue__search-list-workspace"
            and record.truth_layer == "release-gate-input"
        )
    ]
    consistency = consistency.model_copy(
        update={
            "certification_bundles": bundles,
            "truth_surfacing_records": truth_records,
        }
    )

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert result.passed is False
    assert (
        "coverage-gap pair bundle missing coverage_gap_ids: "
        "enterprise-vue2__public-primevue__dashboard-workspace"
    ) in result.blockers
    assert (
        "truth surfacing missing required layers for pair: "
        "enterprise-vue2__public-primevue__search-list-workspace"
    ) in result.blockers


def test_validate_frontend_cross_provider_consistency_deduplicates_lists() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    bundles = list(consistency.certification_bundles)
    bundles.append(
        bundles[2].model_copy(
            update={"pair_id": "enterprise-vue2__public-primevue__wizard-workspace-copy"}
        )
    )
    truth_records = list(consistency.truth_surfacing_records)
    truth_records.extend(
        [
            truth_records[0].model_copy(
                update={"pair_id": "enterprise-vue2__public-primevue__wizard-workspace-copy"}
            ),
            truth_records[1].model_copy(
                update={"pair_id": "enterprise-vue2__public-primevue__wizard-workspace-copy"}
            ),
        ]
    )
    consistency = consistency.model_copy(
        update={
            "certification_bundles": bundles,
            "truth_surfacing_records": truth_records,
        }
    )

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert len(result.warnings) == len(set(result.warnings))
    assert len(result.blockers) == len(set(result.blockers))


def test_frontend_cross_provider_consistency_validation_result_runtime_object_canonicalizes_lists() -> None:
    result = FrontendCrossProviderConsistencyValidationResult(
        passed=False,
        blockers=["a", "a"],
        warnings=["w", "w"],
        certification_gates={"pair-001": "ready"},
    )

    assert result.blockers == ["a"]
    assert result.warnings == ["w"]


def test_frontend_cross_provider_consistency_models_deduplicate_set_like_lists() -> None:
    consistency = FrontendCrossProviderConsistencySet(
        work_item_id="150",
        source_work_item_ids=["147", "147", "148"],
        ux_equivalence_clauses=[
            UxEquivalenceClause(
                clause_id="clause-001",
                clause_kind="task-outcome",
                description="same task outcome",
                required_journey_ids=["journey-001", "journey-001"],
                required_schema_slot_ids=["slot-001", "slot-001", "slot-002"],
            )
        ],
        diff_records=[
            ConsistencyDiffRecord(
                diff_id="diff-001",
                pair_id="pair-001",
                journey_id="journey-001",
                page_schema_id="dashboard-workspace",
                quality_dimension="visual",
                severity="low",
                summary="minor visual drift",
                evidence_refs=["artifact:one", "artifact:one", "artifact:two"],
            )
        ],
        coverage_gaps=[
            CoverageGapRecord(
                gap_id="gap-001",
                pair_id="pair-001",
                gap_kind="coverage-gap",
                journey_id="journey-001",
                page_schema_id="dashboard-workspace",
                schema_slot_ids=["slot-001", "slot-001", "slot-002"],
                detail="missing a journey",
                upstream_truth_refs=["artifact:truth-a", "artifact:truth-a"],
            )
        ],
        certification_bundles=[
            ProviderPairCertificationBundle(
                pair_id="pair-001",
                baseline_provider_id="enterprise-vue2",
                candidate_provider_id="public-primevue",
                page_schema_id="dashboard-workspace",
                compared_style_pack_id="modern-saas",
                required_journey_ids=["journey-001", "journey-001"],
                state_vector=ConsistencyStateVector(
                    final_verdict="consistent",
                    comparability_state="coverage-gap",
                    blocking_state="ready",
                    evidence_state="advisory",
                ),
                diff_record_ids=["diff-001", "diff-001"],
                coverage_gap_ids=["gap-001", "gap-001"],
            )
        ],
        truth_surfacing_records=[],
        readiness_gate=ConsistencyReadinessGate(
            rules=[
                ReadinessGateRule(
                    gate_state="ready",
                    allowed_final_verdicts=["consistent", "consistent"],
                    allowed_comparability_states=["comparable", "comparable"],
                    allowed_blocking_states=["ready", "ready"],
                    allowed_evidence_states=["fresh", "fresh"],
                    description="ready",
                ),
                ReadinessGateRule(
                    gate_state="conditional",
                    allowed_final_verdicts=["consistent", "consistent"],
                    allowed_comparability_states=["coverage-gap", "coverage-gap"],
                    allowed_blocking_states=["ready", "ready"],
                    allowed_evidence_states=["advisory", "advisory"],
                    description="conditional",
                ),
                ReadinessGateRule(
                    gate_state="blocked",
                    allowed_final_verdicts=["drifted", "drifted", "consistent"],
                    allowed_comparability_states=["not-comparable", "not-comparable"],
                    allowed_blocking_states=["upstream-blocked", "upstream-blocked"],
                    allowed_evidence_states=["needs-recheck", "needs-recheck"],
                    description="blocked",
                ),
            ],
            required_coverage_scope=[
                "required-journeys",
                "required-journeys",
                "required-schema-slots",
            ],
            optional_coverage_scope=[
                "provider-native-visual-advisories",
                "provider-native-visual-advisories",
            ],
            ux_equivalence_clause_ids=["clause-001", "clause-001"],
        ),
        handoff_contract=ConsistencyHandoffContract(
            schema_family="frontend-cross-provider-consistency",
            current_version="1.0",
            compatible_versions=["1.0", "1.0"],
            artifact_root="governance/frontend/cross-provider-consistency",
            canonical_files=[
                "consistency.manifest.yaml",
                "consistency.manifest.yaml",
                "handoff.schema.yaml",
            ],
            program_service_fields=[
                "pair_id",
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
                "pair_id",
                "final_verdict",
                "comparability_state",
                "certification_gate",
            ],
            verify_fields=[
                "pair_id",
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
        ),
    )

    clause = consistency.ux_equivalence_clauses[0]
    diff = consistency.diff_records[0]
    gap = consistency.coverage_gaps[0]
    bundle = consistency.certification_bundles[0]

    assert consistency.source_work_item_ids == ["147", "148"]
    assert clause.required_journey_ids == ["journey-001"]
    assert clause.required_schema_slot_ids == ["slot-001", "slot-002"]
    assert diff.evidence_refs == ["artifact:one", "artifact:two"]
    assert gap.schema_slot_ids == ["slot-001", "slot-002"]
    assert gap.upstream_truth_refs == ["artifact:truth-a"]
    assert bundle.required_journey_ids == ["journey-001"]
    assert bundle.diff_record_ids == ["diff-001"]
    assert bundle.coverage_gap_ids == ["gap-001"]
    assert consistency.readiness_gate.required_coverage_scope == [
        "required-journeys",
        "required-schema-slots",
    ]
    assert consistency.readiness_gate.optional_coverage_scope == [
        "provider-native-visual-advisories"
    ]
    assert consistency.readiness_gate.ux_equivalence_clause_ids == ["clause-001"]
    assert consistency.readiness_gate.rules[0].allowed_final_verdicts == ["consistent"]
    assert consistency.readiness_gate.rules[2].allowed_final_verdicts == [
        "drifted",
        "consistent",
    ]
    assert consistency.handoff_contract.compatible_versions == ["1.0"]
    assert consistency.handoff_contract.canonical_files == [
        "consistency.manifest.yaml",
        "handoff.schema.yaml",
    ]
    assert consistency.handoff_contract.program_service_fields == [
        "pair_id",
        "baseline_provider_id",
        "candidate_provider_id",
        "final_verdict",
        "comparability_state",
        "blocking_state",
        "evidence_state",
        "certification_gate",
    ]
    assert consistency.handoff_contract.cli_fields == [
        "pair_id",
        "final_verdict",
        "comparability_state",
        "certification_gate",
    ]
    assert consistency.handoff_contract.verify_fields == [
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
    ]
