"""Packaging configuration regressions for wheel contents."""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_wheel_force_includes_workitem_markdown_templates() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    force_include = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]

    expected = {
        "templates/spec-template.md": "ai_sdlc/templates/spec-template.md",
        "templates/plan-template.md": "ai_sdlc/templates/plan-template.md",
        "templates/tasks-template.md": "ai_sdlc/templates/tasks-template.md",
        "templates/execution-log-template.md": "ai_sdlc/templates/execution-log-template.md",
    }

    for source, destination in expected.items():
        assert force_include.get(source) == destination
