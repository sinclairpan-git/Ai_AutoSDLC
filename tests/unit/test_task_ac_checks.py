"""Unit tests for task_ac_checks (FR-090 / SC-014, shared with DecomposeGate)."""

from __future__ import annotations

from ai_sdlc.gates.task_ac_checks import first_task_missing_acceptance


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
