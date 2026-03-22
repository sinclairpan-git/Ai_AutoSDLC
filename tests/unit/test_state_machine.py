"""Unit tests for work item state machine."""

from __future__ import annotations

import pytest

from ai_sdlc.core.state_machine import (
    InvalidTransitionError,
    get_valid_transitions,
    transition,
)
from ai_sdlc.models.work_item import WorkItemStatus


class TestValidTransitions:
    """Test all 12+ legal transitions."""

    LEGAL_TRANSITIONS = [
        (WorkItemStatus.CREATED, WorkItemStatus.INTAKE_CLASSIFIED),
        (WorkItemStatus.INTAKE_CLASSIFIED, WorkItemStatus.GOVERNANCE_FROZEN),
        (WorkItemStatus.GOVERNANCE_FROZEN, WorkItemStatus.DOCS_BASELINE),
        (WorkItemStatus.DOCS_BASELINE, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.DEV_EXECUTING, WorkItemStatus.DEV_VERIFYING),
        (WorkItemStatus.DEV_EXECUTING, WorkItemStatus.SUSPENDED),
        (WorkItemStatus.DEV_EXECUTING, WorkItemStatus.FAILED),
        (WorkItemStatus.DEV_VERIFYING, WorkItemStatus.DEV_REVIEWED),
        (WorkItemStatus.DEV_VERIFYING, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.DEV_REVIEWED, WorkItemStatus.ARCHIVING),
        (WorkItemStatus.ARCHIVING, WorkItemStatus.KNOWLEDGE_REFRESHING),
        (WorkItemStatus.ARCHIVING, WorkItemStatus.COMPLETED),
        (WorkItemStatus.KNOWLEDGE_REFRESHING, WorkItemStatus.COMPLETED),
        (WorkItemStatus.SUSPENDED, WorkItemStatus.RESUMED),
        (WorkItemStatus.RESUMED, WorkItemStatus.DEV_EXECUTING),
    ]

    @pytest.mark.parametrize(("current", "target"), LEGAL_TRANSITIONS)
    def test_legal_transition(
        self, current: WorkItemStatus, target: WorkItemStatus
    ) -> None:
        result = transition(current, target)
        assert result == target


class TestInvalidTransitions:
    """Test illegal transitions are rejected."""

    ILLEGAL_TRANSITIONS = [
        (WorkItemStatus.CREATED, WorkItemStatus.COMPLETED),
        (WorkItemStatus.CREATED, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.COMPLETED, WorkItemStatus.CREATED),
        (WorkItemStatus.FAILED, WorkItemStatus.DEV_EXECUTING),
        (WorkItemStatus.DEV_EXECUTING, WorkItemStatus.CREATED),
        (WorkItemStatus.DOCS_BASELINE, WorkItemStatus.COMPLETED),
        (WorkItemStatus.ARCHIVING, WorkItemStatus.DEV_EXECUTING),
    ]

    @pytest.mark.parametrize(("current", "target"), ILLEGAL_TRANSITIONS)
    def test_illegal_transition_raises(
        self, current: WorkItemStatus, target: WorkItemStatus
    ) -> None:
        with pytest.raises(InvalidTransitionError):
            transition(current, target)


class TestGetValidTransitions:
    def test_created_has_one_target(self) -> None:
        targets = get_valid_transitions(WorkItemStatus.CREATED)
        assert targets == [WorkItemStatus.INTAKE_CLASSIFIED]

    def test_dev_executing_has_three_targets(self) -> None:
        targets = get_valid_transitions(WorkItemStatus.DEV_EXECUTING)
        assert len(targets) == 3

    def test_completed_is_terminal(self) -> None:
        assert get_valid_transitions(WorkItemStatus.COMPLETED) == []

    def test_failed_is_terminal(self) -> None:
        assert get_valid_transitions(WorkItemStatus.FAILED) == []

    def test_archiving_has_two_targets(self) -> None:
        """BR-051: ARCHIVING can go to KNOWLEDGE_REFRESHING or COMPLETED."""
        targets = get_valid_transitions(WorkItemStatus.ARCHIVING)
        assert WorkItemStatus.KNOWLEDGE_REFRESHING in targets
        assert WorkItemStatus.COMPLETED in targets
        assert len(targets) == 2
