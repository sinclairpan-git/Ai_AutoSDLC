"""Tests for local PR review schema validation helpers."""

from __future__ import annotations

from ai_sdlc.core.loop_models import SchemaValidationStatus
from ai_sdlc.core.pr_review_models import FindingSeverity, ReviewFinding, ReviewPack
from ai_sdlc.core.pr_review_schema import (
    validate_artifact_file,
    validate_artifact_model,
    validate_artifact_payload,
)


def _valid_review_pack_payload() -> dict[str, object]:
    return {
        "schema_version": "1",
        "artifact_kind": "review-pack",
        "created_by": "ai-sdlc",
        "created_at": "2026-06-29T00:00:00Z",
        "ai_sdlc_version": "0.9.1",
        "review_id": "review-001",
        "loop_id": "loop-001",
        "repo_root": "/repo",
        "base_ref": "main",
        "head_ref": "HEAD",
        "base_commit": "a" * 40,
        "head_commit": "b" * 40,
        "changed_files": ["src/app.py"],
        "diff_summary": "",
        "diff_coverage": {},
        "work_item_refs": [],
        "test_results_refs": [],
        "policy_refs": [],
        "policy_profile_id": "default",
        "policy_decisions": {},
        "redaction_report_path": "",
        "reviewer_allowlist": [],
    }


def test_validate_artifact_payload_accepts_valid_payload() -> None:
    report = validate_artifact_payload(_valid_review_pack_payload(), ReviewPack)

    assert report.status == SchemaValidationStatus.VALID
    assert report.errors == []
    assert report.target_artifact_kind == "review-pack"


def test_validate_artifact_payload_blocks_missing_required_field() -> None:
    payload = _valid_review_pack_payload()
    payload.pop("head_commit")

    report = validate_artifact_payload(payload, ReviewPack)

    assert report.status == SchemaValidationStatus.INVALID
    assert any("head_commit" in error for error in report.errors)
    assert report.next_action == "Fix the artifact schema errors before continuing."


def test_validate_artifact_payload_blocks_incompatible_schema_version() -> None:
    payload = _valid_review_pack_payload()
    payload["schema_version"] = "999"

    report = validate_artifact_payload(payload, ReviewPack)

    assert report.status == SchemaValidationStatus.INCOMPATIBLE_SCHEMA
    assert report.errors == [
        "unsupported schema_version: expected 1, got '999'",
    ]


def test_validate_artifact_payload_blocks_illegal_enum() -> None:
    payload = ReviewFinding(
        id="F-001",
        severity=FindingSeverity.REQUIRED,
        file="src/app.py",
        claim="Claim.",
        evidence="Evidence.",
        risk="Risk.",
        suggested_fix="Fix.",
        confidence=0.8,
    ).model_dump(mode="json")
    payload["severity"] = "P0"

    report = validate_artifact_payload(payload, ReviewFinding)

    assert report.status == SchemaValidationStatus.INVALID
    assert any("severity" in error for error in report.errors)


def test_validate_artifact_model_round_trips_model_payload() -> None:
    review_pack = ReviewPack.model_validate(_valid_review_pack_payload())

    report = validate_artifact_model(review_pack)

    assert report.status == SchemaValidationStatus.VALID


def test_validate_artifact_file_reads_json_or_yaml_payload(tmp_path) -> None:
    path = tmp_path / "review-pack.json"
    path.write_text(
        "{\n"
        '  "schema_version": "1",\n'
        '  "artifact_kind": "review-pack",\n'
        '  "created_by": "ai-sdlc",\n'
        '  "created_at": "2026-06-29T00:00:00Z",\n'
        '  "ai_sdlc_version": "0.9.1",\n'
        '  "review_id": "review-001",\n'
        '  "loop_id": "loop-001",\n'
        '  "repo_root": "/repo",\n'
        '  "base_ref": "main",\n'
        '  "head_ref": "HEAD",\n'
        f'  "base_commit": "{"a" * 40}",\n'
        f'  "head_commit": "{"b" * 40}"\n'
        "}\n",
        encoding="utf-8",
    )

    report = validate_artifact_file(path, ReviewPack)

    assert report.status == SchemaValidationStatus.VALID
    assert report.target_path == str(path)


def test_validate_artifact_file_blocks_non_mapping_root(tmp_path) -> None:
    path = tmp_path / "findings.json"
    path.write_text("[]\n", encoding="utf-8")

    report = validate_artifact_file(path, ReviewPack)

    assert report.status == SchemaValidationStatus.INVALID
    assert report.errors == ["artifact root must be a mapping"]
