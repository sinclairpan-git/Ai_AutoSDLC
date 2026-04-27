"""Read-only branch/worktree lifecycle inventory helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ai_sdlc.branch.git_client import GitClient


class BranchLifecycleKind(str, Enum):
    """Lifecycle classification for local branches/worktrees."""

    DESIGN = "design"
    FEATURE = "feature"
    SCRATCH = "scratch"
    ARCHIVE = "archive"
    UNMANAGED = "unmanaged"


@dataclass(frozen=True, slots=True)
class BranchInventoryEntry:
    """Machine-readable read-only branch inventory entry."""

    name: str
    kind: BranchLifecycleKind
    head_commit: str
    is_current: bool
    upstream: str | None
    worktree_path: Path | None
    ahead_of_main: int
    behind_of_main: int

    def to_json_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind.value,
            "head_commit": self.head_commit,
            "is_current": self.is_current,
            "upstream": self.upstream,
            "worktree_path": (
                self.worktree_path.as_posix() if self.worktree_path else None
            ),
            "ahead_of_main": self.ahead_of_main,
            "behind_of_main": self.behind_of_main,
        }


_KIND_ORDER = {
    BranchLifecycleKind.DESIGN: 0,
    BranchLifecycleKind.FEATURE: 1,
    BranchLifecycleKind.SCRATCH: 2,
    BranchLifecycleKind.ARCHIVE: 3,
    BranchLifecycleKind.UNMANAGED: 4,
}


def classify_branch_kind(name: str) -> BranchLifecycleKind:
    """Classify one branch name into the frozen lifecycle kinds."""
    if name.startswith("design/"):
        return BranchLifecycleKind.DESIGN
    if name.startswith("feature/"):
        return BranchLifecycleKind.FEATURE
    if name.startswith("codex/") or name.startswith("scratch/"):
        return BranchLifecycleKind.SCRATCH

    lowered = name.lower()
    if (
        lowered.startswith("backup")
        or lowered.startswith("archive/")
        or "archive" in lowered
        or "backup" in lowered
    ):
        return BranchLifecycleKind.ARCHIVE
    return BranchLifecycleKind.UNMANAGED


def sort_branch_inventory(
    entries: list[BranchInventoryEntry] | tuple[BranchInventoryEntry, ...],
) -> list[BranchInventoryEntry]:
    """Return branch inventory in a stable order for snapshot tests."""
    return sorted(entries, key=lambda item: (_KIND_ORDER[item.kind], item.name))


def build_branch_inventory(
    git: GitClient,
    *,
    base: str | None = None,
) -> tuple[BranchInventoryEntry, ...]:
    """Build a lifecycle-aware inventory from local branches."""
    entries: list[BranchInventoryEntry] = []
    for branch in git.list_local_branches():
        divergence = git.branch_divergence(branch.name, base=base)
        entries.append(
            BranchInventoryEntry(
                name=branch.name,
                kind=classify_branch_kind(branch.name),
                head_commit=branch.head_commit,
                is_current=branch.is_current,
                upstream=branch.upstream,
                worktree_path=branch.worktree_path,
                ahead_of_main=divergence.ahead_of_base,
                behind_of_main=divergence.behind_base,
            )
        )
    return tuple(sort_branch_inventory(entries))


__all__ = [
    "BranchInventoryEntry",
    "BranchLifecycleKind",
    "build_branch_inventory",
    "classify_branch_kind",
    "sort_branch_inventory",
]
