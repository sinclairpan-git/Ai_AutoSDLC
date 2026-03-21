"""Incident Studio — process production incidents into structured fix plans."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ai_sdlc.models.incident import (
    IncidentAnalysis,
    IncidentBrief,
    IncidentFixPlan,
    IncidentTask,
    PostmortemRecord,
)
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)


class IncidentStudio:
    """Process incident briefs into analysis, fix plan, tasks, and postmortem template."""

    def process(
        self, input_data: Any, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Process an IncidentBrief and produce incident artifacts.

        Args:
            input_data: An IncidentBrief instance.
            context: Must include "work_item_id" and optionally "root" for file output.

        Returns:
            Dictionary with "analysis", "fix_plan", "postmortem" artifacts.
        """
        if not isinstance(input_data, IncidentBrief):
            raise TypeError(
                f"IncidentStudio expects IncidentBrief, got {type(input_data).__name__}"
            )

        ctx = context or {}
        work_item_id = ctx.get("work_item_id", "WI-UNKNOWN")
        brief: IncidentBrief = input_data

        analysis = self._build_analysis(work_item_id, brief)
        fix_plan = self._build_fix_plan(work_item_id, brief)
        postmortem = self._build_postmortem(work_item_id, brief)

        root = ctx.get("root")
        if root:
            self._save_artifacts(
                Path(root), work_item_id, analysis, fix_plan, postmortem
            )

        return {
            "analysis": analysis,
            "fix_plan": fix_plan,
            "postmortem": postmortem,
        }

    def _build_analysis(self, wid: str, brief: IncidentBrief) -> IncidentAnalysis:
        return IncidentAnalysis(
            work_item_id=wid,
            summary=f"Incident: {brief.phenomenon}",
            probable_causes=[f"Investigation needed for: {brief.phenomenon}"],
            affected_modules=[brief.impact_scope] if brief.impact_scope else [],
            risk_assessment=f"Severity: {brief.severity.value}",
        )

    def _build_fix_plan(self, wid: str, brief: IncidentBrief) -> IncidentFixPlan:
        tasks = [
            IncidentTask(
                task_id=f"{wid}-IT-1",
                title="Investigate root cause",
                description=f"Analyze: {brief.phenomenon}",
                verification="Root cause identified and documented",
            ),
            IncidentTask(
                task_id=f"{wid}-IT-2",
                title="Implement fix",
                description="Apply targeted fix for identified root cause",
                verification="Fix verified in staging environment",
            ),
            IncidentTask(
                task_id=f"{wid}-IT-3",
                title="Regression testing",
                description="Run full regression suite + targeted tests",
                verification="All tests pass, no new issues",
            ),
        ]
        return IncidentFixPlan(
            work_item_id=wid,
            strategy=f"Hotfix for {brief.severity.value} incident: {brief.phenomenon}",
            tasks=tasks,
            rollback_plan="Revert hotfix commit and redeploy previous version",
        )

    def _build_postmortem(self, wid: str, brief: IncidentBrief) -> PostmortemRecord:
        return PostmortemRecord(
            work_item_id=wid,
            incident_summary=brief.phenomenon,
            timeline=f"Reported at: {brief.reported_at or now_iso()}",
            root_cause="<!-- TODO: Fill in after investigation -->",
            resolution="<!-- TODO: Fill in after fix is applied -->",
            lessons_learned=["<!-- TODO: Add lessons learned -->"],
            action_items=["<!-- TODO: Add follow-up action items -->"],
            prevention_measures=["<!-- TODO: Add prevention measures -->"],
        )

    def _save_artifacts(
        self,
        root: Path,
        wid: str,
        analysis: IncidentAnalysis,
        fix_plan: IncidentFixPlan,
        postmortem: PostmortemRecord,
    ) -> None:
        from ai_sdlc.utils.fs import AI_SDLC_DIR

        out_dir = root / AI_SDLC_DIR / "work-items" / wid
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "incident-analysis.md").write_text(
            f"# Incident Analysis: {wid}\n\n"
            f"## Summary\n\n{analysis.summary}\n\n"
            f"## Probable Causes\n\n"
            + "\n".join(f"- {c}" for c in analysis.probable_causes)
            + "\n\n## Affected Modules\n\n"
            + "\n".join(f"- {m}" for m in analysis.affected_modules)
            + f"\n\n## Risk Assessment\n\n{analysis.risk_assessment}\n",
            encoding="utf-8",
        )

        (out_dir / "fix-plan.md").write_text(
            f"# Fix Plan: {wid}\n\n"
            f"## Strategy\n\n{fix_plan.strategy}\n\n"
            f"## Tasks\n\n"
            + "\n".join(
                f"### {t.task_id}: {t.title}\n\n{t.description}\n\n**Verification**: {t.verification}\n"
                for t in fix_plan.tasks
            )
            + f"\n## Rollback Plan\n\n{fix_plan.rollback_plan}\n",
            encoding="utf-8",
        )

        (out_dir / "postmortem.md").write_text(
            f"# Postmortem: {wid}\n\n"
            f"## Incident Summary\n\n{postmortem.incident_summary}\n\n"
            f"## Timeline\n\n{postmortem.timeline}\n\n"
            f"## Root Cause\n\n{postmortem.root_cause}\n\n"
            f"## Resolution\n\n{postmortem.resolution}\n\n"
            f"## Lessons Learned\n\n"
            + "\n".join(f"- {lesson}" for lesson in postmortem.lessons_learned)
            + "\n",
            encoding="utf-8",
        )
