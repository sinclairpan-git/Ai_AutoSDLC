"""Tests for local adversarial PR review model contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_sdlc.core.loop_models import (
    LOOP_SCHEMA_VERSION,
    LoopPolicyProfile,
    LoopRound,
    LoopRun,
    LoopStatus,
    LoopType,
    SchemaValidationReport,
    SchemaValidationStatus,
)
from ai_sdlc.core.pr_review_models import (
    DiffSourceDescriptor,
    DiffSourceKind,
    FindingResolution,
    FindingResolutionStatus,
    FindingSeverity,
    ModelResolution,
    ModelResolutionSource,
    ModelResolutionStatus,
    ProviderIsolationStatus,
    ProviderMode,
    ProviderRunnerInvocation,
    ReviewAttestation,
    ReviewFinding,
    ReviewFindings,
    ReviewPack,
    ReviewRun,
    ReviewVerdict,
    SourceAccessStatus,
    SourceAdapterResolution,
)


def test_loop_run_persists_required_artifact_metadata() -> None:
    loop_run = LoopRun(
        loop_id="loop-001",
        loop_type=LoopType.LOCAL_PR_REVIEW,
        status=LoopStatus.CREATED,
        rounds=[
            LoopRound(
                round_number=1,
                status=LoopStatus.RUNNING,
                input_artifacts=["review-pack.json"],
            )
        ],
        current_round=1,
    )

    payload = loop_run.model_dump(mode="json")

    assert payload["schema_version"] == LOOP_SCHEMA_VERSION
    assert payload["artifact_kind"] == "loop-run"
    assert payload["created_by"] == "ai-sdlc"
    assert payload["created_at"]
    assert payload["ai_sdlc_version"]
    assert payload["loop_type"] == "local-pr-review"
    assert payload["status"] == "created"
    assert payload["rounds"][0]["artifact_kind"] == "loop-round"


def test_loop_run_rejects_current_round_without_round_record() -> None:
    with pytest.raises(ValidationError, match="current_round must reference"):
        LoopRun(
            loop_id="loop-001",
            loop_type=LoopType.LOCAL_PR_REVIEW,
            current_round=1,
        )


def test_review_pack_requires_commit_scope_and_stable_metadata() -> None:
    review_pack = ReviewPack(
        review_id="review-001",
        loop_id="loop-001",
        diff_source=DiffSourceDescriptor(
            source_kind=DiffSourceKind.LOCAL_GIT_RANGE,
            adapter_id="local-git-range",
            source_id="main...HEAD",
            repo_root="/repo",
            base_ref="main",
            head_ref="HEAD",
            base_commit="a" * 40,
            head_commit="b" * 40,
            access_status=SourceAccessStatus.RESOLVED,
        ),
        source_adapter="local-git-range",
        source_access_status=SourceAccessStatus.RESOLVED,
        source_resolution_path="/repo/.ai-sdlc/reviews/pr/review-001/source-resolution.json",
        repo_root="/repo",
        base_ref="main",
        head_ref="HEAD",
        base_commit="a" * 40,
        head_commit="b" * 40,
        changed_files=["src/app.py"],
        diff_path="/repo/.ai-sdlc/reviews/pr/review-001/diff.patch",
        diff_coverage={"changed_files": 1, "included_files": 1},
        policy_decisions={"model": "current", "remote_model_policy": "disclose"},
        model_selector="current",
        resolved_model="gpt",
        model_resolution_status=ModelResolutionStatus.RESOLVED,
        model_resolution_source=ModelResolutionSource.CURRENT_AGENT,
        provider_mode=ProviderMode.LOCAL_AGENT,
        code_egress=True,
    )

    payload = review_pack.model_dump(mode="json")

    assert payload["artifact_kind"] == "review-pack"
    assert payload["schema_version"] == LOOP_SCHEMA_VERSION
    assert payload["review_id"] == "review-001"
    assert payload["diff_source"]["source_kind"] == "local-git-range"
    assert payload["source_adapter"] == "local-git-range"
    assert payload["source_access_status"] == "resolved"
    assert payload["changed_files"] == ["src/app.py"]
    assert payload["diff_path"].endswith("/diff.patch")
    assert payload["policy_decisions"] == {
        "model": "current",
        "remote_model_policy": "disclose",
    }
    assert payload["model_selector"] == "current"
    assert payload["resolved_model"] == "gpt"
    assert payload["model_resolution_status"] == "resolved"
    assert payload["model_resolution_source"] == "current_agent"
    assert payload["provider_mode"] == "local_agent"
    assert payload["code_egress"] is True


def test_review_pack_rejects_missing_commit_scope() -> None:
    with pytest.raises(ValidationError, match="missing review pack scope fields"):
        ReviewPack(
            review_id="review-001",
            loop_id="loop-001",
            repo_root="/repo",
            base_ref="main",
            head_ref="HEAD",
            base_commit="",
            head_commit="b" * 40,
        )


def test_review_pack_resolved_model_state_requires_resolved_model_and_source() -> None:
    with pytest.raises(ValidationError, match="resolved review pack model state"):
        ReviewPack(
            review_id="review-001",
            loop_id="loop-001",
            repo_root="/repo",
            base_ref="main",
            head_ref="HEAD",
            base_commit="a" * 40,
            head_commit="b" * 40,
            model_resolution_status=ModelResolutionStatus.RESOLVED,
            resolved_model="",
        )


def test_source_resolution_requires_blocker_when_unresolved() -> None:
    with pytest.raises(ValidationError, match="unresolved source requires"):
        SourceAdapterResolution(
            source_kind=DiffSourceKind.PATCH,
            adapter_id="patch",
            repo_root="/repo",
            access_status=SourceAccessStatus.NEEDS_USER,
        )


def test_source_resolution_embeds_descriptor() -> None:
    resolution = SourceAdapterResolution(
        source_kind=DiffSourceKind.LOCAL_GIT_RANGE,
        adapter_id="local-git-range",
        source_id="main...HEAD",
        repo_root="/repo",
        base_ref="main",
        head_ref="HEAD",
        base_commit="a" * 40,
        head_commit="b" * 40,
        access_status=SourceAccessStatus.RESOLVED,
    )

    descriptor = resolution.to_descriptor().model_dump(mode="json")

    assert resolution.artifact_kind == "source-resolution"
    assert descriptor["source_kind"] == "local-git-range"
    assert descriptor["adapter_id"] == "local-git-range"
    assert descriptor["base_commit"] == "a" * 40


def test_review_attestation_is_ci_read_only() -> None:
    attestation = ReviewAttestation(
        review_id="review-001",
        loop_id="loop-001",
        head_commit="b" * 40,
        verdict=ReviewVerdict.FULLY_CLEAN,
        review_run_path=".ai-sdlc/reviews/pr/review-001/review-run.json",
        review_pack_path=".ai-sdlc/reviews/pr/review-001/review-pack.json",
        final_report_path=".ai-sdlc/reviews/pr/review-001/final-report.md",
    )

    payload = attestation.model_dump(mode="json")

    assert payload["artifact_kind"] == "review-attestation"
    assert payload["ci_may_call_model"] is False
    assert payload["diff_source"]["source_kind"] == "local-git-range"
    assert payload["verdict"] == "fully_clean"


def test_review_attestation_requires_non_git_range_diff_source_hash() -> None:
    with pytest.raises(
        ValidationError,
        match="non-git-range review attestation requires diff_source_hash",
    ):
        ReviewAttestation(
            review_id="review-001",
            loop_id="loop-001",
            head_commit="b" * 40,
            diff_source=DiffSourceDescriptor(source_kind=DiffSourceKind.LOCAL_STAGED),
            verdict=ReviewVerdict.FULLY_CLEAN,
            review_run_path=".ai-sdlc/reviews/pr/review-001/review-run.json",
            review_pack_path=".ai-sdlc/reviews/pr/review-001/review-pack.json",
            final_report_path=".ai-sdlc/reviews/pr/review-001/final-report.md",
        )


def test_review_attestation_rejects_ci_model_calls() -> None:
    with pytest.raises(ValidationError, match="cannot authorize CI model calls"):
        ReviewAttestation(
            review_id="review-001",
            loop_id="loop-001",
            head_commit="b" * 40,
            verdict=ReviewVerdict.FULLY_CLEAN,
            review_run_path=".ai-sdlc/reviews/pr/review-001/review-run.json",
            review_pack_path=".ai-sdlc/reviews/pr/review-001/review-pack.json",
            final_report_path=".ai-sdlc/reviews/pr/review-001/final-report.md",
            ci_may_call_model=True,
        )


def test_review_finding_uses_stable_severity_and_resolution_values() -> None:
    finding = ReviewFinding(
        id="F-001",
        severity=FindingSeverity.BLOCKER,
        file="src/app.py",
        line=12,
        claim="Missing authorization check.",
        evidence="The changed endpoint accepts requests without auth.",
        risk="Unauthorized access.",
        suggested_fix="Require auth before reading the record.",
        confidence=0.92,
        resolution=FindingResolutionStatus.UNRESOLVED,
    )

    payload = finding.model_dump(mode="json")

    assert payload["severity"] == "BLOCKER"
    assert payload["resolution"] == "unresolved"
    assert payload["artifact_kind"] == "review-finding"


def test_review_finding_rejects_illegal_enum() -> None:
    with pytest.raises(ValidationError):
        ReviewFinding(
            id="F-001",
            severity="P0",
            file="src/app.py",
            claim="Issue.",
            evidence="Evidence.",
            risk="Risk.",
            suggested_fix="Fix.",
            confidence=0.5,
        )


def test_review_findings_records_provider_verdict_and_findings() -> None:
    findings = ReviewFindings(
        review_id="review-001",
        loop_id="loop-001",
        review_pack_path="/repo/.ai-sdlc/reviews/pr/review-001/review-pack.json",
        provider_id="mock-reviewer",
        model_selector="fixture",
        resolved_model="mock-reviewer",
        verdict=ReviewVerdict.CHANGES_REQUIRED,
        findings=[
            ReviewFinding(
                id="F-001",
                severity=FindingSeverity.REQUIRED,
                file="src/app.py",
                claim="Missing test.",
                evidence="The changed behavior has no focused test.",
                risk="Regression may ship.",
                suggested_fix="Add a focused regression test.",
                confidence=0.8,
            )
        ],
    )

    payload = findings.model_dump(mode="json")

    assert payload["artifact_kind"] == "review-findings"
    assert payload["verdict"] == "changes_required"
    assert payload["findings"][0]["severity"] == "REQUIRED"


def test_review_findings_rejects_duplicate_finding_ids() -> None:
    finding = ReviewFinding(
        id="F-001",
        severity=FindingSeverity.REQUIRED,
        file="src/app.py",
        claim="Missing test.",
        evidence="The changed behavior has no focused test.",
        risk="Regression may ship.",
        suggested_fix="Add a focused regression test.",
        confidence=0.8,
    )

    with pytest.raises(ValidationError, match="duplicate review finding ids"):
        ReviewFindings(
            review_id="review-001",
            loop_id="loop-001",
            review_pack_path="/repo/review-pack.json",
            provider_id="mock-reviewer",
            model_selector="fixture",
            resolved_model="mock-reviewer",
            verdict=ReviewVerdict.CHANGES_REQUIRED,
            findings=[
                finding,
                finding.model_copy(update={"file": "src/other.py"}),
            ],
        )


def test_review_findings_requires_finding_for_changes_required() -> None:
    with pytest.raises(ValidationError, match="require at least one finding"):
        ReviewFindings(
            review_id="review-001",
            loop_id="loop-001",
            review_pack_path="/repo/review-pack.json",
            provider_id="mock-reviewer",
            model_selector="fixture",
            resolved_model="mock-reviewer",
            verdict=ReviewVerdict.CHANGES_REQUIRED,
        )


def test_review_findings_requires_blocker_for_blocked_verdict() -> None:
    with pytest.raises(ValidationError, match="blocked findings require blocker"):
        ReviewFindings(
            review_id="review-001",
            loop_id="loop-001",
            review_pack_path="/repo/review-pack.json",
            provider_id="mock-reviewer",
            model_selector="fixture",
            resolved_model="mock-reviewer",
            verdict=ReviewVerdict.BLOCKED,
        )


def test_review_findings_rejects_clean_verdict_with_required_findings() -> None:
    with pytest.raises(ValidationError, match="clean findings cannot include"):
        ReviewFindings(
            review_id="review-001",
            loop_id="loop-001",
            review_pack_path="/repo/review-pack.json",
            provider_id="mock-reviewer",
            model_selector="fixture",
            resolved_model="mock-reviewer",
            verdict=ReviewVerdict.CLEAN,
            findings=[
                ReviewFinding(
                    id="F-001",
                    severity=FindingSeverity.REQUIRED,
                    file="src/app.py",
                    claim="Missing test.",
                    evidence="No test covers the changed behavior.",
                    risk="Regression may ship.",
                    suggested_fix="Add a focused test.",
                    confidence=0.8,
                )
            ],
        )


def test_fixed_resolution_requires_audit_metadata() -> None:
    with pytest.raises(ValidationError, match="fixed findings require"):
        FindingResolution(
            finding_id="F-001",
            status=FindingResolutionStatus.FIXED,
        )


def test_waived_resolution_requires_audit_metadata() -> None:
    with pytest.raises(ValidationError, match="waived findings require"):
        FindingResolution(
            finding_id="F-001",
            status=FindingResolutionStatus.WAIVED,
            reason="",
            operator="",
        )
    with pytest.raises(ValidationError, match="waived findings require"):
        FindingResolution(
            finding_id="F-001",
            status=FindingResolutionStatus.WAIVED,
            reason="Accepted release risk.",
            operator="qa-owner",
            resolved_at="",
        )


def test_policy_profile_defaults_are_safe_by_default() -> None:
    policy = LoopPolicyProfile()

    assert policy.default_provider == "local-agent"
    assert policy.default_model == "current"
    assert policy.allowed_model_selectors == []
    assert policy.remote_model_policy == "disclose"
    assert policy.high_risk_secret_policy == "needs_user"
    assert policy.max_rounds == 2
    assert policy.default_close_mode == "strict"
    assert policy.redaction_strictness == "fail-closed"


def test_model_resolution_records_current_model_source() -> None:
    resolution = ModelResolution(
        provider_id="local-agent",
        provider_mode=ProviderMode.LOCAL_AGENT,
        model_selector="current",
        resolved_model="gpt-5",
        resolution_source=ModelResolutionSource.CURRENT_AGENT,
        status=ModelResolutionStatus.RESOLVED,
        code_egress=True,
    )

    payload = resolution.model_dump(mode="json")

    assert payload["artifact_kind"] == "model-resolution"
    assert payload["provider_mode"] == "local_agent"
    assert payload["model_selector"] == "current"
    assert payload["resolved_model"] == "gpt-5"
    assert payload["resolution_source"] == "current_agent"
    assert payload["status"] == "resolved"
    assert payload["code_egress"] is True


def test_unresolved_model_resolution_requires_blocker() -> None:
    with pytest.raises(ValidationError, match="requires blocker"):
        ModelResolution(
            provider_id="local-agent",
            model_selector="current",
            status=ModelResolutionStatus.NEEDS_USER,
        )


def test_provider_invocation_records_isolation_and_exit_contract() -> None:
    invocation = ProviderRunnerInvocation(
        provider_id="mock-reviewer",
        provider_mode=ProviderMode.MOCK,
        model_selector="fixture",
        resolved_model="mock-reviewer",
        model_resolution_source=ModelResolutionSource.MOCK_FIXTURE,
        code_egress=False,
        command="ai-sdlc",
        argv=["pr-review", "mock-reviewer"],
        cwd="/repo",
        input_path="/repo/.ai-sdlc/reviews/pr/review-001/review-pack.json",
        output_path="/repo/.ai-sdlc/reviews/pr/review-001/findings.json",
        isolation_status=ProviderIsolationStatus.ISOLATED_PROCESS,
        exit_code=10,
        status=LoopStatus.NEEDS_FIX,
    )

    payload = invocation.model_dump(mode="json")

    assert payload["artifact_kind"] == "provider-runner-invocation"
    assert payload["provider_mode"] == "mock"
    assert payload["model_selector"] == "fixture"
    assert payload["resolved_model"] == "mock-reviewer"
    assert payload["model_resolution_source"] == "mock_fixture"
    assert payload["code_egress"] is False
    assert payload["isolation_status"] == "isolated_process"
    assert payload["exit_code"] == 10
    assert payload["status"] == "needs_fix"


def test_provider_invocation_rejects_empty_resolved_model() -> None:
    with pytest.raises(ValidationError, match="provider runner field is required"):
        ProviderRunnerInvocation(
            provider_id="local-agent",
            model_selector="current",
            resolved_model="",
            model_resolution_source=ModelResolutionSource.CURRENT_AGENT,
            command="ai-sdlc",
            cwd="/repo",
            input_path="/repo/review-pack.json",
            output_path="/repo/findings.json",
        )


def test_review_run_tracks_unresolved_counts_and_verdict() -> None:
    review_run = ReviewRun(
        review_id="review-001",
        loop_id="loop-001",
        provider_id="mock-reviewer",
        provider_mode=ProviderMode.MOCK,
        model_selector="fixture",
        resolved_model="mock-reviewer",
        model_resolution_status=ModelResolutionStatus.RESOLVED,
        model_resolution_source=ModelResolutionSource.MOCK_FIXTURE,
        verdict=ReviewVerdict.CHANGES_REQUIRED,
        unresolved_blockers=1,
        unresolved_required=2,
    )

    payload = review_run.model_dump(mode="json")

    assert payload["artifact_kind"] == "review-run"
    assert payload["loop_type"] == "local-pr-review"
    assert payload["provider_mode"] == "mock"
    assert payload["model_selector"] == "fixture"
    assert payload["resolved_model"] == "mock-reviewer"
    assert payload["model_resolution_status"] == "resolved"
    assert payload["model_resolution_source"] == "mock_fixture"
    assert payload["verdict"] == "changes_required"
    assert payload["unresolved_blockers"] == 1


def test_schema_validation_report_requires_errors_for_invalid_status() -> None:
    with pytest.raises(ValidationError, match="require errors"):
        SchemaValidationReport(
            target_artifact_kind="review-pack",
            status=SchemaValidationStatus.INVALID,
        )
