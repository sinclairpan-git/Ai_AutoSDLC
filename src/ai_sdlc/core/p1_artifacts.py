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


def _dedupe_text_items(values: list[str] | tuple[str, ...] | None) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _dedupe_pair_items(
    values: list[tuple[int, int]] | tuple[tuple[int, int], ...] | None,
) -> list[tuple[int, int]]:
    deduped: list[tuple[int, int]] = []
    for value in values or []:
        pair = tuple(value)
        if len(pair) != 2:
            continue
        normalized = (int(pair[0]), int(pair[1]))
        if normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _normalize_worker_assignment(
    assignment: WorkerAssignment,
) -> WorkerAssignment:
    return WorkerAssignment(
        worker_id=assignment.worker_id,
        worker_index=assignment.worker_index,
        parallel_group=assignment.parallel_group,
        group_id=assignment.group_id,
        task_ids=list(assignment.task_ids),
        branch_name=assignment.branch_name,
        allowed_paths=_dedupe_text_items(assignment.allowed_paths),
        forbidden_paths=_dedupe_text_items(assignment.forbidden_paths),
        contract_id=assignment.contract_id,
    )


def _normalize_overlap_result(result: OverlapResult) -> OverlapResult:
    overlapping_files = _dedupe_text_items(result.overlapping_files)
    conflicting_files = {
        str(path): _dedupe_text_items(workers)
        for path, workers in result.conflicting_files.items()
    }
    conflicting_workers = _dedupe_pair_items(result.conflicting_workers)
    return OverlapResult(
        has_overlap=result.has_overlap,
        has_conflicts=result.has_conflicts,
        overlapping_files=overlapping_files,
        conflicting_files=conflicting_files,
        conflicting_workers=conflicting_workers,
        total_shared_files=len(overlapping_files),
        recommendation=result.recommendation,
        details=result.details,
    )


def _normalize_merge_simulation(result: MergeSimulation) -> MergeSimulation:
    return MergeSimulation(
        success=result.success,
        conflicts=_dedupe_text_items(result.conflicts),
        predicted_conflicts=_dedupe_text_items(result.predicted_conflicts),
        merge_order=list(result.merge_order),
        notes=result.notes,
    )


def _normalize_parallel_coordination_artifact(
    artifact: ParallelCoordinationArtifact,
) -> ParallelCoordinationArtifact:
    return ParallelCoordinationArtifact(
        work_item_id=artifact.work_item_id,
        group_task_ids={str(group_id): list(task_ids) for group_id, task_ids in artifact.group_task_ids.items()},
        assignments=[
            _normalize_worker_assignment(assignment) for assignment in artifact.assignments
        ],
        overlap_result=_normalize_overlap_result(artifact.overlap_result),
        merge_simulation=_normalize_merge_simulation(artifact.merge_simulation),
    )


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
    payload = _normalize_parallel_coordination_artifact(payload)
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
    return _normalize_parallel_coordination_artifact(
        YamlStore.load(path, ParallelCoordinationArtifact)
    )
