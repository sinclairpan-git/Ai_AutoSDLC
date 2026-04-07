"""Unit tests for all stage gates, P1 extra gates, and postmortem."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.core.frontend_contract_verification import (
    FRONTEND_CONTRACT_CHECK_OBJECTS,
    FRONTEND_CONTRACT_SOURCE_NAME,
)
from ai_sdlc.core.frontend_gate_verification import (
    FRONTEND_GATE_CHECK_OBJECTS,
    FRONTEND_GATE_SOURCE_NAME,
)
from ai_sdlc.core.release_gate import (
    ReleaseGateCheck,
    ReleaseGateReport,
    build_release_gate_governance_payload,
)
from ai_sdlc.gates.extra_gates import KnowledgeGate, ParallelGate, PostmortemGate
from ai_sdlc.gates.pipeline_gates import (
    CloseGate,
    DecomposeGate,
    DesignGate,
    DoneGate,
    ExecuteGate,
    InitGate,
    PRDGate,
    RefineGate,
    ReviewGate,
    VerificationGate,
    VerifyGate,
)
from ai_sdlc.gates.registry import GateRegistry, get_gate_by_stage
from ai_sdlc.knowledge.engine import initialize_baseline
from ai_sdlc.models.gate import GateVerdict, GovernanceState
from ai_sdlc.models.state import OverlapResult, ParallelPolicy


def _frontend_contract_summary_payload(
    *,
    gate_verdict: str = "PASS",
    blockers: tuple[str, ...] = (),
    coverage_gaps: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "source_name": FRONTEND_CONTRACT_SOURCE_NAME,
        "check_objects": list(FRONTEND_CONTRACT_CHECK_OBJECTS),
        "blockers": list(blockers),
        "coverage_gaps": list(coverage_gaps),
        "advisory_checks": [],
        "gate_verdict": gate_verdict,
        "gate_checks": [],
    }


def _frontend_gate_summary_payload(
    *,
    gate_verdict: str = "PASS",
    blockers: tuple[str, ...] = (),
    coverage_gaps: tuple[str, ...] = (),
) -> dict[str, object]:
    return {
        "source_name": FRONTEND_GATE_SOURCE_NAME,
        "check_objects": list(FRONTEND_GATE_CHECK_OBJECTS),
        "blockers": list(blockers),
        "coverage_gaps": list(coverage_gaps),
        "advisory_checks": [],
        "gate_verdict": gate_verdict,
        "gate_checks": [],
    }


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

    def test_explicit_gate_surfaces_are_registered(self) -> None:
        mapping = get_gate_by_stage()
        assert isinstance(mapping["prd"], PRDGate)
        assert isinstance(mapping["review"], ReviewGate)
        assert isinstance(mapping["done"], DoneGate)
        assert isinstance(mapping["verification"], VerificationGate)


class TestInitGate:
    def test_pass(self, initialized_project_dir: Path, git_repo: Path) -> None:
        import shutil

        ai_sdlc = initialized_project_dir / ".ai-sdlc"
        dest = git_repo / ".ai-sdlc"
        shutil.copytree(ai_sdlc, dest)
        result = InitGate().check({"root": str(git_repo)})
        assert result.verdict == GateVerdict.PASS

    def test_pass_initialized_project_without_git_repo(
        self, initialized_project_dir: Path
    ) -> None:
        result = InitGate().check({"root": str(initialized_project_dir)})
        assert result.verdict == GateVerdict.PASS
        assert all(check.name != "git_initialized" for check in result.checks)

    def test_fail_no_ai_sdlc(self, tmp_path: Path) -> None:
        result = InitGate().check({"root": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY

    def test_fail_when_constitution_has_too_few_principles(
        self, initialized_project_dir: Path
    ) -> None:
        constitution = (
            initialized_project_dir / ".ai-sdlc" / "memory" / "constitution.md"
        )
        constitution.write_text("# Constitution\n- Principle 1\n", encoding="utf-8")

        result = InitGate().check({"root": str(initialized_project_dir)})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "constitution_principles" and not c.passed for c in result.checks)

    def test_fail_when_tech_stack_has_no_source(self, initialized_project_dir: Path) -> None:
        tech_stack = (
            initialized_project_dir / ".ai-sdlc" / "profiles" / "tech-stack.yml"
        )
        tech_stack.write_text("backend:\n  name: python\n", encoding="utf-8")

        result = InitGate().check({"root": str(initialized_project_dir)})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "tech_stack_source" and not c.passed for c in result.checks)


class TestRefineGate:
    @pytest.mark.parametrize(
        "scenario_heading",
        [
            "scenario",
            "Scenario 1:",
            "场景 1:",
            "**场景 1**",
            "#### 场景 1",
            "- 场景 1",
            "- **场景 1**",
        ],
    )
    def test_pass_with_supported_scenario_heading(
        self, tmp_path: Path, scenario_heading: str
    ) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            f"### 用户故事 1\n{scenario_heading}\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
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

    def test_fail_when_user_story_has_no_acceptance_scenario(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\n没有场景\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        result = RefineGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "acceptance_scenarios_present" and not c.passed for c in result.checks)

    def test_fail_when_scenario_is_only_mentioned_in_body(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\n这里提到场景覆盖，但不是验收场景标题。\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        result = RefineGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "acceptance_scenarios_present" and not c.passed for c in result.checks)


class TestPRDGate:
    def test_pass(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "spec.md").write_text(
            "### 用户故事 1\nscenario\n\n- **FR-001**: requirement\n",
            encoding="utf-8",
        )
        result = PRDGate().check({"spec_dir": str(spec_dir)})
        assert result.stage == "prd"
        assert result.verdict == GateVerdict.PASS


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
        (spec_dir / "tasks.md").write_text(
            "### Task 1.1 — 示例\n"
            "- **依赖**：无\n"
            "- **验收标准（AC）**：\n"
            "  1. 示例\n"
        )
        result = DecomposeGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.PASS

    def test_fail_missing_task_acceptance(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs"
        spec_dir.mkdir()
        (spec_dir / "tasks.md").write_text("### Task 1.1 — 示例\n- **依赖**：无\n")
        result = DecomposeGate().check({"spec_dir": str(spec_dir)})
        assert result.verdict == GateVerdict.RETRY
        assert any("acceptance" in c.name or "验收" in c.message for c in result.checks)

    def test_fail_no_tasks(self, tmp_path: Path) -> None:
        result = DecomposeGate().check({"spec_dir": str(tmp_path)})
        assert result.verdict == GateVerdict.RETRY


class TestVerifyGate:
    def test_pass(self) -> None:
        result = VerifyGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    "checkpoint_spec_dir",
                ),
                "verification_sources": ("verify constraints",),
                "constraint_blockers": (),
                "coverage_gaps": (),
            }
        )
        assert result.verdict == GateVerdict.PASS
        assert any(c.name == "verification_surface_declared" and c.passed for c in result.checks)

    def test_passes_with_frontend_contract_summary_payload(self) -> None:
        result = VerifyGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_CONTRACT_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_CONTRACT_SOURCE_NAME,
                ),
                "constraint_blockers": (),
                "coverage_gaps": (),
                "frontend_contract_verification": _frontend_contract_summary_payload(),
            }
        )

        assert result.verdict == GateVerdict.PASS
        assert any(
            c.name == "frontend_contract_summary_declared" and c.passed
            for c in result.checks
        )
        assert any(
            c.name == "frontend_contract_status_clear" and c.passed
            for c in result.checks
        )

    def test_passes_with_frontend_gate_summary_payload(self) -> None:
        result = VerifyGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_GATE_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_GATE_SOURCE_NAME,
                ),
                "constraint_blockers": (),
                "coverage_gaps": (),
                "frontend_gate_verification": _frontend_gate_summary_payload(),
            }
        )

        assert result.verdict == GateVerdict.PASS
        assert any(
            c.name == "frontend_gate_summary_declared" and c.passed
            for c in result.checks
        )
        assert any(
            c.name == "frontend_gate_status_clear" and c.passed
            for c in result.checks
        )

    def test_fail_critical(self) -> None:
        result = VerifyGate().check({"critical_issues": 1, "high_issues": 0})
        assert result.verdict == GateVerdict.RETRY

    def test_fail_too_many_high(self) -> None:
        result = VerifyGate().check({"critical_issues": 0, "high_issues": 5})
        assert result.verdict == GateVerdict.RETRY

    def test_retries_when_frontend_gate_summary_surfaces_071_visual_a11y_issue_review(
        self,
    ) -> None:
        result = VerifyGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_GATE_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_GATE_SOURCE_NAME,
                ),
                "constraint_blockers": (
                    "BLOCKER: visual / a11y issues detected; review and disposition required",
                ),
                "coverage_gaps": ("frontend_visual_a11y_issue_review",),
                "frontend_gate_verification": _frontend_gate_summary_payload(
                    gate_verdict="RETRY",
                    blockers=(
                        "BLOCKER: visual / a11y issues detected; review and disposition required",
                    ),
                    coverage_gaps=("frontend_visual_a11y_issue_review",),
                ),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        status_check = next(c for c in result.checks if c.name == "frontend_gate_status_clear")
        assert "frontend_visual_a11y_issue_review" in status_check.message
        assert "frontend_visual_a11y_evidence_stable_empty" not in status_check.message


class TestVerificationGate:
    def test_blocks_when_constraint_blockers_exist(self) -> None:
        result = VerificationGate().check(
            {
                "verification_check_objects": ("required_governance_files",),
                "verification_sources": ("verify constraints",),
                "constraint_blockers": ("BLOCKER: missing constitution",),
                "coverage_gaps": (),
            }
        )
        assert result.stage == "verification"
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "constraint_blockers_clear" and not c.passed for c in result.checks)

    def test_retries_when_frontend_contract_source_has_no_summary_payload(self) -> None:
        result = VerificationGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_CONTRACT_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_CONTRACT_SOURCE_NAME,
                ),
                "constraint_blockers": (),
                "coverage_gaps": (),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        assert any(
            c.name == "frontend_contract_summary_declared" and not c.passed
            for c in result.checks
        )

    def test_retries_when_frontend_contract_summary_reports_gap(self) -> None:
        result = VerificationGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_CONTRACT_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_CONTRACT_SOURCE_NAME,
                ),
                "constraint_blockers": (),
                "coverage_gaps": (),
                "frontend_contract_verification": _frontend_contract_summary_payload(
                    gate_verdict="RETRY",
                    blockers=(
                        "BLOCKER: frontend contract observations unavailable: no implementation observations declared",
                    ),
                    coverage_gaps=("frontend_contract_observations",),
                ),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        assert any(
            c.name == "frontend_contract_status_clear" and not c.passed
            for c in result.checks
        )

    def test_retries_when_frontend_gate_source_has_no_summary_payload(self) -> None:
        result = VerificationGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_GATE_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_GATE_SOURCE_NAME,
                ),
                "constraint_blockers": (),
                "coverage_gaps": (),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        assert any(
            c.name == "frontend_gate_summary_declared" and not c.passed
            for c in result.checks
        )

    def test_retries_when_frontend_gate_summary_reports_gap(self) -> None:
        result = VerificationGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_GATE_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_GATE_SOURCE_NAME,
                ),
                "constraint_blockers": (),
                "coverage_gaps": (),
                "frontend_gate_verification": _frontend_gate_summary_payload(
                    gate_verdict="RETRY",
                    blockers=(
                        "BLOCKER: frontend gate policy artifacts unavailable: governance/frontend/gates not found",
                    ),
                    coverage_gaps=("frontend_gate_policy_artifacts",),
                ),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        assert any(
            c.name == "frontend_gate_status_clear" and not c.passed
            for c in result.checks
        )

    def test_retries_when_frontend_gate_summary_surfaces_071_visual_a11y_issue_review(
        self,
    ) -> None:
        result = VerificationGate().check(
            {
                "verification_check_objects": (
                    "required_governance_files",
                    *FRONTEND_GATE_CHECK_OBJECTS,
                ),
                "verification_sources": (
                    "verify constraints",
                    FRONTEND_GATE_SOURCE_NAME,
                ),
                "constraint_blockers": (
                    "BLOCKER: visual / a11y issues detected; review and disposition required",
                ),
                "coverage_gaps": ("frontend_visual_a11y_issue_review",),
                "frontend_gate_verification": _frontend_gate_summary_payload(
                    gate_verdict="RETRY",
                    blockers=(
                        "BLOCKER: visual / a11y issues detected; review and disposition required",
                    ),
                    coverage_gaps=("frontend_visual_a11y_issue_review",),
                ),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        status_check = next(c for c in result.checks if c.name == "frontend_gate_status_clear")
        assert "frontend_visual_a11y_issue_review" in status_check.message
        assert "frontend_visual_a11y_evidence_stable_empty" not in status_check.message


class TestReviewGate:
    def test_requires_review_evidence(self) -> None:
        result = ReviewGate().check({"review_recorded": False})
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "review_evidence_present" and not c.passed for c in result.checks)

    def test_passes_with_review_evidence(self) -> None:
        result = ReviewGate().check({"review_recorded": True})
        assert result.verdict == GateVerdict.PASS


class TestExecuteGate:
    def test_pass(self) -> None:
        result = ExecuteGate().check(
            {"tests_passed": True, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.PASS

    def test_stays_local_and_advisory_only_even_with_governance_payload(self) -> None:
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "verification_governance": {
                    "gate_decision_payload": {"decision_result": "block"}
                },
            }
        )
        assert result.verdict == GateVerdict.PASS

    def test_stays_local_and_advisory_only_even_with_provenance_phase1_payload(self) -> None:
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "provenance_phase1": {
                    "decision_result": "block",
                    "enforced": False,
                },
            }
        )
        assert result.verdict == GateVerdict.PASS


def test_release_gate_governance_payload_reuses_gate_capable_minimum_fields() -> None:
    report = ReleaseGateReport(
        source_path="specs/003-cross-cutting-authoring-and-extension-contracts/release-gate-evidence.md",
        overall_verdict="BLOCK",
        checks=(
            ReleaseGateCheck(
                name="portability",
                verdict="BLOCK",
                evidence_source="tests/integration/test_cli_module_invocation.py",
                reason="portability gate escalated to BLOCK",
            ),
        ),
    )

    closed = build_release_gate_governance_payload(
        report,
        decision_subject="release:003-cross-cutting-authoring-and-extension-contracts",
        evidence_refs=(report.source_path,),
    )
    advisory = build_release_gate_governance_payload(
        report,
        decision_subject="release:003-cross-cutting-authoring-and-extension-contracts",
        evidence_refs=(report.source_path,),
        source_closure_status="incomplete",
    )

    assert closed["decision_result"] == "block"
    assert closed["source_closure_status"] == "closed"
    assert closed["observer_version"] == "v1"
    assert advisory["decision_result"] == "advisory"
    assert advisory["source_closure_status"] == "incomplete"

    def test_fail_tests(self) -> None:
        result = ExecuteGate().check(
            {"tests_passed": False, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.RETRY

    def test_fail_without_build_success(self) -> None:
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "build_succeeded": False,
                "committed": True,
                "logged": True,
            }
        )
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "build_succeeded" and not c.passed for c in result.checks)

    def test_log_before_commit_pass(self) -> None:
        """BR-032: log timestamp <= commit timestamp."""
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "log_timestamp": "2026-03-21T10:00:00",
                "commit_timestamp": "2026-03-21T10:00:01",
            }
        )
        assert result.verdict == GateVerdict.PASS

    def test_log_before_commit_fail(self) -> None:
        """BR-032: fails when commit happens before log."""
        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "log_timestamp": "2026-03-21T10:00:02",
                "commit_timestamp": "2026-03-21T10:00:01",
            }
        )
        assert result.verdict == GateVerdict.RETRY

    def test_log_before_commit_skip_when_absent(self) -> None:
        """BR-032: check skipped when timestamps not provided."""
        result = ExecuteGate().check(
            {"tests_passed": True, "committed": True, "logged": True}
        )
        assert result.verdict == GateVerdict.PASS
        assert all(c.name != "log_before_commit" for c in result.checks)

    def test_fail_when_decompose_prerequisite_missing_acceptance(
        self, tmp_path: Path
    ) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text("### Task 1.1\n- **依赖**：无\n", encoding="utf-8")

        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "spec_dir": str(spec_dir),
            }
        )
        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "decompose_prerequisite" and not c.passed for c in result.checks)

    def test_pass_when_decompose_prerequisite_ok(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text(
            "### Task 1.1\n- **依赖**：无\n- **验收标准（AC）**：\n  1. 示例\n",
            encoding="utf-8",
        )

        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "committed": True,
                "logged": True,
                "spec_dir": str(spec_dir),
            }
        )
        assert result.verdict == GateVerdict.PASS
        assert any(c.name == "decompose_prerequisite" and c.passed for c in result.checks)

    def test_fail_when_target_task_is_doc_first(self, tmp_path: Path) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text(
            "### Task 6.44 — 先 spec-plan-tasks 后实现\n"
            "- **依赖**：Task 6.43\n"
            "- **验收标准（AC）**：\n"
            "  1. 先更新 specs\n",
            encoding="utf-8",
        )

        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "build_succeeded": True,
                "committed": True,
                "logged": True,
                "spec_dir": str(spec_dir),
                "target_task_id": "T644",
            }
        )

        assert result.verdict == GateVerdict.RETRY
        assert any(c.name == "doc_first_prerequisite" and not c.passed for c in result.checks)

    def test_fail_when_target_doc_first_task_touches_forbidden_paths(
        self, tmp_path: Path
    ) -> None:
        spec_dir = tmp_path / "specs" / "001"
        spec_dir.mkdir(parents=True)
        (spec_dir / "tasks.md").write_text(
            "### Task 6.44 — 仅文档：冻结需求\n"
            "- **依赖**：Task 6.43\n"
            "- **验收标准（AC）**：\n"
            "  1. 仅更新文档\n",
            encoding="utf-8",
        )

        result = ExecuteGate().check(
            {
                "tests_passed": True,
                "build_succeeded": True,
                "committed": True,
                "logged": True,
                "spec_dir": str(spec_dir),
                "target_task_id": "6.44",
                "changed_files": ("src/ai_sdlc/core/verify_constraints.py",),
            }
        )

        assert result.verdict == GateVerdict.RETRY
        assert any(
            c.name == "doc_first_prerequisite"
            and "verify_constraints.py" in c.message
            for c in result.checks
        )


class TestCloseGate:
    def test_pass(self, tmp_path: Path) -> None:
        (tmp_path / "development-summary.md").write_text("# Summary")
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
                "review_recorded": True,
            }
        )
        assert result.verdict == GateVerdict.PASS

    def test_fail_when_postmortem_is_incomplete(self, tmp_path: Path) -> None:
        (tmp_path / "development-summary.md").write_text("# Summary", encoding="utf-8")
        (tmp_path / "postmortem.md").write_text(
            "# Postmortem\n\n## Root Cause\n\nTODO\n",
            encoding="utf-8",
        )
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
                "postmortem_path": "postmortem.md",
            }
        )
        assert result.verdict == GateVerdict.RETRY
        assert any(
            check.name == "section_fix_description" and not check.passed
            for check in result.checks
        )

    def test_fail_no_summary(self, tmp_path: Path) -> None:
        result = CloseGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
            }
        )
        assert result.verdict == GateVerdict.RETRY


class TestDoneGate:
    def test_blocks_when_knowledge_refresh_is_pending(self, tmp_path: Path) -> None:
        summary = tmp_path / "development-summary.md"
        summary.write_text("# Summary\n", encoding="utf-8")

        result = DoneGate().check(
            {
                "root": str(tmp_path),
                "all_tasks_complete": True,
                "tests_passed": True,
                "review_recorded": True,
                "summary_path": str(summary),
                "knowledge_refresh_level": 2,
                "knowledge_refresh_completed": False,
            }
        )
        assert result.verdict == GateVerdict.RETRY
        assert any(
            c.name == "knowledge_refresh_complete" and not c.passed
            for c in result.checks
        )


# --- P1: KnowledgeGate, ParallelGate, GovernanceState ---


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
        result = gate.check(
            {
                "root": str(tmp_path),
                "spec_changed": True,
            }
        )
        assert result.verdict == GateVerdict.HALT
        assert any("L3" in c.message for c in result.checks)

    def test_halts_on_significant_file_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check(
            {
                "root": str(tmp_path),
                "changed_files": ["src/handler.py"],
            }
        )
        assert result.verdict == GateVerdict.HALT

    def test_passes_on_insignificant_changes(self, tmp_path: Path) -> None:
        initialize_baseline(tmp_path)
        gate = KnowledgeGate()
        result = gate.check(
            {
                "root": str(tmp_path),
                "changed_files": ["README.md"],
            }
        )
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
        result = gate.check(
            {
                "parallel_policy": policy,
                "overlap_result": overlap,
            }
        )
        assert result.verdict == GateVerdict.HALT

    def test_halts_when_contracts_not_frozen(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(
            enabled=True,
            require_overlap_check=True,
            require_contract_freeze=True,
        )
        overlap = OverlapResult(has_conflicts=False)
        result = gate.check(
            {
                "parallel_policy": policy,
                "overlap_result": overlap,
                "contracts_frozen": False,
            }
        )
        assert result.verdict == GateVerdict.HALT

    def test_passes_all_checks(self) -> None:
        gate = ParallelGate()
        policy = ParallelPolicy(
            enabled=True,
            require_overlap_check=True,
            require_contract_freeze=True,
        )
        overlap = OverlapResult(has_conflicts=False)
        result = gate.check(
            {
                "parallel_policy": policy,
                "overlap_result": overlap,
                "contracts_frozen": True,
            }
        )
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
        from ai_sdlc.models.gate import GovernanceItem

        gov = GovernanceState(work_type="maintenance_task")
        gov.items["quality_policy"] = GovernanceItem(exists=True, path="policy.yaml")
        gov.items["branch_policy"] = GovernanceItem(exists=True, path="branch.yaml")
        assert gov.all_required_present


# --- PostmortemGate ---

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
