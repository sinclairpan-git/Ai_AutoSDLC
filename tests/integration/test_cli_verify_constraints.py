"""Integration tests: ai-sdlc verify constraints (FR-089 / SC-012)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def _minimal_constitution(root: Path) -> None:
    mem = root / ".ai-sdlc" / "memory"
    mem.mkdir(parents=True, exist_ok=True)
    (mem / "constitution.md").write_text("# Constitution\n", encoding="utf-8")


class TestCliVerifyConstraints:
    def test_exit_1_missing_constitution(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_1_spec_conflict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        cp = Checkpoint(
            current_stage="init",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/missing-wi",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        )
        save_checkpoint(tmp_path, cp)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "BLOCKER" in result.output

    def test_exit_0_ok(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        spec = tmp_path / "specs" / "001-wi"
        spec.mkdir(parents=True)
        cp = Checkpoint(
            current_stage="init",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001-wi",
                design_branch="d",
                feature_branch="f",
                current_branch="main",
            ),
        )
        save_checkpoint(tmp_path, cp)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 0
        assert "no blocker" in result.output.lower()

    def test_json_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        init_project(tmp_path)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])
        assert result.exit_code == 1
        assert '"ok"' in result.output
        assert "blockers" in result.output
