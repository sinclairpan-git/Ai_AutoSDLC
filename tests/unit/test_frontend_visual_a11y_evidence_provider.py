"""Unit tests for frontend visual / a11y evidence provider helpers."""

from __future__ import annotations

import json

import pytest

from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME,
    FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
    FrontendVisualA11yEvidenceEvaluation,
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
