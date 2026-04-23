"""Unit tests for frontend visual / a11y evidence provider helpers."""

from __future__ import annotations

import json

import pytest

from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME,
    FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
    FrontendVisualA11yEvidenceArtifact,
    FrontendVisualA11yEvidenceEvaluation,
    FrontendVisualA11yEvidenceFreshness,
    FrontendVisualA11yEvidenceProvenance,
    build_auto_frontend_visual_a11y_evidence_artifact,
    build_frontend_visual_a11y_evidence_artifact,
    load_frontend_visual_a11y_evidence_artifact,
    visual_a11y_evidence_artifact_path,
    write_frontend_visual_a11y_evidence_artifact,
)


def test_write_and_load_frontend_visual_a11y_evidence_artifact_round_trips(
    tmp_path,
) -> None:
    spec_dir = tmp_path / "specs" / "071-demo"
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-pass",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="pass",
            ),
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="partial-error",
                outcome="issue",
                report_type="violation-report",
                severity="high",
                location_anchor="form.error-banner",
                quality_hint="Error banner loses contrast",
            ),
        ],
        provider_kind="manual",
        provider_name="qa-review",
        generated_at="2026-04-07T12:00:00Z",
        source_digest="sha256:evidence-input",
        source_ref="evidence/orders.form.json",
    )

    artifact_path = write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)
    loaded = load_frontend_visual_a11y_evidence_artifact(artifact_path)

    assert artifact_path == spec_dir / FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME
    assert loaded == artifact

    raw = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert raw["schema_version"] == FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION
    assert raw["provenance"]["provider_name"] == "qa-review"
    assert raw["freshness"]["source_digest"] == "sha256:evidence-input"


def test_visual_a11y_evidence_artifact_path_uses_canonical_filename(tmp_path) -> None:
    spec_dir = tmp_path / "specs" / "071-demo"

    path = visual_a11y_evidence_artifact_path(spec_dir)

    assert path == spec_dir / FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME


def test_load_frontend_visual_a11y_evidence_artifact_requires_provenance(
    tmp_path,
) -> None:
    artifact_path = tmp_path / FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
                "freshness": {"generated_at": "2026-04-07T12:00:00Z"},
                "evaluations": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="provenance"):
        load_frontend_visual_a11y_evidence_artifact(artifact_path)


def test_load_frontend_visual_a11y_evidence_artifact_rejects_invalid_issue_report_type(
    tmp_path,
) -> None:
    artifact_path = tmp_path / FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
                "provenance": {
                    "provider_kind": "manual",
                    "provider_name": "fixture",
                },
                "freshness": {"generated_at": "2026-04-07T12:00:00Z"},
                "evaluations": [
                    {
                        "evaluation_id": "eval-issue",
                        "target_id": "orders.form",
                        "surface_id": "refreshing",
                        "outcome": "issue",
                        "report_type": "unsupported-report",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="report_type"):
        load_frontend_visual_a11y_evidence_artifact(artifact_path)


def test_frontend_visual_a11y_evidence_artifact_to_json_dict_deduplicates_evaluations() -> None:
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
            ),
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
            ),
        ],
        provider_kind="manual",
        provider_name="qa-review",
        generated_at="2026-04-07T12:00:00Z",
    )

    payload = artifact.to_json_dict()

    assert payload["evaluations"] == [
        {
            "evaluation_id": "eval-issue",
            "target_id": "orders.form",
            "surface_id": "refreshing",
            "outcome": "issue",
            "report_type": "violation-report",
            "severity": None,
            "location_anchor": None,
            "quality_hint": None,
            "changed_scope_explanation": None,
        }
    ]


def test_build_frontend_visual_a11y_evidence_artifact_deduplicates_source_evaluations() -> None:
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
            ),
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
            ),
        ],
        provider_kind="manual",
        provider_name="qa-review",
        generated_at="2026-04-07T12:00:00Z",
    )

    assert artifact.evaluations == (
        FrontendVisualA11yEvidenceEvaluation(
            evaluation_id="eval-issue",
            target_id="orders.form",
            surface_id="refreshing",
            outcome="issue",
            report_type="violation-report",
        ),
    )


def test_frontend_visual_a11y_evidence_artifact_runtime_object_canonicalizes_evaluations() -> None:
    artifact = FrontendVisualA11yEvidenceArtifact(
        schema_version=FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
        provenance=FrontendVisualA11yEvidenceProvenance(
            provider_kind="manual",
            provider_name="qa-review",
        ),
        freshness=FrontendVisualA11yEvidenceFreshness(
            generated_at="2026-04-07T12:00:00Z"
        ),
        evaluations=(
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
            ),
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="eval-issue",
                target_id="orders.form",
                surface_id="refreshing",
                outcome="issue",
                report_type="violation-report",
            ),
        ),
    )

    assert artifact.evaluations == (
        FrontendVisualA11yEvidenceEvaluation(
            evaluation_id="eval-issue",
            target_id="orders.form",
            surface_id="refreshing",
            outcome="issue",
            report_type="violation-report",
        ),
    )


