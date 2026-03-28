"""Unit tests for close-check core logic (FR-091 / SC-017)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ai_sdlc.core.close_check import run_close_check
from ai_sdlc.core.workitem_traceability import extract_execution_batches


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


def _write_execution_log(
    wi_dir: Path,
    *,
    git_committed: bool,
    commit_hash: str = "N/A",
    batch_number: int = 1,
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
        f"### Batch 2026-03-28-{batch_number:03d} | Batch {batch_number} demo\n\n"
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
    execution_batch_number: int = 1,
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
        batch_number=execution_batch_number,
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
            batch_number=execution_batch_number,
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


def test_extract_execution_batches_handles_realistic_header_formats() -> None:
    log_text = (
        "### Batch 2026-03-25-001 | Task 6.3–6.5\n"
        "### Batch 2026-03-25-002 | Task 6.1（T10 可移植性审计收口）\n"
    )

    assert extract_execution_batches(log_text) == []


def test_close_check_passes_when_explicit_execution_batch_range_covers_planned_batches(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e1"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## Batch 2：contract models\n"
            "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
            "- **验收标准（AC）**：对象模型可区分 draft / final\n\n"
            "## Batch 3：PRD draft authoring\n"
            "### Task 2.1 — 实现一句话想法 -> draft PRD 生成入口\n"
            "- **验收标准（AC）**：一行想法可以生成 draft PRD\n"
            "## Batch 4：Human Reviewer checkpoints\n"
            "### Task 3.1 — 定义 reviewer decision artifact\n"
            "- **验收标准（AC）**：决策可记录\n\n"
            "## Batch 5：backend delegation / fallback\n"
            "### Task 4.1 — 实现 backend capability declaration\n"
            "- **验收标准（AC）**：capability 可枚举\n"
        ),
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    wi.joinpath("task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-29-001 | 002 Batch 2-5 runtime contract closure\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
        "- 命令：`uv run ruff check src tests`\n"
        "- 命令：`uv run ai-sdlc verify constraints`\n"
        "#### 2.3 任务记录\n"
        "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "#### 2.8 归档后动作\n"
        "- **已完成 git 提交**：是\n"
        "- **提交哈希**：`abc1234`\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: realistic execution headers")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_blocker_when_in_progress_history_is_not_a_reopen_signal(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e2"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## Batch 1：contract models\n"
            "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
            "- **验收标准（AC）**：对象模型可区分 draft / final\n"
        ),
        plan_status="completed",
    )
    exec_log = root / "specs" / "001-wi" / "task-execution-log.md"
    exec_log.write_text(
        "# Log\n\n"
        "### Batch 2026-03-28-001 | 001 Batch 1 demo\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
        "- 命令：`uv run ruff check src tests`\n"
        "- 命令：`uv run ai-sdlc verify constraints`\n"
        "#### 2.3 任务记录\n"
        "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "- 历史状态：this item was previously in_progress while batch 7 was still running\n"
        "#### 2.8 归档后动作\n"
        "- **已完成 git 提交**：是\n"
        "- **提交哈希**：`abc1234`\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: record reopened note")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert all("reopen" not in b.lower() for b in r.blockers)


def test_close_check_passes_for_001_style_history_without_status_correction(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e2b"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## Batch 1：contract models\n"
            "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
            "- **验收标准（AC）**：对象模型可区分 draft / final\n"
        ),
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    wi.joinpath("task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-28-001 | 001 Batch 1 demo\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
        "- 命令：`uv run ruff check src tests`\n"
        "- 命令：`uv run ai-sdlc verify constraints`\n"
        "#### 2.3 任务记录\n"
        "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "- 历史状态：this item was previously in_progress while batch 7 was still running\n"
        "#### 2.8 归档后动作\n"
        "- **已完成 git 提交**：是\n"
        "- **提交哈希**：`abc1234`\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: 001-style historical note")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_passes_when_latest_only_batch_without_status_correction(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e3"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## Batch 1：PRD draft authoring\n"
            "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
            "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
            "## Batch 2：Human Reviewer checkpoints\n"
            "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
            "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n\n"
        ),
        plan_status="completed",
        execution_batch_number=2,
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


def test_close_check_blocker_when_003_status_correction_is_explicit(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e3b"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## 执行状态校正（2026-03-29）\n"
            "- `003` work item 总体状态恢复为 `in_progress`\n\n"
            "## Batch 1：PRD draft authoring\n"
            "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
            "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
            "## Batch 2：Human Reviewer checkpoints\n"
            "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
            "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
        ),
        plan_status="completed",
        execution_batch_number=2,
    )

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is False
    assert any("batch" in b.lower() for b in r.blockers)


def test_close_check_passes_when_generic_archive_headers_do_not_count_as_batches(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo3e4"
    root.mkdir()
    _setup_repo(
        root,
        tasks_body=(
            "## Batch 1：PRD draft authoring\n"
            "### Task 1.1 — 实现一句话想法 -> draft PRD 生成入口\n"
            "- **验收标准（AC）**：一行想法可以生成 draft PRD\n\n"
            "## Batch 2：Human Reviewer checkpoints\n"
            "### Task 2.1 — 把 reviewer checkpoints 接入 PRD freeze / docs baseline freeze / close 前\n"
            "- **验收标准（AC）**：reviewer 决策可被 close-check 读取\n"
        ),
        plan_status="completed",
    )
    wi = root / "specs" / "001-wi"
    wi.joinpath("task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-25-001 | Task 6.3–6.5\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
        "- 命令：`uv run ruff check src tests`\n"
        "- 命令：`uv run ai-sdlc verify constraints`\n"
        "#### 2.3 任务记录\n"
        "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "#### 2.8 归档后动作\n"
        "- **已完成 git 提交**：是\n"
        "- **提交哈希**：`abc1234`\n\n"
        "### Batch 2026-03-25-002 | Task 6.1（T10 可移植性审计收口）\n\n"
        "#### 2.2 统一验证命令\n"
        "- **验证画像**：`code-change`\n"
        "- 命令：`uv run pytest tests/unit/test_close_check.py -q`\n"
        "- 命令：`uv run ruff check src tests`\n"
        "- 命令：`uv run ai-sdlc verify constraints`\n"
        "#### 2.3 任务记录\n"
        "- **改动范围**：`src/example.py`、`tests/test_example.py`\n"
        "#### 2.4 代码审查（`rules/code-review.md` 摘要）\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "#### 2.8 归档后动作\n"
        "- **已完成 git 提交**：是\n"
        "- **提交哈希**：`def5678`\n",
        encoding="utf-8",
    )
    _commit_all(root, "docs: generic headers should not count")

    r = run_close_check(cwd=root, wi=Path("specs/001-wi"))
    assert r.ok is True
    assert r.blockers == []


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
