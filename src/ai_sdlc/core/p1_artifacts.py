"""Persistence helpers for P1 runtime artifacts."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.config import YamlStore
from ai_sdlc.models.state import (
    MergeSimulation,
    OverlapResult,
    ParallelCoordinationArtifact,
    WorkerAssignment,
)
from ai_sdlc.models.work import ExecutionPath, FreezeSnapshot, ResumePoint
from ai_sdlc.utils.helpers import AI_SDLC_DIR


def work_item_root(root: Path, work_item_id: str) -> Path:
    return root / AI_SDLC_DIR / "work-items" / work_item_id


def save_freeze_snapshot(root: Path, work_item_id: str, snapshot: FreezeSnapshot) -> Path:
    path = work_item_root(root, work_item_id) / "freeze-snapshot.yaml"
    YamlStore.save(path, snapshot)
    return path


def save_resume_point(root: Path, work_item_id: str, resume_point: ResumePoint) -> Path:
    path = work_item_root(root, work_item_id) / "resume-point.yaml"
    YamlStore.save(path, resume_point)
    return path


def load_resume_point(root: Path, work_item_id: str) -> ResumePoint | None:
    path = work_item_root(root, work_item_id) / "resume-point.yaml"
    if not path.exists():
        return None
    return YamlStore.load(path, ResumePoint)


def save_execution_path(root: Path, work_item_id: str, execution_path: ExecutionPath) -> Path:
    path = work_item_root(root, work_item_id) / "execution-path.yaml"
    YamlStore.save(path, execution_path)
    return path


def load_execution_path(root: Path, work_item_id: str) -> ExecutionPath | None:
    path = work_item_root(root, work_item_id) / "execution-path.yaml"
    if not path.exists():
        return None
    return YamlStore.load(path, ExecutionPath)


def save_parallel_coordination_artifact(
    root: Path,
    work_item_id: str,
    *,
    assignments: list[WorkerAssignment],
    overlap_result: OverlapResult,
    merge_simulation: MergeSimulation,
    group_task_ids: dict[str, list[str]] | None = None,
    artifact: ParallelCoordinationArtifact | None = None,
) -> Path:
    payload = artifact or ParallelCoordinationArtifact(
        work_item_id=work_item_id,
        group_task_ids=group_task_ids or {},
        assignments=assignments,
        overlap_result=overlap_result,
        merge_simulation=merge_simulation,
    )
    path = work_item_root(root, work_item_id) / "parallel-coordination.yaml"
    YamlStore.save(path, payload)
    return path


def load_parallel_coordination_artifact(
    root: Path,
    work_item_id: str,
) -> ParallelCoordinationArtifact | None:
    path = work_item_root(root, work_item_id) / "parallel-coordination.yaml"
    if not path.exists():
        return None
    return YamlStore.load(path, ParallelCoordinationArtifact)
