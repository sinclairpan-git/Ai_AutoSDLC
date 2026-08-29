from __future__ import annotations

from importlib import import_module
from typing import Any

import pytest

from ai_sdlc.core.loop_models import LoopStatus, LoopType
from ai_sdlc.core.loop_status import (
    LoopStatusCommandStatus,
    LoopStatusResult,
    LoopSummary,
)


def _build_summary(**kwargs: Any) -> Any:
    try:
        module = import_module("ai_sdlc.cli.default_summary")
    except ModuleNotFoundError:
        pytest.fail("default summary projection is missing")
    builder = getattr(module, "build_default_summary", None)
    assert callable(builder), "default summary projection builder is missing"
    return builder(**kwargs)


def _active_loop(
    loop_type: LoopType,
    loop_id: str,
    *,
    next_action: str = "",
) -> LoopStatusResult:
    return LoopStatusResult(
        status=LoopStatusCommandStatus.READY,
        result="Current loop is available.",
        current_loop=LoopSummary(
            loop_id=loop_id,
            loop_type=loop_type,
            status=LoopStatus.RUNNING,
            is_current=True,
            next_action=next_action,
        ),
    )


def test_default_summary_falls_back_to_pipeline_when_no_loop_is_current() -> None:
    summary = _build_summary(
        checkpoint_stage="execute",
        result="completed",
        loop_statuses=(
            LoopStatusResult(
                status=LoopStatusCommandStatus.NO_CURRENT,
                result="No current loop.",
            ),
        ),
    )

    assert summary.current_loop == "pipeline/execute"
    assert summary.result == "completed"
    assert summary.next_action is None


def test_default_summary_uses_the_single_current_loop_and_its_next_action() -> None:
    summary = _build_summary(
        checkpoint_stage="verify",
        result="needs_review",
        loop_statuses=(
            _active_loop(
                LoopType.IMPLEMENTATION,
                "impl-1",
                next_action="Run implementation review.",
            ),
        ),
    )

    assert summary.current_loop == "implementation/impl-1 (running)"
    assert summary.next_action == "Run implementation review."


def test_default_summary_fails_closed_for_multiple_current_loops() -> None:
    summary = _build_summary(
        checkpoint_stage="execute",
        result="blocked",
        loop_statuses=(
            _active_loop(LoopType.REQUIREMENT, "req-1"),
            _active_loop(LoopType.IMPLEMENTATION, "impl-1"),
        ),
    )

    assert summary.current_loop == "ambiguous"
    assert any("Multiple current loops" in item for item in summary.blockers)


def test_default_summary_fails_closed_for_malformed_loop_pointer() -> None:
    summary = _build_summary(
        checkpoint_stage="execute",
        result="blocked",
        loop_statuses=(
            LoopStatusResult(
                status=LoopStatusCommandStatus.BLOCKED,
                result="Current loop pointer is malformed.",
                blocker="Current implementation pointer is malformed.",
                next_action="Rerun ai-sdlc loop implementation start.",
            ),
        ),
    )

    assert summary.current_loop == "blocked"
    assert summary.blockers == ("Current implementation pointer is malformed.",)
    assert summary.next_action == "Rerun ai-sdlc loop implementation start."


def test_default_summary_uses_status_surface_workitem_action_before_loop() -> None:
    summary = _build_summary(
        checkpoint_stage="execute",
        result="blocked",
        loop_statuses=(
            _active_loop(
                LoopType.IMPLEMENTATION,
                "impl-1",
                next_action="Run implementation review.",
            ),
        ),
        status_surface={
            "workitem_diagnostics": {
                "next_required_action": "Continue T43 exact-head remediation.",
            }
        },
    )

    assert summary.next_action == "Continue T43 exact-head remediation."


def test_default_summary_falls_back_to_branch_lifecycle_action() -> None:
    summary = _build_summary(
        checkpoint_stage="close",
        result="ready",
        status_surface={
            "workitem_diagnostics": {"next_required_action": ""},
            "branch_lifecycle": {
                "next_required_action": "Record the branch disposition.",
            },
        },
    )

    assert summary.next_action == "Record the branch disposition."


def test_default_summary_bounds_next_blockers_and_rules() -> None:
    summary = _build_summary(
        checkpoint_stage="execute",
        result="open_gates",
        loop_statuses=(
            _active_loop(
                LoopType.IMPLEMENTATION,
                "impl-1",
                next_action="Loop next.",
            ),
        ),
        primary_next_actions=("Fix the current gate.", "Ignored explicit action."),
        workitem_next_actions=("Continue T11.",),
        blockers=("gate-a", "gate-a", "gate-b", "gate-c", "gate-d"),
        applicable_rules=("pipeline — Pipeline", "tdd — TDD", "debugging — Debugging"),
    )

    assert summary.next_action == "Fix the current gate."
    assert summary.blockers == ("gate-a", "gate-b", "gate-c")
    assert summary.applicable_rules == ("pipeline — Pipeline", "tdd — TDD")


def test_default_summary_only_promotes_explicitly_blocking_status_items() -> None:
    summary = _build_summary(
        checkpoint_stage="verify",
        result="blocked",
        status_surface={
            "workitem_diagnostics": {
                "items": [
                    {"blocking": False, "detail": "advisory only"},
                    {"blocking": True, "detail": "task evidence is missing"},
                ]
            }
        },
    )

    assert summary.blockers == ("task evidence is missing",)
