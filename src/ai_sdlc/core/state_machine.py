"""Work item state machine with validated transitions."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.config import YamlStore
from ai_sdlc.core.reviewer_gate import (
    ReviewerGateOutcomeKind,
    evaluate_reviewer_gate,
)
from ai_sdlc.models.work import WorkItem, WorkItemStatus
from ai_sdlc.utils.helpers import now_iso


class InvalidTransitionError(Exception):
    """Raised when an illegal state transition is attempted."""


TRANSITIONS: dict[WorkItemStatus, list[WorkItemStatus]] = {
    WorkItemStatus.CREATED: [WorkItemStatus.INTAKE_CLASSIFIED],
    WorkItemStatus.INTAKE_CLASSIFIED: [WorkItemStatus.GOVERNANCE_FROZEN],
    WorkItemStatus.GOVERNANCE_FROZEN: [WorkItemStatus.DOCS_BASELINE],
    WorkItemStatus.DOCS_BASELINE: [WorkItemStatus.DEV_EXECUTING],
    WorkItemStatus.DEV_EXECUTING: [
        WorkItemStatus.DEV_VERIFYING,
        WorkItemStatus.SUSPENDED,
        WorkItemStatus.FAILED,
    ],
    WorkItemStatus.DEV_VERIFYING: [
        WorkItemStatus.DEV_REVIEWED,
        WorkItemStatus.DEV_EXECUTING,
    ],
    WorkItemStatus.DEV_REVIEWED: [WorkItemStatus.ARCHIVING],
    WorkItemStatus.ARCHIVING: [
        WorkItemStatus.KNOWLEDGE_REFRESHING,
        WorkItemStatus.COMPLETED,  # L0: no refresh needed (BR-051)
    ],
    WorkItemStatus.KNOWLEDGE_REFRESHING: [WorkItemStatus.COMPLETED],
    WorkItemStatus.SUSPENDED: [WorkItemStatus.RESUMED],
    WorkItemStatus.RESUMED: [WorkItemStatus.DEV_EXECUTING],
    WorkItemStatus.COMPLETED: [],
    WorkItemStatus.FAILED: [],
}


def get_valid_transitions(current: WorkItemStatus) -> list[WorkItemStatus]:
    """Return the list of valid target states from the current state."""
    return TRANSITIONS.get(current, [])


def transition(current: WorkItemStatus, target: WorkItemStatus) -> WorkItemStatus:
    """Attempt a state transition.

    Args:
        current: The current work item status.
        target: The desired target status.

    Returns:
        The target status if the transition is valid.

    Raises:
        InvalidTransitionError: If the transition is not allowed.
    """
    valid = get_valid_transitions(current)
    if target not in valid:
        raise InvalidTransitionError(
            f"Cannot transition from {current.value} to {target.value}. "
            f"Valid targets: {[s.value for s in valid]}"
        )
    return target


def work_item_path(root: Path, work_item_id: str) -> Path:
    """Return the filesystem path of a persisted work item."""
    return root / ".ai-sdlc" / "work-items" / work_item_id / "work-item.yaml"


def save_work_item(root: Path, work_item: WorkItem) -> Path:
    """Persist a work item under `.ai-sdlc/work-items/<WI>/work-item.yaml`."""
    if not work_item.created_at:
        work_item.created_at = now_iso()
    work_item.updated_at = now_iso()
    path = work_item_path(root, work_item.work_item_id)
    YamlStore.save(path, work_item)
    return path


def load_work_item(root: Path, work_item_id: str) -> WorkItem:
    """Load a persisted work item."""
    return YamlStore.load(work_item_path(root, work_item_id), WorkItem)


def transition_work_item(
    root: Path,
    work_item: WorkItem,
    target: WorkItemStatus,
) -> WorkItem:
    """Apply a legal transition and persist the new status to work-item.yaml."""
    new_status = transition(work_item.status, target)
    gate = evaluate_reviewer_gate(root, work_item.work_item_id, new_status)
    if gate.outcome != ReviewerGateOutcomeKind.ALLOW:
        checkpoint_label = gate.checkpoint.value if gate.checkpoint is not None else "n/a"
        raise InvalidTransitionError(
            f"Cannot transition from {work_item.status.value} to {new_status.value}. "
            f"Reviewer gate {gate.outcome.value} at {checkpoint_label}: {gate.reason}. "
            f"Next action: {gate.next_action}"
        )
    work_item.status = new_status
    save_work_item(root, work_item)
    return work_item
