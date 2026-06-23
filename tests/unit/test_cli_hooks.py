"""Regression tests for shared CLI hooks."""

from __future__ import annotations

from pathlib import Path

import pytest
from rich.console import Console

from ai_sdlc.cli import cli_hooks
from ai_sdlc.routers.bootstrap import init_project


def test_adapter_hook_warns_and_continues_when_project_config_is_locked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    def _locked_config(_root: Path) -> object:
        raise PermissionError(
            "[WinError 5] Access is denied: "
            "'.ai-sdlc/project/config/project-config.yaml'"
        )

    console = Console(record=True, width=120)
    monkeypatch.setattr(cli_hooks, "ensure_ide_adaptation", _locked_config)

    cli_hooks.run_ide_adapter_if_initialized(console=console)

    output = console.export_text()
    normalized_output = " ".join(output.split())
    assert "project-config.yaml appears to be temporarily locked" in output
    assert "Current command will continue" in output
    assert (
        "does not mean code generation or the frontend build failed"
        in normalized_output
    )
    assert "WinError 5" in output


def test_adapter_hook_still_raises_unexpected_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    def _unexpected_error(_root: Path) -> object:
        raise RuntimeError("unexpected adapter failure")

    monkeypatch.setattr(cli_hooks, "ensure_ide_adaptation", _unexpected_error)

    with pytest.raises(RuntimeError, match="unexpected adapter failure"):
        cli_hooks.run_ide_adapter_if_initialized(console=Console())


def test_adapter_hook_reraises_permission_errors_outside_project_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    init_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    def _locked_adapter_file(_root: Path) -> object:
        raise PermissionError("[WinError 5] Access is denied: 'AGENTS.md'")

    monkeypatch.setattr(cli_hooks, "ensure_ide_adaptation", _locked_adapter_file)

    with pytest.raises(PermissionError, match="AGENTS.md"):
        cli_hooks.run_ide_adapter_if_initialized(console=Console())
