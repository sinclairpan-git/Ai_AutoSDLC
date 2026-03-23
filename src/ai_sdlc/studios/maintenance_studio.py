"""Maintenance Brief Studio — lightweight path for maintenance tasks."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ai_sdlc.models.work import (
    MaintenanceBrief,
    MaintenancePlan,
    MaintenanceTask,
    SmallTaskGraph,
)

logger = logging.getLogger(__name__)


class MaintenanceStudio:
    """Process maintenance briefs into lightweight plans with small task graphs."""

    def process(
        self, input_data: Any, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Process a MaintenanceBrief and produce a lightweight maintenance plan.

        Args:
            input_data: A MaintenanceBrief instance.
            context: Must include "work_item_id", optionally "root".

        Returns:
            Dictionary with "plan" artifact.
        """
        if not isinstance(input_data, MaintenanceBrief):
            raise TypeError(
                f"MaintenanceStudio expects MaintenanceBrief, got {type(input_data).__name__}"
            )

        ctx = context or {}
        work_item_id = ctx.get("work_item_id", "WI-UNKNOWN")
        brief: MaintenanceBrief = input_data

        plan = self._build_plan(work_item_id, brief)

        root = ctx.get("root")
        if root:
            self._save_artifacts(Path(root), work_item_id, plan)

        return {"plan": plan}

    def _build_plan(self, wid: str, brief: MaintenanceBrief) -> MaintenancePlan:
        tasks = self._generate_tasks(wid, brief)
        execution_order = [t.task_id for t in tasks]

        return MaintenancePlan(
            work_item_id=wid,
            brief_summary=brief.description,
            category=brief.category,
            task_graph=SmallTaskGraph(tasks=tasks, execution_order=execution_order),
        )

    def _generate_tasks(
        self, wid: str, brief: MaintenanceBrief
    ) -> list[MaintenanceTask]:
        tasks: list[MaintenanceTask] = []

        tasks.append(
            MaintenanceTask(
                task_id=f"{wid}-MT-1",
                title="Assess current state",
                description=f"Review impact scope: {', '.join(brief.impact_scope) or 'TBD'}",
                verification="Current state documented",
            )
        )

        tasks.append(
            MaintenanceTask(
                task_id=f"{wid}-MT-2",
                title="Execute maintenance",
                description=brief.description,
                depends_on=[f"{wid}-MT-1"],
                file_paths=brief.impact_scope,
                verification="Changes applied successfully",
            )
        )

        tasks.append(
            MaintenanceTask(
                task_id=f"{wid}-MT-3",
                title="Verify and test",
                description="Run relevant tests and verify no regressions",
                depends_on=[f"{wid}-MT-2"],
                verification="All tests pass, no regressions",
            )
        )

        return tasks

    def _save_artifacts(self, root: Path, wid: str, plan: MaintenancePlan) -> None:
        from ai_sdlc.utils.helpers import AI_SDLC_DIR

        out_dir = root / AI_SDLC_DIR / "work-items" / wid
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "maintenance-brief.md").write_text(
            f"# Maintenance Plan: {wid}\n\n"
            f"## Summary\n\n{plan.brief_summary}\n\n"
            f"## Category\n\n{plan.category or 'general'}\n\n"
            f"## Tasks ({plan.task_graph.task_count})\n\n"
            + "\n".join(
                f"### {t.task_id}: {t.title}\n\n{t.description}\n\n"
                f"**Depends on**: {', '.join(t.depends_on) or 'none'}\n\n"
                f"**Verification**: {t.verification}\n"
                for t in plan.task_graph.tasks
            ),
            encoding="utf-8",
        )
