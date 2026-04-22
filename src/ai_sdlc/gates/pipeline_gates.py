"""Pipeline stage gates — quality gates for the 7 core SDLC stages.

Each gate implements ``check(context) -> GateResult`` following :class:`GateProtocol`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ai_sdlc.core.frontend_contract_verification import FRONTEND_CONTRACT_SOURCE_NAME
from ai_sdlc.core.frontend_gate_verification import FRONTEND_GATE_SOURCE_NAME
from ai_sdlc.core.frontend_inheritance_truth import (
    summarize_frontend_inheritance_status_for_display,
)
from ai_sdlc.gates.extra_gates import PostmortemGate
from ai_sdlc.gates.task_ac_checks import (
    doc_first_execute_blocker,
    first_task_missing_acceptance,
)
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict
from ai_sdlc.utils.helpers import AI_SDLC_DIR


def _dedupe_text_items(values: list[Any]) -> list[str]:
    deduped: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


class InitGate:
    """Gate check for the INIT stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify INIT stage completion.

        Context keys:
            root (Path): Project root directory.
        """
        root = Path(context["root"])
        checks: list[GateCheck] = []

        ai_sdlc_dir = root / AI_SDLC_DIR
        checks.append(
            GateCheck(
                name="ai_sdlc_dir_exists",
                passed=ai_sdlc_dir.is_dir(),
                message="" if ai_sdlc_dir.is_dir() else f"{ai_sdlc_dir} not found",
            )
        )

        state_file = ai_sdlc_dir / "project" / "config" / "project-state.yaml"
        checks.append(
            GateCheck(
                name="project_state_exists",
                passed=state_file.exists(),
                message="" if state_file.exists() else f"{state_file} not found",
            )
        )

        constitution = ai_sdlc_dir / "memory" / "constitution.md"
        checks.append(
            GateCheck(
                name="constitution_exists",
                passed=constitution.exists(),
                message="" if constitution.exists() else f"{constitution} not found",
            )
        )

        tech_stack = ai_sdlc_dir / "profiles" / "tech-stack.yml"
        checks.append(
            GateCheck(
                name="tech_stack_exists",
                passed=tech_stack.exists(),
                message="" if tech_stack.exists() else f"{tech_stack} not found",
            )
        )

        decisions = ai_sdlc_dir / "profiles" / "decisions.yml"
        checks.append(
            GateCheck(
                name="decisions_exists",
                passed=decisions.exists(),
                message="" if decisions.exists() else f"{decisions} not found",
            )
        )

        principle_count = 0
        if constitution.exists():
            principle_count = len(
                [
                    line
                    for line in constitution.read_text(encoding="utf-8").splitlines()
                    if line.strip().startswith(("- ", "* "))
                ]
            )
        checks.append(
            GateCheck(
                name="constitution_principles",
                passed=principle_count >= 3,
                message=""
                if principle_count >= 3
                else f"Constitution has only {principle_count} principles",
            )
        )

        tech_content = tech_stack.read_text(encoding="utf-8") if tech_stack.exists() else ""
        has_source = "source:" in tech_content.lower() or "来源:" in tech_content
        checks.append(
            GateCheck(
                name="tech_stack_source",
                passed=has_source,
                message="" if has_source else "tech-stack.yml missing source attribution",
            )
        )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="init", verdict=verdict, checks=checks)


class RefineGate:
    """Gate check for the REFINE stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify REFINE stage completion.

        Context keys:
            spec_dir (str): Path to the spec directory.
        """
        spec_dir = Path(context["spec_dir"])
        checks: list[GateCheck] = []

        spec_file = spec_dir / "spec.md"
        spec_exists = spec_file.exists()
        checks.append(
            GateCheck(
                name="spec_exists",
                passed=spec_exists,
                message="" if spec_exists else f"{spec_file} not found",
            )
        )

        if spec_exists:
            content = spec_file.read_text(encoding="utf-8")

            us_count = len(re.findall(r"###\s+用户故事", content))
            checks.append(
                GateCheck(
                    name="user_stories_present",
                    passed=us_count >= 1,
                    message=f"Found {us_count} user stories",
                )
            )

            fr_count = len(re.findall(r"FR-\d{3}", content))
            checks.append(
                GateCheck(
                    name="functional_requirements",
                    passed=fr_count > 0,
                    message=f"Found {fr_count} FRs",
                )
            )

            has_clarification = bool(re.search(r"\[NEEDS[_ ]CLARIFICATION\]", content))
            checks.append(
                GateCheck(
                    name="no_needs_clarification",
                    passed=not has_clarification,
                    message=""
                    if not has_clarification
                        else "Found NEEDS_CLARIFICATION markers",
                )
            )

            has_acceptance_scenarios = _all_user_stories_have_scenarios(content)
            checks.append(
                GateCheck(
                    name="acceptance_scenarios_present",
                    passed=has_acceptance_scenarios,
                    message=""
                    if has_acceptance_scenarios
                    else "One or more user stories are missing acceptance scenarios",
                )
            )
        else:
            for name in (
                "user_stories_present",
                "functional_requirements",
                "no_needs_clarification",
                "acceptance_scenarios_present",
            ):
                checks.append(
                    GateCheck(name=name, passed=False, message="spec.md missing")
                )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="refine", verdict=verdict, checks=checks)


class PRDGate:
    """Explicit PRD Gate surface for refine-entry readiness checks."""

    def check(self, context: dict[str, Any]) -> GateResult:
        result = RefineGate().check(context)
        return GateResult(stage="prd", verdict=result.verdict, checks=result.checks)


class DesignGate:
    """Gate check for the DESIGN stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify DESIGN stage completion.

        Context keys:
            spec_dir (str): Path to the spec directory.
        """
        spec_dir = Path(context["spec_dir"])
        checks: list[GateCheck] = []

        required_files = ["plan.md", "research.md", "data-model.md"]
        for fname in required_files:
            fpath = spec_dir / fname
            checks.append(
                GateCheck(
                    name=f"{fname}_exists",
                    passed=fpath.exists(),
                    message="" if fpath.exists() else f"{fpath} not found",
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="design", verdict=verdict, checks=checks)


class DecomposeGate:
    """Gate check for the DECOMPOSE stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify DECOMPOSE stage completion.

        Context keys:
            spec_dir (str): Path to the spec directory.
        """
        spec_dir = Path(context["spec_dir"])
        checks: list[GateCheck] = []

        tasks_file = spec_dir / "tasks.md"
        exists = tasks_file.exists()
        checks.append(
            GateCheck(
                name="tasks_exists",
                passed=exists,
                message="" if exists else f"{tasks_file} not found",
            )
        )

        if exists:
            content = tasks_file.read_text(encoding="utf-8")
            task_count = len(re.findall(r"### Task \d+\.\d+", content))
            checks.append(
                GateCheck(
                    name="tasks_count",
                    passed=task_count > 0,
                    message=f"Found {task_count} tasks",
                )
            )

            has_deps = "依赖" in content or "depends" in content.lower()
            checks.append(
                GateCheck(
                    name="has_dependencies",
                    passed=has_deps,
                    message="" if has_deps else "No dependency information found",
                )
            )

            # FR-090: each Task block must include task-level acceptance info.
            # Accept any of: "验收标准", standalone "AC", or "**验证**" field.
            first_missing = first_task_missing_acceptance(content)
            checks.append(
                GateCheck(
                    name="task_acceptance_present",
                    passed=first_missing is None,
                    message=""
                    if first_missing is None
                    else f"Missing task-level acceptance for Task {first_missing}",
                )
            )
        else:
            checks.append(
                GateCheck(
                    name="tasks_count",
                    passed=False,
                    message="tasks.md missing",
                )
            )
            checks.append(
                GateCheck(
                    name="has_dependencies",
                    passed=False,
                    message="tasks.md missing",
                )
            )
            checks.append(
                GateCheck(
                    name="task_acceptance_present",
                    passed=False,
                    message="tasks.md missing",
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="decompose", verdict=verdict, checks=checks)


class VerifyGate:
    """Gate check for the VERIFY stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify VERIFY stage completion using the explicit Verification Gate surface."""
        result = VerificationGate().check(context)
        return GateResult(stage="verify", verdict=result.verdict, checks=result.checks)


class VerificationGate:
    """Explicit Verification Gate surface aligned with verify-constraints."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify the explicit verification surface, with legacy fallback support.

        Context keys:
            verification_sources (tuple[str, ...] | list[str]): verification truth sources.
            verification_check_objects (tuple[str, ...] | list[str]): declared check objects.
            constraint_blockers (tuple[str, ...] | list[str]): verify blockers.
            coverage_gaps (tuple[str, ...] | list[str]): optional coverage gaps.
        """
        checks: list[GateCheck] = []
        sources = _string_tuple(context.get("verification_sources", ()))
        objects = _string_tuple(context.get("verification_check_objects", ()))
        blockers = _string_tuple(context.get("constraint_blockers", ()))
        coverage_gaps = _string_tuple(context.get("coverage_gaps", ()))
        frontend_contract_payload = context.get("frontend_contract_verification")
        frontend_gate_payload = context.get("frontend_gate_verification")

        if sources or objects or "constraint_blockers" in context or "coverage_gaps" in context:
            surface_ok = bool(sources) and bool(objects)
            checks.append(
                GateCheck(
                    name="verification_surface_declared",
                    passed=surface_ok,
                    message=""
                    if surface_ok
                    else "Verification Gate surface missing sources or check objects",
                )
            )
            checks.append(
                GateCheck(
                    name="verification_sources_declared",
                    passed=bool(sources),
                    message=""
                    if sources
                    else "Verification Gate has no declared source surface",
                )
            )
            checks.append(
                GateCheck(
                    name="verification_check_objects_declared",
                    passed=bool(objects),
                    message=", ".join(_dedupe_text_items(list(objects)))
                    if objects
                    else "Verification Gate has no declared check objects",
                )
            )
            checks.append(
                GateCheck(
                    name="constraint_blockers_clear",
                    passed=len(blockers) == 0,
                    message=""
                    if not blockers
                    else "; ".join(_dedupe_text_items(list(blockers))[:3]),
                )
            )
            checks.append(
                GateCheck(
                    name="coverage_gaps_clear",
                    passed=len(coverage_gaps) == 0,
                    message=""
                    if not coverage_gaps
                    else "; ".join(_dedupe_text_items(list(coverage_gaps))[:3]),
                )
            )
            if _frontend_contract_summary_requested(
                sources=sources,
                payload=frontend_contract_payload,
            ):
                checks.extend(
                    _frontend_contract_gate_checks(
                        sources=sources,
                        objects=objects,
                        payload=frontend_contract_payload,
                    )
                )
            if _frontend_gate_summary_requested(
                sources=sources,
                payload=frontend_gate_payload,
            ):
                checks.extend(
                    _frontend_gate_gate_checks(
                        sources=sources,
                        objects=objects,
                        payload=frontend_gate_payload,
                    )
                )
            verdict = GateVerdict.PASS if all(c.passed for c in checks) else GateVerdict.RETRY
            return GateResult(stage="verification", verdict=verdict, checks=checks)

        critical = context.get("critical_issues", 0)
        high = context.get("high_issues", 0)
        checks.append(
            GateCheck(
                name="verification_surface_declared",
                passed=True,
                message="Legacy issue-count surface",
            )
        )
        checks.append(
            GateCheck(
                name="no_critical_issues",
                passed=critical == 0,
                message="" if critical == 0 else f"{critical} CRITICAL issues remain",
            )
        )

        checks.append(
            GateCheck(
                name="high_issues_acceptable",
                passed=high <= 3,
                message=""
                if high <= 3
                else f"{high} HIGH issues exceed threshold of 3",
            )
        )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="verification", verdict=verdict, checks=checks)


def _frontend_contract_summary_requested(
    *,
    sources: tuple[str, ...],
    payload: object,
) -> bool:
    return FRONTEND_CONTRACT_SOURCE_NAME in sources or isinstance(payload, dict)


def _frontend_contract_gate_checks(
    *,
    sources: tuple[str, ...],
    objects: tuple[str, ...],
    payload: object,
) -> list[GateCheck]:
    if not isinstance(payload, dict):
        return [
            GateCheck(
                name="frontend_contract_summary_declared",
                passed=False,
                message=(
                    "frontend contract verification source declared but summary payload missing"
                ),
            ),
            GateCheck(
                name="frontend_contract_source_linked",
                passed=FRONTEND_CONTRACT_SOURCE_NAME in sources,
                message=""
                if FRONTEND_CONTRACT_SOURCE_NAME in sources
                else "frontend contract verification summary missing from verification_sources",
            ),
            GateCheck(
                name="frontend_contract_status_clear",
                passed=False,
                message="frontend contract verification summary payload missing",
            ),
        ]

    payload_source = str(payload.get("source_name", "")).strip()
    payload_objects = _string_tuple(payload.get("check_objects", ()))
    payload_blockers = _string_tuple(payload.get("blockers", ()))
    payload_coverage_gaps = _string_tuple(payload.get("coverage_gaps", ()))
    payload_gate_verdict = str(payload.get("gate_verdict", "")).strip()

    summary_declared = (
        bool(payload_source) and bool(payload_objects) and bool(payload_gate_verdict)
    )
    missing_payload_fields = [
        field_name
        for field_name, present in (
            ("source_name", bool(payload_source)),
            ("check_objects", bool(payload_objects)),
            ("gate_verdict", bool(payload_gate_verdict)),
        )
        if not present
    ]
    source_linked = payload_source in sources
    unlinked_objects = [name for name in payload_objects if name not in objects]
    status_clear = (
        payload_gate_verdict == GateVerdict.PASS.value
        and not payload_blockers
        and not payload_coverage_gaps
    )

    return [
        GateCheck(
            name="frontend_contract_summary_declared",
            passed=summary_declared,
            message=""
            if summary_declared
            else "frontend contract verification summary missing fields: "
            + ", ".join(_dedupe_text_items(missing_payload_fields)),
        ),
        GateCheck(
            name="frontend_contract_source_linked",
            passed=source_linked,
            message=""
            if source_linked
            else "frontend contract verification summary not linked to verification_sources",
        ),
        GateCheck(
            name="frontend_contract_check_objects_linked",
            passed=summary_declared and not unlinked_objects,
            message=""
            if summary_declared and not unlinked_objects
            else "frontend contract verification summary objects missing from verification_check_objects: "
            + ", ".join(
                _dedupe_text_items(list(unlinked_objects or payload_objects))
            ),
        ),
        GateCheck(
            name="frontend_contract_status_clear",
            passed=status_clear,
            message=""
            if status_clear
            else _summarize_frontend_contract_status(
                gate_verdict=payload_gate_verdict,
                blockers=payload_blockers,
                coverage_gaps=payload_coverage_gaps,
            ),
        ),
    ]


def _frontend_gate_summary_requested(
    *,
    sources: tuple[str, ...],
    payload: object,
) -> bool:
    return FRONTEND_GATE_SOURCE_NAME in sources or isinstance(payload, dict)


def _frontend_gate_gate_checks(
    *,
    sources: tuple[str, ...],
    objects: tuple[str, ...],
    payload: object,
) -> list[GateCheck]:
    if not isinstance(payload, dict):
        return [
            GateCheck(
                name="frontend_gate_summary_declared",
                passed=False,
                message=(
                    "frontend gate verification source declared but summary payload missing"
                ),
            ),
            GateCheck(
                name="frontend_gate_source_linked",
                passed=FRONTEND_GATE_SOURCE_NAME in sources,
                message=""
                if FRONTEND_GATE_SOURCE_NAME in sources
                else "frontend gate verification summary missing from verification_sources",
            ),
            GateCheck(
                name="frontend_gate_status_clear",
                passed=False,
                message="frontend gate verification summary payload missing",
            ),
        ]

    payload_source = str(payload.get("source_name", "")).strip()
    payload_objects = _string_tuple(payload.get("check_objects", ()))
    payload_blockers = _string_tuple(payload.get("blockers", ()))
    payload_coverage_gaps = _string_tuple(payload.get("coverage_gaps", ()))
    payload_gate_verdict = str(payload.get("gate_verdict", "")).strip()

    summary_declared = (
        bool(payload_source) and bool(payload_objects) and bool(payload_gate_verdict)
    )
    missing_payload_fields = [
        field_name
        for field_name, present in (
            ("source_name", bool(payload_source)),
            ("check_objects", bool(payload_objects)),
            ("gate_verdict", bool(payload_gate_verdict)),
        )
        if not present
    ]
    source_linked = payload_source in sources
    unlinked_objects = [name for name in payload_objects if name not in objects]
    status_clear = (
        payload_gate_verdict == GateVerdict.PASS.value
        and not payload_blockers
        and not payload_coverage_gaps
    )

    return [
        GateCheck(
            name="frontend_gate_summary_declared",
            passed=summary_declared,
            message=""
            if summary_declared
            else "frontend gate verification summary missing fields: "
            + ", ".join(_dedupe_text_items(missing_payload_fields)),
        ),
        GateCheck(
            name="frontend_gate_source_linked",
            passed=source_linked,
            message=""
            if source_linked
            else "frontend gate verification summary not linked to verification_sources",
        ),
        GateCheck(
            name="frontend_gate_check_objects_linked",
            passed=summary_declared and not unlinked_objects,
            message=""
            if summary_declared and not unlinked_objects
            else "frontend gate verification summary objects missing from verification_check_objects: "
            + ", ".join(
                _dedupe_text_items(list(unlinked_objects or payload_objects))
            ),
        ),
        GateCheck(
            name="frontend_gate_status_clear",
            passed=status_clear,
            message=""
            if status_clear
            else _summarize_frontend_gate_status(
                gate_verdict=payload_gate_verdict,
                blockers=payload_blockers,
                coverage_gaps=payload_coverage_gaps,
            ),
        ),
    ]


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    items: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in items:
            items.append(text)
    return tuple(items)


def _summarize_frontend_contract_status(
    *,
    gate_verdict: str,
    blockers: tuple[str, ...],
    coverage_gaps: tuple[str, ...],
) -> str:
    details: list[str] = []
    if gate_verdict:
        details.append(f"gate_verdict={gate_verdict}")
    if blockers:
        details.append(
            "blockers=" + "; ".join(_dedupe_text_items(list(blockers))[:2])
        )
    if coverage_gaps:
        details.append(
            "coverage_gaps="
            + ", ".join(_dedupe_text_items(list(coverage_gaps))[:3])
        )
    if details:
        return "frontend contract verification not clear: " + " | ".join(details)
    return "frontend contract verification not clear"


def _summarize_frontend_gate_status(
    *,
    gate_verdict: str,
    blockers: tuple[str, ...],
    coverage_gaps: tuple[str, ...],
) -> str:
    details: list[str] = []
    if gate_verdict:
        details.append(f"gate_verdict={gate_verdict}")
    if blockers:
        details.append(
            "blockers=" + "; ".join(_dedupe_text_items(list(blockers))[:2])
        )
    if coverage_gaps:
        details.append(
            "coverage_gaps="
            + ", ".join(_dedupe_text_items(list(coverage_gaps))[:3])
        )
    if details:
        return "frontend gate verification not clear: " + " | ".join(details)
    return "frontend gate verification not clear"


class ReviewGate:
    """Explicit Review Gate surface for self-review / code-review evidence."""

    def check(self, context: dict[str, Any]) -> GateResult:
        evidence = str(context.get("review_evidence", "")).strip()
        recorded = bool(context.get("review_recorded", False) or evidence)
        checks = [
            GateCheck(
                name="review_evidence_present",
                passed=recorded,
                message=""
                if recorded
                else "Review Gate requires self-review or equivalent review evidence",
            )
        ]
        verdict = GateVerdict.PASS if recorded else GateVerdict.RETRY
        return GateResult(stage="review", verdict=verdict, checks=checks)


class ExecuteGate:
    """Gate check for each EXECUTE batch."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify EXECUTE batch completion.

        Context keys:
            tests_passed (bool): Whether all tests passed.
            committed (bool): Whether changes are committed.
            logged (bool): Whether execution is logged.
        """
        checks: list[GateCheck] = []

        spec_dir_raw = context.get("spec_dir")
        if isinstance(spec_dir_raw, str) and spec_dir_raw.strip():
            spec_dir = Path(spec_dir_raw)
            tasks_file = spec_dir / "tasks.md"
            if not tasks_file.exists():
                checks.append(
                    GateCheck(
                        name="decompose_prerequisite",
                        passed=False,
                        message=f"{tasks_file} not found",
                    )
                )
            else:
                content = tasks_file.read_text(encoding="utf-8")
                first_missing = first_task_missing_acceptance(content)
                checks.append(
                    GateCheck(
                        name="decompose_prerequisite",
                        passed=first_missing is None,
                        message=""
                        if first_missing is None
                        else f"Task {first_missing} missing acceptance fields",
                    )
                )
                target_task = str(
                    context.get("target_task_id")
                    or context.get("current_task")
                    or ""
                ).strip()
                if target_task:
                    blocker = doc_first_execute_blocker(
                        content,
                        task_ref=target_task,
                        touched_paths=tuple(context.get("changed_files", ()) or ()),
                    )
                    checks.append(
                        GateCheck(
                            name="doc_first_prerequisite",
                            passed=blocker is None,
                            message="" if blocker is None else blocker,
                        )
                    )

        tests_ok = context.get("tests_passed", False)
        checks.append(
            GateCheck(
                name="tests_passed",
                passed=tests_ok,
                message="" if tests_ok else "Tests did not pass",
            )
        )

        build_ok = context.get("build_succeeded", tests_ok)
        checks.append(
            GateCheck(
                name="build_succeeded",
                passed=build_ok,
                message="" if build_ok else "Build did not succeed",
            )
        )

        committed = context.get("committed", False)
        checks.append(
            GateCheck(
                name="changes_committed",
                passed=committed,
                message="" if committed else "Changes not committed",
            )
        )

        logged = context.get("logged", False)
        checks.append(
            GateCheck(
                name="execution_logged",
                passed=logged,
                message="" if logged else "Execution not logged",
            )
        )

        log_ts = context.get("log_timestamp", "")
        commit_ts = context.get("commit_timestamp", "")
        if log_ts and commit_ts:
            order_ok = log_ts <= commit_ts
            checks.append(
                GateCheck(
                    name="log_before_commit",
                    passed=order_ok,
                    message=(
                        ""
                        if order_ok
                        else "Execution log must be written before commit"
                    ),
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="execute", verdict=verdict, checks=checks)


class CloseGate:
    """Gate check for the CLOSE stage."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify CLOSE stage completion via the explicit Done Gate surface."""
        result = DoneGate().check(context)
        checks = list(result.checks)
        verdict = result.verdict

        postmortem_path = context.get("postmortem_path")
        if isinstance(postmortem_path, str) and postmortem_path.strip():
            postmortem = PostmortemGate().check(context)
            checks.extend(postmortem.checks)
            if postmortem.verdict != GateVerdict.PASS:
                verdict = GateVerdict.RETRY

        return GateResult(stage="close", verdict=verdict, checks=checks)


