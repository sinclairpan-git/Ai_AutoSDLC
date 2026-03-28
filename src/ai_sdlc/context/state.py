"""Checkpoint, resume-pack, and working-set management."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ai_sdlc.core.config import YamlStore, YamlStoreError
from ai_sdlc.models.state import (
    Checkpoint,
    CompletedStage,
    ResumePack,
    WorkingSet,
)
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)

CHECKPOINT_PATH = Path(".ai-sdlc") / "state" / "checkpoint.yml"
RESUME_PACK_PATH = Path(".ai-sdlc") / "state" / "resume-pack.yaml"

STAGE_FILES: dict[str, list[str]] = {
    "init": [],
    "refine": ["prd_path", "constitution_path", "tech_stack_path"],
    "design": ["prd_path", "constitution_path", "tech_stack_path", "spec_path"],
    "decompose": ["spec_path", "plan_path", "constitution_path"],
    "verify": ["spec_path", "plan_path", "tasks_path"],
    "execute": ["tasks_path", "plan_path", "spec_path", "constitution_path"],
    "close": ["tasks_path", "spec_path"],
}

VALID_CHECKPOINT_STAGES = frozenset(STAGE_FILES)


class CheckpointLoadError(Exception):
    """Raised when checkpoint.yml is missing or violates recovery contracts."""


class ResumePackError(Exception):
    """Raised when resume-pack.yaml cannot be loaded safely."""


class ResumePackNotFoundError(ResumePackError):
    """Raised when resume-pack.yaml is required but missing."""


# ── checkpoint management ──


def save_checkpoint(root: Path, checkpoint: Checkpoint) -> None:
    """Save checkpoint, backing up the previous version."""
    cp_path = root / CHECKPOINT_PATH
    if cp_path.exists():
        bak = cp_path.with_suffix(".yml.bak")
        shutil.copy2(cp_path, bak)
    checkpoint.pipeline_last_updated = now_iso()
    YamlStore.save(cp_path, checkpoint)


def load_checkpoint(root: Path, *, strict: bool = False) -> Checkpoint | None:
    """Load checkpoint from file. Returns None if not found.

    Falls back to .bak file if primary is corrupted.
    """
    cp_path = root / CHECKPOINT_PATH
    bak = cp_path.with_suffix(".yml.bak")

    if not cp_path.exists():
        if strict:
            raise CheckpointLoadError("checkpoint.yml not found")
        return None

    try:
        return _load_checkpoint_candidate(root, cp_path, strict=strict)
    except (YamlStoreError, CheckpointLoadError) as exc:
        logger.warning("Checkpoint load failed (%s), trying backup", exc)
        if bak.exists():
            return _load_checkpoint_candidate(root, bak, strict=strict)
        if strict and isinstance(exc, CheckpointLoadError):
            raise
        if strict:
            raise CheckpointLoadError(str(exc)) from exc
        return None


def update_stage(
    root: Path,
    stage: str,
    artifacts: list[str] | None = None,
) -> Checkpoint | None:
    """Mark a stage as completed and advance the checkpoint."""
    cp = load_checkpoint(root)
    if cp is None:
        return None
    cp.completed_stages.append(
        CompletedStage(
            stage=stage,
            completed_at=now_iso(),
            artifacts=artifacts or [],
        )
    )
    save_checkpoint(root, cp)
    return cp


# ── resume pack ──


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
        current_branch=cp.feature.current_branch if cp.feature else "",
        docs_baseline_ref=cp.feature.docs_baseline_ref if cp.feature else "",
        docs_baseline_at=cp.feature.docs_baseline_at if cp.feature else "",
        timestamp=now_iso(),
    )


def save_resume_pack(root: Path, pack: ResumePack) -> None:
    """Save a resume pack to disk."""
    YamlStore.save(root / RESUME_PACK_PATH, pack)


def load_resume_pack(root: Path) -> ResumePack:
    """Load an existing resume pack and validate the paired checkpoint."""
    path = root / RESUME_PACK_PATH
    if not path.exists():
        raise ResumePackNotFoundError(
            "No resume pack found. Run ai-sdlc init to start fresh."
        )

    try:
        pack = YamlStore.load(path, ResumePack)
    except YamlStoreError as exc:
        raise ResumePackError(
            "Resume pack corrupted. Please inspect .ai-sdlc/state/resume-pack.yaml manually."
        ) from exc

    load_checkpoint(root, strict=True)
    return pack


# ── working set ──


def build_working_set(root: Path, stage: str) -> WorkingSet:
    """Build the working set of context files for a given stage."""
    ws = WorkingSet()

    path_map = {
        "prd_path": _find_prd(root),
        "constitution_path": str(root / ".ai-sdlc" / "memory" / "constitution.md"),
        "tech_stack_path": str(root / ".ai-sdlc" / "profiles" / "tech-stack.yml"),
        "spec_path": _find_spec(root),
        "plan_path": _find_plan(root),
        "tasks_path": _find_tasks(root),
    }

    needed = STAGE_FILES.get(stage, [])
    active: list[str] = []
    for field in needed:
        value = path_map.get(field, "")
        if value and Path(value).exists():
            setattr(ws, field, value)
            active.append(value)

    ws.active_files = active
    return ws


def _find_prd(root: Path) -> str:
    """Find the PRD file in the project root."""
    for p in root.glob("*PRD*"):
        if p.is_file() and p.suffix == ".md":
            return str(p)
    for p in root.glob("*prd*"):
        if p.is_file() and p.suffix == ".md":
            return str(p)
    return ""


def _find_spec(root: Path) -> str:
    """Find the first spec.md in specs/."""
    for p in (root / "specs").rglob("spec.md"):
        return str(p)
    return ""


def _find_plan(root: Path) -> str:
    """Find the first plan.md in specs/."""
    for p in (root / "specs").rglob("plan.md"):
        return str(p)
    return ""


def _find_tasks(root: Path) -> str:
    """Find the first tasks.md in specs/."""
    for p in (root / "specs").rglob("tasks.md"):
        return str(p)
    return ""


def _load_checkpoint_candidate(
    root: Path,
    path: Path,
    *,
    strict: bool,
) -> Checkpoint:
    checkpoint = YamlStore.load(path, Checkpoint)
    if strict:
        _validate_checkpoint(root, checkpoint)
    return checkpoint


def _validate_checkpoint(root: Path, checkpoint: Checkpoint) -> None:
    """Validate checkpoint.yml against FR-054 recovery constraints."""
    if checkpoint.current_stage not in VALID_CHECKPOINT_STAGES:
        raise CheckpointLoadError(
            f"Invalid checkpoint current_stage: {checkpoint.current_stage}"
        )

    if not checkpoint.feature or not checkpoint.feature.spec_dir.strip():
        raise CheckpointLoadError("checkpoint feature.spec_dir is missing")

    if checkpoint.current_stage == "init":
        return

    if checkpoint.feature.id == "unknown":
        raise CheckpointLoadError("checkpoint spec_dir is unresolved for recovery")

    spec_dir = root / checkpoint.feature.spec_dir
    if not spec_dir.exists():
        raise CheckpointLoadError(
            f"checkpoint spec_dir does not exist: {checkpoint.feature.spec_dir}"
        )
