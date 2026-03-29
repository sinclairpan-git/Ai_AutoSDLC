"""Unit tests for reviewer gate decisions."""

from __future__ import annotations

from ai_sdlc.core.p1_artifacts import save_reviewer_decision
from ai_sdlc.core.reviewer_gate import (
    ReviewerGateOutcomeKind,
    evaluate_reviewer_gate,
    required_reviewer_checkpoint,
)
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
    WorkItemStatus,
)


def test_required_reviewer_checkpoint_mapping() -> None:
    assert required_reviewer_checkpoint(WorkItemStatus.GOVERNANCE_FROZEN) == PrdReviewerCheckpoint.PRD_FREEZE
    assert required_reviewer_checkpoint(WorkItemStatus.DOCS_BASELINE) == PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE
    assert required_reviewer_checkpoint(WorkItemStatus.DEV_REVIEWED) == PrdReviewerCheckpoint.PRE_CLOSE
    assert required_reviewer_checkpoint(WorkItemStatus.DEV_EXECUTING) is None


def test_gate_allows_matching_approve(tmp_path) -> None:
    save_reviewer_decision(
        tmp_path,
        "WI-001",
        PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
            decision=PrdReviewerDecisionKind.APPROVE,
            target="WI-001",
            reason="Approved for governance freeze",
            next_action="Proceed",
            timestamp="2026-03-29T10:00:00+08:00",
        ),
    )

    outcome = evaluate_reviewer_gate(
        tmp_path,
        "WI-001",
        WorkItemStatus.GOVERNANCE_FROZEN,
    )

    assert outcome.outcome == ReviewerGateOutcomeKind.ALLOW
    assert outcome.checkpoint == PrdReviewerCheckpoint.PRD_FREEZE
    assert outcome.target_status == WorkItemStatus.GOVERNANCE_FROZEN
    assert outcome.reason == "Approved for governance freeze"
    assert outcome.next_action == "Proceed"


def test_gate_denies_missing_approval(tmp_path) -> None:
    outcome = evaluate_reviewer_gate(
        tmp_path,
        "WI-001",
        WorkItemStatus.DOCS_BASELINE,
    )

    assert outcome.outcome == ReviewerGateOutcomeKind.DENY_MISSING
    assert outcome.checkpoint == PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE
    assert outcome.target_status == WorkItemStatus.DOCS_BASELINE
    assert "docs_baseline_freeze" in outcome.reason
    assert "approve" in outcome.next_action


def test_gate_denies_revise(tmp_path) -> None:
    save_reviewer_decision(
        tmp_path,
        "WI-001",
        PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
            decision=PrdReviewerDecisionKind.REVISE,
            target="WI-001",
            reason="Adjust docs baseline first",
            next_action="Revise the docs baseline",
            timestamp="2026-03-29T11:00:00+08:00",
        ),
    )

    outcome = evaluate_reviewer_gate(
        tmp_path,
        "WI-001",
        WorkItemStatus.DOCS_BASELINE,
    )

    assert outcome.outcome == ReviewerGateOutcomeKind.DENY_REVISE
    assert outcome.checkpoint == PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE
    assert outcome.target_status == WorkItemStatus.DOCS_BASELINE
    assert outcome.reason == "Adjust docs baseline first"
    assert outcome.next_action == "Revise the docs baseline"


def test_gate_denies_block(tmp_path) -> None:
    save_reviewer_decision(
        tmp_path,
        "WI-001",
        PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
            decision=PrdReviewerDecisionKind.BLOCK,
            target="WI-001",
            reason="Not ready to close",
            next_action="Resolve open issues",
            timestamp="2026-03-29T12:00:00+08:00",
        ),
    )

    outcome = evaluate_reviewer_gate(
        tmp_path,
        "WI-001",
        WorkItemStatus.DEV_REVIEWED,
    )

    assert outcome.outcome == ReviewerGateOutcomeKind.DENY_BLOCK
    assert outcome.checkpoint == PrdReviewerCheckpoint.PRE_CLOSE
    assert outcome.target_status == WorkItemStatus.DEV_REVIEWED
    assert outcome.reason == "Not ready to close"
    assert outcome.next_action == "Resolve open issues"
