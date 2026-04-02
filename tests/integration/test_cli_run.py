"""Integration test for ai-sdlc run CLI command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import load_checkpoint, save_checkpoint
from ai_sdlc.core.config import save_project_config
from ai_sdlc.core.runner import SDLCRunner
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.telemetry.enums import TelemetryMode, TelemetryProfile
from ai_sdlc.telemetry.paths import (
    telemetry_local_root,
    telemetry_manifest_path,
    telemetry_reports_root,
)

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
    @staticmethod
    def _write_pipeline_config(
        root: Path,
        *,
        max_tasks_per_batch: int = 2,
        max_debug_rounds_per_task: int = 3,
        consecutive_failure_limit: int = 2,
    ) -> None:
        cfg = root / ".ai-sdlc" / "config" / "pipeline.yml"
        cfg.parent.mkdir(parents=True, exist_ok=True)
        cfg.write_text(
            (
                "stages:\n"
                "  - id: execute\n"
                "    batch:\n"
                "      strategy: by_phase\n"
                f"      max_tasks_per_batch: {max_tasks_per_batch}\n"
                "      auto_archive: true\n"
                "      auto_commit: true\n"
                "circuit_breaker:\n"
                f"  max_debug_rounds_per_task: {max_debug_rounds_per_task}\n"
                f"  consecutive_failure_limit: {consecutive_failure_limit}\n"
            ),
            encoding="utf-8",
        )

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
        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 1
        assert "adapter activate" in result.output
        doc = tmp_path / ".codex" / "AI-SDLC.md"
        assert doc.is_file()

    def test_run_dry_run_continues_after_adapter_activation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", ".", "--agent-target", "codex"]).exit_code == 0
        assert runner.invoke(app, ["adapter", "activate", "--agent-target", "codex"]).exit_code == 0

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        assert "Pipeline completed." in result.output

    def test_run_dry_run_lazy_inits_telemetry_without_governance_artifacts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0

        result = runner.invoke(app, ["run", "--dry-run"])

        assert result.exit_code == 0
        manifest = json.loads(
            telemetry_manifest_path(tmp_path).read_text(encoding="utf-8")
        )
        assert manifest["version"] == 1
        assert telemetry_reports_root(tmp_path).exists() is False

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

    def test_run_non_dry_run_executes_batches_updates_checkpoint_and_summary(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        self._write_pipeline_config(git_repo)

        spec_dir = git_repo / "specs" / "WI-2026-RUN"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text(
            "### Task 1.1 — setup\n"
            "- **Task ID**: T001\n"
            "- **依赖**：无\n"
            "- **文件**：src/setup.py\n"
            "- **验收标准（AC）**：\n"
            "  1. setup done\n\n"
            "### Task 1.2 — implement\n"
            "- **Task ID**: T002\n"
            "- **依赖**：T001\n"
            "- **文件**：src/app.py\n"
            "- **验收标准（AC）**：\n"
            "  1. app done\n\n"
            "### Task 2.1 — verify\n"
            "- **Task ID**: T003\n"
            "- **依赖**：T002\n"
            "- **文件**：tests/test_app.py\n"
            "- **验收标准（AC）**：\n"
            "  1. verify done\n",
            encoding="utf-8",
        )
        save_checkpoint(
            git_repo,
            Checkpoint(
                current_stage="execute",
                feature=FeatureInfo(
                    id="WI-2026-RUN",
                    spec_dir="specs/WI-2026-RUN",
                    design_branch="design/WI-2026-RUN",
                    feature_branch="feature/WI-2026-RUN",
                    current_branch="main",
                ),
            ),
        )

        result = runner.invoke(app, ["run"])

        assert result.exit_code == 0
        assert "Pipeline completed. Stage: close" in result.output
        assert (spec_dir / "task-execution-log.md").exists()
        assert (spec_dir / "development-summary.md").exists()

        cp = load_checkpoint(git_repo)
        assert cp is not None
        assert cp.execute_progress is not None
        assert cp.execute_progress.total_batches == 2
        assert cp.execute_progress.completed_batches == 2
        assert cp.execute_progress.last_committed_task == "T003"

    def test_run_binds_telemetry_profile_and_mode_from_project_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        assert runner.invoke(app, ["init", "."]).exit_code == 0
        save_project_config(
            tmp_path,
            ProjectConfig(
                telemetry_profile=TelemetryProfile.EXTERNAL_PROJECT,
                telemetry_mode=TelemetryMode.STRICT,
            ),
        )

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

        manifest = json.loads(
            telemetry_manifest_path(tmp_path).read_text(encoding="utf-8")
        )
        goal_session_id = next(iter(manifest["sessions"]))
        workflow_run_id = next(iter(manifest["runs"]))
        run_event = json.loads(
            (
                telemetry_local_root(tmp_path)
                / "sessions"
                / goal_session_id
                / "runs"
                / workflow_run_id
                / "events.ndjson"
            ).read_text(encoding="utf-8").splitlines()[0]
        )

        assert run_event["profile"] == "external_project"
        assert run_event["mode"] == "strict"

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
