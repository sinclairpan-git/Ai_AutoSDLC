"""Integration tests for `ai-sdlc scan`."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


def test_scan_reports_results_for_uninitialized_path(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(tmp_path)])

    assert result.exit_code == 0
    assert "Scanning project at" in result.output
    assert "Scan Results" in result.output
    assert "Total Files" in result.output


def test_scan_is_analysis_only_and_skips_ide_adapter_paths_on_initialized_project(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_project(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('hello')\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def _forbid_adapter(*_args, **_kwargs):
        raise AssertionError("scan must not trigger IDE adapter writes")

    with (
        patch(
            "ai_sdlc.cli.main.run_ide_adapter_if_initialized",
            side_effect=_forbid_adapter,
        ),
        patch(
            "ai_sdlc.cli.commands.ensure_ide_adaptation",
            side_effect=_forbid_adapter,
        ),
    ):
        result = runner.invoke(app, ["scan", "."])

    assert result.exit_code == 0
    assert "Scan Results" in result.output
