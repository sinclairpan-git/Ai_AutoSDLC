"""Unit tests for close-check core logic (FR-091 / SC-017)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from ai_sdlc.core.close_check import run_close_check


def _setup_repo(root: Path, *, tasks_body: str, plan_status: str) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
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
        f"  - id: x\n    content: Work\n    status: {plan_status}\n"
        "---\n\n# P\n",
        encoding="utf-8",
    )

    wi = root / "specs" / "001-wi"
    wi.mkdir(parents=True)
    (wi / "tasks.md").write_text(
        "---\n"
        'related_plan: ".cursor/plans/p.md"\n'
        "---\n\n"
        f"{tasks_body}\n",
        encoding="utf-8",
    )
    (wi / "task-execution-log.md").write_text(
        "# Log\n\n"
        "#### 2.2 统一验证命令\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n",
        encoding="utf-8",
    )

    (root / "README.md").write_text("# R\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)


def test_close_check_blocker_tasks_incomplete(tmp_path: Path) -> None:
    root = tmp_path / "repo1"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n- [ ] pending\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("BLOCKER" in b and "tasks.md" in b for b in r.blockers)


def test_close_check_blocker_related_plan_drift(tmp_path: Path) -> None:
    root = tmp_path / "repo2"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="pending",
    )
    (root / "README.md").write_text("# dirty\n", encoding="utf-8")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("related_plan" in b for b in r.blockers)


def test_close_check_pass_when_all_requirements_met(tmp_path: Path) -> None:
    root = tmp_path / "repo3"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.error is None
    assert r.ok is True
    assert r.blockers == []
