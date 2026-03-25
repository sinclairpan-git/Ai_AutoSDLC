"""Integration tests: ai-sdlc workitem close-check (FR-091 / SC-017)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


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
