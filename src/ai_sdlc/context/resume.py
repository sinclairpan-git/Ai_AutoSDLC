"""Resume Pack Manager — build and save context for recovery."""

from __future__ import annotations

import logging
from pathlib import Path

from ai_sdlc.context.checkpoint import load_checkpoint
from ai_sdlc.core.yaml_store import YamlStore
from ai_sdlc.models.context import ResumePack, WorkingSet
from ai_sdlc.utils.time_utils import now_iso

logger = logging.getLogger(__name__)


def build_resume_pack(root: Path) -> ResumePack | None:
    """Build a resume pack from the current checkpoint and file system.

    Returns None if no checkpoint is found.
    """
    cp = load_checkpoint(root)
    if cp is None:
        return None

    ws = WorkingSet()
    if cp.feature:
        spec_dir = root / cp.feature.spec_dir
        if (spec_dir / "spec.md").exists():
            ws.spec_path = str(spec_dir / "spec.md")
        if (spec_dir / "plan.md").exists():
            ws.plan_path = str(spec_dir / "plan.md")
        if (spec_dir / "tasks.md").exists():
            ws.tasks_path = str(spec_dir / "tasks.md")

    if cp.prd_source and (root / cp.prd_source).exists():
        ws.prd_path = cp.prd_source

    constitution = root / ".ai-sdlc" / "memory" / "constitution.md"
    if constitution.exists():
        ws.constitution_path = str(constitution)

    tech_stack = root / ".ai-sdlc" / "profiles" / "tech-stack.yml"
    if tech_stack.exists():
        ws.tech_stack_path = str(tech_stack)

    current_batch = 0
    last_task = ""
    if cp.execute_progress:
        current_batch = cp.execute_progress.current_batch
        last_task = cp.execute_progress.last_committed_task

    return ResumePack(
        current_stage=cp.current_stage,
        current_batch=current_batch,
        last_committed_task=last_task,
        working_set_snapshot=ws,
        timestamp=now_iso(),
    )


def save_resume_pack(root: Path, pack: ResumePack) -> None:
    """Save a resume pack to disk."""
    path = root / ".ai-sdlc" / "state" / "resume-pack.yaml"
    YamlStore.save(path, pack)
