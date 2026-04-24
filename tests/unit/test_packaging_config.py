"""Packaging configuration regressions for wheel contents."""

from __future__ import annotations

import tarfile
import tomllib
import zipfile
from pathlib import Path

import packaging_backend

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_build_system_uses_in_tree_backend() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    build_system = pyproject["build-system"]

    assert build_system["requires"] == []
    assert build_system["build-backend"] == "packaging_backend"
    assert build_system["backend-path"] == ["."]


def test_wheel_force_includes_workitem_markdown_templates() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    force_include = pyproject["tool"]["ai_sdlc"]["packaging"]["force-include"]

    expected = {
        "templates/spec-template.md": "ai_sdlc/templates/spec-template.md",
        "templates/plan-template.md": "ai_sdlc/templates/plan-template.md",
        "templates/tasks-template.md": "ai_sdlc/templates/tasks-template.md",
        "templates/execution-log-template.md": "ai_sdlc/templates/execution-log-template.md",
        "scripts/frontend_browser_gate_probe_runner.mjs": "ai_sdlc/runtime_assets/frontend_browser_gate_probe_runner.mjs",
    }

    for source, destination in expected.items():
        assert force_include.get(source) == destination


def test_editable_wheel_includes_browser_gate_probe_runner_runtime_asset(
    tmp_path: Path,
) -> None:
    wheel_name = packaging_backend.build_editable(str(tmp_path))
    wheel_path = tmp_path / wheel_name

    with zipfile.ZipFile(wheel_path) as archive:
        assert (
            "ai_sdlc/runtime_assets/frontend_browser_gate_probe_runner.mjs"
            in archive.namelist()
        )


def test_sdist_includes_browser_gate_probe_runner_source(
    tmp_path: Path,
) -> None:
    sdist_name = packaging_backend.build_sdist(str(tmp_path))
    sdist_path = tmp_path / sdist_name

    with tarfile.open(sdist_path, "r:gz") as archive:
        members = archive.getnames()
    assert any(
        member.endswith("/scripts/frontend_browser_gate_probe_runner.mjs")
        for member in members
    )
