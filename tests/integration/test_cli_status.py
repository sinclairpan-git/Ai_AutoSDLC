"""Integration tests for ai-sdlc status CLI command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


class TestCliStatus:
    def test_status_initialized(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0
            assert "AI-SDLC Status" in result.output
            assert tmp_path.name in result.output

    def test_status_not_initialized(self) -> None:
        with patch("ai_sdlc.cli.commands.find_project_root", return_value=None):
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 1
