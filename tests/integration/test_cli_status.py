"""Integration tests for ai-sdlc status CLI command."""

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

    def test_status_guides_user_when_legacy_artifacts_need_reconcile(
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
        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "recover --reconcile" in result.output
        assert "旧版产物" in result.output
