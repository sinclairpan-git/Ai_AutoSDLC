"""Self-update advisor commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.core.update_advisor import (
    NOTICE_ACTIONABLE,
    NOTICE_FAILED,
    NOTICE_LIGHT,
    ack_notice,
    detect_runtime_identity,
    evaluate_update_advisor,
    notice_already_acknowledged,
    notice_version_for,
    platform_asset_hint,
    render_notice_lines,
    should_auto_render_notice,
)

self_update_app = typer.Typer(
    help="Check AI-SDLC framework update availability without silently upgrading.",
    no_args_is_help=True,
)
console = Console()
notice_console = Console(stderr=True)


def _print_json(payload: dict[str, object]) -> None:
    console.print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def maybe_render_update_notice() -> None:
    """Render the Stage 0 update notice for interactive installed CLI runs."""
    if not should_auto_render_notice():
        return
    evaluation = evaluate_update_advisor()
    classes = list(evaluation.eligible_notice_classes)
    if not classes and evaluation.refresh_result not in {
        "network_error",
        "parse_error",
        "timeout",
    }:
        return

    notice_class = None
    if NOTICE_ACTIONABLE in classes:
        notice_class = NOTICE_ACTIONABLE
    elif NOTICE_LIGHT in classes:
        notice_class = NOTICE_LIGHT
    elif evaluation.refresh_attempted:
        notice_class = NOTICE_FAILED

    if notice_class is None or notice_already_acknowledged(evaluation, notice_class):
        return

    lines = render_notice_lines(evaluation)
    if not lines:
        return
    notice_console.print(
        Panel(
            "\n".join(lines),
            title="AI-SDLC Update Advisor",
            border_style="yellow",
        )
    )
    ack_notice(
        notice_class,
        notice_version_for(evaluation, notice_class),
    )


@self_update_app.command("identity")
def self_update_identity(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    )
) -> None:
    """Show the installed-runtime identity used by update advisor."""
    identity = detect_runtime_identity()
    payload = identity.to_machine_dict()
    if json_output:
        _print_json(payload)
        return
    console.print(Panel(json.dumps(payload, ensure_ascii=False, indent=2), title="Update Identity"))


@self_update_app.command("evaluate")
def self_update_evaluate(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    ),
    no_refresh: bool = typer.Option(
        False,
        "--no-refresh",
        help="Evaluate cache-only without a network refresh attempt.",
    ),
) -> None:
    """Evaluate update notice eligibility."""
    evaluation = evaluate_update_advisor(allow_refresh=not no_refresh)
    payload = evaluation.to_machine_dict()
    if json_output:
        _print_json(payload)
        return
    lines = render_notice_lines(evaluation)
    if lines:
        console.print(Panel("\n".join(lines), title="AI-SDLC Update Advisor"))
        return
    console.print("[green]No actionable AI-SDLC update notice is available.[/green]")
    console.print(f"reason_code: {evaluation.reason_code}", markup=False)


@self_update_app.command("check")
def self_update_check(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    )
) -> None:
    """User-facing update check for the current installed runtime."""
    self_update_evaluate(json_output=json_output, no_refresh=False)


@self_update_app.command("ack-notice")
def self_update_ack_notice(
    notice_class: str = typer.Argument(..., help="Notice class to acknowledge."),
    notice_version: str = typer.Argument(..., help="Notice version or reason code."),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    ),
) -> None:
    """Record that a notice was shown by a CLI/IDE/AI surface."""
    ack = ack_notice(notice_class, notice_version)
    payload = ack.to_machine_dict()
    if json_output:
        _print_json(payload)
        return
    if ack.ack_recorded:
        console.print("[green]Update notice acknowledgement recorded.[/green]")
    else:
        console.print("[yellow]Update notice acknowledgement was not recorded.[/yellow]")


@self_update_app.command("instructions")
def self_update_instructions(
    version: str = typer.Option(
        "",
        "--version",
        help="Release version to install, for example 0.7.2.",
    ),
) -> None:
    """Print platform-specific manual update instructions."""
    hint = platform_asset_hint(version)
    release_version = version or "<version>"
    release_url = (
        f"https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/v{release_version}"
        if version and not version.startswith("v")
        else f"https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/{release_version}"
    )
    asset_url = release_url.replace("/tag/", "/download/") + f"/{hint['filename']}"
    lines = [
        "AI-SDLC 不会静默改写你的安装环境；请显式执行更新。",
        "AI-SDLC does not silently modify your install; update explicitly.",
        f"平台资产 / Platform asset: {hint['filename']}",
        f"Release: {release_url}",
    ]
    if hint["archive"] == "zip":
        lines.extend(
            [
                "PowerShell 下载 / Download:",
                f"Invoke-WebRequest -Uri {asset_url} -OutFile {hint['filename']}",
                "解压后进入目录并运行 / Extract, enter the folder, then run:",
                ".\\install_offline.ps1",
            ]
        )
    else:
        lines.extend(
            [
                "下载 / Download:",
                f"curl -L -o {hint['filename']} {asset_url}",
                "解压并安装 / Extract and install:",
                f"tar xzf {hint['filename']}",
                "cd ai-sdlc-offline-* && ./install_offline.sh",
            ]
        )
    console.print(Panel("\n".join(lines), title="AI-SDLC Explicit Update"))
