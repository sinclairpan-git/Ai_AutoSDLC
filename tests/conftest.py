"""Shared test fixtures for AI-SDLC."""

from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Generator, Iterable
from pathlib import Path

import pytest

_MANAGED_REPOSITORY_PATHS = (
    ".ai-sdlc/project/config/project-config.yaml",
    ".ai-sdlc/memory/ide-adapter-hint.md",
    ".claude/CLAUDE.md",
    ".github/copilot-instructions.md",
)

_PathState = dict[str, tuple[str, str]]


def _git_output(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=False, capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed with {result.returncode}")
    return result.stdout


def _find_repository_root(candidate: Path) -> Path | None:
    try:
        value = _git_output(candidate, "rev-parse", "--show-toplevel").decode().strip()
        root = Path(value).resolve()
    except (OSError, RuntimeError, UnicodeError):
        return None
    return root if root == candidate.resolve() else None


def _path_states(root: Path, paths: Iterable[Path]) -> _PathState:
    states = {}
    for path in paths:
        if path.is_symlink():
            kind, content = "symlink", path.readlink().as_posix().encode()
        elif path.is_file():
            kind, content = "file", path.read_bytes()
        elif path.is_dir():
            kind, content = "directory", None
        elif path.exists():
            kind, content = "other", None
        else:
            kind, content = "missing", None
        digest = hashlib.sha256(content).hexdigest() if content is not None else ""
        states[path.relative_to(root).as_posix()] = kind, digest
    return states


def _repository_test_state(
    root: Path,
) -> tuple[bytes, bytes, _PathState, _PathState]:
    status = _git_output(root, "status", "--porcelain=v1", "-z", "--untracked-files=no")
    index = _git_output(root, "ls-files", "-s", "-z")
    tracked_paths = (
        root / record.split(b"\t", 1)[1].decode("utf-8", errors="surrogateescape")
        for record in index.split(b"\0")
        if record
    )
    managed_paths = {
        *(root / relative for relative in _MANAGED_REPOSITORY_PATHS),
        *root.glob(".ai-sdlc/work-items/*/resume-pack.yaml"),
    }
    return (
        status,
        index,
        _path_states(root, tracked_paths),
        _path_states(root, managed_paths),
    )


@pytest.fixture(scope="session", autouse=True)
def repository_state_is_not_mutated_by_tests() -> Generator[None, None, None]:
    root = _find_repository_root(Path(__file__).resolve().parents[1])
    if root is None:
        yield
        return
    before = _repository_test_state(root)
    try:
        yield
    finally:
        try:
            after = _repository_test_state(root)
        except (OSError, RuntimeError) as exc:
            pytest.fail(f"repository state guard failed: {exc}", pytrace=False)
        changes = [
            label
            for label, position in (("git-status", 0), ("git-index", 1))
            if before[position] != after[position]
        ]
        for label, position in (("tracked", 2), ("managed", 3)):
            before_paths, after_paths = before[position], after[position]
            changes.extend(
                f"{label}:{path}"
                for path in sorted(before_paths.keys() | after_paths.keys())
                if before_paths.get(path) != after_paths.get(path)
            )
        if changes:
            pytest.fail(
                "pytest mutated repository-managed state: " + ", ".join(changes),
                pytrace=False,
            )


@pytest.fixture(autouse=True)
def isolated_user_agentops_profile(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Keep tests independent from a developer's user-level enterprise profile."""
    home = tmp_path / ".pytest-home"
    home.mkdir(exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    for key in (
        "AI_SDLC_ENTERPRISE_PROFILE",
        "AGENTOPS_REPORTING_MODE",
        "AGENTOPS_INGESTION_ENDPOINT",
        "AGENTOPS_INGESTION_TOKEN",
        "AGENTOPS_INGESTION_TOKEN_ENV",
        "AGENTOPS_INGESTION_MODE",
        "AGENTOPS_INGESTION_TIMEOUT_SECONDS",
        "AGENTOPS_PRODUCER_ID",
        "AGENTOPS_RUNTIME_ID",
        "AGENTOPS_CREDENTIAL_ID",
        "AGENTOPS_KEY_ID",
    ):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture()
def tmp_project_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary directory simulating an empty project."""
    project = tmp_path / "test-project"
    project.mkdir()
    return project


@pytest.fixture()
def isolated_cli_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture()
def initialized_project_dir(tmp_project_dir: Path) -> Path:
    """Provide a temporary directory with .ai-sdlc/ already created."""
    ai_sdlc = tmp_project_dir / ".ai-sdlc"
    ai_sdlc.mkdir()
    config_dir = ai_sdlc / "project" / "config"
    config_dir.mkdir(parents=True)
    state_file = config_dir / "project-state.yaml"
    state_file.write_text(
        "status: initialized\n"
        "project_name: test-project\n"
        "next_work_item_seq: 1\n"
        "version: '1.0'\n"
    )
    memory_dir = ai_sdlc / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "constitution.md").write_text(
        "# Constitution\n- Principle 1\n- Principle 2\n- Principle 3\n",
        encoding="utf-8",
    )
    profiles_dir = ai_sdlc / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / "tech-stack.yml").write_text(
        "backend:\n  name: python\n  source: https://example.com/python\n",
        encoding="utf-8",
    )
    (profiles_dir / "decisions.yml").write_text(
        "decisions:\n  - id: D1\n    choice: use-python\n",
        encoding="utf-8",
    )
    return tmp_project_dir


@pytest.fixture()
def git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary git repository."""
    repo = tmp_path / "git-repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    # Create initial commit so HEAD exists
    readme = repo / "README.md"
    readme.write_text("# Test Repo\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    yield repo
