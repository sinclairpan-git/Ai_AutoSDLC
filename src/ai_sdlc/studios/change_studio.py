"""Change Request Studio — freeze state, analyze impact, and prepare rebaseline."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ai_sdlc.core.p1_artifacts import save_freeze_snapshot, save_resume_point
from ai_sdlc.core.state_machine import (
    load_work_item,
    transition_work_item,
    work_item_path,
)
from ai_sdlc.models.work import (
    ChangeRequest,
    FreezeSnapshot,
    ImpactAnalysis,
    RebaselineRecord,
    ResumePoint,
    WorkItemStatus,
)
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)


class ChangeStudio:
    """Process change requests: freeze current state, analyze impact, create rebaseline."""

    def process(
        self, input_data: Any, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Process a ChangeRequest and produce change management artifacts.

        Args:
            input_data: A ChangeRequest instance.
            context: Must include "work_item_id", "current_stage", "current_batch",
                     optionally "current_branch", "root".

        Returns:
            Dictionary with "freeze_snapshot", "impact_analysis", "rebaseline_record",
            and the updated "change_request".
        """
        if not isinstance(input_data, ChangeRequest):
            raise TypeError(
                f"ChangeStudio expects ChangeRequest, got {type(input_data).__name__}"
            )

        ctx = context or {}
        cr: ChangeRequest = input_data

        freeze = self._create_freeze_snapshot(cr, ctx)
        impact = self._create_impact_analysis(cr, ctx)
        rebaseline = self._create_rebaseline_record(cr)

        cr.freeze_snapshot = freeze
        cr.impact_analysis = impact
        cr.rebaseline_record = rebaseline
        cr.resume_point = self._create_resume_point(ctx)
        cr.status = "analyzing"

        root = ctx.get("root")
        if root:
            self._save_artifacts(Path(root), cr)
            self._suspend_work_item(Path(root), cr.work_item_id)

        return {
            "change_request": cr,
            "freeze_snapshot": freeze,
            "impact_analysis": impact,
            "rebaseline_record": rebaseline,
        }

    def _create_freeze_snapshot(
        self, cr: ChangeRequest, ctx: dict[str, Any]
    ) -> FreezeSnapshot:
        return FreezeSnapshot(
            work_item_id=cr.work_item_id,
            frozen_at=now_iso(),
            current_stage=ctx.get("current_stage", "unknown"),
            current_batch=ctx.get("current_batch", 0),
            current_branch=ctx.get("current_branch", ""),
        )

    def _create_impact_analysis(
        self, cr: ChangeRequest, ctx: dict[str, Any]
    ) -> ImpactAnalysis:
        return ImpactAnalysis(
            change_request_id=cr.change_request_id,
            affected_specs=["<!-- TODO: List affected spec sections -->"],
            affected_plan_sections=["<!-- TODO: List affected plan sections -->"],
            affected_tasks=["<!-- TODO: List affected tasks -->"],
            risk_level=cr.priority,
            notes=f"Change reason: {cr.reason}",
        )

    def _create_rebaseline_record(self, cr: ChangeRequest) -> RebaselineRecord:
        return RebaselineRecord(
            change_request_id=cr.change_request_id,
            diff_summary=f"Change: {cr.description}",
            rebaselined_at=now_iso(),
        )

    def _create_resume_point(self, ctx: dict[str, Any]) -> ResumePoint:
        return ResumePoint(
            stage=ctx.get("current_stage", "unknown"),
            batch=ctx.get("current_batch", 0),
            status=WorkItemStatus.SUSPENDED.value,
            current_branch=ctx.get("current_branch", ""),
        )

    def _save_artifacts(self, root: Path, cr: ChangeRequest) -> None:
        from ai_sdlc.utils.helpers import AI_SDLC_DIR

        out_dir = root / AI_SDLC_DIR / "work-items" / cr.work_item_id
        out_dir.mkdir(parents=True, exist_ok=True)
        if cr.freeze_snapshot is not None:
            save_freeze_snapshot(root, cr.work_item_id, cr.freeze_snapshot)
        if cr.resume_point is not None:
            save_resume_point(root, cr.work_item_id, cr.resume_point)

        if cr.impact_analysis:
            (out_dir / "impact-analysis.md").write_text(
                f"# Impact Analysis: {cr.change_request_id}\n\n"
                f"## Change Description\n\n{cr.description}\n\n"
                f"## Reason\n\n{cr.reason}\n\n"
                f"## Affected Specs\n\n"
                + "\n".join(f"- {s}" for s in cr.impact_analysis.affected_specs)
                + "\n\n## Affected Tasks\n\n"
                + "\n".join(f"- {t}" for t in cr.impact_analysis.affected_tasks)
                + f"\n\n## Risk Level\n\n{cr.impact_analysis.risk_level}\n",
                encoding="utf-8",
            )

        if cr.rebaseline_record:
            (out_dir / "rebaseline-record.md").write_text(
                f"# Rebaseline Record: {cr.change_request_id}\n\n"
                f"## Diff Summary\n\n{cr.rebaseline_record.diff_summary}\n\n"
                f"## Rebaselined At\n\n{cr.rebaseline_record.rebaselined_at}\n",
                encoding="utf-8",
            )

    def _suspend_work_item(self, root: Path, work_item_id: str) -> None:
        if not work_item_path(root, work_item_id).exists():
            return
        work_item = load_work_item(root, work_item_id)
        if work_item.status not in {
            WorkItemStatus.DEV_EXECUTING,
            WorkItemStatus.DEV_VERIFYING,
        }:
            return
        transition_work_item(root, work_item, WorkItemStatus.SUSPENDED)
