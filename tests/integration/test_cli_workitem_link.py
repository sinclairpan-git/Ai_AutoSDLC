"""Integration tests: ai-sdlc workitem link + status (FR-088 / SC-013 partial)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli import workitem_cmd
from ai_sdlc.cli.main import app
from ai_sdlc.context.state import CHECKPOINT_PATH, save_checkpoint
from ai_sdlc.core.p1_artifacts import save_reviewer_decision
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.models.work import (
    PrdReviewerCheckpoint,
    PrdReviewerDecision,
    PrdReviewerDecisionKind,
)
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _checkpoint(tmp_path: Path) -> None:
    cp = Checkpoint(
        current_stage="init",
        feature=FeatureInfo(
            id="unknown",
            spec_dir="specs/001",
            design_branch="design/x",
            feature_branch="feature/x",
            current_branch="main",
        ),
    )
    save_checkpoint(tmp_path, cp)


def _init_git_repo(root: Path) -> None:
    for args in (
        ("init", "--initial-branch=main"),
        ("config", "user.email", "test@test.com"),
        ("config", "user.name", "Test"),
        ("add", "."),
        ("commit", "-m", "test fixture"),
    ):
        subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )


class TestWorkitemLinkStatus:
    @pytest.mark.parametrize("dirty_tree", [False, True])
    def test_workitem_link_adapter_warning_continues_before_load_and_save(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        dirty_tree: bool,
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        _init_git_repo(tmp_path)
        if dirty_tree:
            (tmp_path / "dirty.txt").write_text("pending\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        order: list[str] = []
        original_load = workitem_cmd.load_checkpoint
        original_save = workitem_cmd.save_checkpoint

        def _adapter(*, console: object) -> None:
            order.append("adapter")
            console.print("adapter warning; continuing")  # type: ignore[attr-defined]

        def _load(root: Path) -> Checkpoint | None:
            order.append("load")
            return original_load(root)

        def _save(root: Path, checkpoint: Checkpoint) -> None:
            order.append("save")
            original_save(root, checkpoint)

        monkeypatch.setattr("ai_sdlc.cli.main.run_ide_adapter_if_initialized", _adapter)
        monkeypatch.setattr(workitem_cmd, "load_checkpoint", _load)
        monkeypatch.setattr(workitem_cmd, "save_checkpoint", _save)

        result = runner.invoke(app, ["workitem", "link", "--wi-id", "001-read-only"])

        assert result.exit_code == 0
        assert order == ["adapter", "load", "save"]
        assert "adapter warning; continuing" in result.output

    def test_workitem_link_adapter_exception_stops_before_handler(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)
        order: list[str] = []

        def _adapter(*, console: object) -> None:
            _ = console
            order.append("adapter")
            raise RuntimeError("adapter failed")

        def _load(_root: Path) -> Checkpoint | None:
            order.append("load")
            return None

        monkeypatch.setattr("ai_sdlc.cli.main.run_ide_adapter_if_initialized", _adapter)
        monkeypatch.setattr(workitem_cmd, "load_checkpoint", _load)

        result = runner.invoke(app, ["workitem", "link", "--wi-id", "001-read-only"])

        assert isinstance(result.exception, RuntimeError)
        assert str(result.exception) == "adapter failed"
        assert order == ["adapter"]

    @pytest.mark.parametrize(
        ("args", "expected_exit"),
        [
            (["workitem", "link", "--help"], 0),
            (["workitem", "link", "--unknown-option"], 2),
        ],
    )
    def test_workitem_link_parser_paths_keep_adapter_before_validation(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        args: list[str],
        expected_exit: int,
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)
        checkpoint = tmp_path / CHECKPOINT_PATH
        checkpoint_before = checkpoint.read_bytes()
        calls: list[str] = []

        def _adapter(*, console: object) -> None:
            _ = console
            calls.append("adapter")

        monkeypatch.setattr("ai_sdlc.cli.main.run_ide_adapter_if_initialized", _adapter)

        result = runner.invoke(app, args)

        assert result.exit_code == expected_exit
        assert calls == ["adapter"]
        assert checkpoint.read_bytes() == checkpoint_before

    def test_workitem_link_updates_checkpoint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "workitem",
                "link",
                "--wi-id",
                "001-ai-sdlc-framework",
                "--plan-uri",
                ".cursor/plans/foo.plan.md",
            ],
        )
        assert result.exit_code == 0
        assert "linked_wi_id" in result.output

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            st = runner.invoke(app, ["status"])
        assert st.exit_code == 0
        assert "Linked WI ID" in st.output
        assert "001-ai-sdlc-framework" in st.output
        assert "Linked plan URI" in st.output
        assert ".cursor/plans/foo.plan.md" in st.output
        assert "Last synced (plan)" in st.output

    def test_workitem_link_requires_arg(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)
        checkpoint = tmp_path / CHECKPOINT_PATH
        checkpoint_before = checkpoint.read_bytes()
        calls: list[str] = []

        def _adapter(*, console: object) -> None:
            _ = console
            calls.append("adapter")

        monkeypatch.setattr("ai_sdlc.cli.main.run_ide_adapter_if_initialized", _adapter)

        result = runner.invoke(app, ["workitem", "link"])
        assert result.exit_code == 2
        assert calls == ["adapter"]
        assert checkpoint.read_bytes() == checkpoint_before

    @pytest.mark.parametrize("initialized", [False, True])
    def test_workitem_link_negative_state_still_runs_adapter_first(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        initialized: bool,
    ) -> None:
        if initialized:
            init_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        order: list[str] = []

        def _adapter(*, console: object) -> None:
            _ = console
            order.append("adapter")

        monkeypatch.setattr("ai_sdlc.cli.main.run_ide_adapter_if_initialized", _adapter)

        result = runner.invoke(app, ["workitem", "link", "--wi-id", "001-read-only"])

        assert result.exit_code == 1
        assert order == ["adapter"]
        expected = (
            "No checkpoint found" if initialized else "Not inside an AI-SDLC project"
        )
        assert expected in result.output

    def test_status_without_links_unchanged(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            st = runner.invoke(app, ["status"])
        assert st.exit_code == 0
        assert "Linked WI ID" not in st.output

    def test_status_shows_latest_reviewer_decision(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "workitem",
                "link",
                "--wi-id",
                "WI-2026-777",
                "--plan-uri",
                ".cursor/plans/foo.plan.md",
            ],
        )
        assert result.exit_code == 0

        save_reviewer_decision(
            tmp_path,
            "WI-2026-777",
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRD_FREEZE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target="WI-2026-777",
                reason="Ready to freeze",
                next_action="Persist final_prd",
                timestamp="2026-03-29T10:00:00+08:00",
            ),
        )
        save_reviewer_decision(
            tmp_path,
            "WI-2026-777",
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.DOCS_BASELINE_FREEZE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target="WI-2026-777",
                reason="Docs baseline is aligned",
                next_action="Persist docs baseline",
                timestamp="2026-03-29T11:00:00+08:00",
            ),
        )
        save_reviewer_decision(
            tmp_path,
            "WI-2026-777",
            PrdReviewerDecision(
                checkpoint=PrdReviewerCheckpoint.PRE_CLOSE,
                decision=PrdReviewerDecisionKind.APPROVE,
                target="WI-2026-777",
                reason="Ready to close",
                next_action="Archive work item",
                timestamp="2026-03-29T12:00:00+08:00",
            ),
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            st = runner.invoke(app, ["status"])
        assert st.exit_code == 0
        assert "Latest Reviewer Decision" in st.output
        assert "pre_close:approve -> WI-2026-777" in st.output
