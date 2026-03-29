"""Persistence helpers for P1 runtime artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ai_sdlc.core.config import YamlStore
from ai_sdlc.models.state import (
    MergeSimulation,
    OverlapResult,
    ParallelCoordinationArtifact,
    WorkerAssignment,
)
from ai_sdlc.models.work import (
    ExecutionPath,
    FreezeSnapshot,
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    ResumePoint,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR

_REVIEWER_DECISION_FILENAME = "reviewer-decision.yaml"
_REVIEWER_DECISION_PREFIX = "reviewer-decision-"


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


def _reviewer_decision_path(
    root: Path,
    work_item_id: str,
    checkpoint: PrdReviewerCheckpoint | None = None,
) -> Path:
    base = work_item_root(root, work_item_id)
    if checkpoint is None:
        return base / _REVIEWER_DECISION_FILENAME
    checkpoint_slug = checkpoint.value.replace("_", "-")
    return base / f"{_REVIEWER_DECISION_PREFIX}{checkpoint_slug}.yaml"


def _parse_timestamp(timestamp: str) -> datetime:
    if not timestamp:
        return datetime.min.replace(tzinfo=UTC)
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _latest_reviewer_decision(
    decisions: list[PrdReviewerDecision],
) -> PrdReviewerDecision | None:
    if not decisions:
        return None
    return max(
        decisions,
        key=lambda decision: (
            _parse_timestamp(decision.timestamp),
            decision.checkpoint.value,
        ),
    )


def save_reviewer_decision(
    root: Path,
    work_item_id: str,
    reviewer_decision: PrdReviewerDecision,
) -> Path:
    path = _reviewer_decision_path(root, work_item_id, reviewer_decision.checkpoint)
    YamlStore.save(path, reviewer_decision)
    return path


def load_reviewer_decision(
    root: Path,
    work_item_id: str,
) -> PrdReviewerDecision | None:
    return load_latest_reviewer_decision(root, work_item_id)


def load_reviewer_decision_for_checkpoint(
    root: Path,
    work_item_id: str,
    checkpoint: PrdReviewerCheckpoint,
) -> PrdReviewerDecision | None:
    path = _reviewer_decision_path(root, work_item_id, checkpoint)
    if path.exists():
        return YamlStore.load(path, PrdReviewerDecision)
    return None


def load_latest_reviewer_decision(
    root: Path,
    work_item_id: str,
) -> PrdReviewerDecision | None:
    decisions: list[PrdReviewerDecision] = []
    for checkpoint in PrdReviewerCheckpoint:
        path = _reviewer_decision_path(root, work_item_id, checkpoint)
        if path.exists():
            decisions.append(YamlStore.load(path, PrdReviewerDecision))

    latest = _latest_reviewer_decision(decisions)
    if latest is not None:
        return latest

    legacy_path = _reviewer_decision_path(root, work_item_id)
    if legacy_path.exists():
        return YamlStore.load(legacy_path, PrdReviewerDecision)
    return None


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
