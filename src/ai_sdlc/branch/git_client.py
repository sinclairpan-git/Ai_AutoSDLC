"""Git CLI wrapper for repository operations."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class GitError(Exception):
    """Raised when a git operation fails."""


class GitClient:
    """Thin wrapper around git CLI commands."""

    def __init__(self, repo_path: Path) -> None:
        self.repo_path = repo_path.resolve()

    def _run(self, *args: str) -> str:
        """Execute a git command and return stdout.

        Raises:
            GitError: If the command exits with non-zero status.
        """
        cmd = ["git", *args]
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise GitError("git is not installed or not on PATH") from exc

        if result.returncode != 0:
            raise GitError(
                f"git {' '.join(args)} failed (exit {result.returncode}): "
                f"{result.stderr.strip()}"
            )
        return result.stdout.strip()

    def init(self) -> None:
        """Initialize a new git repository."""
        self._run("init")

    def current_branch(self) -> str:
        """Return the name of the current branch."""
        return self._run("rev-parse", "--abbrev-ref", "HEAD")

    def branch_exists(self, name: str) -> bool:
        """Check if a branch exists."""
        try:
            self._run("rev-parse", "--verify", name)
            return True
        except GitError:
            return False

    def create_branch(self, name: str, *, checkout: bool = True) -> None:
        """Create a new branch, optionally checking it out."""
        if checkout:
            self._run("checkout", "-b", name)
        else:
            self._run("branch", name)

    def checkout(self, name: str) -> None:
        """Switch to an existing branch."""
        self._run("checkout", name)

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in the working tree."""
        status = self._run("status", "--porcelain")
        return len(status) > 0

    def add_and_commit(self, message: str, paths: list[str] | None = None) -> str:
        """Stage files and commit.

        Args:
            message: Commit message.
            paths: Specific paths to add. If None, adds all changes.

        Returns:
            The short commit hash.
        """
        if paths:
            self._run("add", *paths)
        else:
            self._run("add", ".")
        self._run("commit", "-m", message)
        return self._run("rev-parse", "--short", "HEAD")

    def head_commit_timestamp(self) -> str:
        """Return the ISO timestamp of the current HEAD commit."""
        return self._run("show", "-s", "--format=%cI", "HEAD")

    def merge(self, source: str, target: str) -> None:
        """Merge source branch into target branch.

        Checks out target, merges source, then returns to original branch.
        """
        original = self.current_branch()
        self.checkout(target)
        self._run("merge", source, "--no-edit")
        if original != target:
            self.checkout(original)
