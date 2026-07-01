"""Tests for the deterministic implementation loop runtime."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.core.design_contract_loop import (
    DesignContractCheckOptions,
    DesignContractCloseOptions,
    check_design_contract_loop,
    close_design_contract_loop,
)
from ai_sdlc.core.implementation_loop import (
    CURRENT_IMPLEMENTATION_PATH,
    ImplementationCloseOptions,
    ImplementationRecordOptions,
    ImplementationStartOptions,
    close_implementation_loop,
    record_implementation_progress,
    start_implementation_loop,
)
from ai_sdlc.core.requirement_loop import (
    RequirementFreezeOptions,
    RequirementStartOptions,
    freeze_requirement_loop,
    start_requirement_loop,
)


def test_start_implementation_loop_writes_artifacts(tmp_path: Path) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)

    result = start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-001",
        )
    )

    assert result.status == "ready"
    assert result.loop_status == "running"
    assert result.work_item_id == "demo-implementation-loop"
    assert result.required_task_count == 1
    assert result.done_count == 0
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is True
    assert result.next_guidance.writes_code is False
    assert result.implementation is not None
    assert result.implementation.report_path.endswith(
        ".ai-sdlc/loops/implementation/impl-001/implementation-report.json"
    )

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "implementation" / "impl-001"
    assert (loop_dir / "loop-run.json").is_file()
    assert (loop_dir / "implementation-input.json").is_file()
    assert (loop_dir / "implementation-tasks.json").is_file()
    assert (loop_dir / "implementation-progress.json").is_file()
    assert (loop_dir / "verification-evidence.json").is_file()
    assert (loop_dir / "implementation-report.json").is_file()
    assert (loop_dir / "implementation-report.md").is_file()
    assert (tmp_path / CURRENT_IMPLEMENTATION_PATH).is_file()

    tasks = json.loads((loop_dir / "implementation-tasks.json").read_text("utf-8"))
    assert tasks["artifact_kind"] == "implementation-tasks"
    assert tasks["created_by"] == "ai-sdlc"
    assert [item["task_id"] for item in tasks["items"]] == ["T11", "T21"]
    assert [item["required"] for item in tasks["items"]] == [True, False]


def test_start_implementation_loop_dry_run_does_not_write(tmp_path: Path) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)

    result = start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-dry-run",
            dry_run=True,
        )
    )

    assert result.status == "dry_run"
    assert result.dry_run is True
    assert result.required_task_count == 1
    assert not (
        tmp_path / ".ai-sdlc" / "loops" / "implementation" / "impl-dry-run"
    ).exists()


def test_start_implementation_loop_blocks_unclosed_design_contract(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _start_frozen_requirement(tmp_path, work_item)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            requirement_loop_id="req-demo-implementation-loop",
            loop_id="dc-demo-implementation-loop",
        )
    )

    result = start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-unclosed-design",
        )
    )

    assert result.status == "blocked"
    assert "must be closed" in result.blocker
    assert result.next_action == "Run ai-sdlc loop design-contract close --yes."


def test_record_implementation_progress_updates_evidence_and_report(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-record",
        )
    )

    result = record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-record",
            task_id="T11",
            status="done",
            evidence=("src/ai_sdlc/core/implementation_loop.py",),
            verification=("uv run pytest tests/unit/test_implementation_loop.py -q",),
            note="核心 runtime 已验证",
        )
    )

    assert result.status == "ready"
    assert result.loop_status == "passed"
    assert result.done_count == 1
    assert result.evidence_count == 2
    assert result.next_action == "Run ai-sdlc loop implementation close --yes."
    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "implementation" / "impl-record"
    progress = json.loads((loop_dir / "implementation-progress.json").read_text("utf-8"))
    task = next(item for item in progress["tasks"] if item["task_id"] == "T11")
    assert task["status"] == "done"
    assert task["evidence"] == ["src/ai_sdlc/core/implementation_loop.py"]
    assert task["verification_commands"] == [
        "uv run pytest tests/unit/test_implementation_loop.py -q"
    ]


def test_record_implementation_progress_blocks_unknown_task(tmp_path: Path) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-unknown-task",
        )
    )

    result = record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-unknown-task",
            task_id="T99",
            status="done",
            evidence=("x.py",),
        )
    )

    assert result.status == "blocked"
    assert result.blocker == "Unknown implementation task id: T99."


def test_record_implementation_progress_blocks_done_without_evidence(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-no-evidence",
        )
    )

    result = record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-no-evidence",
            task_id="T11",
            status="done",
        )
    )

    assert result.status == "blocked"
    assert "must include --evidence or --verification" in result.blocker


def test_record_implementation_progress_blocked_state_has_no_fake_command(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-task-blocked",
        )
    )

    result = record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-task-blocked",
            task_id="T11",
            status="blocked",
            note="等待用户提供验证环境。",
        )
    )

    assert result.status == "needs_fix"
    assert result.loop_status == "needs_fix"
    assert result.next_action == "Resolve implementation blocker for T11, then record progress."
    assert result.next_guidance.command == ""


def test_close_implementation_loop_blocks_incomplete_required_tasks(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-incomplete",
        )
    )

    result = close_implementation_loop(
        ImplementationCloseOptions(root=tmp_path, loop_id="impl-incomplete", yes=True)
    )

    assert result.status == "needs_fix"
    assert result.blocker == "T11 is not done."
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "implementation"
        / "impl-incomplete"
        / "implementation-close.json"
    ).exists()


def test_close_implementation_loop_writes_close_artifact(tmp_path: Path) -> None:
    work_item = _write_ready_work_item(tmp_path)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-close",
        )
    )
    record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-close",
            task_id="T11",
            status="done",
            verification=("uv run pytest tests/unit/test_implementation_loop.py -q",),
        )
    )

    result = close_implementation_loop(
        ImplementationCloseOptions(root=tmp_path, loop_id="impl-close", yes=True)
    )

    assert result.status == "ready"
    assert result.closed is True
    assert result.loop_status == "closed"
    assert result.next_action == "Run ai-sdlc pr-review start."
    close_payload = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "implementation"
            / "impl-close"
            / "implementation-close.json"
        ).read_text("utf-8")
    )
    assert close_payload["artifact_kind"] == "implementation-close"
    assert close_payload["next_loop_type"] == "local-pr-review"


def test_close_implementation_loop_routes_frontend_work_to_frontend_evidence(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(tmp_path, frontend=True)
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-frontend",
        )
    )
    record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-frontend",
            task_id="T11",
            status="done",
            verification=("uv run pytest tests/unit/test_implementation_loop.py -q",),
        )
    )

    result = close_implementation_loop(
        ImplementationCloseOptions(root=tmp_path, loop_id="impl-frontend", yes=True)
    )

    assert result.status == "ready"
    assert result.next_action == (
        "Run ai-sdlc loop frontend-evidence start --wi specs/demo-implementation-loop."
    )
    close_payload = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "implementation"
            / "impl-frontend"
            / "implementation-close.json"
        ).read_text("utf-8")
    )
    assert close_payload["next_loop_type"] == "frontend-evidence"


def test_close_implementation_loop_ignores_frontend_signal_inside_words(
    tmp_path: Path,
) -> None:
    work_item = _write_ready_work_item(
        tmp_path,
        extra_spec="This backend build guidance uses a test suite.",
    )
    _close_design_contract_for_work_item(tmp_path, work_item)
    start_implementation_loop(
        ImplementationStartOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            loop_id="impl-non-frontend-words",
        )
    )
    record_implementation_progress(
        ImplementationRecordOptions(
            root=tmp_path,
            loop_id="impl-non-frontend-words",
            task_id="T11",
            status="done",
            verification=("uv run pytest tests/unit/test_implementation_loop.py -q",),
        )
    )

    result = close_implementation_loop(
        ImplementationCloseOptions(
            root=tmp_path,
            loop_id="impl-non-frontend-words",
            yes=True,
        )
    )

    assert result.next_action == "Run ai-sdlc pr-review start."
    close_payload = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "implementation"
            / "impl-non-frontend-words"
            / "implementation-close.json"
        ).read_text("utf-8")
    )
    assert close_payload["next_loop_type"] == "local-pr-review"


def _write_ready_work_item(
    tmp_path: Path,
    *,
    frontend: bool = False,
    extra_spec: str = "",
) -> Path:
    work_item = tmp_path / "specs" / "demo-implementation-loop"
    work_item.mkdir(parents=True)
    frontend_text = " 前端页面和浏览器证据。" if frontend else ""
    extra_spec_text = f" {extra_spec}" if extra_spec else ""
    (work_item / "spec.md").write_text(
        "\n".join(
            [
                "# PRD：Implementation Demo",
                "",
                "**状态**：formal baseline 已冻结",
                "",
                "## 需求",
                "",
                f"- **FR-IMPL-001**：系统必须记录实现任务证据。{frontend_text}{extra_spec_text}",
                "",
                "## 成功标准",
                "",
                "- **SC-IMPL-001**：完成任务后可以关闭 implementation loop。",
            ]
        ),
        encoding="utf-8",
    )
    (work_item / "plan.md").write_text(
        "\n".join(
            [
                "# 实施计划：Implementation Demo",
                "",
                "## 技术背景",
                "Python runtime.",
                "## 阶段计划",
                "Phase 1.",
                "## 验证",
                "Run pytest.",
                "## 回退",
                "Revert the commit.",
            ]
        ),
        encoding="utf-8",
    )
    (work_item / "tasks.md").write_text(
        "\n".join(
            [
                "# 任务分解：Implementation Demo",
                "",
                "### Task 1.1 Implement runtime",
                "",
                "- **任务编号**：T11",
                "- **优先级**：P0",
                "- **文件**：src/ai_sdlc/core/implementation_loop.py",
                "- **验收标准**：",
                "  1. FR-IMPL-001 and SC-IMPL-001 are covered.",
                "- **验证**：`uv run pytest tests/unit/test_implementation_loop.py -q`",
                "",
                "### Task 2.1 Deferred polish",
                "",
                "- **任务编号**：T21",
                "- **优先级**：P2",
                "- **文件**：README.md",
                "- **验收标准**：",
                "  1. Deferred.",
                "- **验证**：`uv run pytest tests/unit/test_implementation_loop.py -q`",
            ]
        ),
        encoding="utf-8",
    )
    return work_item


def _start_frozen_requirement(tmp_path: Path, work_item: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            idea="Implementation loop needs evidence tracking.",
            acceptance=("Implementation evidence can be closed.",),
            work_item_id=work_item.name,
            loop_id="req-demo-implementation-loop",
        )
    )
    freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            loop_id="req-demo-implementation-loop",
            yes=True,
        )
    )


def _close_design_contract_for_work_item(tmp_path: Path, work_item: Path) -> None:
    _start_frozen_requirement(tmp_path, work_item)
    check = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-implementation-loop",
            requirement_loop_id="req-demo-implementation-loop",
            loop_id="dc-demo-implementation-loop",
        )
    )
    assert check.status == "ready"
    close = close_design_contract_loop(
        DesignContractCloseOptions(
            root=tmp_path,
            loop_id="dc-demo-implementation-loop",
            yes=True,
        )
    )
    assert close.status == "ready"
    assert close.closed is True
