"""Unit tests for task_ac_checks (FR-090 / SC-014, shared with gates)."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.gates.task_ac_checks import (
    doc_first_execute_blocker,
    first_doc_first_task_scope_violation,
    first_task_missing_acceptance,
    next_pending_task_ref,
)


def test_no_tasks_returns_none() -> None:
    assert first_task_missing_acceptance("# preamble only\n") is None


def test_first_task_missing_acceptance_detected() -> None:
    md = "### Task 1.1 — x\n- **依赖**：无\n### Task 1.2\n- **验证**：pytest\n"
    assert first_task_missing_acceptance(md) == "1.1"


def test_pass_with_yanshou() -> None:
    md = (
        "### Task 1.1\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. ok\n"
    )
    assert first_task_missing_acceptance(md) is None


def test_pass_with_verification_field() -> None:
    md = "### Task 2.0\n- **依赖**：无\n- **验证**：`pytest`\n"
    assert first_task_missing_acceptance(md) is None


def test_pass_with_standalone_ac_token() -> None:
    md = "### Task 3.0\n- **依赖**：无\n- **AC**：done when tests pass\n"
    assert first_task_missing_acceptance(md) is None


def test_doc_first_scope_violation_detected_for_code_path() -> None:
    md = (
        "### Task 6.6 — 仅文档：冻结需求\n"
        "- **产物**：`src/ai_sdlc/core/verify_constraints.py`\n"
        "- **验证**：审阅通过\n"
    )
    assert first_doc_first_task_scope_violation(md) == (
        "6.6",
        "src/ai_sdlc/core/verify_constraints.py",
    )


def test_doc_first_scope_violation_ignores_rule_markdown() -> None:
    md = (
        "### Task 6.6 — 仅文档：冻结需求\n"
        "- **产物**：`src/ai_sdlc/rules/pipeline.md`\n"
        "- **验证**：审阅通过\n"
    )
    assert first_doc_first_task_scope_violation(md) is None


def test_doc_first_execute_blocker_matches_runtime_task_id() -> None:
    md = (
        "### Task 6.44 — 先 spec-plan-tasks 后实现\n"
        "- **产物**：`specs/001-ai-sdlc-framework/tasks.md`\n"
        "- **验证**：审阅通过\n"
    )
    blocker = doc_first_execute_blocker(md, task_ref="T644")
    assert blocker is not None
    assert "Task 6.44" in blocker
    assert "design/decompose" in blocker


def test_doc_first_execute_blocker_reports_forbidden_touched_paths() -> None:
    md = (
        "### Task 6.44 — 仅需求沉淀\n"
        "- **产物**：`specs/001-ai-sdlc-framework/spec.md`\n"
        "- **验证**：审阅通过\n"
    )
    blocker = doc_first_execute_blocker(
        md,
        task_ref="6.44",
        touched_paths=("tests/unit/test_verify_constraints.py",),
    )
    assert blocker is not None
    assert "tests/unit/test_verify_constraints.py" in blocker


def test_doc_first_execute_blocker_deduplicates_forbidden_touched_paths() -> None:
    md = (
        "### Task 6.44 — 仅需求沉淀\n"
        "- **产物**：`specs/001-ai-sdlc-framework/spec.md`\n"
        "- **验证**：审阅通过\n"
    )
    blocker = doc_first_execute_blocker(
        md,
        task_ref="6.44",
        touched_paths=(
            "tests/unit/test_verify_constraints.py",
            "tests/unit/test_verify_constraints.py",
            "src/ai_sdlc/core/verify_constraints.py",
        ),
    )
    assert blocker is not None
    assert blocker.count("tests/unit/test_verify_constraints.py") == 1
    assert blocker.count("src/ai_sdlc/core/verify_constraints.py") == 1


def test_next_pending_task_ref_uses_current_batch_and_last_committed(tmp_path: Path) -> None:
    tasks_md = tmp_path / "tasks.md"
    tasks_md.write_text(
        "### Task 6.43 — 代码任务\n"
        "- **依赖**：无\n"
        "- **验收标准（AC）**：\n"
        "  1. ok\n"
        "\n"
        "### Task 6.44 — 仅文档：冻结需求\n"
        "- **依赖**：Task 6.43\n"
        "- **验收标准（AC）**：\n"
        "  1. ok\n",
        encoding="utf-8",
    )
    assert next_pending_task_ref(tasks_md, current_batch=0, last_committed_task="T643") == "T644"
