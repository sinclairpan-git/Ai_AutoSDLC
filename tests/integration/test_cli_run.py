"""Integration test for ai-sdlc run CLI command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


class TestRunCommand:
    def test_run_outside_project(self, tmp_path: Path) -> None:
        """Not inside a project → exit 1 (not found) or 2 (halt), never success."""
        result = runner.invoke(app, ["run", "--dry-run"], cwd=str(tmp_path))
        assert result.exit_code in (1, 2)

    def test_run_help(self) -> None:
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "dry-run" in result.output
        assert "mode" in result.output
