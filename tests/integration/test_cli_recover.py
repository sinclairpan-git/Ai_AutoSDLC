"""Integration tests for ai-sdlc recover CLI command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


def _write_legacy_root_artifacts(root: Path) -> None:
    (root / ".git").mkdir(exist_ok=True)
    (root / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
    (root / "spec.md").write_text(
        "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
        encoding="utf-8",
    )
    (root / "research.md").write_text("# research\n", encoding="utf-8")
    (root / "data-model.md").write_text("# data model\n", encoding="utf-8")
    (root / "plan.md").write_text("# plan\n", encoding="utf-8")
    (root / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )


class TestCliRecover:
    def test_recover_with_checkpoint(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        cp = Checkpoint(
            current_stage="design",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="d/001",
                feature_branch="f/001",
                current_branch="d/001",
            ),
        )
        save_checkpoint(tmp_path, cp)

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])
            assert result.exit_code == 0
            assert "Recovery" in result.output or "recovered" in result.output.lower()

    def test_recover_no_checkpoint(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])
            assert result.exit_code == 1
            assert "No checkpoint" in result.output

    def test_recover_reconcile_updates_legacy_checkpoint(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        _write_legacy_root_artifacts(tmp_path)
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="unknown",
                    spec_dir="specs/unknown",
                    design_branch="design/unknown",
                    feature_branch="feature/unknown",
                    current_branch="main",
                ),
            ),
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover", "--reconcile"])

        assert result.exit_code == 0
        assert "verify" in result.output.lower()
        assert "spec.md" in result.output

    def test_recover_prompts_and_applies_reconcile_for_legacy_artifacts(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        _write_legacy_root_artifacts(tmp_path)
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="unknown",
                    spec_dir="specs/unknown",
                    design_branch="design/unknown",
                    feature_branch="feature/unknown",
                    current_branch="main",
                ),
            ),
        )

        with (
            patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path),
            patch("ai_sdlc.cli.commands._is_interactive_terminal", return_value=True),
        ):
            result = runner.invoke(app, ["recover"], input="y\n")

        assert result.exit_code == 0
        assert "reconcile" in result.output.lower()
        assert "verify" in result.output.lower()
