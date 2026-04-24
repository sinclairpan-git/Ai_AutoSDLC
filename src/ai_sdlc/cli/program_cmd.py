"""Program-level CLI commands for multi-spec orchestration."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ai_sdlc.core.frontend_delivery_truth import summarize_frontend_delivery_truth_item
from ai_sdlc.core.frontend_inheritance_truth import (
    summarize_frontend_inheritance_status_for_display,
)
from ai_sdlc.core.program_service import (
    FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY,
    ProgramFrontendEvidenceClassStatus,
    ProgramFrontendManagedDeliveryApplyRequest,
    ProgramFrontendManagedDeliveryApplyResult,
    ProgramFrontendReadiness,
    ProgramFrontendRemediationInput,
    ProgramService,
    humanize_frontend_browser_gate_state,
    humanize_frontend_delivery_apply_state,
    humanize_frontend_delivery_install_state,
    humanize_frontend_delivery_workspace_state,
)
from ai_sdlc.generators.frontend_provider_profile_artifacts import (
    materialize_builtin_frontend_provider_profile_artifacts,
    supports_builtin_frontend_provider_profile_artifacts,
)
from ai_sdlc.generators.frontend_solution_confirmation_artifacts import (
    frontend_solution_confirmation_memory_root,
    materialize_frontend_solution_confirmation_artifacts,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    FrontendSolutionSnapshot,
    build_builtin_install_strategies,
    build_builtin_style_pack_manifests,
)
from ai_sdlc.telemetry.display import summarize_frontend_delivery_scope_for_display
from ai_sdlc.utils.helpers import find_project_root

program_app = typer.Typer(help="Program-level planning across multiple specs")
truth_app = typer.Typer(help="Program truth-ledger operations")
program_app.add_typer(truth_app, name="truth")
console = Console()


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run 'ai-sdlc init' first.[/red]"
        )
        raise typer.Exit(code=1)
    return root


def _dedupe_cli_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


def _render_managed_delivery_apply_guard(
    mode_title: str,
    request_payload: ProgramFrontendManagedDeliveryApplyRequest,
) -> None:
    table = Table(title=mode_title)
    table.add_column("Action Plan")
    table.add_column("Selected")
    table.add_column("Executable")
    table.add_column("Unsupported")
    table.add_row(
        request_payload.action_plan_id,
        ", ".join(request_payload.selected_action_ids) or "-",
        ", ".join(request_payload.executable_action_ids) or "-",
        ", ".join(request_payload.unsupported_action_ids) or "-",
    )
    console.print(table)

    console.print("\n[bold cyan]Managed Delivery Apply Guard[/bold cyan]")
    console.print(
        f"  - request source: {request_payload.request_source_path}",
        markup=False,
    )
    console.print(
        f"  - apply state: {request_payload.apply_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request_payload.confirmation_required).lower()}",
        markup=False,
    )
    if request_payload.execution_view is not None:
        action_types = []
        action_by_id = {
            action.action_id: action for action in request_payload.execution_view.action_items
        }
        for action_id in request_payload.selected_action_ids:
            action = action_by_id.get(action_id)
            if action is not None:
                action_types.append(action.action_type)
        if action_types:
            console.print(
                "  - selected action types: "
                + ", ".join(_dedupe_cli_text_items(action_types)),
                markup=False,
                soft_wrap=True,
            )
        if request_payload.execution_view.managed_target_path:
            console.print(
                f"  - managed target path: {request_payload.execution_view.managed_target_path}",
                markup=False,
            )
        if request_payload.execution_view.will_not_touch:
            console.print(
                "  - will not touch: "
                + ", ".join(
                    _dedupe_cli_text_items(request_payload.execution_view.will_not_touch)
                ),
                markup=False,
            )
    console.print(
        "  - scope: only selected managed-target actions from the confirmed plan can materialize here",
        markup=False,
    )
    console.print(
        "  - package source boundary: only registry-declared package sets auto-install here",
        markup=False,
    )
    console.print(
        "  - delivery remains incomplete until browser gate and downstream closure finish",
        markup=False,
    )
    for blocker in _dedupe_cli_text_items(request_payload.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for plain_text in _dedupe_cli_text_items(request_payload.plain_language_blockers):
        console.print(f"  - explain: {plain_text}", markup=False)
    for next_step in _dedupe_cli_text_items(request_payload.recommended_next_steps):
        console.print(f"  - next step: {next_step}", markup=False)


def _render_managed_delivery_apply_result(
    root: Path,
    result: ProgramFrontendManagedDeliveryApplyResult,
    artifact_path: Path,
) -> None:
    console.print("\n[bold cyan]Managed Delivery Apply Result[/bold cyan]")
    console.print(f"  - status: {result.result_status}", markup=False)
    console.print(f"  - headline: {result.headline}", markup=False)
    console.print(
        f"  - delivery complete: {str(result.delivery_complete).lower()}",
        markup=False,
    )
    console.print(
        f"  - browser gate required: {str(result.browser_gate_required).lower()}",
        markup=False,
    )
    console.print(
        f"  - browser gate state: {result.browser_gate_state}",
        markup=False,
    )
    if result.next_required_gate:
        console.print(
            f"  - next required gate: {result.next_required_gate}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(result.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    if result.executed_action_ids:
        console.print(
            f"  - executed actions: {', '.join(result.executed_action_ids)}",
            markup=False,
        )
    if result.failed_action_ids:
        console.print(
            f"  - failed actions: {', '.join(result.failed_action_ids)}",
            markup=False,
        )
    if result.blocked_action_ids:
        console.print(
            f"  - blocked actions: {', '.join(result.blocked_action_ids)}",
            markup=False,
        )
    if result.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(result.warnings):
            console.print(f"  - {warning}")
    console.print(
        f"  - apply artifact: {artifact_path.relative_to(root)}",
        markup=False,
    )


@program_app.command("validate")
def program_validate(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Validate program-manifest for IDs, paths, deps, and cycles."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)

    if result.errors:
        console.print("[bold red]Manifest errors[/bold red]")
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
    if result.warnings:
        console.print("[bold yellow]Manifest warnings[/bold yellow]")
        for w in _dedupe_cli_text_items(result.warnings):
            console.print(f"  - {w}")

    if result.valid:
        console.print("[bold green]program validate: PASS[/bold green]")
        raise typer.Exit(code=0)

    console.print("[bold red]program validate: FAIL[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("frontend-evidence-class-sync")
def program_frontend_evidence_class_sync(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    spec_id: str = typer.Option(
        "",
        "--spec-id",
        help="Optional single spec id to sync instead of bounded bulk sync.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend evidence class mirror sync or explicitly update the manifest mirror.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm frontend evidence class manifest sync in execute mode.",
    ),
) -> None:
    """Preview or execute frontend evidence class manifest mirror sync."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    blocking_errors = [
        error
        for error in result.errors
        if f"problem_family={FRONTEND_EVIDENCE_CLASS_MIRROR_PROBLEM_FAMILY}" not in error
    ]
    if blocking_errors:
        console.print(
            "[bold red]Manifest invalid; cannot sync frontend evidence class mirror.[/bold red]"
        )
        for error in _dedupe_cli_text_items(blocking_errors):
            console.print(f"  - {error}")
        raise typer.Exit(code=1)

    sync_result = svc.execute_frontend_evidence_class_sync(
        mf,
        spec_id=spec_id.strip() or None,
        confirmed=not dry_run and yes,
    )

    mode_title = (
        "Program Frontend Evidence Class Sync Dry-Run"
        if dry_run
        else "Program Frontend Evidence Class Sync Execute"
    )
    console.print(f"[bold cyan]{mode_title}[/bold cyan]")
    console.print(
        f"  - scope: {spec_id.strip() or 'all eligible manifest specs'}",
        markup=False,
    )
    console.print(f"  - sync result: {sync_result.sync_result}", markup=False)
    console.print(
        f"  - confirmation required: {str(sync_result.sync_result == 'confirmation_required').lower()}",
        markup=False,
    )
    for updated_spec in sync_result.updated_specs:
        console.print(f"  - updated spec: {updated_spec}", markup=False)
    for written_path in _dedupe_cli_text_items(sync_result.written_paths):
        console.print(f"  - written path: {written_path}", markup=False)
    for blocker in _dedupe_cli_text_items(sync_result.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if sync_result.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(sync_result.warnings):
            console.print(f"  - {warning}")

    if dry_run:
        raise typer.Exit(code=0 if not sync_result.remaining_blockers else 1)

    if not yes:
        console.print(
            "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
        )
        raise typer.Exit(code=2)

    raise typer.Exit(code=0 if sync_result.passed else 1)


@program_app.command("status")
def program_status(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Show current status across specs in the program manifest."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    rows = svc.build_status(mf, validation_result=result)
    truth_surface = svc.build_truth_ledger_surface(mf, validation_result=result)

    table = Table(title="Program Status")
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Stage")
    table.add_column("Tasks")
    table.add_column("Blocked By")
    table.add_column("Frontend")

    for row in rows:
        tasks = (
            f"{row.completed_tasks}/{row.total_tasks}" if row.total_tasks > 0 else "-"
        )
        blocked = (
            ", ".join(_dedupe_cli_text_items(row.blocked_by))
            if row.blocked_by
            else "-"
        )
        stage = row.stage_hint
        if not row.exists:
            stage = "missing_path"
        table.add_row(
            row.spec_id,
            row.path,
            stage,
            tasks,
            blocked,
            _format_program_status_frontend_cell(
                row.frontend_readiness,
                row.frontend_evidence_class_status,
            ),
        )

    console.print(table)
    _render_frontend_status_lines(rows)
    _render_frontend_delivery_context_lines(svc)
    if truth_surface is not None:
        _render_truth_ledger_lines(truth_surface)

    if not result.valid:
        console.print(
            "\n[bold red]Manifest invalid; status shown with best-effort parsing.[/bold red]"
        )
        for error in _dedupe_cli_text_items(result.errors):
            if "problem_family=frontend_evidence_class_" in error:
                continue
            console.print(f"  - {error}")
        raise typer.Exit(code=1)

    raise typer.Exit(code=0)


@program_app.command("page-ui-schema-handoff")
def program_page_ui_schema_handoff() -> None:
    """Show the provider/kernel handoff surface for the 147 page/UI schema baseline."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_page_ui_schema_handoff()

    console.print("[bold cyan]Frontend Page/UI Schema Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - style pack: {handoff.effective_style_pack_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - delivery entry: {handoff.delivery_entry_id or '-'}",
        markup=False,
    )
    console.print(
        "  - provider theme adapter: "
        + (handoff.provider_theme_adapter_id or "-"),
        markup=False,
    )
    for package_name in _dedupe_cli_text_items(handoff.component_library_packages):
        console.print(f"  - component package: {package_name}", markup=False)
    for entry in handoff.entries:
        console.print(
            "  - page schema: "
            f"{entry.page_schema_id} | ui schema: {entry.ui_schema_id} | recipe: {entry.page_recipe_id}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("delivery-registry-handoff")
def program_delivery_registry_handoff() -> None:
    """Show the delivery registry handoff surface for the 099 resolver runtime."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_delivery_registry_handoff()

    console.print("[bold cyan]Frontend Delivery Registry Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(f"  - registry: {handoff.registry_id}", markup=False)
    console.print(f"  - entry: {handoff.entry_id or '-'}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - requested frontend stack: {handoff.requested_frontend_stack or '-'}",
        markup=False,
    )
    console.print(
        f"  - effective frontend stack: {handoff.effective_frontend_stack or '-'}",
        markup=False,
    )
    console.print(
        f"  - requested style pack: {handoff.requested_style_pack_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - effective style pack: {handoff.effective_style_pack_id or '-'}",
        markup=False,
    )
    console.print(f"  - access mode: {handoff.access_mode or '-'}", markup=False)
    if handoff.install_strategy_ids:
        for install_strategy_id in _dedupe_cli_text_items(handoff.install_strategy_ids):
            console.print(
                f"  - install strategy: {install_strategy_id}",
                markup=False,
            )
    console.print(
        f"  - package manager: {handoff.package_manager or '-'}",
        markup=False,
    )
    registry_url = getattr(handoff, "registry_url", "")
    if registry_url:
        console.print(
            f"  - install registry url: {registry_url}",
            markup=False,
        )
    console.print(
        f"  - provider manifest ref: {handoff.provider_manifest_ref or '-'}",
        markup=False,
    )
    console.print(
        "  - provider theme adapter: "
        + (handoff.provider_theme_adapter_id or "-"),
        markup=False,
    )
    for package_name in _dedupe_cli_text_items(handoff.component_library_packages):
        console.print(f"  - component package: {package_name}", markup=False)
    for package_name in _dedupe_cli_text_items(handoff.adapter_packages):
        console.print(f"  - adapter package: {package_name}", markup=False)
    for requirement in _dedupe_cli_text_items(handoff.availability_prerequisites):
        console.print(f"  - availability prerequisite: {requirement}", markup=False)
    for requirement in _dedupe_cli_text_items(handoff.runtime_requirements):
        console.print(f"  - runtime requirement: {requirement}", markup=False)
    for posture_mode in _dedupe_cli_text_items(handoff.supported_posture_modes):
        console.print(f"  - supported posture: {posture_mode}", markup=False)
    for style_entry in handoff.supported_style_entries:
        console.print(
            "  - style support: "
            f"{style_entry.style_pack_id} | {style_entry.fidelity_status} | "
            f"{style_entry.resolved_style_support_ref}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("generation-constraints-handoff")
def program_generation_constraints_handoff() -> None:
    """Show the generation constraints handoff bound to the current delivery context."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_generation_constraints_handoff()

    console.print("[bold cyan]Frontend Generation Constraints Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - work item: {handoff.work_item_id}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - delivery entry: {handoff.delivery_entry_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - apply state: {handoff.managed_delivery_apply_state or '-'}",
        markup=False,
    )
    if handoff.managed_delivery_apply_artifact_path:
        console.print(
            "  - apply artifact: "
            + handoff.managed_delivery_apply_artifact_path,
            markup=False,
        )
    console.print(
        "  - provider theme adapter: "
        + (handoff.provider_theme_adapter_id or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter carrier: "
        + (handoff.provider_runtime_adapter_carrier_mode or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter delivery: "
        + (handoff.provider_runtime_adapter_delivery_state or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter evidence: "
        + (handoff.provider_runtime_adapter_evidence_state or "-"),
        markup=False,
    )
    for package_name in _dedupe_cli_text_items(handoff.component_library_packages):
        console.print(f"  - component package: {package_name}", markup=False)
    for page_schema_id in _dedupe_cli_text_items(handoff.page_schema_ids):
        console.print(f"  - page schema: {page_schema_id}", markup=False)
    for recipe_id in _dedupe_cli_text_items(handoff.allowed_recipe_ids):
        console.print(f"  - recipe: {recipe_id}", markup=False)
    for component_id in _dedupe_cli_text_items(handoff.whitelist_component_ids):
        console.print(f"  - whitelist component: {component_id}", markup=False)
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("theme-token-governance-handoff")
def program_theme_token_governance_handoff() -> None:
    """Show the provider/page-schema handoff surface for the 148 theme governance baseline."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_theme_token_governance_handoff()

    console.print("[bold cyan]Frontend Theme Token Governance Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - delivery entry: {handoff.delivery_entry_id or '-'}",
        markup=False,
    )
    console.print(
        "  - provider theme adapter: "
        + (handoff.provider_theme_adapter_id or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter carrier: "
        + (handoff.provider_runtime_adapter_carrier_mode or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter delivery: "
        + (handoff.provider_runtime_adapter_delivery_state or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter evidence: "
        + (handoff.provider_runtime_adapter_evidence_state or "-"),
        markup=False,
    )
    for package_name in _dedupe_cli_text_items(handoff.component_library_packages):
        console.print(f"  - component package: {package_name}", markup=False)
    console.print(
        f"  - requested style pack: {handoff.requested_style_pack_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - effective style pack: {handoff.effective_style_pack_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - artifact root: {handoff.artifact_root}",
        markup=False,
    )
    console.print(
        f"  - token mappings: {handoff.token_mapping_count}",
        markup=False,
    )
    for page_schema_id in _dedupe_cli_text_items(handoff.page_schema_ids):
        console.print(f"  - page schema: {page_schema_id}", markup=False)
    for override in handoff.override_diagnostics:
        console.print(
            "  - override: "
            f"{override.override_id} | scope: {override.scope} | "
            f"requested: {override.requested_value} | "
            f"effective: {override.effective_value}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("quality-platform-handoff")
def program_quality_platform_handoff() -> None:
    """Show the Track C quality platform handoff surface for the 149 baseline."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_quality_platform_handoff()

    console.print("[bold cyan]Frontend Quality Platform Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - delivery entry: {handoff.delivery_entry_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - apply state: {handoff.managed_delivery_apply_state or '-'}",
        markup=False,
    )
    if handoff.managed_delivery_apply_artifact_path:
        console.print(
            "  - apply artifact: "
            + handoff.managed_delivery_apply_artifact_path,
            markup=False,
        )
    console.print(
        "  - provider theme adapter: "
        + (handoff.provider_theme_adapter_id or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter carrier: "
        + (handoff.provider_runtime_adapter_carrier_mode or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter delivery: "
        + (handoff.provider_runtime_adapter_delivery_state or "-"),
        markup=False,
    )
    console.print(
        "  - runtime adapter evidence: "
        + (handoff.provider_runtime_adapter_evidence_state or "-"),
        markup=False,
    )
    for package_name in _dedupe_cli_text_items(handoff.component_library_packages):
        console.print(f"  - component package: {package_name}", markup=False)
    console.print(
        f"  - requested style pack: {handoff.requested_style_pack_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - effective style pack: {handoff.effective_style_pack_id or '-'}",
        markup=False,
    )
    console.print(f"  - artifact root: {handoff.artifact_root}", markup=False)
    console.print(f"  - matrix coverage: {handoff.matrix_coverage_count}", markup=False)
    for evidence_contract_id in _dedupe_cli_text_items(handoff.evidence_contract_ids):
        console.print(f"  - evidence contract: {evidence_contract_id}", markup=False)
    for page_schema_id in _dedupe_cli_text_items(handoff.page_schema_ids):
        console.print(f"  - page schema: {page_schema_id}", markup=False)
    for diagnostic in handoff.quality_diagnostics:
        console.print(
            "  - quality diagnostic: "
            f"{diagnostic.matrix_id} | page: {diagnostic.page_schema_id} | "
            f"browser: {diagnostic.browser_id} | viewport: {diagnostic.viewport_id} | "
            f"gate: {diagnostic.gate_state} | evidence: {diagnostic.evidence_state}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("provider-expansion-handoff")
def program_provider_expansion_handoff() -> None:
    """Show the provider expansion handoff surface for the 151 baseline."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_provider_expansion_handoff()

    console.print("[bold cyan]Frontend Provider Expansion Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - requested frontend stack: {handoff.requested_frontend_stack or '-'}",
        markup=False,
    )
    console.print(
        f"  - effective frontend stack: {handoff.effective_frontend_stack or '-'}",
        markup=False,
    )
    console.print(
        f"  - artifact root: {handoff.artifact_root}",
        markup=False,
    )
    console.print(
        f"  - react stack visibility: {handoff.react_stack_visibility}",
        markup=False,
    )
    console.print(
        f"  - react binding visibility: {handoff.react_binding_visibility}",
        markup=False,
    )
    for provider in handoff.provider_diagnostics:
        console.print(
            "  - provider diagnostic: "
            f"{provider.provider_id} | gate: {provider.certification_gate} | "
            f"roster: {provider.roster_admission_state} | "
            f"visibility: {provider.choice_surface_visibility} | "
            f"pair refs: {provider.pair_certification_count}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("provider-runtime-adapter-handoff")
def program_provider_runtime_adapter_handoff() -> None:
    """Show the provider runtime adapter handoff surface for the 153 baseline."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_provider_runtime_adapter_handoff()

    console.print("[bold cyan]Frontend Provider Runtime Adapter Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(
        f"  - provider: {handoff.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - requested frontend stack: {handoff.requested_frontend_stack or '-'}",
        markup=False,
    )
    console.print(
        f"  - effective frontend stack: {handoff.effective_frontend_stack or '-'}",
        markup=False,
    )
    console.print(f"  - artifact root: {handoff.artifact_root}", markup=False)
    console.print(f"  - carrier mode: {handoff.carrier_mode or '-'}", markup=False)
    console.print(
        f"  - runtime delivery state: {handoff.runtime_delivery_state or '-'}",
        markup=False,
    )
    console.print(
        f"  - evidence return state: {handoff.evidence_return_state or '-'}",
        markup=False,
    )
    for provider in handoff.provider_diagnostics:
        console.print(
            "  - provider diagnostic: "
            f"{provider.provider_id} | stack: {provider.target_frontend_stack} | "
            f"gate: {provider.certification_gate} | carrier: {provider.carrier_mode} | "
            f"runtime: {provider.runtime_delivery_state} | "
            f"evidence: {provider.evidence_return_state} | "
            f"scaffold files: {provider.scaffold_file_count}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@program_app.command("cross-provider-consistency-handoff")
def program_cross_provider_consistency_handoff() -> None:
    """Show the cross-provider consistency handoff surface for the 150 baseline."""

    root = _resolve_root()
    svc = ProgramService(root)
    handoff = svc.build_frontend_cross_provider_consistency_handoff()

    console.print("[bold cyan]Frontend Cross Provider Consistency Handoff[/bold cyan]")
    console.print(f"  - state: {handoff.state}", markup=False)
    console.print(f"  - schema version: {handoff.schema_version}", markup=False)
    console.print(f"  - artifact root: {handoff.artifact_root}", markup=False)
    console.print(
        "  - runtime adapter carrier: "
        f"{handoff.provider_runtime_adapter_carrier_mode or '-'}",
        markup=False,
    )
    console.print(
        "  - runtime adapter delivery: "
        f"{handoff.provider_runtime_adapter_delivery_state or '-'}",
        markup=False,
    )
    console.print(
        "  - runtime adapter evidence: "
        f"{handoff.provider_runtime_adapter_evidence_state or '-'}",
        markup=False,
    )
    console.print(f"  - pair count: {handoff.pair_count}", markup=False)
    console.print(f"  - ready pairs: {handoff.ready_pair_count}", markup=False)
    console.print(
        f"  - conditional pairs: {handoff.conditional_pair_count}",
        markup=False,
    )
    console.print(f"  - blocked pairs: {handoff.blocked_pair_count}", markup=False)
    for page_schema_id in _dedupe_cli_text_items(handoff.page_schema_ids):
        console.print(f"  - page schema: {page_schema_id}", markup=False)
    for diagnostic in handoff.pair_diagnostics:
        console.print(
            "  - pair diagnostic: "
            f"{diagnostic.pair_id} | page: {diagnostic.page_schema_id} | "
            f"verdict: {diagnostic.final_verdict} | "
            f"comparability: {diagnostic.comparability_state} | "
            f"blocking: {diagnostic.blocking_state} | "
            f"evidence: {diagnostic.evidence_state} | "
            f"gate: {diagnostic.certification_gate}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(handoff.warnings):
        console.print(f"  - warning: {warning}", markup=False)

    raise typer.Exit(code=0 if handoff.state == "ready" else 1)


@truth_app.command("sync")
def program_truth_sync(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview truth snapshot materialization or explicitly write truth_snapshot.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm truth snapshot write in execute mode.",
    ),
) -> None:
    """Preview or materialize the program truth snapshot."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    validation = svc.validate_manifest(mf)
    snapshot = svc.build_truth_snapshot(mf, validation_result=validation)
    surface = svc.build_truth_ledger_surface(mf, validation_result=validation)
    capability_surface_by_id = {
        str(item.get("capability_id", "")).strip(): item
        for item in (surface or {}).get("release_capabilities", [])
        if isinstance(item, dict)
    }
    mode_title = "Program Truth Sync Dry-Run" if dry_run else "Program Truth Sync Execute"
    console.print(f"[bold cyan]{mode_title}[/bold cyan]")
    console.print(f"  - truth snapshot state: {snapshot.state}", markup=False)
    console.print(f"  - snapshot hash: {snapshot.snapshot_hash}", markup=False)
    console.print(
        "  - release targets: "
        + (
            ", ".join(_dedupe_cli_text_items(mf.release_targets))
            if mf.release_targets
            else "-"
        ),
        markup=False,
    )
    capability_items: list[dict[str, object]] = []
    for item in snapshot.computed_capabilities:
        capability_item: dict[str, object] = {
            "capability_id": item.capability_id,
            "closure_state": item.closure_state,
            "audit_state": item.audit_state,
            "blocking_refs": list(item.blocking_refs),
        }
        enriched = capability_surface_by_id.get(item.capability_id, {})
        for key in (
            "plain_language_blockers",
            "recommended_next_steps",
            "blocking_reason_summary",
            "frontend_delivery_status",
            "frontend_delivery_summary",
            "capability_next_actions",
        ):
            if key in enriched:
                capability_item[key] = enriched[key]
        capability_items.append(capability_item)
    _render_truth_release_capability_lines(capability_items)
    _render_truth_source_inventory(snapshot.source_inventory)
    _render_truth_validation_summary(validation.errors, validation.warnings)

    if dry_run:
        raise typer.Exit(code=0)

    if not yes:
        console.print(
            "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
        )
        raise typer.Exit(code=2)

    svc.write_truth_snapshot(snapshot)
    console.print(
        f"  - written path: {root.joinpath(manifest).relative_to(root)}",
        markup=False,
    )
    raise typer.Exit(code=0)


@truth_app.command("audit")
def program_truth_audit(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Audit persisted truth snapshot freshness and release-target readiness."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    validation = svc.validate_manifest(mf)
    surface = svc.build_truth_ledger_surface(mf, validation_result=validation)
    if surface is None:
        console.print("[yellow]Truth ledger is not enabled in the manifest.[/yellow]")
        raise typer.Exit(code=1)

    console.print("[bold cyan]Program Truth Audit[/bold cyan]")
    console.print(f"  - state: {surface['state']}", markup=False)
    console.print(f"  - snapshot state: {surface['snapshot_state']}", markup=False)
    console.print(f"  - detail: {surface['detail']}", markup=False)
    for action in _dedupe_cli_text_items(surface.get("next_required_actions", [])):
        console.print(f"  - next action: {action}", markup=False)
    console.print(
        "  - release targets: "
        + (
            ", ".join(_dedupe_cli_text_items(surface["release_targets"]))
            if surface["release_targets"]
            else "-"
        ),
        markup=False,
    )
    _render_truth_release_capability_lines(surface["release_capabilities"])
    if surface["migration_pending_count"]:
        console.print(
            f"  - migration pending: {surface['migration_pending_count']}",
            markup=False,
        )
        for spec in _dedupe_cli_text_items(surface["migration_pending_specs"])[:5]:
            console.print(f"    pending spec: {spec}", markup=False)
        for source in _dedupe_cli_text_items(
            surface.get("migration_pending_sources", [])
        )[:5]:
            console.print(f"    pending source: {source}", markup=False)
        for suggestion in _dedupe_cli_text_items(surface["migration_suggestions"]):
            console.print(f"    suggestion: {suggestion}", markup=False)
    _render_truth_source_inventory(surface.get("source_inventory"))
    _render_truth_validation_summary(
        list(surface["validation_errors"]),
        list(surface["validation_warnings"]),
    )

    raise typer.Exit(code=0 if surface["state"] == "ready" else 1)


@program_app.command("plan")
def program_plan(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
) -> None:
    """Show dependency topo order and parallel tiers."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot compute plan.[/bold red]")
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    tiers = svc.topo_tiers(mf)
    if not tiers:
        console.print("[yellow]No schedulable tiers computed.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="Program Plan")
    table.add_column("Tier")
    table.add_column("Specs")
    for idx, tier in enumerate(tiers):
        table.add_row(str(idx), ", ".join(_dedupe_cli_text_items(tier)))
    console.print(table)
    raise typer.Exit(code=0)


@program_app.command("integrate")
def program_integrate(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Dry-run only in current phase; execute is guarded and not enabled yet.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded execute mode.",
    ),
    allow_dirty: bool = typer.Option(
        False,
        "--allow-dirty",
        help="Allow execute gate to run on dirty working tree (not recommended).",
    ),
) -> None:
    """Build or execute a guarded integration runbook."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build integration runbook.[/bold red]")
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    plan = svc.build_integration_dry_run(mf)
    if not plan.steps:
        console.print("[red]No integration steps generated.[/red]")
        raise typer.Exit(code=1)

    mode_title = (
        "Program Integrate Dry-Run" if dry_run else "Program Integrate Execute (Guarded)"
    )
    table = Table(title="Program Integrate Dry-Run")
    table.add_column("Order")
    table.add_column("Tier")
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Verification")
    table.add_column("Archive Checks")
    table.add_column("Frontend Hint")
    for step in plan.steps:
        table.add_row(
            str(step.order),
            str(step.tier),
            step.spec_id,
            step.path,
            " ; ".join(_dedupe_cli_text_items(step.verification_commands)),
            " ; ".join(_dedupe_cli_text_items(step.archive_checks)),
            _format_frontend_readiness(step.frontend_readiness),
        )
    table.title = mode_title
    console.print(table)
    _render_frontend_integrate_lines(plan.steps)

    if plan.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for w in _dedupe_cli_text_items(plan.warnings):
            console.print(f"  - {w}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Mode: `{'dry-run' if dry_run else 'execute'}`",
            "",
            "## Steps",
            "",
        ]
        for step in plan.steps:
            lines.extend(
                [
                    f"### {step.order}. {step.spec_id} (tier {step.tier})",
                    f"- Path: `{step.path}`",
                    f"- Frontend: `{_format_frontend_readiness(step.frontend_readiness)}`",
                    "- Verification:",
                ]
            )
            lines.extend(
                [
                    f"  - `{cmd}`"
                    for cmd in _dedupe_cli_text_items(step.verification_commands)
                ]
            )
            lines.append("- Archive checks:")
            lines.extend(
                [
                    f"  - {item}"
                    for item in _dedupe_cli_text_items(step.archive_checks)
                ]
            )
            handoff = getattr(step, "frontend_recheck_handoff", None)
            if not dry_run and handoff is not None:
                lines.append("- Frontend recheck handoff:")
                lines.append(f"  - {handoff.reason}")
                lines.extend(
                    [
                        f"  - `{cmd}`"
                        for cmd in _dedupe_cli_text_items(
                            handoff.recommended_commands
                        )
                    ]
                )
            lines.append("")
        if not dry_run:
            remediation_lines = _frontend_remediation_report_lines(plan.steps)
            if remediation_lines:
                lines.append("## Frontend Remediation Handoff")
                lines.append("")
                lines.extend(remediation_lines)
                lines.append("")
            handoff_lines = _frontend_recheck_report_lines(plan.steps)
            if handoff_lines:
                lines.append("## Frontend Recheck Handoff")
                lines.append("")
                lines.extend(handoff_lines)
                lines.append("")
        if plan.warnings:
            lines.append("## Warnings")
            lines.extend([f"- {w}" for w in _dedupe_cli_text_items(plan.warnings)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    if not yes:
        console.print(
            "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
        )
        raise typer.Exit(code=2)

    _render_frontend_execute_preflight(plan.steps)
    gates = svc.evaluate_execute_gates(mf, allow_dirty=allow_dirty)
    if gates.warnings:
        console.print("\n[bold yellow]Gate warnings[/bold yellow]")
        for item in _dedupe_cli_text_items(gates.warnings):
            console.print(f"  - {item}")
    if not gates.passed:
        console.print("\n[bold red]Execution gates failed[/bold red]")
        for item in gates.failed:
            console.print(f"  - {item}")
        _render_frontend_recheck_handoff(plan.steps)
        _render_frontend_remediation_handoff(plan.steps)
        raise typer.Exit(code=1)

    _render_frontend_recheck_handoff(plan.steps)
    console.print("\n[bold green]Execution gates passed[/bold green]")
    console.print(
        "Guarded execute completed: runbook generated and gates validated."
    )

    raise typer.Exit(code=0)


@program_app.command("remediate")
def program_remediate(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview remediation runbook or explicitly execute bounded remediation commands.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm bounded remediation execute mode.",
    ),
) -> None:
    """Preview or execute the bounded frontend remediation runbook."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build remediation runbook.[/bold red]")
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    runbook = svc.build_frontend_remediation_runbook(mf)
    mode_title = (
        "Program Frontend Remediation Dry-Run"
        if dry_run
        else "Program Frontend Remediation Execute"
    )

    if not runbook.steps:
        console.print("[green]No frontend remediation steps generated.[/green]")
        raise typer.Exit(code=0)

    table = Table(title=mode_title)
    table.add_column("Spec")
    table.add_column("Path")
    table.add_column("Fix Inputs")
    table.add_column("Action Commands")
    for step in runbook.steps:
        table.add_row(
            step.spec_id,
            step.path,
            ", ".join(_dedupe_cli_text_items(step.fix_inputs)[:3]) or "-",
            " ; ".join(_dedupe_cli_text_items(step.action_commands)) or "-",
        )
    console.print(table)
    guidance_lines: list[str] = []
    for step in runbook.steps:
        for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
            guidance_lines.append(f"  - {step.spec_id} explain: {plain_text}")
        for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
            guidance_lines.append(f"  - {step.spec_id} next step: {next_step}")
    if guidance_lines:
        console.print("\n[bold cyan]Frontend Remediation Guidance[/bold cyan]")
        for line in guidance_lines:
            console.print(line, markup=False)
    if runbook.action_commands:
        console.print("\n[bold cyan]Frontend Remediation Actions[/bold cyan]")
        for command in _dedupe_cli_text_items(runbook.action_commands):
            console.print(f"  - {command}", markup=False)

    if runbook.follow_up_commands:
        console.print("\n[bold cyan]Frontend Remediation Follow-Up[/bold cyan]")
        for command in _dedupe_cli_text_items(runbook.follow_up_commands):
            console.print(f"  - {command}", markup=False)

    if runbook.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(runbook.warnings):
            console.print(f"  - {warning}")

    execution_result = None
    runbook_for_writeback = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        runbook_for_writeback = runbook
        execution_result = svc.execute_frontend_remediation_runbook(mf)
        writeback_path = svc.write_frontend_remediation_writeback_artifact(
            mf,
            runbook=runbook_for_writeback,
            execution_result=execution_result,
        )
        _render_frontend_remediation_execution_result(execution_result.command_results)
        if execution_result.blockers:
            console.print("\n[bold red]Remaining Frontend Remediation Blockers[/bold red]")
            for blocker in _dedupe_cli_text_items(execution_result.blockers):
                console.print(f"  - {blocker}")
        console.print(
            "\n[bold cyan]Frontend Remediation Writeback[/bold cyan]"
        )
        console.print(
            f"  - saved: {writeback_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Mode: `{'dry-run' if dry_run else 'execute'}`",
            "",
            "## Steps",
            "",
        ]
        for step in runbook.steps:
            lines.extend(
                [
                    f"### {step.spec_id}",
                    f"- Path: `{step.path}`",
                    f"- Fix inputs: `{', '.join(_dedupe_cli_text_items(step.fix_inputs)) or '-'}`",
                    f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                    f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                    "- Action commands:",
                ]
            )
            lines.extend(
                [
                    f"  - `{command}`"
                    for command in _dedupe_cli_text_items(step.action_commands)
                ]
            )
            lines.append("")
        if runbook.follow_up_commands:
            lines.append("## Follow-Up Commands")
            lines.append("")
            lines.extend(
                [
                    f"- `{command}`"
                    for command in _dedupe_cli_text_items(runbook.follow_up_commands)
                ]
            )
            lines.append("")
        if execution_result is not None:
            lines.append("## Command Results")
            lines.append("")
            for item in execution_result.command_results:
                lines.append(f"- `{item.command}` -> `{item.status}`")
                for path in _dedupe_cli_text_items(item.written_paths):
                    lines.append(f"  - wrote `{path}`")
                if item.summary:
                    lines.append(f"  - {item.summary}")
            lines.append("")
            if execution_result.blockers:
                lines.append("## Remaining Blockers")
                lines.append("")
                lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(execution_result.blockers)])
                lines.append("")
            lines.append("## Writeback Artifact")
            lines.append("")
            lines.append(
                f"- `{writeback_path.relative_to(root)}`"
            )
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert execution_result is not None
    if execution_result.passed:
        console.print(
            f"Frontend remediation writeback saved: {writeback_path.relative_to(root)}",
            markup=False,
        )
        console.print("\n[bold green]Frontend remediation execute completed[/bold green]")
        raise typer.Exit(code=0)

    console.print(
        f"Frontend remediation writeback saved: {writeback_path.relative_to(root)}",
        markup=False,
    )
    console.print("\n[bold red]Frontend remediation execute incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("managed-delivery-apply")
def program_managed_delivery_apply(
    request: str | None = typer.Option(
        None,
        "--request",
        help="Optional path to a managed delivery apply request YAML relative to project root; when omitted, materialize from current truth.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview managed delivery apply or explicitly execute the narrow apply runtime.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm managed delivery apply execute mode.",
    ),
    ack_effective_change: bool = typer.Option(
        False,
        "--ack-effective-change",
        help="Acknowledge requested_* versus effective_* differences when deriving the request from current truth.",
    ),
) -> None:
    """Preview or execute the narrow managed delivery apply runtime."""
    root = _resolve_root()
    svc = ProgramService(root)

    request_payload = svc.build_frontend_managed_delivery_apply_request(
        request,
        second_confirmation_acknowledged=(True if ack_effective_change else None),
    )
    mode_title = (
        "Program Managed Delivery Apply Dry-Run"
        if dry_run
        else "Program Managed Delivery Apply Execute"
    )
    _render_managed_delivery_apply_guard(mode_title, request_payload)

    if dry_run:
        raise typer.Exit(code=0 if not request_payload.remaining_blockers else 1)

    if not yes:
        console.print(
            "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
        )
        raise typer.Exit(code=2)

    if (
        request is None
        and not ack_effective_change
        and "second_confirmation_missing" in request_payload.remaining_blockers
    ):
        console.print(
            "\n[bold yellow]Effective solution change requires explicit acknowledgement[/bold yellow]"
        )
        console.print(
            "  - current truth contains requested_* versus effective_* differences; review the managed delivery guard before executing",
            markup=False,
        )
        console.print(
            "  - pass `--ack-effective-change` to confirm the effective solution may differ from the requested solution",
            markup=False,
        )
        raise typer.Exit(code=2)

    result = svc.execute_frontend_managed_delivery_apply(
        request,
        request=request_payload,
        confirmed=True,
    )
    artifact_path = svc.write_frontend_managed_delivery_apply_artifact(
        request,
        request=request_payload,
        result=result,
    )
    _render_managed_delivery_apply_result(root, result, artifact_path)

    raise typer.Exit(code=0 if result.passed else 1)


@program_app.command("browser-gate-probe")
def program_browser_gate_probe(
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview browser gate probe runtime or materialize the gate-run artifact bundle.",
    ),
) -> None:
    """Preview or execute the browser gate probe runtime baseline."""
    root = _resolve_root()
    svc = ProgramService(root)
    request = svc.build_frontend_browser_gate_probe_request()

    table = Table(
        title=(
            "Program Browser Gate Probe Dry-Run"
            if dry_run
            else "Program Browser Gate Probe Execute"
        )
    )
    table.add_column("Apply Artifact")
    table.add_column("Gate Run")
    table.add_column("Spec")
    table.add_column("Probe Set")
    table.add_row(
        request.apply_artifact_path or "-",
        request.gate_run_id or "-",
        request.spec_dir or "-",
        ", ".join(_dedupe_cli_text_items(request.required_probe_set)) or "-",
    )
    console.print(table)
    console.print("\n[bold cyan]Browser Gate Probe Guard[/bold cyan]")
    console.print(f"  - probe state: {request.probe_state}", markup=False)
    console.print(f"  - apply artifact: {request.apply_artifact_path}", markup=False)
    if request.execution_context is not None:
        console.print(
            f"  - managed frontend target: {request.execution_context.managed_frontend_target}",
            markup=False,
        )
        console.print(
            f"  - delivery entry: {request.execution_context.delivery_entry_id or '-'}",
            markup=False,
        )
        console.print(
            "  - provider theme adapter: "
            + (request.execution_context.provider_theme_adapter_id or "-"),
            markup=False,
        )
        for package_name in _dedupe_cli_text_items(
            request.execution_context.component_library_packages
        ):
            console.print(f"  - component package: {package_name}", markup=False)
        for page_schema_id in _dedupe_cli_text_items(
            request.execution_context.page_schema_ids
        ):
            console.print(f"  - page schema: {page_schema_id}", markup=False)
        console.print(
            f"  - browser entry ref: {request.execution_context.browser_entry_ref}",
            markup=False,
        )
    if request.overall_gate_status_preview:
        console.print(
            f"  - overall gate status preview: {request.overall_gate_status_preview}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    for plain_text in _dedupe_cli_text_items(request.plain_language_blockers):
        console.print(f"  - explain: {plain_text}", markup=False)
    for next_step in _dedupe_cli_text_items(request.recommended_next_steps):
        console.print(f"  - next step: {next_step}", markup=False)

    if dry_run:
        raise typer.Exit(code=0 if not request.remaining_blockers else 1)

    result = svc.execute_frontend_browser_gate_probe(request=request)
    console.print("\n[bold cyan]Browser Gate Probe Result[/bold cyan]")
    console.print(f"  - runtime state: {result.probe_runtime_state}", markup=False)
    console.print(f"  - overall gate status: {result.overall_gate_status}", markup=False)
    console.print(f"  - gate run id: {result.gate_run_id}", markup=False)
    console.print(f"  - artifact path: {result.artifact_path}", markup=False)
    console.print(f"  - artifact root: {result.artifact_root}", markup=False)
    if result.execute_gate_state:
        console.print(
            f"  - execute gate state: {result.execute_gate_state}",
            markup=False,
        )
    if result.decision_reason:
        console.print(
            f"  - decision reason: {result.decision_reason}",
            markup=False,
        )
    if result.recommended_next_command:
        console.print(
            f"  - next command: {result.recommended_next_command}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(result.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    if result.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(result.warnings):
            console.print(f"  - {warning}")
    raise typer.Exit(code=0 if result.passed else 1)


@program_app.command("browser-gate-baseline")
def program_browser_gate_baseline(
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview or materialize the current visual regression baseline bootstrap.",
    ),
    threshold: float = typer.Option(
        0.03,
        "--threshold",
        help="Diff threshold written into baseline metadata.",
    ),
    artifact: str = typer.Option(
        "",
        "--artifact",
        help="Optional browser gate artifact path relative to project root; defaults to latest.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm execute mode for baseline materialization.",
    ),
) -> None:
    """Preview or execute visual regression baseline bootstrap from the latest gate run."""
    root = _resolve_root()
    svc = ProgramService(root)
    request = svc.build_frontend_browser_gate_baseline_request(
        artifact_path=artifact or None,
        threshold=threshold,
    )

    table = Table(
        title=(
            "Program Browser Gate Baseline Dry-Run"
            if dry_run
            else "Program Browser Gate Baseline Execute"
        )
    )
    table.add_column("Artifact")
    table.add_column("Gate Run")
    table.add_column("Matrix")
    table.add_row(
        request.artifact_path or "-",
        request.gate_run_id or "-",
        request.matrix_id or "-",
    )
    console.print(table)
    console.print("\n[bold cyan]Browser Gate Baseline Guard[/bold cyan]")
    console.print(f"  - baseline state: {request.baseline_state}", markup=False)
    console.print(f"  - threshold: {request.threshold}", markup=False)
    if request.bootstrap_artifact_ref:
        console.print(
            f"  - bootstrap artifact: {request.bootstrap_artifact_ref}",
            markup=False,
        )
    if request.baseline_image_path:
        console.print(
            f"  - baseline image path: {request.baseline_image_path}",
            markup=False,
        )
    if request.baseline_metadata_path:
        console.print(
            f"  - baseline metadata path: {request.baseline_metadata_path}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if dry_run:
        raise typer.Exit(code=0 if not request.remaining_blockers else 1)

    if not yes:
        console.print(
            "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
        )
        raise typer.Exit(code=2)

    result = svc.execute_frontend_browser_gate_baseline(request=request)
    console.print("\n[bold cyan]Browser Gate Baseline Result[/bold cyan]")
    console.print(f"  - baseline state: {result.baseline_state}", markup=False)
    console.print(f"  - gate run id: {result.gate_run_id}", markup=False)
    console.print(f"  - matrix id: {result.matrix_id}", markup=False)
    if result.baseline_image_path:
        console.print(
            f"  - baseline image path: {result.baseline_image_path}",
            markup=False,
        )
    if result.baseline_metadata_path:
        console.print(
            f"  - baseline metadata path: {result.baseline_metadata_path}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(result.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)
    if result.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(result.warnings):
            console.print(f"  - {warning}")
    raise typer.Exit(code=0 if result.passed else 1)


@program_app.command("provider-handoff")
def program_provider_handoff(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
) -> None:
    """Show the read-only frontend provider handoff payload."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build provider handoff.[/bold red]")
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    handoff = svc.build_frontend_provider_handoff(mf)

    if handoff.steps:
        table = Table(title="Program Frontend Provider Handoff")
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in handoff.steps:
            table.add_row(
                step.spec_id,
                step.path,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Provider Handoff Steps[/bold cyan]")
        for step in handoff.steps:
            console.print(f"  - {step.spec_id}: {step.path}", markup=False)
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions):
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend provider handoff required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Handoff[/bold cyan]")
    console.print(
        f"  - source writeback: {handoff.writeback_artifact_path}",
        markup=False,
    )
    console.print(
        f"  - provider state: {handoff.provider_execution_state}",
        markup=False,
    )
    if handoff.writeback_generated_at:
        console.print(
            f"  - writeback generated_at: {handoff.writeback_generated_at}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(handoff.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if handoff.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(handoff.warnings):
            console.print(f"  - {warning}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            "# Program Frontend Provider Handoff",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source writeback: `{handoff.writeback_artifact_path}`",
            f"- Provider state: `{handoff.provider_execution_state}`",
        ]
        if handoff.writeback_generated_at:
            lines.append(f"- Writeback generated_at: `{handoff.writeback_generated_at}`")
        lines.append("")
        if handoff.steps:
            lines.append("## Steps")
            lines.append("")
            for step in handoff.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if handoff.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(handoff.remaining_blockers)])
            lines.append("")
        if handoff.warnings:
            lines.append("## Warnings")
            lines.append("")
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(handoff.warnings)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if handoff.warnings and not handoff.writeback_generated_at:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


@program_app.command("provider-runtime")
def program_provider_runtime(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded provider runtime request or explicitly execute the guarded runtime baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded provider runtime execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend provider runtime baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print("[bold red]Manifest invalid; cannot build provider runtime.[/bold red]")
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_provider_runtime_request(mf)
    mode_title = (
        "Program Frontend Provider Runtime Dry-Run"
        if dry_run
        else "Program Frontend Provider Runtime Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Provider Runtime Steps[/bold cyan]")
        for step in request.steps:
            console.print(f"  - {step.spec_id}: {step.path}", markup=False)
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No guarded frontend provider runtime steps required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Runtime Guard[/bold cyan]")
    console.print(f"  - source handoff: {request.handoff_source_path}", markup=False)
    console.print(
        f"  - provider state: {request.provider_execution_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.handoff_generated_at:
        console.print(
            f"  - handoff generated_at: {request.handoff_generated_at}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    runtime_result = None
    runtime_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        runtime_result = svc.execute_frontend_provider_runtime(
            mf,
            request=request,
            confirmed=True,
        )
        runtime_artifact_path = svc.write_frontend_provider_runtime_artifact(
            mf,
            request=request,
            result=runtime_result,
        )
        _render_frontend_provider_runtime_result(runtime_result)
        console.print("\n[bold cyan]Frontend Provider Runtime Artifact[/bold cyan]")
        console.print(
            f"  - saved: {runtime_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source handoff: `{request.handoff_source_path}`",
            f"- Provider state: `{request.provider_execution_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.handoff_generated_at:
            lines.append(f"- Handoff generated_at: `{request.handoff_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if runtime_result is not None:
            lines.append("## Frontend Provider Runtime Result")
            lines.append("")
            lines.append(f"- Invocation result: `{runtime_result.invocation_result}`")
            lines.append(
                f"- Provider state: `{runtime_result.provider_execution_state}`"
            )
            lines.append(f"- Confirmed: `{str(runtime_result.confirmed).lower()}`")
            if runtime_result.patch_summaries:
                lines.append("- Patch summaries:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(
                            runtime_result.patch_summaries
                        )
                    ]
                )
            if runtime_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(
                            runtime_result.remaining_blockers
                        )
                    ]
                )
            lines.append("")
        if runtime_artifact_path is not None:
            lines.append("## Frontend Provider Runtime Artifact")
            lines.append("")
            lines.append(f"- `{runtime_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (runtime_result is not None and runtime_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if runtime_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(runtime_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert runtime_result is not None
    if runtime_result.passed:
        console.print("\n[bold green]Frontend provider runtime completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend provider runtime incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("solution-confirm")
def program_solution_confirm(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    mode: str = typer.Option(
        "simple",
        "--mode",
        help="Confirmation flow mode: simple or advanced.",
    ),
    frontend_stack: str = typer.Option(
        "",
        "--frontend-stack",
        help="Optional requested frontend stack override.",
    ),
    provider_id: str = typer.Option(
        "",
        "--provider-id",
        help="Optional requested provider override.",
    ),
    style_pack_id: str = typer.Option(
        "",
        "--style-pack-id",
        help="Optional requested style pack override.",
    ),
    enterprise_provider_eligible: bool = typer.Option(
        True,
        "--enterprise-provider-eligible/--enterprise-provider-ineligible",
        help="Whether enterprise provider prerequisites are currently satisfied.",
    ),
    failed_preflight_check_ids: list[str] = typer.Option(
        None,
        "--failed-preflight-check-id",
        help="Optional failed availability/preflight check IDs.",
    ),
    fallback_candidate_available: bool = typer.Option(
        True,
        "--fallback-candidate-available/--no-fallback-candidate",
        help="Whether a public fallback candidate is available when enterprise is blocked.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview or explicitly materialize the structured solution confirmation snapshot.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm solution confirmation execute mode.",
    ),
    continue_execution: bool = typer.Option(
        False,
        "--continue",
        help="After persisting the solution confirmation snapshot, continue into managed delivery apply.",
    ),
    ack_effective_change: bool = typer.Option(
        False,
        "--ack-effective-change",
        help="Acknowledge requested_* versus effective_* differences before continuing into apply.",
    ),
) -> None:
    """Preview or execute the structured frontend solution confirmation baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build frontend solution confirmation.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"simple", "advanced"}:
        console.print("[bold red]`--mode` must be `simple` or `advanced`.[/bold red]")
        raise typer.Exit(code=2)

    snapshot = svc.build_frontend_solution_confirmation(
        mf,
        mode="simple",
        requested_frontend_stack=frontend_stack or None,
        requested_provider_id=provider_id or None,
        requested_style_pack_id=style_pack_id or None,
        enterprise_provider_eligible=enterprise_provider_eligible,
        failed_preflight_check_ids=list(failed_preflight_check_ids or []),
        fallback_candidate_available=fallback_candidate_available,
    )
    snapshot = _coerce_frontend_solution_confirmation_mode(
        snapshot,
        mode=normalized_mode,
    )

    mode_title = (
        "Program Frontend Solution Confirm Simple"
        if normalized_mode == "simple"
        else "Program Frontend Solution Confirm Advanced"
    )
    console.print(f"[bold]{mode_title}[/bold]")

    if normalized_mode == "advanced":
        _render_frontend_solution_confirmation_wizard(snapshot)
    else:
        _render_frontend_solution_confirmation_recommendation(snapshot)
    _render_frontend_solution_confirmation_final(snapshot)

    artifact_paths: list[Path] = []
    latest_snapshot_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        if snapshot.preflight_status != "blocked":
            if not supports_builtin_frontend_provider_profile_artifacts(
                snapshot.effective_provider_id
            ):
                console.print(
                    "\n[bold red]Unsupported frontend provider profile artifacts[/bold red]"
                )
                console.print(
                    "  - "
                    f"provider_id: {snapshot.effective_provider_id}",
                    markup=False,
                )
                console.print(
                    "  - supported built-in providers: enterprise-vue2, public-primevue",
                    markup=False,
                )
                console.print(
                    "  - use `--dry-run` or choose a built-in provider before executing",
                    markup=False,
                )
                raise typer.Exit(code=1)
            artifact_paths = materialize_frontend_solution_confirmation_artifacts(
                root,
                style_packs=build_builtin_style_pack_manifests(),
                install_strategies=build_builtin_install_strategies(),
                snapshot=snapshot,
            )
            artifact_paths.extend(
                materialize_builtin_frontend_provider_profile_artifacts(
                    root,
                    provider_id=snapshot.effective_provider_id,
                )
            )
            latest_snapshot_path = (
                frontend_solution_confirmation_memory_root(root) / "latest.yaml"
            )
            console.print("\n[bold cyan]Frontend Solution Confirmation Artifact[/bold cyan]")
            console.print(
                f"  - saved: {latest_snapshot_path.relative_to(root)}",
                markup=False,
            )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = _frontend_solution_confirmation_report_lines(
            manifest=manifest,
            mode_title=mode_title,
            snapshot=snapshot,
            mode=normalized_mode,
            latest_snapshot_path=latest_snapshot_path,
            artifact_paths=artifact_paths,
        )
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        if continue_execution:
            console.print(
                "[bold yellow]`--continue` is only available together with `--execute`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        raise typer.Exit(code=0)

    if snapshot.preflight_status == "blocked":
        console.print(
            "\n[bold red]Frontend solution confirmation blocked[/bold red]"
        )
        raise typer.Exit(code=1)

    console.print(
        "\n[bold green]Frontend solution confirmation materialized[/bold green]"
    )
    if not continue_execution:
        raise typer.Exit(code=0)

    changed_fields = _frontend_solution_confirmation_change_fields(snapshot)
    requires_effective_change_ack = bool(changed_fields)
    if requires_effective_change_ack and not ack_effective_change:
        console.print(
            "\n[bold yellow]Effective solution change requires explicit acknowledgement[/bold yellow]"
        )
        console.print(
            "  - requested_* and effective_* differ; review the confirmation diff before continuing into apply",
            markup=False,
        )
        console.print(
            "  - pass `--ack-effective-change` to confirm the effective solution may differ from the requested solution",
            markup=False,
        )
        raise typer.Exit(code=2)

    apply_request = svc.build_frontend_managed_delivery_apply_request(
        second_confirmation_acknowledged=(
            ack_effective_change or not requires_effective_change_ack
        )
    )
    _render_managed_delivery_apply_guard(
        "Program Managed Delivery Apply Execute",
        apply_request,
    )
    apply_result = svc.execute_frontend_managed_delivery_apply(
        request=apply_request,
        confirmed=True,
    )
    artifact_path = svc.write_frontend_managed_delivery_apply_artifact(
        request=apply_request,
        result=apply_result,
    )
    _render_managed_delivery_apply_result(root, apply_result, artifact_path)
    raise typer.Exit(code=0 if apply_result.passed else 1)


@program_app.command("provider-patch-handoff")
def program_provider_patch_handoff(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
) -> None:
    """Show the readonly frontend provider patch handoff payload."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build provider patch handoff.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    handoff = svc.build_frontend_provider_patch_handoff(mf)

    if handoff.steps:
        table = Table(title="Program Frontend Provider Patch Handoff")
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Patch Availability")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in handoff.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.patch_availability_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Provider Patch Handoff Steps[/bold cyan]")
        for step in handoff.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.patch_availability_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions):
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend provider patch handoff required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Patch Handoff[/bold cyan]")
    console.print(
        f"  - source runtime artifact: {handoff.runtime_artifact_path}",
        markup=False,
    )
    console.print(
        f"  - patch availability: {handoff.patch_availability_state}",
        markup=False,
    )
    if handoff.runtime_generated_at:
        console.print(
            f"  - runtime generated_at: {handoff.runtime_generated_at}",
            markup=False,
        )
    for summary in _dedupe_cli_text_items(handoff.patch_summaries):
        console.print(f"  - patch summary: {summary}", markup=False)
    for blocker in _dedupe_cli_text_items(handoff.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if handoff.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(handoff.warnings):
            console.print(f"  - {warning}")

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            "# Program Frontend Provider Patch Handoff",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source runtime artifact: `{handoff.runtime_artifact_path}`",
            f"- Patch availability: `{handoff.patch_availability_state}`",
        ]
        if handoff.runtime_generated_at:
            lines.append(f"- Runtime generated_at: `{handoff.runtime_generated_at}`")
        lines.append("")
        if handoff.steps:
            lines.append("## Steps")
            lines.append("")
            for step in handoff.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Patch availability: `{step.patch_availability_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if handoff.patch_summaries:
            lines.append("## Patch Summaries")
            lines.append("")
            lines.extend(
                [
                    f"- {summary}"
                    for summary in _dedupe_cli_text_items(handoff.patch_summaries)
                ]
            )
            lines.append("")
        if handoff.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(handoff.remaining_blockers)])
            lines.append("")
        if handoff.warnings:
            lines.append("## Warnings")
            lines.append("")
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(handoff.warnings)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if handoff.warnings and not handoff.runtime_generated_at:
        raise typer.Exit(code=1)
    raise typer.Exit(code=0)


@program_app.command("provider-patch-apply")
def program_provider_patch_apply(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded provider patch apply request or explicitly execute the guarded apply baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded provider patch apply execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend provider patch apply baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build provider patch apply.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_provider_patch_apply_request(mf)
    mode_title = (
        "Program Frontend Provider Patch Apply Dry-Run"
        if dry_run
        else "Program Frontend Provider Patch Apply Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Patch Availability")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.patch_availability_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Provider Patch Apply Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.patch_availability_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No guarded frontend provider patch apply steps required.[/green]")

    console.print("\n[bold cyan]Frontend Provider Patch Apply Guard[/bold cyan]")
    console.print(f"  - source handoff: {request.handoff_source_path}", markup=False)
    console.print(
        f"  - patch apply state: {request.patch_apply_state}",
        markup=False,
    )
    console.print(
        f"  - patch availability: {request.patch_availability_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.handoff_generated_at:
        console.print(
            f"  - handoff generated_at: {request.handoff_generated_at}",
            markup=False,
        )
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    apply_result = None
    apply_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        apply_result = svc.execute_frontend_provider_patch_apply(
            mf,
            request=request,
            confirmed=True,
        )
        apply_artifact_path = svc.write_frontend_provider_patch_apply_artifact(
            mf,
            request=request,
            result=apply_result,
        )
        _render_frontend_provider_patch_apply_result(apply_result)
        console.print("\n[bold cyan]Frontend Provider Patch Apply Artifact[/bold cyan]")
        console.print(
            f"  - saved: {apply_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source handoff: `{request.handoff_source_path}`",
            f"- Patch apply state: `{request.patch_apply_state}`",
            f"- Patch availability: `{request.patch_availability_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.handoff_generated_at:
            lines.append(f"- Handoff generated_at: `{request.handoff_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Patch availability: `{step.patch_availability_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if apply_result is not None:
            lines.append("## Frontend Provider Patch Apply Result")
            lines.append("")
            lines.append(f"- Apply result: `{apply_result.apply_result}`")
            lines.append(f"- Patch apply state: `{apply_result.patch_apply_state}`")
            lines.append(f"- Confirmed: `{str(apply_result.confirmed).lower()}`")
            if apply_result.apply_summaries:
                lines.append("- Apply summaries:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(apply_result.apply_summaries)])
            if apply_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(apply_result.written_paths)])
            if apply_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(apply_result.remaining_blockers)])
            lines.append("")
        if apply_artifact_path is not None:
            lines.append("## Frontend Provider Patch Apply Artifact")
            lines.append("")
            lines.append(f"- `{apply_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (apply_result is not None and apply_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if apply_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(apply_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert apply_result is not None
    if apply_result.passed:
        console.print("\n[bold green]Frontend provider patch apply completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend provider patch apply incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("cross-spec-writeback")
def program_cross_spec_writeback(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded cross-spec writeback request or explicitly execute the guarded writeback baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded cross-spec writeback execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend cross-spec writeback baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build cross-spec writeback.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_cross_spec_writeback_request(mf)
    mode_title = (
        "Program Frontend Cross-Spec Writeback Dry-Run"
        if dry_run
        else "Program Frontend Cross-Spec Writeback Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Writeback State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.writeback_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Cross-Spec Writeback Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.writeback_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No guarded frontend cross-spec writeback steps required.[/green]")

    console.print("\n[bold cyan]Frontend Cross-Spec Writeback Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - writeback state: {request.writeback_state}", markup=False)
    console.print(f"  - apply result: {request.apply_result}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    writeback_result = None
    writeback_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        writeback_result = svc.execute_frontend_cross_spec_writeback(
            mf,
            request=request,
            confirmed=True,
        )
        writeback_artifact_path = svc.write_frontend_cross_spec_writeback_artifact(
            mf,
            request=request,
            result=writeback_result,
        )
        _render_frontend_cross_spec_writeback_result(writeback_result)
        console.print("\n[bold cyan]Frontend Cross-Spec Writeback Artifact[/bold cyan]")
        console.print(
            f"  - saved: {writeback_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Writeback state: `{request.writeback_state}`",
            f"- Apply result: `{request.apply_result}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Writeback state: `{step.writeback_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if writeback_result is not None:
            lines.append("## Frontend Cross-Spec Writeback Result")
            lines.append("")
            lines.append(
                f"- Orchestration result: `{writeback_result.orchestration_result}`"
            )
            lines.append(f"- Writeback state: `{writeback_result.writeback_state}`")
            lines.append(f"- Confirmed: `{str(writeback_result.confirmed).lower()}`")
            if writeback_result.orchestration_summaries:
                lines.append("- Orchestration summaries:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(writeback_result.orchestration_summaries)]
                )
            if writeback_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(writeback_result.written_paths)])
            if writeback_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(writeback_result.remaining_blockers)]
                )
            lines.append("")
        if writeback_artifact_path is not None:
            lines.append("## Frontend Cross-Spec Writeback Artifact")
            lines.append("")
            lines.append(f"- `{writeback_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (writeback_result is not None and writeback_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if writeback_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(writeback_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert writeback_result is not None
    if writeback_result.passed:
        console.print("\n[bold green]Frontend cross-spec writeback completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend cross-spec writeback incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("guarded-registry")
def program_guarded_registry(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview guarded frontend registry orchestration or explicitly execute the guarded registry baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm guarded registry execute mode.",
    ),
) -> None:
    """Preview or execute the guarded frontend registry baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build guarded registry request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_guarded_registry_request(mf)
    mode_title = (
        "Program Frontend Guarded Registry Dry-Run"
        if dry_run
        else "Program Frontend Guarded Registry Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Registry State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.registry_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Guarded Registry Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.registry_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No guarded frontend registry steps required.[/green]")

    console.print("\n[bold cyan]Frontend Guarded Registry Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - registry state: {request.registry_state}", markup=False)
    console.print(f"  - writeback state: {request.writeback_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    registry_result = None
    registry_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        registry_result = svc.execute_frontend_guarded_registry(
            mf,
            request=request,
            confirmed=True,
        )
        registry_artifact_path = svc.write_frontend_guarded_registry_artifact(
            mf,
            request=request,
            result=registry_result,
        )
        _render_frontend_guarded_registry_result(registry_result)
        console.print("\n[bold cyan]Frontend Guarded Registry Artifact[/bold cyan]")
        console.print(
            f"  - saved: {registry_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Registry state: `{request.registry_state}`",
            f"- Writeback state: `{request.writeback_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Registry state: `{step.registry_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if registry_result is not None:
            lines.append("## Frontend Guarded Registry Result")
            lines.append("")
            lines.append(f"- Registry result: `{registry_result.registry_result}`")
            lines.append(f"- Registry state: `{registry_result.registry_state}`")
            lines.append(f"- Confirmed: `{str(registry_result.confirmed).lower()}`")
            if registry_result.registry_summaries:
                lines.append("- Registry summaries:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(registry_result.registry_summaries)])
            if registry_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(registry_result.written_paths)])
            if registry_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(registry_result.remaining_blockers)])
            lines.append("")
        if registry_artifact_path is not None:
            lines.append("## Frontend Guarded Registry Artifact")
            lines.append("")
            lines.append(f"- `{registry_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (registry_result is not None and registry_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if registry_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(registry_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert registry_result is not None
    if registry_result.passed:
        console.print("\n[bold green]Frontend guarded registry completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend guarded registry incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("broader-governance")
def program_broader_governance(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview broader frontend governance orchestration or explicitly execute the broader governance baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm broader governance execute mode.",
    ),
) -> None:
    """Preview or execute the broader frontend governance baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build broader governance request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_broader_governance_request(mf)
    mode_title = (
        "Program Frontend Broader Governance Dry-Run"
        if dry_run
        else "Program Frontend Broader Governance Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Governance State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.governance_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Broader Governance Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.governance_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No broader frontend governance steps required.[/green]")

    console.print("\n[bold cyan]Frontend Broader Governance Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - governance state: {request.governance_state}", markup=False)
    console.print(f"  - registry state: {request.registry_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    governance_result = None
    governance_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        governance_result = svc.execute_frontend_broader_governance(
            mf,
            request=request,
            confirmed=True,
        )
        governance_artifact_path = svc.write_frontend_broader_governance_artifact(
            mf,
            request=request,
            result=governance_result,
        )
        _render_frontend_broader_governance_result(governance_result)
        console.print("\n[bold cyan]Frontend Broader Governance Artifact[/bold cyan]")
        console.print(
            f"  - saved: {governance_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Governance state: `{request.governance_state}`",
            f"- Registry state: `{request.registry_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Governance state: `{step.governance_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if governance_result is not None:
            lines.append("## Frontend Broader Governance Result")
            lines.append("")
            lines.append(
                f"- Governance result: `{governance_result.governance_result}`"
            )
            lines.append(f"- Governance state: `{governance_result.governance_state}`")
            lines.append(f"- Confirmed: `{str(governance_result.confirmed).lower()}`")
            if governance_result.governance_summaries:
                lines.append("- Governance summaries:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(governance_result.governance_summaries)]
                )
            if governance_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(governance_result.written_paths)])
            if governance_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(governance_result.remaining_blockers)]
                )
            lines.append("")
        if governance_artifact_path is not None:
            lines.append("## Frontend Broader Governance Artifact")
            lines.append("")
            lines.append(f"- `{governance_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (
            governance_result is not None and governance_result.warnings
        ):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if governance_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(governance_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert governance_result is not None
    if governance_result.passed:
        console.print("\n[bold green]Frontend broader governance completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend broader governance incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("final-governance")
def program_final_governance(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview final frontend governance orchestration or explicitly execute the final governance baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm final governance execute mode.",
    ),
) -> None:
    """Preview or execute the final frontend governance baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build final governance request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_final_governance_request(mf)
    mode_title = (
        "Program Frontend Final Governance Dry-Run"
        if dry_run
        else "Program Frontend Final Governance Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Final Governance State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.final_governance_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Final Governance Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.final_governance_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No final frontend governance steps required.[/green]")

    console.print("\n[bold cyan]Frontend Final Governance Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(
        f"  - final governance state: {request.final_governance_state}",
        markup=False,
    )
    console.print(f"  - governance state: {request.governance_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    final_governance_result = None
    final_governance_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        final_governance_result = svc.execute_frontend_final_governance(
            mf,
            request=request,
            confirmed=True,
        )
        final_governance_artifact_path = svc.write_frontend_final_governance_artifact(
            mf,
            request=request,
            result=final_governance_result,
        )
        _render_frontend_final_governance_result(final_governance_result)
        console.print("\n[bold cyan]Frontend Final Governance Artifact[/bold cyan]")
        console.print(
            f"  - saved: {final_governance_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Final governance state: `{request.final_governance_state}`",
            f"- Governance state: `{request.governance_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Final governance state: `{step.final_governance_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if final_governance_result is not None:
            lines.append("## Frontend Final Governance Result")
            lines.append("")
            lines.append(
                "- Final governance result: "
                + f"`{final_governance_result.final_governance_result}`"
            )
            lines.append(
                "- Final governance state: "
                + f"`{final_governance_result.final_governance_state}`"
            )
            lines.append(
                f"- Confirmed: `{str(final_governance_result.confirmed).lower()}`"
            )
            if final_governance_result.final_governance_summaries:
                lines.append("- Final governance summaries:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in final_governance_result.final_governance_summaries
                    ]
                )
            if final_governance_result.written_paths:
                lines.append("- Written paths:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(final_governance_result.written_paths)]
                )
            if final_governance_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(final_governance_result.remaining_blockers)
                    ]
                )
            lines.append("")
        if final_governance_artifact_path is not None:
            lines.append("## Frontend Final Governance Artifact")
            lines.append("")
            lines.append(f"- `{final_governance_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (
            final_governance_result is not None and final_governance_result.warnings
        ):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if final_governance_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(final_governance_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert final_governance_result is not None
    if final_governance_result.passed:
        console.print("\n[bold green]Frontend final governance completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend final governance incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("writeback-persistence")
def program_writeback_persistence(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend writeback persistence orchestration or explicitly execute the writeback persistence baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm writeback persistence execute mode.",
    ),
) -> None:
    """Preview or execute the frontend writeback persistence baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build writeback persistence request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_writeback_persistence_request(mf)
    mode_title = (
        "Program Frontend Writeback Persistence Dry-Run"
        if dry_run
        else "Program Frontend Writeback Persistence Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Persistence State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.persistence_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Writeback Persistence Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.persistence_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend writeback persistence steps required.[/green]")

    console.print("\n[bold cyan]Frontend Writeback Persistence Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - persistence state: {request.persistence_state}", markup=False)
    console.print(
        f"  - final governance state: {request.final_governance_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    persistence_result = None
    persistence_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        persistence_result = svc.execute_frontend_writeback_persistence(
            mf,
            request=request,
            confirmed=True,
        )
        persistence_artifact_path = svc.write_frontend_writeback_persistence_artifact(
            mf,
            request=request,
            result=persistence_result,
        )
        _render_frontend_writeback_persistence_result(persistence_result)
        console.print("\n[bold cyan]Frontend Writeback Persistence Artifact[/bold cyan]")
        console.print(
            f"  - saved: {persistence_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Persistence state: `{request.persistence_state}`",
            f"- Final governance state: `{request.final_governance_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Persistence state: `{step.persistence_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if persistence_result is not None:
            lines.append("## Frontend Writeback Persistence Result")
            lines.append("")
            lines.append(
                f"- Persistence result: `{persistence_result.persistence_result}`"
            )
            lines.append(f"- Persistence state: `{persistence_result.persistence_state}`")
            lines.append(f"- Confirmed: `{str(persistence_result.confirmed).lower()}`")
            if persistence_result.persistence_summaries:
                lines.append("- Persistence summaries:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(persistence_result.persistence_summaries)]
                )
            if persistence_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(persistence_result.written_paths)])
            if persistence_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(persistence_result.remaining_blockers)]
                )
            lines.append("")
        if persistence_artifact_path is not None:
            lines.append("## Frontend Writeback Persistence Artifact")
            lines.append("")
            lines.append(f"- `{persistence_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (
            persistence_result is not None and persistence_result.warnings
        ):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if persistence_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(persistence_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert persistence_result is not None
    if persistence_result.passed:
        console.print("\n[bold green]Frontend writeback persistence completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend writeback persistence incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("persisted-write-proof")
def program_persisted_write_proof(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend persisted write proof orchestration or explicitly execute the persisted write proof baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm persisted write proof execute mode.",
    ),
) -> None:
    """Preview or execute the frontend persisted write proof baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build persisted write proof request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_persisted_write_proof_request(mf)
    mode_title = (
        "Program Frontend Persisted Write Proof Dry-Run"
        if dry_run
        else "Program Frontend Persisted Write Proof Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Proof State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.proof_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Persisted Write Proof Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.proof_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend persisted write proof steps required.[/green]")

    console.print("\n[bold cyan]Frontend Persisted Write Proof Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - proof state: {request.proof_state}", markup=False)
    console.print(
        f"  - persistence state: {request.persistence_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    proof_result = None
    proof_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        proof_result = svc.execute_frontend_persisted_write_proof(
            mf,
            request=request,
            confirmed=True,
        )
        proof_artifact_path = svc.write_frontend_persisted_write_proof_artifact(
            mf,
            request=request,
            result=proof_result,
        )
        _render_frontend_persisted_write_proof_result(proof_result)
        console.print("\n[bold cyan]Frontend Persisted Write Proof Artifact[/bold cyan]")
        console.print(
            f"  - saved: {proof_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Proof state: `{request.proof_state}`",
            f"- Persistence state: `{request.persistence_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Proof state: `{step.proof_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if proof_result is not None:
            lines.append("## Frontend Persisted Write Proof Result")
            lines.append("")
            lines.append(f"- Proof result: `{proof_result.proof_result}`")
            lines.append(f"- Proof state: `{proof_result.proof_state}`")
            lines.append(f"- Confirmed: `{str(proof_result.confirmed).lower()}`")
            if proof_result.proof_summaries:
                lines.append("- Proof summaries:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(proof_result.proof_summaries)])
            if proof_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(proof_result.written_paths)])
            if proof_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(proof_result.remaining_blockers)])
            lines.append("")
        if proof_artifact_path is not None:
            lines.append("## Frontend Persisted Write Proof Artifact")
            lines.append("")
            lines.append(f"- `{proof_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (proof_result is not None and proof_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if proof_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(proof_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert proof_result is not None
    if proof_result.passed:
        console.print("\n[bold green]Frontend persisted write proof completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend persisted write proof incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("final-proof-publication")
def program_final_proof_publication(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend final proof publication orchestration or explicitly execute the final proof publication baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm final proof publication execute mode.",
    ),
) -> None:
    """Preview or execute the frontend final proof publication baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build final proof publication request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_final_proof_publication_request(mf)
    mode_title = (
        "Program Frontend Final Proof Publication Dry-Run"
        if dry_run
        else "Program Frontend Final Proof Publication Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Publication State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.publication_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Final Proof Publication Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.publication_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend final proof publication steps required.[/green]")

    console.print("\n[bold cyan]Frontend Final Proof Publication Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(
        f"  - publication state: {request.publication_state}",
        markup=False,
    )
    console.print(f"  - proof state: {request.proof_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    publication_result = None
    publication_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        publication_result = svc.execute_frontend_final_proof_publication(
            mf,
            request=request,
            confirmed=True,
        )
        publication_artifact_path = svc.write_frontend_final_proof_publication_artifact(
            mf,
            request=request,
            result=publication_result,
        )
        _render_frontend_final_proof_publication_result(publication_result)
        console.print("\n[bold cyan]Frontend Final Proof Publication Artifact[/bold cyan]")
        console.print(
            f"  - saved: {publication_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Publication state: `{request.publication_state}`",
            f"- Proof state: `{request.proof_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Publication state: `{step.publication_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if publication_result is not None:
            lines.append("## Frontend Final Proof Publication Result")
            lines.append("")
            lines.append(
                f"- Publication result: `{publication_result.publication_result}`"
            )
            lines.append(
                f"- Publication state: `{publication_result.publication_state}`"
            )
            lines.append(
                f"- Confirmed: `{str(publication_result.confirmed).lower()}`"
            )
            if publication_result.publication_summaries:
                lines.append("- Publication summaries:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(publication_result.publication_summaries)]
                )
            if publication_result.written_paths:
                lines.append("- Written paths:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(publication_result.written_paths)]
                )
            if publication_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(publication_result.remaining_blockers)]
                )
            lines.append("")
        if publication_artifact_path is not None:
            lines.append("## Frontend Final Proof Publication Artifact")
            lines.append("")
            lines.append(f"- `{publication_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (
            publication_result is not None and publication_result.warnings
        ):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if publication_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(publication_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert publication_result is not None
    if publication_result.passed:
        console.print("\n[bold green]Frontend final proof publication completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend final proof publication incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("final-proof-closure")
def program_final_proof_closure(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend final proof closure orchestration or explicitly execute the final proof closure baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm final proof closure execute mode.",
    ),
) -> None:
    """Preview or execute the frontend final proof closure baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build final proof closure request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_final_proof_closure_request(mf)
    mode_title = (
        "Program Frontend Final Proof Closure Dry-Run"
        if dry_run
        else "Program Frontend Final Proof Closure Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Closure State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.closure_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Final Proof Closure Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.closure_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend final proof closure steps required.[/green]")

    console.print("\n[bold cyan]Frontend Final Proof Closure Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - closure state: {request.closure_state}", markup=False)
    console.print(f"  - publication state: {request.publication_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    closure_result = None
    closure_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        closure_result = svc.execute_frontend_final_proof_closure(
            mf,
            request=request,
            confirmed=True,
        )
        closure_artifact_path = svc.write_frontend_final_proof_closure_artifact(
            mf,
            request=request,
            result=closure_result,
        )
        _render_frontend_final_proof_closure_result(closure_result)
        console.print("\n[bold cyan]Frontend Final Proof Closure Artifact[/bold cyan]")
        console.print(
            f"  - saved: {closure_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Closure state: `{request.closure_state}`",
            f"- Publication state: `{request.publication_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Closure state: `{step.closure_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if closure_result is not None:
            lines.append("## Frontend Final Proof Closure Result")
            lines.append("")
            lines.append(f"- Closure result: `{closure_result.closure_result}`")
            lines.append(f"- Closure state: `{closure_result.closure_state}`")
            lines.append(f"- Confirmed: `{str(closure_result.confirmed).lower()}`")
            if closure_result.closure_summaries:
                lines.append("- Closure summaries:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(closure_result.closure_summaries)])
            if closure_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(closure_result.written_paths)])
            if closure_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(closure_result.remaining_blockers)]
                )
            lines.append("")
        if closure_artifact_path is not None:
            lines.append("## Frontend Final Proof Closure Artifact")
            lines.append("")
            lines.append(f"- `{closure_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (closure_result is not None and closure_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if closure_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(closure_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert closure_result is not None
    if closure_result.passed:
        console.print("\n[bold green]Frontend final proof closure completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend final proof closure incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("final-proof-archive")
def program_final_proof_archive(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend final proof archive orchestration or explicitly execute the final proof archive baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm final proof archive execute mode.",
    ),
) -> None:
    """Preview or execute the frontend final proof archive baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build final proof archive request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_final_proof_archive_request(mf)
    mode_title = (
        "Program Frontend Final Proof Archive Dry-Run"
        if dry_run
        else "Program Frontend Final Proof Archive Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Archive State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.archive_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print("\n[bold cyan]Frontend Final Proof Archive Steps[/bold cyan]")
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.archive_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print("[green]No frontend final proof archive steps required.[/green]")

    console.print("\n[bold cyan]Frontend Final Proof Archive Guard[/bold cyan]")
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - archive state: {request.archive_state}", markup=False)
    console.print(f"  - closure state: {request.closure_state}", markup=False)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    archive_result = None
    archive_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        archive_result = svc.execute_frontend_final_proof_archive(
            mf,
            request=request,
            confirmed=True,
        )
        archive_artifact_path = svc.write_frontend_final_proof_archive_artifact(
            mf,
            request=request,
            result=archive_result,
        )
        _render_frontend_final_proof_archive_result(archive_result)
        console.print("\n[bold cyan]Frontend Final Proof Archive Artifact[/bold cyan]")
        console.print(
            f"  - saved: {archive_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Archive state: `{request.archive_state}`",
            f"- Closure state: `{request.closure_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Archive state: `{step.archive_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if archive_result is not None:
            lines.append("## Frontend Final Proof Archive Result")
            lines.append("")
            lines.append(f"- Archive result: `{archive_result.archive_result}`")
            lines.append(f"- Archive state: `{archive_result.archive_state}`")
            lines.append(f"- Confirmed: `{str(archive_result.confirmed).lower()}`")
            if archive_result.archive_summaries:
                lines.append("- Archive summaries:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(archive_result.archive_summaries)])
            if archive_result.written_paths:
                lines.append("- Written paths:")
                lines.extend([f"  - {item}" for item in _dedupe_cli_text_items(archive_result.written_paths)])
            if archive_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [f"  - {item}" for item in _dedupe_cli_text_items(archive_result.remaining_blockers)]
                )
            lines.append("")
        if archive_artifact_path is not None:
            lines.append("## Frontend Final Proof Archive Artifact")
            lines.append("")
            lines.append(f"- `{archive_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (archive_result is not None and archive_result.warnings):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if archive_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(archive_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert archive_result is not None
    if archive_result.passed:
        console.print("\n[bold green]Frontend final proof archive completed[/bold green]")
        raise typer.Exit(code=0)

    console.print("\n[bold red]Frontend final proof archive incomplete[/bold red]")
    raise typer.Exit(code=1)


@program_app.command("final-proof-archive-thread-archive")
def program_final_proof_archive_thread_archive(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend final proof archive thread archive or explicitly execute the bounded thread archive baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm final proof archive thread archive execute mode.",
    ),
) -> None:
    """Preview or execute the bounded frontend final proof archive thread archive baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build final proof archive thread archive request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_final_proof_archive_thread_archive_request(mf)
    mode_title = (
        "Program Frontend Final Proof Archive Thread Archive Dry-Run"
        if dry_run
        else "Program Frontend Final Proof Archive Thread Archive Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Thread Archive State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.thread_archive_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print(
            "\n[bold cyan]Frontend Final Proof Archive Thread Archive Steps[/bold cyan]"
        )
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.thread_archive_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print(
            "[green]No frontend final proof archive thread archive steps required.[/green]"
        )

    console.print(
        "\n[bold cyan]Frontend Final Proof Archive Thread Archive Guard[/bold cyan]"
    )
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(f"  - archive state: {request.archive_state}", markup=False)
    console.print(
        f"  - thread archive state: {request.thread_archive_state}",
        markup=False,
    )
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    thread_archive_result = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        thread_archive_result = (
            svc.execute_frontend_final_proof_archive_thread_archive(
                mf,
                request=request,
                confirmed=True,
            )
        )
        _render_frontend_final_proof_archive_thread_archive_result(
            thread_archive_result
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Archive state: `{request.archive_state}`",
            f"- Thread archive state: `{request.thread_archive_state}`",
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Thread archive state: `{step.thread_archive_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if thread_archive_result is not None:
            lines.append("## Frontend Final Proof Archive Thread Archive Result")
            lines.append("")
            lines.append(
                f"- Thread archive result: `{thread_archive_result.thread_archive_result}`"
            )
            lines.append(
                f"- Thread archive state: `{thread_archive_result.thread_archive_state}`"
            )
            lines.append(
                f"- Confirmed: `{str(thread_archive_result.confirmed).lower()}`"
            )
            if thread_archive_result.thread_archive_summaries:
                lines.append("- Thread archive summaries:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(thread_archive_result.thread_archive_summaries)
                    ]
                )
            if thread_archive_result.written_paths:
                lines.append("- Written paths:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(
                            thread_archive_result.written_paths
                        )
                    ]
                )
            if thread_archive_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(thread_archive_result.remaining_blockers)
                    ]
                )
            lines.append("")
        lines.append("## Frontend Final Proof Archive Artifact")
        lines.append("")
        lines.append(f"- `{request.artifact_source_path}`")
        lines.append("")
        if request.warnings or (
            thread_archive_result is not None and thread_archive_result.warnings
        ):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if thread_archive_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(thread_archive_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert thread_archive_result is not None
    if thread_archive_result.passed:
        console.print(
            "\n[bold green]Frontend final proof archive thread archive completed[/bold green]"
        )
        raise typer.Exit(code=0)

    console.print(
        "\n[bold red]Frontend final proof archive thread archive incomplete[/bold red]"
    )
    raise typer.Exit(code=1)


@program_app.command("final-proof-archive-project-cleanup")
def program_final_proof_archive_project_cleanup(
    manifest: str = typer.Option(
        "program-manifest.yaml",
        "--manifest",
        help="Path to program manifest relative to project root.",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--execute",
        help="Preview frontend final proof archive project cleanup or explicitly execute the bounded project cleanup baseline.",
    ),
    report: str = typer.Option(
        "",
        "--report",
        help="Optional report output path relative to project root.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm final proof archive project cleanup execute mode.",
    ),
) -> None:
    """Preview or execute the bounded frontend final proof archive project cleanup baseline."""
    root = _resolve_root()
    svc = ProgramService(root, root / manifest)

    try:
        mf = svc.load_manifest()
    except Exception as exc:
        console.print(f"[red]Failed to load manifest: {exc}[/red]")
        raise typer.Exit(code=2) from None

    result = svc.validate_manifest(mf)
    if not result.valid:
        console.print(
            "[bold red]Manifest invalid; cannot build final proof archive project cleanup request.[/bold red]"
        )
        for e in _dedupe_cli_text_items(result.errors):
            console.print(f"  - {e}")
        raise typer.Exit(code=1)

    request = svc.build_frontend_final_proof_archive_project_cleanup_request(mf)
    mode_title = (
        "Program Frontend Final Proof Archive Project Cleanup Dry-Run"
        if dry_run
        else "Program Frontend Final Proof Archive Project Cleanup Execute"
    )

    if request.steps:
        table = Table(title=mode_title)
        table.add_column("Spec")
        table.add_column("Path")
        table.add_column("Project Cleanup State")
        table.add_column("Pending Inputs")
        table.add_column("Next Actions")
        for step in request.steps:
            table.add_row(
                step.spec_id,
                step.path,
                step.project_cleanup_state,
                ", ".join(_dedupe_cli_text_items(step.pending_inputs)) or "-",
                " ; ".join(_dedupe_cli_text_items(step.suggested_next_actions)) or "-",
            )
        console.print(table)
        console.print(
            "\n[bold cyan]Frontend Final Proof Archive Project Cleanup Steps[/bold cyan]"
        )
        for step in request.steps:
            console.print(
                f"  - {step.spec_id}: {step.path} [{step.project_cleanup_state}]",
                markup=False,
            )
            for pending in _dedupe_cli_text_items(step.pending_inputs):
                console.print(f"    pending input: {pending}", markup=False)
            for action in _dedupe_cli_text_items(step.suggested_next_actions)[:3]:
                console.print(f"    next action: {action}", markup=False)
            for plain_text in _dedupe_cli_text_items(step.plain_language_blockers)[:2]:
                console.print(f"    explain: {plain_text}", markup=False)
            for next_step in _dedupe_cli_text_items(step.recommended_next_steps)[:2]:
                console.print(f"    next step: {next_step}", markup=False)
    else:
        console.print(
            "[green]No frontend final proof archive project cleanup steps required.[/green]"
        )

    console.print(
        "\n[bold cyan]Frontend Final Proof Archive Project Cleanup Guard[/bold cyan]"
    )
    console.print(f"  - source artifact: {request.artifact_source_path}", markup=False)
    console.print(
        f"  - project cleanup state: {request.project_cleanup_state}",
        markup=False,
    )
    console.print(
        f"  - thread archive state: {request.thread_archive_state}",
        markup=False,
    )
    console.print(
        f"  - cleanup targets state: {request.cleanup_targets_state}",
        markup=False,
    )
    console.print(
        f"  - cleanup targets count: {len(request.cleanup_targets)}",
        markup=False,
    )
    console.print(
        "  - cleanup target eligibility state: "
        + str(request.cleanup_target_eligibility_state),
        markup=False,
    )
    console.print(
        "  - cleanup target eligibility count: "
        + str(len(request.cleanup_target_eligibility)),
        markup=False,
    )
    console.print(
        "  - cleanup preview plan state: "
        + str(request.cleanup_preview_plan_state),
        markup=False,
    )
    console.print(
        "  - cleanup preview plan count: "
        + str(len(request.cleanup_preview_plan)),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal state: "
        + str(request.cleanup_mutation_proposal_state),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal count: "
        + str(len(request.cleanup_mutation_proposal)),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal approval state: "
        + str(request.cleanup_mutation_proposal_approval_state),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal approval count: "
        + str(len(request.cleanup_mutation_proposal_approval)),
        markup=False,
    )
    console.print(
        "  - cleanup mutation execution gating state: "
        + str(request.cleanup_mutation_execution_gating_state),
        markup=False,
    )
    console.print(
        "  - cleanup mutation execution gating count: "
        + str(len(request.cleanup_mutation_execution_gating)),
        markup=False,
    )
    for line in _project_cleanup_truth_output_lines(request):
        console.print(line, markup=False, soft_wrap=True)
    console.print(
        f"  - confirmation required: {str(request.confirmation_required).lower()}",
        markup=False,
    )
    if request.artifact_generated_at:
        console.print(
            f"  - artifact generated_at: {request.artifact_generated_at}",
            markup=False,
        )
    for path in _dedupe_cli_text_items(request.written_paths):
        console.print(f"  - existing written path: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(request.remaining_blockers):
        console.print(f"  - blocker: {blocker}", markup=False)

    if request.warnings:
        console.print("\n[bold yellow]Warnings[/bold yellow]")
        for warning in _dedupe_cli_text_items(request.warnings):
            console.print(f"  - {warning}")

    project_cleanup_result = None
    project_cleanup_artifact_path: Path | None = None
    if not dry_run:
        if not yes:
            console.print(
                "[bold yellow]`--execute` requires explicit confirmation via `--yes`.[/bold yellow]"
            )
            raise typer.Exit(code=2)
        project_cleanup_result = (
            svc.execute_frontend_final_proof_archive_project_cleanup(
                mf,
                request=request,
                confirmed=True,
            )
        )
        project_cleanup_artifact_path = (
            svc.write_frontend_final_proof_archive_project_cleanup_artifact(
                mf,
                request=request,
                result=project_cleanup_result,
            )
        )
        _render_frontend_final_proof_archive_project_cleanup_result(
            project_cleanup_result
        )
        console.print(
            "\n[bold cyan]Frontend Final Proof Archive Project Cleanup Artifact[/bold cyan]"
        )
        console.print(
            f"  - saved: {project_cleanup_artifact_path.relative_to(root)}",
            markup=False,
        )

    if report:
        report_path = root / report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = [
            f"# {mode_title}",
            "",
            f"- Manifest: `{manifest}`",
            f"- Source artifact: `{request.artifact_source_path}`",
            f"- Project cleanup state: `{request.project_cleanup_state}`",
            f"- Thread archive state: `{request.thread_archive_state}`",
            f"- Cleanup targets state: `{request.cleanup_targets_state}`",
            f"- Cleanup targets count: `{len(request.cleanup_targets)}`",
            (
                "- Cleanup target eligibility state: "
                + f"`{request.cleanup_target_eligibility_state}`"
            ),
            (
                "- Cleanup target eligibility count: "
                + f"`{len(request.cleanup_target_eligibility)}`"
            ),
            f"- Cleanup preview plan state: `{request.cleanup_preview_plan_state}`",
            f"- Cleanup preview plan count: `{len(request.cleanup_preview_plan)}`",
            (
                "- Cleanup mutation proposal state: "
                + f"`{request.cleanup_mutation_proposal_state}`"
            ),
            (
                "- Cleanup mutation proposal count: "
                + f"`{len(request.cleanup_mutation_proposal)}`"
            ),
            (
                "- Cleanup mutation proposal approval state: "
                + f"`{request.cleanup_mutation_proposal_approval_state}`"
            ),
            (
                "- Cleanup mutation proposal approval count: "
                + f"`{len(request.cleanup_mutation_proposal_approval)}`"
            ),
            (
                "- Cleanup mutation execution gating state: "
                + f"`{request.cleanup_mutation_execution_gating_state}`"
            ),
            (
                "- Cleanup mutation execution gating count: "
                + f"`{len(request.cleanup_mutation_execution_gating)}`"
            ),
            f"- Confirmation required: `{str(request.confirmation_required).lower()}`",
        ]
        if request.artifact_generated_at:
            lines.append(f"- Artifact generated_at: `{request.artifact_generated_at}`")
        lines.append("")
        request_detail_lines = _project_cleanup_truth_report_lines(request)
        if request_detail_lines:
            lines.extend(request_detail_lines)
            lines.append("")
        if request.steps:
            lines.append("## Steps")
            lines.append("")
            for step in request.steps:
                lines.extend(
                    [
                        f"### {step.spec_id}",
                        f"- Path: `{step.path}`",
                        f"- Project cleanup state: `{step.project_cleanup_state}`",
                        f"- Pending inputs: `{', '.join(_dedupe_cli_text_items(step.pending_inputs)) or '-'}`",
                        f"- Explain: `{'; '.join(_dedupe_cli_text_items(step.plain_language_blockers)) or '-'}`",
                        f"- Next steps: `{'; '.join(_dedupe_cli_text_items(step.recommended_next_steps)) or '-'}`",
                        "- Suggested next actions:",
                    ]
                )
                lines.extend([f"  - {action}" for action in _dedupe_cli_text_items(step.suggested_next_actions)])
                lines.append("")
        if request.written_paths:
            lines.append("## Existing Written Paths")
            lines.append("")
            lines.extend([f"- {path}" for path in _dedupe_cli_text_items(request.written_paths)])
            lines.append("")
        if request.remaining_blockers:
            lines.append("## Remaining Blockers")
            lines.append("")
            lines.extend([f"- {blocker}" for blocker in _dedupe_cli_text_items(request.remaining_blockers)])
            lines.append("")
        if project_cleanup_result is not None:
            lines.append("## Frontend Final Proof Archive Project Cleanup Result")
            lines.append("")
            lines.append(
                "- Project cleanup result: "
                + f"`{project_cleanup_result.project_cleanup_result}`"
            )
            lines.append(
                "- Project cleanup state: "
                + f"`{project_cleanup_result.project_cleanup_state}`"
            )
            lines.append(
                "- Cleanup targets state: "
                + f"`{project_cleanup_result.cleanup_targets_state}`"
            )
            lines.append(
                "- Cleanup targets count: "
                + f"`{len(project_cleanup_result.cleanup_targets)}`"
            )
            lines.append(
                "- Cleanup target eligibility state: "
                + f"`{project_cleanup_result.cleanup_target_eligibility_state}`"
            )
            lines.append(
                "- Cleanup target eligibility count: "
                + f"`{len(project_cleanup_result.cleanup_target_eligibility)}`"
            )
            lines.append(
                "- Cleanup preview plan state: "
                + f"`{project_cleanup_result.cleanup_preview_plan_state}`"
            )
            lines.append(
                "- Cleanup preview plan count: "
                + f"`{len(project_cleanup_result.cleanup_preview_plan)}`"
            )
            lines.append(
                "- Cleanup mutation proposal state: "
                + f"`{project_cleanup_result.cleanup_mutation_proposal_state}`"
            )
            lines.append(
                "- Cleanup mutation proposal count: "
                + f"`{len(project_cleanup_result.cleanup_mutation_proposal)}`"
            )
            lines.append(
                "- Cleanup mutation proposal approval state: "
                + f"`{project_cleanup_result.cleanup_mutation_proposal_approval_state}`"
            )
            lines.append(
                "- Cleanup mutation proposal approval count: "
                + f"`{len(project_cleanup_result.cleanup_mutation_proposal_approval)}`"
            )
            lines.append(
                "- Cleanup mutation execution gating state: "
                + f"`{project_cleanup_result.cleanup_mutation_execution_gating_state}`"
            )
            lines.append(
                "- Cleanup mutation execution gating count: "
                + f"`{len(project_cleanup_result.cleanup_mutation_execution_gating)}`"
            )
            lines.append(
                f"- Confirmed: `{str(project_cleanup_result.confirmed).lower()}`"
            )
            lines.extend(_project_cleanup_truth_report_lines(project_cleanup_result))
            if project_cleanup_result.project_cleanup_summaries:
                lines.append("- Project cleanup summaries:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(
                            project_cleanup_result.project_cleanup_summaries
                        )
                    ]
                )
            if project_cleanup_result.written_paths:
                lines.append("- Written paths:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(
                            project_cleanup_result.written_paths
                        )
                    ]
                )
            if project_cleanup_result.remaining_blockers:
                lines.append("- Remaining blockers:")
                lines.extend(
                    [
                        f"  - {item}"
                        for item in _dedupe_cli_text_items(project_cleanup_result.remaining_blockers)
                    ]
                )
            lines.append("")
        if project_cleanup_artifact_path is not None:
            lines.append("## Frontend Final Proof Archive Project Cleanup Artifact")
            lines.append("")
            lines.append(f"- `{project_cleanup_artifact_path.relative_to(root)}`")
            lines.append("")
        if request.warnings or (
            project_cleanup_result is not None and project_cleanup_result.warnings
        ):
            lines.append("## Warnings")
            lines.append("")
            warning_lines = _dedupe_cli_text_items(request.warnings)
            if project_cleanup_result is not None:
                warning_lines.extend(_dedupe_cli_text_items(project_cleanup_result.warnings))
            lines.extend([f"- {warning}" for warning in _dedupe_cli_text_items(warning_lines)])
            lines.append("")
        report_path.write_text("\n".join(lines), encoding="utf-8")
        console.print(f"\n[green]Report written:[/green] {report_path}")

    if dry_run:
        raise typer.Exit(code=0)

    assert project_cleanup_result is not None
    if project_cleanup_result.passed:
        console.print(
            "\n[bold green]Frontend final proof archive project cleanup completed[/bold green]"
        )
        raise typer.Exit(code=0)

    console.print(
        "\n[bold red]Frontend final proof archive project cleanup incomplete[/bold red]"
    )
    raise typer.Exit(code=1)


def _format_frontend_readiness(readiness: ProgramFrontendReadiness | None) -> str:
    if readiness is None:
        return "-"

    state = readiness.state
    effective_state = readiness.execute_gate_state or readiness.state
    if readiness.execute_gate_state and readiness.execute_gate_state != readiness.state:
        state = f"{readiness.state} / {readiness.execute_gate_state}"
    elif (
        effective_state == "ready"
        and readiness.decision_reason == "advisory_only"
    ):
        state = f"{readiness.state} / {readiness.decision_reason}"

    details: list[str] = []
    if effective_state != "ready" and readiness.decision_reason:
        details.append(readiness.decision_reason)
    coverage_gaps = _dedupe_cli_text_items(readiness.coverage_gaps)
    blockers = _dedupe_cli_text_items(readiness.blockers)
    if coverage_gaps:
        details.append(", ".join(coverage_gaps[:2]))
    elif effective_state != "ready" and blockers:
        details.append(blockers[0])

    suffix = f" [{'; '.join(details)}]" if details else ""
    return f"{state}{suffix}"


def _format_frontend_evidence_class_status(
    status: ProgramFrontendEvidenceClassStatus | None,
) -> str:
    if status is None or not status.has_blocker:
        return ""

    summary = status.problem_family
    if status.summary_token:
        summary = f"{summary}:{status.summary_token}"
    return f"frontend evidence: {summary}"


def _format_program_status_frontend_cell(
    readiness: ProgramFrontendReadiness | None,
    frontend_evidence_class_status: ProgramFrontendEvidenceClassStatus | None,
) -> str:
    base = _format_frontend_readiness(readiness)
    summary = _format_frontend_evidence_class_status(frontend_evidence_class_status)
    if not summary:
        return base
    if base == "-":
        return summary
    return f"{base} | {summary}"


def _render_frontend_status_lines(rows: list[object]) -> None:
    console.print("\n[bold cyan]Frontend Readiness[/bold cyan]")
    for row in rows:
        spec_id = str(getattr(row, "spec_id", "")).strip() or "unknown-spec"
        readiness = getattr(row, "frontend_readiness", None)
        evidence_class_status = getattr(row, "frontend_evidence_class_status", None)
        console.print(
            f"  - {spec_id}: "
            f"{_format_program_status_frontend_cell(readiness, evidence_class_status)}",
            markup=False,
        )


def _render_frontend_delivery_context_lines(svc: ProgramService) -> None:
    registry = svc.build_frontend_delivery_registry_handoff()
    runtime_adapter = svc.build_frontend_provider_runtime_adapter_handoff()
    status_surface = svc.build_frontend_delivery_status_surface()
    inheritance_surface = svc.build_frontend_inheritance_status_surface()

    console.print("\n[bold cyan]Frontend Delivery Context[/bold cyan]")
    if status_surface:
        status_note = _frontend_delivery_context_status_note(status_surface)
        if status_note:
            console.print(
                f"  - delivery status: {status_note}",
                markup=False,
            )
        console.print(
            "  - scope note: this section covers package download/integration truth only; "
            "later code generation and frontend test inheritance are tracked separately",
            markup=False,
        )
        if inheritance_surface:
            console.print(
                "  - inheritance status: "
                f"{summarize_frontend_inheritance_status_for_display(inheritance_surface)}",
                markup=False,
            )
            inheritance_risk_note = _frontend_inheritance_context_risk_note(
                inheritance_surface
            )
            if inheritance_risk_note:
                console.print(
                    f"  - inheritance risk: {inheritance_risk_note}",
                    markup=False,
                )
        console.print(
            "  - delivery result: "
            f"{humanize_frontend_delivery_apply_state(str(status_surface.get('delivery_state', status_surface.get('apply_state', '-'))))}",
            markup=False,
        )
        console.print(
            "  - download: "
            f"{humanize_frontend_delivery_install_state(str(status_surface.get('install_state', '-')))}",
            markup=False,
        )
        console.print(
            "  - integration: "
            f"{humanize_frontend_delivery_workspace_state(str(status_surface.get('workspace_state', '-')))}",
            markup=False,
        )
        console.print(
            "  - browser gate: "
            f"{humanize_frontend_browser_gate_state(str(status_surface.get('browser_gate_state', '-')))}",
            markup=False,
        )
        apply_artifact_path = str(status_surface.get("apply_artifact_path", "")).strip()
        if apply_artifact_path:
            console.print(
                f"  - apply artifact: {apply_artifact_path}",
                markup=False,
            )
        browser_gate_artifact_path = str(
            status_surface.get("browser_gate_artifact_path", "")
        ).strip()
        if browser_gate_artifact_path:
            console.print(
                f"  - browser gate artifact: {browser_gate_artifact_path}",
                markup=False,
            )
        next_step = _frontend_delivery_context_next_step(status_surface)
        if next_step:
            console.print(
                f"  - next step: {next_step}",
                markup=False,
            )
    console.print(
        "  - selected provider: "
        f"{registry.effective_provider_id or runtime_adapter.effective_provider_id or '-'}",
        markup=False,
    )
    console.print(
        f"  - delivery entry: {registry.entry_id or '-'}",
        markup=False,
    )
    console.print(
        "  - requested frontend stack: "
        f"{registry.requested_frontend_stack or runtime_adapter.requested_frontend_stack or '-'}",
        markup=False,
    )
    console.print(
        "  - effective frontend stack: "
        f"{registry.effective_frontend_stack or runtime_adapter.effective_frontend_stack or '-'}",
        markup=False,
    )
    for package_name in _dedupe_cli_text_items(registry.component_library_packages):
        console.print(f"  - selected package: {package_name}", markup=False)
    console.print(
        "  - runtime adapter carrier: "
        f"{runtime_adapter.carrier_mode or '-'}",
        markup=False,
    )
    console.print(
        "  - runtime adapter delivery: "
        f"{runtime_adapter.runtime_delivery_state or '-'}",
        markup=False,
    )
    console.print(
        "  - runtime adapter evidence: "
        f"{runtime_adapter.evidence_return_state or '-'}",
        markup=False,
    )


def _frontend_delivery_context_status_note(
    status_surface: dict[str, object],
) -> str:
    apply_state = str(status_surface.get("apply_state", "")).strip()
    install_state = str(status_surface.get("install_state", "")).strip()
    workspace_state = str(status_surface.get("workspace_state", "")).strip()
    browser_gate_state = str(status_surface.get("browser_gate_state", "")).strip()

    if (
        apply_state == "not_applied"
        and install_state != "installed"
        and workspace_state != "integrated"
    ):
        return "selection recorded only; packages are not downloaded or integrated into the project yet"
    if install_state == "installed" and workspace_state != "integrated":
        return "packages are downloaded, but project integration is still incomplete"
    if workspace_state == "integrated" and browser_gate_state in {"pending", "not_started"}:
        return "packages are in the project, but browser evidence is still required before delivery can be treated as complete"
    if apply_state == "blocked_before_start":
        return "delivery is blocked before any project mutation happened"
    return ""


def _frontend_delivery_context_next_step(
    status_surface: dict[str, object],
) -> str:
    apply_state = str(status_surface.get("apply_state", "")).strip()
    browser_gate_state = str(status_surface.get("browser_gate_state", "")).strip()

    if apply_state == "not_applied":
        return "uv run ai-sdlc program solution-confirm --execute --continue --yes"
    if (
        apply_state == "apply_succeeded_pending_browser_gate"
        and browser_gate_state in {"pending", "not_started"}
    ):
        return "uv run ai-sdlc program browser-gate-probe --execute"
    return ""


def _frontend_inheritance_context_risk_note(
    inheritance_surface: dict[str, str],
) -> str:
    generation_state = str(inheritance_surface.get("generation", "")).strip()
    quality_state = str(inheritance_surface.get("quality", "")).strip()
    if generation_state == "not_inherited" or quality_state == "not_inherited":
        return (
            "continuing may generate against the wrong component library or validate "
            "against the wrong standard until inheritance is bound"
        )
    if generation_state == "blocked" or quality_state == "blocked":
        return (
            "later code generation or frontend tests remain blocked until inheritance "
            "is repaired"
        )
    return ""


def _render_truth_ledger_lines(surface: dict[str, object]) -> None:
    console.print("\n[bold cyan]Truth Ledger[/bold cyan]")
    console.print(f"  - state: {surface['state']}", markup=False)
    console.print(f"  - snapshot state: {surface['snapshot_state']}", markup=False)
    console.print(f"  - detail: {surface['detail']}", markup=False)
    for action in _dedupe_cli_text_items(surface.get("next_required_actions", [])):
        console.print(f"  - next action: {action}", markup=False)
    release_targets = surface.get("release_targets", [])
    if release_targets:
        console.print(
            "  - release targets: "
            + ", ".join(_dedupe_cli_text_items(release_targets)),
            markup=False,
        )
    _render_truth_release_capability_lines(surface.get("release_capabilities", []))
    migration_pending_count = int(surface.get("migration_pending_count", 0) or 0)
    if migration_pending_count:
        console.print(
            f"  - migration pending: {migration_pending_count}",
            markup=False,
        )
    _render_truth_source_inventory(surface.get("source_inventory"))


def _render_truth_release_capability_lines(items: list[object]) -> None:
    for item in items:
        if hasattr(item, "model_dump"):
            item = item.model_dump(mode="json")
        if not isinstance(item, dict):
            continue
        console.print(
            f"  - capability: {item['capability_id']} | closure={item['closure_state']} | audit={item['audit_state']}",
            markup=False,
        )
        plain_language_blockers = _dedupe_cli_text_items(
            item.get("plain_language_blockers", [])
        )
        recommended_next_steps = _dedupe_cli_text_items(
            item.get("recommended_next_steps", [])
        )
        blocking_reason_summary = str(
            item.get("blocking_reason_summary", "")
        ).strip()
        if blocking_reason_summary and not plain_language_blockers:
            console.print(
                f"    reason: {blocking_reason_summary}",
                markup=False,
            )
        for plain_text in plain_language_blockers:
            console.print(
                f"    explain: {plain_text}",
                markup=False,
            )
        for next_step in recommended_next_steps:
            console.print(
                f"    next step: {next_step}",
                markup=False,
            )
        frontend_delivery_summary = _format_frontend_delivery_truth_for_console(item)
        if frontend_delivery_summary:
            console.print(
                f"    frontend delivery: {frontend_delivery_summary}",
                markup=False,
            )
            console.print(
                "    frontend scope: "
                f"{summarize_frontend_delivery_scope_for_display()}",
                markup=False,
            )
        frontend_inheritance_summary = summarize_frontend_inheritance_status_for_display(
            item.get("frontend_inheritance_status")
            if isinstance(item.get("frontend_inheritance_status"), dict)
            else {}
        )
        if frontend_inheritance_summary:
            console.print(
                f"    frontend inheritance: {frontend_inheritance_summary}",
                markup=False,
            )
        for blocker in _dedupe_cli_text_items(item.get("blocking_refs", [])):
            console.print(f"    blocker: {blocker}", markup=False)
        for action in _dedupe_cli_text_items(item.get("capability_next_actions", [])):
            if recommended_next_steps:
                break
            console.print(f"    next action: {action}", markup=False)


def _format_frontend_delivery_truth_for_console(item: dict[str, object]) -> str:
    return summarize_frontend_delivery_truth_item(item)


def _render_truth_source_inventory(source_inventory: object) -> None:
    if hasattr(source_inventory, "model_dump"):
        source_inventory = source_inventory.model_dump(mode="json")
    if not isinstance(source_inventory, dict):
        return

    console.print(
        "  - source inventory: "
        f"{source_inventory.get('state', 'incomplete')}",
        markup=False,
    )
    console.print(
        "    totals: "
        f"{source_inventory.get('mapped_sources', 0)}/"
        f"{source_inventory.get('total_sources', 0)} mapped"
        f", unmapped sources: {source_inventory.get('unmapped_sources', 0)}"
        f", missing sources: {source_inventory.get('missing_sources', 0)}",
        markup=False,
    )
    console.print(
        "    signals: "
        f"phase={source_inventory.get('phase_signal_count', 0)}, "
        f"deferred={source_inventory.get('deferred_signal_count', 0)}, "
        f"non_goal={source_inventory.get('non_goal_signal_count', 0)}",
        markup=False,
    )
    layer_totals = source_inventory.get("layer_totals", {})
    layer_materialized = source_inventory.get("layer_materialized", {})
    if isinstance(layer_totals, dict) and layer_totals:
        layer_parts = []
        for layer, total in layer_totals.items():
            materialized = 0
            if isinstance(layer_materialized, dict):
                materialized = int(layer_materialized.get(layer, 0) or 0)
            layer_parts.append(f"{layer} {materialized}/{total}")
        console.print(
            "    layers: " + ", ".join(layer_parts),
            markup=False,
        )
    unmapped_paths = source_inventory.get("unmapped_paths", [])
    if isinstance(unmapped_paths, list):
        for path in _dedupe_cli_text_items(unmapped_paths)[:5]:
            console.print(f"    unmapped source: {path}", markup=False)


def _render_truth_validation_summary(
    errors: list[str],
    warnings: list[str],
) -> None:
    migration_prefix = "migration_pending:"
    non_migration_warnings = [
        warning
        for warning in _dedupe_cli_text_items(warnings)
        if not warning.startswith(migration_prefix)
    ]
    if non_migration_warnings:
        console.print(
            f"  - warnings: {len(non_migration_warnings)}",
            markup=False,
        )
        for warning in non_migration_warnings[:5]:
            console.print(f"    warning: {warning}", markup=False)
    deduped_errors = _dedupe_cli_text_items(errors)
    if deduped_errors:
        console.print(f"  - validation errors: {len(deduped_errors)}", markup=False)
        for error in deduped_errors[:5]:
            console.print(f"    validation: {error}", markup=False)


def _render_frontend_integrate_lines(steps: list[object]) -> None:
    console.print("\n[bold cyan]Frontend Hints[/bold cyan]")
    for step in steps:
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        readiness = getattr(step, "frontend_readiness", None)
        console.print(
            f"  - {spec_id}: {_format_frontend_readiness(readiness)}",
            markup=False,
        )


def _render_frontend_execute_preflight(steps: list[object]) -> None:
    console.print("\n[bold cyan]Frontend Execute Preflight[/bold cyan]")
    for step in steps:
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        readiness = getattr(step, "frontend_readiness", None)
        console.print(
            f"  - {spec_id}: {_format_frontend_readiness(readiness)}",
            markup=False,
        )


def _render_frontend_recheck_handoff(steps: list[object]) -> None:
    handoff_lines = _frontend_recheck_output_lines(steps)
    if not handoff_lines:
        return

    console.print("\n[bold cyan]Frontend Recheck Handoff[/bold cyan]")
    for line in handoff_lines:
        console.print(line, markup=False)


def _render_frontend_remediation_handoff(steps: list[object]) -> None:
    handoff_lines = _frontend_remediation_output_lines(steps)
    if not handoff_lines:
        return

    console.print("\n[bold cyan]Frontend Remediation Handoff[/bold cyan]")
    for line in handoff_lines:
        console.print(line, markup=False)


def _frontend_recheck_output_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        handoff = getattr(step, "frontend_recheck_handoff", None)
        if handoff is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"  - {spec_id}: {getattr(handoff, 'reason', '')}")
        for command in _dedupe_cli_text_items(
            getattr(handoff, "recommended_commands", ())
        )[:2]:
            lines.append(f"    command: {command}")
    return lines


def _format_frontend_remediation(
    remediation: ProgramFrontendRemediationInput | None,
) -> str:
    if remediation is None:
        return "-"

    details: list[str] = []
    fix_inputs = _dedupe_cli_text_items(remediation.fix_inputs)
    blockers = _dedupe_cli_text_items(remediation.blockers)
    if fix_inputs:
        details.append(", ".join(fix_inputs[:2]))
    elif blockers:
        details.append(blockers[0])

    suffix = f" [{'; '.join(details)}]" if details else ""
    return f"{remediation.state}{suffix}"


def _frontend_remediation_output_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        remediation = getattr(step, "frontend_remediation_input", None)
        if remediation is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"  - {spec_id}: {_format_frontend_remediation(remediation)}")
        for action in _dedupe_cli_text_items(getattr(remediation, "suggested_actions", ()))[:3]:
            lines.append(f"    action: {action}")
        for command in _dedupe_cli_text_items(
            getattr(remediation, "recommended_commands", ())
        )[:3]:
            lines.append(f"    command: {command}")
        for plain_text in _dedupe_cli_text_items(
            getattr(remediation, "plain_language_blockers", ())
        )[:2]:
            lines.append(f"    explain: {plain_text}")
        for next_step in _dedupe_cli_text_items(
            getattr(remediation, "recommended_next_steps", ())
        )[:2]:
            lines.append(f"    next step: {next_step}")
    return lines


def _frontend_recheck_report_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        handoff = getattr(step, "frontend_recheck_handoff", None)
        if handoff is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"- {spec_id}: {getattr(handoff, 'reason', '')}")
        for command in _dedupe_cli_text_items(
            getattr(handoff, "recommended_commands", ())
        ):
            lines.append(f"  - `{command}`")
    return lines


def _frontend_remediation_report_lines(steps: list[object]) -> list[str]:
    lines: list[str] = []
    for step in steps:
        remediation = getattr(step, "frontend_remediation_input", None)
        if remediation is None:
            continue
        spec_id = str(getattr(step, "spec_id", "")).strip() or "unknown-spec"
        lines.append(f"- {spec_id}: {_format_frontend_remediation(remediation)}")
        for action in _dedupe_cli_text_items(getattr(remediation, "suggested_actions", ())):
            lines.append(f"  - {action}")
        for command in _dedupe_cli_text_items(
            getattr(remediation, "recommended_commands", ())
        ):
            lines.append(f"  - `{command}`")
        for plain_text in _dedupe_cli_text_items(
            getattr(remediation, "plain_language_blockers", ())
        ):
            lines.append(f"  - explain: {plain_text}")
        for next_step in _dedupe_cli_text_items(
            getattr(remediation, "recommended_next_steps", ())
        ):
            lines.append(f"  - next step: {next_step}")
    return lines


def _render_frontend_remediation_execution_result(results: list[object]) -> None:
    if not results:
        return

    console.print("\n[bold cyan]Frontend Remediation Command Results[/bold cyan]")
    for item in results:
        command = str(getattr(item, "command", "")).strip()
        status = str(getattr(item, "status", "")).strip() or "unknown"
        console.print(f"  - {command} -> {status}", markup=False)
        for path in _dedupe_cli_text_items(getattr(item, "written_paths", ()))[:4]:
            console.print(f"    wrote: {path}", markup=False)
        summary = str(getattr(item, "summary", "")).strip()
        if summary:
            console.print(f"    summary: {summary}", markup=False)


def _coerce_frontend_solution_confirmation_mode(
    snapshot: FrontendSolutionSnapshot,
    *,
    mode: str,
) -> FrontendSolutionSnapshot:
    if snapshot.confirmed_by_mode == mode:
        return snapshot

    payload = snapshot.model_dump(mode="json")
    payload["confirmed_by_mode"] = mode
    payload["recommendation_source"] = f"{mode}-mode"
    return FrontendSolutionSnapshot(**payload)


def _frontend_solution_confirmation_change_fields(
    snapshot: FrontendSolutionSnapshot,
) -> list[str]:
    fields = [
        "project_shape",
        "frontend_stack",
        "provider_id",
        "backend_stack",
        "api_collab_mode",
        "style_pack_id",
    ]
    changed_fields: list[str] = []
    for field_name in fields:
        requested_value = getattr(snapshot, f"requested_{field_name}")
        effective_value = getattr(snapshot, f"effective_{field_name}")
        if requested_value != effective_value:
            changed_fields.append(field_name)
    return changed_fields


def _frontend_solution_confirmation_fallback_required(
    snapshot: FrontendSolutionSnapshot,
) -> bool:
    return snapshot.decision_status in {"fallback_required", "fallback_confirmed"}


def _render_frontend_solution_confirmation_recommendation(
    snapshot: FrontendSolutionSnapshot,
) -> None:
    console.print("\n[bold cyan]Recommended Solution[/bold cyan]")
    console.print(
        f"  - recommended_frontend_stack: {snapshot.recommended_frontend_stack}",
        markup=False,
    )
    console.print(
        f"  - recommended_provider_id: {snapshot.recommended_provider_id}",
        markup=False,
    )
    console.print(
        f"  - recommended_style_pack_id: {snapshot.recommended_style_pack_id}",
        markup=False,
    )
    console.print(
        f"  - recommendation_reason_text: {snapshot.recommendation_reason_text}",
        markup=False,
    )


def _render_frontend_solution_confirmation_wizard(
    snapshot: FrontendSolutionSnapshot,
) -> None:
    changed_fields = _dedupe_cli_text_items(
        _frontend_solution_confirmation_change_fields(snapshot)
    )
    step_lines = [
        "Step 1/7: Recommendation",
        "Step 2/7: Requested frontend stack",
        "Step 3/7: Requested provider",
        "Step 4/7: Requested style pack",
        "Step 5/7: Availability summary",
        "Step 6/7: Effective solution diff",
        "Step 7/7: Final confirmation",
    ]
    console.print("\n[bold cyan]Structured Wizard[/bold cyan]")
    for line in step_lines:
        console.print(f"  - {line}", markup=False)
    console.print(
        f"  - requested_frontend_stack: {snapshot.requested_frontend_stack}",
        markup=False,
    )
    console.print(
        f"  - requested_provider_id: {snapshot.requested_provider_id}",
        markup=False,
    )
    console.print(
        f"  - requested_style_pack_id: {snapshot.requested_style_pack_id}",
        markup=False,
    )
    console.print(
        "  - availability_summary: "
        + snapshot.availability_summary.overall_status,
        markup=False,
    )
    console.print(
        "  - effective_diff: "
        + (", ".join(changed_fields) if changed_fields else "none"),
        markup=False,
    )


def _render_frontend_solution_confirmation_final(
    snapshot: FrontendSolutionSnapshot,
) -> None:
    changed_fields = _dedupe_cli_text_items(
        _frontend_solution_confirmation_change_fields(snapshot)
    )
    console.print("\n[bold cyan]Final Preflight[/bold cyan]")
    console.print(
        f"  - requested_frontend_stack: {snapshot.requested_frontend_stack}",
        markup=False,
    )
    console.print(
        f"  - requested_provider_id: {snapshot.requested_provider_id}",
        markup=False,
    )
    console.print(
        f"  - requested_style_pack_id: {snapshot.requested_style_pack_id}",
        markup=False,
    )
    console.print(
        f"  - effective_frontend_stack: {snapshot.effective_frontend_stack}",
        markup=False,
    )
    console.print(
        f"  - effective_provider_id: {snapshot.effective_provider_id}",
        markup=False,
    )
    console.print(
        f"  - effective_style_pack_id: {snapshot.effective_style_pack_id}",
        markup=False,
    )
    console.print(
        f"  - preflight_status: {snapshot.preflight_status}",
        markup=False,
    )
    console.print(
        "  - will_change_on_confirm: "
        + (", ".join(changed_fields) if changed_fields else "none"),
        markup=False,
    )
    console.print(
        "  - fallback_required: "
        + str(_frontend_solution_confirmation_fallback_required(snapshot)).lower(),
        markup=False,
    )


def _frontend_solution_confirmation_report_lines(
    *,
    manifest: str,
    mode_title: str,
    snapshot: FrontendSolutionSnapshot,
    mode: str,
    latest_snapshot_path: Path | None,
    artifact_paths: list[Path],
) -> list[str]:
    changed_fields = _dedupe_cli_text_items(
        _frontend_solution_confirmation_change_fields(snapshot)
    )
    lines: list[str] = [
        f"# {mode_title}",
        "",
        f"- Manifest: `{manifest}`",
        f"- Mode: `{mode}`",
        "",
    ]
    if mode == "advanced":
        lines.extend(
            [
                "## Structured Wizard",
                "",
                "- Step 1/7: Recommendation",
                "- Step 2/7: Requested frontend stack",
                "- Step 3/7: Requested provider",
                "- Step 4/7: Requested style pack",
                "- Step 5/7: Availability summary",
                "- Step 6/7: Effective solution diff",
                "- Step 7/7: Final confirmation",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Recommended Solution",
                "",
                f"- recommended_frontend_stack: `{snapshot.recommended_frontend_stack}`",
                f"- recommended_provider_id: `{snapshot.recommended_provider_id}`",
                f"- recommended_style_pack_id: `{snapshot.recommended_style_pack_id}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Final Preflight",
            "",
            f"- requested_frontend_stack: `{snapshot.requested_frontend_stack}`",
            f"- requested_provider_id: `{snapshot.requested_provider_id}`",
            f"- requested_style_pack_id: `{snapshot.requested_style_pack_id}`",
            f"- effective_frontend_stack: `{snapshot.effective_frontend_stack}`",
            f"- effective_provider_id: `{snapshot.effective_provider_id}`",
            f"- effective_style_pack_id: `{snapshot.effective_style_pack_id}`",
            f"- preflight_status: `{snapshot.preflight_status}`",
            "- will_change_on_confirm: `"
            + (", ".join(changed_fields) if changed_fields else "none")
            + "`",
            "- fallback_required: `"
            + str(_frontend_solution_confirmation_fallback_required(snapshot)).lower()
            + "`",
            "",
        ]
    )
    if latest_snapshot_path is not None:
        lines.extend(
            [
                "## Frontend Solution Confirmation Artifact",
                "",
                f"- `{latest_snapshot_path}`",
                "",
            ]
        )
    if artifact_paths:
        lines.extend(
            [
                "## Materialized Files",
                "",
            ]
        )
        lines.extend([f"- `{path}`" for path in _dedupe_cli_text_items(artifact_paths)])
        lines.append("")
    return lines


def _render_frontend_provider_runtime_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Provider Runtime Result[/bold cyan]")
    console.print(
        f"  - invocation result: {getattr(result, 'invocation_result', 'unknown')}",
        markup=False,
    )
    console.print(
        "  - provider state: "
        + str(getattr(result, "provider_execution_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(getattr(result, "patch_summaries", ())):
        console.print(f"  - patch summary: {summary}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_provider_patch_apply_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Provider Patch Apply Result[/bold cyan]")
    console.print(
        f"  - apply result: {getattr(result, 'apply_result', 'unknown')}",
        markup=False,
    )
    console.print(
        "  - patch apply state: "
        + str(getattr(result, "patch_apply_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(getattr(result, "apply_summaries", ())):
        console.print(f"  - apply summary: {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_cross_spec_writeback_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Cross-Spec Writeback Result[/bold cyan]")
    console.print(
        "  - orchestration result: "
        + str(getattr(result, "orchestration_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - writeback state: "
        + str(getattr(result, "writeback_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(
        getattr(result, "orchestration_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_guarded_registry_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Guarded Registry Result[/bold cyan]")
    console.print(
        "  - registry result: "
        + str(getattr(result, "registry_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - registry state: "
        + str(getattr(result, "registry_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(getattr(result, "registry_summaries", ())):
        console.print(f"  - {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_broader_governance_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Broader Governance Result[/bold cyan]")
    console.print(
        "  - governance result: "
        + str(getattr(result, "governance_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - governance state: "
        + str(getattr(result, "governance_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(
        getattr(result, "governance_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_final_governance_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Final Governance Result[/bold cyan]")
    console.print(
        "  - final governance result: "
        + str(getattr(result, "final_governance_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - final governance state: "
        + str(getattr(result, "final_governance_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(
        getattr(result, "final_governance_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_writeback_persistence_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Writeback Persistence Result[/bold cyan]")
    console.print(
        "  - persistence result: "
        + str(getattr(result, "persistence_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - persistence state: "
        + str(getattr(result, "persistence_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(
        getattr(result, "persistence_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_persisted_write_proof_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Persisted Write Proof Result[/bold cyan]")
    console.print(
        "  - proof result: " + str(getattr(result, "proof_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - proof state: " + str(getattr(result, "proof_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(getattr(result, "proof_summaries", ())):
        console.print(f"  - {summary}", markup=False)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False)


def _render_frontend_final_proof_publication_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Final Proof Publication Result[/bold cyan]")
    console.print(
        "  - publication result: "
        + str(getattr(result, "publication_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - publication state: "
        + str(getattr(result, "publication_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(
        getattr(result, "publication_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False, soft_wrap=True)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False, soft_wrap=True)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False, soft_wrap=True)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False, soft_wrap=True)


def _render_frontend_final_proof_closure_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Final Proof Closure Result[/bold cyan]")
    console.print(
        "  - closure result: " + str(getattr(result, "closure_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - closure state: " + str(getattr(result, "closure_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(getattr(result, "closure_summaries", ())):
        console.print(f"  - {summary}", markup=False, soft_wrap=True)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False, soft_wrap=True)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False, soft_wrap=True)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False, soft_wrap=True)


def _render_frontend_final_proof_archive_result(result: object) -> None:
    console.print("\n[bold cyan]Frontend Final Proof Archive Result[/bold cyan]")
    console.print(
        "  - archive result: " + str(getattr(result, "archive_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - archive state: " + str(getattr(result, "archive_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(getattr(result, "archive_summaries", ())):
        console.print(f"  - {summary}", markup=False, soft_wrap=True)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False, soft_wrap=True)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False, soft_wrap=True)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False, soft_wrap=True)


def _render_frontend_final_proof_archive_thread_archive_result(result: object) -> None:
    console.print(
        "\n[bold cyan]Frontend Final Proof Archive Thread Archive Result[/bold cyan]"
    )
    console.print(
        "  - thread archive result: "
        + str(getattr(result, "thread_archive_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - thread archive state: "
        + str(getattr(result, "thread_archive_state", "unknown")),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for summary in _dedupe_cli_text_items(
        getattr(result, "thread_archive_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False, soft_wrap=True)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False, soft_wrap=True)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False, soft_wrap=True)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False, soft_wrap=True)


def _render_frontend_final_proof_archive_project_cleanup_result(
    result: object,
) -> None:
    console.print(
        "\n[bold cyan]Frontend Final Proof Archive Project Cleanup Result[/bold cyan]"
    )
    console.print(
        "  - project cleanup result: "
        + str(getattr(result, "project_cleanup_result", "unknown")),
        markup=False,
    )
    console.print(
        "  - project cleanup state: "
        + str(getattr(result, "project_cleanup_state", "unknown")),
        markup=False,
    )
    console.print(
        "  - cleanup targets state: "
        + str(getattr(result, "cleanup_targets_state", "unknown")),
        markup=False,
    )
    console.print(
        "  - cleanup targets count: "
        + str(len(getattr(result, "cleanup_targets", ()))),
        markup=False,
    )
    console.print(
        "  - cleanup target eligibility state: "
        + str(getattr(result, "cleanup_target_eligibility_state", "unknown")),
        markup=False,
    )
    console.print(
        "  - cleanup target eligibility count: "
        + str(len(getattr(result, "cleanup_target_eligibility", ()))),
        markup=False,
    )
    console.print(
        "  - cleanup preview plan state: "
        + str(getattr(result, "cleanup_preview_plan_state", "unknown")),
        markup=False,
    )
    console.print(
        "  - cleanup preview plan count: "
        + str(len(getattr(result, "cleanup_preview_plan", ()))),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal state: "
        + str(getattr(result, "cleanup_mutation_proposal_state", "unknown")),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal count: "
        + str(len(getattr(result, "cleanup_mutation_proposal", ()))),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal approval state: "
        + str(
            getattr(
                result,
                "cleanup_mutation_proposal_approval_state",
                "unknown",
            )
        ),
        markup=False,
    )
    console.print(
        "  - cleanup mutation proposal approval count: "
        + str(len(getattr(result, "cleanup_mutation_proposal_approval", ()))),
        markup=False,
    )
    console.print(
        "  - cleanup mutation execution gating state: "
        + str(
            getattr(
                result,
                "cleanup_mutation_execution_gating_state",
                "unknown",
            )
        ),
        markup=False,
    )
    console.print(
        "  - cleanup mutation execution gating count: "
        + str(len(getattr(result, "cleanup_mutation_execution_gating", ()))),
        markup=False,
    )
    console.print(
        f"  - confirmed: {str(getattr(result, 'confirmed', False)).lower()}",
        markup=False,
    )
    for line in _project_cleanup_truth_output_lines(result):
        console.print(line, markup=False, soft_wrap=True)
    for summary in _dedupe_cli_text_items(
        getattr(result, "project_cleanup_summaries", ())
    ):
        console.print(f"  - {summary}", markup=False, soft_wrap=True)
    for path in _dedupe_cli_text_items(getattr(result, "written_paths", ())):
        console.print(f"  - wrote: {path}", markup=False, soft_wrap=True)
    for blocker in _dedupe_cli_text_items(getattr(result, "remaining_blockers", ())):
        console.print(f"  - blocker: {blocker}", markup=False, soft_wrap=True)
    for warning in _dedupe_cli_text_items(getattr(result, "warnings", ())):
        console.print(f"  - warning: {warning}", markup=False, soft_wrap=True)


def _coerce_truth_item_mapping(item: object) -> dict[str, object] | None:
    if hasattr(item, "model_dump"):
        item = item.model_dump(mode="json")
    if isinstance(item, dict):
        return item
    return None


def _project_cleanup_truth_output_lines(result: object) -> list[str]:
    lines: list[str] = []
    lines.extend(
        _project_cleanup_truth_block_lines(
            "cleanup target",
            getattr(result, "cleanup_targets", ()),
            state=str(getattr(result, "cleanup_targets_state", "unknown")),
            action_field="cleanup_action",
            path_field="path",
            kind_field="kind",
        )
    )
    lines.extend(
        _project_cleanup_truth_block_lines(
            "eligibility",
            getattr(result, "cleanup_target_eligibility", ()),
            state=str(
                getattr(result, "cleanup_target_eligibility_state", "unknown")
            ),
            action_field="eligibility",
        )
    )
    lines.extend(
        _project_cleanup_truth_block_lines(
            "preview",
            getattr(result, "cleanup_preview_plan", ()),
            state=str(getattr(result, "cleanup_preview_plan_state", "unknown")),
            action_field="planned_action",
        )
    )
    lines.extend(
        _project_cleanup_truth_block_lines(
            "proposal",
            getattr(result, "cleanup_mutation_proposal", ()),
            state=str(
                getattr(result, "cleanup_mutation_proposal_state", "unknown")
            ),
            action_field="proposed_action",
        )
    )
    lines.extend(
        _project_cleanup_truth_block_lines(
            "approval",
            getattr(result, "cleanup_mutation_proposal_approval", ()),
            state=str(
                getattr(
                    result,
                    "cleanup_mutation_proposal_approval_state",
                    "unknown",
                )
            ),
            action_field="approved_action",
        )
    )
    lines.extend(
        _project_cleanup_truth_block_lines(
            "gating",
            getattr(result, "cleanup_mutation_execution_gating", ()),
            state=str(
                getattr(
                    result,
                    "cleanup_mutation_execution_gating_state",
                    "unknown",
                )
            ),
            action_field="gated_action",
        )
    )
    return lines


def _project_cleanup_truth_report_lines(result: object) -> list[str]:
    lines: list[str] = []
    lines.extend(
        _project_cleanup_truth_report_block_lines(
            "Cleanup targets",
            getattr(result, "cleanup_targets", ()),
            state=str(getattr(result, "cleanup_targets_state", "unknown")),
            action_field="cleanup_action",
            path_field="path",
            kind_field="kind",
        )
    )
    lines.extend(
        _project_cleanup_truth_report_block_lines(
            "Cleanup target eligibility",
            getattr(result, "cleanup_target_eligibility", ()),
            state=str(
                getattr(result, "cleanup_target_eligibility_state", "unknown")
            ),
            action_field="eligibility",
        )
    )
    lines.extend(
        _project_cleanup_truth_report_block_lines(
            "Cleanup preview plan",
            getattr(result, "cleanup_preview_plan", ()),
            state=str(getattr(result, "cleanup_preview_plan_state", "unknown")),
            action_field="planned_action",
        )
    )
    lines.extend(
        _project_cleanup_truth_report_block_lines(
            "Cleanup mutation proposal",
            getattr(result, "cleanup_mutation_proposal", ()),
            state=str(
                getattr(result, "cleanup_mutation_proposal_state", "unknown")
            ),
            action_field="proposed_action",
        )
    )
    lines.extend(
        _project_cleanup_truth_report_block_lines(
            "Cleanup mutation proposal approval",
            getattr(result, "cleanup_mutation_proposal_approval", ()),
            state=str(
                getattr(
                    result,
                    "cleanup_mutation_proposal_approval_state",
                    "unknown",
                )
            ),
            action_field="approved_action",
        )
    )
    lines.extend(
        _project_cleanup_truth_report_block_lines(
            "Cleanup mutation execution gating",
            getattr(result, "cleanup_mutation_execution_gating", ()),
            state=str(
                getattr(
                    result,
                    "cleanup_mutation_execution_gating_state",
                    "unknown",
                )
            ),
            action_field="gated_action",
        )
    )
    return lines


def _project_cleanup_truth_block_lines(
    label: str,
    items: object,
    *,
    state: str,
    action_field: str,
    path_field: str | None = None,
    kind_field: str | None = None,
) -> list[str]:
    if state in {"missing", "empty"}:
        return []
    lines: list[str] = []
    seen_chunks: set[tuple[str, ...]] = set()
    emitted = 0
    for item in list(items):
        payload = _coerce_truth_item_mapping(item)
        if payload is None:
            continue
        target_id = str(payload.get("target_id", "")).strip() or "unknown-target"
        action = str(payload.get(action_field, "")).strip()
        chunk: list[str] = []
        if path_field is not None or kind_field is not None:
            path = str(payload.get(path_field or "", "")).strip()
            kind = str(payload.get(kind_field or "", "")).strip()
            chunk.append(
                f"  - {label}: {target_id}"
                f" | {kind or '-'}"
                f" | {path or '-'}"
                f" | {action or '-'}"
            )
        else:
            chunk.append(f"  - {label}: {target_id} -> {action or '-'}")
        reason = str(payload.get("reason", "")).strip()
        if reason:
            chunk.append(f"    reason: {reason}")
        chunk_key = tuple(chunk)
        if chunk_key in seen_chunks:
            continue
        seen_chunks.add(chunk_key)
        lines.extend(chunk)
        emitted += 1
        if emitted >= 3:
            break
    return lines


def _project_cleanup_truth_report_block_lines(
    title: str,
    items: object,
    *,
    state: str,
    action_field: str,
    path_field: str | None = None,
    kind_field: str | None = None,
) -> list[str]:
    if state in {"missing", "empty"}:
        return []
    lines = [f"- {title}:"]
    emitted = 0
    seen_chunks: set[tuple[str, ...]] = set()
    for item in list(items):
        payload = _coerce_truth_item_mapping(item)
        if payload is None:
            continue
        target_id = str(payload.get("target_id", "")).strip() or "unknown-target"
        action = str(payload.get(action_field, "")).strip()
        chunk: list[str] = []
        if path_field is not None or kind_field is not None:
            path = str(payload.get(path_field or "", "")).strip()
            kind = str(payload.get(kind_field or "", "")).strip()
            chunk.append(
                f"  - `{target_id}` | `{kind or '-'}` | `{path or '-'}` | `{action or '-'}`"
            )
        else:
            chunk.append(f"  - `{target_id}` -> `{action or '-'}`")
        reason = str(payload.get("reason", "")).strip()
        if reason:
            chunk.append(f"    - reason: {reason}")
        chunk_key = tuple(chunk)
        if chunk_key in seen_chunks:
            continue
        seen_chunks.add(chunk_key)
        emitted += 1
        lines.extend(chunk)
        if emitted >= 3:
            break
    return lines if emitted else []
