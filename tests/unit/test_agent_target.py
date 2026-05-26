"""Unit tests for interactive agent target selection."""

from __future__ import annotations

import io

import pytest

from ai_sdlc.integrations import agent_target
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


def test_windows_agent_target_selector_uses_numbered_prompt_without_clear(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = io.StringIO()
    monkeypatch.setattr(agent_target.os, "name", "nt")
    monkeypatch.setattr(
        agent_target.os,
        "system",
        lambda _command: (_ for _ in ()).throw(AssertionError("cls should not run")),
    )

    selected = interactive_select_agent_target(
        IDEKind.CLAUDE_CODE,
        output_stream=output,
        read_line=lambda: "2\n",
    )

    text = output.getvalue()
    assert selected == IDEKind.CODEX
    assert "输入编号" in text
    assert "1. Claude Code" in text
    assert "2. Codex" in text
    assert "方向键选择" not in text
    assert "\x1b[2J" not in text


def test_windows_shell_selector_uses_numbered_default_without_clear(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = io.StringIO()
    monkeypatch.setattr(agent_target.os, "name", "nt")
    monkeypatch.setattr(
        agent_target.os,
        "system",
        lambda _command: (_ for _ in ()).throw(AssertionError("cls should not run")),
    )

    selected = interactive_select_preferred_shell(
        PreferredShell.POWERSHELL,
        output_stream=output,
        read_line=lambda: "\n",
    )

    text = output.getvalue()
    assert selected is PreferredShell.POWERSHELL
    assert "输入编号" in text
    assert "1. PowerShell（默认）" in text
    assert "方向键选择" not in text
    assert "\x1b[2J" not in text
