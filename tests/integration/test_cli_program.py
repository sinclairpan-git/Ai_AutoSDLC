"""Integration tests for ai-sdlc program CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from ai_sdlc.cli.main import app

runner = CliRunner()


def _write_manifest(root: Path) -> None:
    (root / "specs" / "001-auth").mkdir(parents=True)
    (root / "specs" / "002-course").mkdir(parents=True)
    (root / "specs" / "003-enroll").mkdir(parents=True)
    (root / "program-manifest.yaml").write_text(
        """
schema_version: "1"
specs:
  - id: "001-auth"
    path: "specs/001-auth"
    depends_on: []
  - id: "002-course"
    path: "specs/002-course"
    depends_on: []
  - id: "003-enroll"
    path: "specs/003-enroll"
    depends_on: ["001-auth", "002-course"]
""".strip()
        + "\n",
        encoding="utf-8",
    )


class TestCliProgram:
    def test_program_validate_pass(self, initialized_project_dir: Path) -> None:
        _write_manifest(initialized_project_dir)
        with patch(
            "ai_sdlc.cli.program_cmd.find_project_root",
            return_value=initialized_project_dir,
        ):
            result = runner.invoke(app, ["program", "validate"])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_program_validate_fail_cycle(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        (root / "specs" / "a").mkdir(parents=True)
        (root / "specs" / "b").mkdir(parents=True)
        (root / "program-manifest.yaml").write_text(
            """
specs:
  - id: a
    path: specs/a
    depends_on: [b]
  - id: b
    path: specs/b
    depends_on: [a]
""".strip()
            + "\n",
            encoding="utf-8",
        )
        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            result = runner.invoke(app, ["program", "validate"])
        assert result.exit_code == 1
        assert "cycle" in result.output.lower()

    def test_program_status_and_plan(self, initialized_project_dir: Path) -> None:
        root = initialized_project_dir
        _write_manifest(root)
        (root / "specs" / "001-auth" / "tasks.md").write_text(
            "- [x] done\n- [ ] todo\n", encoding="utf-8"
        )
        (root / "specs" / "002-course" / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )

        with patch("ai_sdlc.cli.program_cmd.find_project_root", return_value=root):
            status = runner.invoke(app, ["program", "status"])
            plan = runner.invoke(app, ["program", "plan"])

        assert status.exit_code == 0
        assert "Program Status" in status.output
        assert "001-auth" in status.output
        assert "003-enroll" in status.output

        assert plan.exit_code == 0
        assert "Program Plan" in plan.output
        assert "003-enroll" in plan.output
