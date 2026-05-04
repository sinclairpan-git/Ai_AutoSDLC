"""Unit tests for the in-tree packaging backend."""

from __future__ import annotations

import zipfile
from pathlib import Path

import packaging_backend


def test_build_wheel_includes_templates_and_entry_points(tmp_path: Path) -> None:
    wheel_name = packaging_backend.build_wheel(str(tmp_path))

    wheel_path = tmp_path / wheel_name
    assert wheel_path.is_file()
    assert wheel_name.endswith("-py3-none-any.whl")

    with zipfile.ZipFile(wheel_path) as archive:
        names = set(archive.namelist())

        assert "ai_sdlc/templates/spec-template.md" in names
        assert "ai_sdlc/templates/plan-template.md" in names
        assert "ai_sdlc/templates/tasks-template.md" in names
        assert "ai_sdlc/templates/execution-log-template.md" in names

        entry_points = archive.read("ai_sdlc-0.7.3.dist-info/entry_points.txt").decode(
            "utf-8"
        )
        assert "[console_scripts]" in entry_points
        assert "ai-sdlc = ai_sdlc.cli.main:app" in entry_points
