"""Unit tests for GitClient write guardrails."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from ai_sdlc.branch.git_client import GitClient, GitError, IndexLockState


class _RecordingGitClient(GitClient):
    def __init__(self, repo_path: Path) -> None:
        super().__init__(repo_path)
        self.calls: list[tuple[str, ...]] = []

    def _run_raw(self, *args: str) -> str:
        self.calls.append(args)
        if args[:3] == ("diff", "--cached", "--stat"):
            return " README.md | 1 +\n"
        if args[:2] == ("status", "--short"):
            return "M  README.md\n"
        if args[:2] == ("rev-parse", "--short"):
            return "abc1234"
        return ""


class _SlowGitClient(GitClient):
    def __init__(self, repo_path: Path, events: list[tuple[str, str, float]]) -> None:
        super().__init__(repo_path, write_lock_timeout_sec=1.0, write_lock_poll_sec=0.01)
        self._events = events

    def _run_raw(self, *args: str) -> str:
        self._events.append(("start", args[0], time.monotonic()))
        time.sleep(0.12)
        self._events.append(("end", args[0], time.monotonic()))
        return ""


def test_is_write_command_classifies_git_mutations(git_repo: Path) -> None:
    git = GitClient(git_repo)

    assert git.is_write_command("add", ".")
    assert git.is_write_command("commit", "-m", "msg")
    assert git.is_write_command("merge", "feature/x")
    assert git.is_write_command("checkout", "main")
    assert git.is_write_command("branch", "-D", "feature/x")
    assert git.is_write_command("branch", "feature/x")
    assert git.is_write_command("worktree", "remove", "/tmp/demo")
    assert git.is_write_command("push", "origin", "main")

    assert not git.is_write_command("status", "--short")
    assert not git.is_write_command("diff", "--cached")
    assert not git.is_write_command("rev-parse", "--short", "HEAD")


def test_add_and_commit_runs_add_status_diff_commit_sequence(git_repo: Path) -> None:
    git = _RecordingGitClient(git_repo)

    short_hash = git.add_and_commit("test commit", ["README.md"])

    assert short_hash == "abc1234"
    assert git.calls == [
        ("add", "README.md"),
        ("status", "--short"),
        ("diff", "--cached", "--stat"),
        ("commit", "-m", "test commit"),
        ("rev-parse", "--short", "HEAD"),
    ]


def test_write_commands_are_serialized_per_repo(git_repo: Path) -> None:
    events: list[tuple[str, str, float]] = []
    first = _SlowGitClient(git_repo, events)
    second = _SlowGitClient(git_repo, events)

    t1 = threading.Thread(target=first._run, args=("add", "."), daemon=True)
    t2 = threading.Thread(
        target=second._run,
        args=("commit", "--allow-empty", "-m", "guarded"),
        daemon=True,
    )

    t1.start()
    time.sleep(0.02)
    t2.start()
    t1.join()
    t2.join()

    add_start = next(ts for kind, cmd, ts in events if kind == "start" and cmd == "add")
    add_end = next(ts for kind, cmd, ts in events if kind == "end" and cmd == "add")
    commit_start = next(
        ts for kind, cmd, ts in events if kind == "start" and cmd == "commit"
    )

    assert add_start < add_end <= commit_start


def test_inspect_index_lock_marks_active_git_process(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    git = GitClient(git_repo)
    git.index_lock_path.write_text("lock", encoding="utf-8")
    monkeypatch.setattr(
        git,
        "_list_active_git_processes",
        lambda: ("123 git commit",),
    )

    inspection = git.inspect_index_lock()

    assert inspection.state is IndexLockState.ACTIVE
    assert inspection.active_processes == ("123 git commit",)

    with pytest.raises(GitError, match="Active git process appears to hold .git/index.lock"):
        git.checkout("main")


def test_remove_stale_index_lock_requires_no_active_git_process(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git = GitClient(git_repo)
    git.index_lock_path.write_text("lock", encoding="utf-8")
    monkeypatch.setattr(git, "_list_active_git_processes", lambda: ())

    inspection = git.inspect_index_lock()
    assert inspection.state is IndexLockState.STALE

    git.remove_stale_index_lock()
    assert not git.index_lock_path.exists()


def test_remove_stale_index_lock_blocks_when_process_still_active(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git = GitClient(git_repo)
    git.index_lock_path.write_text("lock", encoding="utf-8")
    monkeypatch.setattr(
        git,
        "_list_active_git_processes",
        lambda: ("456 git merge",),
    )

    with pytest.raises(GitError, match="Active git process appears to hold .git/index.lock"):
        git.remove_stale_index_lock()
