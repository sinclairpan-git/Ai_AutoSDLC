"""Verify subcommands — read-only governance checks (FR-089)."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from ai_sdlc.core.verify_constraints import build_constraint_report
from ai_sdlc.telemetry.contracts import Evidence, TelemetryEvent
from ai_sdlc.telemetry.detectors import escalate_hard_gate_violation
from ai_sdlc.telemetry.enums import (
    ActorType,
    CaptureMode,
    Confidence,
    ScopeLevel,
    TelemetryEventStatus,
    TraceLayer,
)
from ai_sdlc.telemetry.evaluators import build_verify_constraint_evaluation
from ai_sdlc.telemetry.generators import (
    constraint_report_digest,
    constraint_report_locator,
)
from ai_sdlc.telemetry.runtime import RuntimeTelemetry
from ai_sdlc.utils.helpers import find_project_root

verify_app = typer.Typer(
    help=(
        "Read-only verification. Complements `ai-sdlc doctor` (environment/PATH); "
        "this command checks governance files, checkpoint vs specs tree, and "
        "repo-local framework backlog structure when present (FR-089)."
    ),
)
console = Console()


@verify_app.command(
    "constraints",
    help=(
        "Read-only: required governance files and checkpoint/specs consistency; "
        "when tasks.md exists under feature.spec_dir, task-level acceptance must "
        "match gate decompose (SC-014); doc-first / requirements-first rule surfaces "
        "and doc-first task scope must stay aligned with design/decompose intent; "
        "for active 003 work items, the draft PRD, reviewer decision, backend "
        "delegation/fallback, and release-gate evidence surfaces must be present; "
        "when docs/framework-defect-backlog.zh-CN.md exists, its structured entry fields "
        "must be complete. Does not write checkpoint. "
        "Exit 0 if no BLOCKERs, else 1."
    ),
)
def verify_constraints(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Machine-readable report on stdout.",
    ),
) -> None:
    """Validate constitution, checkpoint spec_dir, and tasks.md AC vs SC-014 (FR-089)."""
    root = find_project_root()
    if root is None:
        msg = "Not inside an AI-SDLC project (.ai-sdlc/ not found)."
        if as_json:
            typer.echo(
                json.dumps({"ok": False, "error": msg, "blockers": [], "root": None}, indent=2)
            )
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(code=1)

    report = build_constraint_report(root)
    blockers = list(report.blockers)
    telemetry = RuntimeTelemetry(root)
    goal_session_id = telemetry.open_session()
    evaluation_event = TelemetryEvent(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=goal_session_id,
        trace_layer=TraceLayer.EVALUATION,
        actor_type=ActorType.FRAMEWORK_RUNTIME,
        capture_mode=CaptureMode.AUTO,
        confidence=Confidence.HIGH,
        status=(
            TelemetryEventStatus.FAILED
            if blockers
            else TelemetryEventStatus.SUCCEEDED
        ),
    )
    telemetry.writer.write_event(evaluation_event)

    report_digest = constraint_report_digest(report)
    report_locator = constraint_report_locator(report)
    report_evidence = Evidence(
        scope_level=ScopeLevel.SESSION,
        goal_session_id=goal_session_id,
        capture_mode=CaptureMode.AUTO,
        confidence=Confidence.HIGH,
        locator=report_locator,
        digest=report_digest,
    )
    telemetry.writer.write_evidence(report_evidence)

    evaluation = build_verify_constraint_evaluation(
        report,
        source_event=evaluation_event,
        source_evidence=report_evidence,
    )
    telemetry.writer.write_evaluation(evaluation)

    violation = escalate_hard_gate_violation(
        report,
        evaluation=evaluation,
        source_event=evaluation_event,
        source_evidence=report_evidence,
    )
    if violation is not None:
        telemetry.writer.write_violation(violation)

    telemetry.close_session(
        goal_session_id,
        status=(
            TelemetryEventStatus.FAILED
            if blockers
            else TelemetryEventStatus.SUCCEEDED
        ),
    )

    if as_json:
        typer.echo(
            json.dumps(
                {
                    "ok": len(blockers) == 0,
                    "blockers": blockers,
                    "root": str(root),
                    "verification_gate": {
                        "name": report.gate_name,
                        "source_name": report.source_name,
                        "check_objects": list(report.check_objects),
                        "coverage_gaps": list(report.coverage_gaps),
                        "release_gate": report.release_gate,
                    },
                    "telemetry": {
                        "goal_session_id": goal_session_id,
                        "event_id": evaluation_event.event_id,
                        "evidence_id": report_evidence.evidence_id,
                        "evaluation_id": evaluation.evaluation_id,
                        "violation_id": violation.violation_id if violation is not None else None,
                        "report_digest": report_digest,
                        "report_locator": report_locator,
                    },
                },
                indent=2,
            )
        )
    else:
        if blockers:
            console.print("[bold red]Constraint violations[/bold red]")
            for b in blockers:
                console.print(f"  {b}")
        else:
            console.print("[green]verify constraints: no BLOCKERs.[/green]")
            if report.release_gate is not None:
                verdict = str(report.release_gate.get("overall_verdict", "UNKNOWN"))
                console.print(f"[cyan]release gate: {verdict}[/cyan]")

    raise typer.Exit(code=1 if blockers else 0)
