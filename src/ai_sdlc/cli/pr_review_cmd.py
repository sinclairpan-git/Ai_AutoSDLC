"""CLI commands for local adversarial PR review."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.branch.git_client import GitClient, GitError
from ai_sdlc.core.pr_review_provider import MockReviewerFixture, ProviderRunStatus
from ai_sdlc.core.pr_review_service import (
    PRReviewCommandStatus,
    PRReviewStartOptions,
    attest_pr_review,
    close_pr_review,
    doctor_pr_review,
    fix_pr_review,
    parse_provider_command,
    rerun_pr_review,
    start_pr_review,
    status_pr_review,
)
from ai_sdlc.utils.helpers import find_project_root

pr_review_app = typer.Typer(
    help="Run local adversarial PR review loops.",
    no_args_is_help=True,
)
console = Console()


@pr_review_app.command(name="doctor")
def pr_review_doctor(
    base_ref: str | None = typer.Option(
        None,
        "--base",
        help="Base branch or revision. Defaults to the repository default branch.",
    ),
    head_ref: str = typer.Option("HEAD", "--head", help="Head branch or revision."),
    diff_source: str = typer.Option(
        "local-git-range",
        "--diff-source",
        help="Review input source: local-git-range, patch, local-staged, local-unstaged, or scm-pr.",
    ),
    patch_file: str = typer.Option("", "--patch-file", help="Patch file for patch diff source."),
    source_id: str = typer.Option("", "--source-id", help="External source id such as PR/MR id."),
    source_provider: str = typer.Option(
        "",
        "--source-provider",
        help="External source provider such as github, gitlab, gitee, or custom.",
    ),
    provider_id: str = typer.Option(
        "",
        "--provider",
        help="Review provider: local-agent or mock-reviewer. Defaults to loop policy.",
    ),
    model_selector: str = typer.Option(
        "current",
        "--model",
        help="Model selector. Defaults to current.",
    ),
    current_model: str = typer.Option(
        "",
        "--current-model",
        help="Explicit current model for local CLI/agent environments.",
    ),
    provider_command: str = typer.Option(
        "",
        "--provider-command",
        help="Local reviewer command for local-agent.",
    ),
    code_egress: bool = typer.Option(
        False,
        "--code-egress/--no-code-egress",
        help="Whether the selected provider may send code to a remote model service.",
    ),
    confirm_code_egress: bool = typer.Option(
        False,
        "--confirm-code-egress",
        help="Confirm policy-gated remote code egress.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Check local PR review readiness without writing review artifacts."""

    root = _project_root_or_exit(json_output=json_output)
    resolved_base = _resolve_base_ref(
        root,
        base_ref,
        diff_source=diff_source,
        json_output=json_output,
    )
    result = doctor_pr_review(
        root=root,
        base_ref=resolved_base,
        head_ref=head_ref,
        diff_source=diff_source,
        patch_file=patch_file,
        source_id=source_id,
        source_provider=source_provider,
        provider_id=provider_id,
        model_selector=model_selector,
        current_model=current_model,
        provider_command=parse_provider_command(provider_command),
        code_egress=code_egress,
        code_egress_confirmed=confirm_code_egress,
    )
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    raise typer.Exit(0 if result.status == PRReviewCommandStatus.READY else 1)


