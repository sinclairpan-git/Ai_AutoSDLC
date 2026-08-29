"""Allow `python -m ai_sdlc` when the console script is not on PATH."""

from __future__ import annotations

import sys

from ai_sdlc import __version__
from ai_sdlc.cli.main import app


def _emit_ascii_module_help() -> None:
    """Emit an ASCII-only fallback help surface for module invocation on Windows."""
    sys.stdout.write(
        "Usage: python -m ai_sdlc [OPTIONS] COMMAND [ARGS]...\n"
        "\n"
        "ai-sdlc: AI-native SDLC automation framework.\n"
        "Common commands are shown here; advanced commands remain directly callable.\n"
        "\n"
        "Commands:\n"
        "  init\n"
        "  adopt\n"
        "  status\n"
        "  recover\n"
        "  run\n"
        "  self-update\n"
    )


if __name__ == "__main__":
    if len(sys.argv) == 1 or (
        len(sys.argv) == 2 and sys.argv[1] in {"--help", "-h"}
    ):
        _emit_ascii_module_help()
        raise SystemExit(0)
    if len(sys.argv) == 2 and sys.argv[1] == "--version":
        sys.stdout.write(f"{__version__}\n")
        raise SystemExit(0)
    app()
