"""Unit tests for frontend quality platform baseline models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_quality_platform import (
    FrontendQualityPlatformSet,
    QualityCoverageMatrixEntry,
    QualityEvidenceContract,
    QualityPlatformHandoffContract,
    QualityTruthSurfacingRecord,
    QualityVerdictEnvelope,
    build_p2_frontend_quality_platform_baseline,
)


def _handoff() -> QualityPlatformHandoffContract:
    return QualityPlatformHandoffContract(
        schema_family="frontend-quality-platform",
        current_version="1.0",
        compatible_versions=["1.0"],
        artifact_root="governance/frontend/quality-platform",
        canonical_files=[
            "quality-platform.manifest.yaml",
            "handoff.schema.yaml",
            "coverage-matrix.yaml",
            "evidence-platform.yaml",
            "interaction-quality.yaml",
            "truth-surfacing.yaml",
        ],
        program_service_fields=[
            "matrix_id",
            "page_schema_id",
            "browser_id",
            "viewport_id",
            "style_pack_id",
            "gate_state",
        ],
        cli_fields=[
            "matrix_id",
            "page_schema_id",
            "browser_id",
            "viewport_id",
            "gate_state",
        ],
        verify_fields=[
            "matrix_id",
            "page_schema_id",
            "browser_id",
            "viewport_id",
            "style_pack_id",
            "gate_state",
            "evidence_state",
        ],
    )


def test_build_p2_frontend_quality_platform_baseline_materializes_matrix_and_handoff_truth() -> None:
    platform = build_p2_frontend_quality_platform_baseline()

    assert platform.work_item_id == "149"
    assert platform.source_work_item_ids == ["071", "137", "143", "144", "147", "148"]
    assert platform.handoff_contract.artifact_root == (
        "governance/frontend/quality-platform"
    )
    assert {entry.page_schema_id for entry in platform.coverage_matrix} == {
        "dashboard-workspace",
        "search-list-workspace",
    }
    assert {entry.browser_id for entry in platform.coverage_matrix} == {
        "chromium",
        "webkit",
    }
    assert {contract.evidence_contract_id for contract in platform.evidence_contracts} == {
        "visual-regression-evidence",
        "a11y-matrix-evidence",
        "interaction-quality-evidence",
    }
    assert {verdict.gate_state for verdict in platform.verdict_envelopes} == {
        "pass",
        "advisory",
    }

    truth_record = platform.truth_surfacing_records[0]
    assert truth_record.truth_layer == "runtime-truth"
    assert truth_record.artifact_root_ref == "governance/frontend/quality-platform"
    assert truth_record.gate_state in {"pass", "advisory"}


def test_quality_platform_set_rejects_duplicate_matrix_ids() -> None:
    matrix_entry = QualityCoverageMatrixEntry(
        matrix_id="dashboard-modern-saas-desktop-chromium",
        page_schema_id="dashboard-workspace",
        browser_id="chromium",
        viewport_id="desktop-1440",
        style_pack_id="modern-saas",
        interaction_flow_id="dashboard-review-flow",
        evidence_contract_ids=["visual-regression-evidence"],
    )

    with pytest.raises(ValueError, match="duplicate matrix ids"):
        FrontendQualityPlatformSet(
            work_item_id="149",
            source_work_item_ids=["147", "148"],
            coverage_matrix=[matrix_entry, matrix_entry],
            evidence_contracts=[
                QualityEvidenceContract(
                    evidence_contract_id="visual-regression-evidence",
                    evidence_kind="visual-regression",
                    artifact_rel_path="governance/frontend/quality-platform/evidence/visual-regression",
                    required_payload_fields=["screenshot_ref", "diff_ratio"],
                )
            ],
            verdict_envelopes=[
                QualityVerdictEnvelope(
                    verdict_id="dashboard-visual-pass",
                    matrix_id="dashboard-modern-saas-desktop-chromium",
                    verdict_family="visual-regression",
                    gate_state="pass",
                    evidence_state="complete",
                    severity="info",
                    evidence_refs=[
                        "artifact:governance/frontend/quality-platform/evidence/visual-regression/dashboard.yaml"
                    ],
                )
            ],
            truth_surfacing_records=[
                QualityTruthSurfacingRecord(
                    matrix_id="dashboard-modern-saas-desktop-chromium",
                    truth_layer="runtime-truth",
                    gate_state="pass",
                    evidence_state="complete",
                    artifact_root_ref="governance/frontend/quality-platform",
                    verdict_ref="verdict:dashboard-visual-pass",
                )
            ],
            handoff_contract=_handoff(),
        )


def test_quality_verdict_envelope_requires_artifact_evidence_refs() -> None:
    with pytest.raises(ValueError, match="evidence_refs must use artifact: references"):
        QualityVerdictEnvelope(
            verdict_id="dashboard-visual-pass",
            matrix_id="dashboard-modern-saas-desktop-chromium",
            verdict_family="visual-regression",
            gate_state="pass",
            evidence_state="complete",
            severity="info",
            evidence_refs=["tmp/dashboard.png"],
        )


def test_frontend_quality_platform_set_rejects_unknown_matrix_and_evidence_contract_refs() -> None:
    with pytest.raises(ValueError, match="unknown evidence contract ids"):
        FrontendQualityPlatformSet(
            work_item_id="149",
            source_work_item_ids=["147", "148"],
            coverage_matrix=[
                QualityCoverageMatrixEntry(
                    matrix_id="dashboard-modern-saas-desktop-chromium",
                    page_schema_id="dashboard-workspace",
                    browser_id="chromium",
                    viewport_id="desktop-1440",
                    style_pack_id="modern-saas",
                    interaction_flow_id="dashboard-review-flow",
                    evidence_contract_ids=["missing-contract"],
                )
            ],
            evidence_contracts=[
                QualityEvidenceContract(
                    evidence_contract_id="visual-regression-evidence",
                    evidence_kind="visual-regression",
                    artifact_rel_path="governance/frontend/quality-platform/evidence/visual-regression",
                    required_payload_fields=["screenshot_ref", "diff_ratio"],
                )
            ],
            verdict_envelopes=[
                QualityVerdictEnvelope(
                    verdict_id="dashboard-visual-pass",
                    matrix_id="dashboard-modern-saas-desktop-chromium",
                    verdict_family="visual-regression",
                    gate_state="pass",
                    evidence_state="complete",
                    severity="info",
                    evidence_refs=[
                        "artifact:governance/frontend/quality-platform/evidence/visual-regression/dashboard.yaml"
                    ],
                )
            ],
            truth_surfacing_records=[
                QualityTruthSurfacingRecord(
                    matrix_id="dashboard-modern-saas-desktop-chromium",
                    truth_layer="runtime-truth",
                    gate_state="pass",
                    evidence_state="complete",
                    artifact_root_ref="governance/frontend/quality-platform",
                    verdict_ref="verdict:dashboard-visual-pass",
                )
            ],
            handoff_contract=_handoff(),
        )
