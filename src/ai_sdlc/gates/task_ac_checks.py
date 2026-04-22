"""Task-level checks shared by decompose / execute / verify gates.

Rules match ``DecomposeGate`` check ``task_acceptance_present``: each ``### Task`` block
must include 「验收标准」, a standalone ``AC`` token, or 「验证」.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.generators.doc_gen import TasksParser

_TASK_SPLIT_RE = re.compile(r"(?m)^###\s+Task\s+")
_TASK_ID_RE = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)")
_DOC_FIRST_MARKERS = (
    "仅文档",
    "仅需求",
    "仅需求沉淀",
    "先 spec-plan-tasks",
    "先spec-plan-tasks",
)
_PATH_RE = re.compile(r"(?:src|tests)/[^\s`'\"),，；]+")


@dataclass(frozen=True, slots=True)
class TaskBlock:
    """A parsed markdown task block with both human and runtime identifiers."""

    task_id: str
    runtime_task_id: str
    block: str


def _dedupe_text_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def _iter_task_blocks(tasks_md: str) -> list[TaskBlock]:
    blocks: list[TaskBlock] = []
    parts = _TASK_SPLIT_RE.split(tasks_md)
    for part in parts[1:]:
        m = _TASK_ID_RE.match(part.strip())
        if not m:
            continue
        task_id = f"{m.group('major')}.{m.group('minor')}"
        runtime_task_id = f"T{m.group('major')}{m.group('minor')}"
        blocks.append(TaskBlock(task_id=task_id, runtime_task_id=runtime_task_id, block=part))
    return blocks


def _matches_task_ref(block: TaskBlock, task_ref: str) -> bool:
    norm = task_ref.strip()
    return norm in {
        block.task_id,
        block.runtime_task_id,
        f"Task {block.task_id}",
    }


def _is_doc_first_block(block: str) -> bool:
    header = block.splitlines()[0] if block.splitlines() else block
    return any(marker in header for marker in _DOC_FIRST_MARKERS)


def _is_forbidden_execute_path(path: str) -> bool:
    cleaned = path.strip().strip("`'\"").rstrip(".,);，；")
    if cleaned.startswith("tests/"):
        return True
    if not cleaned.startswith("src/"):
        return False
    suffixes = Path(cleaned).suffixes
    if not suffixes:
        return False
    return ".md" not in suffixes


def _forbidden_paths(text: str) -> list[str]:
    paths: list[str] = []
    for raw in _PATH_RE.findall(text):
        if _is_forbidden_execute_path(raw):
            cleaned = raw.strip().strip("`'\"").rstrip(".,);，；")
            if cleaned not in paths:
                paths.append(cleaned)
    return paths


def first_task_missing_acceptance(tasks_md: str) -> str | None:
    """Return the first Task id missing acceptance markers, else ``None``."""
    for parsed in _iter_task_blocks(tasks_md):
        task_id = parsed.task_id
        block = parsed.block

        has_acceptance = (
            "验收标准" in block
            or re.search(r"(?m)\bAC\b", block) is not None
            or "验证" in block
        )
        if not has_acceptance:
            return task_id
    return None


def first_doc_first_task_scope_violation(tasks_md: str) -> tuple[str, str] | None:
    """Return the first doc-first task pointing at forbidden code/test paths."""
    for parsed in _iter_task_blocks(tasks_md):
        if not _is_doc_first_block(parsed.block):
            continue
        forbidden = _forbidden_paths(parsed.block)
        if forbidden:
            return (parsed.task_id, forbidden[0])
    return None


def doc_first_execute_blocker(
    tasks_md: str,
    *,
    task_ref: str,
    touched_paths: tuple[str, ...] = (),
) -> str | None:
    """Return a blocking message when a targeted task must stay in design/decompose."""
    for parsed in _iter_task_blocks(tasks_md):
        if not _matches_task_ref(parsed, task_ref):
            continue
        if not _is_doc_first_block(parsed.block):
            return None
        forbidden = [path for path in touched_paths if _is_forbidden_execute_path(path)]
        if forbidden:
            sample = ", ".join(_dedupe_text_items(forbidden)[:3])
            return (
                f"Task {parsed.task_id} is doc-first/design-decompose-only; "
                f"update spec.md / plan.md / tasks.md before execute. "
                f"Forbidden touched paths: {sample}"
            )
        return (
            f"Task {parsed.task_id} is doc-first/design-decompose-only; "
            "route the work through design/decompose and keep execute away from "
            "non-Markdown src/ code and tests/ paths until the docs are landed."
        )
    return None


def next_pending_task_ref(
    tasks_path: Path,
    *,
    current_batch: int = 0,
    last_committed_task: str = "",
) -> str | None:
    """Return the next task runtime id implied by current batch progress."""
    plan = TasksParser().parse(tasks_path)
    if not plan.batches:
        return None

    batch_index = current_batch if 0 <= current_batch < len(plan.batches) else 0
    batches = plan.batches[batch_index:]
    first = True
    for batch in batches:
        task_ids = list(batch.tasks)
        if first and last_committed_task and last_committed_task in task_ids:
            start = task_ids.index(last_committed_task) + 1
            task_ids = task_ids[start:]
        if task_ids:
            return task_ids[0]
        first = False
    return None
