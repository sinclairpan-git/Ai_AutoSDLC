"""Integration tests for ai-sdlc status CLI command."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import (
    build_resume_pack,
    load_resume_pack,
    save_checkpoint,
    save_resume_pack,
)
from ai_sdlc.core.config import YamlStore, save_project_state
from ai_sdlc.core.p1_artifacts import (
    save_execution_path,
    save_parallel_coordination_artifact,
    save_resume_point,
)
from ai_sdlc.integrations.ide_adapter import acknowledge_adapter
from ai_sdlc.models.gate import GovernanceItem, GovernanceState
from ai_sdlc.models.project import ProjectState, ProjectStatus
from ai_sdlc.models.state import (
    Checkpoint,
    ExecuteProgress,
    ExecutionBatch,
    ExecutionPlan,
    FeatureInfo,
    MergeSimulation,
    OverlapResult,
    RuntimeState,
    Task,
    TaskStatus,
    WorkerAssignment,
    WorkingSet,
)
from ai_sdlc.models.work import ExecutionPath, ExecutionPathStep, ResumePoint
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry.contracts import Artifact, TelemetryEvent, Violation
from ai_sdlc.telemetry.enums import ArtifactRole, ArtifactType, ScopeLevel, TraceLayer
from ai_sdlc.telemetry.paths import telemetry_indexes_root, telemetry_local_root
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter

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


def _write_specs_dir_legacy_artifacts(root: Path, work_item_id: str = "LEGACY-001") -> None:
    (root / ".git").mkdir(exist_ok=True)
    (root / "product-requirements.md").write_text("# PRD\n", encoding="utf-8")
    spec_dir = root / "specs" / work_item_id
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "### 用户故事 1\n场景\n\n- **FR-001**: requirement\n",
        encoding="utf-8",
    )
    (spec_dir / "research.md").write_text("# research\n", encoding="utf-8")
    (spec_dir / "data-model.md").write_text("# data model\n", encoding="utf-8")
    (spec_dir / "plan.md").write_text("# plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=root,
        check=True,
        capture_output=True,
    )


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True, capture_output=True)


def _create_branch_ahead_of_main(root: Path, branch_name: str) -> None:
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=root,
        check=True,
        capture_output=True,
    )
    (root / "scratch.txt").write_text(f"{branch_name}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: {branch_name}"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "checkout", "main"], cwd=root, check=True, capture_output=True)


def _write_branch_lifecycle_fixture(
    root: Path,
    *,
    wi_name: str = "001-wi",
    branch_disposition_status: str = "待最终收口",
) -> None:
    _init_git_repo(root)
    init_project(root)
    wi_dir = root / "specs" / wi_name
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "tasks.md").write_text(
        "### Task 1.1 — 示例\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. 示例\n",
        encoding="utf-8",
    )
    (wi_dir / "task-execution-log.md").write_text(
        "# Log\n\n"
        "### Batch 2026-03-31-001 | Batch 1 demo\n\n"
        "#### 2.5 任务/计划同步状态（Mandatory）\n"
        "- 关联 branch/worktree disposition 计划：`待最终收口`\n"
        "#### 2.8 归档后动作\n"
        f"- 当前批次 branch disposition 状态：`{branch_disposition_status}`\n"
        "- 当前批次 worktree disposition 状态：`待最终收口`\n",
        encoding="utf-8",
    )
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="verify",
            feature=FeatureInfo(
                id=wi_name.split("-", 1)[0],
                spec_dir=f"specs/{wi_name}",
                design_branch=f"design/{wi_name}",
                feature_branch=f"feature/{wi_name}",
                current_branch="main",
            ),
        ),
    )
    _commit_all(root, "docs: seed branch lifecycle status fixture")


class TestCliStatus:
    @pytest.fixture(autouse=True)
    def _no_ide_adapter_hook(self) -> None:
        with patch("ai_sdlc.cli.commands.ensure_ide_adaptation"):
            yield

    def test_status_initialized(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])
            assert result.exit_code == 0
            assert "AI-SDLC Status" in result.output
            assert tmp_path.name in result.output

    def test_status_displays_adapter_target_and_activation_truth(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path, agent_target="codex")
        acknowledge_adapter(tmp_path, agent_target="codex")

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Agent Target" in result.output
        assert "codex" in result.output
        assert "acknowledged" in result.output

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

    def test_status_guides_user_when_blank_checkpoint_needs_reconcile(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        _write_legacy_root_artifacts(tmp_path)
        checkpoint_path = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text("", encoding="utf-8")

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "recover --reconcile" in result.output
        assert "旧版产物" in result.output
        assert "Invalid checkpoint" not in result.output
        assert "trying backup" not in result.output

    def test_status_json_reports_not_initialized_when_telemetry_is_absent(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        telemetry_root = telemetry_local_root(tmp_path)
        assert telemetry_root.exists() is False

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["telemetry"]["state"] == "not_initialized"
        assert payload["telemetry"]["current"] is None
        assert payload["telemetry"]["latest"] is None
        assert telemetry_root.exists() is False

    def test_status_shows_reconciled_specs_dir_after_recover(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        _write_specs_dir_legacy_artifacts(tmp_path, "LEGACY-001")

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            recover_result = runner.invoke(app, ["recover", "--reconcile"])
            status_result = runner.invoke(app, ["status"])

        assert recover_result.exit_code == 0
        assert status_result.exit_code == 0
        assert "Pipeline Stage" in status_result.output
        assert "verify" in status_result.output
        assert "Feature ID" in status_result.output
        assert "LEGACY-001" in status_result.output
        assert "unknown" not in status_result.output

    def test_status_json_returns_bounded_latest_and_current_summary(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        local_root = telemetry_local_root(tmp_path)
        local_root.mkdir(parents=True, exist_ok=True)
        manifest_path = local_root / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessions": {
                        "gs_01": {"path": "sessions/gs_01"},
                        "gs_02": {"path": "sessions/gs_02"},
                    },
                    "runs": {
                        "wr_01": {"goal_session_id": "gs_01", "path": "sessions/gs_01/runs/wr_01"},
                        "wr_02": {"goal_session_id": "gs_02", "path": "sessions/gs_02/runs/wr_02"},
                    },
                    "steps": {
                        "st_01": {
                            "goal_session_id": "gs_01",
                            "workflow_run_id": "wr_01",
                            "path": "sessions/gs_01/runs/wr_01/steps/st_01",
                        },
                        "st_02": {
                            "goal_session_id": "gs_02",
                            "workflow_run_id": "wr_02",
                            "path": "sessions/gs_02/runs/wr_02/steps/st_02",
                        },
                    },
                }
            ),
            encoding="utf-8",
        )
        indexes_root = telemetry_indexes_root(tmp_path)
        indexes_root.mkdir(parents=True, exist_ok=True)
        (indexes_root / "latest-artifacts.json").write_text(
            json.dumps(
                {
                    "artifact_ids": ["art_01", "art_02", "art_03", "art_04", "art_05"],
                }
            ),
            encoding="utf-8",
        )
        (indexes_root / "open-violations.json").write_text(
            json.dumps(
                {
                    "violation_ids": ["vio_01", "vio_02", "vio_03", "vio_04"],
                }
            ),
            encoding="utf-8",
        )
        (indexes_root / "timeline-cursor.json").write_text(
            json.dumps(
                {
                    "event_count": 9,
                    "last_event_id": "evt_02",
                    "last_timestamp": "2026-03-27T09:00:00Z",
                    "latest_goal_session_id": "gs_02",
                    "latest_workflow_run_id": "wr_02",
                    "latest_step_id": "st_02",
                }
            ),
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert set(payload) == {"telemetry", "branch_lifecycle"}
        telemetry = payload["telemetry"]
        assert telemetry["state"] == "ready"
        assert telemetry["current"] == {
            "manifest_version": 1,
            "sessions": {"count": 2, "latest_goal_session_id": "gs_02"},
            "runs": {"count": 2, "latest_workflow_run_id": "wr_02"},
            "steps": {"count": 2, "latest_step_id": "st_02"},
        }
        assert telemetry["latest"]["artifacts"] == {
            "count": 5,
            "sample_ids": ["art_01", "art_02", "art_03"],
        }
        assert telemetry["latest"]["open_violations"] == {
            "count": 4,
            "sample_ids": ["vio_02", "vio_03", "vio_04"],
        }
        assert telemetry["latest"]["timeline_cursor"] == {
            "event_count": 9,
            "last_event_id": "evt_02",
            "last_timestamp": "2026-03-27T09:00:00Z",
        }
        assert payload["branch_lifecycle"]["state"] == "unavailable"

    def test_status_shows_p1_artifact_surfaces(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        work_item_id = "WI-2026-P1-STATUS"
        spec_dir = tmp_path / "specs" / work_item_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        (spec_dir / "development-summary.md").write_text("# Summary\n", encoding="utf-8")
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="close",
                linked_wi_id=work_item_id,
                feature=FeatureInfo(
                    id=work_item_id,
                    spec_dir=f"specs/{work_item_id}",
                    design_branch=f"design/{work_item_id}",
                    feature_branch=f"feature/{work_item_id}",
                    current_branch=f"feature/{work_item_id}",
                ),
            ),
        )
        save_resume_point(
            tmp_path,
            work_item_id,
            ResumePoint(
                stage="execute",
                batch=4,
                status="suspended",
                current_branch=f"feature/{work_item_id}",
            ),
        )
        save_execution_path(
            tmp_path,
            work_item_id,
            ExecutionPath(
                steps=[
                    ExecutionPathStep(task_id=f"{work_item_id}-MT-1", title="Assess"),
                    ExecutionPathStep(task_id=f"{work_item_id}-MT-2", title="Execute"),
                ]
            ),
        )
        save_parallel_coordination_artifact(
            tmp_path,
            work_item_id,
            assignments=[
                WorkerAssignment(
                    worker_id="worker-1",
                    worker_index=1,
                    parallel_group="group-0",
                    group_id="group-0",
                    branch_name=f"feature/{work_item_id}-worker-1",
                    task_ids=["T1"],
                    allowed_paths=["src/a.py"],
                    forbidden_paths=["src/b.py"],
                )
            ],
            overlap_result=OverlapResult(
                has_overlap=False,
                has_conflicts=False,
            ),
            merge_simulation=MergeSimulation(
                success=True,
                merge_order=[f"feature/{work_item_id}-worker-1"],
                predicted_conflicts=[],
            ),
            group_task_ids={"group-0": ["T1"]},
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Resume Point" in result.output
        assert "execute / batch 4" in result.output
        assert "Execution Path" in result.output
        assert f"{work_item_id}-MT-1" in result.output
        assert "Parallel Coordination" in result.output
        assert "1 workers" in result.output

    def test_status_displays_governance_and_docs_baseline_binding(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        spec_dir = tmp_path / "specs" / "WI-2026-001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks\n", encoding="utf-8")

        save_checkpoint(
            tmp_path,
            Checkpoint(
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
            ),
        )

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
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Current Branch" in result.output
        assert "feature/WI-2026-001-dev" in result.output
        assert "Docs Baseline" in result.output
        assert "feature/WI-2026-001-docs" in result.output
        assert "Governance Frozen" in result.output
        assert "yes" in result.output.lower()

    def test_status_reads_formal_execute_artifacts(self, tmp_path: Path) -> None:
        init_project(tmp_path)
        spec_dir = tmp_path / "specs" / "WI-2026-ART"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks\n", encoding="utf-8")

        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="execute",
                feature=FeatureInfo(
                    id="WI-2026-ART",
                    spec_dir="specs/WI-2026-ART",
                    design_branch="feature/WI-2026-ART-docs",
                    feature_branch="feature/WI-2026-ART-dev",
                    current_branch="feature/WI-2026-ART-dev",
                ),
            ),
        )

        wi_dir = tmp_path / ".ai-sdlc" / "work-items" / "WI-2026-ART"
        YamlStore.save(
            wi_dir / "execution-plan.yaml",
            ExecutionPlan(
                total_tasks=2,
                total_batches=1,
                tasks=[
                    Task(task_id="T001", title="one", phase=1, status=TaskStatus.COMPLETED),
                    Task(task_id="T002", title="two", phase=1, status=TaskStatus.PENDING),
                ],
                batches=[ExecutionBatch(batch_id=1, phase=1, tasks=["T001", "T002"])],
            ),
        )
        YamlStore.save(
            wi_dir / "runtime.yaml",
            RuntimeState(
                current_stage="execute",
                current_batch=1,
                current_task="T002",
                last_committed_task="T001",
                current_branch="feature/WI-2026-ART-dev",
                execution_mode="confirm",
                last_updated="2026-03-28T12:00:00+00:00",
            ),
        )
        YamlStore.save(
            wi_dir / "working-set.yaml",
            WorkingSet(
                spec_path="specs/WI-2026-ART/spec.md",
                plan_path="specs/WI-2026-ART/plan.md",
                tasks_path="specs/WI-2026-ART/tasks.md",
                active_files=["src/app.py"],
            ),
        )
        (wi_dir / "latest-summary.md").write_text(
            "# Latest Summary\n\nCurrent focus: T002\n",
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "Execution Plan" in result.output
        assert "2 tasks / 1 batches" in result.output
        assert "Runtime Updated" in result.output
        assert "2026-03-28T12:00:00+00:00" in result.output
        assert "Latest Summary" in result.output
        assert "Current focus: T002" in result.output

    def test_status_rebuilds_stale_resume_pack_without_mutating_checkpoint(
        self, tmp_path: Path
    ) -> None:
        init_project(tmp_path)
        spec_dir = tmp_path / "specs" / "WI-2026-STATUS"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
        (spec_dir / "tasks.md").write_text("# Tasks\n", encoding="utf-8")

        checkpoint = Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="WI-2026-STATUS",
                spec_dir="specs/WI-2026-STATUS",
                design_branch="feature/WI-2026-STATUS-docs",
                feature_branch="feature/WI-2026-STATUS-dev",
                current_branch="feature/WI-2026-STATUS-dev",
            ),
            execute_progress=ExecuteProgress(
                current_batch=1,
                total_batches=3,
                last_committed_task="T001",
            ),
        )
        save_checkpoint(tmp_path, checkpoint)
        pack = build_resume_pack(tmp_path)
        assert pack is not None
        save_resume_pack(tmp_path, pack)

        checkpoint.execute_progress = ExecuteProgress(
            current_batch=2,
            total_batches=3,
            last_committed_task="T002",
        )
        save_checkpoint(tmp_path, checkpoint)
        checkpoint_path = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
        before_checkpoint = checkpoint_path.read_text(encoding="utf-8")

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status"])

        after_checkpoint = checkpoint_path.read_text(encoding="utf-8")
        fresh_pack = load_resume_pack(tmp_path)

        assert result.exit_code == 0
        assert "stale" in result.output.lower()
        assert "rebuilding from checkpoint" in result.output.lower()
        assert "rebuilt successfully" in result.output.lower()
        assert "Resume Batch" in result.output
        assert "T002" in result.output
        assert before_checkpoint == after_checkpoint
        assert fresh_pack.current_batch == 2
        assert fresh_pack.last_committed_task == "T002"


def test_status_json_real_cli_path_does_not_mutate_project_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    config_path = (
        tmp_path
        / ".ai-sdlc"
        / "project"
        / "config"
        / "project-config.yaml"
    )
    before = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    time.sleep(1.2)
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["status", "--json"], catch_exceptions=False)

    after = config_path.read_text(encoding="utf-8") if config_path.exists() else None
    assert result.exit_code == 0
    assert after == before


def test_status_json_latest_scope_ids_do_not_depend_on_manifest_key_order(
    tmp_path: Path,
) -> None:
    init_project(tmp_path)
    local_root = telemetry_local_root(tmp_path)
    local_root.mkdir(parents=True, exist_ok=True)

    gs_old = "gs_ffffffffffffffffffffffffffffffff"
    gs_new = "gs_00000000000000000000000000000000"
    wr_old = "wr_ffffffffffffffffffffffffffffffff"
    wr_new = "wr_00000000000000000000000000000000"
    st_old = "st_ffffffffffffffffffffffffffffffff"
    st_new = "st_00000000000000000000000000000000"

    manifest_path = local_root / "manifest.json"
    # Simulate sort_keys=True output order (lexicographic), not registration order.
    manifest_path.write_text(
        json.dumps(
            {
                "version": 1,
                "sessions": {
                    gs_new: {"path": f"sessions/{gs_new}"},
                    gs_old: {"path": f"sessions/{gs_old}"},
                },
                "runs": {
                    wr_new: {"goal_session_id": gs_new, "path": f"sessions/{gs_new}/runs/{wr_new}"},
                    wr_old: {"goal_session_id": gs_old, "path": f"sessions/{gs_old}/runs/{wr_old}"},
                },
                "steps": {
                    st_new: {
                        "goal_session_id": gs_new,
                        "workflow_run_id": wr_new,
                        "path": f"sessions/{gs_new}/runs/{wr_new}/steps/{st_new}",
                    },
                    st_old: {
                        "goal_session_id": gs_old,
                        "workflow_run_id": wr_old,
                        "path": f"sessions/{gs_old}/runs/{wr_old}/steps/{st_old}",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    old_events_path = (
        local_root
        / "sessions"
        / gs_old
        / "runs"
        / wr_old
        / "steps"
        / st_old
        / "events.ndjson"
    )
    new_events_path = (
        local_root
        / "sessions"
        / gs_new
        / "runs"
        / wr_new
        / "steps"
        / st_new
        / "events.ndjson"
    )
    old_events_path.parent.mkdir(parents=True, exist_ok=True)
    new_events_path.parent.mkdir(parents=True, exist_ok=True)
    old_events_path.write_text(
        json.dumps(
            TelemetryEvent(
                scope_level=ScopeLevel.STEP,
                goal_session_id=gs_old,
                workflow_run_id=wr_old,
                step_id=st_old,
                created_at="2026-03-27T10:00:00Z",
                updated_at="2026-03-27T10:00:00Z",
                timestamp="2026-03-27T10:00:00Z",
                trace_layer=TraceLayer.WORKFLOW,
            ).model_dump(mode="json")
        )
        + "\n",
        encoding="utf-8",
    )
    new_events_path.write_text(
        json.dumps(
            TelemetryEvent(
                scope_level=ScopeLevel.STEP,
                goal_session_id=gs_new,
                workflow_run_id=wr_new,
                step_id=st_new,
                created_at="2026-03-27T10:00:10Z",
                updated_at="2026-03-27T10:00:10Z",
                timestamp="2026-03-27T10:00:10Z",
                trace_layer=TraceLayer.TOOL,
            ).model_dump(mode="json")
        )
        + "\n",
        encoding="utf-8",
    )

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    current = payload["telemetry"]["current"]
    assert current["sessions"]["latest_goal_session_id"] == gs_new
    assert current["runs"]["latest_workflow_run_id"] == wr_new
    assert current["steps"]["latest_step_id"] == st_new


def test_status_json_contract_is_available_when_project_state_is_uninitialized(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    save_project_state(
        tmp_path,
        ProjectState(
            status=ProjectStatus.UNINITIALIZED,
            project_name=tmp_path.name,
        ),
    )
    telemetry_root = telemetry_local_root(tmp_path)
    assert telemetry_root.exists() is False
    monkeypatch.chdir(tmp_path)

    status_result = runner.invoke(app, ["status", "--json"], catch_exceptions=False)
    doctor_result = runner.invoke(app, ["doctor"], catch_exceptions=False)

    assert status_result.exit_code == 0
    payload = json.loads(status_result.output)
    assert payload["telemetry"]["state"] == "not_initialized"
    assert "status --json surface" in doctor_result.output
    assert "not_initialized" in doctor_result.output


def test_status_json_reflects_fresh_writes_without_manual_rebuild(
    tmp_path: Path,
) -> None:
    init_project(tmp_path)
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    older_event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_ffffffffffffffffffffffffffffffff",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.WORKFLOW,
    )
    writer.write_event(older_event)

    fresh_event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_00000000000000000000000000000000",
        workflow_run_id="wr_00000000000000000000000000000000",
        created_at="2026-03-27T10:00:10Z",
        updated_at="2026-03-27T10:00:10Z",
        timestamp="2026-03-27T10:00:10Z",
        trace_layer=TraceLayer.TOOL,
    )
    fresh_violation = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=fresh_event.goal_session_id,
        workflow_run_id=fresh_event.workflow_run_id,
        created_at="2026-03-27T10:00:11Z",
        updated_at="2026-03-27T10:00:11Z",
    )
    fresh_artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=fresh_event.goal_session_id,
        workflow_run_id=fresh_event.workflow_run_id,
        created_at="2026-03-27T10:00:12Z",
        updated_at="2026-03-27T10:00:12Z",
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )
    writer.write_event(fresh_event)
    writer.write_violation(fresh_violation)
    writer.write_artifact(fresh_artifact)

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)["telemetry"]
    assert payload["current"]["sessions"]["latest_goal_session_id"] == fresh_event.goal_session_id
    assert payload["current"]["runs"]["latest_workflow_run_id"] == fresh_event.workflow_run_id
    assert payload["latest"]["open_violations"]["count"] == 1
    assert payload["latest"]["open_violations"]["sample_ids"] == [fresh_violation.violation_id]
    assert payload["latest"]["artifacts"]["count"] == 1
    assert payload["latest"]["artifacts"]["sample_ids"] == [fresh_artifact.artifact_id]


def test_status_json_latest_scope_ids_follow_fresh_writes_on_existing_scope(
    tmp_path: Path,
) -> None:
    init_project(tmp_path)
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    stale_session_event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.WORKFLOW,
    )
    latest_session_event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id="gs_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        created_at="2026-03-27T10:00:05Z",
        updated_at="2026-03-27T10:00:05Z",
        timestamp="2026-03-27T10:00:05Z",
        trace_layer=TraceLayer.WORKFLOW,
    )
    writer.write_event(stale_session_event)
    writer.write_event(latest_session_event)

    fresh_write_on_old_scope = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=stale_session_event.goal_session_id,
        created_at="2026-03-27T10:00:10Z",
        updated_at="2026-03-27T10:00:10Z",
        timestamp="2026-03-27T10:00:10Z",
        trace_layer=TraceLayer.TOOL,
    )
    writer.write_event(fresh_write_on_old_scope)

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)["telemetry"]
    assert payload["current"]["sessions"]["latest_goal_session_id"] == stale_session_event.goal_session_id


def test_status_json_fallback_latest_scope_ids_follow_fresh_writes_without_indexes(
    tmp_path: Path,
) -> None:
    init_project(tmp_path)
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    session_a = "gs_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    run_a = "wr_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    step_a = "st_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    session_b = "gs_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    run_b = "wr_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    step_b = "st_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    writer.write_event(
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=session_a,
            workflow_run_id=run_a,
            step_id=step_a,
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:00Z",
            timestamp="2026-03-27T10:00:00Z",
            trace_layer=TraceLayer.WORKFLOW,
        )
    )
    writer.write_event(
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=session_b,
            workflow_run_id=run_b,
            step_id=step_b,
            created_at="2026-03-27T10:00:05Z",
            updated_at="2026-03-27T10:00:05Z",
            timestamp="2026-03-27T10:00:05Z",
            trace_layer=TraceLayer.WORKFLOW,
        )
    )
    writer.write_event(
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=session_a,
            workflow_run_id=run_a,
            step_id=step_a,
            created_at="2026-03-27T10:00:10Z",
            updated_at="2026-03-27T10:00:10Z",
            timestamp="2026-03-27T10:00:10Z",
            trace_layer=TraceLayer.TOOL,
        )
    )
    store.delete_indexes()

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)["telemetry"]
    assert payload["current"]["sessions"]["latest_goal_session_id"] == session_a
    assert payload["current"]["runs"]["latest_workflow_run_id"] == run_a
    assert payload["current"]["steps"]["latest_step_id"] == step_a

    def test_status_json_includes_bounded_branch_lifecycle_summary(
        self, tmp_path: Path
    ) -> None:
        _write_branch_lifecycle_fixture(tmp_path)
        _create_branch_ahead_of_main(tmp_path, "codex/001-status-drift")

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["branch_lifecycle"]["state"] == "ready"
        assert payload["branch_lifecycle"]["blocking_count"] == 1
        assert payload["branch_lifecycle"]["active_work_item"] == "001-wi"
        assert payload["branch_lifecycle"]["sample_entries"][0]["name"] == "codex/001-status-drift"


def test_status_json_latest_summary_falls_back_to_canonical_snapshots_without_indexes(
    tmp_path: Path,
) -> None:
    init_project(tmp_path)
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.TOOL,
    )
    violation = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        created_at="2026-03-27T10:00:02Z",
        updated_at="2026-03-27T10:00:02Z",
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )

    writer.write_event(event)
    writer.write_violation(violation)
    writer.write_artifact(artifact)
    store.delete_indexes()

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)["telemetry"]
    assert payload["latest"]["open_violations"]["count"] == 1
    assert payload["latest"]["open_violations"]["sample_ids"] == [violation.violation_id]
    assert payload["latest"]["artifacts"]["count"] == 1
    assert payload["latest"]["artifacts"]["sample_ids"] == [artifact.artifact_id]
    assert payload["latest"]["timeline_cursor"] == {
        "event_count": 1,
        "last_event_id": event.event_id,
        "last_timestamp": event.timestamp,
    }


def test_status_json_fallback_does_not_recreate_missing_indexes(tmp_path: Path) -> None:
    init_project(tmp_path)
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.TOOL,
    )
    writer.write_event(event)
    store.delete_indexes()
    indexes_root = telemetry_indexes_root(tmp_path)
    assert not list(indexes_root.glob("*.json"))

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    assert not list(indexes_root.glob("*.json"))

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    assert not list(indexes_root.glob("*.json"))


def test_status_json_fallback_latest_scope_ids_ignore_misleading_mtime(
    tmp_path: Path,
) -> None:
    init_project(tmp_path)
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    session_a = "gs_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    run_a = "wr_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    step_a = "st_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    session_b = "gs_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    run_b = "wr_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    step_b = "st_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    writer.write_event(
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=session_b,
            workflow_run_id=run_b,
            step_id=step_b,
            created_at="2026-03-27T10:00:05Z",
            updated_at="2026-03-27T10:00:05Z",
            timestamp="2026-03-27T10:00:05Z",
            trace_layer=TraceLayer.WORKFLOW,
        )
    )
    writer.write_event(
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id=session_a,
            workflow_run_id=run_a,
            step_id=step_a,
            created_at="2026-03-27T10:00:10Z",
            updated_at="2026-03-27T10:00:10Z",
            timestamp="2026-03-27T10:00:10Z",
            trace_layer=TraceLayer.TOOL,
        )
    )

    local_root = telemetry_local_root(tmp_path)
    stale_scope_paths = [
        local_root / "sessions" / session_b,
        local_root / "sessions" / session_b / "runs" / run_b,
        local_root / "sessions" / session_b / "runs" / run_b / "steps" / step_b,
        local_root / "sessions" / session_b / "runs" / run_b / "steps" / step_b / "events.ndjson",
    ]
    fresh_scope_paths = [
        local_root / "sessions" / session_a,
        local_root / "sessions" / session_a / "runs" / run_a,
        local_root / "sessions" / session_a / "runs" / run_a / "steps" / step_a,
        local_root / "sessions" / session_a / "runs" / run_a / "steps" / step_a / "events.ndjson",
    ]
    stale_mtime = 2_000_000_000
    fresh_mtime = stale_mtime - 1_000
    for path in stale_scope_paths:
        os.utime(path, (stale_mtime, stale_mtime))
    for path in fresh_scope_paths:
        os.utime(path, (fresh_mtime, fresh_mtime))
    store.delete_indexes()

    with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
        result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)["telemetry"]
    assert payload["current"]["sessions"]["latest_goal_session_id"] == session_a
    assert payload["current"]["runs"]["latest_workflow_run_id"] == run_a
    assert payload["current"]["steps"]["latest_step_id"] == step_a
