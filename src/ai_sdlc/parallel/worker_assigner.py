"""Worker Assigner — assign task groups to worker branches."""

from __future__ import annotations

import logging

from ai_sdlc.models.parallel import ParallelPolicy, WorkerAssignment

logger = logging.getLogger(__name__)


def assign_workers(
    work_item_id: str,
    groups: dict[str, list[object]],
    policy: ParallelPolicy,
) -> list[WorkerAssignment]:
    """Create worker assignments for each parallel group.

    Each group gets a dedicated worker branch following the naming convention:
    feature/<work_item_id>-worker-<N>

    Args:
        work_item_id: The work item being executed.
        groups: Dict of group_id → tasks from splitter.
        policy: Parallel execution policy.

    Returns:
        List of WorkerAssignment objects.
    """
    assignments: list[WorkerAssignment] = []
    worker_num = 1

    for group_id, tasks in sorted(groups.items()):
        if group_id == "group-seq":
            branch = f"feature/{work_item_id}-dev"
        else:
            branch = f"feature/{work_item_id}-worker-{worker_num}"
            worker_num += 1

        task_ids = [getattr(t, "task_id", str(t)) for t in tasks]
        file_paths = set()
        for t in tasks:
            file_paths.update(getattr(t, "file_paths", []))
            file_paths.update(getattr(t, "allowed_paths", []))

        assignments.append(
            WorkerAssignment(
                worker_id=f"worker-{worker_num - 1}"
                if group_id != "group-seq"
                else "worker-main",
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
