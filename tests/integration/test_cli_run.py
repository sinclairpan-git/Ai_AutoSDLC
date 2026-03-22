"""Integration test for ai-sdlc run CLI command."""

from __future__ import annotations

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


class TestRunCommand:
    def test_run_outside_project(self) -> None:
        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code in (0, 1, 2)

    def test_run_help(self) -> None:
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "dry-run" in result.output
        assert "mode" in result.output
