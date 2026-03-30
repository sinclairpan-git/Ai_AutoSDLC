"""Multi-agent parallel execution: splitting, overlap detection, worker assignment, merge simulation."""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path

from ai_sdlc.core.p1_artifacts import save_parallel_coordination_artifact
from ai_sdlc.models.state import (
    MergeSimulation,
    OverlapResult,
    ParallelCoordinationArtifact,
    ParallelPolicy,
    Task,
    WorkerAssignment,
)
from ai_sdlc.telemetry.enums import TelemetryEventStatus
from ai_sdlc.telemetry.runtime import RuntimeTelemetry

logger = logging.getLogger(__name__)


# ── task splitter ──


def split_into_groups(
    tasks: list[Task],
    policy: ParallelPolicy,
) -> dict[str, list[Task]]:
    """Partition tasks into parallel execution groups.

    Groups are formed such that tasks within a group do not share file paths
    (no overlap). Sequential dependencies are respected.
    """
    if not policy.enabled or not tasks:
        return {"group-0": tasks}

    parallelizable = [t for t in tasks if t.parallelizable]
    sequential = [t for t in tasks if not t.parallelizable]

    if not parallelizable:
        return {"group-0": tasks}

    groups = _greedy_partition(parallelizable, policy.max_workers)

    if sequential:
        groups["group-seq"] = sequential

    return groups


def _greedy_partition(
    tasks: list[Task],
    max_groups: int,
) -> dict[str, list[Task]]:
    """Greedily assign tasks to groups avoiding file path overlaps."""
    group_files: dict[str, set[str]] = {}
    group_tasks: dict[str, list[Task]] = {}

    for task in tasks:
        assigned = False
        task_files = set(task.file_paths + task.allowed_paths)

        for gid in sorted(group_files.keys()):
            if not task_files & group_files[gid] and _dependencies_satisfied(
                task, group_tasks[gid]
            ):
                group_files[gid].update(task_files)
                group_tasks[gid].append(task)
                assigned = True
                break

        if not assigned:
            if len(group_files) < max_groups:
                gid = f"group-{len(group_files)}"
                group_files[gid] = set(task_files)
                group_tasks[gid] = [task]
            else:
                smallest = min(group_tasks, key=lambda g: len(group_tasks[g]))
                group_files[smallest].update(task_files)
                group_tasks[smallest].append(task)

    return group_tasks


def _dependencies_satisfied(task: Task, group_tasks: list[Task]) -> bool:
    """Check that none of the task's dependencies are in the same group (unsatisfied)."""
    group_ids = {t.task_id for t in group_tasks}
    return not bool(set(task.depends_on) & group_ids)


def compute_file_ownership(tasks: list[Task]) -> dict[str, list[str]]:
    """Compute which tasks touch which files."""
    ownership: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        for fp in task.file_paths:
            ownership[fp].append(task.task_id)
        for fp in task.allowed_paths:
            ownership[fp].append(task.task_id)
    return dict(ownership)


# ── overlap detector ──


def detect_overlaps(groups: dict[str, list[Task]]) -> OverlapResult:
    """Detect file path overlaps between parallel task groups."""
    file_to_groups: dict[str, list[str]] = defaultdict(list)

    for gid, tasks in groups.items():
        group_files: set[str] = set()
        for t in tasks:
            group_files.update(t.file_paths)
            group_files.update(t.allowed_paths)
        for fp in group_files:
            file_to_groups[fp].append(gid)

    conflicts: dict[str, list[str]] = {}
    for fp, gids in file_to_groups.items():
        if len(gids) > 1:
            conflicts[fp] = gids

    has_issues = bool(conflicts)
    return OverlapResult(
        has_overlap=has_issues,
        has_conflicts=has_issues,
        conflicting_files=conflicts,
        total_shared_files=len(conflicts),
        recommendation=_generate_overlap_recommendation(conflicts),
    )


def _generate_overlap_recommendation(conflicts: dict[str, list[str]]) -> str:
    if not conflicts:
        return "No file overlaps detected. Safe to proceed with parallel execution."

    file_list = ", ".join(sorted(conflicts.keys())[:5])
    group_count = len({g for groups in conflicts.values() for g in groups})
    return (
        f"Found {len(conflicts)} conflicting file(s) across {group_count} groups: "
        f"{file_list}. Consider merging affected groups or adding interface contracts."
    )


# ── worker assigner ──


