"""Unit tests for cross-platform shell preference helpers."""

from __future__ import annotations

from ai_sdlc.integrations.agent_target import (
    PreferredShell,
    recommended_shell_for_platform,
)


def test_recommended_shell_for_windows() -> None:
    assert recommended_shell_for_platform("win32") is PreferredShell.POWERSHELL


def test_recommended_shell_for_macos() -> None:
    assert recommended_shell_for_platform("darwin") is PreferredShell.ZSH


def test_recommended_shell_for_linux() -> None:
    assert recommended_shell_for_platform("linux") is PreferredShell.BASH


def test_recommended_shell_for_unknown_platform_falls_back_to_auto() -> None:
    assert recommended_shell_for_platform("plan9") is PreferredShell.AUTO
