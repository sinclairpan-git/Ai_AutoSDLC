"""Tests for persisted P1 artifact contracts."""

from __future__ import annotations

from ai_sdlc.core.p1_artifacts import (
    load_execution_path,
    load_parallel_coordination_artifact,
    load_resume_point,
    save_execution_path,
    save_parallel_coordination_artifact,
    save_resume_point,
)
from ai_sdlc.models.state import MergeSimulation, OverlapResult, WorkerAssignment
from ai_sdlc.models.work import ExecutionPath, ExecutionPathStep, ResumePoint


def test_save_and_load_resume_point(tmp_path) -> None:
    resume_point = ResumePoint(
        stage="execute",
        batch=3,
        status="suspended",
        checkpoint_path=".ai-sdlc/state/checkpoint.yml",
        current_branch="feature/WI-001-dev",
    )

    path = save_resume_point(tmp_path, "WI-001", resume_point)
    loaded = load_resume_point(tmp_path, "WI-001")

    assert path.name == "resume-point.yaml"
    assert loaded == resume_point


def test_save_and_load_execution_path(tmp_path) -> None:
    execution_path = ExecutionPath(
        steps=[
            ExecutionPathStep(
                task_id="WI-001-MT-1",
                title="Assess current state",
                depends_on=[],
            ),
            ExecutionPathStep(
                task_id="WI-001-MT-2",
                title="Execute maintenance",
                depends_on=["WI-001-MT-1"],
            ),
        ]
    )

    path = save_execution_path(tmp_path, "WI-001", execution_path)
    loaded = load_execution_path(tmp_path, "WI-001")

    assert path.name == "execution-path.yaml"
    assert loaded == execution_path
    assert loaded.ordered_task_ids == ["WI-001-MT-1", "WI-001-MT-2"]


def test_save_and_load_parallel_coordination_artifact(tmp_path) -> None:
    assignments = [
        WorkerAssignment(
            worker_id="worker-1",
            worker_index=1,
            parallel_group="group-0",
            group_id="group-0",
            branch_name="feature/WI-001-worker-1",
            task_ids=["T1"],
            allowed_paths=["src/auth.py"],
            forbidden_paths=["src/payment.py"],
        )
    ]
    overlap = OverlapResult(
        has_overlap=False,
        has_conflicts=False,
        total_shared_files=0,
        recommendation="clean",
    )
    merge = MergeSimulation(
        success=True,
        merge_order=["feature/WI-001-worker-1"],
        predicted_conflicts=[],
        notes="No conflicts predicted.",
    )

    path = save_parallel_coordination_artifact(
        tmp_path,
        "WI-001",
        assignments=assignments,
        overlap_result=overlap,
        merge_simulation=merge,
    )
    loaded = load_parallel_coordination_artifact(tmp_path, "WI-001")

    assert path.name == "parallel-coordination.yaml"
    assert loaded is not None
    assert loaded.worker_count == 1
    assert loaded.merge_order == ["feature/WI-001-worker-1"]
