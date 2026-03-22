"""Parse tasks.md into an ExecutionPlan model."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ai_sdlc.models.execution import ExecutionBatch, ExecutionPlan, Task

logger = logging.getLogger(__name__)

_TASK_HEADER = re.compile(r"^###\s+Task\s+(\d+)\.(\d+)\s+(.*)", re.IGNORECASE)
_FIELD_PATTERN = re.compile(r"^-\s+\*\*(.*?)\*\*\s*[:：]\s*(.*)")


class TasksParser:
    """Parse a tasks.md Markdown file into an ExecutionPlan."""

    def parse(self, tasks_path: Path) -> ExecutionPlan:
        """Parse tasks.md and return a structured ExecutionPlan.

        Args:
            tasks_path: Path to the tasks.md file.

        Returns:
            Populated ExecutionPlan with tasks grouped into batches by phase.
        """
        if not tasks_path.exists():
            logger.warning("Tasks file not found: %s", tasks_path)
            return ExecutionPlan()

        text = tasks_path.read_text(encoding="utf-8")
        tasks = self._extract_tasks(text)
        batches = self._group_into_batches(tasks)

        return ExecutionPlan(
            total_tasks=len(tasks),
            total_batches=len(batches),
            tasks=tasks,
            batches=batches,
        )

    def _extract_tasks(self, text: str) -> list[Task]:
        """Extract Task objects from markdown text."""
        tasks: list[Task] = []
        current_fields: dict[str, str] = {}
        current_header: re.Match[str] | None = None

        for line in text.splitlines():
            header_match = _TASK_HEADER.match(line.strip())
            if header_match:
                if current_header:
                    tasks.append(self._build_task(current_header, current_fields))
                current_header = header_match
                current_fields = {}
                continue

            field_match = _FIELD_PATTERN.match(line.strip())
            if field_match and current_header:
                key = field_match.group(1).strip().lower()
                value = field_match.group(2).strip()
                current_fields[key] = value

        if current_header:
            tasks.append(self._build_task(current_header, current_fields))

        return tasks

    def _build_task(self, header: re.Match[str], fields: dict[str, str]) -> Task:
        """Build a Task from parsed header and field data."""
        phase = int(header.group(1))
        title = header.group(3).strip()
        task_id = fields.get("task id", f"T{phase}{header.group(2)}")

        depends_raw = fields.get("依赖", fields.get("depends", ""))
        depends_on: list[str] = []
        if depends_raw and depends_raw not in ("无", "none", "None", "-"):
            depends_on = [d.strip() for d in depends_raw.split(",") if d.strip()]

        files_raw = fields.get("文件", fields.get("files", ""))
        file_paths: list[str] = []
        if files_raw and files_raw not in ("TBD", "tbd", "-"):
            file_paths = [f.strip() for f in files_raw.split(",") if f.strip()]

        parallel_raw = fields.get("可并行", fields.get("parallelizable", "否"))
        parallelizable = parallel_raw.lower() in ("是", "yes", "true", "1")

        return Task(
            task_id=task_id,
            title=title,
            phase=phase,
            file_paths=file_paths,
            parallelizable=parallelizable,
            depends_on=depends_on,
        )

    def _group_into_batches(self, tasks: list[Task]) -> list[ExecutionBatch]:
        """Group tasks by phase into execution batches."""
        phase_map: dict[int, list[str]] = {}
        for task in tasks:
            phase_map.setdefault(task.phase, []).append(task.task_id)

        batches: list[ExecutionBatch] = []
        for batch_idx, phase in enumerate(sorted(phase_map), start=1):
            batches.append(
                ExecutionBatch(
                    batch_id=batch_idx,
                    phase=phase,
                    tasks=phase_map[phase],
                )
            )
        return batches
