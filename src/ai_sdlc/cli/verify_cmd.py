"""Verify subcommands — read-only governance checks (FR-089)."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from ai_sdlc.core.verify_constraints import (
    build_constraint_report,
    build_verification_gate_context,
    build_verification_governance_bundle,
)
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
    verification_context = build_verification_gate_context(root)
    verification_sources = tuple(
        verification_context.get("verification_sources", (report.source_name,))
    )
    frontend_contract_summary = verification_context.get("frontend_contract_verification")
    frontend_runtime_attachment = verification_context.get(
        "frontend_contract_runtime_attachment"
    )
    frontend_gate_summary = verification_context.get("frontend_gate_verification")
    blockers = list(report.blockers)
    governance = build_verification_governance_bundle(
        report,
        decision_subject=f"verify:{root}",
        evidence_refs=(),
    )
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
    governance = build_verification_governance_bundle(
        report,
        decision_subject=f"verify:{root}",
        evidence_refs=(report_evidence.evidence_id,),
    )
    effective_blockers = (
        blockers
        if governance["gate_decision_payload"]["decision_result"] == "block"
        else []
    )
    advisories = list(governance.get("advisories", ()))

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
                    "ok": len(effective_blockers) == 0,
                    "blockers": effective_blockers,
                    "advisories": advisories,
                    "root": str(root),
                    "verification_gate": {
                        "name": report.gate_name,
                        "source_name": report.source_name,
                        "sources": list(verification_sources),
                        "check_objects": list(report.check_objects),
                        "coverage_gaps": list(report.coverage_gaps),
                        "release_gate": report.release_gate,
                    },
                    "frontend_contract_verification": frontend_contract_summary,
                    "frontend_contract_runtime_attachment": frontend_runtime_attachment,
                    "frontend_gate_verification": frontend_gate_summary,
                    "governance": governance,
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
        if effective_blockers:
            console.print("[bold red]Constraint violations[/bold red]")
            for b in _string_list(effective_blockers):
                console.print(f"  {b}")
        else:
            console.print("[green]verify constraints: no BLOCKERs.[/green]")
            for advisory in _string_list(advisories):
                console.print(f"[yellow]{advisory}[/yellow]")
            if report.release_gate is not None:
                verdict = str(report.release_gate.get("overall_verdict", "UNKNOWN"))
                console.print(f"[cyan]release gate: {verdict}[/cyan]")
        _render_frontend_contract_summary(frontend_contract_summary)
        _render_frontend_gate_summary(frontend_gate_summary)

    raise typer.Exit(
        code=1 if governance["gate_decision_payload"]["decision_result"] == "block" else 0
    )


def _render_frontend_contract_summary(summary: object) -> None:
    _render_frontend_summary("frontend contract verification", summary)


def _render_frontend_gate_summary(summary: object) -> None:
    _render_frontend_summary("frontend gate verification", summary)


def _render_frontend_summary(label: str, summary: object) -> None:
    if not isinstance(summary, dict):
        return

    verdict = str(summary.get("gate_verdict", "UNKNOWN")).strip() or "UNKNOWN"
    coverage_gaps = _string_list(summary.get("coverage_gaps", ()))
    blockers = _string_list(summary.get("blockers", ()))
    details: list[str] = []
    diagnostic_summary = _frontend_diagnostic_summary(summary)
    if diagnostic_summary:
        details.append(diagnostic_summary)
    if coverage_gaps:
        details.append("coverage gaps: " + ", ".join(coverage_gaps[:3]))
    elif verdict != "PASS" and blockers:
        details.append("blockers: " + "; ".join(blockers[:1]))
    suffix = f" ({'; '.join(details)})" if details else ""
    style = "green" if verdict == "PASS" else "yellow"
    console.print(f"[{style}]{label}: {verdict}{suffix}[/{style}]")
    typer.echo(f"{label}: {verdict}{suffix}")


def _string_list(value: object) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    items: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in items:
            items.append(text)
    return items


def _frontend_diagnostic_summary(summary: dict[str, object]) -> str:
    diagnostic = _frontend_diagnostic_payload(summary)
    if not diagnostic:
        return ""

    status = str(diagnostic.get("diagnostic_status", "")).strip()
    if not status:
        return ""

    projection = diagnostic.get("policy_projection", {})
    if not isinstance(projection, dict):
        projection = {}

    projection_fields: list[str] = []
    coverage_effect = str(projection.get("coverage_effect", "")).strip()
    if coverage_effect:
        projection_fields.append(f"coverage={coverage_effect}")
    report_family_member = str(projection.get("report_family_member", "")).strip()
    if report_family_member:
        projection_fields.append(f"report={report_family_member}")
    blocker_class = str(projection.get("blocker_class", "")).strip()
    if blocker_class:
        projection_fields.append(f"blocker={blocker_class}")

    if not projection_fields:
        return f"diagnostic: {status}"
    return f"diagnostic: {status}; projection: {', '.join(projection_fields)}"


def _frontend_diagnostic_payload(summary: dict[str, object]) -> dict[str, object]:
    diagnostic = summary.get("diagnostic")
    if isinstance(diagnostic, dict):
        return diagnostic

    upstream = summary.get("upstream_contract_verification")
    if not isinstance(upstream, dict):
        return {}

    diagnostic = upstream.get("diagnostic")
    if isinstance(diagnostic, dict):
        return diagnostic
    return {}
