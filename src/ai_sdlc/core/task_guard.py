"""Task-bound code execution guard."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.executable_task import (
    ExecutableTask,
    first_executable_task,
    parse_executable_tasks,
)
from ai_sdlc.core.task_preparation import (
    MinimalTaskCandidate,
    build_minimal_task_candidate,
    minimal_formal_doc_actions,
)
from ai_sdlc.models.state import Checkpoint

ALLOW_CODE_WITH_TASK = "ALLOW_CODE_WITH_TASK"
BLOCK_CODE_PREPARE_TASKS = "BLOCK_CODE_PREPARE_TASKS"

COMPANION_CATEGORIES = frozenset(
    {"product", "test", "doc", "snapshot", "migration", "config", "generated"}
)


def _dedupe(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in values if item))


@dataclass(frozen=True, slots=True)
class TaskGuardResult:
    """Preflight result for code modification authorization."""

    state: str
    allowed: bool
    detail: str
    active_work_item: str | None = None
    task_id: str | None = None
    task_title: str | None = None
    task_goal: str | None = None
    tasks_path: str | None = None
    next_actions: tuple[str, ...] = ()
    preparation_candidate: MinimalTaskCandidate | None = None
    errors: tuple[str, ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "state": self.state,
            "allowed": self.allowed,
            "detail": self.detail,
            "active_work_item": self.active_work_item,
            "task_id": self.task_id,
            "task_title": self.task_title,
            "task_goal": self.task_goal,
            "tasks_path": self.tasks_path,
            "next_actions": list(self.next_actions),
            "errors": list(self.errors),
        }
        if self.preparation_candidate is not None:
            payload["preparation_candidate"] = {
                "work_item_id": self.preparation_candidate.work_item_id,
                "task_id": self.preparation_candidate.task_id,
                "title": self.preparation_candidate.title,
                "goal": self.preparation_candidate.goal,
                "scope": list(self.preparation_candidate.scope),
                "acceptance": list(self.preparation_candidate.acceptance),
                "verify": list(self.preparation_candidate.verify),
            }
        return payload


@dataclass(frozen=True, slots=True)
class TaskScopeFinding:
    """A changed path classification for during/postflight checks."""

    path: str
    allowed: bool
    category: str
    reason: str


@dataclass(frozen=True, slots=True)
class TaskScopeCheckResult:
    """Scope check result for changed paths."""

    ok: bool
    task_id: str
    findings: tuple[TaskScopeFinding, ...] = field(default_factory=tuple)
    verification_commands: tuple[str, ...] = ()
    execution_log_entry: str = ""
    requires_execution_log: bool = False
    requires_task_update: bool = False


def evaluate_task_guard(
    *,
    root: Path,
    checkpoint: Checkpoint | None = None,
    wi: Path | None = None,
    request_text: str = "处理当前用户请求",
) -> TaskGuardResult:
    """Return whether product code may be changed for the next executable task."""
    cp = checkpoint or load_checkpoint(root)
    spec_dir = _resolve_spec_dir(root=root, checkpoint=cp, wi=wi)
    if spec_dir is None:
        candidate = build_minimal_task_candidate(request_text=request_text)
        return TaskGuardResult(
            state=BLOCK_CODE_PREPARE_TASKS,
            allowed=False,
            detail="请先创建当前工作项并确认下一条可执行任务，再修改产品代码。",
            next_actions=minimal_formal_doc_actions(None),
            preparation_candidate=candidate,
        )

    tasks_path = spec_dir / "tasks.md"
    plan_path = spec_dir / "plan.md"
    active_work_item = spec_dir.name
    if not plan_path.is_file():
        candidate = build_minimal_task_candidate(
            work_item_id=active_work_item,
            request_text=request_text,
        )
        return TaskGuardResult(
            state=BLOCK_CODE_PREPARE_TASKS,
            allowed=False,
            detail="请先补齐当前工作项的 plan.md 和 tasks.md，再修改产品代码。",
            active_work_item=active_work_item,
            tasks_path=_repo_relative(root, tasks_path),
            next_actions=minimal_formal_doc_actions(_relative_path(root, spec_dir)),
            preparation_candidate=candidate,
        )
    if not tasks_path.is_file():
        candidate = build_minimal_task_candidate(
            work_item_id=active_work_item,
            request_text=request_text,
        )
        return TaskGuardResult(
            state=BLOCK_CODE_PREPARE_TASKS,
            allowed=False,
            detail="请先补齐当前工作项的 tasks.md，并确认下一条可执行任务。",
            active_work_item=active_work_item,
            tasks_path=_repo_relative(root, tasks_path),
            next_actions=minimal_formal_doc_actions(_relative_path(root, spec_dir)),
            preparation_candidate=candidate,
        )

    parsed = parse_executable_tasks(tasks_path)
    if not parsed.ok:
        return TaskGuardResult(
            state=BLOCK_CODE_PREPARE_TASKS,
            allowed=False,
            detail="当前 tasks.md 存在结构问题，请修复后再修改产品代码。",
            active_work_item=active_work_item,
            tasks_path=_repo_relative(root, tasks_path),
            next_actions=("修复 tasks.md 中的结构问题",),
            errors=tuple(f"{finding.code}: {finding.message}" for finding in parsed.errors),
        )

    task = first_executable_task(tasks_path)
    if task is None:
        candidate = build_minimal_task_candidate(
            work_item_id=active_work_item,
            request_text=request_text,
        )
        return TaskGuardResult(
            state=BLOCK_CODE_PREPARE_TASKS,
            allowed=False,
            detail="当前工作项没有下一条可执行任务，请先准备任务。",
            active_work_item=active_work_item,
            tasks_path=_repo_relative(root, tasks_path),
            next_actions=("新增或更新一条 status=todo/doing 的可执行任务",),
            preparation_candidate=candidate,
        )

    return TaskGuardResult(
        state=ALLOW_CODE_WITH_TASK,
        allowed=True,
        detail=f"已绑定下一条可执行任务 {task.task_id}。",
        active_work_item=active_work_item,
        task_id=task.task_id,
        task_title=task.title,
        task_goal=task.goal,
        tasks_path=_repo_relative(root, tasks_path),
    )


def check_task_scope(
    *,
    task: ExecutableTask,
    changed_paths: tuple[str, ...],
    verification_commands: tuple[str, ...] = (),
    execution_log_entry: str = "",
) -> TaskScopeCheckResult:
    """Check whether changed paths fit the executable task scope."""
    findings = tuple(_classify_changed_path(task, path) for path in changed_paths)
    requires_task_update = any(not finding.allowed for finding in findings)
    requires_execution_log = any(
        finding.category != "product" and finding.allowed for finding in findings
    )
    return TaskScopeCheckResult(
        ok=not requires_task_update,
        task_id=task.task_id,
        findings=findings,
        verification_commands=_dedupe(verification_commands),
        execution_log_entry=execution_log_entry.strip(),
        requires_execution_log=requires_execution_log,
        requires_task_update=requires_task_update,
    )


def _resolve_spec_dir(
    *,
    root: Path,
    checkpoint: Checkpoint | None,
    wi: Path | None,
) -> Path | None:
    if wi is not None:
        candidate = wi if wi.is_absolute() else root / wi
        return candidate if candidate.is_dir() else None
    if checkpoint is None or checkpoint.feature is None:
        return None
    spec_dir = (checkpoint.feature.spec_dir or "").strip()
    if not spec_dir or spec_dir == "specs/unknown":
        return None
    candidate = root / spec_dir
    return candidate if candidate.is_dir() else None


def _classify_changed_path(task: ExecutableTask, path: str) -> TaskScopeFinding:
    normalized = path.strip().replace("\\", "/")
    if _matches_scope(task.scope, normalized):
        return TaskScopeFinding(
            path=normalized,
            allowed=True,
            category="product",
            reason="matched task scope",
        )
    category = _companion_category(normalized)
    if category in {"test", "doc", "snapshot", "migration", "config", "generated"}:
        return TaskScopeFinding(
            path=normalized,
            allowed=True,
            category=category,
            reason="allowed companion file; record it in execution log",
        )
    return TaskScopeFinding(
        path=normalized,
        allowed=False,
        category=category,
        reason="outside task scope; update the task before changing this path",
    )


def _matches_scope(scope: tuple[str, ...], path: str) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) or path == pattern for pattern in scope)


def _companion_category(path: str) -> str:
    if path.startswith("tests/") or "/test_" in path or path.endswith("_test.go"):
        return "test"
    if path.endswith(".md") or path.startswith("docs/"):
        return "doc"
    if "snapshot" in path or "__snapshots__/" in path:
        return "snapshot"
    if "migration" in path or "migrations/" in path:
        return "migration"
    if path.endswith((".yaml", ".yml", ".toml", ".json", ".ini")):
        return "config"
    if path.startswith(("dist/", "build/", "generated/")):
        return "generated"
    return "product"


def _relative_path(root: Path, path: Path) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return path


def _repo_relative(root: Path, path: Path) -> str:
    return _relative_path(root, path).as_posix()
