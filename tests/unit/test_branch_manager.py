"""Unit tests for Branch Manager."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_sdlc.branch.branch_manager import (
    BranchError,
    BranchManager,
    GovernanceNotFrozenError,
)
from ai_sdlc.branch.file_guard import FileGuard, ProtectedFileError
from ai_sdlc.branch.git_client import GitClient
from ai_sdlc.context.state import load_checkpoint, load_resume_pack, save_checkpoint
from ai_sdlc.core.config import YamlStore
from ai_sdlc.generators.template_gen import TemplateGenerator
from ai_sdlc.models.gate import GovernanceItem, GovernanceState
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def _write_frozen_governance(root: Path, work_item_id: str) -> None:
    item_paths = {
        "tech_profile": root / ".ai-sdlc" / "profiles" / "tech-stack.yml",
        "constitution": root / ".ai-sdlc" / "memory" / "constitution.md",
        "clarify": root / ".ai-sdlc" / "profiles" / "decisions.yml",
        "quality_policy": root / "policies" / "quality-gate.md",
        "branch_policy": root / "policies" / "git-branch.md",
        "parallel_policy": root / "policies" / "multi-agent.md",
    }
    for name, path in item_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name}: present\n", encoding="utf-8")

    gov_path = root / ".ai-sdlc" / "work-items" / work_item_id / "governance.yaml"
    state = GovernanceState(frozen=True, frozen_at="2026-03-28T12:00:00+00:00")
    for name, path in item_paths.items():
        state.items[name] = GovernanceItem(
            exists=True,
            path=str(path),
            verified_at="2026-03-28T12:00:00+00:00",
        )
    YamlStore.save(gov_path, state)
    if (root / ".git").exists():
        subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "freeze governance"],
            cwd=root,
            check=True,
            capture_output=True,
        )


class TestBranchManager:
    def test_create_docs_branch(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        _write_frozen_governance(git_repo, "WI-2026-001")
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
        _write_frozen_governance(git_repo, "WI-2026-001")
        bm.create_docs_branch("WI-2026-001")
        gc.checkout(gc.default_branch_name())
        bm.switch_to_docs("WI-2026-001")
        assert gc.current_branch() == "feature/WI-2026-001-docs"

    def test_switch_to_docs_falls_back_to_legacy_design_branch(
        self, git_repo: Path
    ) -> None:
        gc = GitClient(git_repo)
        _write_frozen_governance(git_repo, "WI-2026-001")
        gc.create_branch("design/WI-2026-001-docs", checkout=True)
        gc.checkout(gc.default_branch_name())

        bm = BranchManager(gc)
        bm.switch_to_docs("WI-2026-001")

        assert gc.current_branch() == "design/WI-2026-001-docs"

    def test_switch_to_dev(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        _write_frozen_governance(git_repo, "WI-2026-001")
        bm.create_dev_branch("WI-2026-001")
        gc.checkout(gc.default_branch_name())
        bm.switch_to_dev("WI-2026-001")
        assert gc.current_branch() == "feature/WI-2026-001-dev"

    def test_uncommitted_changes_block_switch(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        _write_frozen_governance(git_repo, "WI-2026-001")
        bm.create_docs_branch("WI-2026-001")
        gc.checkout(gc.default_branch_name())
        (git_repo / "dirty.txt").write_text("uncommitted")
        gc._run("add", "dirty.txt")
        with pytest.raises(BranchError, match="uncommitted"):
            bm.switch_to_docs("WI-2026-001")

    def test_merge_to_main(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        _write_frozen_governance(git_repo, "WI-2026-001")
        bm.create_docs_branch("WI-2026-001")
        (git_repo / "spec.md").write_text("# Spec")
        gc.add_and_commit("add spec", ["spec.md"])
        gc.checkout(gc.default_branch_name())
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
        _write_frozen_governance(git_repo, "WI-2026-001")
        bm.create_docs_branch("WI-2026-001")
        gc.checkout(gc.default_branch_name())
        name = bm.create_docs_branch("WI-2026-001")
        assert name == "feature/WI-2026-001-docs"

    def test_create_docs_branch_requires_frozen_governance(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)

        with pytest.raises(GovernanceNotFrozenError, match="governance"):
            bm.create_docs_branch("WI-2026-001")

    def test_create_docs_branch_protects_governance_inputs(self, git_repo: Path) -> None:
        gc = GitClient(git_repo)
        bm = BranchManager(gc)
        _write_frozen_governance(git_repo, "WI-2026-001")

        bm.create_docs_branch("WI-2026-001")

        constitution = git_repo / ".ai-sdlc" / "memory" / "constitution.md"
        decisions = git_repo / ".ai-sdlc" / "profiles" / "decisions.yml"
        assert bm.file_guard.is_protected(str(constitution))
        assert bm.file_guard.is_protected(str(decisions))

        with pytest.raises(ProtectedFileError, match="protected file"):
            bm.file_guard.guard_write(str(constitution))


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
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        _write_frozen_governance(tmp_path, "WI-1")
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        mock_git.checkout.assert_called_once_with("feature/WI-1-dev")

    def test_switch_to_dev_spec_dir_baseline_fails(self, tmp_path: Path) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        _write_frozen_governance(tmp_path, "WI-1")
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
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        _write_frozen_governance(tmp_path, "WI-1")
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
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        _write_frozen_governance(tmp_path, "WI-1")
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
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        fg = FileGuard()
        bm = BranchManager(mock_git, file_guard=fg)
        _write_frozen_governance(tmp_path, "WI-1")
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        with pytest.raises(ProtectedFileError, match="protected file"):
            protected_spec.write_text("mutated", encoding="utf-8")

    def test_switch_to_dev_requires_frozen_governance(self, tmp_path: Path) -> None:
        spec_rel = "specs/wi"
        spec_path = tmp_path / spec_rel
        spec_path.mkdir(parents=True)
        (spec_path / "spec.md").write_text("s")
        (spec_path / "plan.md").write_text("p")
        (spec_path / "tasks.md").write_text("t")

        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        with pytest.raises(GovernanceNotFrozenError, match="governance"):
            bm.switch_to_dev("WI-1", spec_dir=spec_rel)

    def test_switch_to_dev_rolls_back_checkout_when_baseline_fails(
        self, tmp_path: Path
    ) -> None:
        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        _write_frozen_governance(tmp_path, "WI-1")

        with pytest.raises(BranchError, match="Baseline recheck failed"):
            bm.switch_to_dev("WI-1", spec_dir="missing")

        assert mock_git.checkout.call_args_list[0].args == ("feature/WI-1-dev",)
        assert mock_git.checkout.call_args_list[1].args == ("feature/WI-1-docs",)

    def test_switch_to_dev_updates_checkpoint_and_resume_pack(
        self, tmp_path: Path
    ) -> None:
        spec_rel = "specs/wi"
        spec_path = tmp_path / spec_rel
        spec_path.mkdir(parents=True)
        (spec_path / "spec.md").write_text("s")
        (spec_path / "plan.md").write_text("p")
        (spec_path / "tasks.md").write_text("t")

        checkpoint = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="WI-1",
                spec_dir=spec_rel,
                design_branch="feature/WI-1-docs",
                feature_branch="feature/WI-1-dev",
                current_branch="feature/WI-1-docs",
            ),
        )
        save_checkpoint(tmp_path, checkpoint)

        mock_git = MagicMock()
        mock_git.has_uncommitted_changes.return_value = False
        mock_git.current_branch.return_value = "feature/WI-1-docs"
        mock_git.repo_path = tmp_path

        bm = BranchManager(mock_git)
        _write_frozen_governance(tmp_path, "WI-1")
        bm.switch_to_dev("WI-1", spec_dir=spec_rel)

        refreshed = load_checkpoint(tmp_path, strict=True)
        assert refreshed is not None
        assert refreshed.feature.current_branch == "feature/WI-1-dev"
        assert refreshed.feature.docs_baseline_ref == "feature/WI-1-docs"
        assert refreshed.feature.docs_baseline_at != ""

        resume = load_resume_pack(tmp_path)
        assert resume.current_branch == "feature/WI-1-dev"
        assert resume.docs_baseline_ref == "feature/WI-1-docs"
        assert resume.working_set_snapshot.spec_path.endswith("spec.md")

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
