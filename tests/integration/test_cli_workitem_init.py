"""Integration tests: ai-sdlc workitem init (FR-008 / SC-008)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.core.config import load_project_state
from ai_sdlc.core.plan_check import parse_markdown_frontmatter
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


class TestCliWorkitemInit:
    def test_workitem_init_guides_formal_bootstrap_when_state_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        (root / ".ai-sdlc" / "project" / "config").mkdir(parents=True)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
            ],
        )

        assert result.exit_code == 1
        assert "formal bootstrap" in result.output.lower()
        assert "project-state.yaml" in result.output
        assert "ai-sdlc init ." in result.output
        assert not (root / "specs").exists()

    def test_workitem_init_generates_direct_formal_docs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
                "--wi-id",
                "008-direct-formal-entry",
                "--related-plan",
                ".cursor/plans/direct-formal.md",
                "--related-doc",
                "docs/superpowers/specs/direct-formal-design.md",
            ],
        )
        assert result.exit_code == 0
        assert "specs/008-direct-formal-entry" in result.output
        assert "canonical formal docs" in result.output.lower()

        wi_dir = root / "specs" / "008-direct-formal-entry"
        assert (wi_dir / "spec.md").is_file()
        assert (wi_dir / "plan.md").is_file()
        assert (wi_dir / "tasks.md").is_file()
        assert not (root / "docs" / "superpowers" / "plans").exists()

        fm, _ = parse_markdown_frontmatter(wi_dir / "tasks.md")
        assert fm["related_plan"] == ".cursor/plans/direct-formal.md"
        assert fm["related_doc"] == ["docs/superpowers/specs/direct-formal-design.md"]

    def test_workitem_init_auto_generated_id_updates_project_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Branch Lifecycle Truth Guard",
            ],
        )
        assert result.exit_code == 0
        assert "specs/001-branch-lifecycle-truth-guard" in result.output

        state = load_project_state(root)
        assert state.next_work_item_seq == 2

    def test_workitem_init_rejects_duplicate_initialization(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        first = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
                "--wi-id",
                "008-direct-formal-entry",
            ],
        )
        assert first.exit_code == 0

        second = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Direct Formal Entry",
                "--wi-id",
                "008-direct-formal-entry",
            ],
        )
        assert second.exit_code == 1
        assert "already exist" in second.output.lower()

    def test_workitem_init_skips_existing_sequences_when_project_state_lags(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        existing = root / "specs" / "046-existing-formal-baseline"
        existing.mkdir(parents=True)
        (existing / "spec.md").write_text("# existing\n", encoding="utf-8")
        state_path = root / ".ai-sdlc" / "project" / "config" / "project-state.yaml"
        state_path.write_text(
            "status: initialized\n"
            "project_name: demo\n"
            "next_work_item_seq: 20\n"
            "version: '1.0'\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(root)

        result = runner.invoke(
            app,
            [
                "workitem",
                "init",
                "--title",
                "Frontend Program Final Proof Archive Orchestration Baseline",
            ],
        )

        assert result.exit_code == 0
        assert (
            "specs/047-frontend-program-final-proof-archive-orchestration-baseline"
            in result.output
        )
        assert load_project_state(root).next_work_item_seq == 48

    def test_workitem_init_requires_title(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = tmp_path / "repo"
        root.mkdir()
        init_project(root)
        monkeypatch.chdir(root)

        result = runner.invoke(app, ["workitem", "init"])
        assert result.exit_code == 2
