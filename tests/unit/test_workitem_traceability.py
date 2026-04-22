"""Unit tests for workitem traceability JSON surfaces."""

from __future__ import annotations

from ai_sdlc.core.workitem_traceability import (
    CompletionTruthResult,
    WorkItemBranchLifecycleResult,
    _explicit_contract_lines,
)


def test_completion_truth_to_json_dict_deduplicates_blockers() -> None:
    payload = CompletionTruthResult(
        ok=False,
        blockers=["traceability blocker", "traceability blocker"],
    ).to_json_dict()

    assert payload["blockers"] == ["traceability blocker"]


def test_completion_truth_result_canonicalizes_runtime_blockers() -> None:
    result = CompletionTruthResult(
        ok=False,
        blockers=["traceability blocker", "traceability blocker"],
    )

    assert result.blockers == ["traceability blocker"]


def test_completion_truth_result_canonicalizes_runtime_batch_lists() -> None:
    result = CompletionTruthResult(
        ok=False,
        planned_batches=[1, 1, 2],
        executed_batches=[2, 2, 3],
    )

    assert result.planned_batches == [1, 2]
    assert result.executed_batches == [2, 3]


def test_completion_truth_to_json_dict_deduplicates_batch_lists() -> None:
    payload = CompletionTruthResult(
        ok=False,
        planned_batches=[1, 1, 2],
        executed_batches=[2, 2, 3],
    ).to_json_dict()

    assert payload["planned_batches"] == [1, 2]
    assert payload["executed_batches"] == [2, 3]


def test_branch_lifecycle_to_json_dict_deduplicates_lists() -> None:
    payload = WorkItemBranchLifecycleResult(
        ok=False,
        blockers=["lifecycle blocker", "lifecycle blocker"],
        warnings=["lifecycle warning", "lifecycle warning"],
        next_required_actions=["next action", "next action"],
    ).to_json_dict()

    assert payload["blockers"] == ["lifecycle blocker"]
    assert payload["warnings"] == ["lifecycle warning"]
    assert payload["next_required_actions"] == ["next action"]


def test_branch_lifecycle_result_canonicalizes_runtime_lists() -> None:
    result = WorkItemBranchLifecycleResult(
        ok=False,
        blockers=["lifecycle blocker", "lifecycle blocker"],
        warnings=["lifecycle warning", "lifecycle warning"],
        next_required_actions=["next action", "next action"],
    )

    assert result.blockers == ["lifecycle blocker"]
    assert result.warnings == ["lifecycle warning"]
    assert result.next_required_actions == ["next action"]


def test_branch_lifecycle_summary_detail_deduplicates_warnings() -> None:
    result = WorkItemBranchLifecycleResult(
        ok=False,
        warnings=["lifecycle warning", "lifecycle warning"],
    )

    assert result.summary_detail() == "lifecycle warning"


def test_explicit_contract_lines_deduplicate_repeated_lines() -> None:
    line = "- 执行状态校正：已按 contract 修正"

    assert _explicit_contract_lines(f"{line}\n{line}", f"{line}\n") == [line]
