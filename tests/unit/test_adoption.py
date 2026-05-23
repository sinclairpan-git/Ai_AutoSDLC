from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ai_sdlc.core.adoption import (
    AdoptedTask,
    AdoptionBudget,
    AdoptionContinuePoint,
    AdoptionMap,
    AdoptionTaskStatus,
    build_adoption_map,
    discover_adoption_sources,
    recommend_continue_point,
    write_adoption_artifacts,
)


def test_discovery_ignores_build_outputs_and_honors_budget(tmp_path: Path) -> None:
    (tmp_path / "tasks.json").write_text("[]\n", encoding="utf-8")
    ignored = tmp_path / "node_modules" / "tasks.json"
    ignored.parent.mkdir()
    ignored.write_text("[]\n", encoding="utf-8")
    generated = tmp_path / ".ai-sdlc" / "adoption" / "adoption-map.json"
    generated.parent.mkdir(parents=True)
    generated.write_text("[]\n", encoding="utf-8")

    sources = discover_adoption_sources(
        tmp_path,
        target=tmp_path,
        budget=AdoptionBudget(max_candidate_files=10),
    )

    assert [source.rel_path for source in sources] == ["tasks.json"]


def test_discovery_supports_chinese_names_readme_and_content_sniff(tmp_path: Path) -> None:
    (tmp_path / "任务.md").write_text("- [ ] 支付回调\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("- [ ] 初始化项目\n", encoding="utf-8")
    (tmp_path / "data.json").write_text(
        json.dumps({"items": [{"title": "隐藏任务", "status": "todo"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    sources = discover_adoption_sources(
        tmp_path,
        target=tmp_path,
        budget=AdoptionBudget(),
    )

    assert {source.rel_path for source in sources} >= {"任务.md", "README.md", "data.json"}


def test_json_schema_inference_supports_nested_and_missing_fields(tmp_path: Path) -> None:
    payload = {
        "items": [
            {
                "key": "PAY-1",
                "summary": "支付回调幂等",
                "state": "in_progress",
                "files": ["src/pay/callback.py"],
                "updated_at": "2026-05-20",
                "children": [
                    {
                        "id": "PAY-1.1",
                        "title": "补测试",
                        "progress": 0,
                    }
                ],
            }
        ]
    }
    (tmp_path / "progress.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    adoption_map = build_adoption_map(tmp_path)

    assert {task.external_id for task in adoption_map.tasks} >= {"PAY-1", "PAY-1.1"}
    main_task = next(task for task in adoption_map.tasks if task.external_id == "PAY-1")
    child = next(task for task in adoption_map.tasks if task.external_id == "PAY-1.1")
    assert main_task.status is AdoptionTaskStatus.DOING
    assert main_task.confidence >= 0.8
    assert main_task.ai_sdlc_task_id == "ADOPT-001"
    assert main_task.updated_at == "2026-05-20"
    assert child.status is AdoptionTaskStatus.UNKNOWN
    assert child.confidence < main_task.confidence


def test_json_schema_inference_uses_percent_and_completion_progress_keys(
    tmp_path: Path,
) -> None:
    payload = {
        "tasks": [
            {"id": "PCT-1", "title": "百分比进行中", "percent": 45},
            {"id": "CMP-1", "title": "完成度已完成", "completion": 100},
        ]
    }
    (tmp_path / "progress.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    adoption_map = build_adoption_map(tmp_path)

    statuses = {task.external_id: task.status for task in adoption_map.tasks}
    assert statuses["PCT-1"] is AdoptionTaskStatus.DOING
    assert statuses["CMP-1"] is AdoptionTaskStatus.DONE


def test_markdown_and_git_sources_do_not_require_git_history(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        "- [ ] 接入支付回调\n- [x] 完成用户登录\n- [X] 完成订单列表\n进行中：订单退款\n",
        encoding="utf-8",
    )

    adoption_map = build_adoption_map(tmp_path, prefer_text="支付回调")

    assert adoption_map.continue_point.title == "接入支付回调"
    assert any(
        task.title == "完成订单列表" and task.status is AdoptionTaskStatus.DONE
        for task in adoption_map.tasks
    )
    assert any(task.title == "订单退款" for task in adoption_map.tasks)
    assert any("未检测到 Git 历史" in warning for warning in adoption_map.warnings)


def test_continue_point_prefers_user_correction() -> None:
    adoption_map = build_adoption_map_fixture()

    selected = recommend_continue_point(adoption_map.tasks, prefer_text="支付回调")

    assert selected.title == "支付回调"
    assert selected.confidence >= 0.75


def test_continue_point_penalizes_blockers_and_dependencies() -> None:
    blocked = AdoptedTask(
        external_id="A",
        ai_sdlc_task_id="ADOPT-001",
        title="支付回调",
        description="",
        status=AdoptionTaskStatus.DOING,
        source="tasks.json",
        confidence=0.8,
        blockers=("等待接口",),
    )
    ready = AdoptedTask(
        external_id="B",
        ai_sdlc_task_id="ADOPT-002",
        title="订单退款",
        description="",
        status=AdoptionTaskStatus.DOING,
        source="tasks.json",
        confidence=0.72,
    )

    selected = recommend_continue_point((blocked, ready))

    assert selected.task_id == "B"
    assert "存在阻塞" not in selected.reason


def test_write_artifacts_does_not_modify_original_task_file(tmp_path: Path) -> None:
    task_file = tmp_path / "tasks.json"
    original = '[{"id":"1","title":"支付回调","status":"doing"}]\n'
    task_file.write_text(original, encoding="utf-8")
    adoption_map = build_adoption_map(tmp_path)

    map_path, bridge_path, checkpoint_path = write_adoption_artifacts(tmp_path, adoption_map)

    assert task_file.read_text(encoding="utf-8") == original
    assert map_path.is_file()
    assert checkpoint_path.is_file()
    assert "active_task" in checkpoint_path.read_text(encoding="utf-8")
    assert bridge_path.read_text(encoding="utf-8").startswith("# 接入已有项目桥接结果")


def test_recent_git_commit_can_seed_low_confidence_task(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "app.py").write_text("print('hi')\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "feat: payment callback"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    adoption_map = build_adoption_map(tmp_path)

    assert any("payment callback" in task.title for task in adoption_map.tasks)


def test_git_branch_diff_and_test_sources_are_included(tmp_path: Path) -> None:
    _init_git_repo(tmp_path)
    (tmp_path / "tests").mkdir()
    (tmp_path / "app.py").write_text("print('hi')\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "app.py").write_text("print('changed')\n", encoding="utf-8")

    adoption_map = build_adoption_map(tmp_path)

    titles = {task.title for task in adoption_map.tasks}
    assert "继续当前分支：main" in titles
    assert "继续当前未提交改动" in titles
    assert "保留并复用现有测试结构" in titles


def test_scan_budget_stops_before_deep_directory_walk(tmp_path: Path) -> None:
    current = tmp_path
    for index in range(20):
        current = current / f"dir-{index}"
        current.mkdir()
        (current / "任务.md").write_text("- [ ] 深层任务\n", encoding="utf-8")

    sources = discover_adoption_sources(
        tmp_path,
        target=tmp_path,
        budget=AdoptionBudget(max_visited_dirs=3, max_visited_files=100),
    )

    assert len(sources) <= 3


def test_checkpoint_candidate_is_generated(tmp_path: Path) -> None:
    (tmp_path / "tasks.json").write_text(
        '[{"id":"A","title":"支付回调","status":"doing"}]\n',
        encoding="utf-8",
    )

    adoption_map = build_adoption_map(tmp_path)

    assert adoption_map.checkpoint_candidate["active_task"] == "A"
    assert adoption_map.checkpoint_candidate["current_stage"] == "execute"


def build_adoption_map_fixture() -> AdoptionMap:
    return AdoptionMap(
        generated_at="2026-05-23T00:00:00Z",
        root="/tmp/repo",
        sources=(),
        tasks=(
            AdoptedTask(
                external_id="A",
                ai_sdlc_task_id="ADOPT-001",
                title="用户登录",
                description="",
                status=AdoptionTaskStatus.DOING,
                source="tasks.json",
                confidence=0.8,
            ),
            AdoptedTask(
                external_id="B",
                ai_sdlc_task_id="ADOPT-002",
                title="支付回调",
                description="",
                status=AdoptionTaskStatus.TODO,
                source="tasks.json",
                confidence=0.65,
            ),
        ),
        continue_point=AdoptionContinuePoint("A", "用户登录", 0.9, "fixture", False),
        checkpoint_candidate={"active_task": "A"},
    )


def _init_git_repo(root: Path) -> None:
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
