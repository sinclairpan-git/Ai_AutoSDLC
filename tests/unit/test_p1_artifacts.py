"""Tests for persisted P1 artifact contracts."""

from __future__ import annotations

from ai_sdlc.core.config import YamlStore
from ai_sdlc.core.p1_artifacts import (
    load_execution_path,
    load_latest_reviewer_decision,
    load_parallel_coordination_artifact,
    load_resume_point,
    load_reviewer_decision_for_checkpoint,
    save_execution_path,
    save_parallel_coordination_artifact,
    save_resume_point,
    save_reviewer_decision,
    work_item_root,
)
from ai_sdlc.models.state import (
    MergeSimulation,
    OverlapResult,
    ParallelCoordinationArtifact,
    WorkerAssignment,
)
from ai_sdlc.models.work import (
    ExecutionPath,
    ExecutionPathStep,
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
    ResumePoint,
)


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


def test_save_and_load_reviewer_decisions_per_checkpoint(tmp_path) -> None:
    decisions = {
        PrdReviewerCheckpoint.PRD_FREEZE: PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
            decision=PrdReviewerDecisionKind.APPROVE,
            target="WI-001",
            reason="Looks good",
            next_action="Persist final_prd",
            timestamp="2026-03-29T10:00:00+08:00",
        ),
        PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE: PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
            decision=PrdReviewerDecisionKind.APPROVE,
            target="WI-001",
            reason="Docs baseline is aligned",
            next_action="Persist docs baseline",
            timestamp="2026-03-29T11:00:00+08:00",
        ),
        PrdReviewerCheckpoint.PRE_CLOSE: PrdReviewerDecision(
            checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
            decision=PrdReviewerDecisionKind.APPROVE,
            target="WI-001",
            reason="Ready to close",
            next_action="Archive work item",
            timestamp="2026-03-29T12:00:00+08:00",
        ),
    }

    saved_paths = {
        checkpoint: save_reviewer_decision(tmp_path, "WI-001", decision)
        for checkpoint, decision in decisions.items()
    }

    assert {path.name for path in saved_paths.values()} == {
        "reviewer-decision-prd-freeze.yaml",
        "reviewer-decision-docs-baseline-freeze.yaml",
        "reviewer-decision-pre-close.yaml",
    }

    for checkpoint, decision in decisions.items():
        loaded = load_reviewer_decision_for_checkpoint(tmp_path, "WI-001", checkpoint)
        assert loaded == decision
        assert loaded is not None
        assert loaded.to_status_view()["summary"] == f"{checkpoint.value}:approve -> WI-001"

    latest = load_latest_reviewer_decision(tmp_path, "WI-001")
    assert latest == decisions[PrdReviewerCheckpoint.PRE_CLOSE]
    assert latest is not None
    assert latest.to_status_view()["summary"] == "pre_close:approve -> WI-001"


def test_load_latest_reviewer_decision_falls_back_to_legacy_file(tmp_path) -> None:
    decision = PrdReviewerDecision(
        checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
        decision=PrdReviewerDecisionKind.APPROVE,
        target="WI-001",
        reason="Legacy artifact still valid",
        next_action="Persist final_prd",
        timestamp="2026-03-29T09:00:00+08:00",
    )

    legacy_path = work_item_root(tmp_path, "WI-001") / "reviewer-decision.yaml"
    YamlStore.save(legacy_path, decision)

    loaded = load_reviewer_decision_for_checkpoint(
        tmp_path,
        "WI-001",
        PrdReviewerCheckpoint.PRD_FREEZE,
    )
    latest = load_latest_reviewer_decision(tmp_path, "WI-001")

    assert legacy_path.name == "reviewer-decision.yaml"
    assert loaded is None
    assert latest == decision
    assert latest is not None
    assert latest.to_status_view()["summary"] == "prd_freeze:approve -> WI-001"


def test_legacy_reviewer_decision_does_not_satisfy_wrong_checkpoint(tmp_path) -> None:
    decision = PrdReviewerDecision(
        checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
        decision=PrdReviewerDecisionKind.APPROVE,
        target="WI-001",
        reason="Legacy artifact still valid for PRD freeze only",
        next_action="Persist final_prd",
        timestamp="2026-03-29T09:00:00+08:00",
    )

    legacy_path = work_item_root(tmp_path, "WI-001") / "reviewer-decision.yaml"
    YamlStore.save(legacy_path, decision)

    loaded = load_reviewer_decision_for_checkpoint(
        tmp_path,
        "WI-001",
        PrdReviewerCheckpoint.PRE_CLOSE,
    )
    latest = load_latest_reviewer_decision(tmp_path, "WI-001")

    assert loaded is None
    assert latest == decision


def test_legacy_reviewer_decision_does_not_satisfy_checkpoint_specific_loader(
    tmp_path,
) -> None:
    decision = PrdReviewerDecision(
        checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
        decision=PrdReviewerDecisionKind.APPROVE,
        target="WI-001",
        reason="Legacy artifact only",
        next_action="Persist final_prd",
        timestamp="2026-03-29T09:00:00+08:00",
    )

    legacy_path = work_item_root(tmp_path, "WI-001") / "reviewer-decision.yaml"
    YamlStore.save(legacy_path, decision)

    loaded = load_reviewer_decision_for_checkpoint(
        tmp_path,
        "WI-001",
        PrdReviewerCheckpoint.PRD_FREEZE,
    )
    latest = load_latest_reviewer_decision(tmp_path, "WI-001")

    assert loaded is None
    assert latest == decision


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


