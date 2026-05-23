from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.models.state import Checkpoint, FeatureInfo
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


def _write_work_item(root: Path, *, status: str = "todo") -> Path:
    spec_dir = root / "specs" / "183-wi"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "plan.md").write_text("# Plan\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(
        f"""
### Task 1.1 Implement

- task_id: T11
- status: {status}
- goal: Implement guarded work
- scope:
  - src/a.py
- acceptance:
  - done
- verify:
  - pytest
""",
        encoding="utf-8",
    )
    return spec_dir


def _save_checkpoint(root: Path) -> None:
    save_checkpoint(
        root,
        Checkpoint(
            current_stage="execute",
            feature=FeatureInfo(
                id="183-wi",
                spec_dir="specs/183-wi",
                design_branch="design/183-wi",
                feature_branch="feature/183-wi",
                current_branch="feature/183-wi",
            ),
        ),
    )


def test_workitem_guard_json_shows_next_executable_task(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_project(tmp_path)
    _write_work_item(tmp_path)
    _save_checkpoint(tmp_path)
    monkeypatch.chdir(tmp_path)

    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        result = runner.invoke(app, ["workitem", "guard", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["state"] == "ALLOW_CODE_WITH_TASK"
    assert payload["task_id"] == "T11"
    assert payload["task_goal"] == "Implement guarded work"


def test_workitem_guard_blocks_without_executable_task(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_project(tmp_path)
    _write_work_item(tmp_path, status="done")
    _save_checkpoint(tmp_path)
    monkeypatch.chdir(tmp_path)

    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        result = runner.invoke(app, ["workitem", "guard", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["state"] == "BLOCK_CODE_PREPARE_TASKS"
    assert "preparation_candidate" in payload


def test_workitem_guard_blocks_missing_plan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_project(tmp_path)
    spec_dir = _write_work_item(tmp_path)
    (spec_dir / "plan.md").unlink()
    _save_checkpoint(tmp_path)
    monkeypatch.chdir(tmp_path)

    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        result = runner.invoke(app, ["workitem", "guard", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["state"] == "BLOCK_CODE_PREPARE_TASKS"
    assert "plan.md" in payload["detail"]
