"""Unit tests for plan vs Git drift logic (FR-087)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_sdlc.core.plan_check import (
    PlanCheckResult,
    count_pending_todos,
    git_changed_paths,
    parse_markdown_frontmatter,
    resolve_plan_path_from_wi,
    run_plan_check,
)


def test_count_pending_todos() -> None:
    fm = {
        "todos": [
            {"id": "a", "status": "pending"},
            {"id": "b", "status": "completed"},
            {"id": "c", "status": "pending"},
        ]
    }
    assert count_pending_todos(fm) == 2
    assert count_pending_todos({}) == 0
    assert count_pending_todos({"todos": "bad"}) == 0


def test_parse_markdown_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "x.md"
    p.write_text(
        "---\nfoo: 1\ntodos:\n  - id: a\n    status: pending\n---\nBody\n",
        encoding="utf-8",
    )
    fm, body = parse_markdown_frontmatter(p)
    assert fm.get("foo") == 1
    assert "Body" in body


def test_resolve_plan_path_from_wi(tmp_path: Path) -> None:
    root = tmp_path
    wi = root / "specs/001-wi"
    wi.mkdir(parents=True)
    plan_dir = root / ".cursor" / "plans"
    plan_dir.mkdir(parents=True)
    plan_file = plan_dir / "p.md"
    plan_file.write_text("---\ntodos: []\n---\n")
    (wi / "tasks.md").write_text(
        '---\nrelated_plan: ".cursor/plans/p.md"\n---\n',
        encoding="utf-8",
    )
    got = resolve_plan_path_from_wi(root, wi)
    assert got == plan_file.resolve()


@pytest.fixture()
def git_project_with_plan(tmp_path: Path) -> Path:
    """Git repo with .ai-sdlc, specs WI, and external plan with one pending todo."""
    root = tmp_path / "proj"
    root.mkdir()
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=root,
        check=True,
        capture_output=True,
    )

    ai = root / ".ai-sdlc" / "project" / "config"
    ai.mkdir(parents=True)
    (ai / "project-state.yaml").write_text(
        "status: initialized\nproject_name: p\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )

    plan_dir = root / ".cursor" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "p.md").write_text(
        "---\n"
        "todos:\n"
        "  - id: x\n    content: Work\n    status: pending\n"
        "---\n\n# P\n",
        encoding="utf-8",
    )

    wi = root / "specs" / "001-wi"
    wi.mkdir(parents=True)
    (wi / "tasks.md").write_text(
        '---\nrelated_plan: ".cursor/plans/p.md"\n---\n',
        encoding="utf-8",
    )

    (root / "README.md").write_text("# R\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return root


def test_run_plan_check_drift_pending_and_dirty(git_project_with_plan: Path) -> None:
    (git_project_with_plan / "README.md").write_text("# changed\n", encoding="utf-8")
    r = run_plan_check(
        cwd=git_project_with_plan,
        wi=Path("specs/001-wi"),
        plan=None,
    )
    assert r.error is None
    assert r.drift is True
    assert r.pending_todos == 1
    assert len(r.changed_paths) >= 1


def test_run_plan_check_no_drift_pending_clean_tree(git_project_with_plan: Path) -> None:
    r = run_plan_check(
        cwd=git_project_with_plan,
        wi=Path("specs/001-wi"),
        plan=None,
    )
    assert r.error is None
    assert r.drift is False
    assert r.pending_todos == 1


def test_git_changed_paths_empty_when_not_git(tmp_path: Path) -> None:
    assert git_changed_paths(tmp_path) == []


def test_plan_check_to_json_dict_deduplicates_changed_paths() -> None:
    payload = PlanCheckResult(
        drift=True,
        plan_file=None,
        pending_todos=1,
        changed_paths=["README.md", "README.md"],
    ).to_json_dict()

    assert payload["changed_paths"] == ["README.md"]


def test_plan_check_result_canonicalizes_runtime_changed_paths() -> None:
    result = PlanCheckResult(
        drift=True,
        plan_file=None,
        pending_todos=1,
        changed_paths=["README.md", "README.md"],
    )

    assert result.changed_paths == ["README.md"]
