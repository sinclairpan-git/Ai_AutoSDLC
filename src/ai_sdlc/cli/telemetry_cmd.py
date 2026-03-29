"""Manual telemetry recording commands."""

from __future__ import annotations

from pathlib import Path

import typer
from pydantic import ValidationError
from rich.console import Console

from ai_sdlc.telemetry.contracts import (
    Evaluation,
    Evidence,
    ScopeLevel,
    TelemetryEvent,
    Violation,
)
from ai_sdlc.telemetry.enums import (
    ActorType,
    CaptureMode,
    Confidence,
    EvaluationResult,
    EvaluationStatus,
    EvidenceStatus,
    RootCauseClass,
    SuggestedChangeLayer,
    TelemetryEventStatus,
    TraceLayer,
    ViolationRiskLevel,
    ViolationStatus,
)
from ai_sdlc.telemetry.runtime import RuntimeTelemetry
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter
from ai_sdlc.utils.helpers import find_project_root

telemetry_app = typer.Typer(help="Manual telemetry recording commands.", no_args_is_help=True)

console = Console()


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]")
        raise typer.Exit(code=1)
    return root


def _bad_parameter(exc: ValidationError) -> typer.BadParameter:
    message = "; ".join(error["msg"] for error in exc.errors())
    return typer.BadParameter(message)


def _raise_value_error(exc: ValueError) -> None:
    console.print(f"[red]Error: {exc}[/red]")
    raise typer.Exit(code=2)


def _build_writer(root: Path) -> TelemetryWriter:
    store = TelemetryStore(root)
    store.ensure_initialized()
    return TelemetryWriter(store)


@telemetry_app.command("open-session")
def open_session_command() -> None:
    """Open a manual goal session and print its session id."""
    root = _resolve_root()
    telemetry = RuntimeTelemetry(root)
    session_id = telemetry.open_session()
    console.print(session_id)


@telemetry_app.command("close-session")
def close_session_command(
    goal_session_id: str = typer.Option(..., "--goal-session-id"),
    status: str = typer.Option(
        TelemetryEventStatus.SUCCEEDED.value,
        "--status",
        help="Terminal session status.",
    ),
) -> None:
    """Close a manual goal session and print its session id."""
    root = _resolve_root()
    telemetry = RuntimeTelemetry(root)
    try:
        terminal_status = TelemetryEventStatus(status)
        session_id = telemetry.close_session(goal_session_id, status=terminal_status)
    except ValueError as exc:
        _raise_value_error(exc)
    except ValidationError as exc:  # pragma: no cover - guarded by contract tests
        raise _bad_parameter(exc) from exc
    console.print(session_id)


@telemetry_app.command("record-event")
def record_event_command(
    scope: ScopeLevel = typer.Option(..., "--scope"),
    goal_session_id: str = typer.Option(..., "--goal-session-id"),
    workflow_run_id: str | None = typer.Option(None, "--workflow-run-id"),
    step_id: str | None = typer.Option(None, "--step-id"),
    trace_layer: TraceLayer = typer.Option(
        TraceLayer.HUMAN,
        "--trace-layer",
        help="Manual trace layer for the event.",
    ),
    status: TelemetryEventStatus = typer.Option(
        TelemetryEventStatus.STARTED,
        "--status",
        help="Event status.",
    ),
    actor_type: ActorType = typer.Option(
        ActorType.HUMAN,
        "--actor-type",
        help="Who reported the event.",
    ),
    capture_mode: CaptureMode = typer.Option(
        CaptureMode.HUMAN_REPORTED,
        "--capture-mode",
        help="How the event was captured.",
    ),
    confidence: Confidence = typer.Option(
        Confidence.MEDIUM,
        "--confidence",
        help="Confidence in the record.",
    ),
) -> None:
    """Record a manual telemetry event through the canonical writer."""
    root = _resolve_root()
    try:
        event = TelemetryEvent(
            scope_level=scope,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            trace_layer=trace_layer,
            status=status,
            actor_type=actor_type,
            capture_mode=capture_mode,
            confidence=confidence,
        )
    except ValidationError as exc:
        raise _bad_parameter(exc) from exc

    telemetry = RuntimeTelemetry(root)
    try:
        telemetry.validate_manual_scope(
            scope_level=event.scope_level,
            goal_session_id=event.goal_session_id,
            workflow_run_id=event.workflow_run_id,
            step_id=event.step_id,
        )
        telemetry.validate_manual_event(
            trace_layer=event.trace_layer,
            actor_type=event.actor_type,
            capture_mode=event.capture_mode,
        )
    except ValueError as exc:
        _raise_value_error(exc)

    writer = _build_writer(root)

    writer.write_event(event)
    console.print(event.event_id)