class DoneGate:
    """Explicit Done Gate surface for completion readiness."""

    def check(self, context: dict[str, Any]) -> GateResult:
        """Verify completion semantics, including refresh blocking.

        Context keys:
            root (Path|str): Project root directory.
            all_tasks_complete (bool): Whether all tasks are done.
            tests_passed (bool): Whether final tests passed.
        """
        checks: list[GateCheck] = []

        all_tasks = context.get("all_tasks_complete", False)
        checks.append(
            GateCheck(
                name="all_tasks_complete",
                passed=all_tasks,
                message="" if all_tasks else "Not all tasks are completed",
            )
        )

        tests_ok = context.get("tests_passed", False)
        checks.append(
            GateCheck(
                name="final_tests_passed",
                passed=tests_ok,
                message="" if tests_ok else "Final tests did not pass",
            )
        )

        truth_required = context.get("program_truth_audit_required", False)
        if truth_required:
            truth_ready = context.get("program_truth_audit_ready", False)
            truth_detail = context.get("program_truth_audit_detail", "")
            truth_state = str(context.get("program_truth_audit_state", "")).strip()
            truth_inheritance_status = context.get(
                "program_truth_audit_frontend_inheritance_status", {}
            )
            truth_next_actions = _dedupe_text_items(
                list(context.get("program_truth_audit_next_actions", []) or [])
            )
            truth_message = str(truth_detail or "Program truth audit is not ready")
            if truth_state:
                truth_message = f"state={truth_state}; {truth_message}"
            if isinstance(truth_inheritance_status, dict) and truth_inheritance_status:
                inheritance_summary = summarize_frontend_inheritance_status_for_display(
                    truth_inheritance_status
                )
                if inheritance_summary:
                    truth_message += f"; inheritance: {inheritance_summary}"
                inheritance_risk = _done_gate_frontend_inheritance_risk_note(
                    truth_inheritance_status
                )
                if inheritance_risk:
                    truth_message += f"; risk: {inheritance_risk}"
            if not truth_ready and truth_next_actions:
                truth_message += "; next action: " + " ; ".join(
                    _dedupe_text_items(list(truth_next_actions))[:2]
                )
            checks.append(
                GateCheck(
                    name="program_truth_audit_ready",
                    passed=bool(truth_ready),
                    message="" if truth_ready else truth_message,
                )
            )

        summary_path = context.get("summary_path")
        if isinstance(summary_path, str) and summary_path.strip():
            summary = Path(summary_path)
        else:
            spec_dir_raw = context.get("spec_dir")
            if isinstance(spec_dir_raw, str) and spec_dir_raw.strip():
                summary = Path(spec_dir_raw) / "development-summary.md"
            else:
                root = Path(context.get("root", "."))
                summary = root / "development-summary.md"
        checks.append(
            GateCheck(
                name="summary_exists",
                passed=summary.exists(),
                message="" if summary.exists() else "development-summary.md not found",
            )
        )

        if "review_recorded" in context or "review_evidence" in context:
            review_result = ReviewGate().check(context)
            checks.extend(review_result.checks)

        refresh_level = context.get("knowledge_refresh_level")
        if refresh_level is not None:
            refresh_completed = bool(
                context.get("knowledge_refresh_completed", refresh_level == 0)
            )
            refresh_ok = refresh_level == 0 or refresh_completed
            checks.append(
                GateCheck(
                    name="knowledge_refresh_complete",
                    passed=refresh_ok,
                    message=(
                        "L0: no refresh needed"
                        if refresh_level == 0
                        else (
                            ""
                            if refresh_ok
                            else f"L{refresh_level}: refresh required before completion"
                        )
                    ),
                )
            )

        all_passed = all(c.passed for c in checks)
        verdict = GateVerdict.PASS if all_passed else GateVerdict.RETRY
        return GateResult(stage="done", verdict=verdict, checks=checks)


