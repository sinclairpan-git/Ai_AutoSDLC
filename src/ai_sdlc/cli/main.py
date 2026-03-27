"""AI-SDLC CLI entry point."""

import typer
from rich.console import Console

from ai_sdlc.cli.cli_hooks import run_ide_adapter_if_initialized
from ai_sdlc.cli.commands import (
    index_command,
    init_command,
    recover_command,
    refresh_command,
    scan_command,
    status_command,
)
from ai_sdlc.cli.doctor_cmd import doctor_command
from ai_sdlc.cli.telemetry_cmd import telemetry_app
from ai_sdlc.cli.program_cmd import program_app
from ai_sdlc.cli.run_cmd import run_command
from ai_sdlc.cli.stage_cmd import stage_app
from ai_sdlc.cli.sub_apps import gate_app, rules_app, studio_app
from ai_sdlc.cli.verify_cmd import verify_app
from ai_sdlc.cli.workitem_cmd import workitem_app

app = typer.Typer(
    name="ai-sdlc",
    help="AI-native SDLC automation framework.",
    no_args_is_help=True,
)

_hook_console = Console()


@app.callback()
def _global_before_command(ctx: typer.Context) -> None:
    """First non-init command in an initialized project applies IDE adapter."""
    if ctx.invoked_subcommand is None:
        return
    # Read-only surfaces must not trigger adapter writes.
    if ctx.invoked_subcommand in ("init", "doctor", "status", "verify"):
        return
    run_ide_adapter_if_initialized(console=_hook_console)


app.command(name="init")(init_command)
app.command(name="doctor")(doctor_command)
app.command(name="status")(status_command)
app.command(name="recover")(recover_command)
app.command(name="index")(index_command)
app.command(name="scan")(scan_command)
app.command(name="refresh")(refresh_command)
app.command(name="run")(run_command)
app.add_typer(gate_app, name="gate")
app.add_typer(rules_app, name="rules")
app.add_typer(studio_app, name="studio")
app.add_typer(stage_app, name="stage")
app.add_typer(program_app, name="program")
app.add_typer(workitem_app, name="workitem")
app.add_typer(verify_app, name="verify")
app.add_typer(telemetry_app, name="telemetry")

if __name__ == "__main__":
    app()
