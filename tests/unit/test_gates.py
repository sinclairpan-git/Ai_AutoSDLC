"""Unit tests for all stage gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.gates.base import GateRegistry
from ai_sdlc.gates.close_gate import CloseGate
from ai_sdlc.gates.decompose_gate import DecomposeGate
from ai_sdlc.gates.design_gate import DesignGate
from ai_sdlc.gates.execute_gate import ExecuteGate
from ai_sdlc.gates.init_gate import InitGate
from ai_sdlc.gates.refine_gate import RefineGate
from ai_sdlc.gates.verify_gate import VerifyGate
from ai_sdlc.models.gate import GateVerdict


class TestGateRegistry:
    def test_register_and_get(self) -> None:
        reg = GateRegistry()
        gate = InitGate()
        reg.register("init", gate)
        assert reg.get("init") is gate

    def test_get_missing(self) -> None:
        reg = GateRegistry()
        assert reg.get("missing") is None

    def test_check_missing_raises(self) -> None:
        reg = GateRegistry()
        with pytest.raises(KeyError):
            reg.check("missing", {})

    def test_stages_list(self) -> None:
        reg = GateRegistry()
        reg.register("init", InitGate())
        reg.register("refine", RefineGate())
        assert set(reg.stages) == {"init", "refine"}


class TestInitGate:
    def test_pass(self, initialized_project_dir: Path, git_repo: Path) -> None:
        import shutil

        ai_sdlc = initialized_project_dir / ".ai-sdlc"
        dest = git_repo / ".ai-sdlc"
        shutil.copytree(ai_sdlc, dest)
        result = InitGate().check({"root": str(git_repo)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_ai_sdlc(self, tmp_path: Path) -> None:
        result = InitGate().check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY


class TestRefineGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\nscenario\n\n- **FR-001**: requirement\n"
        )
        result = RefineGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_spec(self, tmp_path: Path) -> None:
        result = RefineGate().check({"spec_dir": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY

    def test_fail_needs_clarification(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\n[NEEDS_CLARIFICATION]\nFR-001\n"
        )
        result = RefineGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY


class TestDesignGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        for f in ("plan.md", "research.md", "data-model.md"):
            (spec_dir / f).write_text(f"# {f}")
        result = DesignGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_missing(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "plan.md").write_text("# plan")
        result = DesignGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY


class TestDecomposeGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "tasks.md").write_text("### Task 1.1\n- **依赖**：无\n")
        result = DecomposeGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_tasks(self, tmp_path: Path) -> None:
        result = DecomposeGate().check({"spec_dir": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY


class TestVerifyGate:
    def test_pass(self) -> None:
        result = VerifyGate().check({"critical_issues": 0, "high_issues": 2})
        assert result.verdict == GateVerdict.PASS

    def test_fail_critical(self) -> None:
        result = VerifyGate().check({"critical_issues": 1, "high_issues": 0})
        assert result.verdict == GateVerdict.RETRY

    def test_fail_too_many_high(self) -> None:
        result = VerifyGate().check({"critical_issues": 0, "high_issues": 5})
        assert result.verdict == GateVerdict.RETRY


class TestExecuteGate:
    def test_pass(self) -> None:
        result = ExecuteGate().check(
            {"tests_passed": True, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.PASS

    def test_fail_tests(self) -> None:
        result = ExecuteGate().check(
            {"tests_passed": False, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.RETRY


class TestCloseGate:
    def test_pass(self, tmp_path: Path) -> None:
        (tmp_path / "development-summary.md").write_text("# Summary")
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
            }
        )
        assert result.verdict == GateVerdict.PASS

    def test_fail_no_summary(self, tmp_path: Path) -> None:
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
            }
        )
        assert result.verdict == GateVerdict.RETRY
