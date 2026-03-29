"""Document scaffolding and tasks.md parsing."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.backends.routing import BackendRoutingCoordinator
from ai_sdlc.generators.template_gen import TemplateGenerator
from ai_sdlc.models.state import ExecutionBatch, ExecutionPlan, Task
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

_BACKEND_ROUTE_BYPASS_KEY = "_ai_sdlc_backend_route_bypass"
_TEMPLATE_GENERATOR_KEY = "_ai_sdlc_template_gen"
_BACKEND_REGISTRY_KEY = "backend_registry"
_REQUESTED_BACKEND_KEY = "requested_backend"
_BACKEND_POLICY_KEY = "backend_policy"
_BACKEND_DECISIONS_KEY = "backend_decisions"


@dataclass(frozen=True, slots=True)
class ScaffoldRenderResult:
    """Scaffold creation result with optional backend decision evidence."""

    created_paths: list[Path]
    backend_decisions: dict[str, object | None]


@dataclass(frozen=True, slots=True)
class RenderResult:
    """Rendered document and the backend decision that produced it."""

    content: str
    backend_decision: object | None = None


# ── document scaffolder ──


class DocScaffolder:
    """Generate spec, plan, tasks, and execution-log scaffolds.

    Uses Jinja2 templates under ``ai_sdlc/templates`` and writes Markdown files
    under ``<root>/specs/<work_item_id>/``, skipping files that already exist.
    """

    TEMPLATES = ["spec.md.j2", "plan.md.j2", "tasks.md.j2", "execution-log.md.j2"]
    OUTPUT_NAMES = ["spec.md", "plan.md", "tasks.md", "execution-log.md"]

    def __init__(
        self,
        template_gen: TemplateGenerator | None = None,
        *,
        router: BackendRoutingCoordinator | None = None,
    ) -> None:
        self._gen = template_gen or TemplateGenerator()
        self._router = router

    def render(self, template_name: str, context: dict[str, object]) -> str:
        """Render a template to string."""
        return self.render_with_backend_selection(template_name, context).content

    def render_with_backend_selection(
        self, template_name: str, context: dict[str, object]
    ) -> RenderResult:
        """Render a template and expose the backend decision used."""
        if context.get(_BACKEND_ROUTE_BYPASS_KEY):
            return RenderResult(content=self._render_direct(template_name, context))

        if template_name == "spec.md.j2":
            return self._route_and_record("spec.md", template_name, context)
        if template_name == "plan.md.j2":
            return self._route_and_record("plan.md", template_name, context)
        if template_name == "tasks.md.j2":
            return self._route_and_record("tasks.md", template_name, context)
        rendered = self._render_direct(template_name, context)
        if template_name == "execution-log.md.j2":
            decisions = self._backend_decisions(context)
            if decisions is not None:
                decisions["execution-log.md"] = None
        return RenderResult(content=rendered)

    def scaffold(
        self,
        root: Path,
        work_item_id: str,
        context: dict[str, object] | None = None,
    ) -> list[Path]:
        """Generate scaffold documents in specs/<work_item_id>/ directory."""
        return self.scaffold_with_backend_selection(root, work_item_id, context).created_paths

    def scaffold_with_backend_selection(
        self,
        root: Path,
        work_item_id: str,
        context: dict[str, object] | None = None,
    ) -> ScaffoldRenderResult:
        """Generate scaffold documents and expose backend decisions."""
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
        backend_decisions = self._backend_decisions(ctx, create=True)
        for tmpl, out_name in zip(self.TEMPLATES, self.OUTPUT_NAMES, strict=True):
            out_path = spec_dir / out_name
            if out_path.exists():
                logger.info("Skipping existing file: %s", out_path)
                continue
            rendered = self.render_with_backend_selection(tmpl, ctx)
            self._write_output(out_path, rendered.content)
            logger.info("Created scaffold: %s", out_path)
            created.append(out_path)
        return ScaffoldRenderResult(
            created_paths=created,
            backend_decisions=dict(backend_decisions),
        )

    def _write_output(self, output_path: Path, content: str) -> None:
        file_guard = getattr(self._gen, "_file_guard", None)
        if file_guard is not None:
            file_guard.write_text(output_path, content, encoding="utf-8")
            return
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

    def _route_and_record(
        self,
        output_name: str,
        template_name: str,
        context: dict[str, object],
    ) -> RenderResult:
        routed_context = dict(context)
        routed_context.setdefault(_TEMPLATE_GENERATOR_KEY, self._gen)
        router = self._routing(context)
        if template_name == "spec.md.j2":
            routed = router.generate_spec(routed_context)
        elif template_name == "plan.md.j2":
            routed = router.generate_plan(routed_context)
        else:
            routed = router.generate_tasks(routed_context)
        decisions = self._backend_decisions(context)
        if decisions is not None:
            decisions[output_name] = routed.backend_decision
        return RenderResult(
            content=routed.content,
            backend_decision=routed.backend_decision,
        )

    def _render_direct(self, template_name: str, context: dict[str, object]) -> str:
        renderer = self._template_renderer(context)
        return renderer.render(template_name, context)

    def _template_renderer(self, context: dict[str, object]) -> object:
        renderer = context.get(_TEMPLATE_GENERATOR_KEY)
        if renderer is not None:
            return renderer
        return self._gen

    def _routing(self, context: dict[str, object]) -> BackendRoutingCoordinator:
        import ai_sdlc.backends.native as native_backend

        registry = context.get(_BACKEND_REGISTRY_KEY)
        requested_backend = context.get(_REQUESTED_BACKEND_KEY)
        policy = context.get(_BACKEND_POLICY_KEY)
        if (
            isinstance(registry, native_backend.BackendRegistry)
            or requested_backend is not None
            or isinstance(policy, native_backend.BackendSelectionPolicy)
        ):
            return BackendRoutingCoordinator(
                registry=(
                    registry if isinstance(registry, native_backend.BackendRegistry) else None
                ),
                requested_backend=(
                    requested_backend if isinstance(requested_backend, str) else None
                ),
                policy=(
                    policy if isinstance(policy, native_backend.BackendSelectionPolicy) else None
                ),
            )
        if self._router is None:
            self._router = BackendRoutingCoordinator()
        return self._router

    def _backend_decisions(
        self,
        context: dict[str, object],
        *,
        create: bool = False,
    ) -> dict[str, object | None] | None:
        decisions = context.get(_BACKEND_DECISIONS_KEY)
        if isinstance(decisions, dict):
            return decisions
        if not create:
            return None
        decisions = {}
        context[_BACKEND_DECISIONS_KEY] = decisions
        return decisions


# ── tasks parser ──

_TASK_HEADER = re.compile(
    r"^###\s+(?:Task|任务)\s+(\d+)\.(\d+)\s+(.*)", re.IGNORECASE
)
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
        task_id = fields.get(
            "task id",
            fields.get("任务编号", f"T{phase}{header.group(2)}"),
        )

        depends_raw = fields.get("依赖", fields.get("depends", ""))
        depends_on: list[str] = []
        if depends_raw and depends_raw not in ("无", "none", "None", "-"):
            depends_on = [d.strip() for d in depends_raw.split(",") if d.strip()]

        files_raw = fields.get("文件", fields.get("files", ""))
        file_paths: list[str] = []
        if files_raw and files_raw not in ("TBD", "tbd", "-", "待定"):
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
