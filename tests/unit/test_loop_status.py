"""Tests for read-only Loop Engine status summaries."""

from __future__ import annotations

import json
import os
from pathlib import Path

from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopStatus
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


def test_get_loop_status_reports_no_current_loop(tmp_path: Path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.NO_CURRENT
    assert result.current_loop is None
    assert result.next_action == "Run ai-sdlc pr-review start --base <branch>."


def test_get_loop_status_blocks_uninitialized_project(tmp_path: Path) -> None:
    result = get_loop_status(tmp_path)

    assert result.status == LoopStatusCommandStatus.BLOCKED
    assert ".ai-sdlc is missing" in result.blocker
    assert result.next_action == "Run ai-sdlc init ."


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
    assert [loop.loop_id for loop in result.items] == [
        "loop-review-002",
        "loop-review-001",
    ]
    assert result.items[0].is_current is False
    assert result.items[1].is_current is True
    current_artifacts = {artifact.kind for artifact in result.items[1].artifacts}
    non_current_artifacts = {artifact.kind for artifact in result.items[0].artifacts}
    assert "current-review-pointer" in current_artifacts
    assert "current-review-pointer" not in non_current_artifacts


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


def test_list_loops_does_not_write_artifacts(tmp_path: Path) -> None:
    _write_review_run(tmp_path)
    before = _snapshot_files(tmp_path / ".ai-sdlc")

    result = list_loops(tmp_path)

    assert result.status == LoopStatusCommandStatus.READY
    assert _snapshot_files(tmp_path / ".ai-sdlc") == before


def _write_review_run(
    root: Path,
    *,
    review_id: str = "review-001",
    loop_id: str = "loop-review-001",
    updated_at: str = "2026-06-30T00:00:00Z",
) -> Path:
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir(review_id)
    review_pack_path = review_dir / "review-pack.json"
    findings_path = review_dir / "findings.json"
    review_pack_path.write_text("{}\n", encoding="utf-8")
    findings_path.write_text("{}\n", encoding="utf-8")
    review_run = ReviewRun(
        review_id=review_id,
        loop_id=loop_id,
        status=LoopStatus.NEEDS_FIX,
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
        verdict=ReviewVerdict.CHANGES_REQUIRED,
        unresolved_blockers=1,
        next_action="Run ai-sdlc pr-review fix.",
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
