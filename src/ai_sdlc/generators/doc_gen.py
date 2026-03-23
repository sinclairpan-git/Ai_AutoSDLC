"""Document scaffolding and tasks.md parsing."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from ai_sdlc.generators.template_gen import TemplateGenerator
from ai_sdlc.models.state import ExecutionBatch, ExecutionPlan, Task
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)


# ── document scaffolder ──


class DocScaffolder:
    """Generate spec, plan, tasks, and execution-log scaffolds.

    Uses Jinja2 templates under ``ai_sdlc/templates`` and writes Markdown files
    under ``<root>/specs/<work_item_id>/``, skipping files that already exist.
    """

    TEMPLATES = ["spec.md.j2", "plan.md.j2", "tasks.md.j2", "execution-log.md.j2"]
    OUTPUT_NAMES = ["spec.md", "plan.md", "tasks.md", "execution-log.md"]

    def __init__(self, template_gen: TemplateGenerator | None = None) -> None:
        self._gen = template_gen or TemplateGenerator()

    def render(self, template_name: str, context: dict[str, object]) -> str:
        """Render a template to string."""
        return self._gen.render(template_name, context)

    def scaffold(
        self,
        root: Path,
        work_item_id: str,
        context: dict[str, object] | None = None,
    ) -> list[Path]:
        """Generate scaffold documents in specs/<work_item_id>/ directory."""
        ctx = dict(context or {})
        ctx.setdefault("work_item_id", work_item_id)
        ctx.setdefault("created_at", now_iso())
        ctx.setdefault("project_name", work_item_id)
        ctx.setdefault("modules", [])
        ctx.setdefault("tasks", [])
        ctx.setdefault("batches", [])

        spec_dir = root / "specs" / work_item_id
        spec_dir.mkdir(parents=True, exist_ok=True)

        created: list[Path] = []
        for tmpl, out_name in zip(self.TEMPLATES, self.OUTPUT_NAMES, strict=True):
            out_path = spec_dir / out_name
            if out_path.exists():
                logger.info("Skipping existing file: %s", out_path)
                continue
            self._gen.render_to_file(tmpl, ctx, out_path)
            logger.info("Created scaffold: %s", out_path)
            created.append(out_path)
        return created


# ── tasks parser ──

_TASK_HEADER = re.compile(r"^###\s+Task\s+(\d+)\.(\d+)\s+(.*)", re.IGNORECASE)
_FIELD_PATTERN = re.compile(r"^-\s+\*\*(.*?)\*\*\s*[:：]\s*(.*)")


class TasksParser:
    """Parse a tasks.md Markdown file into an ExecutionPlan."""

    def parse(self, tasks_path: Path) -> ExecutionPlan:
        """Parse tasks.md and return a structured ExecutionPlan."""
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