@telemetry_app.command("record-evidence")
def record_evidence_command(
    scope: ScopeLevel = typer.Option(..., "--scope"),
    goal_session_id: str = typer.Option(..., "--goal-session-id"),
    workflow_run_id: str | None = typer.Option(None, "--workflow-run-id"),
    step_id: str | None = typer.Option(None, "--step-id"),
    status: EvidenceStatus = typer.Option(
        EvidenceStatus.AVAILABLE,
        "--status",
        help="Evidence status.",
    ),
    capture_mode: CaptureMode = typer.Option(
        CaptureMode.HUMAN_REPORTED,
        "--capture-mode",
        help="How the evidence was captured.",
    ),
    confidence: Confidence = typer.Option(
        Confidence.MEDIUM,
        "--confidence",
        help="Confidence in the record.",
    ),
    locator: str = typer.Option(..., "--locator", help="Evidence locator."),
    digest: str | None = typer.Option(None, "--digest", help="Optional evidence digest."),
) -> None:
    """Record manual evidence through the canonical writer."""
    root = _resolve_root()
    try:
        evidence = Evidence(
            scope_level=scope,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            status=status,
            capture_mode=capture_mode,
            confidence=confidence,
            locator=locator,
            digest=digest,
        )
    except ValidationError as exc:
        raise _bad_parameter(exc) from exc

    telemetry = RuntimeTelemetry(root)
    try:
        telemetry.validate_manual_scope(
            scope_level=evidence.scope_level,
            goal_session_id=evidence.goal_session_id,
            workflow_run_id=evidence.workflow_run_id,
            step_id=evidence.step_id,
        )
    except ValueError as exc:
        _raise_value_error(exc)

    writer = _build_writer(root)

    writer.write_evidence(evidence)
    console.print(evidence.evidence_id)


@telemetry_app.command("record-evaluation")
def record_evaluation_command(
    scope: ScopeLevel = typer.Option(..., "--scope"),
    goal_session_id: str = typer.Option(..., "--goal-session-id"),
    workflow_run_id: str | None = typer.Option(None, "--workflow-run-id"),
    step_id: str | None = typer.Option(None, "--step-id"),
    result: EvaluationResult = typer.Option(
        EvaluationResult.PASSED,
        "--result",
        help="Evaluation outcome.",
    ),
    status: EvaluationStatus = typer.Option(
        EvaluationStatus.PENDING,
        "--status",
        help="Evaluation status.",
    ),
    root_cause_class: RootCauseClass | None = typer.Option(
        None,
        "--root-cause-class",
        help="Optional root cause classification.",
    ),
    suggested_change_layer: SuggestedChangeLayer | None = typer.Option(
        None,
        "--suggested-change-layer",
        help="Optional suggested remediation layer.",
    ),
) -> None:
    """Record a manual evaluation through the canonical writer."""
    root = _resolve_root()
    try:
        evaluation = Evaluation(
            scope_level=scope,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            result=result,
            status=status,
            root_cause_class=root_cause_class,
            suggested_change_layer=suggested_change_layer,
        )
    except ValidationError as exc:
        raise _bad_parameter(exc) from exc

    telemetry = RuntimeTelemetry(root)
    try:
        telemetry.validate_manual_scope(
            scope_level=evaluation.scope_level,
            goal_session_id=evaluation.goal_session_id,
            workflow_run_id=evaluation.workflow_run_id,
            step_id=evaluation.step_id,
        )
    except ValueError as exc:
        _raise_value_error(exc)

    writer = _build_writer(root)
    try:
        writer.write_evaluation(evaluation)
    except ValueError as exc:
        _raise_value_error(exc)
    console.print(evaluation.evaluation_id)


@telemetry_app.command("record-violation")
def record_violation_command(
    scope: ScopeLevel = typer.Option(..., "--scope"),
    goal_session_id: str = typer.Option(..., "--goal-session-id"),
    workflow_run_id: str | None = typer.Option(None, "--workflow-run-id"),
    step_id: str | None = typer.Option(None, "--step-id"),
    status: ViolationStatus = typer.Option(
        ViolationStatus.OPEN,
        "--status",
        help="Violation status.",
    ),
    risk_level: ViolationRiskLevel = typer.Option(
        ViolationRiskLevel.MEDIUM,
        "--risk-level",
        help="Violation risk level.",
    ),
    root_cause_class: RootCauseClass | None = typer.Option(
        None,
        "--root-cause-class",
        help="Optional root cause classification.",
    ),
) -> None:
    """Record a manual violation through the canonical writer."""
    root = _resolve_root()
    try:
        violation = Violation(
            scope_level=scope,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            status=status,
            risk_level=risk_level,
            root_cause_class=root_cause_class,
        )
    except ValidationError as exc:
        raise _bad_parameter(exc) from exc

    telemetry = RuntimeTelemetry(root)
    try:
        telemetry.validate_manual_scope(
            scope_level=violation.scope_level,
            goal_session_id=violation.goal_session_id,
            workflow_run_id=violation.workflow_run_id,
            step_id=violation.step_id,
        )
    except ValueError as exc:
        _raise_value_error(exc)

    writer = _build_writer(root)
    try:
        writer.write_violation(violation)
    except ValueError as exc:
        _raise_value_error(exc)
    console.print(violation.violation_id)
