"""Integration tests: ai-sdlc workitem close-check (FR-091 / SC-017)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.p1_artifacts import save_reviewer_decision
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
)

runner = CliRunner()


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _write_execution_log(
    wi_dir: Path,
    *,
    git_committed: bool,
    commit_hash: str = "N/A",
    batch_number: int = 1,
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/integration/test_cli_workitem_close_check.py -q",
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


def _write_release_gate_evidence(wi_dir: Path, *, overall_verdict: str = "PASS") -> None:
    checks = [
        {
            "name": "recoverability",
            "verdict": "PASS",
            "evidence_source": "tests/integration/test_cli_recover.py",
            "reason": "resume-pack rebuild and recover flows are covered",
        },
        {
            "name": "portability",
            "verdict": overall_verdict,
            "evidence_source": "tests/integration/test_cli_module_invocation.py",
            "reason": f"portability gate escalated to {overall_verdict}",
        },
        {
            "name": "multi_ide",
            "verdict": "PASS",
            "evidence_source": "tests/integration/test_cli_status.py",
            "reason": "status/adapter surfaces keep IDE-aware behavior bounded",
        },
        {
            "name": "stability",
            "verdict": "PASS",
            "evidence_source": "uv run pytest -q",
            "reason": "focused regression suites are green",
        },
    ]
    if overall_verdict == "PASS":
        checks[1]["reason"] = "module invocation fallback works without PATH assumptions"
    rendered_checks = ",\n".join(
        "      {\n"
        f'        "name": "{check["name"]}",\n'
        f'        "verdict": "{check["verdict"]}",\n'
        f'        "evidence_source": "{check["evidence_source"]}",\n'
        f'        "reason": "{check["reason"]}"\n'
        "      }"
        for check in checks
    )
    (wi_dir / "release-gate-evidence.md").write_text(
        "# 003 release gate evidence\n\n"
        "- release_gate_evidence: present\n"
        "- PASS: supported\n"
        "- WARN: supported\n"
        "- BLOCK: supported\n\n"
        "```json\n"
        "{\n"
        '  "release_gate_evidence": {\n'
        f'    "overall_verdict": "{overall_verdict}",\n'
        '    "checks": [\n'
        f"{rendered_checks}\n"
        "    ]\n"
        "  }\n"
        "}\n"
        "```\n",
        encoding="utf-8",
    )


def _setup_repo(
    root: Path,
    *,
    tasks_body: str,
    plan_status: str,
    wi_rel: str = "specs/001-wi",
    git_committed: bool = True,
    execution_batch_number: int = 1,
    verification_profile: str = "code-change",
    verification_commands: tuple[str, ...] = (
        "uv run pytest tests/integration/test_cli_workitem_close_check.py -q",
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

    wi = root / wi_rel
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
            ["git", "add", f"{wi_rel}/task-execution-log.md"],
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


class TestCliWorkitemCloseCheck:
    def test_exit_1_when_tasks_incomplete(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r1"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n- [ ] pending\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_0_when_all_green(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_git_closeout_not_committed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2b"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            git_committed=False,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "git" in result.output.lower()

    def test_exit_1_when_worktree_dirty_after_git_closeout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2c"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        (root / "README.md").write_text("# dirty\n", encoding="utf-8")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "working tree" in result.output.lower()

    def test_exit_1_when_verification_profile_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            verification_profile="",
            verification_commands=("uv run ai-sdlc verify constraints",),
            changed_paths=("docs/example.md",),
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "verification profile" in result.output.lower()

    def test_exit_0_when_completion_truth_is_not_opted_in_for_001_style_history(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d1"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n\n"
                "## Batch 2：PRD draft authoring\n"
                "### Task 2.1 — 实现一句话想法 -> draft PRD 生成入口\n"
                "- **验收标准（AC）**：一行想法可以生成 draft PRD\n"
            ),
            plan_status="completed",
            execution_batch_number=2,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_explicit_execution_batch_range_covers_planned_batches(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d1b"
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
            "### Batch 2026-03-29-001 | 002 Batch 2-5 runtime contract closure\n\n"
            "#### 2.2 统一验证命令\n"
            "- **验证画像**：`code-change`\n"
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
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
        _commit_all(root, "docs: realistic execution headers")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_generic_archive_headers_do_not_count_as_batches(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d1c"
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
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
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
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
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
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_completion_truth_reopened_status_note(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d2"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body=(
                "## Batch 1：contract models\n"
                "### Task 1.1 — 定义 draft PRD / reviewer / release evidence 的正式对象模型\n"
                "- **验收标准（AC）**：对象模型可区分 draft / final\n"
                "- 状态校正：work item reopened and moved back to in_progress\n"
            ),
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "reopen" in result.output.lower() or "in_progress" in result.output

    def test_exit_0_when_in_progress_history_is_not_a_reopen_signal(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d2b"
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
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
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
        _commit_all(root, "docs: historical in_progress note")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_001_style_history_has_no_status_correction(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d2c"
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
            "- 命令：`uv run pytest tests/integration/test_cli_workitem_close_check.py -q`\n"
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
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_0_when_explicit_batch_coverage_is_missing_without_status_correction(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d3"
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
            execution_batch_number=2,
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_003_status_correction_is_explicit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2d3b"
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
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "batch" in result.output.lower()

    def test_exit_0_for_docs_only_profile_with_minimal_evidence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2e"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            verification_profile="docs-only",
            verification_commands=("uv run ai-sdlc verify constraints",),
            changed_paths=("docs/example.md", "specs/001-wi/tasks.md"),
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_docs_only_profile_missing_verify_constraints(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2f"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
            verification_profile="docs-only",
            verification_commands=("uv run ai-sdlc workitem close-check --wi specs/001-wi",),
            changed_paths=("docs/example.md",),
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "verify constraints" in result.output.lower()

    def test_json_output_has_required_fields(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r3"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            ["workitem", "close-check", "--wi", "specs/001-wi", "--json"],
        )
        assert result.exit_code == 0
        assert '"ok"' in result.output
        assert "blockers" in result.output
        assert "checks" in result.output

    def test_help_mentions_close_stage_and_read_only(self) -> None:
        result = runner.invoke(app, ["workitem", "close-check", "--help"])
        assert result.exit_code == 0
        out = result.output.lower()
        assert "close" in out and "read-only" in out

    def test_exit_1_when_docs_claim_unimplemented_but_command_exists(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r4"
        root.mkdir()
        _setup_repo(
            root,
            tasks_body="- [x] done\n### Task 1.1\n- **验收标准（AC）**：ok",
            plan_status="completed",
        )
        wi = root / "specs" / "001-wi"
        (wi / "drift.md").write_text(
            "未来可能提供：`ai-sdlc verify constraints`。\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_0_when_violation_only_in_unlisted_deep_docs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r5"
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
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", "specs/001-wi"])
        assert result.exit_code == 0

    def test_exit_1_when_deep_docs_violation_with_all_docs_flag(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r6"
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
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "close-check",
                "--wi",
                "specs/001-wi",
                "--all-docs",
            ],
        )
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_help_mentions_all_docs_option(self) -> None:
        result = runner.invoke(app, ["workitem", "close-check", "--help"])
        assert result.exit_code == 0
        assert "--all-docs" in result.output

    def test_exit_1_when_003_pre_close_approval_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r7"
        root.mkdir()
        wi_rel = "specs/003-cross-cutting-authoring-and-extension-contracts"
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
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        _write_release_gate_evidence(wi)
        _commit_all(root, "docs: add 003 release gate evidence")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])
        assert result.exit_code == 1
        assert "pre_close" in result.output

    def test_exit_0_when_003_pre_close_approval_present(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r8"
        root.mkdir()
        wi_rel = "specs/003-cross-cutting-authoring-and-extension-contracts"
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
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        _write_release_gate_evidence(wi)
        save_reviewer_decision(
            root,
            wi.name,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target=wi.name,
                reason="Ready to close",
                next_action="Proceed to archive",
                timestamp="2026-03-29T12:00:00+08:00",
            ),
        )
        _commit_all(root, "docs: add 003 close approval evidence")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])
        assert result.exit_code == 0

    def test_exit_1_when_003_pre_close_revise_denied(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r9"
        root.mkdir()
        wi_rel = "specs/003-cross-cutting-authoring-and-extension-contracts"
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
            wi_rel=wi_rel,
        )
        wi = root / wi_rel
        _write_release_gate_evidence(wi)
        save_reviewer_decision(
            root,
            wi.name,
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
                decision=PrdReviewerDecisionKind.REVISE,
                target=wi.name,
                reason="Please revise final notes",
                next_action="Revise before close",
                timestamp="2026-03-29T12:00:00+08:00",
            ),
        )
        _commit_all(root, "docs: add 003 close revise evidence")
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "close-check", "--wi", wi_rel])
        assert result.exit_code == 1
        assert "revise" in result.output.lower()
