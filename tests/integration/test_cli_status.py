"""Integration tests for ai-sdlc status CLI command."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry.paths import telemetry_indexes_root, telemetry_local_root

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
    @pytest.fixture(autouse=True)
    def _no_ide_adapter_hook(self) -> None:
        with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
            yield

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
                }
            ),
            encoding="utf-8",
        )

        with patch("ai_sdlc.cli.commands.find_project_root", return_value=tmp_path):
            result = runner.invoke(app, ["status", "--json"])

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert set(payload) == {"telemetry"}
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
