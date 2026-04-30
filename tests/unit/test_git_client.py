"""Unit tests for GitClient write guardrails."""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from ai_sdlc.branch.git_client import (
    GitClient,
    GitError,
    IndexLockInspection,
    IndexLockState,
    LocalBranchInspection,
)


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


def test_write_commands_block_while_repo_guard_is_held(git_repo: Path) -> None:
    first = GitClient(git_repo)
    second = GitClient(
        git_repo,
        write_lock_timeout_sec=0.01,
        write_lock_poll_sec=0.001,
    )

    with (
        first._repo_write_guard("add", "."),
        pytest.raises(GitError, match="Timed out waiting"),
    ):
        second._run("commit", "--allow-empty", "-m", "guarded")


def test_clear_stale_repo_write_lock_ignores_raced_file_removal(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git = GitClient(git_repo)

    class _RacyLockPath:
        def exists(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            raise FileNotFoundError

        def unlink(self) -> None:
            raise AssertionError("unlink should not run when the lock file already disappeared")

    monkeypatch.setattr(
        GitClient,
        "repo_write_lock_path",
        property(lambda self: _RacyLockPath()),
    )

    assert git._clear_stale_repo_write_lock() is False


def test_clear_stale_repo_write_lock_keeps_incomplete_payload(
    git_repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git = GitClient(git_repo)

    class _IncompleteLockPath:
        def exists(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            return "{"

        def unlink(self) -> None:
            raise AssertionError("unlink should not run for an in-flight lock payload")

    monkeypatch.setattr(
        GitClient,
        "repo_write_lock_path",
        property(lambda self: _IncompleteLockPath()),
    )

    assert git._clear_stale_repo_write_lock() is False


def test_pid_is_active_uses_windows_process_query_without_os_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signature_attrs: dict[str, tuple[object, object]] = {}

    class _FakeWinFunc:
        def __init__(self, name: str, result: int) -> None:
            self.name = name
            self.result = result
            self.argtypes = None
            self.restype = None

        def __call__(self, *_args):
            signature_attrs[self.name] = (self.argtypes, self.restype)
            if self.name == "GetExitCodeProcess":
                _args[1]._obj.value = 259
            return self.result

    def _unexpected_kill(_pid: int, _signal: int) -> None:
        raise AssertionError("Windows PID probing must not call os.kill")

    monkeypatch.setattr("ai_sdlc.branch.git_client.os.name", "nt")
    monkeypatch.setattr("ai_sdlc.branch.git_client.os.kill", _unexpected_kill)
    monkeypatch.setattr(
        "ai_sdlc.branch.git_client.ctypes.windll",
        SimpleNamespace(
            kernel32=SimpleNamespace(
                OpenProcess=_FakeWinFunc("OpenProcess", 123),
                GetExitCodeProcess=_FakeWinFunc("GetExitCodeProcess", 1),
                CloseHandle=_FakeWinFunc("CloseHandle", 1),
                GetLastError=_FakeWinFunc("GetLastError", 0),
            )
        ),
        raising=False,
    )

    assert GitClient._pid_is_active(42) is True
    assert signature_attrs["OpenProcess"][1] is not None
    assert signature_attrs["GetExitCodeProcess"][1] is not None
    assert signature_attrs["CloseHandle"][1] is not None


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


def test_index_lock_inspection_runtime_object_canonicalizes_active_processes(
    git_repo: Path,
) -> None:
    inspection = IndexLockInspection(
        state=IndexLockState.ACTIVE,
        path=git_repo / ".git" / "index.lock",
        active_processes=("123 git commit", "123 git commit", "456 git merge"),
    )

    assert inspection.active_processes == ("123 git commit", "456 git merge")


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


def test_list_local_branches_includes_worktree_binding(git_repo: Path, tmp_path: Path) -> None:
    subprocess.run(
        ["git", "branch", "codex/demo-scratch"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    scratch_tree = tmp_path / "scratch-tree"
    subprocess.run(
        ["git", "worktree", "add", str(scratch_tree), "codex/demo-scratch"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    branches = GitClient(git_repo).list_local_branches()

    branch_names = [item.name for item in branches]
    assert branch_names == sorted(branch_names)

    scratch = next(item for item in branches if item.name == "codex/demo-scratch")
    assert scratch.upstream is None
    assert scratch.worktree_path == scratch_tree.resolve()


def test_branch_divergence_against_main_reports_ahead_and_behind(git_repo: Path) -> None:
    default_branch = GitClient(git_repo).default_branch_name()
    subprocess.run(
        ["git", "checkout", "-b", "feature/diverge-demo"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (git_repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.txt"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "feature commit"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "checkout", default_branch],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (git_repo / "main.txt").write_text("main\n", encoding="utf-8")
    subprocess.run(["git", "add", "main.txt"], cwd=git_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "main commit"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    divergence = GitClient(git_repo).branch_divergence(
        "feature/diverge-demo", base=default_branch
    )

    assert divergence.branch == "feature/diverge-demo"
    assert divergence.base == default_branch
    assert divergence.ahead_of_base == 1
    assert divergence.behind_base == 1


def test_list_worktrees_returns_paths_and_checked_out_branches(
    git_repo: Path, tmp_path: Path
) -> None:
    subprocess.run(
        ["git", "branch", "codex/worktree-demo"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    scratch_tree = tmp_path / "worktree-demo"
    subprocess.run(
        ["git", "worktree", "add", str(scratch_tree), "codex/worktree-demo"],
        cwd=git_repo,
        check=True,
        capture_output=True,
        text=True,
    )

    worktrees = GitClient(git_repo).list_worktrees()
    default_branch = GitClient(git_repo).default_branch_name()

    assert any(
        item.path == git_repo.resolve() and item.branch == default_branch
        for item in worktrees
    )
    assert any(
        item.path == scratch_tree.resolve() and item.branch == "codex/worktree-demo"
        for item in worktrees
    )


def test_default_branch_name_supports_custom_initial_branch(tmp_path: Path) -> None:
    repo = tmp_path / "custom-default-branch"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--initial-branch=trunk"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (repo / "README.md").write_text("# trunk repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    assert GitClient(repo).default_branch_name() == "trunk"


def test_default_branch_name_rejects_feature_only_upstream_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "feature-only"
    repo.mkdir()
    client = GitClient(repo)
    monkeypatch.setattr(client, "_read_symbolic_ref", lambda _ref: None)
    monkeypatch.setattr(client, "branch_exists", lambda _name: False)
    monkeypatch.setattr(
        client,
        "list_local_branches",
        lambda: (
            LocalBranchInspection(
                name="feature/demo",
                head_commit="abc1234",
                is_current=True,
                upstream="origin/feature/demo",
                worktree_path=repo,
            ),
        ),
    )

    with pytest.raises(GitError, match="unable to determine repository default branch"):
        client.default_branch_name()


def test_run_raw_forces_utf8_decoding(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    client = GitClient(tmp_path)
    captured: dict[str, object] = {}

    def _fake_run(*_args, **kwargs):
        captured.update(kwargs)
        return subprocess.CompletedProcess(
            args=["git", "status"],
            returncode=0,
            stdout="ok\n",
            stderr="",
        )

    monkeypatch.setattr("ai_sdlc.branch.git_client.subprocess.run", _fake_run)

    assert client._run_raw("status") == "ok"
    assert captured["encoding"] == "utf-8"
    assert captured["errors"] == "replace"
    assert captured["timeout"] == 5.0


def test_run_raw_reports_git_command_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    client = GitClient(tmp_path, command_timeout_sec=0.25)

    def _fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["git", "status"], timeout=0.25)

    monkeypatch.setattr("ai_sdlc.branch.git_client.subprocess.run", _fake_run)

    with pytest.raises(GitError, match="git status timed out after 0.25 second"):
        client._run_raw("status")
