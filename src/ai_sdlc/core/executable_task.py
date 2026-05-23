"""Parse and validate executable task blocks from ``tasks.md``."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path, PurePosixPath

TASK_HEADING_RE = re.compile(r"^###\s+Task\s+(?P<major>\d+)\.(?P<minor>\d+)\s+(?P<title>\S.*)$")
INVALID_TASK_HEADING_RE = re.compile(r"^###\s+(?:Task\s+|任务\s+)", re.IGNORECASE)
FIELD_RE = re.compile(r"^-\s+(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(?P<value>.*)$")
LIST_ITEM_RE = re.compile(r"^\s{2,}-\s+(?P<value>.+?)\s*$")
TASK_ID_RE = re.compile(r"^T[0-9][0-9A-Za-z_-]*$")

REQUIRED_FIELDS = frozenset({"task_id", "status", "scope", "acceptance", "verify"})
KNOWN_FIELDS = frozenset(
    {
        "task_id",
        "status",
        "goal",
        "priority",
        "depends",
        "scope",
        "acceptance",
        "verify",
        "notes",
    }
)
LIST_FIELDS = frozenset({"depends", "scope", "acceptance", "verify", "notes"})
EXECUTABLE_STATUSES = frozenset({"todo", "doing"})
NON_EXECUTABLE_STATUSES = frozenset({"done", "blocked", "needs-review"})
VALID_STATUSES = EXECUTABLE_STATUSES | NON_EXECUTABLE_STATUSES
PLACEHOLDER_RE = re.compile(r"(?<![/\w-])(?:TODO|placeholder)(?:\s*:|$)", re.IGNORECASE)
TEMPLATE_SCOPE_RE = re.compile(r"(^|/)(?:example|examples)(/|\.|$)", re.IGNORECASE)


class ExecutableTaskStatus(str, Enum):
    """Executable task lifecycle states accepted by the guard contract."""

    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs-review"


@dataclass(frozen=True, slots=True)
class ExecutableTaskFinding:
    """A parser finding with enough context for CLI/status surfaces."""

    code: str
    message: str
    task_id: str | None = None
    line: int | None = None


@dataclass(frozen=True, slots=True)
class ExecutableTask:
    """A normalized task block that can be used by later guard phases."""

    heading_id: str
    title: str
    task_id: str
    status: ExecutableTaskStatus
    goal: str = ""
    priority: str = ""
    depends: tuple[str, ...] = ()
    scope: tuple[str, ...] = ()
    acceptance: tuple[str, ...] = ()
    verify: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    unknown_fields: dict[str, str] = field(default_factory=dict)
    findings: tuple[ExecutableTaskFinding, ...] = ()

    @property
    def is_executable(self) -> bool:
        if self.status.value not in EXECUTABLE_STATUSES:
            return False
        return not any(finding.code != "unknown_field" for finding in self.findings)


@dataclass(frozen=True, slots=True)
class ExecutableTaskParseResult:
    """Structured parse output for a ``tasks.md`` file."""

    tasks: tuple[ExecutableTask, ...] = ()
    errors: tuple[ExecutableTaskFinding, ...] = ()
    warnings: tuple[ExecutableTaskFinding, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(slots=True)
class _TaskBlock:
    heading_id: str
    title: str
    start_line: int
    fields: dict[str, list[str]] = field(default_factory=dict)
    scalar_fields: dict[str, str] = field(default_factory=dict)
    unknown_fields: dict[str, str] = field(default_factory=dict)


def parse_executable_tasks(tasks_path: Path) -> ExecutableTaskParseResult:
    """Parse ``tasks.md`` into executable-task records and findings."""
    if not tasks_path.is_file():
        return ExecutableTaskParseResult(
            errors=(
                ExecutableTaskFinding(
                    code="tasks_file_missing",
                    message=f"tasks.md not found: {tasks_path}",
                ),
            )
        )
    return parse_executable_tasks_text(tasks_path.read_text(encoding="utf-8"))


def parse_executable_tasks_text(text: str) -> ExecutableTaskParseResult:
    """Parse executable task blocks from markdown text."""
    blocks, heading_errors = _parse_blocks(text)
    tasks: list[ExecutableTask] = []
    errors: list[ExecutableTaskFinding] = list(heading_errors)
    warnings: list[ExecutableTaskFinding] = []
    seen_ids: dict[str, int] = {}

    for block in blocks:
        task, block_errors, block_warnings = _build_task(block)
        if task.task_id in seen_ids:
            duplicate = ExecutableTaskFinding(
                code="duplicate_task_id",
                message=f"duplicate task_id: {task.task_id}",
                task_id=task.task_id,
                line=block.start_line,
            )
            block_errors.append(duplicate)
            task = _replace_task_findings(task, (*task.findings, duplicate))
        else:
            seen_ids[task.task_id] = block.start_line
        tasks.append(task)
        errors.extend(block_errors)
        warnings.extend(block_warnings)

    return ExecutableTaskParseResult(
        tasks=tuple(tasks),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def first_executable_task(tasks_path: Path) -> ExecutableTask | None:
    """Return the first executable task, if the document has one."""
    result = parse_executable_tasks(tasks_path)
    if not result.ok:
        return None
    for task in result.tasks:
        if task.is_executable:
            return task
    return None


def _parse_blocks(text: str) -> tuple[list[_TaskBlock], list[ExecutableTaskFinding]]:
    blocks: list[_TaskBlock] = []
    errors: list[ExecutableTaskFinding] = []
    current: _TaskBlock | None = None
    active_field: str | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        heading = TASK_HEADING_RE.match(stripped)
        if heading:
            current = _TaskBlock(
                heading_id=f"{heading.group('major')}.{heading.group('minor')}",
                title=heading.group("title").strip(),
                start_line=line_number,
            )
            blocks.append(current)
            active_field = None
            continue

        if INVALID_TASK_HEADING_RE.match(stripped):
            errors.append(
                ExecutableTaskFinding(
                    code="invalid_heading",
                    message=(
                        "task heading must use `### Task <major>.<minor> <title>`"
                    ),
                    line=line_number,
                )
            )
            current = None
            active_field = None
            continue

        if current is None:
            continue

        field_match = FIELD_RE.match(stripped)
        if field_match:
            key = _normalize_field_key(field_match.group("key"))
            value = field_match.group("value").strip()
            active_field = key
            current.fields.setdefault(key, [])
            if value:
                current.fields[key].append(value)
                current.scalar_fields[key] = value
            else:
                current.scalar_fields.setdefault(key, "")
            continue

        list_item = LIST_ITEM_RE.match(line)
        if list_item and active_field and active_field in LIST_FIELDS:
            current.fields.setdefault(active_field, []).append(list_item.group("value").strip())

    return blocks, errors


def _build_task(
    block: _TaskBlock,
) -> tuple[ExecutableTask, list[ExecutableTaskFinding], list[ExecutableTaskFinding]]:
    errors: list[ExecutableTaskFinding] = []
    warnings: list[ExecutableTaskFinding] = []
    unknown_fields: dict[str, str] = {}

    for key, value in block.scalar_fields.items():
        if key not in KNOWN_FIELDS:
            unknown_fields[key] = value
            warnings.append(
                ExecutableTaskFinding(
                    code="unknown_field",
                    message=f"unknown task field: {key}",
                    task_id=block.scalar_fields.get("task_id"),
                    line=block.start_line,
                )
            )

    missing = sorted(field for field in REQUIRED_FIELDS if not _field_values(block, field))
    for field_name in missing:
        errors.append(
            ExecutableTaskFinding(
                code=f"missing_{field_name}",
                message=f"task is missing required field: {field_name}",
                task_id=block.scalar_fields.get("task_id"),
                line=block.start_line,
            )
        )

    task_id = _first_value(block, "task_id") or f"T{block.heading_id.replace('.', '')}"
    if not TASK_ID_RE.fullmatch(task_id):
        errors.append(
            ExecutableTaskFinding(
                code="invalid_task_id",
                message=f"invalid task_id: {task_id}",
                task_id=task_id,
                line=block.start_line,
            )
        )

    status_raw = (_first_value(block, "status") or "todo").strip().lower()
    if status_raw not in VALID_STATUSES:
        errors.append(
            ExecutableTaskFinding(
                code="invalid_status",
                message=f"invalid task status: {status_raw}",
                task_id=task_id,
                line=block.start_line,
            )
        )
        status_raw = "blocked"

    depends = _parse_csv_or_list(_field_values(block, "depends"))
    scope = _field_values(block, "scope")
    acceptance = _field_values(block, "acceptance")
    verify = _field_values(block, "verify")
    notes = _field_values(block, "notes")

    for path in scope:
        if not _valid_scope_path(path):
            errors.append(
                ExecutableTaskFinding(
                    code="invalid_scope",
                    message=f"invalid task scope path: {path}",
                    task_id=task_id,
                    line=block.start_line,
                )
            )
        if TEMPLATE_SCOPE_RE.search(path):
            errors.append(
                ExecutableTaskFinding(
                    code="template_scope",
                    message=f"task scope points at template/example path: {path}",
                    task_id=task_id,
                    line=block.start_line,
                )
            )

    placeholder = _first_placeholder(
        {
            "scope": scope,
            "acceptance": acceptance,
            "verify": verify,
            "notes": notes,
        }
    )
    if placeholder is not None:
        field_name, value = placeholder
        errors.append(
            ExecutableTaskFinding(
                code="placeholder_content",
                message=f"task contains placeholder content in {field_name}: {value}",
                task_id=task_id,
                line=block.start_line,
            )
        )

    task_findings = tuple(errors)
    task = ExecutableTask(
        heading_id=block.heading_id,
        title=block.title,
        task_id=task_id,
        status=ExecutableTaskStatus(status_raw),
        goal=_first_value(block, "goal") or block.title,
        priority=_first_value(block, "priority") or "",
        depends=tuple(depends),
        scope=tuple(scope),
        acceptance=tuple(acceptance),
        verify=tuple(verify),
        notes=tuple(notes),
        unknown_fields=unknown_fields,
        findings=task_findings,
    )
    return task, errors, warnings


def _field_values(block: _TaskBlock, field_name: str) -> tuple[str, ...]:
    values = block.fields.get(field_name, [])
    return tuple(value.strip() for value in values if value.strip())


def _first_value(block: _TaskBlock, field_name: str) -> str | None:
    values = _field_values(block, field_name)
    return values[0] if values else None


def _parse_csv_or_list(values: Iterable[str]) -> tuple[str, ...]:
    parsed: list[str] = []
    for value in values:
        if value.lower() in {"none", "无", "-"}:
            continue
        parsed.extend(item.strip() for item in value.split(",") if item.strip())
    return tuple(dict.fromkeys(parsed))


def _normalize_field_key(key: str) -> str:
    return key.strip().lower().replace("-", "_")


def _valid_scope_path(path: str) -> bool:
    candidate = path.strip().replace("\\", "/")
    if not candidate or candidate.startswith("/") or "://" in candidate:
        return False
    parts = PurePosixPath(candidate).parts
    return not any(part == ".." for part in parts)


def _first_placeholder(values_by_field: dict[str, tuple[str, ...]]) -> tuple[str, str] | None:
    for field_name, values in values_by_field.items():
        for value in values:
            if _is_placeholder_value(value):
                return field_name, value
    return None


def _is_placeholder_value(value: str) -> bool:
    normalized = value.strip()
    if PLACEHOLDER_RE.search(normalized):
        return True
    if "待补充" not in normalized:
        return False
    return "占位" not in normalized and "不可执行" not in normalized


def _replace_task_findings(
    task: ExecutableTask,
    findings: tuple[ExecutableTaskFinding, ...],
) -> ExecutableTask:
    return ExecutableTask(
        heading_id=task.heading_id,
        title=task.title,
        task_id=task.task_id,
        status=task.status,
        goal=task.goal,
        priority=task.priority,
        depends=task.depends,
        scope=task.scope,
        acceptance=task.acceptance,
        verify=task.verify,
        notes=task.notes,
        unknown_fields=task.unknown_fields,
        findings=findings,
    )
