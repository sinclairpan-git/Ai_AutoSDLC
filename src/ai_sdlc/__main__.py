"""Allow `python -m ai_sdlc` when the console script is not on PATH."""

from __future__ import annotations

import sys

from ai_sdlc.cli.main import app


def _emit_ascii_module_help() -> None:
    """Emit an ASCII-only fallback help surface for module invocation on Windows."""
    sys.stdout.write(
        "Usage: python -m ai_sdlc [OPTIONS] COMMAND [ARGS]...\n"
        "\n"
        "ai-sdlc: AI-native SDLC automation framework.\n"
        "\n"
        "Commands:\n"
        "  init\n"
        "  doctor\n"
        "  status\n"
        "  recover\n"
        "  index\n"
        "  scan\n"
        "  refresh\n"
        "  run\n"
        "  adapter\n"
        "  gate\n"
        "  rules\n"
        "  studio\n"
        "  stage\n"
        "  program\n"
        "  host-runtime\n"
        "  workitem\n"
        "  verify\n"
        "  telemetry\n"
        "  provenance\n"
        "  trace\n"
        "  self-update\n"
    )


if __name__ == "__main__":
    if len(sys.argv) == 1 or (
        len(sys.argv) == 2 and sys.argv[1] in {"--help", "-h"}
    ):
        _emit_ascii_module_help()
        raise SystemExit(0)
    app()
