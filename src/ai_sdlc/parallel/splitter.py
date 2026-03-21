"""Task Splitter — partition tasks into parallel groups based on file boundaries."""

from __future__ import annotations

import logging
from collections import defaultdict

from ai_sdlc.models.execution import Task
from ai_sdlc.models.parallel import ParallelPolicy

logger = logging.getLogger(__name__)


def split_into_groups(
    tasks: list[Task],
    policy: ParallelPolicy,
) -> dict[str, list[Task]]:
    """Partition tasks into parallel execution groups.

    Groups are formed such that tasks within a group do not share file paths
    (no overlap). Sequential dependencies are respected: if task B depends on
    task A, they must be in the same group with correct ordering, or B must
    be in a later group.

    Args:
        tasks: All tasks in the execution plan.
        policy: Parallel execution policy with max_workers, etc.

    Returns:
        Dict mapping group_id → list of tasks in that group.
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
            if len(group_files) > max_groups:
                break
            if not task_files & group_files[gid] and _dependencies_satisfied(
                task, group_tasks[gid]
            ):
                group_files[gid].update(task_files)
                group_tasks[gid].append(task)
                assigned = True
                break

        if not assigned:
            gid = f"group-{len(group_files)}"
            group_files[gid] = set(task_files)
            group_tasks[gid] = [task]

    return group_tasks


def _dependencies_satisfied(task: Task, group_tasks: list[Task]) -> bool:
    """Check that none of the task's dependencies are in the same group (unsatisfied)."""
    group_ids = {t.task_id for t in group_tasks}
    return not bool(set(task.depends_on) & group_ids)


def compute_file_ownership(tasks: list[Task]) -> dict[str, list[str]]:
    """Compute which tasks touch which files.

    Returns:
        Dict mapping file_path → list of task_ids that reference it.
    """
    ownership: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        for fp in task.file_paths:
            ownership[fp].append(task.task_id)
        for fp in task.allowed_paths:
            ownership[fp].append(task.task_id)
    return dict(ownership)
