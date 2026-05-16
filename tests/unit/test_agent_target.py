"""Unit tests for interactive agent target selection."""

from __future__ import annotations

import io

from ai_sdlc.integrations.agent_target import (
    IDEKind,
    PreferredShell,
    interactive_select_agent_target,
    interactive_select_preferred_shell,
)


def test_interactive_select_agent_target_uses_arrow_navigation() -> None:
    output = io.StringIO()
    keys = iter(["down", "down", "enter"])

    selected = interactive_select_agent_target(
        IDEKind.CLAUDE_CODE,
        read_key=lambda: next(keys),
        output_stream=output,
    )

    assert selected == IDEKind.CURSOR
    assert "\x1b[2J" not in output.getvalue()


def test_interactive_select_preferred_shell_uses_arrow_navigation_without_ansi_on_non_tty() -> None:
    output = io.StringIO()
    keys = iter(["down", "enter"])

    selected = interactive_select_preferred_shell(
        PreferredShell.POWERSHELL,
        read_key=lambda: next(keys),
        output_stream=output,
    )

    assert selected is PreferredShell.BASH
    assert "\x1b[2J" not in output.getvalue()
