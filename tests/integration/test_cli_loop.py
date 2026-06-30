"""Integration tests for the ai-sdlc loop CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.loop_artifacts import LoopArtifactStore
from ai_sdlc.core.loop_models import LoopStatus
from ai_sdlc.core.loop_status import CURRENT_REVIEW_PATH
from ai_sdlc.core.pr_review_models import (
    ModelResolutionSource,
    ModelResolutionStatus,
    ProviderMode,
    ReviewRun,
    ReviewVerdict,
)

runner = CliRunner()


def test_loop_help_lists_status_and_list() -> None:
    result = runner.invoke(app, ["loop", "--help"])

    assert result.exit_code == 0
    assert "status" in result.output
    assert "list" in result.output


def test_loop_status_json_reads_current_review(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["result"] == "Current loop found."
    assert payload["current_loop"]["loop_type"] == "local-pr-review"
    assert payload["current_loop"]["status"] == "needs_fix"
    assert payload["current_loop"]["is_current"] is True
    assert payload["current_loop"]["local_pr_review"]["review_id"] == "review-001"


def test_loop_status_human_includes_review_and_artifacts(tmp_path: Path) -> None:
    review_run_path = _write_review_run(tmp_path)
    _write_current_pointer(tmp_path, review_run_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status"])

    assert result.exit_code == 0
    assert "Result: ready" in result.output
    assert "Next: Run ai-sdlc pr-review fix." in result.output
    assert "Loop type: local-pr-review" in result.output
    assert "Review ID: review-001" in result.output
    assert "Loop next: Run ai-sdlc pr-review fix." in result.output
    assert "Unresolved: blockers=1, required=0, advisory=0" in result.output
    assert "Artifacts:" in result.output
    assert ".ai-sdlc/reviews/pr/review-001/review-run.json" in result.output


def test_loop_list_human_includes_each_loop_next_action(tmp_path: Path) -> None:
    _write_review_run(tmp_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list"])

    assert result.exit_code == 0
    assert "Loop 1" in result.output
    assert "Loop next: Run ai-sdlc pr-review fix." in result.output


def test_loop_status_human_skips_update_notice(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / ".ai-sdlc").mkdir()
    calls: list[bool] = []
    monkeypatch.setattr(
        "ai_sdlc.cli.main.maybe_render_update_notice",
        lambda: calls.append(True),
    )

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "status"])

    assert result.exit_code == 0
    assert calls == []


def test_loop_list_json_reads_runs_and_reports_malformed(
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
    bad_dir = LoopArtifactStore(tmp_path).review_run_dir("review-bad")
    bad_dir.mkdir(parents=True)
    (bad_dir / "review-run.json").write_text("{not-json", encoding="utf-8")

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == "loop-review-001"
    assert payload["current_review_id"] == "review-001"
    assert payload["malformed_count"] == 1
    assert [loop["loop_id"] for loop in payload["items"]] == [
        "loop-review-002",
        "loop-review-001",
    ]
    assert payload["items"][0]["is_current"] is False
    assert payload["items"][1]["is_current"] is True
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/review-bad/review-run.json"
    )


def test_loop_list_json_reports_malformed_current_pointer(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    pointer_path = tmp_path / CURRENT_REVIEW_PATH
    pointer_path.parent.mkdir(parents=True, exist_ok=True)
    pointer_path.write_text("{not-json", encoding="utf-8")

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == ""
    assert payload["malformed_count"] == 1
    assert payload["artifact_errors"][0]["kind"] == "current-review-pointer"
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/current-review.json"
    )


def test_loop_list_json_reports_missing_current_pointer_target(
    tmp_path: Path,
) -> None:
    _write_review_run(tmp_path)
    missing_path = (
        tmp_path / ".ai-sdlc" / "reviews" / "pr" / "missing" / "review-run.json"
    )
    _write_current_pointer(tmp_path, missing_path)

    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["loop", "list", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ready"
    assert payload["current_loop_id"] == ""
    assert payload["malformed_count"] == 1
    assert payload["artifact_errors"][0]["kind"] == "current-review-target"
    assert payload["artifact_errors"][0]["path"] == (
        ".ai-sdlc/reviews/pr/missing/review-run.json"
    )


def test_loop_status_json_reports_missing_project() -> None:
    with patch("ai_sdlc.cli.loop_cmd.find_project_root", return_value=None):
        result = runner.invoke(app, ["loop", "status", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["status"] == "blocked"
    assert ".ai-sdlc is missing" in payload["blocker"]
    assert "ai-sdlc init" in payload["next_action"]


def test_python_module_help_fallback_lists_loop() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0
    assert "loop" in result.stdout


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
