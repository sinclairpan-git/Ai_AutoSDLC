"""Unit tests for branch lifecycle inventory classification."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.branch_inventory import (
    BranchInventoryEntry,
    BranchLifecycleKind,
    classify_branch_kind,
    sort_branch_inventory,
)


def test_classify_branch_kind_covers_design_feature_scratch_archive_and_unmanaged() -> None:
    assert classify_branch_kind("design/007-demo") is BranchLifecycleKind.DESIGN
    assert classify_branch_kind("feature/007-demo") is BranchLifecycleKind.FEATURE
    assert classify_branch_kind("codex/007-demo") is BranchLifecycleKind.SCRATCH
    assert classify_branch_kind("backup-main-before-reset") is BranchLifecycleKind.ARCHIVE
    assert classify_branch_kind("legacy/topic") is BranchLifecycleKind.UNMANAGED


def test_sort_branch_inventory_is_stable_by_kind_then_name() -> None:
    entries = [
        BranchInventoryEntry(
            name="codex/z-demo",
            kind=BranchLifecycleKind.SCRATCH,
            head_commit="c3",
            is_current=False,
            upstream=None,
            worktree_path=None,
            ahead_of_main=0,
            behind_of_main=0,
        ),
        BranchInventoryEntry(
            name="design/007-demo",
            kind=BranchLifecycleKind.DESIGN,
            head_commit="a1",
            is_current=False,
            upstream=None,
            worktree_path=None,
            ahead_of_main=0,
            behind_of_main=0,
        ),
        BranchInventoryEntry(
            name="feature/007-demo",
            kind=BranchLifecycleKind.FEATURE,
            head_commit="b2",
            is_current=False,
            upstream=None,
            worktree_path=Path("/tmp/feature-demo"),
            ahead_of_main=1,
            behind_of_main=0,
        ),
        BranchInventoryEntry(
            name="backup-main-before-reset",
            kind=BranchLifecycleKind.ARCHIVE,
            head_commit="d4",
            is_current=False,
            upstream=None,
            worktree_path=None,
            ahead_of_main=0,
            behind_of_main=4,
        ),
    ]

    sorted_entries = sort_branch_inventory(entries)

    assert [item.name for item in sorted_entries] == [
        "design/007-demo",
        "feature/007-demo",
        "codex/z-demo",
        "backup-main-before-reset",
    ]


def test_branch_inventory_entry_exposes_machine_readable_dict() -> None:
    entry = BranchInventoryEntry(
        name="codex/007-demo",
        kind=BranchLifecycleKind.SCRATCH,
        head_commit="abc1234",
        is_current=False,
        upstream=None,
        worktree_path=Path("/tmp/codex-007-demo"),
        ahead_of_main=3,
        behind_of_main=12,
    )

    assert entry.to_json_dict() == {
        "name": "codex/007-demo",
        "kind": "scratch",
        "head_commit": "abc1234",
        "is_current": False,
        "upstream": None,
        "worktree_path": "/tmp/codex-007-demo",
        "ahead_of_main": 3,
        "behind_of_main": 12,
    }
