"""Tests for SDLCRunner confirm mode."""

from __future__ import annotations

import shutil
from pathlib import Path

from ai_sdlc.core.runner import SDLCRunner
from ai_sdlc.gates.base import GateRegistry
from ai_sdlc.gates.init_gate import InitGate


class TestConfirmMode:
    def test_confirm_callback_pauses_pipeline(
        self,
        initialized_project_dir: Path,
        git_repo: Path,
    ) -> None:
        """Pipeline pauses when confirm callback returns False."""
        ai_sdlc = initialized_project_dir / ".ai-sdlc"
        dest = git_repo / ".ai-sdlc"
        shutil.copytree(ai_sdlc, dest)
        (git_repo / ".ai-sdlc" / "state").mkdir(exist_ok=True)

        runner = SDLCRunner(git_repo)

        call_count = 0

        def reject_callback(stage: str, _result: object) -> bool:
            nonlocal call_count
            call_count += 1
            return False

        reg = GateRegistry()
        reg.register("init", InitGate())
        runner._registry = reg

        runner.run(mode="confirm", on_confirm=reject_callback)

        assert call_count >= 1