def _done_gate_frontend_inheritance_risk_note(
    inheritance_status: dict[str, Any],
) -> str:
    generation_state = str(inheritance_status.get("generation", "")).strip()
    quality_state = str(inheritance_status.get("quality", "")).strip()
    if generation_state == "not_inherited" or quality_state == "not_inherited":
        return (
            "continuing may generate against the wrong component library or validate "
            "against the wrong standard"
        )
    if generation_state == "blocked" or quality_state == "blocked":
        return "later code generation or frontend tests remain blocked"
    return ""


def _all_user_stories_have_scenarios(content: str) -> bool:
    """Return True when every user story block contains an acceptance scenario marker."""
    blocks = re.split(r"^###\s+用户故事.*$", content, flags=re.MULTILINE)
    story_blocks = [block for block in blocks[1:] if block.strip()]
    if not story_blocks:
        return False
    return all(
        any(_is_acceptance_scenario_heading(line) for line in block.splitlines())
        for block in story_blocks
    )


def _is_acceptance_scenario_heading(line: str) -> bool:
    """Return True when a line is a supported acceptance scenario heading."""
    normalized = _normalize_markdown_heading(line)
    return bool(re.match(r"^(场景|scenario)\b", normalized, re.IGNORECASE))


def _normalize_markdown_heading(line: str) -> str:
    """Strip common Markdown wrappers before heading classification."""
    normalized = line.strip()
    while normalized:
        previous = normalized
        normalized = re.sub(r"^#{1,6}\s+", "", normalized).strip()
        normalized = re.sub(r"^[-*+]\s+", "", normalized).strip()
        normalized = re.sub(r"^\d+[.)]\s+", "", normalized).strip()
        normalized = re.sub(r"^\*\*(.+)\*\*$", r"\1", normalized).strip()
        normalized = re.sub(r"^__(.+)__$", r"\1", normalized).strip()
        if normalized == previous:
            break
    return normalized
