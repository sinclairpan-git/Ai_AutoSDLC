"""AI-SDLC CLI entry point."""

import typer

from ai_sdlc.cli.gate_cmd import gate_app
from ai_sdlc.cli.index_cmd import index_command
from ai_sdlc.cli.init_cmd import init_command
from ai_sdlc.cli.recover_cmd import recover_command
from ai_sdlc.cli.refresh_cmd import refresh_command
from ai_sdlc.cli.scan_cmd import scan_command
from ai_sdlc.cli.status_cmd import status_command
from ai_sdlc.cli.studio_cmd import studio_app

app = typer.Typer(
    name="ai-sdlc",
    help="AI-native SDLC automation framework.",
    no_args_is_help=True,
)

app.command(name="init")(init_command)
app.command(name="status")(status_command)
app.command(name="recover")(recover_command)
app.command(name="index")(index_command)
app.command(name="scan")(scan_command)
app.command(name="refresh")(refresh_command)
app.add_typer(gate_app, name="gate")
app.add_typer(studio_app, name="studio")

if __name__ == "__main__":
    app()
