"""Workitem 只读命令不得消费 IDE adapter hook。"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.cli_hooks import run_ide_adapter_if_initialized
from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()

_CASES = (
    ("plan-check-normal", ("plan-check", "--plan", ".cursor/plans/read-only.md")),
    ("plan-check-help", ("plan-check", "--help")),
    ("plan-check-invalid", ("plan-check",)),
    ("guard-normal", ("guard", "--request", "只读探针")),
    ("guard-help", ("guard", "--help")),
    ("guard-invalid", ("guard", "--unknown-option")),
    ("close-check-normal", ("close-check", "--wi", "specs/001-read-only")),
    ("close-check-help", ("close-check", "--help")),
    ("close-check-invalid", ("close-check",)),
    ("branch-check-normal", ("branch-check", "--wi", "specs/001-read-only")),
    ("branch-check-help", ("branch-check", "--help")),
    ("branch-check-invalid", ("branch-check",)),
    ("truth-check-normal", ("truth-check", "--wi", "specs/001-read-only")),
    ("truth-check-help", ("truth-check", "--help")),
    ("truth-check-invalid", ("truth-check",)),
)


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout


def _initialize_read_only_project(root: Path, *, cursor: bool = False) -> None:
    root.mkdir()
    if cursor:
        (root / ".cursor").mkdir()
    init_project(root, agent_target="cursor" if cursor else None)

    plan = root / ".cursor" / "plans" / "read-only.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text("---\ntodos: []\n---\n# Read-only plan\n", encoding="utf-8")
    wi = root / "specs" / "001-read-only"
    wi.mkdir(parents=True)
    for name in ("spec.md", "plan.md", "tasks.md", "task-execution-log.md"):
        (wi / name).write_text(f"# {name}\n", encoding="utf-8")

    _git(root, "init", "--initial-branch=main")
    _git(root, "config", "user.email", "test@test.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "test fixture")


def _tree_snapshot(root: Path) -> tuple[dict[str, bytes], bytes]:
    files = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }
    status = _git(root, "status", "--porcelain=v1", "-uall")
    return files, status


@pytest.mark.parametrize(
    ("case_id", "command"), _CASES, ids=[case[0] for case in _CASES]
)
def test_read_only_workitem_commands_do_not_consume_adapter_hook(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case_id: str,
    command: tuple[str, ...],
) -> None:
    _ = case_id
    root = tmp_path / "repo"
    _initialize_read_only_project(root)
    monkeypatch.chdir(root)
    args = ["workitem", *command]
    before = _tree_snapshot(root)

    monkeypatch.setattr(
        "ai_sdlc.cli.main.run_ide_adapter_if_initialized",
        lambda *, console: None,
    )
    baseline = runner.invoke(app, args)
    assert _tree_snapshot(root) == before

    calls: list[str] = []

    def _sentinel(*, console: object) -> None:
        calls.append("adapter")
        console.print("ADAPTER_SENTINEL_MARKER")  # type: ignore[attr-defined]
        (root / "adapter-sentinel.txt").write_text("consumed\n", encoding="utf-8")

    monkeypatch.setattr("ai_sdlc.cli.main.run_ide_adapter_if_initialized", _sentinel)
    candidate = runner.invoke(app, args)

    assert calls == []
    assert "ADAPTER_SENTINEL_MARKER" not in candidate.output
    assert _tree_snapshot(root) == before
    assert candidate.exit_code == baseline.exit_code
    assert candidate.stdout == baseline.stdout
    assert candidate.stderr == baseline.stderr


@pytest.mark.real_ide_hook
def test_plan_check_real_cursor_hook_matches_no_op_without_writes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline_root = tmp_path / "baseline" / "repo"
    baseline_root.parent.mkdir()
    _initialize_read_only_project(baseline_root, cursor=True)
    canonical_rule = baseline_root / ".cursor" / "rules" / "ai-sdlc.mdc"
    canonical_rule.unlink()
    _git(baseline_root, "add", "-A")
    _git(baseline_root, "commit", "-m", "remove managed rule")

    candidate_root = tmp_path / "candidate" / "repo"
    candidate_root.parent.mkdir()
    shutil.copytree(baseline_root, candidate_root)
    relative_guarded = (
        Path(".cursor/rules/ai-sdlc.mdc"),
        Path(".ai-sdlc/project/config/project-config.yaml"),
    )

    def _guarded(root: Path) -> dict[str, bytes | None]:
        return {
            path.as_posix(): (root / path).read_bytes()
            if (root / path).exists()
            else None
            for path in relative_guarded
        }

    assert _guarded(candidate_root) == _guarded(baseline_root)
    assert _tree_snapshot(candidate_root) == _tree_snapshot(baseline_root)
    baseline_before = (_guarded(baseline_root), _tree_snapshot(baseline_root))
    candidate_before = (_guarded(candidate_root), _tree_snapshot(candidate_root))
    args = ["workitem", "plan-check", "--plan", ".cursor/plans/read-only.md"]

    monkeypatch.chdir(baseline_root)
    monkeypatch.setattr(
        "ai_sdlc.cli.main.run_ide_adapter_if_initialized",
        lambda *, console: None,
    )
    baseline = runner.invoke(app, args)
    assert (_guarded(baseline_root), _tree_snapshot(baseline_root)) == baseline_before

    monkeypatch.chdir(candidate_root)
    monkeypatch.setattr(
        "ai_sdlc.cli.main.run_ide_adapter_if_initialized",
        run_ide_adapter_if_initialized,
    )
    candidate = runner.invoke(app, args)

    assert (
        _guarded(candidate_root),
        _tree_snapshot(candidate_root),
    ) == candidate_before
    assert candidate.exit_code == baseline.exit_code
    assert candidate.stdout == baseline.stdout
    assert candidate.stderr == baseline.stderr
    assert "IDE adapter" not in candidate.output
