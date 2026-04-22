"""Git CLI wrapper for repository operations."""

from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


def _dedupe_text_items(values: object) -> tuple[str, ...]:
    deduped: list[str] = []
    for value in values or ():
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


class GitError(Exception):
    """Raised when a git operation fails."""


class IndexLockState(str, Enum):
    """Classification of the repository's ``.git/index.lock`` state."""

    MISSING = "missing"
    ACTIVE = "active"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class IndexLockInspection:
    """Structured result for ``.git/index.lock`` preflight checks."""

    state: IndexLockState
    path: Path
    active_processes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "active_processes",
            _dedupe_text_items(self.active_processes),
        )


@dataclass(frozen=True, slots=True)
class LocalBranchInspection:
    """Read-only snapshot of one local branch."""

    name: str
    head_commit: str
    is_current: bool
    upstream: str | None
    worktree_path: Path | None


@dataclass(frozen=True, slots=True)
class WorktreeInspection:
    """Read-only snapshot of one registered worktree."""

    path: Path
    head_commit: str
    branch: str | None


@dataclass(frozen=True, slots=True)
class BranchDivergence:
    """Ahead/behind counts for ``branch`` relative to ``base``."""

    branch: str
    base: str
    ahead_of_base: int
    behind_base: int


class GitClient:
    """Thin wrapper around git CLI commands."""

    def __init__(
        self,
        repo_path: Path,
        *,
        write_lock_timeout_sec: float = 10.0,
        write_lock_poll_sec: float = 0.05,
    ) -> None:
        self.repo_path = repo_path.resolve()
        self._write_lock_timeout_sec = write_lock_timeout_sec
        self._write_lock_poll_sec = write_lock_poll_sec

    @property
    def git_dir(self) -> Path:
        """Return the effective git dir, resolving worktree indirection if needed."""
        dot_git = self.repo_path / ".git"
        if dot_git.is_dir():
            return dot_git
        if dot_git.is_file():
            head = dot_git.read_text(encoding="utf-8").strip()
            if head.startswith("gitdir:"):
                raw = head.split(":", 1)[1].strip()
                path = Path(raw)
                if not path.is_absolute():
                    path = (self.repo_path / path).resolve()
                return path
        return dot_git

    @property
    def index_lock_path(self) -> Path:
        """Return the repository's ``index.lock`` path."""
        return self.git_dir / "index.lock"

    @property
    def repo_write_lock_path(self) -> Path:
        """Return the framework-owned repo write guard lock path."""
        return self.git_dir / "ai-sdlc-write.lock"

    @staticmethod
    def is_write_command(*args: str) -> bool:
        """Return whether a git subcommand mutates repo/index/ref state."""
        if not args:
            return False
        cmd = args[0]
        if cmd in {
            "init",
            "add",
            "commit",
            "merge",
            "checkout",
            "switch",
            "push",
            "reset",
            "rebase",
            "stash",
            "tag",
        }:
            return True
        if cmd == "branch":
            if len(args) == 1:
                return False
            if args[1].startswith("-"):
                destructive = {"-d", "-D", "-m", "-M", "-c", "-C"}
                return any(arg in destructive for arg in args[1:])
            return True
        if cmd == "worktree":
            return len(args) > 1 and args[1] in {
                "add",
                "remove",
                "move",
                "prune",
                "lock",
                "unlock",
            }
        return False

    def _run(self, *args: str) -> str:
        """Execute a git command and return stdout.

        Raises:
            GitError: If the command exits with non-zero status.
        """
        if self.is_write_command(*args):
            with self._repo_write_guard(*args):
                self._raise_if_index_lock_not_ready()
                return self._run_raw(*args)
        return self._run_raw(*args)

    def _run_raw(self, *args: str) -> str:
        """Execute a git command without acquiring the framework repo write guard."""
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

    @contextmanager
    def _repo_write_guard(self, *args: str):
        """Serialize framework-owned git write commands per repository."""
        self.repo_write_lock_path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self._write_lock_timeout_sec

        while True:
            try:
                fd = os.open(
                    self.repo_write_lock_path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    0o600,
                )
                break
            except FileExistsError:
                if self._clear_stale_repo_write_lock():
                    continue
                if time.monotonic() >= deadline:
                    raise GitError(
                        "Timed out waiting for repository git write guard; "
                        "do not launch parallel git add/commit/merge/checkout flows "
                        f"in {self.repo_path}"
                    ) from None
                time.sleep(self._write_lock_poll_sec)

        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "pid": os.getpid(),
                    "repo": str(self.repo_path),
                    "args": list(args),
                    "started_at": time.time(),
                },
                fh,
            )

        try:
            yield
        finally:
            with suppress(FileNotFoundError):
                self.repo_write_lock_path.unlink()

    def _clear_stale_repo_write_lock(self) -> bool:
        """Remove a stale framework repo write lock if its owner PID is gone."""
        path = self.repo_write_lock_path
        if not path.exists():
            return False

        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return False

        if not raw.strip():
            return False

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return False
        pid = int(payload.get("pid", 0) or 0)
        if pid <= 0:
            return False
        if pid > 0 and self._pid_is_active(pid):
            return False
        try:
            path.unlink()
        except FileNotFoundError:
            return False
        return True

    def inspect_index_lock(self) -> IndexLockInspection:
        """Classify ``.git/index.lock`` as missing, active, or stale."""
        path = self.index_lock_path
        if not path.exists():
            return IndexLockInspection(IndexLockState.MISSING, path)
        active = self._list_active_git_processes()
        state = IndexLockState.ACTIVE if active else IndexLockState.STALE
        return IndexLockInspection(state=state, path=path, active_processes=active)

    def remove_stale_index_lock(self) -> None:
        """Explicit stale-lock cleanup path. Never runs automatically."""
        inspection = self.inspect_index_lock()
        if inspection.state is IndexLockState.MISSING:
            return
        if inspection.state is IndexLockState.ACTIVE:
            raise GitError(
                "Active git process appears to hold .git/index.lock; "
                f"wait for it to finish instead of deleting {inspection.path}. "
                f"Active processes: {', '.join(inspection.active_processes[:3])}"
            )
        inspection.path.unlink(missing_ok=True)

    def _raise_if_index_lock_not_ready(self) -> None:
        inspection = self.inspect_index_lock()
        if inspection.state is IndexLockState.MISSING:
            return
        if inspection.state is IndexLockState.ACTIVE:
            raise GitError(
                "Active git process appears to hold .git/index.lock; "
                f"wait and retry instead of deleting {inspection.path}. "
                f"Active processes: {', '.join(inspection.active_processes[:3])}"
            )
        raise GitError(
            f"Stale {inspection.path} detected; confirm no active git process exists "
            "and call remove_stale_index_lock() explicitly. Do not delete lock files by default."
        )

    def _list_active_git_processes(self) -> tuple[str, ...]:
        """Best-effort process snapshot used only to avoid default stale-lock deletion."""
        try:
            result = subprocess.run(
                ["ps", "-ax", "-o", "pid=,command="],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return ()
        if result.returncode != 0:
            return ()

        active: list[str] = []
        for raw in result.stdout.splitlines():
            line = raw.strip()
            if not line:
                continue
            lowered = line.lower()
            if " git " in f" {lowered} " or lowered.startswith("git "):
                active.append(line)
        return tuple(active)

    @staticmethod
    def _pid_is_active(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        else:
            return True

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

    def revision_exists(self, revision: str) -> bool:
        """Return whether ``revision`` resolves to a commit."""
        try:
            self._run("rev-parse", "--verify", f"{revision}^{{commit}}")
            return True
        except GitError:
            return False

    def resolve_revision(self, revision: str, *, short: bool = False) -> str:
        """Resolve ``revision`` to a commit hash."""
        args = ["rev-parse"]
        if short:
            args.append("--short")
        args.extend(["--verify", f"{revision}^{{commit}}"])
        return self._run(*args)

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

    def merge_base(self, left: str, right: str) -> str:
        """Return the merge-base commit for ``left`` and ``right``."""
        return self._run("merge-base", left, right)

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """Return whether ``ancestor`` is contained in ``descendant`` history."""
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True
        if result.returncode == 1:
            return False
        raise GitError(
            "git merge-base --is-ancestor failed "
            f"(exit {result.returncode}): {result.stderr.strip()}"
        )

    def changed_paths(self, base: str, target: str) -> tuple[str, ...]:
        """Return repo-relative changed paths between ``base`` and ``target``."""
        raw = self._run("diff", "--name-only", f"{base}..{target}")
        return tuple(path for path in raw.splitlines() if path.strip())

    def revision_divergence(self, revision: str, *, base: str = "main") -> BranchDivergence:
        """Return ahead/behind counts for ``revision`` relative to ``base``."""
        raw = self._run("rev-list", "--left-right", "--count", f"{base}...{revision}")
        behind_raw, ahead_raw = raw.split()
        return BranchDivergence(
            branch=revision,
            base=base,
            ahead_of_base=int(ahead_raw),
            behind_base=int(behind_raw),
        )

    def path_exists_at_revision(self, revision: str, path: str) -> bool:
        """Return whether ``path`` exists at ``revision``."""
        result = subprocess.run(
            ["git", "cat-file", "-e", f"{revision}:{path}"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True
        if result.returncode == 128:
            return False
        raise GitError(
            f"git cat-file -e {revision}:{path} failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )

    def read_file_at_revision(self, revision: str, path: str) -> str:
        """Return file contents for ``path`` at ``revision``."""
        return self._run("show", f"{revision}:{path}")

    def list_worktrees(self) -> tuple[WorktreeInspection, ...]:
        """Return registered worktrees from ``git worktree list --porcelain``."""
        raw = self._run("worktree", "list", "--porcelain")
        items: list[WorktreeInspection] = []
        current_path: Path | None = None
        current_head = ""
        current_branch: str | None = None

        def _flush() -> None:
            if current_path is None:
                return
            items.append(
                WorktreeInspection(
                    path=current_path,
                    head_commit=current_head,
                    branch=current_branch,
                )
            )

        for line in raw.splitlines():
            if not line.strip():
                _flush()
                current_path = None
                current_head = ""
                current_branch = None
                continue
            if line.startswith("worktree "):
                current_path = Path(line.removeprefix("worktree ").strip()).resolve()
            elif line.startswith("HEAD "):
                current_head = line.removeprefix("HEAD ").strip()
            elif line.startswith("branch "):
                ref = line.removeprefix("branch ").strip()
                current_branch = ref.removeprefix("refs/heads/")

        _flush()
        return tuple(items)

    def list_local_branches(self) -> tuple[LocalBranchInspection, ...]:
        """Return local branches with upstream and worktree binding."""
        worktree_by_branch = {
            item.branch: item.path
            for item in self.list_worktrees()
            if item.branch is not None
        }
        raw = self._run(
            "for-each-ref",
            "--format=%(refname:short)%00%(objectname:short)%00%(upstream:short)%00%(HEAD)",
            "refs/heads",
        )
        items: list[LocalBranchInspection] = []
        for line in raw.splitlines():
            if not line:
                continue
            name, head_commit, upstream, head_marker = line.split("\0")
            normalized_upstream = upstream or None
            items.append(
                LocalBranchInspection(
                    name=name,
                    head_commit=head_commit,
                    is_current=head_marker.strip() == "*",
                    upstream=normalized_upstream,
                    worktree_path=worktree_by_branch.get(name),
                )
            )
        return tuple(sorted(items, key=lambda item: item.name))

    def branch_divergence(self, branch: str, *, base: str = "main") -> BranchDivergence:
        """Return ahead/behind counts for ``branch`` relative to ``base``."""
        raw = self._run("rev-list", "--left-right", "--count", f"{base}...{branch}")
        behind_raw, ahead_raw = raw.split()
        return BranchDivergence(
            branch=branch,
            base=base,
            ahead_of_base=int(ahead_raw),
            behind_base=int(behind_raw),
        )

    def add_and_commit(self, message: str, paths: list[str] | None = None) -> str:
        """Stage files and commit.

        Args:
            message: Commit message.
            paths: Specific paths to add. If None, adds all changes.

        Returns:
            The short commit hash.
        """
        with self._repo_write_guard("add", "status", "diff", "commit"):
            self._raise_if_index_lock_not_ready()
            if paths:
                self._run_raw("add", *paths)
            else:
                self._run_raw("add", ".")
            self._run_raw("status", "--short")
            self._run_raw("diff", "--cached", "--stat")
            self._run_raw("commit", "-m", message)
            return self._run_raw("rev-parse", "--short", "HEAD")

    def head_commit_timestamp(self) -> str:
        """Return the ISO timestamp of the current HEAD commit."""
        return self._run("show", "-s", "--format=%cI", "HEAD")

    def merge(self, source: str, target: str) -> None:
        """Merge source branch into target branch.

        Checks out target, merges source, then returns to original branch.
        """
        original = self.current_branch()
        with self._repo_write_guard("checkout", "merge", "checkout"):
            self._raise_if_index_lock_not_ready()
            self._run_raw("checkout", target)
            self._run_raw("merge", source, "--no-edit")
            if original != target:
                self._run_raw("checkout", original)

    def push(self, remote: str = "origin", branch: str = "") -> None:
        """Push the current branch, after add/status/diff/commit has finished."""
        if branch:
            self._run("push", remote, branch)
            return
        self._run("push", remote, self.current_branch())
