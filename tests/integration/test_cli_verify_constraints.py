"""Integration tests: ai-sdlc verify constraints (FR-089 / SC-012)."""

from __future__ import annotations

import json
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


def _framework_backlog(root: Path, *, include_eval: bool) -> None:
    path = root / "docs" / "framework-defect-backlog.zh-CN.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# 框架缺陷待办池\n\n"
        "## FD-2026-03-26-001 | 示例条目\n\n"
        "- 现象: 发现框架缺陷\n"
        "- 触发场景: 用户要求登记\n"
        "- 影响范围: 规则与流程\n"
        "- 根因分类: B\n"
        "- 建议改动层级: rule / policy, workflow\n"
        "- prompt / context: 会话内发现偏离\n"
        "- rule / policy: pipeline.md 条款 17\n"
        "- middleware: 无\n"
        "- workflow: 需登记再继续\n"
        "- tool: ai-sdlc verify constraints\n"
    )
    if include_eval:
        body += "- eval: 结构化字段完整率\n"
    body += (
        "- 风险等级: 中\n"
        "- 可验证成功标准: verify constraints 无 BLOCKER\n"
        "- 是否需要回归测试补充: 是\n"
    )
    path.write_text(body, encoding="utf-8")


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

    def test_exit_1_tasks_missing_acceptance(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        spec = tmp_path / "specs" / "001-wi"
        spec.mkdir(parents=True)
        (spec / "tasks.md").write_text(
            "### Task 1.1\n- **依赖**：无\n",
            encoding="utf-8",
        )
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
        assert result.exit_code == 1
        assert "BLOCKER" in result.output
        assert "SC-014" in result.output

    def test_json_output(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        save_checkpoint(
            tmp_path,
            Checkpoint(
                current_stage="init",
                feature=FeatureInfo(
                    id="001",
                    spec_dir="specs/missing-wi",
                    design_branch="d",
                    feature_branch="f",
                    current_branch="main",
                ),
            ),
        )
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert set(payload) >= {"ok", "blockers", "root"}
        session_id = payload["telemetry"]["goal_session_id"]
        events_path = (
            tmp_path
            / ".ai-sdlc"
            / "local"
            / "telemetry"
            / "sessions"
            / session_id
            / "events.ndjson"
        )
        lines = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert lines[-1]["scope_level"] == "session"
        assert lines[-1]["status"] == "failed"
        assert lines[-1]["trace_layer"] == "workflow"
        telemetry_root = tmp_path / ".ai-sdlc" / "local" / "telemetry"
        assert telemetry_root.is_dir()
        assert list(telemetry_root.rglob("events.ndjson"))
        assert list(telemetry_root.rglob("evidence.ndjson"))
        assert list(telemetry_root.rglob("evaluations/*.json"))
        assert list(telemetry_root.rglob("violations/*.json"))

    def test_json_output_outside_project_includes_root(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints", "--json"])
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert payload["ok"] is False
        assert payload["blockers"] == []
        assert "root" in payload
        assert payload["root"] is None

    def test_exit_1_when_skip_registry_unmapped(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        spec = tmp_path / "specs" / "001-wi"
        spec.mkdir(parents=True)
        (spec / "spec.md").write_text("- **FR-001**: x\n", encoding="utf-8")
        (spec / "tasks.md").write_text(
            "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. ok\n",
            encoding="utf-8",
        )
        rules_dir = tmp_path / "src" / "ai_sdlc" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "agent-skip-registry.zh.md").write_text(
            "| 日期 | 发现阶段 | 跳过内容摘要 | 根因 | 框架强化建议 | wi_id | 状态 |\n"
            "|------|----------|--------------|------|--------------|-------|------|\n"
            "| 2026-03-26 | 执行 | x | A | 引入 FR-999 并补 Task 9.9 | 001-wi | 已记录 |\n",
            encoding="utf-8",
        )
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
        assert result.exit_code == 1
        assert "skip-registry" in result.output

    def test_exit_1_when_framework_backlog_missing_required_field(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _framework_backlog(tmp_path, include_eval=False)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 1
        assert "framework-defect-backlog" in result.output

    def test_exit_0_when_framework_backlog_well_formed(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        init_project(tmp_path)
        _minimal_constitution(tmp_path)
        _framework_backlog(tmp_path, include_eval=True)
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(app, ["verify", "constraints"])
        assert result.exit_code == 0
        assert "no blocker" in result.output.lower()
