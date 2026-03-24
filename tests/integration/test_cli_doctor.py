"""Integration tests for `ai-sdlc doctor`."""

from __future__ import annotations

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


def test_doctor_runs_and_prints_python() -> None:
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python executable" in result.output
    assert "sys.prefix" in result.output
    assert "python -m ai_sdlc" in result.output
