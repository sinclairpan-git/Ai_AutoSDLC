"""Enterprise profile configuration commands."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
import yaml
from rich.console import Console

from ai_sdlc.core.agentops_bridge import (
    DEFAULT_TOKEN_ENV,
    ENTERPRISE_PROFILE_ENV,
    INGESTION_MODE_DIRECT_LOCAL,
    INGESTION_MODE_GATEWAY,
    REPORTING_MODE_REQUIRED,
    REPORTING_MODES,
    enterprise_profile_paths,
)

enterprise_app = typer.Typer(
    help="Configure lightweight enterprise-managed AI-SDLC settings.",
    no_args_is_help=True,
)
console = Console()


@enterprise_app.command("configure")
def enterprise_configure(
    endpoint: str = typer.Option(
        "",
        "--endpoint",
        help="AgentOps Gateway base URL for enterprise reporting.",
    ),
    enterprise_id: str = typer.Option(
        "",
        "--enterprise-id",
        help="Enterprise or department identifier for this managed profile.",
    ),
    reporting_mode: str = typer.Option(
        REPORTING_MODE_REQUIRED,
        "--reporting-mode",
        help="AgentOps reporting mode: off, opportunistic, or required.",
    ),
    token_env: str = typer.Option(
        DEFAULT_TOKEN_ENV,
        "--token-env",
        help="Environment variable that contains the AgentOps token.",
    ),
    ingestion_mode: str = typer.Option(
        INGESTION_MODE_GATEWAY,
        "--ingestion-mode",
        help="AgentOps ingestion mode. Use gateway for enterprise setups.",
    ),
    profile_path: Path | None = typer.Option(
        None,
        "--profile-path",
        help="Profile path. Defaults to user-level enterprise.yaml.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON output."),
) -> None:
    """Write a user-level enterprise profile without storing token values."""
    normalized_reporting_mode = reporting_mode.strip().lower()
    if normalized_reporting_mode not in REPORTING_MODES:
        raise typer.BadParameter("reporting-mode must be off, opportunistic, or required")
    normalized_ingestion_mode = ingestion_mode.strip().lower() or INGESTION_MODE_GATEWAY
    if normalized_ingestion_mode not in {INGESTION_MODE_GATEWAY, INGESTION_MODE_DIRECT_LOCAL}:
        raise typer.BadParameter("ingestion-mode must be gateway or direct_local")
    endpoint = endpoint.strip()
    if normalized_reporting_mode != "off" and not endpoint:
        raise typer.BadParameter("endpoint is required unless reporting-mode is off")
    resolved_path = profile_path or _default_write_profile_path()
    payload = {
        "schema_version": "ai_sdlc_enterprise_profile.v1",
        "managed": True,
        "enterprise_id": enterprise_id.strip(),
        "agentops_reporting_mode": normalized_reporting_mode,
        "agentops_ingestion_endpoint": endpoint,
        "agentops_ingestion_mode": normalized_ingestion_mode,
        "agentops_token_env": token_env.strip() or DEFAULT_TOKEN_ENV,
    }
    resolved_path = resolved_path.expanduser()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    result = {
        "ok": True,
        "profile_path": str(resolved_path),
        "reporting_mode": normalized_reporting_mode,
        "token_env": payload["agentops_token_env"],
        "token_written": False,
    }
    if json_output:
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return
    console.print("[green]Enterprise profile written.[/green]")
    console.print(f"Profile: {resolved_path}")
    console.print(f"AgentOps reporting mode: {normalized_reporting_mode}")
    console.print(
        f"Token source: environment variable {payload['agentops_token_env']} "
        "(token value was not written)"
    )


def _default_write_profile_path() -> Path:
    explicit = os.environ.get(ENTERPRISE_PROFILE_ENV, "").strip()
    if explicit:
        return Path(explicit)
    paths = enterprise_profile_paths(env=os.environ)
    if os.name == "nt":
        return paths[-1] if paths else Path.home() / "AI-SDLC" / "enterprise.yaml"
    return Path.home() / ".config" / "ai-sdlc" / "enterprise.yaml"
