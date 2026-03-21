"""Unit tests for Branch Manager."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.branch.branch_manager import BranchError, BranchManager
from ai_sdlc.branch.git_client import GitClient


class TestBranchManager:
    def test_create_docs_branch(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        name = bm.create_docs_branch("WI-2026-001")
        assert name == "design/WI-2026-001-docs"
        assert gc.current_branch() == "design/WI-2026-001-docs"

    def test_create_dev_branch(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        name = bm.create_dev_branch("WI-2026-001")
        assert name == "feature/WI-2026-001-dev"
        assert gc.current_branch() == "feature/WI-2026-001-dev"

    def test_switch_to_docs(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        bm.create_docs_branch("WI-2026-001")
        gc.checkout("main")
        bm.switch_to_docs("WI-2026-001")
        assert gc.current_branch() == "design/WI-2026-001-docs"

    def test_switch_to_dev(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        bm.create_dev_branch("WI-2026-001")
        gc.checkout("main")
        bm.switch_to_dev("WI-2026-001")
        assert gc.current_branch() == "feature/WI-2026-001-dev"

    def test_uncommitted_changes_block_switch(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        bm.create_docs_branch("WI-2026-001")
        gc.checkout("main")
        (git_repo / "dirty.txt").write_text("uncommitted")
        gc._run("add", "dirty.txt")
        with pytest.raises(BranchError, match="uncommitted"):
            bm.switch_to_docs("WI-2026-001")

    def test_merge_to_main(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        bm.create_docs_branch("WI-2026-001")
        (git_repo / "spec.md").write_text("# Spec")
        gc.add_and_commit("add spec", ["spec.md"])
        gc.checkout("main")
        bm.merge_to_main("design/WI-2026-001-docs")
        assert (git_repo / "spec.md").exists()

    def test_check_baseline_pass(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        spec_dir = git_repo / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("spec")
        (spec_dir / "plan.md").write_text("plan")
        assert bm.check_baseline("specs/001") is True

    def test_check_baseline_fail(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        assert bm.check_baseline("specs/missing") is False

    def test_idempotent_create(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        bm.create_docs_branch("WI-2026-001")
        gc.checkout("main")
        name = bm.create_docs_branch("WI-2026-001")
        assert name == "design/WI-2026-001-docs"
