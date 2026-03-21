"""Tests for P1 gates: KnowledgeGate, ParallelGate, and extended Governance."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.gates.knowledge_gate import KnowledgeGate
from ai_sdlc.gates.parallel_gate import ParallelGate
from ai_sdlc.knowledge.baseline import initialize_baseline
from ai_sdlc.models.gate import GateVerdict
from ai_sdlc.models.governance import GovernanceState
from ai_sdlc.models.parallel import OverlapResult, ParallelPolicy


class TestKnowledgeGate:
    def test_halts_if_not_initialized(self, tmp_path: Path) -> None:
        gate = KnowledgeGate()
        result = gate.check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.HALT
        assert any("not initialized" in c.message.lower() for c in result.checks)

    def test_passes_if_initialized_no_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.PASS

    def test_halts_if_spec_changed(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check({
            "root": str(tmp_path),
            "spec_changed": True,
        })
        assert result.verdict == GateVerdict.HALT
        assert any("L3" in c.message for c in result.checks)

    def test_halts_on_significant_file_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check({
            "root": str(tmp_path),
            "changed_files": ["src/handler.py"],
        })
        assert result.verdict == GateVerdict.HALT

    def test_passes_on_insignificant_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check({
            "root": str(tmp_path),
            "changed_files": ["README.md"],
        })
        assert result.verdict == GateVerdict.PASS


class TestParallelGate:
    def test_passes_without_policy(self) -> None:
        gate = ParallelGate()
        result = gate.check({})
        assert result.verdict == GateVerdict.PASS

    def test_passes_when_disabled(self) -> None:
        gate = ParallelGate()
        result = gate.check({"parallel_policy": ParallelPolicy(enabled=False)})
        assert result.verdict == GateVerdict.PASS

    def test_halts_when_overlap_check_missing(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(enabled=True, require_overlap_check=True)
        result = gate.check({"parallel_policy": policy})
        assert result.verdict == GateVerdict.HALT
        assert any("overlap" in c.message.lower() for c in result.checks)

    def test_halts_on_file_conflicts(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(enabled=True, require_overlap_check=True)
        overlap = OverlapResult(
            has_conflicts=True,
            total_shared_files=2,
            recommendation="Merge groups",
        )
        result = gate.check({
            "parallel_policy": policy,
            "overlap_result": overlap,
        })
        assert result.verdict == GateVerdict.HALT

    def test_halts_when_contracts_not_frozen(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(
            enabled=True,
            require_overlap_check=True,
            require_contract_freeze=True,
        )
        overlap = OverlapResult(has_conflicts=False)
        result = gate.check({
            "parallel_policy": policy,
            "overlap_result": overlap,
            "contracts_frozen": False,
        })
        assert result.verdict == GateVerdict.HALT

    def test_passes_all_checks(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(
            enabled=True,
            require_overlap_check=True,
            require_contract_freeze=True,
        )
        overlap = OverlapResult(has_conflicts=False)
        result = gate.check({
            "parallel_policy": policy,
            "overlap_result": overlap,
            "contracts_frozen": True,
        })
        assert result.verdict == GateVerdict.PASS


class TestGovernanceStateExtended:
    def test_default_has_knowledge_baseline_item(self) -> None:
        gov = GovernanceState()
        assert "knowledge_baseline" in gov.items
        assert "environment_policy" in gov.items

    def test_required_items_by_work_type(self) -> None:
        gov_new = GovernanceState(work_type="new_requirement")
        assert "knowledge_baseline" in gov_new.required_items
        assert "clarify" in gov_new.required_items

        gov_incident = GovernanceState(work_type="production_issue")
        assert "clarify" not in gov_incident.required_items

        gov_maint = GovernanceState(work_type="maintenance_task")
        assert "tech_profile" not in gov_maint.required_items
        assert "quality_policy" in gov_maint.required_items

    def test_all_required_present_false(self) -> None:
        gov = GovernanceState(work_type="new_requirement")
        assert not gov.all_required_present

    def test_all_required_present_true(self) -> None:
        from ai_sdlc.models.governance import GovernanceItem

        gov = GovernanceState(work_type="maintenance_task")
        gov.items["quality_policy"] = GovernanceItem(exists=True, path="policy.yaml")
        gov.items["branch_policy"] = GovernanceItem(exists=True, path="branch.yaml")
        assert gov.all_required_present
