"""Typer-derived CLI command paths (FR-098 / SC-023)."""

from __future__ import annotations

from types import SimpleNamespace

from ai_sdlc.cli.command_names import _walk_group, collect_flat_command_strings


def test_command_inventory_includes_commands_hidden_only_from_root_help() -> None:
    group = SimpleNamespace(
        commands={
            "visible": SimpleNamespace(hidden=False),
            "advanced": SimpleNamespace(hidden=True),
        }
    )

    assert _walk_group(group, ("ai-sdlc",)) == [
        "ai-sdlc advanced",
        "ai-sdlc visible",
    ]


def test_collect_flat_command_strings_includes_nested_subcommands() -> None:
    cmds = collect_flat_command_strings()
    assert "ai-sdlc adopt" in cmds
    assert "ai-sdlc adapter activate" in cmds
    assert "ai-sdlc adapter select" in cmds
    assert "ai-sdlc adapter status" in cmds
    assert "ai-sdlc agentops doctor" in cmds
    assert "ai-sdlc agentops retry" in cmds
    assert "ai-sdlc agentops status" in cmds
    assert "ai-sdlc verify constraints" in cmds
    assert "ai-sdlc workitem close-check" in cmds
    assert "ai-sdlc workitem init" in cmds
    assert "ai-sdlc workitem plan-check" in cmds
    assert "ai-sdlc workitem truth-check" in cmds
    assert "ai-sdlc gate check" in cmds
    assert "ai-sdlc provenance summary" in cmds
    assert "ai-sdlc provenance explain" in cmds
    assert "ai-sdlc provenance gaps" in cmds
    assert "ai-sdlc loop status" in cmds
    assert "ai-sdlc loop list" in cmds
    assert "ai-sdlc pr-review doctor" in cmds
    assert "ai-sdlc pr-review start" in cmds
    assert "ai-sdlc pr-review status" in cmds
    assert "ai-sdlc pr-review fix" in cmds
    assert "ai-sdlc pr-review rerun" in cmds
    assert "ai-sdlc pr-review close" in cmds
    assert len(cmds) > 5
