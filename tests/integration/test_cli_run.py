"""Integration test for ai-sdlc run CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.runner import SDLCRunner
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.state import Checkpoint, FeatureInfo

runner = CliRunner()

IDE_ENV_KEYS = [
    "CURSOR_TRACE_ID",
    "CURSOR_AGENT",
    "VSCODE_IPC_HOOK_CLI",
    "TERM_PROGRAM",
    "OPENAI_CODEX",
    "CODEX_CLI_READY",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDECODE",
]


@pytest.fixture(autouse=True)
def _clear_ide_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in IDE_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


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

    def test_run_triggers_ide_adapter_after_codex_marker(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / ".codex").mkdir()
        assert runner.invoke(app, ["run", "--dry-run"]).exit_code == 0
        doc = tmp_path / ".codex" / "AI-SDLC.md"
        assert doc.is_file()

    def test_run_non_dry_run_does_not_halt_init_when_git_repo_is_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0

        original_run_gate = SDLCRunner._run_gate

        def gate_wrapper(self: SDLCRunner, stage: str, cp: Checkpoint) -> GateResult:
            if stage == "init":
                return original_run_gate(self, stage, cp)
            return GateResult(
                stage=stage,
                verdict=GateVerdict.PASS,
                checks=[GateCheck(name=f"{stage}_ok", passed=True)],
            )

        monkeypatch.setattr(SDLCRunner, "_run_gate", gate_wrapper)

        result = runner.invoke(app, ["run"])
        assert result.exit_code == 0
        assert "Pipeline completed. Stage: close" in result.output
        assert "Not a git repository" not in result.output

    def test_run_dry_run_guides_user_when_legacy_reconcile_is_needed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
        (tmp_path / "spec.md").write_text(
            "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        (tmp_path / "research.md").write_text("# research\n", encoding="utf-8")
        (tmp_path / "data-model.md").write_text("# data model\n", encoding="utf-8")
        (tmp_path / "plan.md").write_text("# plan\n", encoding="utf-8")
        (tmp_path / "tasks.md").write_text(
            "### Task 1.1 — 示例\n"
            "- **依赖**：无\n"
            "- **验收标准（AC）**：\n"
            "  1. 示例\n",
            encoding="utf-8",
        )
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

        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 1
        assert "recover --reconcile" in result.output

    def test_run_dry_run_continues_after_reconcile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".git").mkdir()
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        (tmp_path / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
        (tmp_path / "spec.md").write_text(
            "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        (tmp_path / "research.md").write_text("# research\n", encoding="utf-8")
        (tmp_path / "data-model.md").write_text("# data model\n", encoding="utf-8")
        (tmp_path / "plan.md").write_text("# plan\n", encoding="utf-8")
        (tmp_path / "tasks.md").write_text(
            "### Task 1.1 — 示例\n"
            "- **依赖**：无\n"
            "- **验收标准（AC）**：\n"
            "  1. 示例\n",
            encoding="utf-8",
        )
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

        assert runner.invoke(app, ["recover", "--reconcile"]).exit_code == 0

        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 0
        assert "Pipeline completed. Stage: verify" in result.output
