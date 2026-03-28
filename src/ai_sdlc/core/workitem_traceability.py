"""Completion-truth traceability helpers for work item close-check."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

BATCH_SUMMARY_RE = re.compile(r"(?m)^\s*Batch\s+(?P<num>\d+)\s*[:：]")
BATCH_HEADER_RE = re.compile(r"(?m)^##\s+Batch\s+(?P<num>\d+)\b")
EXECUTION_HEADER_RE = re.compile(
    r"(?m)^###\s+Batch\s+(?P<stamp>\d{4}-\d{2}-\d{2}-(?P<seq>\d+))(?:\s*\|\s*(?P<label>.*))?$"
)
EXPLICIT_BATCH_RE = re.compile(r"\bBatch\s+(?P<start>\d+)(?:\s*[-~—]\s*(?P<end>\d+))?\b")
STATUS_CORRECTION_LINE_RE = re.compile(r"(?i)(?:执行)?状态校正|re[- ]?opened?|reopen")


@dataclass
class CompletionTruthResult:
    """Outcome of planned-vs-executed work item traceability checks."""

    ok: bool
    blockers: list[str] = field(default_factory=list)
    planned_batches: list[int] = field(default_factory=list)
    executed_batches: list[int] = field(default_factory=list)
    reopened_status_note: bool = False

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "blockers": self.blockers,
            "planned_batches": self.planned_batches,
            "executed_batches": self.executed_batches,
            "reopened_status_note": self.reopened_status_note,
        }


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
    return lines


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
