"""Integration tests for ai-sdlc recover CLI command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import (
    build_resume_pack,
    load_checkpoint,
    save_checkpoint,
    save_resume_pack,
)
from ai_sdlc.core.config import YamlStore
from ai_sdlc.core.handoff import update_handoff
from ai_sdlc.models.gate import GovernanceItem, GovernanceState
from ai_sdlc.models.state import Checkpoint, ExecuteProgress, FeatureInfo
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


def _write_direct_formal_artifacts(root: Path, work_item_id: str) -> Path:
    spec_dir = root / "specs" / work_item_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
        encoding="utf-8",
    )
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )
    (spec_dir / "task-execution-log.md").write_text("# Execution Log\n", encoding="utf-8")
    (spec_dir / "development-summary.md").write_text("# Development Summary\n", encoding="utf-8")
    return spec_dir


class TestCliRecover:
    def test_recover_surfaces_continuity_handoff_next_steps(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        spec_dir = tmp_path / "specs" / "182-continuity"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="execute",
                feature=FeatureInfo(
                    id="182-continuity",
                    spec_dir="specs/182-continuity",
                    design_branch="design/182-continuity",
                    feature_branch="feature/182-continuity",
                    current_branch="feature/182-continuity",
                ),
            ),
        )
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)
        update_handoff(
            tmp_path,
            goal="Expose handoff in recover",
            state="Recover should show the fast resume file",
            next_steps=["Continue with handoff CLI implementation"],
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 0
        assert "Continuity Handoff" in result.output
        assert "ready" in result.output.lower()
        assert "Continue with handoff CLI implementation" in result.output

    def test_recover_with_resume_pack(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
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
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])
            assert result.exit_code == 0
            assert "Recovery" in result.output or "recovered" in result.output.lower()

    def test_recover_missing_resume_pack(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="design",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001",
                    design_branch="d/001",
                    feature_branch="f/001",
                    current_branch="d/001",
                ),
            ),
        )
        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])
            assert result.exit_code == 0
            assert "rebuilding from checkpoint" in result.output.lower()
            assert "rebuilt successfully" in result.output.lower()
            assert "continuing" in result.output.lower()

    def test_recover_corrupted_resume_pack(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc" / "state").mkdir(parents=True)
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="design",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/001",
                    design_branch="d/001",
                    feature_branch="f/001",
                    current_branch="d/001",
                ),
            ),
        )
        (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").write_text(
            ": invalid yaml {{",
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 0
        assert "rebuilding from checkpoint" in result.output.lower()
        assert "rebuilt successfully" in result.output.lower()

    def test_recover_stale_resume_pack_rebuilds_and_uses_latest_batch(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / ".ai-sdlc").mkdir()
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        checkpoint = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="001",
                spec_dir="specs/001",
                design_branch="d/001",
                feature_branch="f/001",
                current_branch="f/001",
            ),
            execute_progress=ExecuteProgress(
                current_batch=1,
                total_batches=5,
                last_committed_task="T001",
            ),
        )
        save_checkpoint(tmp_path, checkpoint)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)

        checkpoint.execute_progress = ExecuteProgress(
            current_batch=4,
            total_batches=5,
            last_committed_task="T004",
        )
        save_checkpoint(tmp_path, checkpoint)

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 0
        assert "stale" in result.output.lower()
        assert "rebuilding from checkpoint" in result.output.lower()
        assert "rebuilt successfully" in result.output.lower()
        assert "Current Batch" in result.output
        assert "4" in result.output
        assert "T004" in result.output

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
        assert (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").exists()

    def test_recover_reconcile_realigns_stale_checkpoint_to_current_branch_work_item(
        self,
        tmp_path: Path,
    ) -> None:
        work_item_id = (
            "158-agent-adapter-verified-host-ingress-closure-audit-reconciliation-baseline"
        )
        init_project(tmp_path)
        _write_legacy_root_artifacts(tmp_path)
        _write_direct_formal_artifacts(tmp_path, work_item_id)
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                feature=FeatureInfo(
                    id="001-ai-sdlc-framework",
                    spec_dir="specs/001-ai-sdlc-framework",
                    design_branch="design/001-ai-sdlc-framework-docs",
                    feature_branch="feature/001-ai-sdlc-framework-dev",
                    current_branch="main",
                ),
            ),
        )

        with (
            patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path),
            patch(
                "ai_sdlc.core.reconcile.GitClient.current_branch",
                return_value="codex/158-agent-adapter-ingress-audit",
            ),
        ):
            result = runner.invoke(app, ["recover", "--reconcile"])

        checkpoint = load_checkpoint(tmp_path)

        assert result.exit_code == 0
        assert checkpoint is not None
        assert checkpoint.current_stage == "close"
        assert checkpoint.feature.id == work_item_id
        assert checkpoint.feature.spec_dir == f"specs/{work_item_id}"
        assert checkpoint.feature.current_branch == "codex/158-agent-adapter-ingress-audit"
        assert checkpoint.feature.design_branch == f"design/{work_item_id}-docs"
        assert checkpoint.feature.feature_branch == f"feature/{work_item_id}-dev"
        assert "close" in result.output.lower()
        assert "Reconciled Spec Dir" in result.output
        assert (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").exists()
        assert (
            tmp_path / ".ai-sdlc" / "work-items" / work_item_id / "resume-pack.yaml"
        ).exists()

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
        assert (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").exists()

    def test_recover_stops_until_reconcile_is_applied_for_legacy_artifacts(
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
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 1
        assert "recover --reconcile" in result.output
        assert "Pipeline state recovered successfully" not in result.output
        assert "Resume Stage" not in result.output

    def test_recover_invalid_checkpoint_fails(self, tmp_path: Path) -> None:
        (tmp_path / ".ai-sdlc" / "state").mkdir(parents=True)
        (tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml").write_text(
            "current_stage: bogus\n"
            "feature:\n"
            "  id: '001'\n"
            "  spec_dir: specs/001\n"
            "  design_branch: design/001\n"
            "  feature_branch: feature/001\n"
            "  current_branch: main\n",
            encoding="utf-8",
        )
        (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").write_text(
            "current_stage: design\n"
            "current_batch: 0\n"
            "last_committed_task: ''\n"
            "working_set_snapshot: {}\n"
            "timestamp: '2026-01-01T00:00:00+00:00'\n",
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 1
        assert "checkpoint" in result.output.lower()

    def test_recover_rebuilds_legacy_resume_pack_from_legacy_checkpoint(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        spec_dir = tmp_path / "specs" / "WI-2026-LEGACY"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        checkpoint_path = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(
            """
