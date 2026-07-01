"""Tests for the deterministic design-contract loop runtime."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.core.design_contract_loop import (
    CURRENT_DESIGN_CONTRACT_PATH,
    DesignContractCheckOptions,
    DesignContractCloseOptions,
    check_design_contract_loop,
    close_design_contract_loop,
)
from ai_sdlc.core.requirement_loop import (
    RequirementFreezeOptions,
    RequirementStartOptions,
    freeze_requirement_loop,
    start_requirement_loop,
)


def test_check_design_contract_loop_writes_passed_artifacts(tmp_path: Path) -> None:
    work_item = _write_work_item(tmp_path)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-001",
        )
    )

    assert result.status == "ready"
    assert result.loop_status == "passed"
    assert result.work_item_id == "demo-contract"
    assert result.work_item_path == "specs/demo-contract"
    assert result.blocker_count == 0
    assert result.coverage_count == 2
    assert result.design_contract is not None
    assert result.design_contract.status == "passed"
    assert result.design_contract.coverage_count == 2
    assert result.design_contract.coverage_matrix_path.endswith(
        ".ai-sdlc/loops/design-contract/dc-001/coverage-matrix.json"
    )
    assert result.design_contract.report_path.endswith(
        ".ai-sdlc/loops/design-contract/dc-001/design-contract-report.json"
    )
    assert result.next_action == "Run ai-sdlc loop design-contract close --yes."
    assert result.next_guidance.command == "ai-sdlc loop design-contract close --yes"
    assert result.next_guidance.requires_model is False
    assert result.next_guidance.writes_artifacts is True
    assert result.next_guidance.writes_code is False

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-001"
    assert (loop_dir / "loop-run.json").is_file()
    assert (loop_dir / "design-contract-input.json").is_file()
    assert (loop_dir / "coverage-matrix.json").is_file()
    assert (loop_dir / "design-contract-report.json").is_file()
    assert (loop_dir / "design-contract-report.md").is_file()
    assert (tmp_path / CURRENT_DESIGN_CONTRACT_PATH).is_file()

    report = json.loads(
        (loop_dir / "design-contract-report.json").read_text(encoding="utf-8")
    )
    assert report["artifact_kind"] == "design-contract-report"
    assert report["status"] == "passed"
    assert report["coverage_count"] == 2
    assert {item["source_id"] for item in report["coverage_items"]} == {
        "FR-DEMO-001",
        "SC-DEMO-001",
    }
    assert {
        item["source_id"]: item["covered_by"] for item in report["coverage_items"]
    } == {
        "FR-DEMO-001": ["T11"],
        "SC-DEMO-001": ["T11"],
    }
    coverage = json.loads((loop_dir / "coverage-matrix.json").read_text(encoding="utf-8"))
    assert coverage["artifact_kind"] == "coverage-matrix"
    assert coverage["created_by"] == "ai-sdlc"
    assert coverage["created_at"]
    assert coverage["ai_sdlc_version"]
    pointer = json.loads(
        (tmp_path / CURRENT_DESIGN_CONTRACT_PATH).read_text(encoding="utf-8")
    )
    assert pointer["artifact_kind"] == "current-design-contract-pointer"
    assert pointer["created_by"] == "ai-sdlc"
    assert pointer["created_at"]
    assert pointer["ai_sdlc_version"]

    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["loop_type"] == "design-contract"
    assert loop_run["status"] == "passed"
    assert loop_run["work_item_id"] == work_item.name
    contract_input = json.loads(
        (loop_dir / "design-contract-input.json").read_text(encoding="utf-8")
    )
    assert contract_input["requirement_loop_id"] == "req-current"


def test_check_design_contract_loop_dry_run_does_not_write(tmp_path: Path) -> None:
    _write_work_item(tmp_path)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-dry-run",
            dry_run=True,
        )
    )

    assert result.status == "dry_run"
    assert result.dry_run is True
    assert result.loop_status == "created"
    assert result.design_contract is not None
    assert result.design_contract.status == "created"
    assert result.design_contract.work_item_id == "demo-contract"
    assert result.design_contract.coverage_matrix_path.endswith(
        ".ai-sdlc/loops/design-contract/dc-dry-run/coverage-matrix.json"
    )
    assert result.design_contract.report_path.endswith(
        ".ai-sdlc/loops/design-contract/dc-dry-run/design-contract-report.json"
    )
    assert not (
        tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-dry-run"
    ).exists()
    assert any(artifact.kind == "loop-run" for artifact in result.artifacts)


def test_check_design_contract_loop_blocks_missing_current_requirement_loop(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, with_frozen_requirement=False)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-missing-current-requirement",
        )
    )

    assert result.status == "blocked"
    assert "frozen current requirement loop is required" in result.blocker
    assert "No current requirement loop exists" in result.blocker
    assert result.next_action == "Run ai-sdlc loop requirement start."
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "design-contract"
        / "dc-missing-current-requirement"
    ).exists()


def test_check_design_contract_loop_uses_current_frozen_requirement_by_default(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, requirement_loop_id="req-default-frozen")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-current-requirement",
        )
    )

    assert result.status == "ready"
    input_payload = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-current-requirement"
            / "design-contract-input.json"
        ).read_text(encoding="utf-8")
    )
    assert input_payload["requirement_loop_id"] == "req-default-frozen"


def test_check_design_contract_loop_blocks_unfrozen_current_requirement_loop(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, with_frozen_requirement=False)
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-current-unfrozen",
            idea="Demo users need a design contract.",
            acceptance=("Design contract can be checked.",),
        )
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-unfrozen-current-requirement",
        )
    )

    assert result.status == "blocked"
    assert result.blocker == (
        "Requirement loop req-current-unfrozen must be frozen before "
        "design-contract check."
    )
    assert result.next_action == (
        "Run ai-sdlc loop requirement freeze --loop-id req-current-unfrozen --yes."
    )


def test_check_design_contract_loop_blocks_missing_requirement_loop(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            requirement_loop_id="req-missing",
            loop_id="dc-missing-requirement",
        )
    )

    assert result.status == "blocked"
    assert "must exist and be frozen" in result.blocker
    assert result.next_action == "Run ai-sdlc loop requirement start."
    assert not (
        tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-missing-requirement"
    ).exists()


def test_check_design_contract_loop_blocks_unfrozen_requirement_loop(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            idea="需要设计合同前置验证",
            acceptance=("需求可被冻结",),
            loop_id="req-unfrozen",
        )
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            requirement_loop_id="req-unfrozen",
            loop_id="dc-unfrozen-requirement",
        )
    )

    assert result.status == "blocked"
    assert result.blocker == (
        "Requirement loop req-unfrozen must be frozen before design-contract check."
    )
    assert (
        result.next_action
        == "Run ai-sdlc loop requirement freeze --loop-id req-unfrozen --yes."
    )


def test_check_design_contract_loop_accepts_frozen_requirement_loop(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    start_result = start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            idea="需要设计合同前置验证",
            acceptance=("需求可被冻结",),
            loop_id="req-frozen",
        )
    )
    assert start_result.status == "ready"
    freeze_result = freeze_requirement_loop(
        RequirementFreezeOptions(root=tmp_path, loop_id="req-frozen", yes=True)
    )
    assert freeze_result.status == "ready"
    assert freeze_result.frozen is True

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            requirement_loop_id="req-frozen",
            loop_id="dc-frozen-requirement",
        )
    )

    assert result.status == "ready"
    input_payload = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-frozen-requirement"
            / "design-contract-input.json"
        ).read_text(encoding="utf-8")
    )
    assert input_payload["requirement_loop_id"] == "req-frozen"


def test_check_design_contract_loop_blocks_mismatched_requirement_work_item(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, with_frozen_requirement=False)
    start_requirement_loop(
        RequirementStartOptions(
            root=tmp_path,
            loop_id="req-other-work-item",
            idea="Other work item needs a design contract.",
            acceptance=("Other work item can be checked.",),
            work_item_id="other-contract",
        )
    )
    freeze_requirement_loop(
        RequirementFreezeOptions(root=tmp_path, loop_id="req-other-work-item", yes=True)
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            requirement_loop_id="req-other-work-item",
            loop_id="dc-mismatched-requirement",
        )
    )

    assert result.status == "blocked"
    assert result.blocker == (
        "Requirement loop req-other-work-item belongs to work item other-contract, "
        "but design-contract work item is demo-contract."
    )
    assert "--work-item-id demo-contract" in result.next_action


def test_check_design_contract_loop_reports_missing_coverage(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, include_task_refs=False, verification_value="")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-needs-fix",
        )
    )

    assert result.status == "needs_fix"
    assert result.loop_status == "needs_fix"
    assert result.blocker_count >= 2
    assert "Fix design-contract blockers" in result.next_action

    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-needs-fix"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "missing_coverage" in {finding["code"] for finding in report["findings"]}


def test_check_design_contract_loop_infers_generated_task_coverage(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, include_task_refs=False)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-inferred-coverage",
        )
    )

    assert result.status == "ready"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-inferred-coverage"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert {item["status"] for item in report["coverage_items"]} == {"covered"}
    assert {
        item["source_id"]: item["covered_by"] for item in report["coverage_items"]
    } == {
        "FR-DEMO-001": ["T11"],
        "SC-DEMO-001": ["T11"],
    }


def test_check_design_contract_loop_ignores_non_task_coverage_refs(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        include_task_refs=False,
        verification_value="",
        tasks_intro_extra="\n".join(
            [
                "## Deferred notes",
                "",
                "FR-DEMO-001 and SC-DEMO-001 are mentioned outside executable tasks.",
                "",
                "```markdown",
                "FR-DEMO-001 SC-DEMO-001",
                "```",
                "",
            ]
        ),
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-non-task-coverage",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-non-task-coverage"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert {item["status"] for item in report["coverage_items"]} == {"missing"}
    assert all(item["covered_by"] == [] for item in report["coverage_items"])
    assert {finding["source_id"] for finding in report["findings"]} >= {
        "FR-DEMO-001",
        "SC-DEMO-001",
    }


def test_check_design_contract_loop_ignores_trailing_non_task_coverage_refs(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        include_task_refs=False,
        verification_value="",
        tasks_tail_extra="\n".join(
            [
                "",
                "## Coverage matrix",
                "",
                "- FR-DEMO-001",
                "- SC-DEMO-001",
            ]
        ),
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-trailing-coverage",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-trailing-coverage"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert {item["status"] for item in report["coverage_items"]} == {"missing"}
    assert all(item["covered_by"] == [] for item in report["coverage_items"])


def test_check_design_contract_loop_reports_placeholders(tmp_path: Path) -> None:
    _write_work_item(tmp_path, placeholder=True)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-placeholder",
        )
    )

    assert result.status == "needs_fix"
    assert result.blocker_count >= 1
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-placeholder"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "placeholder" in {finding["code"] for finding in report["findings"]}


def test_check_design_contract_loop_accepts_filled_feature_spec_title(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, spec_title="# 功能规格：Frontend Program Demo")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-filled-feature-title",
        )
    )

    assert result.status == "ready"
    assert result.blocker_count == 0


def test_check_design_contract_loop_accepts_direct_formal_as_product_term(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        spec_title="# 功能规格：Direct Formal Work Item",
        spec_intro_extra="本功能延续 direct-formal work item 入口。",
        plan_extra="direct-formal 是本次合同覆盖的正常产品术语。",
        tasks_intro_extra="direct-formal 相关任务必须仍可进入合同检查。",
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-direct-formal-term",
        )
    )

    assert result.status == "ready"
    assert result.blocker_count == 0


def test_check_design_contract_loop_accepts_english_plan_sections(
    tmp_path: Path,
) -> None:
    work_item = _write_work_item(tmp_path)
    (work_item / "plan.md").write_text(
        "\n".join(
            [
                "# Implementation Plan",
                "",
                "## Technical Context",
                "Python runtime.",
                "## Phase Plan",
                "Phase 1.",
                "## Verification",
                "Run pytest.",
                "## Rollback",
                "Revert the commit.",
            ]
        ),
        encoding="utf-8",
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-english-plan",
        )
    )

    assert result.status == "ready"
    assert result.blocker_count == 0


def test_check_design_contract_loop_reports_unrendered_feature_spec_title(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, spec_title="# 功能规格：{{ project_name }}")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-template-feature-title",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-template-feature-title"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "placeholder" in {finding["code"] for finding in report["findings"]}


@pytest.mark.parametrize(
    "status_line",
    [
        "**状态**: 草稿",
        "**Status**: Draft",
    ],
)
def test_check_design_contract_loop_blocks_draft_status_variants(
    tmp_path: Path,
    status_line: str,
) -> None:
    _write_work_item(tmp_path, spec_status_line=status_line)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-draft-status",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-draft-status"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "draft_spec" in {finding["code"] for finding in report["findings"]}


def test_check_design_contract_loop_ignores_example_contract_ids(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        spec_intro_extra="\n".join(
            [
                "## 用户故事与示例",
                "",
                "**独立测试**：构造 `FR-EXAMPLE-001` 和 `SC-EXAMPLE-001`。",
                "",
                "```markdown",
                "- **FR-CODE-001**：代码块中的编号不能成为合同项。",
                "```",
                "",
            ]
        ),
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-ignore-examples",
        )
    )

    assert result.status == "ready"
    assert result.coverage_count == 2
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-ignore-examples"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert {item["source_id"] for item in report["coverage_items"]} == {
        "FR-DEMO-001",
        "SC-DEMO-001",
    }


def test_check_design_contract_loop_treats_exit_criteria_as_contract_section(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, success_heading="## Exit Criteria")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-exit-criteria",
        )
    )

    assert result.status == "ready"
    assert result.coverage_count == 2
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-exit-criteria"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert {item["source_id"] for item in report["coverage_items"]} == {
        "FR-DEMO-001",
        "SC-DEMO-001",
    }


def test_check_design_contract_loop_blocks_unparseable_task_sections(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, task_heading="### 工作 1.1 Check contract")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-task-sections",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-task-sections"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "task_section_gap" in {finding["code"] for finding in report["findings"]}


def test_check_design_contract_loop_accepts_generated_chinese_task_sections(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, task_heading="### 任务 1.1 Check contract")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-chinese-task-section",
        )
    )

    assert result.status == "ready"
    assert result.blocker_count == 0


def test_check_design_contract_loop_accepts_english_task_labels(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        acceptance_label="- **Acceptance Criteria**",
        verification_label="- **Verification**",
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-english-task-labels",
        )
    )

    assert result.status == "ready"
    assert result.blocker_count == 0


def test_check_design_contract_loop_ignores_p2_task_detail_gaps(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        extra_task_sections="\n".join(
            [
                "",
                "### Task 2.1 Deferred polish",
                "",
                "- **任务编号**：T12",
                "- **优先级**：P2",
                "- Backlog note without acceptance or verification details.",
            ]
        ),
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-p2-task-gap",
        )
    )

    assert result.status == "ready"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-p2-task-gap"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "task_acceptance_gap" not in {
        finding["code"] for finding in report["findings"]
    }
    assert "task_verification_gap" not in {
        finding["code"] for finding in report["findings"]
    }


def test_check_design_contract_loop_ignores_p2_task_contract_coverage(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        include_task_refs=False,
        verification_value="",
        extra_task_sections="\n".join(
            [
                "",
                "### Task 2.1 Deferred coverage note",
                "",
                "- **任务编号**：T12",
                "- **优先级**：P2",
                "- Deferred backlog mentions FR-DEMO-001 and SC-DEMO-001.",
            ]
        ),
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-p2-coverage",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-p2-coverage"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert {item["status"] for item in report["coverage_items"]} == {"missing"}
    assert all(item["covered_by"] == [] for item in report["coverage_items"])
    assert "missing_coverage" in {finding["code"] for finding in report["findings"]}


def test_check_design_contract_loop_requires_verification_command(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, verification_value="")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-empty-verification",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-empty-verification"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "task_verification_gap" in {
        finding["code"] for finding in report["findings"]
    }


def test_check_design_contract_loop_checks_plan_scope_drift(tmp_path: Path) -> None:
    _write_work_item(tmp_path, plan_extra="Touch implementation_loop.py.")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-plan-drift",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-plan-drift"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    scope_findings = [
        finding for finding in report["findings"] if finding["code"] == "scope_drift"
    ]
    assert scope_findings
    assert scope_findings[0]["path"] == "specs/demo-contract/plan.md"


def test_check_design_contract_loop_checks_local_review_scope_drift(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, plan_extra="Run ai-sdlc pr-review start.")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-local-review-drift",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-local-review-drift"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    scope_findings = [
        finding for finding in report["findings"] if finding["code"] == "scope_drift"
    ]
    assert scope_findings
    assert "ai-sdlc pr-review" in scope_findings[0]["message"]


def test_check_design_contract_loop_checks_frontend_command_scope_drift(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, plan_extra="Run ai-sdlc loop frontend-evidence check.")

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-frontend-command-drift",
        )
    )

    assert result.status == "needs_fix"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-frontend-command-drift"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    scope_findings = [
        finding for finding in report["findings"] if finding["code"] == "scope_drift"
    ]
    assert scope_findings
    assert "ai-sdlc loop frontend-evidence" in scope_findings[0]["message"]


def test_check_design_contract_loop_allows_active_work_item_scope(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        relative_path="specs/implementation-loop-runtime",
        plan_extra="Run ai-sdlc loop implementation check and touch implementation_loop.py.",
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/implementation-loop-runtime",
            loop_id="dc-active-scope",
        )
    )

    assert result.status == "ready"
    report = json.loads(
        (
            tmp_path
            / ".ai-sdlc"
            / "loops"
            / "design-contract"
            / "dc-active-scope"
            / "design-contract-report.json"
        ).read_text(encoding="utf-8")
    )
    assert "scope_drift" not in {finding["code"] for finding in report["findings"]}


def test_check_design_contract_loop_blocks_non_canonical_work_item_dir(
    tmp_path: Path,
) -> None:
    _write_work_item(
        tmp_path,
        relative_path="other/demo-contract",
        with_frozen_requirement=False,
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="other/demo-contract",
            loop_id="dc-non-canonical",
        )
    )

    assert result.status == "blocked"
    assert "canonical specs/<work-item>" in result.blocker
    assert not (tmp_path / ".ai-sdlc").exists()


def test_close_design_contract_loop_writes_close_artifact(tmp_path: Path) -> None:
    _write_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-close",
        )
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-close", yes=True)
    )

    assert result.status == "ready"
    assert result.loop_status == "closed"
    assert result.closed is True
    assert result.design_contract is not None
    assert result.design_contract.status == "closed"
    assert result.next_action == "Start implementation loop for demo-contract."
    assert result.next_guidance.safety == "no_action"
    assert result.next_guidance.writes_artifacts is False

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-close"
    assert (loop_dir / "design-contract-close.json").is_file()
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["status"] == "closed"


def test_close_design_contract_loop_revalidates_changed_docs(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-stale-close",
        )
    )
    tasks_path = tmp_path / "specs" / "demo-contract" / "tasks.md"
    tasks_path.write_text(
        tasks_path.read_text(encoding="utf-8").replace(
            "- **验证**：uv run pytest tests/unit/test_demo.py -q",
            "- **验证**：",
        ),
        encoding="utf-8",
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-stale-close", yes=True)
    )

    assert result.status == "needs_fix"
    assert result.loop_status == "needs_fix"
    assert result.closed is False
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "design-contract"
        / "dc-stale-close"
        / "design-contract-close.json"
    ).exists()

    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-stale-close"
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    report = json.loads((loop_dir / "design-contract-report.json").read_text(encoding="utf-8"))
    assert loop_run["status"] == "needs_fix"
    assert "task_verification_gap" in {
        finding["code"] for finding in report["findings"]
    }


def test_close_design_contract_loop_repeat_close_keeps_implementation_next_action(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-repeat-close",
        )
    )
    close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-repeat-close", yes=True)
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-repeat-close", yes=True)
    )

    assert result.status == "ready"
    assert result.closed is True
    assert result.loop_status == "closed"
    assert result.next_action == "Start implementation loop for demo-contract."
    assert result.next_guidance.safety == "no_action"
    assert result.next_guidance.alternatives == [
        "Start implementation loop for demo-contract."
    ]


def test_check_design_contract_loop_blocks_recheck_of_closed_loop(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-closed-recheck",
        )
    )
    close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-closed-recheck", yes=True)
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-closed-recheck",
        )
    )

    assert result.status == "blocked"
    assert "already closed" in result.blocker
    loop_dir = tmp_path / ".ai-sdlc" / "loops" / "design-contract" / "dc-closed-recheck"
    loop_run = json.loads((loop_dir / "loop-run.json").read_text(encoding="utf-8"))
    assert loop_run["status"] == "closed"


def test_check_design_contract_loop_preserves_closed_current_default_recheck(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    check_result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
        )
    )
    close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id=check_result.loop_id, yes=True)
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
        )
    )

    assert result.status == "ready"
    assert result.closed is True
    assert result.loop_id == check_result.loop_id
    assert result.loop_status == "closed"
    assert result.next_action == "Start implementation loop for demo-contract."

    pointer = json.loads(
        (tmp_path / CURRENT_DESIGN_CONTRACT_PATH).read_text(encoding="utf-8")
    )
    assert pointer["loop_id"] == check_result.loop_id


def test_check_design_contract_loop_dry_run_after_close_stays_preview(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    check_result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
        )
    )
    close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id=check_result.loop_id, yes=True)
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-dry-after-close",
            dry_run=True,
        )
    )

    assert result.status == "dry_run"
    assert result.dry_run is True
    assert result.closed is False
    assert result.loop_status == "created"
    assert result.loop_id == "dc-dry-after-close"
    assert result.next_guidance.writes_artifacts is True

    pointer = json.loads(
        (tmp_path / CURRENT_DESIGN_CONTRACT_PATH).read_text(encoding="utf-8")
    )
    assert pointer["loop_id"] == check_result.loop_id
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "design-contract"
        / "dc-dry-after-close"
    ).exists()


def test_close_design_contract_loop_requires_yes(tmp_path: Path) -> None:
    _write_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-close-needs-yes",
        )
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-close-needs-yes")
    )

    assert result.status == "blocked"
    assert "Pass --yes" in result.blocker
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "design-contract"
        / "dc-close-needs-yes"
        / "design-contract-close.json"
    ).exists()


def test_close_design_contract_loop_blocks_unresolved_contract(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path, include_task_refs=False, verification_value="")
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-close-blocked",
        )
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-close-blocked", yes=True)
    )

    assert result.status == "needs_fix"
    assert result.loop_status == "needs_fix"
    assert result.blocker_count >= 2


def test_close_design_contract_loop_blocks_non_current_explicit_loop_id(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="dc-old",
        )
    )
    _write_work_item(
        tmp_path,
        include_task_refs=False,
        relative_path="specs/current-contract",
    )
    check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/current-contract",
            loop_id="dc-current",
        )
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, loop_id="dc-old", yes=True)
    )

    assert result.status == "blocked"
    assert "Only the current design-contract loop can be closed" in result.blocker
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "loops"
        / "design-contract"
        / "dc-old"
        / "design-contract-close.json"
    ).exists()


def test_close_design_contract_loop_blocks_symlinked_current_pointer(
    tmp_path: Path,
) -> None:
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.mkdir()
    outside.joinpath("loop-run.json").write_text("{}", encoding="utf-8")
    link = tmp_path / "linked-outside"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")
    pointer_path = tmp_path / CURRENT_DESIGN_CONTRACT_PATH
    pointer_path.parent.mkdir(parents=True)
    pointer_path.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "artifact_kind": "current-design-contract-pointer",
                "loop_id": "dc-symlink",
                "loop_run_path": "linked-outside/loop-run.json",
            }
        ),
        encoding="utf-8",
    )

    result = close_design_contract_loop(
        DesignContractCloseOptions(root=tmp_path, yes=True)
    )

    assert result.status == "blocked"
    assert "must stay within project" in result.blocker


def test_check_design_contract_loop_blocks_unsafe_loop_id(tmp_path: Path) -> None:
    _write_work_item(tmp_path)

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/demo-contract",
            loop_id="../bad",
        )
    )

    assert result.status == "blocked"
    assert "Invalid design-contract loop id" in result.blocker
    assert not (tmp_path / ".ai-sdlc" / "loops" / "design-contract").exists()


def test_check_design_contract_loop_blocks_missing_work_item(tmp_path: Path) -> None:
    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            work_item="specs/missing-contract",
            loop_id="dc-missing",
        )
    )

    assert result.status == "blocked"
    assert "does not exist" in result.blocker
    assert not (tmp_path / ".ai-sdlc").exists()


def test_check_design_contract_loop_uses_checkpoint_feature_spec_dir(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    checkpoint = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(
        "\n".join(
            [
                "current_stage: execute",
                "feature:",
                "  id: demo-contract",
                "  spec_dir: specs/demo-contract",
            ]
        ),
        encoding="utf-8",
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            loop_id="dc-checkpoint-spec-dir",
        )
    )

    assert result.status == "ready"
    assert result.work_item_path == "specs/demo-contract"


def test_check_design_contract_loop_prefers_checkpoint_linked_wi_id(
    tmp_path: Path,
) -> None:
    _write_work_item(tmp_path)
    checkpoint = tmp_path / ".ai-sdlc" / "state" / "checkpoint.yml"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(
        "\n".join(
            [
                "current_stage: execute",
                "linked_plan_uri: .cursor/plans/demo.plan.md",
                "linked_wi_id: demo-contract",
            ]
        ),
        encoding="utf-8",
    )

    result = check_design_contract_loop(
        DesignContractCheckOptions(
            root=tmp_path,
            loop_id="dc-checkpoint-linked-wi",
        )
    )

    assert result.status == "ready"
    assert result.work_item_path == "specs/demo-contract"


def _write_work_item(
    root: Path,
    *,
    include_task_refs: bool = True,
    with_frozen_requirement: bool = True,
    requirement_loop_id: str = "req-current",
    placeholder: bool = False,
    relative_path: str = "specs/demo-contract",
    task_heading: str = "### Task 1.1 Check contract",
    plan_extra: str = "",
    spec_intro_extra: str = "",
    success_heading: str = "## 成功标准",
    acceptance_label: str = "- **验收标准**",
    verification_label: str = "- **验证**",
    verification_value: str = "uv run pytest tests/unit/test_demo.py -q",
    tasks_intro_extra: str = "",
    tasks_tail_extra: str = "",
    extra_task_sections: str = "",
    spec_status_line: str = "**状态**：已冻结",
    spec_title: str = "# PRD：Demo Contract",
) -> Path:
    work_item = root / relative_path
    work_item.mkdir(parents=True)
    spec_extra = "\nTODO: remove placeholder.\n" if placeholder else ""
    work_item.joinpath("spec.md").write_text(
        "\n".join(
            [
                spec_title,
                "",
                spec_status_line,
                "",
                spec_intro_extra,
                "## 需求",
                "",
                "- **FR-DEMO-001**：系统必须检查合同覆盖。",
                "",
                success_heading,
                "",
                "- **SC-DEMO-001**：合同通过后可以关闭。",
                spec_extra,
            ]
        ),
        encoding="utf-8",
    )
    work_item.joinpath("plan.md").write_text(
        "\n".join(
            [
                "# 实施计划",
                "",
                "## 技术背景",
                "Python runtime.",
                "## 阶段计划",
                "Phase 1.",
                "## 验证策略",
                "Run pytest.",
                "## 回退方式",
                "Revert the commit.",
                plan_extra,
            ]
        ),
        encoding="utf-8",
    )
    refs = "FR-DEMO-001 and SC-DEMO-001" if include_task_refs else "contract docs"
    work_item.joinpath("tasks.md").write_text(
        "\n".join(
            [
                "# 任务分解",
                "",
                tasks_intro_extra,
                task_heading,
                "",
                "- **任务编号**：T11",
                "- **优先级**：P0",
                f"{acceptance_label}：Cover {refs}.",
                f"{verification_label}：{verification_value}",
                extra_task_sections,
                tasks_tail_extra,
            ]
        ),
        encoding="utf-8",
    )
    if with_frozen_requirement:
        _ensure_frozen_requirement_loop(root, loop_id=requirement_loop_id)
    return work_item


def _ensure_frozen_requirement_loop(root: Path, *, loop_id: str) -> None:
    freeze_path = (
        root
        / ".ai-sdlc"
        / "loops"
        / "requirement"
        / loop_id
        / "requirement-freeze.json"
    )
    if freeze_path.is_file():
        return
    start_result = start_requirement_loop(
        RequirementStartOptions(
            root=root,
            loop_id=loop_id,
            idea="Demo users need a checked design contract.",
            acceptance=("The design contract can be checked before implementation.",),
        )
    )
    assert start_result.status == "ready"
    freeze_result = freeze_requirement_loop(
        RequirementFreezeOptions(root=root, loop_id=loop_id, yes=True)
    )
    assert freeze_result.frozen is True
