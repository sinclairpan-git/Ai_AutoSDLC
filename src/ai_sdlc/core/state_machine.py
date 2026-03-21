"""Work item state machine with validated transitions."""

from __future__ import annotations

from ai_sdlc.models.work_item import WorkItemStatus


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
    WorkItemStatus.ARCHIVING: [WorkItemStatus.KNOWLEDGE_REFRESHING],
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
