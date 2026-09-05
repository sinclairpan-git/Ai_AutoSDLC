"""Tests for the deterministic requirement loop runtime."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ai_sdlc.core.requirement_loop import (
    CURRENT_REQUIREMENT_PATH,
    RequirementFreezeOptions,
    RequirementStartOptions,
    freeze_requirement_loop,
    review_requirement_loop,
    start_requirement_loop,
)


def _tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


def _write_execution(
    root: Path,
    loop_id: str,
    *,
    severity: str = "",
    name: str = "review-execution.json",
) -> Path:
    result = review_requirement_loop(root, loop_id)
    assert result.review is not None
    findings = []
    if severity:
        findings = [
            {
                "severity": severity,
                "location": "intake.acceptance_criteria",
                "description": "缺少失败路径验收。",
                "recommendation": "增加失败路径断言。",
            }
        ]
    payload = {
        "input_digest": result.review.input_digest,
        "round_number": result.review.round_number,
        "results": [
            {
                "role_id": role["role_id"],
                "status": "completed",
                "findings": findings if index == 0 else [],
            }
            for index, role in enumerate(result.review.roles)
        ],
    }
    path = root / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_start_requirement_loop_writes_artifacts(tmp_path: Path) -> None:
    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-001",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置", "审批记录可以追踪"),
            work_item_id="192-loop-engine-requirement-loop-runtime",
        )
    )

    assert result.status == "ready"
    assert result.loop_id == "req-001"
    assert result.loop_status == "needs_review"
    assert result.acceptance_count == 2
    assert result.source_kind == "idea"
    assert result.source_path == ""
    assert result.requirement is not None
    assert (
        result.requirement.summary == "运营用户需要订单审批流，范围只覆盖后台人工审批。"
    )
    assert result.requirement.source_kind == "idea"
    assert result.requirement.acceptance_count == 2
    assert (
        result.next_action == "Run ai-sdlc loop requirement review --loop-id req-001."
    )

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-001"
    assert (loop_dir / "loop-run.json").is_file()
    assert (loop_dir / "requirement-intake.json").is_file()
    assert (loop_dir / "requirement-brief.md").is_file()
    assert (loop_dir / "clarification-questions.md").is_file()
    assert (loop_dir / "acceptance-checklist.md").is_file()
    assert (tmp_path / CURRENT_REQUIREMENT_PATH).is_file()

    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["loop_type"] == "requirement"
    assert loop_run["status"] == "needs_review"
    assert loop_run["work_item_id"] == "192-loop-engine-requirement-loop-runtime"

    intake = json.loads(
        (loop_dir / "requirement-intake.json").read_text(encoding="utf-8")
    )
    assert intake["artifact_kind"] == "requirement-intake"
    assert intake["review_required"] is True
    assert intake["summary"] == "运营用户需要订单审批流，范围只覆盖后台人工审批。"
    assert intake["acceptance_criteria"] == ["审批节点可以配置", "审批记录可以追踪"]


def test_start_requirement_loop_without_acceptance_needs_user(tmp_path: Path) -> None:
    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-needs-user",
            idea="做一个报表",
        )
    )

    assert result.status == "needs_user"
    assert result.loop_status == "needs_user"
    assert result.acceptance_count == 0
    assert result.clarification_count >= 1
    assert "acceptance" in result.next_action
    assert "--loop-id req-needs-user" in result.next_action
    assert "--acceptance" in result.next_action

    checklist = (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / "req-needs-user"
        / "acceptance-checklist.md"
    ).read_text(encoding="utf-8")
    assert "待补充" in checklist


def test_start_requirement_loop_reuses_existing_intake_when_adding_acceptance(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-add-acceptance",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
        )
    )

    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-add-acceptance",
            acceptance=("审批节点可以配置",),
        )
    )

    assert result.status == "ready"
    assert result.loop_status == "needs_review"
    assert result.acceptance_count == 1
    assert result.summary == "运营用户需要订单审批流，范围只覆盖后台人工审批。"
    assert result.next_action == (
        "Run ai-sdlc loop requirement review --loop-id req-add-acceptance."
    )

    intake_path = (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / "req-add-acceptance"
        / "requirement-intake.json"
    )
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    assert intake["raw_text"] == "运营用户需要订单审批流，范围只覆盖后台人工审批。"
    assert intake["acceptance_criteria"] == ["审批节点可以配置"]


def test_start_requirement_loop_generates_unique_default_loop_ids(
    tmp_path: Path,
) -> None:
    first = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )
    second = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            idea="客服用户需要 SLA 提醒，范围只覆盖站内提醒。",
            acceptance=("SLA 超时前可以提醒",),
        )
    )

    assert first.loop_id.startswith("requirement-")
    assert second.loop_id.startswith("requirement-")
    assert first.loop_id != second.loop_id
    assert (tmp_path / ".ai-sdlc" / "loops" / "requirement" / first.loop_id).is_dir()
    assert (tmp_path / ".ai-sdlc" / "loops" / "requirement" / second.loop_id).is_dir()


def test_start_requirement_loop_dry_run_does_not_write(tmp_path: Path) -> None:
    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-dry-run",
            idea="管理员用户需要导出审计日志，范围只覆盖 CSV。",
            acceptance=("可以下载 CSV",),
            dry_run=True,
        )
    )

    assert result.status == "dry_run"
    assert result.dry_run is True
    assert result.loop_status == "needs_review"
    assert result.source_kind == "idea"
    assert result.requirement is not None
    assert result.requirement.summary == "管理员用户需要导出审计日志，范围只覆盖 CSV。"
    assert not (tmp_path / ".ai-sdlc").exists()
    assert any(artifact.kind == "loop-run" for artifact in result.artifacts)


def test_start_requirement_loop_reads_input_file(tmp_path: Path) -> None:
    input_path = tmp_path / "requirement.md"
    input_path.write_text(
        "客服用户需要工单提醒，范围只覆盖站内通知。", encoding="utf-8"
    )

    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-file",
            input_file="requirement.md",
            acceptance=("站内通知可见",),
        )
    )

    assert result.status == "ready"
    assert result.source_kind == "input-file"
    assert result.source_path == "requirement.md"
    assert result.requirement is not None
    assert result.requirement.source_kind == "input-file"
    assert result.requirement.source_path == "requirement.md"
    intake = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "requirement"
            / "req-file"
            / "requirement-intake.json"
        ).read_text(encoding="utf-8")
    )
    assert intake["source_kind"] == "input-file"
    assert intake["source_path"] == "requirement.md"


def test_start_requirement_loop_blocks_missing_input(tmp_path: Path) -> None:
    result = start_requirement_loop(RequirementStartOptions(root=tmp_path))

    assert result.status == "blocked"
    assert "requires --idea or --input-file" in result.blocker
    assert not (tmp_path / ".ai-sdlc").exists()


def test_start_requirement_loop_blocks_unsafe_loop_id(tmp_path: Path) -> None:
    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="../bad",
            idea="运营用户需要订单审批流，范围只覆盖后台人工审批。",
            acceptance=("审批节点可以配置",),
        )
    )

    assert result.status == "blocked"
    assert "Invalid requirement loop id" in result.blocker


def test_start_requirement_loop_blocks_unquoted_command_loop_id(
    tmp_path: Path,
) -> None:
    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="Q3 roadmap",
            idea="Ops users need roadmap approval.",
            acceptance=("Roadmap items can be approved.",),
        )
    )

    assert result.status == "blocked"
    assert "Invalid requirement loop id" in result.blocker
    assert "letters, digits, hyphen, and underscore" in result.blocker
    assert not (tmp_path / ".ai-sdlc").exists()


def test_freeze_requirement_loop_blocks_unsafe_loop_id(tmp_path: Path) -> None:
    result = freeze_requirement_loop(
        RequirementFreezeOptions(root=tmp_path, loop_id="../bad", yes=True)
    )

    assert result.status == "blocked"
    assert "Invalid requirement loop id" in result.blocker


def test_freeze_requirement_loop_blocks_unquoted_command_loop_id(
    tmp_path: Path,
) -> None:
    result = freeze_requirement_loop(
        RequirementFreezeOptions(root=tmp_path, loop_id="Q3 roadmap", yes=True)
    )

    assert result.status == "blocked"
    assert "Invalid requirement loop id" in result.blocker
    assert "letters, digits, hyphen, and underscore" in result.blocker


def test_freeze_requirement_loop_closes_current_loop(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-freeze",
            idea="财务用户需要付款审批，范围只覆盖国内付款。",
            acceptance=("审批通过后才能付款",),
        )
    )
    execution = _write_execution(tmp_path, "req-freeze")

    result = freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            yes=True,
            accepted_by="tester",
            review_result_file=execution.as_posix(),
        )
    )

    assert result.status == "ready"
    assert result.loop_status == "closed"
    assert result.frozen is True
    assert "design-contract" in result.next_action
    assert result.acceptance_count == 1

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-freeze"
    assert (loop_dir / "requirement-freeze.json").is_file()
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["status"] == "closed"
    assert "design-contract" in loop_run["next_action"]
    freeze = json.loads(
        (loop_dir / "requirement-freeze.json").read_text(encoding="utf-8")
    )
    assert len(freeze["review_input_digest"]) == 64
    assert freeze["review_role_ids"][0] == "requirement-quality"


def test_freeze_requirement_loop_requires_yes(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-no-yes",
            idea="运营用户需要任务提醒，范围只覆盖邮件。",
            acceptance=("邮件可以发送",),
        )
    )

    result = freeze_requirement_loop(RequirementFreezeOptions(root=tmp_path))

    assert result.status == "blocked"
    assert "--yes" in result.next_action
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / "req-no-yes"
        / "requirement-freeze.json"
    ).exists()


def test_freeze_requirement_loop_blocks_without_acceptance(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-no-acceptance",
            idea="做一个报表",
        )
    )

    result = freeze_requirement_loop(RequirementFreezeOptions(root=tmp_path, yes=True))

    assert result.status == "needs_user"
    assert result.loop_status == "needs_user"
    assert "acceptance criterion" in result.blocker
    loop_run = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "requirement"
            / "req-no-acceptance"
            / "loop-run.json"
        ).read_text(encoding="utf-8")
    )
    assert loop_run["status"] == "needs_user"


def test_freeze_requirement_loop_is_idempotent_after_closed(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-idempotent",
            idea="客服用户需要 SLA 提醒，范围只覆盖站内提醒。",
            acceptance=("SLA 超时前可以提醒",),
        )
    )
    execution = _write_execution(tmp_path, "req-idempotent")
    first = freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            yes=True,
            review_result_file=execution.as_posix(),
        )
    )
    second = freeze_requirement_loop(RequirementFreezeOptions(root=tmp_path, yes=True))

    assert first.status == "ready"
    assert second.status == "ready"
    assert second.result == "Requirement loop is already frozen."


def test_start_requirement_loop_blocks_restart_after_freeze(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-frozen-restart",
            idea="财务用户需要付款审批，范围只覆盖国内付款。",
            acceptance=("审批通过后才能付款",),
        )
    )
    execution = _write_execution(tmp_path, "req-frozen-restart")
    freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            yes=True,
            review_result_file=execution.as_posix(),
        )
    )

    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-frozen-restart",
            idea="客服用户需要 SLA 提醒，范围只覆盖站内提醒。",
            acceptance=("SLA 超时前可以提醒",),
        )
    )

    assert result.status == "blocked"
    assert "Frozen requirement loops cannot be restarted" in result.blocker
    assert "design-contract" in result.next_action

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-frozen-restart"
    intake = json.loads(
        (loop_dir / "requirement-intake.json").read_text(encoding="utf-8")
    )
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert intake["raw_text"] == "财务用户需要付款审批，范围只覆盖国内付款。"
    assert loop_run["status"] == "closed"


def test_start_requirement_loop_blocks_restart_when_loop_run_is_closed(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-closed-restart",
            idea="财务用户需要付款审批，范围只覆盖国内付款。",
            acceptance=("审批通过后才能付款",),
        )
    )
    execution = _write_execution(tmp_path, "req-closed-restart")
    freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            yes=True,
            review_result_file=execution.as_posix(),
        )
    )
    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-closed-restart"
    (loop_dir / "requirement-freeze.json").unlink()

    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-closed-restart",
            idea="客服用户需要 SLA 提醒，范围只覆盖站内提醒。",
            acceptance=("SLA 超时前可以提醒",),
        )
    )

    assert result.status == "blocked"
    assert "Frozen requirement loops cannot be restarted" in result.blocker
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["status"] == "closed"


def test_review_requirement_loop_is_read_only(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-read-only",
            idea="管理员需要通过权限控制导出审计日志，范围只覆盖 CSV。",
            acceptance=("授权管理员可以下载 CSV",),
        )
    )
    before = _tree_hashes(tmp_path)

    result = review_requirement_loop(tmp_path, "req-read-only")

    assert result.status == "ready"
    assert result.review is not None
    assert result.review.round_number == 1
    assert [role["role_id"] for role in result.review.roles] == [
        "requirement-quality",
        "security-privacy-authorization",
    ]
    assert _tree_hashes(tmp_path) == before


def test_new_requirement_freeze_requires_current_execution(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-missing-execution",
            idea="运营用户需要导出报表，范围只覆盖 CSV。",
            acceptance=("可以下载 CSV",),
        )
    )
    before = _tree_hashes(tmp_path)

    result = freeze_requirement_loop(RequirementFreezeOptions(root=tmp_path, yes=True))

    assert result.status == "blocked"
    assert "review-result-file" in result.blocker
    assert _tree_hashes(tmp_path) == before


def test_initial_needs_user_clarification_stays_in_round_one(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-clarify-round-one",
            idea="做一个报表",
        )
    )

    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-clarify-round-one",
            acceptance=("运营用户可以下载 CSV",),
        )
    )

    assert result.status == "ready"
    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-clarify-round-one"
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["current_round"] == 1
    assert len(loop_run["rounds"]) == 1


def test_reviewed_revision_uses_round_two_and_blocks_third_version(
    tmp_path: Path,
) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-two-rounds",
            idea="运营用户需要导出报表，范围只覆盖 CSV。",
            acceptance=("可以下载 CSV",),
        )
    )
    round_one = _write_execution(
        tmp_path,
        "req-two-rounds",
        severity="required",
        name="round-one.json",
    )

    revised = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-two-rounds",
            idea="运营用户需要导出报表，范围只覆盖 CSV，并返回明确错误。",
            acceptance=("可以下载 CSV", "失败时返回可判定错误"),
            review_result_file=round_one.as_posix(),
        )
    )

    assert revised.status == "ready"
    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "requirement" / "req-two-rounds"
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["current_round"] == 2
    assert len(loop_run["rounds"]) == 2

    stale_freeze = freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            yes=True,
            review_result_file=round_one.as_posix(),
        )
    )
    assert stale_freeze.status == "blocked"
    assert "stale" in stale_freeze.blocker

    before = _tree_hashes(tmp_path)
    third = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-two-rounds",
            idea="运营用户需要导出 XLSX，并返回明确错误。",
            acceptance=("可以下载 XLSX",),
        )
    )
    assert third.status == "blocked"
    assert "two substantive rounds" in third.blocker
    assert "two-round" in third.next_action
    assert "review" not in third.next_action
    assert _tree_hashes(tmp_path) == before

    round_two = _write_execution(tmp_path, "req-two-rounds", name="round-two.json")
    frozen = freeze_requirement_loop(
        RequirementFreezeOptions(
            root=tmp_path,
            yes=True,
            review_result_file=round_two.as_posix(),
        )
    )
    assert frozen.status == "ready"
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["current_round"] == 2
    assert loop_run["rounds"][1]["status"] == "closed"


def test_reviewed_revision_without_acceptance_preserves_current_criteria(
    tmp_path: Path,
) -> None:
    loop_id = "req-preserve-acceptance"
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id=loop_id,
            idea="运营用户需要导出 CSV。",
            acceptance=("仅导出所属租户数据",),
        )
    )
    execution = _write_execution(tmp_path, loop_id, severity="required")

    result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id=loop_id,
            idea="运营用户需要导出所属租户 CSV。",
            review_result_file=execution.as_posix(),
        )
    )

    assert result.status == "ready"
    intake = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "requirement"
            / loop_id
            / "requirement-intake.json"
        ).read_text(encoding="utf-8")
    )
    assert intake["acceptance_criteria"] == ["仅导出所属租户数据"]


def test_legacy_requirement_can_freeze_without_execution(tmp_path: Path) -> None:
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-legacy",
            idea="运营用户需要导出报表，范围只覆盖 CSV。",
            acceptance=("可以下载 CSV",),
        )
    )
    intake_path = (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / "req-legacy"
        / "requirement-intake.json"
    )
    payload = json.loads(intake_path.read_text(encoding="utf-8"))
    payload.pop("review_required")
    intake_path.write_text(json.dumps(payload), encoding="utf-8")

    result = freeze_requirement_loop(RequirementFreezeOptions(root=tmp_path, yes=True))

    assert result.status == "ready"
    assert result.warnings == [
        "Legacy requirement intake does not require a review execution."
    ]
