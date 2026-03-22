"""Unit tests for PostmortemGate."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.gates.postmortem_gate import PostmortemGate
from ai_sdlc.models.gate import GateVerdict

COMPLETE_POSTMORTEM = """# Postmortem: INC-001

## Root Cause

Database connection pool exhausted due to unclosed connections in error path.

## Fix Description

Added connection cleanup in finally block and increased pool size from 10 to 25.

## Lessons Learned

1. Always use context managers for database connections
2. Add connection pool monitoring alerts
"""


class TestPostmortemGate:
    def test_complete_postmortem_passes(self, tmp_path: Path) -> None:
        pm = tmp_path / "postmortem.md"
        pm.write_text(COMPLETE_POSTMORTEM, encoding="utf-8")
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "postmortem.md"})
        assert result.verdict == GateVerdict.PASS
        assert all(c.passed for c in result.checks)

    def test_missing_file_retries(self, tmp_path: Path) -> None:
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "missing.md"})
        assert result.verdict == GateVerdict.RETRY

    def test_empty_root_cause_section_retries(self, tmp_path: Path) -> None:
        pm = tmp_path / "postmortem.md"
        pm.write_text(
            """# Postmortem

## Root Cause

## Fix Description

We fixed it.

## Lessons Learned

Be careful.
""",
            encoding="utf-8",
        )
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "postmortem.md"})
        assert result.verdict == GateVerdict.RETRY
        section_checks = [c for c in result.checks if "section_" in c.name]
        root_cause = next(c for c in section_checks if "root_cause" in c.name)
        assert not root_cause.passed

    def test_todo_in_lessons_learned_retries(self, tmp_path: Path) -> None:
        pm = tmp_path / "postmortem.md"
        pm.write_text(
            """# Postmortem

## Root Cause

The bug.

## Fix Description

The fix.

## Lessons Learned

TODO: write lessons
""",
            encoding="utf-8",
        )
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path, "postmortem_path": "postmortem.md"})
        assert result.verdict == GateVerdict.RETRY

    def test_no_postmortem_path_retries(self, tmp_path: Path) -> None:
        gate = PostmortemGate()
        result = gate.check({"root": tmp_path})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "postmortem_path" and not c.passed for c in result.checks)
