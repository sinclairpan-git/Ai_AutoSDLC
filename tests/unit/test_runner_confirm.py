"""Tests for SDLCRunner confirm mode."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from ai_sdlc.core.runner import SDLCRunner
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict


class TestConfirmMode:
    def test_confirm_callback_pauses_pipeline(self, tmp_path: Path) -> None:
        """Pipeline pauses when confirm callback returns False."""
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

        runner = SDLCRunner(tmp_path)

        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        calls: list[str] = []

        def reject(stage: str, _result: object) -> bool:
            calls.append(stage)
            return False

        runner.run(mode="confirm", on_confirm=reject)
        assert len(calls) >= 1

    def test_auto_mode_ignores_callback(self, tmp_path: Path) -> None:
        """Auto mode does not call the confirm callback."""
        ai_sdlc = tmp_path / ".ai-sdlc"
        (ai_sdlc / "project" / "config").mkdir(parents=True)
        (ai_sdlc / "state").mkdir(parents=True)
        (ai_sdlc / "project" / "config" / "project-state.yaml").write_text(
            "status: initialized\nproject_name: test\n"
        )

        runner = SDLCRunner(tmp_path)

        pass_result = GateResult(
            stage="init",
            verdict=GateVerdict.PASS,
            checks=[GateCheck(name="ok", passed=True)],
        )
        runner._run_gate = MagicMock(return_value=pass_result)

        calls: list[str] = []

        def track(stage: str, _result: object) -> bool:
            calls.append(stage)
            return True

        runner.run(mode="auto", on_confirm=track)
        assert len(calls) == 0
