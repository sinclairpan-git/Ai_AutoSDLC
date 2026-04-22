from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
import typer
from rich.console import Console

import ai_sdlc.cli.verify_cmd as verify_cmd_module


def test_string_list_deduplicates_values() -> None:
    assert verify_cmd_module._string_list(["a", "a", "b", "  ", "b"]) == ["a", "b"]


def test_render_frontend_summary_deduplicates_coverage_gaps() -> None:
    original_console = verify_cmd_module.console
    verify_cmd_module.console = Console(width=200, force_terminal=False)
    try:
        with verify_cmd_module.console.capture() as capture:
            verify_cmd_module._render_frontend_summary(
                "frontend contract verification",
                {
                    "gate_verdict": "RETRY",
                    "coverage_gaps": [
                        "frontend_contract_runtime_scope",
                        "frontend_contract_runtime_scope",
                        "frontend_gate_policy_artifacts",
                    ],
                    "blockers": [],
                },
            )
        output = capture.get()
    finally:
        verify_cmd_module.console = original_console

    assert output.count("frontend_contract_runtime_scope") == 1
    assert output.count("frontend_gate_policy_artifacts") == 1


def test_verify_constraints_terminal_deduplicates_blockers_and_advisories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_console = verify_cmd_module.console
    verify_cmd_module.console = Console(width=200, force_terminal=False)

    class _FakeWriter:
        def write_event(self, _event) -> None:
            pass

        def write_evidence(self, _evidence) -> None:
            pass

        def write_evaluation(self, _evaluation) -> None:
            pass

        def write_violation(self, _violation) -> None:
            pass

    class _FakeRuntimeTelemetry:
        def __init__(self, root: Path) -> None:
            assert root == tmp_path
            self.writer = _FakeWriter()

        def open_session(self) -> str:
            return "gs_test_session"

        def close_session(self, goal_session_id: str, status) -> None:
            assert goal_session_id == "gs_test_session"

    report = SimpleNamespace(
        blockers=("duplicate blocker", "duplicate blocker"),
        source_name="verify constraints",
        gate_name="verification",
        check_objects=(),
        coverage_gaps=(),
        release_gate=None,
    )

    monkeypatch.setattr(verify_cmd_module, "find_project_root", lambda: tmp_path)
    monkeypatch.setattr(verify_cmd_module, "build_constraint_report", lambda root: report)
    monkeypatch.setattr(
        verify_cmd_module,
        "build_verification_gate_context",
        lambda root: {},
    )
    monkeypatch.setattr(
        verify_cmd_module,
        "build_verification_governance_bundle",
        lambda *_args, **_kwargs: {
            "gate_decision_payload": {"decision_result": "block"},
            "advisories": ["duplicate advisory", "duplicate advisory"],
        },
    )
    monkeypatch.setattr(verify_cmd_module, "RuntimeTelemetry", _FakeRuntimeTelemetry)
    monkeypatch.setattr(
        verify_cmd_module,
        "TelemetryEvent",
        lambda **kwargs: SimpleNamespace(event_id="ev_test"),
    )
    monkeypatch.setattr(
        verify_cmd_module,
        "Evidence",
        lambda **kwargs: SimpleNamespace(evidence_id="evidence_test"),
    )
    monkeypatch.setattr(
        verify_cmd_module,
        "build_verify_constraint_evaluation",
        lambda *_args, **_kwargs: SimpleNamespace(),
    )
    monkeypatch.setattr(verify_cmd_module, "constraint_report_digest", lambda report: "digest")
    monkeypatch.setattr(verify_cmd_module, "constraint_report_locator", lambda report: "locator")
    monkeypatch.setattr(
        verify_cmd_module,
        "escalate_hard_gate_violation",
        lambda *_args, **_kwargs: None,
    )

    try:
        with verify_cmd_module.console.capture() as capture, pytest.raises(
            typer.Exit
        ) as exc_info:
            verify_cmd_module.verify_constraints(as_json=False)
        output = capture.get()
    finally:
        verify_cmd_module.console = original_console

    assert exc_info.value.exit_code == 1
    assert output.count("duplicate blocker") == 1
    assert output.count("duplicate advisory") == 0


def test_verify_constraints_terminal_deduplicates_advisories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_console = verify_cmd_module.console
    verify_cmd_module.console = Console(width=200, force_terminal=False)

    class _FakeWriter:
        def write_event(self, _event) -> None:
            pass

        def write_evidence(self, _evidence) -> None:
            pass

        def write_evaluation(self, _evaluation) -> None:
            pass

        def write_violation(self, _violation) -> None:
            pass

    class _FakeRuntimeTelemetry:
        def __init__(self, root: Path) -> None:
            assert root == tmp_path
            self.writer = _FakeWriter()

        def open_session(self) -> str:
            return "gs_test_session"

        def close_session(self, goal_session_id: str, status) -> None:
            assert goal_session_id == "gs_test_session"

    report = SimpleNamespace(
        blockers=(),
        source_name="verify constraints",
        gate_name="verification",
        check_objects=(),
        coverage_gaps=(),
        release_gate=None,
    )

    monkeypatch.setattr(verify_cmd_module, "find_project_root", lambda: tmp_path)
    monkeypatch.setattr(verify_cmd_module, "build_constraint_report", lambda root: report)
    monkeypatch.setattr(
        verify_cmd_module,
        "build_verification_gate_context",
        lambda root: {},
    )
    monkeypatch.setattr(
        verify_cmd_module,
        "build_verification_governance_bundle",
        lambda *_args, **_kwargs: {
            "gate_decision_payload": {"decision_result": "allow"},
            "advisories": ["duplicate advisory", "duplicate advisory"],
        },
    )
    monkeypatch.setattr(verify_cmd_module, "RuntimeTelemetry", _FakeRuntimeTelemetry)
    monkeypatch.setattr(
        verify_cmd_module,
        "TelemetryEvent",
        lambda **kwargs: SimpleNamespace(event_id="ev_test"),
    )
    monkeypatch.setattr(
        verify_cmd_module,
        "Evidence",
        lambda **kwargs: SimpleNamespace(evidence_id="evidence_test"),
    )
    monkeypatch.setattr(
        verify_cmd_module,
        "build_verify_constraint_evaluation",
        lambda *_args, **_kwargs: SimpleNamespace(),
    )
    monkeypatch.setattr(verify_cmd_module, "constraint_report_digest", lambda report: "digest")
    monkeypatch.setattr(verify_cmd_module, "constraint_report_locator", lambda report: "locator")
    monkeypatch.setattr(
        verify_cmd_module,
        "escalate_hard_gate_violation",
        lambda *_args, **_kwargs: None,
    )

    try:
        with verify_cmd_module.console.capture() as capture, pytest.raises(
            typer.Exit
        ) as exc_info:
            verify_cmd_module.verify_constraints(as_json=False)
        output = capture.get()
    finally:
        verify_cmd_module.console = original_console

    assert exc_info.value.exit_code == 0
    assert output.count("duplicate advisory") == 1
