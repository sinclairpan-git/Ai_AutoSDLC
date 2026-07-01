"""Tests for read-only Loop Engine status summaries."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ai_sdlc.core.design_contract_loop import (
    DesignContractCheckOptions,
    DesignContractCloseOptions,
    check_design_contract_loop,
    close_design_contract_loop,
)
from ai_sdlc.core.design_contract_models import CURRENT_DESIGN_CONTRACT_PATH
from ai_sdlc.core.frontend_evidence_models import (
    CURRENT_FRONTEND_EVIDENCE_PATH,
    FrontendEvidenceClose,
    FrontendEvidenceCurrentPointer,
    FrontendEvidenceReport,
)
from ai_sdlc.core.implementation_loop import (
    CURRENT_IMPLEMENTATION_PATH,
    ImplementationCloseOptions,
    ImplementationRecordOptions,
    ImplementationStartOptions,
    close_implementation_loop,
    record_implementation_progress,
    start_implementation_loop,
)
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopRound, LoopRun, LoopStatus, LoopType
from ai_sdlc.core.loop_status import (
    CURRENT_REVIEW_PATH,
    LoopStatusCommandStatus,
    get_loop_status,
    list_loops,
)
from ai_sdlc.core.pr_review_models import (
    ModelResolutionSource,
    ModelResolutionStatus,
    ProviderMode,
    ReviewRun,
    ReviewVerdict,
)
from ai_sdlc.core.requirement_loop import (
    CURRENT_REQUIREMENT_PATH,
    RequirementFreezeOptions,
    RequirementStartOptions,
    freeze_requirement_loop,
    start_requirement_loop,
)


def test_get_loop_status_reads_current_local_pr_review_summary(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Current loop found."
    assert result.current_loop is not None
    assert result.current_loop.loop_id == "loop-review-001"
    assert result.current_loop.loop_type == "local-pr-review"
    assert result.current_loop.status == "needs_fix"
    assert result.current_loop.next_action == "Run ai-sdlc pr-review fix."
    assert result.next_action == "Run ai-sdlc pr-review fix."
    assert result.next_guidance.command == "ai-sdlc pr-review fix"
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is True
    assert result.next_guidance.writes_code is False
    assert result.current_loop.next_guidance.command == "ai-sdlc pr-review fix"
    assert result.current_loop.next_guidance.safety == "writes_review_artifacts"
    assert result.current_loop.local_pr_review is not None
    local = result.current_loop.local_pr_review
    assert local.review_id == "review-001"
    assert local.verdict == "changes_required"
    assert local.unresolved_blockers == 1
    assert local.provider_id == "mock-reviewer"
    assert local.resolved_model == "mock-reviewer"
    artifact_paths = {artifact.path for artifact in result.current_loop.artifacts}
    assert ".ai-sdlc/reviews/pr/current-review.json" in artifact_paths
    assert ".ai-sdlc/reviews/pr/review-001/review-run.json" in artifact_paths


def test_get_loop_status_guides_post_fix_review_to_rerun(tmp_path: Path) -> None:
    review_run_path = _write_review_run(
        tmp_path,
        next_action=(
            "Fix BLOCKER/REQUIRED findings, update resolution.yaml, then run "
            "ai-sdlc pr-review rerun."
        ),
    )
    _write_current_pointer(tmp_path, review_run_path)

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop is not None
    assert result.current_loop.status == "needs_fix"
    assert result.next_guidance.command == "ai-sdlc pr-review rerun"
    assert result.next_guidance.requires_model is True
    assert result.next_guidance.writes_artifacts is True
    assert result.next_guidance.writes_code is False
    assert result.next_guidance.safety == "may_call_local_review_agent"
    assert ".ai-sdlc/reviews/pr/review-001/resolution.yaml" in (
        result.next_guidance.evidence
    )
    assert result.current_loop.next_guidance.command == "ai-sdlc pr-review rerun"


def test_get_loop_status_reports_no_current_loop(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.NO_CURRENT
    assert result.current_loop is None
    assert result.next_action == "Run ai-sdlc pr-review start --base <branch>."
    assert result.next_guidance.command == "ai-sdlc pr-review doctor --base <branch>"
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is False
    assert "ai-sdlc pr-review start --base <branch>" in result.next_guidance.alternatives


def test_get_loop_status_blocks_uninitialized_project(tmp_path: Path) -> None:
    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert ".ai-sdlc is missing" in result.blocker
    assert result.next_action == "Run ai-sdlc init ."
    assert result.next_guidance.command == "ai-sdlc init ."
    assert result.next_guidance.writes_artifacts is True


def test_get_loop_status_guides_passed_review_to_close(tmp_path: Path) -> None:
    review_run_path = _write_review_run(
        tmp_path,
        status=LoopStatus.PASSED,
        verdict=ReviewVerdict.CLEAN,
        unresolved_blockers=0,
        next_action="Run ai-sdlc pr-review close.",
    )
    _write_current_pointer(tmp_path, review_run_path)

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.next_guidance.command == "ai-sdlc pr-review close"
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is True
    assert result.next_guidance.writes_code is False
    assert result.next_guidance.safety == "writes_review_artifacts"


def test_get_loop_status_blocks_malformed_pointer_without_traceback(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert "pointer is malformed" in result.blocker
    assert result.next_action == "Rerun ai-sdlc pr-review start."
    assert result.next_guidance.safety == "blocked"
    assert result.next_guidance.requires_model is True


def test_get_loop_status_blocks_absolute_pointer_path(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    LoopArtifactStore(tmp_path).write_json_artifact(
        pointer_path,
        {
            "review_id": "review-001",
            "loop_id": "loop-review-001",
            "review_run_path": str(tmp_path.parent / "outside-review-run.json"),
        },
    )

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert "project-relative" in result.blocker


def test_get_loop_status_blocks_missing_review_run(tmp_path: Path) -> None:
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True)
    pointer_path.write_text(
        json.dumps(
            {
                "review_id": "review-missing",
                "loop_id": "loop-missing",
                "review_run_path": ".ai-sdlc/reviews/pr/review-missing/review-run.json",
            }
        ),
        encoding="utf-8",
    )

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert "missing review-run.json" in result.blocker


def test_get_loop_status_does_not_write_artifacts(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)
    before = _snapshot_files(tmp_path / ".ai-sdlc")

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert _snapshot_files(tmp_path / ".ai-sdlc") == before


def test_list_loops_reads_sorted_local_pr_review_runs_and_marks_current(
    tmp_path: Path,
) -> None:
    older_path = _write_review_run(
        tmp_path,
        review_id="review-001",
        loop_id="loop-review-001",
        updated_at="2026-06-29T01:00:00Z",
    )
    _write_review_run(
        tmp_path,
        review_id="review-002",
        loop_id="loop-review-002",
        updated_at="2026-06-30T01:00:00Z",
    )
    _write_current_pointer(tmp_path, older_path)

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Local PR review loops found."
    assert result.malformed_count == 0
    assert result.current_loop_id == "loop-review-001"
    assert result.current_review_id == "review-001"
    assert result.next_guidance.command == "ai-sdlc loop status"
    assert [loop.loop_id for loop in result.items] == [
        "loop-review-002",
        "loop-review-001",
    ]
    assert [loop.next_guidance.command for loop in result.items] == [
        "ai-sdlc loop list --json",
        "ai-sdlc pr-review fix",
    ]
    assert result.items[0].next_guidance.writes_artifacts is False
    assert "non-current review run" in result.items[0].next_guidance.reason
    assert result.items[0].is_current is False
    assert result.items[1].is_current is True
    current_artifacts = {artifact.kind for artifact in result.items[1].artifacts}
    non_current_artifacts = {artifact.kind for artifact in result.items[0].artifacts}
    assert "current-review-pointer" in current_artifacts
    assert "current-review-pointer" not in non_current_artifacts


def test_list_loops_guides_no_current_pointer_with_history_to_doctor(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop_id == ""
    assert result.blocker == ""
    assert result.next_action == "Run ai-sdlc pr-review start --base <branch>."
    assert result.next_guidance.command == "ai-sdlc pr-review doctor --base <branch>"
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is False
    assert "ai-sdlc pr-review start --base <branch>" in (
        result.next_guidance.alternatives
    )
    assert [loop.next_guidance.command for loop in result.items] == [
        "ai-sdlc loop list --json"
    ]


def test_list_loops_orders_by_review_run_artifact_mtime(
    tmp_path: Path,
) -> None:
    older_path = _write_review_run(
        tmp_path,
        review_id="review-001",
        loop_id="loop-review-001",
        updated_at="2026-06-29T01:00:00Z",
    )
    newer_path = _write_review_run(
        tmp_path,
        review_id="review-002",
        loop_id="loop-review-002",
        updated_at="2026-06-30T01:00:00Z",
    )
    os.utime(newer_path, (100.0, 100.0))
    os.utime(older_path, (200.0, 200.0))

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert [loop.loop_id for loop in result.items] == [
        "loop-review-001",
        "loop-review-002",
    ]


def test_list_loops_skips_malformed_review_run_and_reports_error(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    bad_dir = LoopArtifactStore(tmp_path).review_run_dir("review-bad")
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "review-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert [loop.loop_id for loop in result.items] == ["loop-review-001"]
    assert result.malformed_count == 1
    assert len(result.artifact_errors) == 1
    assert result.artifact_errors[0].kind == "review-run"
    assert result.artifact_errors[0].path == (
        ".ai-sdlc/reviews/pr/review-bad/review-run.json"
    )


def test_list_loops_reports_malformed_current_pointer(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert len(result.artifact_errors) == 1
    assert result.artifact_errors[0].kind == "current-review-pointer"
    assert result.artifact_errors[0].path == ".ai-sdlc/reviews/pr/current-review.json"
    assert result.blocker == (
        "Current review pointer is malformed or references missing artifacts."
    )
    assert result.next_action == (
        "Inspect or remove malformed current-review.json artifacts."
    )
    assert result.next_guidance.safety == "blocked"
    assert result.next_guidance.command == "ai-sdlc pr-review start --base <branch>"
    assert ".ai-sdlc/reviews/pr/current-review.json" in result.next_guidance.evidence


def test_list_loops_reports_missing_current_pointer_target(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    missing_path = (
        tmp_path / ".ai-sdlc" / "reviews" / "pr" / "missing" / "review-run.json"
    )
    _write_current_pointer(tmp_path, missing_path)

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert len(result.artifact_errors) == 1
    assert result.artifact_errors[0].kind == "current-review-target"
    assert result.artifact_errors[0].path == (
        ".ai-sdlc/reviews/pr/missing/review-run.json"
    )
    assert result.next_guidance.safety == "blocked"
    assert ".ai-sdlc/reviews/pr/missing/review-run.json" in (
        result.next_guidance.evidence
    )


def test_list_loops_reports_malformed_current_review_run_as_blocked_guidance(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    bad_dir = LoopArtifactStore(tmp_path).review_run_dir("review-bad-current")
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "review-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")
    _write_current_pointer(tmp_path, bad_path)

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert [loop.loop_id for loop in result.items] == ["loop-review-001"]
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "review-run"
    assert result.artifact_errors[0].path == (
        ".ai-sdlc/reviews/pr/review-bad-current/review-run.json"
    )
    assert result.next_guidance.safety == "blocked"
    assert ".ai-sdlc/reviews/pr/review-bad-current/review-run.json" in (
        result.next_guidance.evidence
    )


def test_list_loops_reports_parent_segment_current_pointer(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    LoopArtifactStore(tmp_path).write_json_artifact(
        pointer_path,
        {
            "review_id": "review-001",
            "loop_id": "loop-review-001",
            "review_run_path": "../outside/review-run.json",
        },
    )

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-review-pointer"
    assert "parent directory" in result.artifact_errors[0].error
    assert result.next_guidance.safety == "blocked"


def test_list_loops_blocks_malformed_current_pointer_without_history(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-review-pointer"
    assert "current-review.json" in result.artifact_errors[0].path


def test_list_loops_blocks_missing_current_pointer_target_without_history(
    tmp_path: Path,
) -> None:
    missing_path = (
        tmp_path / ".ai-sdlc" / "reviews" / "pr" / "missing" / "review-run.json"
    )
    _write_current_pointer(tmp_path, missing_path)

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-review-target"
    assert "missing/review-run.json" in result.artifact_errors[0].path


def test_list_loops_reports_no_local_pr_review_runs(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.NO_CURRENT
    assert result.items == []
    assert result.next_action == "Run ai-sdlc pr-review start --base <branch>."
    assert result.next_guidance.command == "ai-sdlc pr-review doctor --base <branch>"


def test_list_loops_does_not_write_artifacts(tmp_path: Path) -> None:
    _write_review_run(tmp_path)
    before = _snapshot_files(tmp_path / ".ai-sdlc")

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert _snapshot_files(tmp_path / ".ai-sdlc") == before


def test_get_loop_status_reads_current_requirement_loop(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-status",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )

    result = get_loop_status(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Current requirement loop found."
    assert result.current_loop is not None
    assert result.current_loop.loop_type == "requirement"
    assert result.current_loop.status == "needs_review"
    assert result.next_guidance.command == "ai-sdlc loop requirement freeze --yes"
    assert result.next_guidance.requires_model is False
    assert result.current_loop.requirement is not None
    assert result.current_loop.requirement.summary == (
        "运营用户需要订单审批流，范围只覆盖后台人工审批。"
    )
    assert result.current_loop.requirement.acceptance_count == 1
    assert result.current_loop.requirement.frozen is False


def test_get_loop_status_reports_no_current_requirement_loop(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = get_loop_status(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.NO_CURRENT
    assert result.result == "No current requirement loop."
    assert result.next_guidance.command == 'ai-sdlc loop requirement start --idea "<需求描述>"'


def test_get_loop_status_blocks_malformed_requirement_pointer_with_requirement_guidance(
    tmp_path: Path,
) -> None:
    pointer_path = tmp_path / CURRENT_REQUIREMENT_PATH
    pointer_path.parent.mkdir(parents=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    result = get_loop_status(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert result.next_action == "Rerun ai-sdlc loop requirement start."
    assert result.next_guidance.command == 'ai-sdlc loop requirement start --idea "<需求描述>"'
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is True
    assert result.next_guidance.writes_code is False
    assert ".ai-sdlc/loops/requirement/current-requirement.json" in (
        result.next_guidance.evidence
    )


def test_get_loop_status_needs_user_guidance_updates_existing_requirement(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-needs-user-status",
            idea="做一个报表",
        )
    )

    result = get_loop_status(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop is not None
    assert result.current_loop.status == "needs_user"
    assert result.next_guidance.command == (
        'ai-sdlc loop requirement start --loop-id req-needs-user-status --acceptance "<验收标准>"'
    )
    assert result.next_guidance.requires_model is False


def test_list_loops_reads_requirement_runs_and_marks_current(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-old",
            idea="客服用户需要 SLA 提醒，范围只覆盖站内提醒。",
            acceptance=("SLA 超时前可以提醒",),
        )
    )
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-current",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )

    result = list_loops(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Requirement loops found."
    assert result.current_loop_id == "req-current"
    assert [item.loop_id for item in result.items] == ["req-current", "req-old"]
    assert result.items[0].is_current is True
    assert result.items[0].next_guidance.command == "ai-sdlc loop requirement freeze --yes"
    assert result.items[1].is_current is False
    assert result.items[1].next_guidance.command == (
        "ai-sdlc loop list --type requirement --json"
    )


def test_list_loops_orders_requirement_runs_by_updated_at_before_mtime(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-older",
            idea="Ops users need invoice review.",
            acceptance=("Invoices can be approved.",),
        )
    )
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-newer",
            idea="Ops users need refund review.",
            acceptance=("Refunds can be approved.",),
        )
    )
    older_path = (
        tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-older" / "loop-run.json"
    )
    newer_path = (
        tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-newer" / "loop-run.json"
    )
    older_doc = json.loads(older_path.read_text(encoding="utf-8"))
    older_doc["updated_at"] = "2026-06-29T01:00:00Z"
    older_path.write_text(
        json.dumps(older_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    newer_doc = json.loads(newer_path.read_text(encoding="utf-8"))
    newer_doc["updated_at"] = "2026-06-30T01:00:00Z"
    newer_path.write_text(
        json.dumps(newer_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.utime(newer_path, (100.0, 100.0))
    os.utime(older_path, (200.0, 200.0))

    result = list_loops(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["req-newer", "req-older"]


def test_list_loops_reports_malformed_requirement_without_hiding_valid_runs(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-valid",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )
    bad_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-bad"
    bad_dir.mkdir(parents=True)
    (bad_dir / "loop-run.json").write_text("{not-json", encoding="utf-8")

    result = list_loops(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["req-valid"]
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "requirement-loop-run"


def test_list_loops_reports_malformed_current_requirement_run_as_blocked_guidance(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-valid",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )
    bad_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-bad-current"
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "loop-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")
    LoopArtifactStore(tmp_path).write_json_artifact(
        tmp_path / CURRENT_REQUIREMENT_PATH,
        {
            "schema_version": "1",
            "artifact_kind": "current-requirement-pointer",
            "loop_id": "req-bad-current",
            "loop_run_path": bad_path.relative_to(tmp_path).as_posix(),
        },
    )

    result = list_loops(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["req-valid"]
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-requirement-target"
    assert result.blocker == (
        "Current requirement pointer is malformed or references missing artifacts."
    )
    assert result.next_guidance.safety == "blocked"
    assert ".ai-sdlc/loops/requirement/req-bad-current/loop-run.json" in (
        result.next_guidance.evidence
    )


def test_requirement_status_after_freeze_points_to_design_contract(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-frozen-status",
            idea="财务用户需要付款审批，范围只覆盖国内付款。",
            acceptance=("审批通过后才能付款",),
        )
    )
    freeze_requirement_loop(RequirementFreezeOptions(root=tmp_path, yes=True))

    result = get_loop_status(tmp_path, loop_type="requirement")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop is not None
    assert result.current_loop.status == "closed"
    assert result.current_loop.requirement is not None
    assert result.current_loop.requirement.frozen is True
    assert result.next_guidance.safety == "no_action"
    assert result.next_guidance.alternatives == [
        "Start design-contract loop from requirement req-frozen-status."
    ]


def test_get_loop_status_reads_current_design_contract_loop(tmp_path: Path) -> None:
    _write_design_contract_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-design-contract",
            loop_id="dc-status",
        )
    )

    result = get_loop_status(tmp_path, loop_type="design-contract")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Current design-contract loop found."
    assert result.current_loop is not None
    assert result.current_loop.loop_type == "design-contract"
    assert result.current_loop.status == "passed"
    assert result.next_guidance.command == "ai-sdlc loop design-contract close --yes"
    assert result.next_guidance.requires_model is False
    assert result.current_loop.design_contract is not None
    assert result.current_loop.design_contract.work_item_id == "demo-design-contract"
    assert result.current_loop.design_contract.coverage_count == 2


def test_get_loop_status_reports_no_current_design_contract_loop(
    tmp_path: Path,
) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = get_loop_status(tmp_path, loop_type="design-contract")

    assert result.status == LoopStatusCommandStatus.NO_CURRENT
    assert result.result == "No current design-contract loop."
    assert result.next_guidance.command == (
        "ai-sdlc loop design-contract check --wi specs/<work-item>"
    )
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is True


def test_list_loops_reads_design_contract_runs_and_marks_current(
    tmp_path: Path,
) -> None:
    _write_design_contract_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-design-contract",
            loop_id="dc-old",
        )
    )
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-design-contract",
            loop_id="dc-current",
        )
    )

    result = list_loops(tmp_path, loop_type="design-contract")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Design-contract loops found."
    assert result.current_loop_id == "dc-current"
    assert [item.loop_id for item in result.items] == ["dc-current", "dc-old"]
    assert result.items[0].is_current is True
    assert result.items[0].design_contract is not None
    assert result.items[0].next_guidance.command == (
        "ai-sdlc loop design-contract close --yes"
    )
    assert result.items[1].is_current is False
    assert result.items[1].next_guidance.command == (
        "ai-sdlc loop list --type design-contract --json"
    )


def test_design_contract_status_after_close_points_to_implementation(
    tmp_path: Path,
) -> None:
    _write_design_contract_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-design-contract",
            loop_id="dc-closed",
        )
    )
    close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-closed", yes=True)
    )

    result = get_loop_status(tmp_path, loop_type="design-contract")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop is not None
    assert result.current_loop.status == "closed"
    assert result.current_loop.design_contract is not None
    assert result.current_loop.design_contract.closed is True
    assert result.next_guidance.safety == "no_action"
    assert result.next_guidance.alternatives == [
        "Start implementation loop for demo-design-contract."
    ]


def test_list_loops_reports_malformed_current_design_contract_run(
    tmp_path: Path,
) -> None:
    _write_design_contract_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-design-contract",
            loop_id="dc-valid",
        )
    )
    bad_dir = tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-bad"
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "loop-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")
    LoopArtifactStore(tmp_path).write_json_artifact(
        tmp_path / CURRENT_DESIGN_CONTRACT_PATH,
        {
            "schema_version": "1",
            "artifact_kind": "current-design-contract-pointer",
            "loop_id": "dc-bad",
            "loop_run_path": bad_path.relative_to(tmp_path).as_posix(),
        },
    )

    result = list_loops(tmp_path, loop_type="design-contract")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["dc-valid"]
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-design-contract-target"
    assert result.blocker == (
        "Current design-contract pointer is malformed or references missing artifacts."
    )
    assert result.next_guidance.safety == "blocked"


def test_list_loops_reports_invalid_current_design_contract_target(
    tmp_path: Path,
) -> None:
    _write_design_contract_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-design-contract",
            loop_id="dc-valid",
        )
    )
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-wrong-target",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )
    wrong_target = (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / "req-wrong-target"
        / "loop-run.json"
    )
    LoopArtifactStore(tmp_path).write_json_artifact(
        tmp_path / CURRENT_DESIGN_CONTRACT_PATH,
        {
            "schema_version": "1",
            "artifact_kind": "current-design-contract-pointer",
            "loop_id": "req-wrong-target",
            "loop_run_path": wrong_target.relative_to(tmp_path).as_posix(),
        },
    )

    result = list_loops(tmp_path, loop_type="design-contract")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["dc-valid"]
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-design-contract-target"
    assert "not a design-contract loop-run.json" in result.artifact_errors[0].error
    assert result.blocker == (
        "Current design-contract pointer is malformed or references missing artifacts."
    )
    assert result.next_guidance.safety == "blocked"


def test_get_loop_status_reads_current_implementation_loop(tmp_path: Path) -> None:
    _start_implementation_status_loop(tmp_path, loop_id="impl-status")

    result = get_loop_status(tmp_path, loop_type="implementation")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Current implementation loop found."
    assert result.current_loop is not None
    assert result.current_loop.loop_type == "implementation"
    assert result.current_loop.status == "running"
    assert result.next_guidance.command.startswith(
        "ai-sdlc loop implementation record"
    )
    assert result.next_guidance.requires_model is False
    assert result.current_loop.implementation is not None
    assert result.current_loop.implementation.work_item_id == "demo-design-contract"
    assert result.current_loop.implementation.required_task_count == 1
    assert result.current_loop.implementation.done_count == 0


def test_list_loops_reads_implementation_runs_and_marks_current(
    tmp_path: Path,
) -> None:
    _start_implementation_status_loop(tmp_path, loop_id="impl-old")
    _start_implementation_status_loop(tmp_path, loop_id="impl-current")

    result = list_loops(tmp_path, loop_type="implementation")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Implementation loops found."
    assert result.current_loop_id == "impl-current"
    assert [item.loop_id for item in result.items] == ["impl-current", "impl-old"]
    assert result.items[0].is_current is True
    assert result.items[0].next_guidance.command.startswith(
        "ai-sdlc loop implementation record"
    )
    assert result.items[1].is_current is False
    assert result.items[1].next_guidance.command == (
        "ai-sdlc loop list --type implementation --json"
    )


def test_implementation_status_after_close_points_to_local_pr_review(
    tmp_path: Path,
) -> None:
    _start_implementation_status_loop(tmp_path, loop_id="impl-closed")
    record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-closed",
            task_id="T11",
            status="done",
            verification=("uv run pytest tests/unit/test_loop_status.py -q",),
        )
    )
    close_implementation_loop(
        ImplementationCloseOptions(root=tmp_path, loop_id="impl-closed", yes=True)
    )

    result = get_loop_status(tmp_path, loop_type="implementation")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop is not None
    assert result.current_loop.status == "closed"
    assert result.next_guidance.command == "ai-sdlc pr-review start"
    assert result.next_guidance.requires_model is True
    assert result.current_loop.implementation is not None
    assert result.current_loop.implementation.closed is True


def test_list_loops_reports_malformed_current_implementation_run(
    tmp_path: Path,
) -> None:
    _start_implementation_status_loop(tmp_path, loop_id="impl-valid")
    bad_dir = tmp_path / ".ai-sdlc" / "loops" / "implementation" / "impl-bad"
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "loop-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")
    LoopArtifactStore(tmp_path).write_json_artifact(
        tmp_path / CURRENT_IMPLEMENTATION_PATH,
        {
            "schema_version": "1",
            "artifact_kind": "current-implementation-pointer",
            "loop_id": "impl-bad",
            "loop_run_path": bad_path.relative_to(tmp_path).as_posix(),
        },
    )

    result = list_loops(tmp_path, loop_type="implementation")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["impl-valid"]
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-implementation-target"
    assert result.blocker == (
        "Current implementation pointer is malformed or references missing artifacts."
    )
    assert result.next_guidance.safety == "blocked"


def test_get_loop_status_reads_current_frontend_evidence_loop(tmp_path: Path) -> None:
    _write_frontend_evidence_status_loop(tmp_path, loop_id="fe-status")

    result = get_loop_status(tmp_path, loop_type="frontend-evidence")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Current frontend-evidence loop found."
    assert result.current_loop is not None
    assert result.current_loop.loop_type == "frontend-evidence"
    assert result.current_loop.status == "passed"
    assert result.next_guidance.command == "ai-sdlc loop frontend-evidence close --yes"
    assert result.next_guidance.requires_model is False
    assert result.current_loop.frontend_evidence is not None
    assert result.current_loop.frontend_evidence.work_item_id == "demo-frontend"
    assert result.current_loop.frontend_evidence.gate_run_id == "gate-run-status"
    assert result.current_loop.frontend_evidence.overall_gate_status == "passed"


def test_list_loops_reads_frontend_evidence_runs_and_marks_current(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_status_loop(tmp_path, loop_id="fe-old")
    _write_frontend_evidence_status_loop(tmp_path, loop_id="fe-current")

    result = list_loops(tmp_path, loop_type="frontend-evidence")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.result == "Frontend-evidence loops found."
    assert result.current_loop_id == "fe-current"
    assert [item.loop_id for item in result.items] == ["fe-current", "fe-old"]
    assert result.items[0].is_current is True
    assert result.items[0].next_guidance.command == (
        "ai-sdlc loop frontend-evidence close --yes"
    )
    assert result.items[1].is_current is False
    assert result.items[1].next_guidance.command == (
        "ai-sdlc loop list --type frontend-evidence --json"
    )


def test_frontend_evidence_status_after_close_points_to_local_pr_review(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_status_loop(
        tmp_path,
        loop_id="fe-closed",
        status=LoopStatus.CLOSED,
        closed=True,
    )

    result = get_loop_status(tmp_path, loop_type="frontend-evidence")

    assert result.status == LoopStatusCommandStatus.READY
    assert result.current_loop is not None
    assert result.current_loop.status == "closed"
    assert result.next_guidance.command == "ai-sdlc pr-review start"
    assert result.next_guidance.requires_model is True
    assert result.current_loop.frontend_evidence is not None
    assert result.current_loop.frontend_evidence.closed is True


def test_list_loops_reports_malformed_current_frontend_evidence_run(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_status_loop(tmp_path, loop_id="fe-valid")
    bad_dir = tmp_path / ".ai-sdlc" / "loops" / "frontend-evidence" / "fe-bad"
    bad_dir.mkdir(parents=True)
    bad_path = bad_dir / "loop-run.json"
    bad_path.write_text("{not-json", encoding="utf-8")
    LoopArtifactStore(tmp_path).write_json_artifact(
        tmp_path / CURRENT_FRONTEND_EVIDENCE_PATH,
        {
            "schema_version": "1",
            "artifact_kind": "current-frontend-evidence-pointer",
            "loop_id": "fe-bad",
            "loop_run_path": bad_path.relative_to(tmp_path).as_posix(),
        },
    )

    result = list_loops(tmp_path, loop_type="frontend-evidence")

    assert result.status == LoopStatusCommandStatus.READY
    assert [item.loop_id for item in result.items] == ["fe-valid"]
    assert result.current_loop_id == ""
    assert result.malformed_count == 1
    assert result.artifact_errors[0].kind == "current-frontend-evidence-target"
    assert result.blocker == (
        "Current frontend-evidence pointer is malformed or references missing artifacts."
    )
    assert result.next_guidance.safety == "blocked"


def _write_frontend_evidence_status_loop(
    root: Path,
    *,
    loop_id: str,
    status: LoopStatus = LoopStatus.PASSED,
    closed: bool = False,
) -> None:
    store = LoopArtifactStore(root)
    loop_dir = root / ".ai-sdlc" / "loops" / "frontend-evidence" / loop_id
    store.create_loop_run_dir(loop_id, loop_type=LoopType.FRONTEND_EVIDENCE.value)
    next_action = (
        "Run ai-sdlc pr-review start."
        if closed
        else "Run ai-sdlc loop frontend-evidence close --yes."
    )
    report = FrontendEvidenceReport(
        loop_id=loop_id,
        work_item_id="demo-frontend",
        work_item_path="specs/demo-frontend",
        status=status,
        gate_run_id="gate-run-status",
        source_artifact_path=".ai-sdlc/memory/frontend-browser-gate/latest.yaml",
        overall_gate_status="passed",
        execute_gate_state="ready",
        decision_reason="all_checks_passed",
        next_action=next_action,
    )
    loop_run = LoopRun(
        loop_id=loop_id,
        loop_type=LoopType.FRONTEND_EVIDENCE,
        status=status,
        work_item_id="demo-frontend",
        current_round=1,
        rounds=[
            LoopRound(
                round_number=1,
                command=["ai-sdlc", "loop", "frontend-evidence", "start"],
                status=status,
                result=status,
                next_action=next_action,
            )
        ],
        next_action=next_action,
    )
    store.write_json_artifact(loop_dir / "frontend-evidence-report.json", report)
    store.write_json_artifact(loop_dir / "loop-run.json", loop_run)
    if closed:
        store.write_json_artifact(
            loop_dir / "frontend-evidence-close.json",
            FrontendEvidenceClose(
                loop_id=loop_id,
                report_path=(
                    f".ai-sdlc/loops/frontend-evidence/{loop_id}/frontend-evidence-report.json"
                ),
            ),
        )
    store.write_json_artifact(
        root / CURRENT_FRONTEND_EVIDENCE_PATH,
        FrontendEvidenceCurrentPointer(
            loop_id=loop_id,
            loop_run_path=f".ai-sdlc/loops/frontend-evidence/{loop_id}/loop-run.json",
        ),
    )


def _start_implementation_status_loop(root: Path, *, loop_id: str) -> None:
    work_item = _write_design_contract_work_item(root)
    check = check_design_contract_loop(
        DesignContractCheckOptions(
            root=root,
            work_item="specs/demo-design-contract",
            loop_id=f"dc-{loop_id}",
        )
    )
    assert check.status == "ready"
    close = close_design_contract_loop(
        DesignContractCloseOptions(root=root, loop_id=f"dc-{loop_id}", yes=True)
    )
    assert close.status == "ready"
    result = start_implementation_loop(
        ImplementationStartOptions(
            root=root,
            work_item=work_item.as_posix(),
            design_contract_loop_id=f"dc-{loop_id}",
            loop_id=loop_id,
        )
    )
    assert result.status == "ready"


def _write_design_contract_work_item(root: Path) -> Path:
    work_item = root / "specs" / "demo-design-contract"
    work_item.mkdir(parents=True, exist_ok=True)
    work_item.joinpath("spec.md").write_text(
        "\n".join(
            [
                "# PRD：Demo Design Contract",
                "",
                "**状态**：已冻结",
                "",
                "## 需求",
                "",
                "- **FR-DEMO-001**：系统必须检查设计合同。",
                "",
                "## 成功标准",
                "",
                "- **SC-DEMO-001**：合同通过后可以进入实现。",
            ]
        ),
        encoding="utf-8",
    )
    work_item.joinpath("plan.md").write_text(
        "\n".join(
            [
                "# 实施计划",
                "## 技术背景",
                "Python runtime.",
                "## 阶段计划",
                "Phase 1.",
                "## 验证策略",
                "Run pytest.",
                "## 回退方式",
                "Revert the commit.",
            ]
        ),
        encoding="utf-8",
    )
    work_item.joinpath("tasks.md").write_text(
        "\n".join(
            [
                "# 任务分解",
                "### Task 1.1 Check contract",
                "- **任务编号**：T11",
                "- **优先级**：P0",
                "- **验收标准**：Cover FR-DEMO-001 and SC-DEMO-001.",
                "- **验证**：uv run pytest tests/unit/test_demo.py -q",
            ]
        ),
        encoding="utf-8",
    )
    _ensure_frozen_requirement_loop(root, loop_id="req-current")
    return work_item


def _ensure_frozen_requirement_loop(root: Path, *, loop_id: str) -> None:
    freeze_path = (
        root
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / loop_id
        / "requirement-freeze.json"
    )
    if freeze_path.is_file():
        return
    start_result = start_requirement_loop(
        RequirementStartOptions(
            root=root,
            loop_id=loop_id,
            idea="Demo users need a checked design contract.",
            acceptance=("The design contract can be checked before implementation.",),
        )
    )
    assert start_result.status == "ready"
    freeze_result = freeze_requirement_loop(
        RequirementFreezeOptions(root=root, loop_id=loop_id, yes=True)
    )
    assert freeze_result.frozen is True


def _write_review_run(
    root: Path,
    *,
    review_id: str = "review-001",
    loop_id: str = "loop-review-001",
    updated_at: str = "2026-06-30T00:00:00Z",
    status: LoopStatus = LoopStatus.NEEDS_FIX,
    verdict: ReviewVerdict | None = ReviewVerdict.CHANGES_REQUIRED,
    unresolved_blockers: int = 1,
    next_action: str = "Run ai-sdlc pr-review fix.",
    resolution_path: str = "",
) -> Path:
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir(review_id)
    review_pack_path = review_dir / "review-pack.json"
    findings_path = review_dir / "findings.json"
    review_pack_path.write_text("{}\n", encoding="utf-8")
    findings_path.write_text("{}\n", encoding="utf-8")
    if resolution_path:
        (root / resolution_path).write_text("{}\n", encoding="utf-8")
    review_run = ReviewRun(
        review_id=review_id,
        loop_id=loop_id,
        status=status,
        provider_id="mock-reviewer",
        provider_mode=ProviderMode.MOCK,
        model_selector="fixture",
        resolved_model="mock-reviewer",
        model_resolution_status=ModelResolutionStatus.RESOLVED,
        model_resolution_source=ModelResolutionSource.MOCK_FIXTURE,
        base_ref="main",
        head_ref="HEAD",
        base_commit="a" * 40,
        head_commit="b" * 40,
        review_pack_path=f".ai-sdlc/reviews/pr/{review_id}/review-pack.json",
        findings_path=f".ai-sdlc/reviews/pr/{review_id}/findings.json",
        resolution_path=resolution_path,
        verdict=verdict,
        unresolved_blockers=unresolved_blockers,
        next_action=next_action,
        updated_at=updated_at,
    )
    return store.write_json_artifact(review_dir / "review-run.json", review_run)


def _write_current_pointer(root: Path, review_run_path: Path) -> Path:
    pointer_path = root / CURRENT_REVIEW_PATH
    LoopArtifactStore(root).write_json_artifact(
        pointer_path,
        {
            "review_id": "review-001",
            "loop_id": "loop-review-001",
            "review_run_path": review_run_path.relative_to(root).as_posix(),
        },
    )
    return pointer_path


def _snapshot_files(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
