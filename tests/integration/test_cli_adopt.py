"""Integration tests for `ai-sdlc adopt`."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project

runner = CliRunner()


@pytest.fixture(autouse=True)
def _no_ide_adapter_hook() -> None:
    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        yield


def test_adopt_generates_bridge_without_modifying_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    init_project(root)
    source = root / "task-progress.json"
    original = json.dumps(
        [
            {
                "id": "PAY-1",
                "title": "支付回调",
                "status": "doing",
                "files": ["src/pay/callback.py"],
            }
        ],
        ensure_ascii=False,
    )
    source.write_text(original + "\n", encoding="utf-8")
    monkeypatch.chdir(root)

    result = runner.invoke(app, ["adopt", "."])

    assert result.exit_code == 0
    assert "接入已有项目" in result.output
    assert "原任务文件不会被修改" in result.output
    assert source.read_text(encoding="utf-8") == original + "\n"
    assert (root / ".ai-sdlc" / "adoption" / "adoption-map.json").is_file()
    assert (root / ".ai-sdlc" / "adoption" / "bridge.md").is_file()
    assert (root / ".ai-sdlc" / "adoption" / "checkpoint-candidate.json").is_file()


def test_adopt_json_supports_natural_language_correction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    init_project(root)
    (root / "tasks.json").write_text(
        json.dumps(
            [
                {"id": "A", "title": "用户登录", "status": "doing"},
                {"id": "B", "title": "支付回调", "status": "todo"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(root)

    result = runner.invoke(app, ["adopt", ".", "--prefer", "支付回调", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["continue_point"]["task_id"] == "B"
    assert payload["continue_point"]["title"] == "支付回调"
    assert payload["map_path"] == ".ai-sdlc/adoption/adoption-map.json"
    assert payload["checkpoint_candidate_path"] == (
        ".ai-sdlc/adoption/checkpoint-candidate.json"
    )


def test_adopt_requires_initialized_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["adopt", "."])

    assert result.exit_code == 1
    assert "ai-sdlc init ." in result.output
    assert "当前目录还没有初始化" in result.output
