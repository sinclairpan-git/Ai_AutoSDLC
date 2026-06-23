"""ai-sdlc run command — execute the SDLC pipeline."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.cli.beginner_guidance import (
    render_dry_run_open_gate_guidance,
    render_dry_run_pass_guidance,
    render_mutating_run_blocker,
)
from ai_sdlc.cli.commands import _print_reconcile_guidance
from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.agentops_bridge import (
    ENTERPRISE_PROFILE_ENV,
    AgentOpsIdentity,
    AgentOpsReceipt,
    AgentOpsRuntimeContext,
    build_agentops_runtime_batch,
    build_artifact_fact,
    build_gate_fact,
    build_model_span_fact,
    build_stage_fact,
    build_verification_fact,
    deliver_agentops_outbox,
    enterprise_profile_paths,
    load_agentops_ingestion_config,
    persist_agentops_outbox_batch,
)
from ai_sdlc.core.executable_task import parse_executable_tasks
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    build_frontend_contract_runtime_attachment,
    is_frontend_contract_runtime_attachment_work_item,
)
from ai_sdlc.core.plan_check import git_changed_paths
from ai_sdlc.core.reconcile import detect_reconcile_hint
from ai_sdlc.core.runner import PipelineHaltError, SDLCRunner
from ai_sdlc.integrations.ide_adapter import (
    build_adapter_governance_surface,
)
from ai_sdlc.models.state import Checkpoint
from ai_sdlc.utils.helpers import find_project_root, now_iso

console = Console()

_AGENTOPS_DIAGNOSTIC_ITEM_STATES = {"stale", "rejected", "dlq"}
_AGENTOPS_REPORTING_STAGES = (
    "refine",
    "design",
    "decompose",
    "execute",
    "test",
    "review",
    "close",
    "merge_release",
)


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _agentops_receipt_diagnostic_lines(
    receipt: AgentOpsReceipt,
    receipt_path: Path | None,
) -> list[str]:
    lines: list[str] = []
    if receipt_path is not None:
        lines.append(f"AgentOps receipt summary: {receipt_path}")
    fallback_item: dict[str, Any] | None = None
    selected_item: dict[str, Any] | None = None
    for item in receipt.item_results:
        state = str(item.get("state") or item.get("status") or "").strip()
        code = str(item.get("code", "")).strip()
        message = str(item.get("message", "")).strip()
        guidance = str(
            item.get("retry_guidance") or item.get("guidance") or ""
        ).strip()
        if state.lower() in _AGENTOPS_DIAGNOSTIC_ITEM_STATES:
            selected_item = item
            break
        if fallback_item is None and (code or message or guidance):
            fallback_item = item
    item = selected_item or fallback_item
    if item is not None:
        state = str(item.get("state") or item.get("status") or "").strip()
        code = str(item.get("code", "")).strip()
        message = str(item.get("message", "")).strip()
        guidance = str(
            item.get("retry_guidance") or item.get("guidance") or ""
        ).strip()
        details = [
            value
            for value in (
                f"state={state}" if state else "",
                f"code={code}" if code else "",
                f"message={message}" if message else "",
            )
            if value
        ]
        if details:
            lines.append("AgentOps receipt diagnostic item: " + " ".join(details))
        if guidance:
            lines.append(f"AgentOps receipt retry guidance: {guidance}")
    return lines


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
    """Return a warning/blocker based on persisted adapter readiness."""
    payload = build_adapter_governance_surface(root)
    ingress_state = str(payload["adapter_ingress_state"])
    if ingress_state == "verified_loaded":
        return None
    if ingress_state == "materialized":
        return None
    if dry_run:
        return None
    return render_mutating_run_blocker(payload)


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
    stage_results: list[tuple[str, Any]] = []

    def _record_stage_finish(stage: str, result: Any) -> None:
        nonlocal last_result
        last_result = result
        stage_results.append((stage, result))
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
        _flush_agentops_runtime_report(root, cp, stage_results, dry_run=dry_run)
    except PipelineHaltError as exc:
        _record_halt_result(stage_results, exc)
        cp = load_checkpoint(root, warn=False)
        console.print(f"\n[bold red]Pipeline halted: {exc}[/bold red]")
        if cp is not None:
            _flush_agentops_runtime_report(root, cp, stage_results, dry_run=dry_run)
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


def _flush_agentops_runtime_report(
    root: object,
    checkpoint: Checkpoint,
    stage_results: list[tuple[str, Any]],
    *,
    dry_run: bool,
) -> None:
    if not stage_results:
        return
    try:
        agentops_config = load_agentops_ingestion_config(Path(root))
    except Exception as exc:
        if _agentops_config_load_failure_is_required():
            console.print(f"[yellow]AgentOps report pending: {exc}[/yellow]")
            raise typer.Exit(code=2) from None
        if _agentops_verbose_output():
            console.print(f"[yellow]AgentOps report pending: {exc}[/yellow]")
        return
    if not agentops_config.enabled:
        return
    timestamp = now_iso().replace("+00:00", "Z")
    feature_id = checkpoint.feature.id if checkpoint.feature else "unknown"
    mode_label = "dry_run" if dry_run else "run"
    invocation_id = uuid4().hex[:12]
    run_id = (
        f"run_{_safe_agentops_id(feature_id)}_"
        f"{mode_label}_{_safe_agentops_id(timestamp)}_{invocation_id}"
    )
    context = AgentOpsRuntimeContext(
        session_id=f"session_{run_id}",
        run_id=run_id,
        trace_id=f"trace_{run_id}",
        stage_name=checkpoint.current_stage,
        timestamp=timestamp,
        report_type=_agentops_report_type(dry_run=dry_run),
    )
    identity = _agentops_identity_from_env()
    workitem = checkpoint.linked_wi_id or feature_id
    changed_paths = _agentops_changed_paths(root)
    allowed_paths = _agentops_workitem_scope(root, workitem)
    facts = []
    summary_ref = f"vault://sdlc/{run_id}/runtime_report_summary"
    run_passed = all(_agentops_status(result) == "passed" for _, result in stage_results)
    facts.append(
        build_model_span_fact(
            span_id="model_ai_sdlc_runtime_summary",
            operation_name="ai_sdlc.model.summary_only_coordination",
            status_code="ok" if run_passed else "error",
            input_ref=f"vault://sdlc/{run_id}/run_context_summary",
            output_ref=summary_ref,
            stage_name="run",
            workitem=workitem,
            executable_task_id="pipeline_run",
            task_title="AI-SDLC runtime summary",
            token_usage=_agentops_token_usage_summary(),
            cost_estimate=_agentops_cost_estimate_summary(),
        )
    )
    git_summary = _agentops_git_summary(root)
    observed_stage_names: set[str] = set()
    for stage, result in stage_results:
        public_stage_name = _agentops_public_stage_name(stage)
        observed_stage_names.add(public_stage_name)
        rule_results = _agentops_rule_results(result)
        status = _agentops_status(result)
        failed_conditions = _agentops_failed_conditions(rule_results)
        blocking_reason = _agentops_blocking_reason(rule_results)
        metrics = _agentops_engineering_metrics(
            result,
            stage=stage,
            git_summary=git_summary,
        )
        facts.append(
            build_stage_fact(
                stage_name=public_stage_name,
                status=status,
                workitem=workitem,
                executable_task_id=f"pipeline_{stage}",
                task_guard_state="diagnostic",
                task_title=f"Pipeline {stage} stage",
                adapter_diagnostic_state=_agentops_adapter_diagnostic_state(root),
                extra={
                    "parent_span_id": "model_ai_sdlc_runtime_summary",
                    "observed_stage": True,
                    "blocking_reason": blocking_reason,
                    "failure_reason": blocking_reason if status != "passed" else "",
                    "failed_conditions": failed_conditions,
                    "open_gates": failed_conditions if status != "passed" else [],
                    "expected_result": "stage gate passes",
                    "actual_result_summary": _agentops_actual_result_summary(
                        status=status,
                        blocking_reason=blocking_reason,
                        failed_conditions=failed_conditions,
                    ),
                    "retry_guidance": _agentops_retry_guidance(failed_conditions),
                    "next_action": _agentops_next_action(failed_conditions),
                    **metrics,
                },
            )
        )
        facts.append(
            build_gate_fact(
                gate_id=stage,
                status=status,
                workitem=workitem,
                executable_task_id=f"pipeline_{stage}",
                task_guard_state="diagnostic",
                stage_name=public_stage_name,
                task_title=f"Pipeline {stage} gate",
                changed_paths=changed_paths,
                allowed_paths=allowed_paths,
                forbidden_paths=(),
                guard_result="diagnostic",
                blocking_reason=blocking_reason,
                blocking=status != "passed",
                rule_results=rule_results,
            )
        )
    for stage in _AGENTOPS_REPORTING_STAGES:
        if stage in observed_stage_names:
            continue
        facts.append(
            build_stage_fact(
                stage_name=stage,
                status="emitted",
                workitem=workitem,
                executable_task_id=f"pipeline_{stage}",
                task_guard_state="diagnostic",
                task_title=f"Pipeline {stage} stage",
                adapter_diagnostic_state=_agentops_adapter_diagnostic_state(root),
                extra={
                    "parent_span_id": "model_ai_sdlc_runtime_summary",
                    "observed_stage": False,
                    "stage_observation_state": "not_reached",
                    "actual_result_summary": "stage not reached in this run",
                    "next_action": "",
                    **_agentops_idle_engineering_metrics(git_summary),
                },
            )
        )
    facts.extend(
        [
            build_verification_fact(
                verification_id="ai_sdlc_run",
                status="passed" if run_passed else "failed",
                workitem=workitem,
                executable_task_id="pipeline_run",
                task_guard_state="diagnostic",
                command_or_job="ai-sdlc run",
                freshness="fresh",
                stage_name="test",
                test_count=_agentops_total_check_count(stage_results),
                failed_test_count=_agentops_total_failed_check_count(stage_results),
            ),
            build_artifact_fact(
                artifact_ref=summary_ref,
                payload_hash=_agentops_summary_hash(
                    run_id=run_id,
                    changed_paths=changed_paths,
                    allowed_paths=allowed_paths,
                ),
                workitem=workitem,
                executable_task_id="pipeline_run",
                task_guard_state="diagnostic",
            ),
        ]
    )
    batch = build_agentops_runtime_batch(
        outbox_id=f"outbox_{run_id}",
        batch_id=f"batch_{run_id}",
        context=context,
        identity=identity,
        facts=facts,
    )
    try:
        persist_agentops_outbox_batch(root, batch)
        result = deliver_agentops_outbox(
            root,
            outbox_id=str(batch["outbox_id"]),
            config=agentops_config,
            dry_run=dry_run,
        )
    except Exception as exc:
        if agentops_config.required:
            console.print(f"[yellow]AgentOps report pending: {exc}[/yellow]")
            raise typer.Exit(code=2) from None
        if _agentops_verbose_output():
            console.print(f"[yellow]AgentOps report pending: {exc}[/yellow]")
        return
    if result.receipt is not None:
        if result.receipt.has_diagnostics:
            console.print(
                "[yellow]AgentOps report delivered with diagnostics: "
                f"{result.receipt.outbox_state} "
                f"accepted={result.receipt.accepted_count} "
                f"deduplicated={result.receipt.deduplicated_count} "
                f"stale={result.receipt.stale_count} "
                f"rejected={result.receipt.rejected_count} "
                f"dlq={result.receipt.dlq_count}[/yellow]"
            )
            for line in _agentops_receipt_diagnostic_lines(
                result.receipt,
                result.receipt_path,
            ):
                console.print(f"[yellow]{line}[/yellow]")
            if agentops_config.required:
                raise typer.Exit(code=2)
        else:
            console.print(
                "[green]AgentOps report delivered: "
                f"{result.receipt.outbox_state} "
                f"accepted={result.receipt.accepted_count} "
                f"deduplicated={result.receipt.deduplicated_count}[/green]"
            )
    elif result.dry_run and result.config_ready:
        console.print("[yellow]AgentOps report dry-run: delivery skipped[/yellow]")
    elif result.diagnostic is not None:
        if agentops_config.required:
            console.print(
                "[yellow]AgentOps report pending: "
                f"{result.diagnostic.reason_code}[/yellow]"
            )
            raise typer.Exit(code=2)
        if _agentops_verbose_output():
            console.print(
                "[yellow]AgentOps report pending: "
                f"{result.diagnostic.reason_code}[/yellow]"
            )


def _agentops_config_load_failure_is_required() -> bool:
    reporting_mode = os.environ.get("AGENTOPS_REPORTING_MODE", "").strip().lower()
    if reporting_mode == "required":
        return True
    if os.environ.get(ENTERPRISE_PROFILE_ENV, "").strip():
        return True
    try:
        return any(path.is_file() for path in enterprise_profile_paths())
    except OSError:
        return True


def _agentops_verbose_output() -> bool:
    value = os.environ.get("AI_SDLC_AGENTOPS_VERBOSE", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _record_halt_result(
    stage_results: list[tuple[str, Any]],
    exc: PipelineHaltError,
) -> None:
    stage = str(getattr(exc, "stage", "") or "")
    result = getattr(exc, "result", None)
    if not stage or result is None:
        return
    if any(
        existing_stage == stage and existing_result is result
        for existing_stage, existing_result in stage_results
    ):
        return
    stage_results.append((stage, result))


def _agentops_identity_from_env() -> AgentOpsIdentity:
    return AgentOpsIdentity.ops_direct(
        producer_id=_agentops_env("AGENTOPS_PRODUCER_ID", "ai-sdlc-local"),
        runtime_id=_agentops_env("AGENTOPS_RUNTIME_ID", "ai-sdlc-cli"),
        credential_id=_agentops_env("AGENTOPS_CREDENTIAL_ID", "local-agentops-runtime"),
        key_id=_agentops_env("AGENTOPS_KEY_ID", "local-agentops-runtime-key"),
    )


def _agentops_env(name: str, default: str) -> str:
    return os.getenv(name, "").strip() or default


def _agentops_changed_paths(root: object) -> list[str]:
    try:
        return git_changed_paths(Path(root))
    except Exception:
        return []


def _agentops_workitem_scope(root: object, workitem: str) -> list[str]:
    tasks_path = Path(root) / "specs" / workitem / "tasks.md"
    if not tasks_path.is_file():
        return []
    try:
        parsed = parse_executable_tasks(tasks_path)
    except Exception:
        return []
    paths: list[str] = []
    for task in parsed.tasks:
        paths.extend(task.scope)
    return _dedupe_text_items(paths)


def _agentops_summary_hash(
    *,
    run_id: str,
    changed_paths: list[str],
    allowed_paths: list[str],
) -> str:
    raw = "\n".join([run_id, *changed_paths, *allowed_paths]).encode("utf-8")
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def _agentops_report_type(*, dry_run: bool) -> str:
    requested = os.getenv("AGENTOPS_REPORT_TYPE", "").strip()
    if requested in {"real_run", "dry_run_retry", "readiness_fixture", "live_smoke"}:
        return requested
    return "dry_run_retry" if dry_run else "real_run"


def _agentops_public_stage_name(stage: str) -> str:
    if stage in {"verify", "verification"}:
        return "test"
    return stage


def _agentops_adapter_diagnostic_state(root: object) -> str:
    try:
        payload = build_adapter_governance_surface(root)
    except Exception:
        return ""
    return str(payload.get("adapter_ingress_state") or "")


def _agentops_git_summary(root: object) -> dict[str, str]:
    return {
        "commit_sha": _agentops_git_value(root, ("rev-parse", "HEAD")),
        "branch": _agentops_git_value(root, ("branch", "--show-current")),
        "pr_number": os.getenv("AGENTOPS_PR_NUMBER", "").strip(),
    }


def _agentops_git_value(root: object, args: tuple[str, ...]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=Path(root),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def _agentops_engineering_metrics(
    result: Any,
    *,
    stage: str,
    git_summary: dict[str, str],
) -> dict[str, object]:
    checks = list(getattr(result, "checks", []) or [])
    failed_count = sum(1 for check in checks if not bool(getattr(check, "passed", False)))
    is_test_stage = _agentops_public_stage_name(stage) == "test"
    return {
        "test_count": len(checks) if is_test_stage else 0,
        "failed_test_count": failed_count if is_test_stage else 0,
        "ci_check_name": os.getenv("AGENTOPS_CI_CHECK_NAME", "").strip(),
        "ci_result": os.getenv("AGENTOPS_CI_RESULT", "").strip(),
        "review_findings_count": _agentops_int_env("AGENTOPS_REVIEW_FINDINGS_COUNT"),
        "retry_count": int(getattr(result, "retry_count", 0) or 0),
        "duration_ms": 0,
        "token_usage": _agentops_token_usage_summary(),
        "cost_estimate": _agentops_cost_estimate_summary(),
        **git_summary,
    }


def _agentops_idle_engineering_metrics(git_summary: dict[str, str]) -> dict[str, object]:
    return {
        "test_count": 0,
        "failed_test_count": 0,
        "ci_check_name": os.getenv("AGENTOPS_CI_CHECK_NAME", "").strip(),
        "ci_result": os.getenv("AGENTOPS_CI_RESULT", "").strip(),
        "review_findings_count": _agentops_int_env("AGENTOPS_REVIEW_FINDINGS_COUNT"),
        "retry_count": 0,
        "duration_ms": 0,
        "token_usage": _agentops_token_usage_summary(),
        "cost_estimate": _agentops_cost_estimate_summary(),
        **git_summary,
    }


def _agentops_token_usage_summary() -> dict[str, int]:
    return {
        "input_tokens": _agentops_int_env("AGENTOPS_INPUT_TOKENS"),
        "output_tokens": _agentops_int_env("AGENTOPS_OUTPUT_TOKENS"),
        "total_tokens": _agentops_int_env("AGENTOPS_TOTAL_TOKENS"),
    }


def _agentops_cost_estimate_summary() -> dict[str, object]:
    raw_amount = os.getenv("AGENTOPS_COST_ESTIMATE_USD", "").strip()
    try:
        amount = float(raw_amount) if raw_amount else 0.0
    except ValueError:
        amount = 0.0
    return {
        "amount": amount,
        "currency": "USD",
        "source": "summary_only_env" if raw_amount else "",
    }


def _agentops_int_env(name: str) -> int:
    raw = os.getenv(name, "").strip()
    try:
        value = int(raw)
    except ValueError:
        return 0
    return value if value >= 0 else 0


def _agentops_rule_results(result: Any) -> list[dict[str, object]]:
    return [
        {
            "name": str(getattr(check, "name", "")),
            "passed": bool(getattr(check, "passed", False)),
            "message": str(getattr(check, "message", "")),
        }
        for check in getattr(result, "checks", []) or []
    ]


def _agentops_failed_conditions(rule_results: list[dict[str, object]]) -> list[str]:
    conditions: list[str] = []
    for item in rule_results:
        if bool(item.get("passed")):
            continue
        name = str(item.get("name") or item.get("message") or "").strip()
        condition = _safe_agentops_id(name).lower()
        if condition and condition not in conditions:
            conditions.append(condition)
    return conditions


def _agentops_blocking_reason(rule_results: list[dict[str, object]]) -> str:
    failed = [
        str(item.get("message") or item.get("name") or "").strip()
        for item in rule_results
        if not bool(item.get("passed"))
    ]
    return "; ".join(item for item in failed if item)


def _agentops_actual_result_summary(
    *,
    status: str,
    blocking_reason: str,
    failed_conditions: list[str],
) -> str:
    if blocking_reason:
        return blocking_reason[:240]
    if failed_conditions:
        return "failed_conditions=" + ",".join(failed_conditions[:5])
    return status


def _agentops_retry_guidance(failed_conditions: list[str]) -> str:
    if not failed_conditions:
        return ""
    return "Resolve the failed stage conditions, then rerun ai-sdlc run."


def _agentops_next_action(failed_conditions: list[str]) -> str:
    if not failed_conditions:
        return ""
    return f"resolve {failed_conditions[0]}"


def _agentops_total_check_count(stage_results: list[tuple[str, Any]]) -> int:
    return sum(
        len(getattr(result, "checks", []) or [])
        for stage, result in stage_results
        if _agentops_public_stage_name(stage) == "test"
    )


def _agentops_total_failed_check_count(stage_results: list[tuple[str, Any]]) -> int:
    return sum(
        1
        for stage, result in stage_results
        if _agentops_public_stage_name(stage) == "test"
        for check in getattr(result, "checks", []) or []
        if not bool(getattr(check, "passed", False))
    )


def _agentops_status(result: Any) -> str:
    verdict = str(getattr(result.verdict, "value", result.verdict)).upper()
    if verdict == "PASS":
        return "passed"
    if verdict == "HALT":
        return "blocked"
    return "failed"


def _safe_agentops_id(value: object) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in str(value).strip())
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_") or "unknown"
