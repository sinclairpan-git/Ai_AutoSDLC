"""Unit tests for frontend quality platform validation helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_quality_platform import (
    FrontendQualityPlatformValidationResult,
    validate_frontend_quality_platform,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    FrontendQualityPlatformSet,
    InteractionQualityFlow,
    QualityCoverageMatrixEntry,
    QualityEvidenceContract,
    QualityPlatformHandoffContract,
    QualityVerdictEnvelope,
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)


def test_validate_frontend_quality_platform_passes_for_builtin_baseline() -> None:
    platform = build_p2_frontend_quality_platform_baseline()

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.matrix_coverage_count == 3
    assert result.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]


def test_validate_frontend_quality_platform_blocks_unknown_page_schema_and_theme_pack() -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    mutated_matrix = list(platform.coverage_matrix)
    mutated_matrix[0] = mutated_matrix[0].model_copy(
        update={
            "page_schema_id": "unknown-page",
            "style_pack_id": "unknown-pack",
        }
    )
    platform = platform.model_copy(update={"coverage_matrix": mutated_matrix})

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.passed is False
    assert "unknown page schema: unknown-page" in result.blockers
    assert "unknown style pack: unknown-pack" in result.blockers


def test_validate_frontend_quality_platform_blocks_snapshot_style_pack_outside_governance() -> None:
    platform = build_p2_frontend_quality_platform_baseline()

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="unsupported-pack",
            effective_style_pack_id="unsupported-pack",
            recommended_style_pack_id="unsupported-pack",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.passed is False
    assert "effective style pack outside theme governance: unsupported-pack" in result.blockers


def test_validate_frontend_quality_platform_deduplicates_lists() -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    duplicated_matrix = list(platform.coverage_matrix)
    duplicated_matrix.append(platform.coverage_matrix[0])
    duplicated_contracts = list(platform.evidence_contracts)
    duplicated_contracts.append(platform.evidence_contracts[0])
    duplicated_verdicts = list(platform.verdict_envelopes)
    duplicated_verdicts.append(
        platform.verdict_envelopes[0].model_copy(update={"verdict_id": "dup-advisory"})
    )
    platform = platform.model_copy(
        update={
            "coverage_matrix": duplicated_matrix,
            "evidence_contracts": duplicated_contracts,
            "verdict_envelopes": duplicated_verdicts,
        }
    )

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]
    assert len(result.evidence_contract_ids) == len(set(result.evidence_contract_ids))
    assert len(result.warnings) == len(set(result.warnings))


def test_frontend_quality_platform_validation_result_runtime_object_canonicalizes_lists() -> None:
    result = FrontendQualityPlatformValidationResult(
        passed=False,
        blockers=["a", "a"],
        warnings=["w", "w"],
        page_schema_ids=["page-a", "page-a", "page-b"],
        evidence_contract_ids=["contract-a", "contract-a", "contract-b"],
    )

    assert result.blockers == ["a"]
    assert result.warnings == ["w"]
    assert result.page_schema_ids == ["page-a", "page-b"]
    assert result.evidence_contract_ids == ["contract-a", "contract-b"]


def test_frontend_quality_platform_models_deduplicate_set_like_lists() -> None:
    platform = FrontendQualityPlatformSet(
        work_item_id="149",
        source_work_item_ids=["147", "147", "148"],
        coverage_matrix=[
            QualityCoverageMatrixEntry(
                matrix_id="matrix-001",
                page_schema_id="dashboard-workspace",
                browser_id="chromium",
                viewport_id="desktop-1440",
                style_pack_id="modern-saas",
                interaction_flow_id="flow-001",
                evidence_contract_ids=["contract-a", "contract-a", "contract-b"],
            )
        ],
        evidence_contracts=[
            QualityEvidenceContract(
                evidence_contract_id="contract-a",
                evidence_kind="visual-regression",
                artifact_rel_path="governance/frontend/quality-platform/visual.json",
                required_payload_fields=["matrix_id", "matrix_id", "page_schema_id"],
            ),
            QualityEvidenceContract(
                evidence_contract_id="contract-b",
                evidence_kind="complete-a11y",
                artifact_rel_path="governance/frontend/quality-platform/a11y.json",
                required_payload_fields=["matrix_id", "page_schema_id"],
            ),
        ],
        interaction_flows=[
            InteractionQualityFlow(
                flow_id="flow-001",
                page_schema_id="dashboard-workspace",
                required_probe_sources=["smoke", "smoke", "a11y"],
                focus_areas=["navigation", "navigation", "form"],
                remediation_hints=["rerun", "rerun", "stabilize"],
            )
        ],
        verdict_envelopes=[
            QualityVerdictEnvelope(
                verdict_id="verdict-001",
                matrix_id="matrix-001",
                verdict_family="visual-regression",
                gate_state="advisory",
                evidence_state="complete",
                severity="low",
                evidence_refs=["artifact:one", "artifact:one", "artifact:two"],
            )
        ],
        truth_surfacing_records=[],
        handoff_contract=QualityPlatformHandoffContract(
            schema_family="frontend-quality-platform",
            current_version="1.0",
            compatible_versions=["1.0", "1.0"],
            artifact_root="governance/frontend/quality-platform",
            canonical_files=[
                "quality-platform.manifest.yaml",
                "quality-platform.manifest.yaml",
                "handoff.schema.yaml",
            ],
            program_service_fields=[
                "matrix_id",
                "matrix_id",
                "page_schema_id",
                "browser_id",
                "viewport_id",
                "style_pack_id",
                "gate_state",
            ],
            cli_fields=[
                "matrix_id",
                "matrix_id",
                "page_schema_id",
                "browser_id",
                "viewport_id",
                "gate_state",
            ],
            verify_fields=[
                "matrix_id",
                "matrix_id",
                "page_schema_id",
                "browser_id",
                "viewport_id",
                "style_pack_id",
                "gate_state",
                "evidence_state",
            ],
        ),
    )

    assert platform.source_work_item_ids == ["147", "148"]
    assert platform.coverage_matrix[0].evidence_contract_ids == ["contract-a", "contract-b"]
    assert platform.evidence_contracts[0].required_payload_fields == [
        "matrix_id",
        "page_schema_id",
    ]
    assert platform.interaction_flows[0].required_probe_sources == ["smoke", "a11y"]
    assert platform.interaction_flows[0].focus_areas == ["navigation", "form"]
    assert platform.interaction_flows[0].remediation_hints == ["rerun", "stabilize"]
    assert platform.verdict_envelopes[0].evidence_refs == [
        "artifact:one",
        "artifact:two",
    ]
    assert platform.handoff_contract.compatible_versions == ["1.0"]
    assert platform.handoff_contract.canonical_files == [
        "quality-platform.manifest.yaml",
        "handoff.schema.yaml",
    ]
    assert platform.handoff_contract.program_service_fields == [
        "matrix_id",
        "page_schema_id",
        "browser_id",
        "viewport_id",
        "style_pack_id",
        "gate_state",
    ]
    assert platform.handoff_contract.cli_fields == [
        "matrix_id",
        "page_schema_id",
        "browser_id",
        "viewport_id",
        "gate_state",
    ]
    assert platform.handoff_contract.verify_fields == [
        "matrix_id",
        "page_schema_id",
        "browser_id",
        "viewport_id",
        "style_pack_id",
        "gate_state",
        "evidence_state",
    ]
