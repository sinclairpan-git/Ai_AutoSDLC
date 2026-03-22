"""Branch Manager — docs/dev dual-branch lifecycle management."""

from __future__ import annotations

import logging

from ai_sdlc.branch.file_guard import FileGuard
from ai_sdlc.branch.git_client import GitClient, GitError

logger = logging.getLogger(__name__)


class BranchError(Exception):
    """Raised when a branch operation violates policy."""


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
        name = f"design/{work_item_id}-docs"
        if self._git.branch_exists(name):
            self._git.checkout(name)
        else:
            self._git.create_branch(name, checkout=True)
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
        name = f"design/{work_item_id}-docs"
        self._git.checkout(name)

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
        name = f"feature/{work_item_id}-dev"
        self._git.checkout(name)
        if spec_dir:
            if not self.check_baseline(spec_dir):
                raise BranchError(
                    f"Baseline recheck failed after switching to {name}. "
                    f"spec.md and plan.md must exist in {spec_dir}."
                )
            root = self._git.repo_path
            for doc in ("spec.md", "plan.md"):
                self._file_guard.protect(str(root / spec_dir / doc))

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
        required = ["spec.md", "plan.md"]
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
