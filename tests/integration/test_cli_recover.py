"""Integration tests for ai-sdlc recover CLI command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.checkpoint import save_checkpoint
from ai_sdlc.models.checkpoint import Checkpoint, FeatureInfo

runner = CliRunner()


class TestCliRecover:
    def test_recover_with_checkpoint(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        cp = Checkpoint(
            current_stage="design",
            feature=FeatureInfo(
                id="001", spec_dir="specs/001",
                design_branch="d/001", feature_branch="f/001",
                current_branch="d/001",
            ),
        )
        save_checkpoint(tmp_path, cp)

        with patch("ai_sdlc.cli.recover_cmd.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])
            assert result.exit_code == 0
            assert "Recovery" in result.output or "recovered" in result.output.lower()

    def test_recover_no_checkpoint(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        with patch("ai_sdlc.cli.recover_cmd.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])
            assert result.exit_code == 1
            assert "No checkpoint" in result.output
