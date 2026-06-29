"""Integration tests for the ai-sdlc pr-review CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


def test_pr_review_help_lists_p0_commands() -> None:
    result = runner.invoke(app, ["pr-review", "--help"])

    assert result.exit_code == 0
    assert "doctor" in result.output
    assert "start" in result.output
    assert "status" in result.output
    assert "fix" in result.output
    assert "rerun" in result.output
    assert "close" in result.output


def test_pr_review_start_dry_run_json_is_read_only(tmp_path: Path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    with patch("ai_sdlc.cli.pr_review_cmd.find_project_root", return_value=tmp_path):
        result = runner.invoke(
            app,
            [
                "pr-review",
                "start",
                "--base",
                base_commit,
                "--provider",
                "mock-reviewer",
                "--dry-run",
                "--review-id",
                "review-dry",
                "--json",
            ],
        )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "dry_run"
    assert payload["provider_id"] == "mock-reviewer"
    assert payload["resolved_model"] == "mock-reviewer"
    assert not (tmp_path / ".ai-sdlc" / "reviews").exists()


def test_pr_review_start_mock_and_status_json(tmp_path: Path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    with patch("ai_sdlc.cli.pr_review_cmd.find_project_root", return_value=tmp_path):
        start = runner.invoke(
            app,
            [
                "pr-review",
                "start",
                "--base",
                base_commit,
                "--provider",
                "mock-reviewer",
                "--review-id",
                "review-cli",
                "--json",
            ],
        )
        status = runner.invoke(app, ["pr-review", "status", "--json"])

    assert start.exit_code == 0
    start_payload = json.loads(start.output)
    assert start_payload["status"] == "started"
    assert start_payload["verdict"] == "clean"
    assert Path(start_payload["review_pack_path"]).is_file()
    assert Path(start_payload["findings_path"]).is_file()

    assert status.exit_code == 0
    status_payload = json.loads(status.output)
    assert status_payload["status"] == "started"
    assert status_payload["review_id"] == "review-cli"
    assert status_payload["verdict"] == "clean"


def test_pr_review_fix_and_close_require_no_blockers_json(tmp_path: Path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    with patch("ai_sdlc.cli.pr_review_cmd.find_project_root", return_value=tmp_path):
        start = runner.invoke(
            app,
            [
                "pr-review",
                "start",
                "--base",
                base_commit,
                "--provider",
                "mock-reviewer",
                "--mock-fixture",
                "changes_required",
                "--review-id",
                "review-fix-cli",
                "--json",
            ],
        )
        fix = runner.invoke(app, ["pr-review", "fix", "--json"])
        close = runner.invoke(
            app,
            ["pr-review", "close", "--require-no-blockers", "--json"],
        )

    assert start.exit_code == 10
    fix_payload = json.loads(fix.output)
    assert fix.exit_code == 0
    assert fix_payload["status"] == "ready"
    assert Path(fix_payload["fix_plan_path"]).is_file()
    assert Path(fix_payload["resolution_path"]).is_file()

    close_payload = json.loads(close.output)
    assert close.exit_code == 0
    assert close_payload["status"] == "closed"
    assert close_payload["verdict"] == "risk_accepted"
    assert Path(close_payload["final_report_path"]).is_file()


def test_pr_review_rerun_json_regenerates_current_review(tmp_path: Path) -> None:
    base_commit = _init_repo(tmp_path)
    _commit_file(tmp_path, "src/app.py", "print('hello')\n", "add app")

    with patch("ai_sdlc.cli.pr_review_cmd.find_project_root", return_value=tmp_path):
        start = runner.invoke(
            app,
            [
                "pr-review",
                "start",
                "--base",
                base_commit,
                "--provider",
                "mock-reviewer",
                "--review-id",
                "review-rerun-cli",
                "--json",
            ],
        )
        start_payload = json.loads(start.output)
        old_head = json.loads(
            Path(start_payload["review_pack_path"]).read_text(encoding="utf-8")
        )["head_commit"]
        _commit_file(tmp_path, "src/app.py", "print('updated')\n", "update app")
        rerun = runner.invoke(app, ["pr-review", "rerun", "--json"])

    assert rerun.exit_code == 0
    rerun_payload = json.loads(rerun.output)
    new_head = json.loads(
        Path(rerun_payload["review_pack_path"]).read_text(encoding="utf-8")
    )["head_commit"]
    assert rerun_payload["status"] == "started"
    assert new_head != old_head


def test_python_module_help_fallback_lists_pr_review() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_sdlc", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert result.returncode == 0
    assert "pr-review" in result.stdout


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
