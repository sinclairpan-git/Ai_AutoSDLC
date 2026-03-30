"""Tests for multi-agent parallel foundation."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.backends.native import NativeBackend
from ai_sdlc.models.state import ParallelPolicy, Task, WorkerAssignment
from ai_sdlc.parallel.engine import (
    assign_workers,
    build_coordination_artifact,
    compute_file_ownership,
    detect_overlaps,
    emit_worker_lifecycle_fact,
    simulate_merge,
    split_into_groups,
)
from ai_sdlc.telemetry.enums import TelemetryEventStatus
from ai_sdlc.telemetry.paths import telemetry_local_root
from ai_sdlc.telemetry.runtime import RuntimeTelemetry


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _step_root(tmp_path: Path, telemetry: RuntimeTelemetry, step_id: str) -> Path:
    return (
        telemetry_local_root(tmp_path)
        / "sessions"
        / telemetry.goal_session_id
        / "runs"
        / telemetry.workflow_run_id
        / "steps"
        / step_id
    )


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


class TestSplitter:
    def test_disabled_policy_single_group(self) -> None:
        policy = ParallelPolicy(enabled=False)
        tasks = [_task("T1"), _task("T2")]
        groups = split_into_groups(tasks, policy)
        assert len(groups) == 1
        assert len(groups["group-0"]) == 2

    def test_empty_tasks(self) -> None:
        policy = ParallelPolicy(enabled=True)
        groups = split_into_groups([], policy)
        assert groups == {"group-0": []}

    def test_no_overlap_creates_one_group(self) -> None:
        policy = ParallelPolicy(enabled=True, max_workers=3)
        tasks = [
            _task("T1", ["src/auth.py"]),
            _task("T2", ["src/db.py"]),
        ]
        groups = split_into_groups(tasks, policy)
        parallel_groups = {k: v for k, v in groups.items() if k != "group-seq"}
        assert len(parallel_groups) == 1

    def test_overlap_creates_separate_groups(self) -> None:
        policy = ParallelPolicy(enabled=True, max_workers=3)
        tasks = [
            _task("T1", ["src/shared.py", "src/auth.py"]),
            _task("T2", ["src/shared.py", "src/db.py"]),
        ]
        groups = split_into_groups(tasks, policy)
        parallel_groups = {k: v for k, v in groups.items() if k != "group-seq"}
        assert len(parallel_groups) == 2

    def test_sequential_tasks_in_separate_group(self) -> None:
        policy = ParallelPolicy(enabled=True, max_workers=3)
        tasks = [
            _task("T1", ["src/a.py"], parallel=True),
            _task("T2", ["src/b.py"], parallel=False),
        ]
        groups = split_into_groups(tasks, policy)
        assert "group-seq" in groups
        assert len(groups["group-seq"]) == 1

    def test_respects_max_workers(self) -> None:
        policy = ParallelPolicy(enabled=True, max_workers=2)
        tasks = [
            _task("T1", ["a.py"]),
            _task("T2", ["b.py"]),
            _task("T3", ["c.py"]),
            _task("T4", ["d.py"]),
        ]
        groups = split_into_groups(tasks, policy)
        parallel_groups = {k: v for k, v in groups.items() if k != "group-seq"}
        assert len(parallel_groups) <= 3

    def test_all_sequential(self) -> None:
        policy = ParallelPolicy(enabled=True)
        tasks = [
            _task("T1", parallel=False),
            _task("T2", parallel=False),
        ]
        groups = split_into_groups(tasks, policy)
        assert "group-0" in groups

    def test_file_ownership(self) -> None:
        tasks = [
            _task("T1", ["src/a.py", "src/b.py"]),
            _task("T2", ["src/b.py", "src/c.py"]),
        ]
        ownership = compute_file_ownership(tasks)
        assert ownership["src/a.py"] == ["T1"]
        assert set(ownership["src/b.py"]) == {"T1", "T2"}


class TestWorkerAssigner:
    def test_assigns_branches(self) -> None:
        groups = {
            "group-0": [_task("T1", ["a.py"])],
            "group-1": [_task("T2", ["b.py"])],
        }
        policy = ParallelPolicy(enabled=True, max_workers=3)
        assignments = assign_workers("WI-001", groups, policy)
        assert len(assignments) == 2
        branches = {a.branch_name for a in assignments}
        assert any("worker-1" in b for b in branches)
        assert any("worker-2" in b for b in branches)

    def test_sequential_group_uses_dev_branch(self) -> None:
        groups = {
            "group-0": [_task("T1", ["a.py"])],
            "group-seq": [_task("T2", parallel=False)],
        }
        policy = ParallelPolicy(enabled=True)
        assignments = assign_workers("WI-002", groups, policy)
        seq = next(a for a in assignments if a.group_id == "group-seq")
        assert "dev" in seq.branch_name

    def test_forbidden_paths_computed(self) -> None:
        groups = {
            "group-0": [_task("T1", ["src/a.py"])],
            "group-1": [_task("T2", ["src/b.py"])],
        }
        policy = ParallelPolicy(enabled=True)
        assignments = assign_workers("WI-003", groups, policy)
        g0 = next(a for a in assignments if a.group_id == "group-0")
        assert "src/b.py" in g0.forbidden_paths

    def test_assigns_worker_index_and_parallel_group(self) -> None:
        groups = {
            "group-0": [_task("T1", ["src/a.py"])],
            "group-1": [_task("T2", ["src/b.py"])],
            "group-seq": [_task("T3", ["src/c.py"], parallel=False)],
        }
        policy = ParallelPolicy(enabled=True)

        assignments = assign_workers("WI-004", groups, policy)

        group0 = next(a for a in assignments if a.group_id == "group-0")
        seq = next(a for a in assignments if a.group_id == "group-seq")
        assert group0.worker_id == "worker-1"
        assert group0.worker_index == 1
        assert group0.parallel_group == "group-0"
        assert seq.worker_id == "worker-main"
        assert seq.parallel_group == "group-seq"

    def test_emit_worker_lifecycle_fact_records_worker_id_in_fact_layer(
        self, tmp_path: Path
    ) -> None:
        telemetry = RuntimeTelemetry(tmp_path)
        telemetry.open_workflow_run()
        step_id = telemetry.begin_step("execute")
        assignment = WorkerAssignment(
            worker_id="worker-1",
            group_id="group-0",
            branch_name="feature/WI-005-worker-1",
            task_ids=["T1"],
        )

        emit_worker_lifecycle_fact(
            telemetry,
            step_id=step_id,
            assignment=assignment,
            phase="started",
            status=TelemetryEventStatus.STARTED,
        )

        step_root = _step_root(tmp_path, telemetry, step_id)
        events = _read_ndjson(step_root / "events.ndjson")
        evidence = _read_ndjson(step_root / "evidence.ndjson")
        assert events[-1]["trace_layer"] == "tool"
        assert events[-1]["status"] == "started"
        assert evidence[-1]["locator"] == "trace://worker-lifecycle/worker-1/started"

    def test_native_backend_records_delegation_boundary_without_completion(
        self, tmp_path: Path
    ) -> None:
        telemetry = RuntimeTelemetry(tmp_path)
        telemetry.open_workflow_run()
        step_id = telemetry.begin_step("execute")

        result = NativeBackend().execute_task(
            "T-native",
            {
                "telemetry": telemetry,
                "step_id": step_id,
                "worker_id": "worker-2",
            },
        )

        step_root = _step_root(tmp_path, telemetry, step_id)
        events = _read_ndjson(step_root / "events.ndjson")
        evidence = _read_ndjson(step_root / "evidence.ndjson")

        assert result == "pending"
        assert events[-1]["trace_layer"] == "tool"
        assert events[-1]["status"] == "started"
        assert evidence[-1]["locator"] == "trace://native-delegation/T-native/worker-2"


class TestOverlapDetector:
    def test_no_overlaps(self) -> None:
        groups = {
            "group-0": [_task("T1", ["a.py"])],
            "group-1": [_task("T2", ["b.py"])],
        }
        result = detect_overlaps(groups)
        assert not result.has_conflicts
        assert result.total_shared_files == 0

    def test_detects_overlap(self) -> None:
        groups = {
            "group-0": [_task("T1", ["shared.py", "a.py"])],
            "group-1": [_task("T2", ["shared.py", "b.py"])],
        }
        result = detect_overlaps(groups)
        assert result.has_conflicts
        assert "shared.py" in result.conflicting_files
        assert result.total_shared_files == 1

    def test_recommendation_text(self) -> None:
        groups = {
            "group-0": [_task("T1", ["x.py"])],
            "group-1": [_task("T2", ["x.py"])],
        }
        result = detect_overlaps(groups)
        assert (
            "conflicting" in result.recommendation.lower()
            or "x.py" in result.recommendation
        )


class TestMergeSimulator:
    def test_clean_merge(self) -> None:
        from ai_sdlc.parallel.engine import detect_overlaps

        groups = {
            "group-0": [_task("T1", ["a.py"])],
            "group-1": [_task("T2", ["b.py"])],
        }
        overlap = detect_overlaps(groups)
        assignments = [
            WorkerAssignment(
                worker_id="w1",
                group_id="group-0",
                branch_name="feature/WI-001-worker-1",
                task_ids=["T1"],
            ),
            WorkerAssignment(
                worker_id="w2",
                group_id="group-1",
                branch_name="feature/WI-001-worker-2",
                task_ids=["T2"],
            ),
        ]
        sim = simulate_merge(assignments, overlap)
        assert sim.success
        assert len(sim.merge_order) == 2
        assert not sim.predicted_conflicts

    def test_conflict_predicted(self) -> None:
        from ai_sdlc.parallel.engine import detect_overlaps

        groups = {
            "group-0": [_task("T1", ["shared.py"])],
            "group-1": [_task("T2", ["shared.py"])],
        }
        overlap = detect_overlaps(groups)
        assignments = [
            WorkerAssignment(
                worker_id="w1",
                group_id="group-0",
                branch_name="feature/WI-001-worker-1",
                task_ids=["T1"],
            ),
            WorkerAssignment(
                worker_id="w2",
                group_id="group-1",
                branch_name="feature/WI-001-worker-2",
                task_ids=["T2"],
            ),
        ]
        sim = simulate_merge(assignments, overlap)
        assert not sim.success
        assert len(sim.predicted_conflicts) == 1
        assert "shared.py" in sim.predicted_conflicts[0]

    def test_empty_assignments(self) -> None:
        from ai_sdlc.models.state import OverlapResult

        overlap = OverlapResult(has_conflicts=False)
        sim = simulate_merge([], overlap)
        assert sim.success
        assert sim.merge_order == []

    def test_merge_order_sequential_first(self) -> None:
        from ai_sdlc.models.state import OverlapResult

        overlap = OverlapResult(has_conflicts=False)
        assignments = [
            WorkerAssignment(
                worker_id="w1",
                group_id="group-0",
                branch_name="feature/WI-001-worker-1",
                task_ids=["T1"],
            ),
            WorkerAssignment(
                worker_id="w-main",
                group_id="group-seq",
                branch_name="feature/WI-001-dev",
                task_ids=["T0"],
            ),
        ]
        sim = simulate_merge(assignments, overlap)
        assert sim.merge_order[0] == "feature/WI-001-dev"


class TestCoordinationArtifact:
    def test_builds_and_persists_coordination_artifact(self, tmp_path) -> None:
        groups = {
            "group-0": [_task("T1", ["src/auth.py"])],
            "group-1": [_task("T2", ["src/payment.py"])],
        }
        policy = ParallelPolicy(enabled=True, max_workers=2)

        assignments = assign_workers("WI-COORD-001", groups, policy)
        overlap = detect_overlaps(groups)
        merge = simulate_merge(assignments, overlap)

        artifact = build_coordination_artifact(
            "WI-COORD-001",
            groups,
            assignments,
            overlap,
            merge,
            root=tmp_path,
        )

        assert artifact.worker_count == 2
        assert artifact.group_task_ids == {
            "group-0": ["T1"],
            "group-1": ["T2"],
        }
        assert artifact.merge_order == merge.merge_order
        assert (
            tmp_path
            / ".ai-sdlc"
            / "work-items"
            / "WI-COORD-001"
            / "parallel-coordination.yaml"
        ).exists()