@pr_review_app.command(name="start")
def pr_review_start(
    base_ref: str | None = typer.Option(
        None,
        "--base",
        help="Base branch or revision. Defaults to the repository default branch.",
    ),
    head_ref: str = typer.Option("HEAD", "--head", help="Head branch or revision."),
    diff_source: str = typer.Option(
        "local-git-range",
        "--diff-source",
        help="Review input source: local-git-range, patch, local-staged, local-unstaged, or scm-pr.",
    ),
    patch_file: str = typer.Option("", "--patch-file", help="Patch file for patch diff source."),
    source_id: str = typer.Option("", "--source-id", help="External source id such as PR/MR id."),
    source_provider: str = typer.Option(
        "",
        "--source-provider",
        help="External source provider such as github, gitlab, gitee, or custom.",
    ),
    provider_id: str = typer.Option(
        "",
        "--provider",
        help="Review provider: local-agent or mock-reviewer. Defaults to loop policy.",
    ),
    model_selector: str = typer.Option(
        "current",
        "--model",
        help="Model selector. Defaults to current.",
    ),
    current_model: str = typer.Option(
        "",
        "--current-model",
        help="Explicit current model for local CLI/agent environments.",
    ),
    provider_command: str = typer.Option(
        "",
        "--provider-command",
        help="Local reviewer command for local-agent.",
    ),
    mock_fixture: MockReviewerFixture = typer.Option(
        MockReviewerFixture.CLEAN,
        "--mock-fixture",
        help="Mock reviewer fixture.",
    ),
    code_egress: bool = typer.Option(
        False,
        "--code-egress/--no-code-egress",
        help="Whether the selected provider may send code to a remote model service.",
    ),
    confirm_code_egress: bool = typer.Option(
        False,
        "--confirm-code-egress",
        help="Confirm policy-gated remote code egress.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview without writing review artifacts or invoking a provider.",
    ),
    review_id: str = typer.Option("", "--review-id", help="Explicit review id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Start or preview a local adversarial PR review."""

    root = _project_root_or_exit(json_output=json_output)
    resolved_base = _resolve_base_ref(
        root,
        base_ref,
        diff_source=diff_source,
        json_output=json_output,
    )
    result = start_pr_review(
        PRReviewStartOptions(
            root=root,
            base_ref=resolved_base,
            head_ref=head_ref,
            diff_source=diff_source,
            patch_file=patch_file,
            source_id=source_id,
            source_provider=source_provider,
            provider_id=provider_id,
            model_selector=model_selector,
            current_model=current_model,
            provider_command=parse_provider_command(provider_command),
            code_egress=code_egress,
            code_egress_confirmed=confirm_code_egress,
            dry_run=dry_run,
            review_id=review_id,
            mock_fixture=mock_fixture,
        )
    )
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    if result.provider_status == ProviderRunStatus.CHANGES_REQUIRED:
        raise typer.Exit(10)
    raise typer.Exit(
        0
        if result.status in {PRReviewCommandStatus.DRY_RUN, PRReviewCommandStatus.STARTED}
        else 1
    )


@pr_review_app.command(name="status")
def pr_review_status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Show the current local PR review state."""

    root = _project_root_or_exit(json_output=json_output)
    result = status_pr_review(root)
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    raise typer.Exit(0 if result.status != PRReviewCommandStatus.BLOCKED else 1)


@pr_review_app.command(name="fix")
def pr_review_fix(
    max_rounds: int = typer.Option(2, "--max-rounds", help="Maximum fix rounds."),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview fix plan metadata without writing fix artifacts.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Create a fix plan for unresolved BLOCKER/REQUIRED findings."""

    root = _project_root_or_exit(json_output=json_output)
    result = fix_pr_review(root, max_rounds=max_rounds, dry_run=dry_run)
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    raise typer.Exit(0 if result.status == PRReviewCommandStatus.READY else 1)


@pr_review_app.command(name="rerun")
def pr_review_rerun(
    provider_command: str = typer.Option(
        "",
        "--provider-command",
        help="Local reviewer command for local-agent.",
    ),
    mock_fixture: MockReviewerFixture = typer.Option(
        MockReviewerFixture.CLEAN,
        "--mock-fixture",
        help="Mock reviewer fixture.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Regenerate review pack and rerun the local review provider."""

    root = _project_root_or_exit(json_output=json_output)
    result = rerun_pr_review(
        root,
        provider_command=parse_provider_command(provider_command),
        mock_fixture=mock_fixture,
    )
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    if result.provider_status == ProviderRunStatus.CHANGES_REQUIRED:
        raise typer.Exit(10)
    raise typer.Exit(
        0 if result.status == PRReviewCommandStatus.STARTED else 1
    )


@pr_review_app.command(name="close")
def pr_review_close(
    require_no_blockers: bool = typer.Option(
        False,
        "--require-no-blockers",
        help="Allow risk_accepted when REQUIRED findings remain but no BLOCKERs.",
    ),
    evidence: list[str] = typer.Option(
        [],
        "--evidence",
        help="Verification evidence line to include in final report.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Close the local PR review with a final verdict."""

    root = _project_root_or_exit(json_output=json_output)
    result = close_pr_review(
        root,
        require_no_blockers=require_no_blockers,
        verification_evidence=evidence,
    )
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    raise typer.Exit(0 if result.status == PRReviewCommandStatus.CLOSED else 1)


@pr_review_app.command(name="attest")
def pr_review_attest(
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Write a CI-readable attestation for the current closed local review."""

    root = _project_root_or_exit(json_output=json_output)
    result = attest_pr_review(root)
    _emit_result(result.model_dump(mode="json"), json_output=json_output)
    raise typer.Exit(0 if result.status == PRReviewCommandStatus.READY else 1)


def _project_root_or_exit(*, json_output: bool = False) -> Path:
    root = find_project_root()
    if root is None:
        _emit_result(
            {
                "status": PRReviewCommandStatus.BLOCKED,
                "blocker": "Project is not initialized; .ai-sdlc is missing.",
                "next_action": "run ai-sdlc init .",
            },
            json_output=json_output,
        )
        raise typer.Exit(1)
    return root


def _resolve_base_ref(
    root: Path,
    base_ref: str | None,
    *,
    diff_source: str = "local-git-range",
    json_output: bool = False,
) -> str:
    if base_ref and base_ref.strip():
        return base_ref.strip()
    if diff_source.strip() != "local-git-range":
        return ""
    try:
        return GitClient(root).default_branch_name()
    except GitError as exc:
        _emit_result(
            {
                "status": PRReviewCommandStatus.BLOCKED,
                "blocker": str(exc),
                "next_action": "pass --base <branch> explicitly.",
            },
            json_output=json_output,
        )
        raise typer.Exit(1) from exc


def _emit_result(payload: dict[str, object], *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    console.print(f"Result: {payload.get('status', '')}")
    if payload.get("blocker"):
        console.print(f"Blocker: {payload['blocker']}")
    console.print(f"Next: {payload.get('next_action') or '-'}")
    for key in (
        "source_adapter",
        "source_access_status",
        "provider_id",
        "model_selector",
        "resolved_model",
        "code_egress",
    ):
        if key in payload:
            console.print(f"{key}: {payload.get(key)}")
    if isinstance(payload.get("diff_source"), dict):
        source = payload["diff_source"]
        if isinstance(source, dict) and source.get("source_kind"):
            console.print(f"diff_source: {source.get('source_kind')}")
    if payload.get("review_pack_path"):
        console.print(f"review_pack: {payload['review_pack_path']}")
    if payload.get("source_resolution_path"):
        console.print(f"source_resolution: {payload['source_resolution_path']}")
    if payload.get("findings_path"):
        console.print(f"findings: {payload['findings_path']}")


__all__ = ["pr_review_app"]