def test_save_parallel_coordination_artifact_deduplicates_repeated_entries(
    tmp_path,
) -> None:
    assignments = [
        WorkerAssignment(
            worker_id="worker-1",
            worker_index=1,
            parallel_group="group-0",
            group_id="group-0",
            branch_name="feature/WI-001-worker-1",
            task_ids=["T1", "T1"],
            allowed_paths=["src/auth.py", "src/auth.py"],
            forbidden_paths=["src/payment.py", "src/payment.py"],
        ),
        WorkerAssignment(
            worker_id="worker-1",
            worker_index=1,
            parallel_group="group-0",
            group_id="group-0",
            branch_name="feature/WI-001-worker-1",
            task_ids=["T1", "T1"],
            allowed_paths=["src/auth.py", "src/auth.py"],
            forbidden_paths=["src/payment.py", "src/payment.py"],
        ),
    ]
    overlap = OverlapResult(
        has_overlap=True,
        has_conflicts=True,
        overlapping_files=["src/auth.py", "src/auth.py"],
        conflicting_files={"src/auth.py": ["worker-1", "worker-1"]},
        conflicting_workers=[(1, 2), (1, 2)],
        total_shared_files=99,
        recommendation="review",
    )
    merge = MergeSimulation(
        success=True,
        conflicts=["src/auth.py", "src/auth.py"],
        predicted_conflicts=["src/auth.py", "src/auth.py"],
        merge_order=["feature/WI-001-worker-1", "feature/WI-001-worker-1"],
        notes="No conflicts predicted.",
    )

    save_parallel_coordination_artifact(
        tmp_path,
        "WI-001",
        assignments=assignments,
        overlap_result=overlap,
        merge_simulation=merge,
        group_task_ids={"group-0": ["T1", "T1"]},
    )
    loaded = load_parallel_coordination_artifact(tmp_path, "WI-001")

    assert loaded is not None
    assert loaded.group_task_ids == {"group-0": ["T1", "T1"]}
    assert loaded.worker_count == 2
    assert loaded.assignments[0].task_ids == ["T1", "T1"]
    assert loaded.assignments[0].allowed_paths == ["src/auth.py"]
    assert loaded.assignments[0].forbidden_paths == ["src/payment.py"]
    assert loaded.overlap_result.overlapping_files == ["src/auth.py"]
    assert loaded.overlap_result.conflicting_files == {"src/auth.py": ["worker-1"]}
    assert loaded.overlap_result.conflicting_workers == [(1, 2)]
    assert loaded.overlap_result.total_shared_files == 1
    assert loaded.merge_simulation.conflicts == ["src/auth.py"]
    assert loaded.merge_simulation.predicted_conflicts == ["src/auth.py"]
    assert loaded.merge_order == [
        "feature/WI-001-worker-1",
        "feature/WI-001-worker-1",
    ]


def test_load_parallel_coordination_artifact_deduplicates_legacy_repeated_entries(
    tmp_path,
) -> None:
    artifact = ParallelCoordinationArtifact(
        work_item_id="WI-001",
        group_task_ids={"group-0": ["T1", "T1"]},
        assignments=[
            WorkerAssignment(
                worker_id="worker-1",
                worker_index=1,
                parallel_group="group-0",
                group_id="group-0",
                branch_name="feature/WI-001-worker-1",
                task_ids=["T1", "T1"],
                allowed_paths=["src/auth.py", "src/auth.py"],
                forbidden_paths=["src/payment.py", "src/payment.py"],
            ),
            WorkerAssignment(
                worker_id="worker-1",
                worker_index=1,
                parallel_group="group-0",
                group_id="group-0",
                branch_name="feature/WI-001-worker-1",
                task_ids=["T1", "T1"],
                allowed_paths=["src/auth.py", "src/auth.py"],
                forbidden_paths=["src/payment.py", "src/payment.py"],
            ),
        ],
        overlap_result=OverlapResult(
            has_overlap=True,
            has_conflicts=False,
            overlapping_files=["src/auth.py", "src/auth.py"],
            conflicting_files={"src/auth.py": ["worker-1", "worker-1"]},
            conflicting_workers=[(1, 2), (1, 2)],
            total_shared_files=99,
            recommendation="clean",
        ),
        merge_simulation=MergeSimulation(
            success=True,
            conflicts=["src/auth.py", "src/auth.py"],
            predicted_conflicts=["src/auth.py", "src/auth.py"],
            merge_order=["feature/WI-001-worker-1", "feature/WI-001-worker-1"],
            notes="No conflicts predicted.",
        ),
    )
    path = work_item_root(tmp_path, "WI-001") / "parallel-coordination.yaml"
    YamlStore.save(path, artifact)

    loaded = load_parallel_coordination_artifact(tmp_path, "WI-001")

    assert loaded is not None
    assert loaded.group_task_ids == {"group-0": ["T1", "T1"]}
    assert loaded.worker_count == 2
    assert loaded.overlap_result.overlapping_files == ["src/auth.py"]
    assert loaded.overlap_result.conflicting_files == {"src/auth.py": ["worker-1"]}
    assert loaded.overlap_result.conflicting_workers == [(1, 2)]
    assert loaded.overlap_result.total_shared_files == 1
    assert loaded.merge_simulation.conflicts == ["src/auth.py"]
    assert loaded.merge_simulation.predicted_conflicts == ["src/auth.py"]
    assert loaded.merge_order == [
        "feature/WI-001-worker-1",
        "feature/WI-001-worker-1",
    ]
