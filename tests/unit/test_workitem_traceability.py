"""Unit tests for workitem traceability JSON surfaces."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core.branch_inventory import BranchInventoryEntry, BranchLifecycleKind
from ai_sdlc.core.workitem_traceability import (
    CompletionTruthResult,
    WorkItemBranchLifecycleResult,
    _explicit_contract_lines,
    analyze_work_item_branch_lifecycle,
)


def _branch_entry(
    name: str = "feature/001-wi",
    *,
    kind: BranchLifecycleKind = BranchLifecycleKind.FEATURE,
    current: bool = True,
    worktree: bool = True,
    ahead: int = 1,
    behind: int = 0,
) -> BranchInventoryEntry:
    return BranchInventoryEntry(
        name=name,
        kind=kind,
        head_commit="a" * 40,
        is_current=current,
        upstream=None,
        worktree_path=Path("/tmp/001-wi") if worktree else None,
        ahead_of_main=ahead,
        behind_of_main=behind,
    )


def _disposition_log(branch: str, worktree: str | None = None) -> str:
    lines = [
        "### Batch 2026-07-15-001 | lifecycle",
        f"- 当前批次 branch disposition 状态：`{branch}`",
    ]
    if worktree is not None:
        lines.append(f"- 当前批次 worktree disposition 状态：`{worktree}`")
    return "\n".join(lines)


def _analyze(
    branch: str,
    entries: tuple[BranchInventoryEntry, ...],
    *,
    worktree: str | None = None,
    final: bool = False,
) -> WorkItemBranchLifecycleResult:
    return analyze_work_item_branch_lifecycle(
        inventory=entries,
        wi_name="001-wi",
        log_text=_disposition_log(branch, worktree),
        _require_final_branch_disposition=final,
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


def test_merge_pending_accepts_only_unique_current_cleanly_ahead_worktree() -> None:
    result = _analyze(
        "merge-pending",
        (_branch_entry(),),
        worktree="retained(PR #128 review)",
    )

    assert result.ok is True


@pytest.mark.parametrize(
    "entries",
    [
        (),
        (_branch_entry(), _branch_entry("feature/001-wi-scratch")),
        (_branch_entry(ahead=0),),
        (_branch_entry(behind=1),),
        (_branch_entry(current=False),),
        (_branch_entry(worktree=False),),
    ],
)
def test_merge_pending_rejects_inventory_mismatch(entries: tuple[BranchInventoryEntry, ...]) -> None:
    result = _analyze("merge-pending", entries)

    assert result.ok is False
    assert result.blockers


def test_merge_pending_never_satisfies_final_close() -> None:
    result = _analyze(
        "merge-pending",
        (_branch_entry(),),
        worktree="retained(PR #128 review)",
        final=True,
    )

    assert result.ok is False
    assert any("merge-pending" in blocker for blocker in result.blockers)


@pytest.mark.parametrize("branch", ["PR merge carrier", "retained", "Merged", "archived"])
def test_unknown_branch_disposition_fails_closed(branch: str) -> None:
    result = _analyze(branch, (_branch_entry(),))

    assert result.ok is False
    assert any("invalid" in blocker for blocker in result.blockers)
    assert all(blocker.startswith("BLOCKER: branch lifecycle ") for blocker in result.blockers)


@pytest.mark.parametrize(
    ("branch", "entries", "worktree", "expected_ok"),
    [
        ("merged", (_branch_entry(ahead=0, worktree=False),), "removed", True),
        ("merged", (), "removed", False),
        ("merged", (_branch_entry(ahead=0, worktree=False), _branch_entry("feature/001-wi-dev", ahead=0, worktree=False)), "removed", False),
        ("deleted", (), "removed", True),
        ("deleted", (_branch_entry(worktree=False),), "removed", False),
        ("archived(non-mainline evidence)", (_branch_entry(name="archive/001-wi", kind=BranchLifecycleKind.ARCHIVE, current=False, worktree=False),), "removed", True),
        ("archived(non-mainline evidence)", (_branch_entry(current=False, worktree=False),), "removed", False),
    ],
)
def test_final_branch_disposition_requires_bidirectional_git_truth(branch: str, entries: tuple[BranchInventoryEntry, ...], worktree: str, expected_ok: bool) -> None:
    result = _analyze(branch, entries, worktree=worktree, final=True)

    assert result.ok is expected_ok


@pytest.mark.parametrize(
    ("entry", "worktree", "expected_ok"),
    [
        (_branch_entry(ahead=0), "retained(close evidence)", True),
        (_branch_entry(ahead=0), None, False),
        (_branch_entry(ahead=0), "待最终收口", False),
        (_branch_entry(ahead=0), "removed", False),
        (_branch_entry(ahead=0, worktree=False), "removed", True),
        (_branch_entry(ahead=0, worktree=False), "retained(close evidence)", False),
        (_branch_entry(ahead=0), "retained", False),
    ],
)
def test_final_worktree_disposition_requires_bidirectional_inventory_truth(
    entry: BranchInventoryEntry,
    worktree: str | None,
    expected_ok: bool,
) -> None:
    result = _analyze("merged", (entry,), worktree=worktree, final=True)

    assert result.ok is expected_ok
