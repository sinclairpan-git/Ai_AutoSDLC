"""Document scaffolding generator for SDLC pipeline artifacts."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.generators.template_gen import TemplateGenerator
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)


class DocScaffolder:
    """Generate spec, plan, tasks, and execution-log scaffolds.

    Uses Jinja2 templates under ``ai_sdlc/templates`` and writes Markdown files
    under ``<root>/specs/<work_item_id>/``, skipping files that already exist.
    """

    TEMPLATES = ["spec.md.j2", "plan.md.j2", "tasks.md.j2", "execution-log.md.j2"]
    OUTPUT_NAMES = ["spec.md", "plan.md", "tasks.md", "execution-log.md"]

    def __init__(self, template_gen: TemplateGenerator | None = None) -> None:
        self._gen = template_gen or TemplateGenerator()

    def scaffold(
        self,
        root: Path,
        work_item_id: str,
        context: dict[str, object] | None = None,
    ) -> list[Path]:
        """Generate scaffold documents in specs/<work_item_id>/ directory.

        Args:
            root: Project root directory.
            work_item_id: Work item identifier (e.g. "WI-2026-001").
            context: Optional template context variables.

        Returns:
            List of created file paths.
        """
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
