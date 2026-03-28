"""Unit tests for close-check core logic (FR-091 / SC-017)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_sdlc.core.close_check import run_close_check


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


def _write_execution_log(
    wi_dir: Path,
    *,
    git_committed: bool,
    commit_hash: str = "N/A",
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/unit/test_close_check.py -q",
        "uv run ruff check src tests",
        "uv run ai-sdlc verify constraints",
    ),
    changed_paths: tuple[str, ...] = ("src/example.py", "tests/test_example.py"),
) -> None:
    committed_text = "是" if git_committed else "否"
    rendered_hash = f"`{commit_hash}`" if commit_hash != "N/A" else "N/A"
    command_lines = "".join(f"- 命令：`{command}`\n" for command in verification_commands)
    path_text = "、".join(f"`{path}`" for path in changed_paths)
    (wi_dir / "task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-28-001 | demo\n\n"
        "#### 2.2 统一验证命令\n"
        f"- **验证画像**：`{verification_profile}`\n"
        f"{command_lines}"
        "#### 2.3 任务记录\n"
        f"- **改动范围**：{path_text}\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "#### 2.8 归档后动作\n"
        f"- **已完成 git 提交**：{committed_text}\n"
        f"- **提交哈希**：{rendered_hash}\n",
        encoding="utf-8",
    )


def _setup_repo(
    root: Path,
    *,
    tasks_body: str,
    plan_status: str,
    git_committed: bool = True,
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/unit/test_close_check.py -q",
        "uv run ruff check src tests",
        "uv run ai-sdlc verify constraints",
    ),
    changed_paths: tuple[str, ...] = ("src/example.py", "tests/test_example.py"),
) -> None:
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
    _write_execution_log(
        wi,
        git_committed=False,
        verification_profile=verification_profile,
        verification_commands=verification_commands,
        changed_paths=changed_paths,
    )

    (root / "README.md").write_text("# R\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True, capture_output=True)
    if git_committed:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        _write_execution_log(
            wi,
            git_committed=True,
            commit_hash=head,
            verification_profile=verification_profile,
            verification_commands=verification_commands,
            changed_paths=changed_paths,
        )
        subprocess.run(
            ["git", "add", "specs/001-wi/task-execution-log.md"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "--amend", "--no-edit"],
            cwd=root,
            check=True,
            capture_output=True,
        )


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


def test_close_check_blocker_when_git_closeout_not_committed(tmp_path: Path) -> None:
    root = tmp_path / "repo3b"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        git_committed=False,
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("git close-out" in b for b in r.blockers)


def test_close_check_blocker_when_worktree_dirty_after_git_closeout(tmp_path: Path) -> None:
    root = tmp_path / "repo3c"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    (root / "README.md").write_text("# dirty\n", encoding="utf-8")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("working tree" in b for b in r.blockers)


def test_close_check_blocker_when_latest_batch_missing_verification_profile(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3d"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    _write_execution_log(
        wi,
        git_committed=True,
        commit_hash="abc1234",
        verification_profile="",
        verification_commands=("uv run ai-sdlc verify constraints",),
        changed_paths=("docs/example.md",),
    )
    _commit_all(root, "docs: remove profile marker")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("verification profile" in b for b in r.blockers)


def test_close_check_pass_for_docs_only_profile_with_minimal_evidence(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="docs-only",
        verification_commands=("uv run ai-sdlc verify constraints",),
        changed_paths=("docs/example.md", "specs/001-wi/tasks.md"),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_blocker_when_docs_only_profile_missing_verify_constraints(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3f"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="docs-only",
        verification_commands=("uv run ai-sdlc workitem close-check --wi specs/001-wi",),
        changed_paths=("docs/example.md",),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("verify constraints" in b for b in r.blockers)


def test_close_check_blocker_when_docs_only_profile_masks_code_changes(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3g"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
        verification_profile="docs-only",
        verification_commands=("uv run ai-sdlc verify constraints",),
        changed_paths=("src/example.py", "docs/example.md"),
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("docs-only" in b for b in r.blockers)


def test_close_check_blocker_docs_claim_not_implemented_for_registered_command(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo4"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    (wi / "drift.md").write_text(
        "该能力在未实现前保留：`ai-sdlc workitem plan-check`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("docs consistency" in b for b in r.blockers)


def test_close_check_docs_consistency_pass_after_fix(tmp_path: Path) -> None:
    root = tmp_path / "repo5"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    (wi / "summary.md").write_text(
        "`ai-sdlc verify constraints` 已可使用，见命令帮助。\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add summary")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_default_skips_unlisted_docs_sc021(tmp_path: Path) -> None:
    """FR-096: random docs/** files are not scanned unless --all-docs."""
    root = tmp_path / "repo6"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    deep = root / "docs" / "nested"
    deep.mkdir(parents=True)
    (deep / "bad.md").write_text(
        "未来可能提供：`ai-sdlc verify constraints`。\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: add deep doc")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True


def test_close_check_all_docs_finds_deep_violation_sc021(tmp_path: Path) -> None:
    root = tmp_path / "repo7"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    deep = root / "docs" / "nested"
    deep.mkdir(parents=True)
    (deep / "bad.md").write_text(
        "未来可能提供：`ai-sdlc verify constraints`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"), all_docs=True)
    assert r.ok is False
    assert any("docs consistency" in b for b in r.blockers)


def test_close_check_whitelist_user_guide_scanned(tmp_path: Path) -> None:
    root = tmp_path / "repo8"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    ug = root / "docs" / "USER_GUIDE.zh-CN.md"
    ug.parent.mkdir(parents=True)
    ug.write_text(
        "在未实现前可忽略：`ai-sdlc workitem plan-check`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("docs consistency" in b for b in r.blockers)


def test_close_check_respects_synthetic_command_from_registry_sc023(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """SC-023: command list is not frozen to two literals."""
    monkeypatch.setattr(
        "ai_sdlc.core.close_check._registered_command_strings",
        lambda: ("ai-sdlc synthetic-new-cmd",),
    )
    root = tmp_path / "repo9"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    (wi / "x.md").write_text(
        "未实现前：`ai-sdlc synthetic-new-cmd`。\n",
        encoding="utf-8",
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("synthetic-new-cmd" in b for b in r.blockers)
