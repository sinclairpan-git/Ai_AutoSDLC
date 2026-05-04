"""ai-sdlc run command — execute the SDLC pipeline."""

from __future__ import annotations

from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.cli.beginner_guidance import (
    adapter_result_text,
    render_dry_run_open_gate_guidance,
    render_dry_run_pass_guidance,
    render_single_next_step,
)
from ai_sdlc.cli.commands import _print_reconcile_guidance
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    build_frontend_contract_runtime_attachment,
    is_frontend_contract_runtime_attachment_work_item,
)
from ai_sdlc.core.reconcile import detect_reconcile_hint
from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.integrations.ide_adapter import (
    build_adapter_governance_surface,
)
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.utils.helpers import find_project_root

console = Console()


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _stage_start_callback(stage: str, *, dry_run: bool) -> None:
    suffix = " (dry-run)" if dry_run else ""
    console.print(f"[cyan]Stage {stage}: running{suffix}[/cyan]")


def _stage_finish_callback(stage: str, result: Any) -> None:
    verdict = str(getattr(result.verdict, "value", result.verdict)).upper()
    style = {
        "PASS": "green",
        "RETRY": "yellow",
        "HALT": "red",
    }.get(verdict, "red")
    console.print(f"[{style}]Stage {stage}: {verdict}[/{style}]")


def _failed_gate_messages(result: Any) -> list[str]:
    prioritized: dict[str, int] = {}
    for check in getattr(result, "checks", []) or []:
        passed = bool(getattr(check, "passed", False))
        if passed:
            continue
        message = str(getattr(check, "message", "")).strip()
        if not message:
            continue
        name = str(getattr(check, "name", "")).strip()
        priority = 0 if name == "program_truth_audit_ready" else 1
        current = prioritized.get(message)
        if current is None or priority < current:
            prioritized[message] = priority
    return [
        message
        for message, _priority in sorted(
            prioritized.items(), key=lambda item: (item[1], item[0])
        )
    ]


def _adapter_gate_message(root: object, *, dry_run: bool) -> str | None:
    """Return a warning/blocker based on persisted ingress truth."""
    payload = build_adapter_governance_surface(root)
    if payload["adapter_ingress_state"] == "verified_loaded":
        return None
    result_zh, result_en = adapter_result_text(payload)
    if dry_run:
        return render_single_next_step(
            result_zh=result_zh,
            result_en=result_en,
            next_command=None,
            next_zh="本次 dry-run 会自动继续执行；你不需要先手动理解这些内部验证状态。",
            next_en="This dry-run will continue automatically; you do not need to interpret internal verification states first.",
        )
    target = str(payload.get("agent_target") or "codex")
    return render_single_next_step(
        result_zh=result_zh,
        result_en=result_en,
        next_command=f"ai-sdlc adapter select --agent-target {target}",
        next_zh="正式执行前先确认 AI 入口；确认后再运行完整流水线。",
        next_en="Confirm the AI entry before a mutating run, then run the full pipeline.",
    )


def _confirm_callback(stage: str, _result: Any) -> bool:
    """Prompt user for confirmation in confirm mode.

    Args:
        stage: Pipeline stage that just passed.
        _result: Gate result from the stage (unused; required by callback type).

    Returns:
        True to continue, False to pause the pipeline.
    """
    console.print(f"\n[bold cyan]Gate '{stage}' PASSED.[/bold cyan]")
    return typer.confirm("Continue to next stage?", default=True)


def run_command(
    mode: str = typer.Option("auto", help="Execution mode: auto or confirm."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Run gates without execution."
    ),
) -> None:
    """Run the SDLC pipeline from current checkpoint."""
    root = find_project_root()
    if root is None:
        console.print("[red]Not inside an AI-SDLC project.[/red]")
        raise typer.Exit(code=1)

    hint = detect_reconcile_hint(root)
    if hint is not None:
        _print_reconcile_guidance(
            hint,
            current_command="ai-sdlc run",
            blocking=True,
        )
        console.print(
            "[yellow]已停止当前运行，避免基于过时 checkpoint 继续执行。[/yellow]"
        )
        raise typer.Exit(code=1)

    gate_message = _adapter_gate_message(root, dry_run=dry_run)
    if gate_message is not None and dry_run:
        console.print(
            Panel(
                gate_message,
                title="ai-sdlc run",
                border_style="yellow",
            )
        )
    elif gate_message is not None:
        console.print(
            Panel(
                gate_message,
                title="ai-sdlc run",
                border_style="yellow",
            )
        )
        raise typer.Exit(code=1)

    runner = SDLCRunner(root)
    callback = _confirm_callback if mode == "confirm" else None
    last_result: Any | None = None

    def _record_stage_finish(stage: str, result: Any) -> None:
        nonlocal last_result
        last_result = result
        _stage_finish_callback(stage, result)

    try:
        cp = runner.run(
            mode=mode,
            dry_run=dry_run,
            on_confirm=callback,
            on_stage_start=lambda stage: _stage_start_callback(
                stage, dry_run=dry_run
            ),
            on_stage_finish=_record_stage_finish,
        )
        if (
            dry_run
            and last_result is not None
            and str(getattr(last_result.verdict, "value", last_result.verdict)).upper()
            != "PASS"
        ):
            verdict = str(
                getattr(last_result.verdict, "value", last_result.verdict)
            ).upper()
            console.print(
                "[bold yellow]"
                f"Dry-run completed with open gates. Last stage: "
                f"{cp.current_stage} ({verdict})"
                "[/bold yellow]"
            )
            for message in _failed_gate_messages(last_result)[:2]:
                console.print(f"  reason: {message}", markup=False)
            console.print("")
            console.print(render_dry_run_open_gate_guidance(_failed_gate_messages(last_result)))
        else:
            console.print(
                f"\n[bold green]Pipeline completed. Stage: {cp.current_stage}[/bold green]"
            )
            if dry_run:
                console.print("")
                console.print(render_dry_run_pass_guidance())
        _render_frontend_contract_runtime_attachment_summary(root, cp)
    except PipelineHaltError as exc:
        console.print(f"\n[bold red]Pipeline halted: {exc}[/bold red]")
        raise typer.Exit(code=2) from None


def _render_frontend_contract_runtime_attachment_summary(
    root: object,
    checkpoint: Checkpoint | None,
) -> None:
    if checkpoint is None or not is_frontend_contract_runtime_attachment_work_item(
        checkpoint
    ):
        return

    attachment = build_frontend_contract_runtime_attachment(
        root,
        checkpoint=checkpoint,
    )
    coverage_gaps = _dedupe_text_items(attachment.coverage_gaps)[:3]
    blockers = _dedupe_text_items(attachment.blockers)[:1]
    details: list[str] = []
    if coverage_gaps:
        details.append("coverage gaps: " + ", ".join(coverage_gaps))
    elif blockers:
        details.append("blockers: " + "; ".join(blockers))

    suffix = f" ({'; '.join(details)})" if details else ""
    style = "green" if attachment.status == "attached" else "yellow"
    console.print(
        f"[{style}]frontend contract runtime attachment: "
        f"{attachment.status}{suffix}[/{style}]"
    )
