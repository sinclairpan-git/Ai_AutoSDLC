"""Unit tests for work item state machine."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core.p1_artifacts import save_reviewer_decision
from ai_sdlc.core.state_machine import (
    InvalidTransitionError,
    get_valid_transitions,
    load_work_item,
    save_work_item,
    transition,
    transition_work_item,
)
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
    WorkItem,
    WorkItemSource,
    WorkItemStatus,
    WorkType,
)


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


def _make_work_item() -> WorkItem:
    return WorkItem(
        work_item_id="WI-2026-001",
        work_type=WorkType.NEW_REQUIREMENT,
        source=WorkItemSource.TEXT,
        title="State machine fixture",
        description="fixture",
    )


class TestPersistentTransitions:
    def test_transition_work_item_persists_status(self, tmp_path: Path) -> None:
        work_item = _make_work_item()
        save_work_item(tmp_path, work_item)

        updated = transition_work_item(
            tmp_path,
            work_item,
            WorkItemStatus.INTAKE_CLASSIFIED,
        )

        assert updated.status == WorkItemStatus.INTAKE_CLASSIFIED
        loaded = load_work_item(tmp_path, work_item.work_item_id)
        assert loaded.status == WorkItemStatus.INTAKE_CLASSIFIED

    def test_illegal_transition_does_not_mutate_disk(self, tmp_path: Path) -> None:
        work_item = _make_work_item()
        save_work_item(tmp_path, work_item)

        with pytest.raises(InvalidTransitionError):
            transition_work_item(tmp_path, work_item, WorkItemStatus.COMPLETED)

        loaded = load_work_item(tmp_path, work_item.work_item_id)
        assert loaded.status == WorkItemStatus.CREATED

    def test_gated_transition_requires_matching_checkpoint_approval(
        self, tmp_path: Path
    ) -> None:
        work_item = _make_work_item()
        work_item.status = WorkItemStatus.INTAKE_CLASSIFIED
        save_work_item(tmp_path, work_item)

        save_reviewer_decision(
            tmp_path,
            work_item.work_item_id,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target=work_item.work_item_id,
                reason="Approved for docs baseline",
                next_action="Proceed",
                timestamp="2026-03-29T11:00:00+08:00",
            ),
        )

        with pytest.raises(InvalidTransitionError):
            transition_work_item(tmp_path, work_item, WorkItemStatus.GOVERNANCE_FROZEN)

        loaded = load_work_item(tmp_path, work_item.work_item_id)
        assert loaded.status == WorkItemStatus.INTAKE_CLASSIFIED

    def test_transition_work_item_denies_revise_gate(
        self, tmp_path: Path
    ) -> None:
        work_item = _make_work_item()
        work_item.status = WorkItemStatus.INTAKE_CLASSIFIED
        save_work_item(tmp_path, work_item)

        save_reviewer_decision(
            tmp_path,
            work_item.work_item_id,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
                decision=PrdReviewerDecisionKind.REVISE,
                target=work_item.work_item_id,
                reason="Need more detail before freeze",
                next_action="Revise the PRD",
                timestamp="2026-03-29T10:00:00+08:00",
            ),
        )

        with pytest.raises(InvalidTransitionError):
            transition_work_item(tmp_path, work_item, WorkItemStatus.GOVERNANCE_FROZEN)

        loaded = load_work_item(tmp_path, work_item.work_item_id)
        assert loaded.status == WorkItemStatus.INTAKE_CLASSIFIED

    def test_transition_work_item_denies_block_gate(
        self, tmp_path: Path
    ) -> None:
        work_item = _make_work_item()
        work_item.status = WorkItemStatus.GOVERNANCE_FROZEN
        save_work_item(tmp_path, work_item)

        save_reviewer_decision(
            tmp_path,
            work_item.work_item_id,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
                decision=PrdReviewerDecisionKind.BLOCK,
                target=work_item.work_item_id,
                reason="Docs baseline is blocked",
                next_action="Resolve the blocker",
                timestamp="2026-03-29T11:00:00+08:00",
            ),
        )

        with pytest.raises(InvalidTransitionError):
            transition_work_item(tmp_path, work_item, WorkItemStatus.DOCS_BASELINE)

        loaded = load_work_item(tmp_path, work_item.work_item_id)
        assert loaded.status == WorkItemStatus.GOVERNANCE_FROZEN

    def test_cross_stage_chain_persists_until_completed(self, tmp_path: Path) -> None:
        work_item = _make_work_item()
        save_work_item(tmp_path, work_item)

        save_reviewer_decision(
            tmp_path,
            work_item.work_item_id,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target=work_item.work_item_id,
                reason="Approved for governance freeze",
                next_action="Proceed",
                timestamp="2026-03-29T10:00:00+08:00",
            ),
        )
        save_reviewer_decision(
            tmp_path,
            work_item.work_item_id,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target=work_item.work_item_id,
                reason="Docs baseline is aligned",
                next_action="Proceed",
                timestamp="2026-03-29T11:00:00+08:00",
            ),
        )
        save_reviewer_decision(
            tmp_path,
            work_item.work_item_id,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target=work_item.work_item_id,
                reason="Ready to close",
                next_action="Proceed",
                timestamp="2026-03-29T12:00:00+08:00",
            ),
        )

        for target in (
            WorkItemStatus.INTAKE_CLASSIFIED,
            WorkItemStatus.GOVERNANCE_FROZEN,
            WorkItemStatus.DOCS_BASELINE,
            WorkItemStatus.DEV_EXECUTING,
            WorkItemStatus.DEV_VERIFYING,
            WorkItemStatus.DEV_REVIEWED,
            WorkItemStatus.ARCHIVING,
            WorkItemStatus.COMPLETED,
        ):
            work_item = transition_work_item(tmp_path, work_item, target)

        loaded = load_work_item(tmp_path, work_item.work_item_id)
        assert loaded.status == WorkItemStatus.COMPLETED
