"""Integration tests: ai-sdlc workitem link + status (FR-088 / SC-013 partial)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
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


class TestWorkitemLinkStatus:
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

    def test_workitem_link_requires_arg(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        init_project(tmp_path)
        _checkpoint(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["workitem", "link"])
        assert result.exit_code == 2

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

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            st = runner.invoke(app, ["status"])
        assert st.exit_code == 0
        assert "Latest Reviewer Decision" in st.output
        assert "prd_freeze:approve -> WI-2026-777" in st.output
