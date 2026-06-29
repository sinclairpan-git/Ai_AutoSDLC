"""Tests for local PR review service orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from ai_sdlc.core.pr_review_provider import MockReviewerFixture, ProviderRunStatus
from ai_sdlc.core.pr_review_service import (
    CURRENT_REVIEW_PATH,
    PRReviewCommandStatus,
    PRReviewStartOptions,
    close_pr_review,
    doctor_pr_review,
    fix_pr_review,
    rerun_pr_review,
    start_pr_review,
    status_pr_review,
)


def test_start_dry_run_does_not_create_review_artifacts(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            dry_run=True,
            review_id="review-dry",
        )
    )

    assert result.status == PRReviewCommandStatus.DRY_RUN
    assert result.dry_run is True
    assert result.provider_id == "mock-reviewer"
    assert result.resolved_model == "mock-reviewer"
    assert result.changed_files_count == 1
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_start_mock_reviewer_writes_pack_findings_run_and_pointer(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-001",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )

    assert result.status == PRReviewCommandStatus.STARTED
    assert result.provider_status == ProviderRunStatus.SUCCESS
    assert result.verdict == "clean"
    assert Path(result.review_pack_path).is_file()
    assert Path(result.findings_path).is_file()
    assert Path(result.review_run_path).is_file()
    assert (tmp_path / CURRENT_REVIEW_PATH).is_file()

    pointer = json.loads((tmp_path / CURRENT_REVIEW_PATH).read_text(encoding="utf-8"))
    assert pointer["review_id"] == "review-001"
    assert pointer["review_run_path"] == result.review_run_path


def test_status_recovers_current_review(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-status",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.STARTED
    assert result.review_id == "review-status"
    assert result.verdict == "changes_required"
    assert result.unresolved_required == 1
    assert "fix" in result.next_action


def test_start_local_agent_without_command_returns_needs_user(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    result = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="local-agent",
            current_model="gpt-5",
            review_id="review-local",
        )
    )

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "not configured" in result.blocker
    assert result.review_pack_path


def test_doctor_blocks_unknown_base_ref_without_writing_artifacts(tmp_path) -> None:
    _init_repo(tmp_path)

    result = doctor_pr_review(
        root=tmp_path,
        base_ref="missing-base",
        provider_id="mock-reviewer",
    )

    assert result.status == PRReviewCommandStatus.BLOCKED
    assert "missing-base" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_status_without_current_review_returns_next_action(tmp_path) -> None:
    (tmp_path / ".ai-sdlc").mkdir()

    result = status_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.NO_REVIEW
    assert "pr-review start" in result.next_action


def test_fix_generates_plan_and_resolution_without_advisory_auto_plan(
    tmp_path,
) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-fix",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    _append_advisory_finding(Path(start.findings_path))

    result = fix_pr_review(tmp_path, max_rounds=2)

    assert result.status == PRReviewCommandStatus.READY
    assert result.selected_findings_count == 1
    assert result.skipped_advisory_count == 1
    assert Path(result.fix_plan_path).is_file()
    assert Path(result.resolution_path).is_file()

    resolution = yaml.safe_load(Path(result.resolution_path).read_text(encoding="utf-8"))
    assert [item["finding_id"] for item in resolution["finding_resolutions"]] == [
        "MOCK-001"
    ]
    assert "ADV-001" not in Path(result.fix_plan_path).read_text(encoding="utf-8").split(
        "## Required Fixes", 1
    )[1].split("## Advisory", 1)[0]


def test_fix_stops_when_max_rounds_reached(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-max",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    assert fix_pr_review(tmp_path, max_rounds=1).status == PRReviewCommandStatus.READY

    result = fix_pr_review(tmp_path, max_rounds=1)

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "max rounds" in result.blocker


def test_close_blocks_required_findings_then_allows_risk_accepted(
    tmp_path,
) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-close",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )

    blocked = close_pr_review(tmp_path)
    accepted = close_pr_review(
        tmp_path,
        require_no_blockers=True,
        verification_evidence=["uv run pytest tests/unit/test_x.py -q"],
    )

    assert blocked.status == PRReviewCommandStatus.BLOCKED
    assert blocked.verdict == "blocked"
    assert "REQUIRED" in blocked.blocker
    assert accepted.status == PRReviewCommandStatus.CLOSED
    assert accepted.verdict == "risk_accepted"
    assert Path(accepted.final_report_path).is_file()
    assert "uv run pytest" in Path(accepted.final_report_path).read_text(
        encoding="utf-8"
    )


def test_close_fully_clean_after_resolution_marks_required_fixed(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-fixed",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    fix = fix_pr_review(tmp_path)
    resolution_path = Path(fix.resolution_path)
    resolution = yaml.safe_load(resolution_path.read_text(encoding="utf-8"))
    resolution["finding_resolutions"][0]["status"] = "fixed"
    resolution["finding_resolutions"][0]["evidence_refs"] = ["tests passed"]
    resolution_path.write_text(yaml.safe_dump(resolution), encoding="utf-8")

    result = close_pr_review(tmp_path)

    assert result.status == PRReviewCommandStatus.CLOSED
    assert result.verdict == "fully_clean"
    assert result.unresolved_required == 0


def test_rerun_regenerates_review_for_same_scope_changes(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start = start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-rerun",
            mock_fixture=MockReviewerFixture.CLEAN,
        )
    )
    old_head = json.loads(Path(start.review_pack_path).read_text(encoding="utf-8"))[
        "head_commit"
    ]
    _commit_file(tmp_path, "src/app.py", "print('updated')\n", "update app")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    new_head = json.loads(Path(result.review_pack_path).read_text(encoding="utf-8"))[
        "head_commit"
    ]
    assert result.status == PRReviewCommandStatus.STARTED
    assert new_head != old_head


def test_rerun_reports_scope_drift_for_unrelated_new_files(tmp_path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")
    start_pr_review(
        PRReviewStartOptions(
            root=tmp_path,
            base_ref=base_commit,
            provider_id="mock-reviewer",
            review_id="review-drift",
            mock_fixture=MockReviewerFixture.CHANGES_REQUIRED,
        )
    )
    _commit_file(tmp_path, "src/other.py", "print('other')\n", "add other")

    result = rerun_pr_review(tmp_path, mock_fixture=MockReviewerFixture.CLEAN)

    assert result.status == PRReviewCommandStatus.NEEDS_USER
    assert "Scope drift" in result.blocker
    assert "src/other.py" in result.blocker


def _append_advisory_finding(findings_path: Path) -> None:
    payload = json.loads(findings_path.read_text(encoding="utf-8"))
    payload["findings"].append(
        {
            "id": "ADV-001",
            "severity": "ADVISORY",
            "file": "src/docs.py",
            "claim": "Optional cleanup.",
            "evidence": "Fixture advisory.",
            "risk": "Low maintainability risk.",
            "suggested_fix": "Consider cleanup later.",
            "confidence": 0.5,
        }
    )
    findings_path.write_text(json.dumps(payload), encoding="utf-8")


def _init_repo(path: Path) -> str:
    (path / ".ai-sdlc").mkdir()
    _git(path, "init")
    if _git(path, "symbolic-ref", "--short", "HEAD") != "main":
        _git(path, "checkout", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")
    _commit_file(path, "README.md", "# Test\n", "initial")
    return _git(path, "rev-parse", "HEAD")


def _commit_file(path: Path, file_path: str, content: str, message: str) -> None:
    target = path / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(path, "add", file_path)
    _git(path, "commit", "-m", message)


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()
