"""Tests for read-only Loop Engine status summaries."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopStatus
from ai_sdlc.core.loop_status import (
    CURRENT_REVIEW_PATH,
    LoopStatusCommandStatus,
    get_loop_status,
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


def _write_review_run(root: Path) -> Path:
    store = LoopArtifactStore(root)
    review_dir = store.create_review_run_dir("review-001")
    review_pack_path = review_dir / "review-pack.json"
    findings_path = review_dir / "findings.json"
    review_pack_path.write_text("{}\n", encoding="utf-8")
    findings_path.write_text("{}\n", encoding="utf-8")
    review_run = ReviewRun(
        review_id="review-001",
        loop_id="loop-review-001",
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
        review_pack_path=".ai-sdlc/reviews/pr/review-001/review-pack.json",
        findings_path=".ai-sdlc/reviews/pr/review-001/findings.json",
        verdict=ReviewVerdict.CHANGES_REQUIRED,
        unresolved_blockers=1,
        next_action="Run ai-sdlc pr-review fix.",
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
