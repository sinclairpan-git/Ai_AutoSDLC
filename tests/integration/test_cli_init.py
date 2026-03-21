"""Integration tests for ai-sdlc init CLI command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


class TestCliInit:
    def test_init_empty_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / ".ai-sdlc").is_dir()
        assert "Initialized" in result.output

    def test_init_already_initialized(self, initialized_project_dir: Path) -> None:
        result = runner.invoke(app, ["init", str(initialized_project_dir)])
        assert result.exit_code == 0
        assert "already initialized" in result.output

    def test_init_nonexistent_dir(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path / "nope")])
        assert result.exit_code == 2

    def test_init_default_project_name(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert tmp_path.name in result.output
