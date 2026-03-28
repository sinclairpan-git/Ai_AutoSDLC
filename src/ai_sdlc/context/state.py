"""Checkpoint, resume-pack, and working-set management."""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from collections.abc import Callable
from pathlib import Path

from ai_sdlc.core.config import YamlStore, YamlStoreError
from ai_sdlc.models.state import (
    Checkpoint,
    CompletedStage,
    ExecutionPlan,
    ResumePack,
    RuntimeState,
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


ResumePackObserver = Callable[[str], None]


# ── checkpoint management ──


def save_checkpoint(root: Path, checkpoint: Checkpoint) -> None:
    """Save checkpoint, backing up the previous version."""
    cp_path = root / CHECKPOINT_PATH
    if cp_path.exists():
        bak = cp_path.with_suffix(".yml.bak")
        shutil.copy2(cp_path, bak)
    checkpoint.pipeline_last_updated = now_iso()
    YamlStore.save(cp_path, checkpoint)


def load_checkpoint(root: Path, *, strict: bool = False, warn: bool = True) -> Checkpoint | None:
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
        if warn:
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
    return _build_resume_pack_from_checkpoint(root, cp)


def _build_resume_pack_from_checkpoint(root: Path, cp: Checkpoint) -> ResumePack:
    work_item_id = active_work_item_id(cp)
    runtime = load_runtime_state(root, work_item_id) if work_item_id else None
    summary = load_latest_summary(root, work_item_id) if work_item_id else ""
    ws = _build_resume_working_set(root, cp, work_item_id, summary)

    current_batch = 0
    last_task = ""
    if runtime is not None:
        current_batch = runtime.current_batch
        last_task = runtime.last_committed_task
    elif cp.execute_progress:
        current_batch = cp.execute_progress.current_batch
        last_task = cp.execute_progress.last_committed_task

    return ResumePack(
        current_stage=runtime.current_stage if runtime and runtime.current_stage else cp.current_stage,
        current_batch=current_batch,
        last_committed_task=last_task,
        working_set_snapshot=ws,
        current_branch=(
            runtime.current_branch
            if runtime and runtime.current_branch
            else (cp.feature.current_branch if cp.feature else "")
        ),
        docs_baseline_ref=cp.feature.docs_baseline_ref if cp.feature else "",
        docs_baseline_at=cp.feature.docs_baseline_at if cp.feature else "",
        timestamp=now_iso(),
        checkpoint_last_updated=cp.pipeline_last_updated,
        checkpoint_fingerprint=_checkpoint_fingerprint(cp),
    )


def save_resume_pack(root: Path, pack: ResumePack) -> None:
    """Save a resume pack to disk."""
    checkpoint = load_checkpoint(root)
    work_item_id = active_work_item_id(checkpoint)
    _write_resume_pack_files(root, pack, work_item_id)


def load_resume_pack(
    root: Path,
    *,
    observer: ResumePackObserver | None = None,
    event_log: list[str] | None = None,
) -> ResumePack:
    """Load resume-pack.yaml, rebuilding it from checkpoint when safe."""
    checkpoint = load_checkpoint(root, strict=True)
    if checkpoint is None:
        raise CheckpointLoadError("checkpoint.yml not found")

    work_item_id = active_work_item_id(checkpoint)
    root_pack, root_issue = _load_resume_pack_candidate(
        root / RESUME_PACK_PATH,
        checkpoint,
    )
    scoped_issue = None
    if work_item_id:
        scoped_pack, scoped_issue = _load_resume_pack_candidate(
            work_item_resume_pack_path(root, work_item_id),
            checkpoint,
        )
        if (
            root_issue is None
            and scoped_issue is None
            and root_pack is not None
            and scoped_pack is not None
            and root_pack.model_dump(mode="json") != scoped_pack.model_dump(mode="json")
        ):
            scoped_issue = "stale"

    issue = root_issue or scoped_issue
    if issue is not None:
        _emit_resume_pack_event(
            f"resume-pack {issue}; rebuilding from checkpoint",
            observer=observer,
            event_log=event_log,
        )
        pack = _build_resume_pack_from_checkpoint(root, checkpoint)
        _write_resume_pack_files(root, pack, work_item_id)
        _emit_resume_pack_event(
            "resume-pack rebuilt successfully",
            observer=observer,
            event_log=event_log,
        )
        return pack

    if root_pack is None:
        raise ResumePackNotFoundError(
            "No resume pack found. Run ai-sdlc init to start fresh."
        )
    return root_pack


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


def active_work_item_id(checkpoint: Checkpoint | None) -> str:
    """Resolve the active work item id from a checkpoint."""
    if checkpoint is None:
        return ""
    linked = (checkpoint.linked_wi_id or "").strip()
    if linked:
        return linked
    if checkpoint.feature and checkpoint.feature.id != "unknown":
        return checkpoint.feature.id
    return ""


def work_item_dir(root: Path, work_item_id: str) -> Path:
    """Return the canonical work-item artifact directory."""
    return root / ".ai-sdlc" / "work-items" / work_item_id


def execution_plan_path(root: Path, work_item_id: str) -> Path:
    """Return the formal execution plan artifact path."""
    return work_item_dir(root, work_item_id) / "execution-plan.yaml"


def runtime_state_path(root: Path, work_item_id: str) -> Path:
    """Return the formal runtime artifact path."""
    return work_item_dir(root, work_item_id) / "runtime.yaml"


def working_set_path(root: Path, work_item_id: str) -> Path:
    """Return the formal working-set artifact path."""
    return work_item_dir(root, work_item_id) / "working-set.yaml"


def latest_summary_path(root: Path, work_item_id: str) -> Path:
    """Return the formal latest-summary artifact path."""
    return work_item_dir(root, work_item_id) / "latest-summary.md"


def work_item_resume_pack_path(root: Path, work_item_id: str) -> Path:
    """Return the work-item scoped resume-pack path."""
    return work_item_dir(root, work_item_id) / "resume-pack.yaml"


def save_execution_plan(root: Path, work_item_id: str, plan: ExecutionPlan) -> None:
    """Persist execution-plan.yaml for an active work item."""
    YamlStore.save(execution_plan_path(root, work_item_id), plan)


def load_execution_plan(root: Path, work_item_id: str) -> ExecutionPlan | None:
    """Load execution-plan.yaml if it exists."""
    return _load_optional_model(execution_plan_path(root, work_item_id), ExecutionPlan)


def save_runtime_state(root: Path, work_item_id: str, runtime: RuntimeState) -> None:
    """Persist runtime.yaml for an active work item."""
    YamlStore.save(runtime_state_path(root, work_item_id), runtime)


def load_runtime_state(root: Path, work_item_id: str) -> RuntimeState | None:
    """Load runtime.yaml if it exists."""
    return _load_optional_model(runtime_state_path(root, work_item_id), RuntimeState)


def save_working_set(root: Path, work_item_id: str, working_set: WorkingSet) -> None:
    """Persist working-set.yaml for an active work item."""
    YamlStore.save(working_set_path(root, work_item_id), working_set)


def load_working_set(root: Path, work_item_id: str) -> WorkingSet | None:
    """Load working-set.yaml if it exists."""
    return _load_optional_model(working_set_path(root, work_item_id), WorkingSet)


def save_latest_summary(root: Path, work_item_id: str, summary: str) -> None:
    """Persist latest-summary.md for an active work item."""
    path = latest_summary_path(root, work_item_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(summary, encoding="utf-8")


def load_latest_summary(root: Path, work_item_id: str) -> str:
    """Load latest-summary.md if it exists."""
    path = latest_summary_path(root, work_item_id)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_execute_working_set(
    root: Path,
    spec_dir: Path,
    tasks_file: Path,
    *,
    active_files: list[str] | None = None,
    context_summary: str = "",
) -> WorkingSet:
    """Build the formal working-set artifact for an executing work item."""
    ws = WorkingSet()

    if (spec_dir / "spec.md").exists():
        ws.spec_path = _relative_path(root, spec_dir / "spec.md")
    if (spec_dir / "plan.md").exists():
        ws.plan_path = _relative_path(root, spec_dir / "plan.md")
    if tasks_file.exists():
        ws.tasks_path = _relative_path(root, tasks_file)

    prd = _find_prd(root)
    if prd:
        ws.prd_path = _relative_string(root, prd)

    constitution = root / ".ai-sdlc" / "memory" / "constitution.md"
    if constitution.exists():
        ws.constitution_path = _relative_path(root, constitution)

    tech_stack = root / ".ai-sdlc" / "profiles" / "tech-stack.yml"
    if tech_stack.exists():
        ws.tech_stack_path = _relative_path(root, tech_stack)

    ws.active_files = active_files or []
    ws.context_summary = context_summary
    return ws


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

    if not checkpoint.pipeline_last_updated.strip():
        raise CheckpointLoadError("checkpoint pipeline_last_updated is missing")

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


def _build_resume_working_set(
    root: Path,
    checkpoint: Checkpoint,
    work_item_id: str,
    summary: str,
) -> WorkingSet:
    working_set = _build_resume_working_set_from_filesystem(root, checkpoint)
    artifact = load_working_set(root, work_item_id) if work_item_id else None
    if artifact is not None:
        for field in (
            "prd_path",
            "constitution_path",
            "tech_stack_path",
            "spec_path",
            "plan_path",
            "tasks_path",
        ):
            value = getattr(artifact, field)
            if value:
                setattr(working_set, field, value)
        if artifact.active_files:
            working_set.active_files = list(artifact.active_files)
        if artifact.context_summary:
            working_set.context_summary = artifact.context_summary

    if summary:
        working_set.context_summary = summary.strip()
    return working_set


def _build_resume_working_set_from_filesystem(
    root: Path,
    checkpoint: Checkpoint,
) -> WorkingSet:
    ws = WorkingSet()
    if checkpoint.feature:
        spec_dir = root / checkpoint.feature.spec_dir
        if (spec_dir / "spec.md").exists():
            ws.spec_path = str(spec_dir / "spec.md")
        if (spec_dir / "plan.md").exists():
            ws.plan_path = str(spec_dir / "plan.md")
        if (spec_dir / "tasks.md").exists():
            ws.tasks_path = str(spec_dir / "tasks.md")

    if checkpoint.prd_source and (root / checkpoint.prd_source).exists():
        ws.prd_path = checkpoint.prd_source

    constitution = root / ".ai-sdlc" / "memory" / "constitution.md"
    if constitution.exists():
        ws.constitution_path = str(constitution)

    tech_stack = root / ".ai-sdlc" / "profiles" / "tech-stack.yml"
    if tech_stack.exists():
        ws.tech_stack_path = str(tech_stack)
    return ws


def _load_optional_model(path: Path, model_class: type[ExecutionPlan | RuntimeState | WorkingSet]):
    if not path.exists():
        return None
    return YamlStore.load(path, model_class)


def _load_resume_pack_candidate(
    path: Path,
    checkpoint: Checkpoint,
) -> tuple[ResumePack | None, str | None]:
    if not path.exists():
        return None, "missing"

    try:
        pack = YamlStore.load(path, ResumePack)
    except YamlStoreError:
        return None, "corrupted"

    if _resume_pack_is_stale(pack, checkpoint):
        return pack, "stale"
    return pack, None


def _resume_pack_is_stale(pack: ResumePack, checkpoint: Checkpoint) -> bool:
    source = pack.checkpoint_last_updated.strip()
    target = checkpoint.pipeline_last_updated.strip()
    if not source or source != target:
        return True

    fingerprint = pack.checkpoint_fingerprint.strip()
    return not fingerprint or fingerprint != _checkpoint_fingerprint(checkpoint)


def _emit_resume_pack_event(
    message: str,
    *,
    observer: ResumePackObserver | None,
    event_log: list[str] | None,
) -> None:
    logger.info(message)
    if event_log is not None:
        event_log.append(message)
    if observer is not None:
        observer(message)


def _write_resume_pack_files(root: Path, pack: ResumePack, work_item_id: str) -> None:
    root_path = root / RESUME_PACK_PATH
    if not work_item_id:
        YamlStore.save(root_path, pack)
        return

    scoped_path = work_item_resume_pack_path(root, work_item_id)
    staged_root = _staged_resume_pack_path(root_path)
    staged_scoped = _staged_resume_pack_path(scoped_path)
    try:
        YamlStore.save(staged_root, pack)
        YamlStore.save(staged_scoped, pack)
        staged_scoped.replace(scoped_path)
        staged_root.replace(root_path)
    finally:
        staged_root.unlink(missing_ok=True)
        staged_scoped.unlink(missing_ok=True)


def _staged_resume_pack_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.staged")


def _checkpoint_fingerprint(checkpoint: Checkpoint) -> str:
    payload = json.dumps(
        checkpoint.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _relative_string(root: Path, raw_path: str) -> str:
    return _relative_path(root, Path(raw_path))


def _relative_path(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
