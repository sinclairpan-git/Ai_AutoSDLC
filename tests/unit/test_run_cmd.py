from __future__ import annotations

from types import SimpleNamespace

import ai_sdlc.cli.run_cmd as run_cmd_module
from ai_sdlc.cli.run_cmd import _failed_gate_messages


def test_failed_gate_messages_prioritizes_program_truth_audit_reason() -> None:
    result = SimpleNamespace(
        checks=[
            SimpleNamespace(
                name="final_tests_passed",
                passed=False,
                message="Final tests did not pass",
            ),
            SimpleNamespace(
                name="program_truth_audit_ready",
                passed=False,
                message="state=blocked; truth audit failed",
            ),
            SimpleNamespace(
                name="all_tasks_complete",
                passed=False,
                message="Not all tasks are completed",
            ),
        ]
    )

    assert _failed_gate_messages(result) == [
        "state=blocked; truth audit failed",
        "Final tests did not pass",
        "Not all tasks are completed",
    ]


def test_failed_gate_messages_deduplicates_same_message_across_checks() -> None:
    result = SimpleNamespace(
        checks=[
            SimpleNamespace(
                name="final_tests_passed",
                passed=False,
                message="same reason",
            ),
            SimpleNamespace(
                name="program_truth_audit_ready",
                passed=False,
                message="same reason",
            ),
            SimpleNamespace(
                name="all_tasks_complete",
                passed=False,
                message="another reason",
            ),
        ]
    )

    assert _failed_gate_messages(result) == [
        "same reason",
        "another reason",
    ]


def test_runtime_attachment_summary_deduplicates_gap_and_blocker_text() -> None:
    checkpoint = SimpleNamespace()

    original_contract_check = run_cmd_module.is_frontend_contract_runtime_attachment_work_item
    original_builder = run_cmd_module.build_frontend_contract_runtime_attachment
    try:
        run_cmd_module.is_frontend_contract_runtime_attachment_work_item = lambda _checkpoint: True
        run_cmd_module.build_frontend_contract_runtime_attachment = lambda root, checkpoint: SimpleNamespace(
            status="missing",
            coverage_gaps=(
                "frontend_contract_observations",
                "frontend_contract_observations",
                "frontend_gate_policy_artifacts",
            ),
            blockers=(
                "BLOCKER: frontend contract observations unavailable",
                "BLOCKER: frontend contract observations unavailable",
            ),
        )

        with run_cmd_module.console.capture() as capture:
            run_cmd_module._render_frontend_contract_runtime_attachment_summary(
                object(),
                checkpoint,
            )

        output = capture.get()
        assert output.count("frontend_contract_observations") == 1
        assert output.count("frontend_gate_policy_artifacts") == 1
        assert output.count("frontend contract observations unavailable") == 0
    finally:
        run_cmd_module.is_frontend_contract_runtime_attachment_work_item = original_contract_check
        run_cmd_module.build_frontend_contract_runtime_attachment = original_builder
