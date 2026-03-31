"""Integration tests: ai-sdlc workitem truth-check."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _run(root: Path, *args: str) -> str:
    return subprocess.run(
        list(args),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _init_repo(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@example.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    ai = root / ".ai-sdlc" / "project" / "config"
    ai.mkdir(parents=True, exist_ok=True)
    (ai / "project-state.yaml").write_text(
        "status: initialized\nproject_name: demo\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )
    (root / "README.md").write_text("# Demo\n", encoding="utf-8")


def _write_formal_docs(wi_dir: Path, *, include_exec_log: bool = False) -> None:
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "spec.md").write_text("# spec\n", encoding="utf-8")
    (wi_dir / "plan.md").write_text("# plan\n", encoding="utf-8")
    (wi_dir / "tasks.md").write_text("# tasks\n", encoding="utf-8")
    if include_exec_log:
        (wi_dir / "task-execution-log.md").write_text("# log\n", encoding="utf-8")


def _commit_all(root: Path, message: str) -> str:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)
    return _run(root, "git", "rev-parse", "--short", "HEAD")


def _seed_unrelated_mainline_work_item(root: Path) -> None:
    wi_dir = root / "specs" / "008-unrelated-mainline"
    _write_formal_docs(wi_dir, include_exec_log=True)
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "unrelated.py").write_text("VALUE = 8\n", encoding="utf-8")
    _commit_all(root, "seed unrelated mainline work item")


class TestCliWorkitemTruthCheck:
    def test_truth_check_uses_requested_revision_instead_of_current_checkout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _seed_unrelated_mainline_work_item(root)

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(root / "specs" / "006-provenance-trace-phase-1")
        rev = _commit_all(root, "formalize 006")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                rev,
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["classification"] == "formal_freeze_only"
        assert payload["formal_docs"] == {
            "spec": True,
            "plan": True,
            "tasks": True,
            "execution_log": False,
        }
        assert payload["execution_started"] is False
        assert payload["head_matches_revision"] is False
        assert payload["contained_in_main"] is False
        assert payload["code_paths"] == []
        assert payload["test_paths"] == []

    def test_truth_check_reports_branch_only_implemented_for_unmerged_revision(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(
            root / "specs" / "006-provenance-trace-phase-1",
            include_exec_log=True,
        )
        (root / "src").mkdir(exist_ok=True)
        (root / "tests").mkdir(exist_ok=True)
        (root / "src" / "provenance.py").write_text("VALUE = 6\n", encoding="utf-8")
        (root / "tests" / "test_provenance.py").write_text(
            "def test_value():\n    assert 6 == 6\n",
            encoding="utf-8",
        )
        _commit_all(root, "implement 006 branch-only")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                "codex/006-provenance-trace-phase-1",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["classification"] == "branch_only_implemented"
        assert payload["execution_started"] is True
        assert payload["contained_in_main"] is False
        assert "src/provenance.py" in payload["code_paths"]
        assert "tests/test_provenance.py" in payload["test_paths"]
        assert payload["formal_docs"]["execution_log"] is True

    def test_truth_check_reports_mainline_merged_when_revision_is_on_main(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        _init_repo(root)
        _commit_all(root, "init")

        subprocess.run(
            ["git", "checkout", "-b", "codex/006-provenance-trace-phase-1"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        _write_formal_docs(
            root / "specs" / "006-provenance-trace-phase-1",
            include_exec_log=True,
        )
        (root / "src").mkdir(exist_ok=True)
        (root / "src" / "provenance.py").write_text("VALUE = 6\n", encoding="utf-8")
        _commit_all(root, "implement 006")

        subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)
        subprocess.run(
            ["git", "merge", "--no-ff", "codex/006-provenance-trace-phase-1", "-m", "merge 006"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "truth-check",
                "--wi",
                "specs/006-provenance-trace-phase-1",
                "--rev",
                "HEAD",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["classification"] == "mainline_merged"
        assert payload["execution_started"] is True
        assert payload["contained_in_main"] is True
        assert payload["head_matches_revision"] is True
