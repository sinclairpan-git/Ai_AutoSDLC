"""Typer-derived CLI command paths (FR-098 / SC-023)."""

from __future__ import annotations

from ai_sdlc.cli.command_names import collect_flat_command_strings


def test_collect_flat_command_strings_includes_nested_subcommands() -> None:
    cmds = collect_flat_command_strings()
    assert "ai-sdlc verify constraints" in cmds
    assert "ai-sdlc workitem close-check" in cmds
    assert "ai-sdlc workitem init" in cmds
    assert "ai-sdlc workitem plan-check" in cmds
    assert "ai-sdlc workitem truth-check" in cmds
    assert "ai-sdlc gate check" in cmds
    assert "ai-sdlc provenance summary" in cmds
    assert "ai-sdlc provenance explain" in cmds
    assert "ai-sdlc provenance gaps" in cmds
    assert len(cmds) > 5
