"""Tests for local PR review pack generation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ai_sdlc.core.pr_review_pack import (
    ReviewPackBuildOptions,
    ReviewPackBuildStatus,
    build_review_pack,
)


def test_build_review_pack_writes_required_artifacts(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            head_ref="HEAD",
            review_id="review-001",
            loop_id="loop-001",
            current_model="gpt-5",
            work_item_refs=["specs/189/tasks.md"],
            test_results_refs=["pytest.log"],
            policy_refs=[".ai-sdlc/project/config/loop-policy.yaml"],
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert Path(result.review_pack_path).is_file()
    assert Path(result.diff_path).is_file()
    assert Path(result.changed_files_path).is_file()
    assert Path(result.redaction_report_path).is_file()
    assert Path(result.model_resolution_path).is_file()
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/app.py"]
    assert result.review_pack.reviewer_allowlist == ["src/app.py"]
    assert result.review_pack.model_selector == "current"
    assert result.review_pack.resolved_model == "gpt-5"
    assert result.review_pack.model_resolution_status == "resolved"
    assert result.review_pack.code_egress is False

    review_payload = json.loads(
        Path(result.review_pack_path).read_text(encoding="utf-8")
    )
    diff_text = Path(result.diff_path).read_text(encoding="utf-8")
    changed_files = Path(result.changed_files_path).read_text(encoding="utf-8")
    assert review_payload["base_commit"] == base_commit
    assert review_payload["head_commit"] == _git(tmp_path, "rev-parse", "HEAD")
    assert review_payload["work_item_refs"] == ["specs/189/tasks.md"]
    assert review_payload["test_results_refs"] == ["pytest.log"]
    assert review_payload["policy_refs"] == [
        ".ai-sdlc/project/config/loop-policy.yaml"
    ]
    assert review_payload["redaction_report_path"].endswith(
        ".ai-sdlc/reviews/pr/review-001/redaction-report.json"
    )
    assert "src/app.py" in changed_files
    assert "+print('review me')" in diff_text


def test_build_review_pack_stops_when_model_current_cannot_resolve(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-002",
            loop_id="loop-002",
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert "Unable to resolve model=current" in result.blocker
    assert result.review_pack_path == ""
    assert Path(result.changed_files_path).is_file()
    assert Path(result.redaction_report_path).is_file()
    assert Path(result.model_resolution_path).is_file()


def test_build_review_pack_stops_for_high_risk_secret_code_egress(
    tmp_path,
) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(
        tmp_path,
        "src/settings.py",
        'token = "abcdefghijklmnop"\n',
        "add settings",
    )

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-003",
            loop_id="loop-003",
            current_model="gpt-5",
            code_egress=True,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert "High-risk secrets" in result.blocker
    assert result.review_pack_path == ""
    assert result.diff_path == ""
    assert result.redacted_files_count == 1

    redaction_payload = json.loads(
        Path(result.redaction_report_path).read_text(encoding="utf-8")
    )
    assert redaction_payload["needs_user"] is True
    assert redaction_payload["redacted_files"] == ["src/settings.py"]


def test_build_review_pack_stops_when_diff_exceeds_limit(tmp_path) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('review me')\n", "add app")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-004",
            loop_id="loop-004",
            current_model="gpt-5",
            max_diff_bytes=1,
        )
    )

    assert result.status == ReviewPackBuildStatus.NEEDS_USER
    assert "above the configured" in result.blocker
    assert result.review_pack_path == ""
    assert result.diff_path == ""
    assert Path(result.redaction_report_path).is_file()


def test_build_review_pack_omits_redacted_files_from_reviewer_allowlist(
    tmp_path,
) -> None:
    base_commit = _init_repo_with_base_commit(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('safe')\n", "add app")
    _write_file(tmp_path, "src/settings.py", 'api_key = "abcdefghijklmnop"\n')
    _git(tmp_path, "add", "src/settings.py")
    _git(tmp_path, "commit", "-m", "add settings")

    result = build_review_pack(
        ReviewPackBuildOptions(
            root=tmp_path,
            base_ref=base_commit,
            review_id="review-005",
            loop_id="loop-005",
            current_model="gpt-5",
            code_egress=False,
        )
    )

    assert result.status == ReviewPackBuildStatus.READY
    assert result.review_pack is not None
    assert result.review_pack.changed_files == ["src/app.py", "src/settings.py"]
    assert result.review_pack.reviewer_allowlist == ["src/app.py"]
    assert result.redacted_files_count == 1
    assert "settings.py" not in Path(result.diff_path).read_text(encoding="utf-8")


def _init_repo_with_base_commit(path: Path) -> str:
    _git(path, "init")
    if _git(path, "symbolic-ref", "--short", "HEAD") != "main":
        _git(path, "checkout", "-b", "main")
    _git(path, "config", "user.email", "test@example.com")
    _git(path, "config", "user.name", "Test User")
    _commit_file(path, "README.md", "# Test\n", "initial")
    return _git(path, "rev-parse", "HEAD")


def _commit_file(path: Path, file_path: str, content: str, message: str) -> None:
    _write_file(path, file_path, content)
    _git(path, "add", file_path)
    _git(path, "commit", "-m", message)


def _write_file(path: Path, file_path: str, content: str) -> None:
    target = path / file_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


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
