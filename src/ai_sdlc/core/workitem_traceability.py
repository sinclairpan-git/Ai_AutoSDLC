"""Completion-truth traceability helpers for work item close-check."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.branch.git_client import GitClient
from ai_sdlc.core.branch_inventory import BranchInventoryEntry, build_branch_inventory

BATCH_SUMMARY_RE = re.compile(r"(?m)^\s*Batch\s+(?P<num>\d+)\s*[:：]")
BATCH_HEADER_RE = re.compile(r"(?m)^##\s+Batch\s+(?P<num>\d+)\b")
EXECUTION_HEADER_RE = re.compile(
    r"(?m)^###\s+Batch\s+(?P<stamp>\d{4}-\d{2}-\d{2}-(?P<seq>\d+))(?:\s*\|\s*(?P<label>.*))?$"
)
EXPLICIT_BATCH_RE = re.compile(r"\bBatch\s+(?P<start>\d+)(?:\s*[-~—]\s*(?P<end>\d+))?\b")
STATUS_CORRECTION_LINE_RE = re.compile(r"(?i)(?:执行)?状态校正|re[- ]?opened?|reopen")
BRANCH_PLAN_DISPOSITION_RE = re.compile(
    r"(?m)^\s*-\s*关联 branch/worktree disposition 计划：(?P<value>.+?)\s*$"
)
BRANCH_STATUS_DISPOSITION_RE = re.compile(
    r"(?m)^\s*-\s*当前批次 branch disposition 状态：(?P<value>.+?)\s*$"
)
WORKTREE_STATUS_DISPOSITION_RE = re.compile(
    r"(?m)^\s*-\s*当前批次 worktree disposition 状态：(?P<value>.+?)\s*$"
)
WI_SEQ_RE = re.compile(r"^(?P<seq>\d{3})\b")


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _dedupe_int_items(values: object) -> list[int]:
    deduped: list[int] = []
    for value in values or []:
        normalized = int(value)
        if normalized not in deduped:
            deduped.append(normalized)
    return deduped


@dataclass
class CompletionTruthResult:
    """Outcome of planned-vs-executed work item traceability checks."""

    ok: bool
    blockers: list[str] = field(default_factory=list)
    planned_batches: list[int] = field(default_factory=list)
    executed_batches: list[int] = field(default_factory=list)
    reopened_status_note: bool = False

    def __post_init__(self) -> None:
        self.blockers = _dedupe_text_items(self.blockers)
        self.planned_batches = _dedupe_int_items(self.planned_batches)
        self.executed_batches = _dedupe_int_items(self.executed_batches)

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "blockers": _dedupe_text_items(self.blockers),
            "planned_batches": _dedupe_int_items(self.planned_batches),
            "executed_batches": _dedupe_int_items(self.executed_batches),
            "reopened_status_note": self.reopened_status_note,
        }


@dataclass(frozen=True, slots=True)
class BranchDispositionTruth:
    """Execution-log close-out disposition markers for the latest batch."""

    plan: str | None
    branch_status: str | None
    worktree_status: str | None

    @property
    def effective_branch_status(self) -> str | None:
        return self.branch_status or self.plan


@dataclass(frozen=True, slots=True)
class WorkItemBranchLifecycleEntry:
    """One associated branch/worktree finding for a work item."""

    name: str
    kind: str
    ahead_of_main: int
    behind_of_main: int
    worktree_path: str | None
    branch_disposition: str | None
    worktree_disposition: str | None
    status: str
    detail: str

    def to_json_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "kind": self.kind,
            "ahead_of_main": self.ahead_of_main,
            "behind_of_main": self.behind_of_main,
            "worktree_path": self.worktree_path,
            "branch_disposition": self.branch_disposition,
            "worktree_disposition": self.worktree_disposition,
            "status": self.status,
            "detail": self.detail,
        }


@dataclass
class WorkItemBranchLifecycleResult:
    """Read-only lifecycle assessment for branches/worktrees associated with one WI."""

    ok: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    entries: list[WorkItemBranchLifecycleEntry] = field(default_factory=list)
    branch_disposition: str | None = None
    worktree_disposition: str | None = None
    next_required_actions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.blockers = _dedupe_text_items(self.blockers)
        self.warnings = _dedupe_text_items(self.warnings)
        self.next_required_actions = _dedupe_text_items(self.next_required_actions)

    def summary_detail(self) -> str:
        if self.blockers:
            return "; ".join(_dedupe_text_items(self.blockers))
        if self.warnings:
            return "; ".join(_dedupe_text_items(self.warnings))
        if self.entries:
            return (
                "associated branch/worktree disposition resolved: "
                f"{self.branch_disposition or 'unknown'}"
            )
        return "no associated branch/worktree drift"

    def to_json_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "blockers": _dedupe_text_items(self.blockers),
            "warnings": _dedupe_text_items(self.warnings),
            "branch_disposition": self.branch_disposition,
            "worktree_disposition": self.worktree_disposition,
            "next_required_actions": _dedupe_text_items(self.next_required_actions),
            "entries": [item.to_json_dict() for item in self.entries],
        }


def _branch_lifecycle_next_actions(
    *,
    entries: list[WorkItemBranchLifecycleEntry],
    branch_disposition: str | None,
    worktree_disposition: str | None,
) -> list[str]:
    actions: list[str] = []
    unresolved_disposition = branch_disposition in {None, "", "待最终收口"}

    for entry in entries:
        if unresolved_disposition:
            actions.append(
                f"decide whether {entry.name} should be merged, deleted, or archived, then record that branch disposition in task-execution-log.md"
            )
        if entry.branch_disposition == "merged" and entry.ahead_of_main > 0:
            actions.append(
                f"merge {entry.name} into main or correct the branch disposition marker from merged"
            )
        if entry.branch_disposition == "deleted":
            actions.append(
                f"delete local branch {entry.name} or correct the branch disposition marker from deleted"
            )
        if entry.worktree_path is not None and worktree_disposition == "removed":
            actions.append(
                f"remove stale worktree {entry.worktree_path} or correct the worktree disposition marker from removed"
            )

    deduped: list[str] = []
    for action in actions:
        if action not in deduped:
            deduped.append(action)
    return deduped


def _unique_preserve_order(values: list[int]) -> list[int]:
    seen: set[int] = set()
    ordered: list[int] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _expand_explicit_batches(text: str) -> list[int]:
    batches: list[int] = []
    for match in EXPLICIT_BATCH_RE.finditer(text):
        start = int(match.group("start"))
        end_group = match.group("end")
        if end_group is None:
            batches.append(start)
            continue
        end = int(end_group)
        lo, hi = sorted((start, end))
        batches.extend(range(lo, hi + 1))
    return _unique_preserve_order(batches)


def _explicit_contract_lines(*texts: str) -> list[str]:
    lines: list[str] = []
    for text in texts:
        if not text:
            continue
        for line in text.splitlines():
            if STATUS_CORRECTION_LINE_RE.search(line):
                lines.append(line)
    return _dedupe_text_items(lines)


def _completion_truth_contract_enabled(tasks_text: str, log_text: str) -> bool:
    return len(_explicit_contract_lines(tasks_text, log_text)) > 0


def extract_planned_batches(tasks_text: str) -> list[int]:
    """Extract planned batch numbers from tasks.md."""
    batches = [int(m.group("num")) for m in BATCH_SUMMARY_RE.finditer(tasks_text)]
    batches.extend(int(m.group("num")) for m in BATCH_HEADER_RE.finditer(tasks_text))
    return _unique_preserve_order(batches)


def extract_execution_batches(log_text: str) -> list[int]:
    """Extract execution batch coverage from task-execution-log.md."""
    batches: list[int] = []
    for line in log_text.splitlines():
        match = EXECUTION_HEADER_RE.match(line.strip())
        if not match:
            continue
        label = match.group("label") or ""
        explicit_batches = _expand_explicit_batches(label)
        if explicit_batches:
            batches.extend(explicit_batches)
    return _unique_preserve_order(batches)


def _has_reopened_status_note(*texts: str) -> bool:
    return len(_explicit_contract_lines(*texts)) > 0


def _latest_batch_text(log_text: str) -> str:
    matches = list(re.finditer(r"(?m)^### Batch .+$", log_text))
    if not matches:
        return log_text
    return log_text[matches[-1].start() :]


def _normalize_marker_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.replace("`", "").strip()
    return normalized or None


def _last_marker(pattern: re.Pattern[str], text: str) -> str | None:
    matches = list(pattern.finditer(text))
    if not matches:
        return None
    return _normalize_marker_value(matches[-1].group("value"))


def parse_branch_disposition_truth(log_text: str) -> BranchDispositionTruth:
    """Parse latest-batch branch/worktree disposition markers from execution log."""
    batch_text = _latest_batch_text(log_text)
    return BranchDispositionTruth(
        plan=_last_marker(BRANCH_PLAN_DISPOSITION_RE, batch_text),
        branch_status=_last_marker(BRANCH_STATUS_DISPOSITION_RE, batch_text),
        worktree_status=_last_marker(WORKTREE_STATUS_DISPOSITION_RE, batch_text),
    )


def _work_item_seq(wi_name: str) -> str | None:
    match = WI_SEQ_RE.match(wi_name)
    if match is None:
        return None
    return match.group("seq")


def branch_matches_work_item(branch_name: str, wi_name: str) -> bool:
    """Return whether a branch name is explicitly associated with a work item."""
    lowered_branch = branch_name.lower()
    lowered_wi = wi_name.lower()
    if lowered_wi in lowered_branch:
        return True

    seq = _work_item_seq(wi_name)
    if seq is None:
        return False
    return re.search(rf"(^|/){re.escape(seq)}(?:[-/].*|$)", branch_name) is not None


def analyze_work_item_branch_lifecycle(
    *,
    inventory: tuple[BranchInventoryEntry, ...],
    wi_name: str,
    log_text: str | None,
) -> WorkItemBranchLifecycleResult:
    """Evaluate unresolved associated branch/worktree drift for one work item."""
    disposition = (
        parse_branch_disposition_truth(log_text) if log_text is not None else BranchDispositionTruth(None, None, None)
    )
    branch_disposition = disposition.effective_branch_status
    worktree_disposition = disposition.worktree_status

    associated = [entry for entry in inventory if branch_matches_work_item(entry.name, wi_name)]
    entries: list[WorkItemBranchLifecycleEntry] = []
    blockers: list[str] = []
    warnings: list[str] = []

    if not associated:
        return WorkItemBranchLifecycleResult(
            ok=True,
            blockers=[],
            warnings=[],
            entries=[],
            branch_disposition=branch_disposition,
            worktree_disposition=worktree_disposition,
            next_required_actions=[],
        )

    for entry in associated:
        status = "ok"
        detail = (
            f"{entry.name} associated with {wi_name}; "
            f"ahead_of_main={entry.ahead_of_main}; disposition={branch_disposition or 'unknown'}"
        )
        worktree_note = ""
        if entry.worktree_path is not None:
            worktree_note = f"; worktree={entry.worktree_path}"

        if branch_disposition in {None, "", "待最终收口"}:
            if entry.ahead_of_main > 0:
                status = "blocker"
                detail = (
                    f"{entry.name} is associated with {wi_name}, ahead of main by "
                    f"{entry.ahead_of_main} commit(s), and branch disposition is unresolved"
                    f"{worktree_note}"
                )
                blockers.append(f"BLOCKER: branch lifecycle unresolved: {detail}")
            else:
                status = "warning"
                detail = (
                    f"{entry.name} is associated with {wi_name} but branch disposition is unresolved"
                    f"{worktree_note}"
                )
                warnings.append(f"WARNING: {detail}")
        elif branch_disposition == "merged":
            if entry.ahead_of_main > 0:
                status = "blocker"
                detail = (
                    f"{entry.name} is marked merged but still ahead of main by "
                    f"{entry.ahead_of_main} commit(s){worktree_note}"
                )
                blockers.append(f"BLOCKER: branch lifecycle inconsistent: {detail}")
        elif branch_disposition == "deleted":
            status = "blocker"
            detail = f"{entry.name} is marked deleted but still present in local inventory{worktree_note}"
            blockers.append(f"BLOCKER: branch lifecycle inconsistent: {detail}")
        elif branch_disposition == "archived":
            detail = f"{entry.name} archived as non-mainline truth carrier{worktree_note}"

        if entry.worktree_path is not None and worktree_disposition == "removed":
            status = "blocker"
            detail = (
                f"{entry.name} worktree is marked removed but still present at {entry.worktree_path}"
            )
            blockers.append(f"BLOCKER: branch lifecycle inconsistent: {detail}")

        entries.append(
            WorkItemBranchLifecycleEntry(
                name=entry.name,
                kind=entry.kind.value,
                ahead_of_main=entry.ahead_of_main,
                behind_of_main=entry.behind_of_main,
                worktree_path=str(entry.worktree_path) if entry.worktree_path else None,
                branch_disposition=branch_disposition,
                worktree_disposition=worktree_disposition,
                status=status,
                detail=detail,
            )
        )

    return WorkItemBranchLifecycleResult(
        ok=len(blockers) == 0,
        blockers=blockers,
        warnings=warnings,
        entries=entries,
        branch_disposition=branch_disposition,
        worktree_disposition=worktree_disposition,
        next_required_actions=_branch_lifecycle_next_actions(
            entries=entries,
            branch_disposition=branch_disposition,
            worktree_disposition=worktree_disposition,
        ),
    )


def evaluate_work_item_branch_lifecycle(
    *,
    root: Path,
    wi_dir: Path,
    log_text: str | None,
) -> WorkItemBranchLifecycleResult:
    """Build inventory from Git and evaluate associated branch lifecycle for one WI."""
    inventory = build_branch_inventory(GitClient(root))
    return analyze_work_item_branch_lifecycle(
        inventory=inventory,
        wi_name=wi_dir.name,
        log_text=log_text,
    )


def analyze_completion_truth(tasks_text: str, log_text: str) -> CompletionTruthResult:
    """Compare planned work against execution evidence and report blockers."""
    if not _completion_truth_contract_enabled(tasks_text, log_text):
        return CompletionTruthResult(
            ok=True,
            blockers=[],
            planned_batches=extract_planned_batches(tasks_text),
            executed_batches=extract_execution_batches(log_text),
            reopened_status_note=False,
        )

    planned_batches = extract_planned_batches(tasks_text)
    executed_batches = extract_execution_batches(log_text)

    blockers: list[str] = []

    if planned_batches:
        missing_batches = [batch for batch in planned_batches if batch not in executed_batches]
        if missing_batches:
            blockers.append(
                "BLOCKER: planned batch coverage incomplete; missing execution evidence for "
                + ", ".join(f"Batch {batch}" for batch in missing_batches)
            )

    reopened_status_note = _has_reopened_status_note(tasks_text, log_text)
    if reopened_status_note:
        blockers.append(
            "BLOCKER: reopened status note found in tasks.md or task-execution-log.md; "
            "close-out is not final."
        )

    return CompletionTruthResult(
        ok=len(blockers) == 0,
        blockers=blockers,
        planned_batches=planned_batches,
        executed_batches=executed_batches,
        reopened_status_note=reopened_status_note,
    )


__all__ = [
    "BranchDispositionTruth",
    "CompletionTruthResult",
    "WorkItemBranchLifecycleEntry",
    "WorkItemBranchLifecycleResult",
    "analyze_completion_truth",
    "analyze_work_item_branch_lifecycle",
    "branch_matches_work_item",
    "evaluate_work_item_branch_lifecycle",
    "extract_execution_batches",
    "extract_planned_batches",
    "parse_branch_disposition_truth",
]