def assign_workers(
    work_item_id: str,
    groups: dict[str, list[object]],
    policy: ParallelPolicy,
) -> list[WorkerAssignment]:
    """Create worker assignments for each parallel group."""
    assignments: list[WorkerAssignment] = []
    worker_num = 1

    for group_id, tasks in sorted(groups.items()):
        if group_id == "group-seq":
            branch = f"feature/{work_item_id}-dev"
            worker_id = "worker-main"
            worker_index = 0
        else:
            branch = f"feature/{work_item_id}-worker-{worker_num}"
            worker_id = f"worker-{worker_num}"
            worker_index = worker_num
            worker_num += 1

        task_ids = [getattr(t, "task_id", str(t)) for t in tasks]
        file_paths = set()
        for t in tasks:
            file_paths.update(getattr(t, "file_paths", []))
            file_paths.update(getattr(t, "allowed_paths", []))

        assignments.append(
            WorkerAssignment(
                worker_id=worker_id,
                worker_index=worker_index,
                parallel_group=group_id,
                group_id=group_id,
                branch_name=branch,
                task_ids=task_ids,
                allowed_paths=sorted(file_paths),
                forbidden_paths=_compute_forbidden(
                    sorted(file_paths), groups, group_id
                ),
            )
        )

    return assignments


def emit_worker_lifecycle_fact(
    telemetry: RuntimeTelemetry,
    *,
    step_id: str | None,
    assignment: WorkerAssignment,
    phase: str,
    status: TelemetryEventStatus,
) -> None:
    """Append one worker-lifecycle fact to the active telemetry step scope."""
    telemetry.record_tool_event(
        step_id=step_id,
        status=status,
    )
    telemetry.record_tool_evidence(
        step_id=step_id,
        locator=f"trace://worker-lifecycle/{assignment.worker_id}/{phase}",
        digest=(
            f"worker:{assignment.worker_id};phase:{phase};group:{assignment.group_id};"
            f"branch:{assignment.branch_name};status:{status.value}"
        ),
    )


def _compute_forbidden(
    allowed: list[str],
    all_groups: dict[str, list[object]],
    current_group: str,
) -> list[str]:
    """Compute forbidden paths = files owned by other groups."""
    other_files: set[str] = set()
    for gid, tasks in all_groups.items():
        if gid == current_group:
            continue
        for t in tasks:
            other_files.update(getattr(t, "file_paths", []))
            other_files.update(getattr(t, "allowed_paths", []))
    return sorted(other_files - set(allowed))


# ── merge simulator ──


def simulate_merge(
    assignments: list[WorkerAssignment],
    overlap_result: OverlapResult,
) -> MergeSimulation:
    """Simulate merging all worker branches back into the dev branch."""
    if not assignments:
        return MergeSimulation(
            success=True,
            merge_order=[],
            predicted_conflicts=[],
            notes="No workers to merge.",
        )

    merge_order = _compute_merge_order(assignments)
    predicted_conflicts = _predict_conflicts(assignments, overlap_result)

    return MergeSimulation(
        success=len(predicted_conflicts) == 0,
        merge_order=merge_order,
        predicted_conflicts=predicted_conflicts,
        notes=_generate_merge_notes(merge_order, predicted_conflicts),
    )


def build_coordination_artifact(
    work_item_id: str,
    groups: dict[str, list[object]],
    assignments: list[WorkerAssignment],
    overlap_result: OverlapResult,
    merge_simulation: MergeSimulation,
    *,
    root: Path | None = None,
) -> ParallelCoordinationArtifact:
    """Create the persisted coordination truth for a parallel run."""
    artifact = ParallelCoordinationArtifact(
        work_item_id=work_item_id,
        group_task_ids={
            group_id: [getattr(task, "task_id", str(task)) for task in tasks]
            for group_id, tasks in groups.items()
        },
        assignments=assignments,
        overlap_result=overlap_result,
        merge_simulation=merge_simulation,
    )
    if root is not None:
        save_parallel_coordination_artifact(
            root,
            work_item_id,
            assignments=assignments,
            overlap_result=overlap_result,
            merge_simulation=merge_simulation,
            artifact=artifact,
        )
    return artifact


def _compute_merge_order(assignments: list[WorkerAssignment]) -> list[str]:
    """Determine safe merge order: sequential first, then parallel workers."""
    order: list[str] = []

    seq = [a for a in assignments if a.group_id == "group-seq"]
    parallel = [a for a in assignments if a.group_id != "group-seq"]

    for a in seq:
        order.append(a.branch_name)
    for a in sorted(parallel, key=lambda x: x.group_id):
        order.append(a.branch_name)

    return order


def _predict_conflicts(
    assignments: list[WorkerAssignment],
    overlap_result: OverlapResult,
) -> list[str]:
    """Predict merge conflicts based on overlap analysis."""
    if not overlap_result.has_conflicts:
        return []

    conflicts: list[str] = []
    for filepath, groups in overlap_result.conflicting_files.items():
        branches = []
        for a in assignments:
            if a.group_id in groups:
                branches.append(a.branch_name)
        if len(branches) > 1:
            conflicts.append(
                f"File '{filepath}' modified by branches: {', '.join(branches)}"
            )

    return conflicts


def _generate_merge_notes(merge_order: list[str], conflicts: list[str]) -> str:
    parts: list[str] = []
    parts.append(f"Merge order: {' → '.join(merge_order)}")
    if conflicts:
        parts.append(f"WARNING: {len(conflicts)} predicted conflict(s)")
    else:
        parts.append("No conflicts predicted. Merge should be clean.")
    return ". ".join(parts)
