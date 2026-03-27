"""Unit tests for Branch Manager."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_sdlc.branch.branch_manager import BranchError, BranchManager
from ai_sdlc.branch.file_guard import FileGuard, ProtectedFileError
from ai_sdlc.branch.git_client import GitClient
from ai_sdlc.generators.template_gen import TemplateGenerator


class TestBranchManager:
    def test_create_docs_branch(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        name = bm.create_docs_branch("WI-2026-001")
        assert name == "feature/WI-2026-001-docs"
        assert gc.current_branch() == "feature/WI-2026-001-docs"

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
        assert gc.current_branch() == "feature/WI-2026-001-docs"

    def test_switch_to_docs_falls_back_to_legacy_design_branch(
        self, git_repo: Path
    ) -> None:
        gc = GitClient(git_repo)
        gc.create_branch("design/WI-2026-001-docs", checkout=True)
        gc.checkout("main")

        bm = BranchManager(gc)
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
        bm.merge_to_main("feature/WI-2026-001-docs")
        assert (git_repo / "spec.md").exists()

    def test_check_baseline_pass(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        spec_dir = git_repo / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("spec")
        (spec_dir / "plan.md").write_text("plan")
        (spec_dir / "tasks.md").write_text("tasks")
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
        assert name == "feature/WI-2026-001-docs"


class TestBranchManagerMockedGit:
    """Tests using a mocked GitClient (BR-021 / BR-022, hotfix/release)."""

    def test_switch_to_dev_spec_dir_baseline_pass(self, tmp_path: Path) -> None:
        spec_rel = "specs/wi"
        spec_path = tmp_path / spec_rel
        spec_path.mkdir(parents=True)
        (spec_path / "spec.md").write_text("s")
        (spec_path / "plan.md").write_text("p")
        (spec_path / "tasks.md").write_text("t")

        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        mock_git.checkout.assert_called_once_with("feature/WI-1-dev")

    def test_switch_to_dev_spec_dir_baseline_fails(self, tmp_path: Path) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        with pytest.raises(BranchError, match="Baseline recheck failed"):
            bm.switch_to_dev("WI-1", spec_dir="missing")

    def test_switch_to_dev_protects_spec_and_plan(self, tmp_path: Path) -> None:
        spec_rel = "specs/wi"
        spec_path = tmp_path / spec_rel
        spec_path.mkdir(parents=True)
        (spec_path / "spec.md").write_text("s")
        (spec_path / "plan.md").write_text("p")
        (spec_path / "tasks.md").write_text("t")

        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.repo_path = tmp_path

        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        assert fg.is_protected(str(tmp_path / spec_rel / "spec.md"))
        assert fg.is_protected(str(tmp_path / spec_rel / "plan.md"))

    def test_switch_to_dev_blocks_template_write_to_protected_spec(
        self, tmp_path: Path
    ) -> None:
        spec_rel = "specs/wi"
        spec_path = tmp_path / spec_rel
        spec_path.mkdir(parents=True)
        (spec_path / "spec.md").write_text("s")
        (spec_path / "plan.md").write_text("p")
        (spec_path / "tasks.md").write_text("t")

        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        (template_dir / "demo.j2").write_text("{{ title }}\n", encoding="utf-8")

        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.repo_path = tmp_path

        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        gen = TemplateGenerator(template_dir=template_dir, file_guard=fg)
        with pytest.raises(ProtectedFileError, match="protected file"):
            gen.render_to_file(
                "demo.j2",
                {"title": "blocked"},
                spec_path / "spec.md",
            )

    def test_switch_to_dev_blocks_direct_write_to_protected_spec(
        self, tmp_path: Path
    ) -> None:
        spec_rel = "specs/wi"
        spec_path = tmp_path / spec_rel
        spec_path.mkdir(parents=True)
        protected_spec = spec_path / "spec.md"
        protected_spec.write_text("s", encoding="utf-8")
        (spec_path / "plan.md").write_text("p", encoding="utf-8")
        (spec_path / "tasks.md").write_text("t", encoding="utf-8")

        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.repo_path = tmp_path

        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        with pytest.raises(ProtectedFileError, match="protected file"):
            protected_spec.write_text("mutated", encoding="utf-8")

    def test_create_hotfix_branch_new(self) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.branch_exists.return_value = False

        bm = BranchManager(mock_git)
        name = bm.create_hotfix_branch("ISSUE-42")

        assert name == "hotfix/ISSUE-42"
        mock_git.create_branch.assert_called_once_with("hotfix/ISSUE-42", checkout=True)

    def test_create_hotfix_branch_exists(self) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.branch_exists.return_value = True

        bm = BranchManager(mock_git)
        name = bm.create_hotfix_branch("ISSUE-42")

        assert name == "hotfix/ISSUE-42"
        mock_git.checkout.assert_called_once_with("hotfix/ISSUE-42")

    def test_create_release_branch_new(self) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.branch_exists.return_value = False

        bm = BranchManager(mock_git)
        name = bm.create_release_branch("1.0.0")

        assert name == "release/1.0.0"
        mock_git.create_branch.assert_called_once_with("release/1.0.0", checkout=True)

    def test_create_release_branch_exists(self) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.branch_exists.return_value = True

        bm = BranchManager(mock_git)
        name = bm.create_release_branch("1.0.0")

        assert name == "release/1.0.0"
        mock_git.checkout.assert_called_once_with("release/1.0.0")

    def test_file_guard_property(self) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        assert bm.file_guard is fg
