"""Reviewer gate helpers for runtime state transitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ai_sdlc.core.p1_artifacts import load_reviewer_decision_for_checkpoint
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
    WorkItemStatus,
)


class ReviewerGateOutcomeKind(str, Enum):
    """Explicit reviewer gate outcomes for transition checks."""

    ALLOW = "allow"
    DENY_MISSING = "deny_missing"
    DENY_REVISE = "deny_revise"
    DENY_BLOCK = "deny_block"


@dataclass(frozen=True, slots=True)
class ReviewerGateResult:
    """Structured reviewer gate outcome for transitions and close checks."""

    outcome: ReviewerGateOutcomeKind
    checkpoint: PrdReviewerCheckpoint | None
    target_status: WorkItemStatus
    reason: str
    next_action: str
    reviewer_decision: PrdReviewerDecision | None = None


_REVIEWER_CHECKPOINT_BY_STATUS: dict[WorkItemStatus, PrdReviewerCheckpoint] = {
    WorkItemStatus.GOVERNANCE_FROZEN: PrdReviewerCheckpoint.PRD_FREEZE,
    WorkItemStatus.DOCS_BASELINE: PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
    WorkItemStatus.DEV_REVIEWED: PrdReviewerCheckpoint.PRE_CLOSE,
}


def required_reviewer_checkpoint(
    target_status: WorkItemStatus,
) -> PrdReviewerCheckpoint | None:
    """Return the checkpoint required to enter a target status, if any."""
    return _REVIEWER_CHECKPOINT_BY_STATUS.get(target_status)


def _missing_gate_result(
    *,
    checkpoint: PrdReviewerCheckpoint,
    target_status: WorkItemStatus,
) -> ReviewerGateResult:
    reason = f"Missing reviewer approval for {checkpoint.value}"
    next_action = (
        f"Save an approved reviewer decision for {checkpoint.value} before transitioning to "
        f"{target_status.value}."
    )
    return ReviewerGateResult(
        outcome=ReviewerGateOutcomeKind.DENY_MISSING,
        checkpoint=checkpoint,
        target_status=target_status,
        reason=reason,
        next_action=next_action,
    )


def evaluate_reviewer_gate(
    root: Path,
    work_item_id: str,
    target_status: WorkItemStatus,
) -> ReviewerGateResult:
    """Evaluate the reviewer gate for a target status."""
    checkpoint = required_reviewer_checkpoint(target_status)
    if checkpoint is None:
        return ReviewerGateResult(
            outcome=ReviewerGateOutcomeKind.ALLOW,
            checkpoint=None,
            target_status=target_status,
            reason="",
            next_action="",
        )

    decision = load_reviewer_decision_for_checkpoint(root, work_item_id, checkpoint)
    if decision is None:
        return _missing_gate_result(checkpoint=checkpoint, target_status=target_status)

    if decision.decision == PrdReviewerDecisionKind.APPROVE:
        return ReviewerGateResult(
            outcome=ReviewerGateOutcomeKind.ALLOW,
            checkpoint=checkpoint,
            target_status=target_status,
            reason=decision.reason,
            next_action=decision.next_action,
            reviewer_decision=decision,
        )
    if decision.decision == PrdReviewerDecisionKind.REVISE:
        return ReviewerGateResult(
            outcome=ReviewerGateOutcomeKind.DENY_REVISE,
            checkpoint=checkpoint,
            target_status=target_status,
            reason=decision.reason or f"Reviewer requested revisions for {checkpoint.value}",
            next_action=decision.next_action
            or f"Revise the artifact required for {target_status.value}.",
            reviewer_decision=decision,
        )
    return ReviewerGateResult(
        outcome=ReviewerGateOutcomeKind.DENY_BLOCK,
        checkpoint=checkpoint,
        target_status=target_status,
        reason=decision.reason or f"Reviewer blocked {checkpoint.value}",
        next_action=decision.next_action or f"Resolve blockers before {target_status.value}.",
        reviewer_decision=decision,
    )
