"""Branch Manager — docs/dev dual-branch lifecycle management."""

from __future__ import annotations

import logging

from ai_sdlc.branch.file_guard import FileGuard
from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.context.state import (
    build_resume_pack,
    load_checkpoint,
    save_checkpoint,
    save_resume_pack,
)
from ai_sdlc.gates.governance_guard import load_governance_state
from ai_sdlc.utils.helpers import now_iso

logger = logging.getLogger(__name__)


class BranchError(Exception):
    """Raised when a branch operation violates policy."""


class GovernanceNotFrozenError(BranchError):
    """Raised when governance has not been frozen for docs/dev entry."""


class BranchManager:
    """Manages the docs/dev dual-branch model for work items."""

    def __init__(
        self, git_client: GitClient, file_guard: FileGuard | None = None
    ) -> None:
        self._git = git_client
        self._file_guard = file_guard or FileGuard()

    def create_docs_branch(self, work_item_id: str) -> str:
        """Create and checkout the design docs branch.

        Returns:
            The branch name created.

        Raises:
            BranchError: If there are uncommitted changes.
        """
        self._guard_uncommitted()
        governance = self._require_frozen_governance(work_item_id)
        name = self._docs_branch_name(work_item_id)
        if self._git.branch_exists(name):
            self._git.checkout(name)
        else:
            self._git.create_branch(name, checkout=True)
        self._protect_governance_inputs(governance)
        return name

    def create_dev_branch(self, work_item_id: str) -> str:
        """Create and checkout the feature dev branch.

        Returns:
            The branch name created.

        Raises:
            BranchError: If there are uncommitted changes.
        """
        self._guard_uncommitted()
        name = f"feature/{work_item_id}-dev"
        if self._git.branch_exists(name):
            self._git.checkout(name)
        else:
            self._git.create_branch(name, checkout=True)
        return name

    def switch_to_docs(self, work_item_id: str) -> None:
        """Switch to the docs branch for a work item.

        Raises:
            BranchError: If there are uncommitted changes.
        """
        self._guard_uncommitted()
        governance = self._require_frozen_governance(work_item_id)
        name = self._resolve_docs_branch(work_item_id)
        self._git.checkout(name)
        self._protect_governance_inputs(governance)

    def switch_to_dev(self, work_item_id: str, spec_dir: str = "") -> None:
        """Switch to the dev branch for a work item.

        After switching, performs baseline recheck (BR-021)
        and protects spec.md/plan.md from modification (BR-022).

        Args:
            work_item_id: Work item identifier.
            spec_dir: Relative path to spec directory for baseline recheck.

        Raises:
            BranchError: If uncommitted changes or baseline recheck fails.
        """
        self._guard_uncommitted()
        governance = self._require_frozen_governance(work_item_id)
        name = f"feature/{work_item_id}-dev"
        previous_branch = self._current_branch()
        docs_baseline_ref = previous_branch or self._resolve_docs_branch(work_item_id)
        docs_baseline_at = now_iso()
        self._git.checkout(name)
        if spec_dir:
            if not self.check_baseline(spec_dir):
                self._git.checkout(previous_branch)
                raise BranchError(
                    f"Baseline recheck failed after switching to {name}. "
                    f"spec.md, plan.md, and tasks.md must exist in {spec_dir}."
                )
            root = self._git.repo_path
            for doc in ("spec.md", "plan.md"):
                self._file_guard.protect(str(root / spec_dir / doc))
        self._protect_governance_inputs(governance)
        self._refresh_branch_context(
            work_item_id=work_item_id,
            spec_dir=spec_dir,
            current_branch=name,
            docs_baseline_ref=docs_baseline_ref,
            docs_baseline_at=docs_baseline_at,
        )

    def merge_to_main(self, branch_name: str) -> None:
        """Merge a branch into main.

        Raises:
            BranchError: If there are uncommitted changes.
        """
        self._guard_uncommitted()
        self._git.merge(branch_name, "main")

    def check_baseline(self, spec_dir: str) -> bool:
        """Verify that docs-branch artifacts are accessible from current branch.

        Args:
            spec_dir: Relative path to the spec directory.

        Returns:
            True if baseline files are accessible.
        """
        root = self._git.repo_path
        spec_path = root / spec_dir
        if not spec_path.is_dir():
            return False
        required = ["spec.md", "plan.md", "tasks.md"]
        return all((spec_path / f).exists() for f in required)

    def create_hotfix_branch(self, issue_id: str) -> str:
        """Create and checkout a hotfix branch.

        Args:
            issue_id: Issue identifier.

        Returns:
            The branch name created.

        Raises:
            BranchError: If there are uncommitted changes.
        """
        self._guard_uncommitted()
        name = f"hotfix/{issue_id}"
        if self._git.branch_exists(name):
            self._git.checkout(name)
        else:
            self._git.create_branch(name, checkout=True)
        return name

    def create_release_branch(self, version: str) -> str:
        """Create and checkout a release branch.

        Args:
            version: Version string (e.g. "1.0.0").

        Returns:
            The branch name created.

        Raises:
            BranchError: If there are uncommitted changes.
        """
        self._guard_uncommitted()
        name = f"release/{version}"
        if self._git.branch_exists(name):
            self._git.checkout(name)
        else:
            self._git.create_branch(name, checkout=True)
        return name

    @property
    def file_guard(self) -> FileGuard:
        """Return the file guard instance."""
        return self._file_guard

    def _guard_uncommitted(self) -> None:
        """Raise BranchError if there are uncommitted changes."""
        try:
            if self._git.has_uncommitted_changes():
                raise BranchError(
                    "Cannot switch branches with uncommitted changes. "
                    "Commit or stash changes first."
                )
        except GitError as exc:
            raise BranchError(f"Git check failed: {exc}") from exc

    def _current_branch(self) -> str:
        try:
            return self._git.current_branch()
        except GitError as exc:
            raise BranchError(f"Git branch lookup failed: {exc}") from exc

    def _require_frozen_governance(self, work_item_id: str):
        governance = load_governance_state(self._git.repo_path, work_item_id)
        if governance is None or not governance.frozen:
            raise GovernanceNotFrozenError(
                f"Cannot enter docs/dev flow for {work_item_id}: governance not frozen."
            )
        return governance

    def _protect_governance_inputs(self, governance_state) -> None:
        for name in (
            "tech_profile",
            "constitution",
            "clarify",
            "quality_policy",
            "branch_policy",
            "parallel_policy",
        ):
            item = governance_state.items.get(name)
            if item and item.exists and item.path:
                self._file_guard.protect(item.path)

    def _refresh_branch_context(
        self,
        *,
        work_item_id: str,
        spec_dir: str,
        current_branch: str,
        docs_baseline_ref: str,
        docs_baseline_at: str,
    ) -> None:
        root = self._git.repo_path
        checkpoint = load_checkpoint(root)
        if checkpoint is None:
            return

        checkpoint.feature.id = work_item_id
        if spec_dir:
            checkpoint.feature.spec_dir = spec_dir
        checkpoint.feature.feature_branch = current_branch
        checkpoint.feature.current_branch = current_branch
        checkpoint.feature.docs_baseline_ref = docs_baseline_ref
        checkpoint.feature.docs_baseline_at = docs_baseline_at
        save_checkpoint(root, checkpoint)

        resume_pack = build_resume_pack(root)
        if resume_pack is not None:
            save_resume_pack(root, resume_pack)

    @staticmethod
    def _docs_branch_name(work_item_id: str) -> str:
        """Return the canonical docs-branch name mandated by the spec."""
        return f"feature/{work_item_id}-docs"

    @staticmethod
    def _legacy_docs_branch_name(work_item_id: str) -> str:
        """Return the pre-remediation docs-branch name kept for compatibility."""
        return f"design/{work_item_id}-docs"

    def _resolve_docs_branch(self, work_item_id: str) -> str:
        """Resolve docs branch with legacy fallback for pre-existing repos."""
        preferred = self._docs_branch_name(work_item_id)
        if self._git.branch_exists(preferred):
            return preferred
        legacy = self._legacy_docs_branch_name(work_item_id)
        if self._git.branch_exists(legacy):
            return legacy
        return preferred