def test_load_frontend_visual_a11y_evidence_artifact_deduplicates_repeated_evaluations(
    tmp_path,
) -> None:
    artifact_path = tmp_path / FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
                "provenance": {
                    "provider_kind": "manual",
                    "provider_name": "fixture",
                },
                "freshness": {"generated_at": "2026-04-07T12:00:00Z"},
                "evaluations": [
                    {
                        "evaluation_id": "eval-issue",
                        "target_id": "orders.form",
                        "surface_id": "refreshing",
                        "outcome": "issue",
                        "report_type": "violation-report",
                    },
                    {
                        "evaluation_id": "eval-issue",
                        "target_id": "orders.form",
                        "surface_id": "refreshing",
                        "outcome": "issue",
                        "report_type": "violation-report",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    loaded = load_frontend_visual_a11y_evidence_artifact(artifact_path)

    assert loaded.evaluations == (
        FrontendVisualA11yEvidenceEvaluation(
            evaluation_id="eval-issue",
            target_id="orders.form",
            surface_id="refreshing",
            outcome="issue",
            report_type="violation-report",
        ),
    )


def test_build_auto_frontend_visual_a11y_evidence_artifact_surfaces_structural_and_label_issues() -> None:
    artifact = build_auto_frontend_visual_a11y_evidence_artifact(
        target_id="vue3-public-primevue",
        surface_id="managed/frontend/index.html",
        generated_at="2026-04-22T16:20:00Z",
        screenshot_ref=".ai-sdlc/artifacts/frontend-browser-gate/gate-run-001/shared-runtime/navigation-screenshot.png",
        final_url="file:///managed/frontend/index.html",
        page_title="frontend-browser-entry",
        body_text_char_count=420,
        heading_count=0,
        landmark_count=0,
        interactive_count=3,
        unlabeled_button_count=1,
        unlabeled_input_count=2,
        image_missing_alt_count=1,
        console_error_messages=["Unhandled promise rejection"],
        page_error_messages=["ReferenceError: foo is not defined"],
    )

    assert artifact.provenance.provider_kind == "browser_gate_auto"
    assert artifact.provenance.provider_name == "browser_gate_auto_heuristic_v1"
    assert artifact.freshness.source_digest is not None
    assert {item.evaluation_id for item in artifact.evaluations} >= {
        "auto-visual-structure-heading",
        "auto-a11y-landmarks",
        "auto-a11y-button-labels",
        "auto-a11y-input-labels",
        "auto-a11y-image-alt",
        "auto-runtime-console-errors",
    }
    assert any(
        item.outcome == "issue" and item.report_type == "violation-report"
        for item in artifact.evaluations
    )


def test_build_auto_frontend_visual_a11y_evidence_artifact_flags_horizontal_overflow_layout_issue() -> None:
    artifact = build_auto_frontend_visual_a11y_evidence_artifact(
        target_id="vue3-public-primevue",
        surface_id="managed/frontend/index.html",
        generated_at="2026-04-22T16:21:00Z",
        screenshot_ref=".ai-sdlc/artifacts/frontend-browser-gate/gate-run-001/shared-runtime/navigation-screenshot.png",
        final_url="file:///managed/frontend/index.html",
        page_title="frontend-browser-entry",
        body_text_char_count=420,
        heading_count=2,
        landmark_count=2,
        interactive_count=3,
        unlabeled_button_count=0,
        unlabeled_input_count=0,
        image_missing_alt_count=0,
        viewport_width=1024,
        viewport_height=768,
        document_scroll_width=1320,
        document_scroll_height=900,
        horizontal_overflow_count=2,
    )

    layout_evaluations = [
        item for item in artifact.evaluations if item.evaluation_id == "auto-visual-layout-fit"
    ]
    assert len(layout_evaluations) == 1
    assert layout_evaluations[0].outcome == "issue"
    assert layout_evaluations[0].report_type == "violation-report"


def test_build_auto_frontend_visual_a11y_evidence_artifact_surfaces_contrast_and_focus_issues() -> None:
    artifact = build_auto_frontend_visual_a11y_evidence_artifact(
        target_id="vue3-public-primevue",
        surface_id="managed/frontend/index.html",
        generated_at="2026-04-22T16:22:00Z",
        screenshot_ref=".ai-sdlc/artifacts/frontend-browser-gate/gate-run-001/shared-runtime/navigation-screenshot.png",
        final_url="file:///managed/frontend/index.html",
        page_title="frontend-browser-entry",
        body_text_char_count=420,
        heading_count=2,
        landmark_count=2,
        interactive_count=4,
        unlabeled_button_count=0,
        unlabeled_input_count=0,
        image_missing_alt_count=0,
        viewport_width=1280,
        viewport_height=720,
        document_scroll_width=1280,
        document_scroll_height=720,
        horizontal_overflow_count=0,
        low_contrast_text_count=3,
        focusable_count=5,
        focusable_without_visible_focus_count=2,
    )

    evaluation_map = {item.evaluation_id: item for item in artifact.evaluations}
    assert evaluation_map["auto-visual-text-contrast"].outcome == "issue"
    assert evaluation_map["auto-visual-text-contrast"].report_type == "violation-report"
    assert evaluation_map["auto-a11y-focus-visible"].outcome == "issue"
    assert evaluation_map["auto-a11y-focus-visible"].report_type == "violation-report"
