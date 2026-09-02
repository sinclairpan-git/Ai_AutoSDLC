"""Integration tests: ai-sdlc workitem plan-check (FR-087 / SC-011)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.plan_check import PlanCheckResult

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    """Avoid IDE adapter writing files into the temp git repo (would dirty status)."""
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _setup_git_ai_sdlc(root: Path) -> None:
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


def _write_command_plan(root: Path, body: str) -> Path:
    plan = root / "implementation-plan.md"
    plan.write_text(body, encoding="utf-8")
    return plan


def _command_project(tmp_path: Path, name: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / name
    root.mkdir()
    _setup_git_ai_sdlc(root)
    monkeypatch.chdir(root)
    return root


class TestCliWorkitemPlanCheck:
    def test_plan_check_exit_1_drift_sc011(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r"
        root.mkdir()
        _setup_git_ai_sdlc(root)
        (root / "README.md").write_text("# dirty\n", encoding="utf-8")

        monkeypatch.chdir(root)
        result = runner.invoke(
            app,
            ["workitem", "plan-check", "--wi", "specs/001-wi"],
        )
        assert result.exit_code == 1
        assert "Drift" in result.output or "YES" in result.output

    def test_plan_check_exit_0_clean(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r2"
        root.mkdir()
        _setup_git_ai_sdlc(root)

        monkeypatch.chdir(root)
        result = runner.invoke(
            app,
            ["workitem", "plan-check", "--wi", "specs/001-wi"],
        )
        assert result.exit_code == 0

    def test_plan_check_json_drift(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r3"
        root.mkdir()
        _setup_git_ai_sdlc(root)
        (root / "README.md").write_text("# dirty\n", encoding="utf-8")

        monkeypatch.chdir(root)
        result = runner.invoke(
            app,
            [
                "workitem",
                "plan-check",
                "--wi",
                "specs/001-wi",
                "--json",
            ],
        )
        assert result.exit_code == 1
        assert '"drift": true' in result.output

    def test_plan_check_explicit_plan(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r4"
        root.mkdir()
        _setup_git_ai_sdlc(root)
        (root / "README.md").write_text("# dirty\n", encoding="utf-8")

        monkeypatch.chdir(root)
        result = runner.invoke(
            app,
            ["workitem", "plan-check", "--plan", ".cursor/plans/p.md"],
        )
        assert result.exit_code == 1

    def test_plan_check_both_flags_exit_2(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r5"
        root.mkdir()
        _setup_git_ai_sdlc(root)

        monkeypatch.chdir(root)
        result = runner.invoke(
            app,
            [
                "workitem",
                "plan-check",
                "--wi",
                "specs/001-wi",
                "--plan",
                ".cursor/plans/p.md",
            ],
        )
        assert result.exit_code == 2

    def test_help_mentions_read_only(self) -> None:
        result = runner.invoke(app, ["workitem", "plan-check", "--help"])
        assert result.exit_code == 0
        out = result.output.lower()
        assert "read-only" in out and "checkpoint" in out

    def test_plan_check_deduplicates_changed_paths_display(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "r6"
        root.mkdir()
        monkeypatch.chdir(root)

        with patch(
            "ai_sdlc.cli.workitem_cmd.run_plan_check",
            return_value=PlanCheckResult(
                drift=True,
                plan_file=root / ".cursor" / "plans" / "p.md",
                pending_todos=1,
                changed_paths=[
                    "README.md",
                    "README.md",
                    "src/example.py",
                ],
            ),
        ):
            result = runner.invoke(
                app,
                ["workitem", "plan-check", "--wi", "specs/001-wi"],
            )

        assert result.exit_code == 1
        assert result.output.count("README.md") == 1
        assert result.output.count("src/example.py") == 1

    def test_plan_check_command_surface_requires_explicit_plan_exit_2(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _command_project(tmp_path, "requires-plan", monkeypatch)
        results = [
            runner.invoke(app, ["workitem", "plan-check", "--check-ai-sdlc-commands"]),
            runner.invoke(app, ["workitem", "plan-check", "--wi", "specs/001-wi", "--check-ai-sdlc-commands"]),
        ]
        assert [result.exit_code for result in results] == [2, 2]
        assert all("requires --plan" in result.output for result in results)

    def test_plan_check_command_surface_invalid_command_exit_1_with_line(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _command_project(tmp_path, "invalid-command", monkeypatch)
        plan = _write_command_plan(root, "`ai-sdlc workitem plan-check --wi`\n")
        result = runner.invoke(app, ["workitem", "plan-check", "--plan", str(plan), "--check-ai-sdlc-commands"])

        assert result.exit_code == 1
        assert "line 1:" in result.output
        assert "missing value: --wi" in result.output

    def test_plan_check_command_surface_success_text_and_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _command_project(tmp_path, "valid-commands", monkeypatch)
        plan = _write_command_plan(
            root,
            "`ai-sdlc program truth audit`\n"
            "`uv run ai-sdlc workitem plan-check --plan implementation-plan.md`\n"
            "`python -m ai_sdlc program truth sync --execute --yes`\n",
        )
        args = ["workitem", "plan-check", "--plan", str(plan), "--check-ai-sdlc-commands"]
        text = runner.invoke(app, args)
        as_json = runner.invoke(app, [*args, "--json"])

        assert text.exit_code == 0, text.output
        assert "Checked AI-SDLC commands" in text.output
        assert "Command surface valid" in text.output
        assert as_json.exit_code == 0, as_json.output
        payload = json.loads(as_json.output)
        assert payload["plan_file"] == str(plan.resolve())
        assert payload["checked_command_count"] == 3
        assert payload["command_surface_valid"] is True

    def test_plan_check_command_surface_does_not_execute_program_truth_sync(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = _command_project(tmp_path, "no-execution", monkeypatch)
        sentinel = root / "sentinel.txt"
        sentinel.write_text("unchanged\n", encoding="utf-8")
        program_truth = root / "program-manifest.yaml"
        program_truth.write_text('schema_version: "2"\nprogram:\n  goal: "No execution"\n', encoding="utf-8")
        plan = _write_command_plan(root, "`ai-sdlc program truth sync --execute --yes`\n")
        status_before = subprocess.run(["git", "status", "--porcelain"], cwd=root, check=True, capture_output=True, text=True).stdout
        truth_before = program_truth.read_bytes()
        result = runner.invoke(app, ["workitem", "plan-check", "--plan", str(plan), "--check-ai-sdlc-commands"])
        status_after = subprocess.run(["git", "status", "--porcelain"], cwd=root, check=True, capture_output=True, text=True).stdout
        assert result.exit_code == 0, result.output
        assert sentinel.read_text(encoding="utf-8") == "unchanged\n"
        assert program_truth.read_bytes() == truth_before
        assert status_after == status_before

    def test_plan_check_legacy_text_json_and_exit_contract_unchanged(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _command_project(tmp_path, "legacy-contract", monkeypatch)

        text = runner.invoke(app, ["workitem", "plan-check", "--wi", "specs/001-wi"])
        as_json = runner.invoke(app, ["workitem", "plan-check", "--plan", ".cursor/plans/p.md", "--json"])

        assert text.exit_code == 0, text.output
        assert "Checked AI-SDLC commands" not in text.output
        assert as_json.exit_code == 0, as_json.output
        payload = json.loads(as_json.output)
        assert set(payload) == {"drift", "plan_file", "pending_todos", "changed_paths", "error"}
