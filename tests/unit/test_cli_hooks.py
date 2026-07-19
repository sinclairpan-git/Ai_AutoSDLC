"""Regression tests for shared CLI hooks."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from rich.console import Console

from ai_sdlc.cli import cli_hooks
from ai_sdlc.integrations import ide_adapter
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


def test_adapter_hook_warns_after_adapter_write_when_config_persist_is_locked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    baseline_root = tmp_path / "baseline"
    baseline_root.mkdir()
    init_project(baseline_root)
    candidate_root = tmp_path / "candidate"
    shutil.copytree(baseline_root, candidate_root)
    for root in (baseline_root, candidate_root):
        (root / ".cursor").mkdir()

    config_rel = Path(".ai-sdlc/project/config/project-config.yaml")
    rule_rel = Path(".cursor/rules/ai-sdlc.mdc")
    project_config = candidate_root / config_rel
    config_before = project_config.read_bytes()

    success_console = Console(record=True, width=200)
    monkeypatch.chdir(baseline_root)
    cli_hooks.run_ide_adapter_if_initialized(console=success_console)
    expected_rule = (baseline_root / rule_rel).read_bytes()
    assert (baseline_root / config_rel).read_bytes() != config_before

    def _files(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    before = _files(candidate_root)
    canonical_rule = candidate_root / rule_rel
    locked_error = PermissionError(13, "Access is denied", str(project_config))

    def _locked_persist(*args: object, **kwargs: object) -> None:
        _ = args, kwargs
        assert canonical_rule.is_file()
        raise locked_error

    monkeypatch.setattr(ide_adapter, "_persist_config", _locked_persist)
    monkeypatch.chdir(candidate_root)
    console = Console(record=True, width=200)

    cli_hooks.run_ide_adapter_if_initialized(console=console)

    after = _files(candidate_root)
    changed = {
        path
        for path in before.keys() | after.keys()
        if before.get(path) != after.get(path)
    }
    assert changed == {rule_rel.as_posix()}
    assert canonical_rule.read_bytes() == expected_rule
    assert project_config.read_bytes() == config_before
    normalized_output = " ".join(console.export_text().split())
    expected_output = " ".join(
        (
            "AI-SDLC adapter metadata write skipped: project-config.yaml appears to "
            f"be temporarily locked ({locked_error}). Current command will continue; "
            "this does not mean code generation or the frontend build failed. Run "
            "`ai-sdlc adapter status` later only when troubleshooting."
        ).split()
    )
    assert normalized_output == expected_output
