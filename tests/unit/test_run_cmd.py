from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

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


def test_runtime_attachment_summary_deduplicates_gap_and_blocker_text(
    tmp_path: Path,
) -> None:
    checkpoint = SimpleNamespace()
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "ai-sdlc"\n', encoding="utf-8"
    )
    package_init = tmp_path / "src" / "ai_sdlc" / "__init__.py"
    package_init.parent.mkdir(parents=True)
    package_init.write_text("", encoding="utf-8")

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
                tmp_path,
                checkpoint,
            )

        output = capture.get()
        assert output.count("frontend_contract_observations") == 1
        assert output.count("frontend_gate_policy_artifacts") == 1
        assert output.count("frontend contract observations unavailable") == 0
    finally:
        run_cmd_module.is_frontend_contract_runtime_attachment_work_item = original_contract_check
        run_cmd_module.build_frontend_contract_runtime_attachment = original_builder


@pytest.mark.parametrize("identity", ("consumer", "xor"))
def test_runtime_attachment_summary_skips_non_framework_014_without_building(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    identity: str,
) -> None:
    if identity == "xor":
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "ai-sdlc"\n', encoding="utf-8"
        )
    checkpoint = SimpleNamespace(
        feature=SimpleNamespace(
            id="014-runtime-attachment",
            spec_dir="specs/014-runtime-attachment",
        )
    )
    calls: list[Path] = []

    def build_missing(root: Path, checkpoint: object) -> SimpleNamespace:
        calls.append(root)
        return SimpleNamespace(
            status="missing_artifact",
            coverage_gaps=("frontend_contract_observations",),
            blockers=(),
        )

    monkeypatch.setattr(
        run_cmd_module, "build_frontend_contract_runtime_attachment", build_missing
    )

    with run_cmd_module.console.capture() as capture:
        run_cmd_module._render_frontend_contract_runtime_attachment_summary(
            tmp_path, checkpoint
        )

    assert calls == []
    assert "frontend contract runtime attachment" not in capture.get()


def test_agentops_verification_metrics_count_only_test_stage_checks() -> None:
    stage_results = [
        (
            "refine",
            SimpleNamespace(
                checks=[
                    SimpleNamespace(name="prd", passed=False),
                    SimpleNamespace(name="scope", passed=True),
                ]
            ),
        ),
        (
            "verify",
            SimpleNamespace(
                checks=[
                    SimpleNamespace(name="unit", passed=True),
                    SimpleNamespace(name="lint", passed=False),
                ]
            ),
        ),
        (
            "close",
            SimpleNamespace(checks=[SimpleNamespace(name="summary", passed=False)]),
        ),
    ]

    assert run_cmd_module._agentops_total_check_count(stage_results) == 2
    assert run_cmd_module._agentops_total_failed_check_count(stage_results) == 1
