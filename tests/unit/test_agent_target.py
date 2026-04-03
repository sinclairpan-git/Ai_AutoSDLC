"""Unit tests for interactive agent target selection."""

from __future__ import annotations

import io

from ai_sdlc.integrations.agent_target import IDEKind, interactive_select_agent_target


def test_interactive_select_agent_target_uses_arrow_navigation() -> None:
    keys = iter(["down", "down", "enter"])

    selected = interactive_select_agent_target(
        IDEKind.CLAUDE_CODE,
        read_key=lambda: next(keys),
        output_stream=io.StringIO(),
    )

    assert selected == IDEKind.CURSOR
