"""Flow test: multi-agent parallel planning end-to-end."""

from __future__ import annotations

from ai_sdlc.models.execution import Task
from ai_sdlc.models.parallel import ParallelPolicy
from ai_sdlc.parallel.merge_simulator import simulate_merge
from ai_sdlc.parallel.overlap_detector import detect_overlaps
from ai_sdlc.parallel.splitter import split_into_groups
from ai_sdlc.parallel.worker_assigner import assign_workers


def _task(
    tid: str,
    files: list[str] | None = None,
    parallel: bool = True,
    depends: list[str] | None = None,
) -> Task:
    return Task(
        task_id=tid,
        title=f"Task {tid}",
        file_paths=files or [],
        parallelizable=parallel,
        depends_on=depends or [],
    )


class TestParallelPlanningFlow:
    """End-to-end: tasks → split → assign → overlap check → merge simulation."""

    def test_clean_parallel_flow(self) -> None:
        """3 independent tasks with no file overlap → clean merge."""
        tasks = [
            _task("T1", ["src/auth/handler.py", "src/auth/models.py"]),
            _task("T2", ["src/payment/processor.py"]),
            _task("T3", ["src/notification/sender.py"]),
        ]
        policy = ParallelPolicy(enabled=True, max_workers=3)

        groups = split_into_groups(tasks, policy)
        assert len(groups) >= 1

        assignments = assign_workers("WI-PAR-001", groups, policy)
        assert len(assignments) >= 1

        overlap = detect_overlaps(groups)
        assert not overlap.has_conflicts

        merge = simulate_merge(assignments, overlap)
        assert merge.success
        assert len(merge.predicted_conflicts) == 0

    def test_conflict_detection_flow(self) -> None:
        """2 tasks sharing a file → conflict detected → merge predicts failure."""
        tasks = [
            _task("T1", ["src/shared/config.py", "src/auth/handler.py"]),
            _task("T2", ["src/shared/config.py", "src/payment/processor.py"]),
        ]
        policy = ParallelPolicy(enabled=True, max_workers=2)

        groups = split_into_groups(tasks, policy)
        parallel_groups = {k: v for k, v in groups.items() if k != "group-seq"}
        assert len(parallel_groups) == 2

        overlap = detect_overlaps(groups)
        assert overlap.has_conflicts
        assert "src/shared/config.py" in overlap.conflicting_files

        assignments = assign_workers("WI-PAR-002", groups, policy)
        merge = simulate_merge(assignments, overlap)
        assert not merge.success
        assert any("config.py" in c for c in merge.predicted_conflicts)

    def test_mixed_sequential_parallel(self) -> None:
        """Mix of parallel + sequential tasks → sequential in own group."""
        tasks = [
            _task("T1", ["a.py"], parallel=True),
            _task("T2", ["b.py"], parallel=True),
            _task("T3", parallel=False),
        ]
        policy = ParallelPolicy(enabled=True, max_workers=3)

        groups = split_into_groups(tasks, policy)
        assert "group-seq" in groups
        assert len(groups["group-seq"]) == 1

    def test_disabled_policy_single_flow(self) -> None:
        """Disabled parallel policy → all tasks in one group, clean merge."""
        tasks = [_task("T1", ["a.py"]), _task("T2", ["b.py"])]
        policy = ParallelPolicy(enabled=False)

        groups = split_into_groups(tasks, policy)
        assert len(groups) == 1