pipeline:
  started_at: '2026-01-01T00:00:00+00:00'
  last_updated: '2026-01-01T00:05:00+00:00'
current_stage: execute
feature:
  id: 'WI-2026-LEGACY'
  spec_dir: specs/WI-2026-LEGACY
  design_branch: feature/WI-2026-LEGACY-docs
  feature_branch: feature/WI-2026-LEGACY-dev
  current_branch: feature/WI-2026-LEGACY-dev
""".strip(),
            encoding="utf-8",
        )
        (tmp_path / ".ai-sdlc" / "state" / "resume-pack.yaml").write_text(
            """
current_stage: execute
current_batch: 0
last_committed_task: ''
working_set_snapshot: {}
timestamp: '2026-01-01T00:06:00+00:00'
checkpoint_path: .ai-sdlc/state/checkpoint.yml
""".strip(),
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 0
        assert "rebuilding from checkpoint" in result.output.lower()
        assert "rebuilt successfully" in result.output.lower()
        assert "Resume Stage" in result.output
        assert "WI-2026-LEGACY" in result.output

    def test_recover_displays_branch_binding_and_governance(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        spec_dir = tmp_path / "specs" / "WI-2026-001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks\n", encoding="utf-8")

        checkpoint = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="WI-2026-001",
                spec_dir="specs/WI-2026-001",
                design_branch="feature/WI-2026-001-docs",
                feature_branch="feature/WI-2026-001-dev",
                current_branch="feature/WI-2026-001-dev",
                docs_baseline_ref="feature/WI-2026-001-docs",
                docs_baseline_at="2026-03-28T12:00:00+00:00",
            ),
        )
        save_checkpoint(tmp_path, checkpoint)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)

        gov_path = (
            tmp_path
            / ".ai-sdlc"
            / "work-items"
            / "WI-2026-001"
            / "governance.yaml"
        )
        state = GovernanceState(frozen=True, frozen_at="2026-03-28T11:00:00+00:00")
        state.items["constitution"] = GovernanceItem(
            exists=True,
            path=str(tmp_path / ".ai-sdlc" / "memory" / "constitution.md"),
            verified_at="2026-03-28T11:00:00+00:00",
        )
        YamlStore.save(gov_path, state)

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["recover"])

        assert result.exit_code == 0
        assert "Current Branch" in result.output
        assert "feature/WI-2026-001-dev" in result.output
        assert "Docs Baseline" in result.output
        assert "feature/WI-2026-001-docs" in result.output
        assert "Governance Frozen" in result.output
