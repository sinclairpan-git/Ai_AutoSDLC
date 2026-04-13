"""Frontend gate verification report/context helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED,
)
from ai_sdlc.core.frontend_contract_verification import (
    FrontendContractVerificationReport,
    build_frontend_contract_verification_report,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceArtifact,
)
from ai_sdlc.generators.frontend_contract_artifacts import frontend_contracts_root
from ai_sdlc.generators.frontend_gate_policy_artifacts import frontend_gate_policy_root
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    frontend_generation_governance_root,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserProbeExecutionReceipt,
    BrowserQualityBundleMaterializationInput,
    BrowserQualityGateExecutionContext,
)
from ai_sdlc.models.gate import GateCheck, GateResult, GateVerdict

FRONTEND_GATE_SOURCE_NAME = "frontend gate verification"
FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT = "frontend_visual_a11y_policy_artifacts"
FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT = "frontend_visual_a11y_evidence"
FRONTEND_GATE_CHECK_OBJECTS = (
    "frontend_gate_policy_artifacts",
    "frontend_generation_governance_artifacts",
    "frontend_contract_verification",
)
FRONTEND_GATE_EXECUTE_STATE_READY = "ready"
FRONTEND_GATE_EXECUTE_STATE_BLOCKED = "blocked"
FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED = "recheck_required"
FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION = "needs_remediation"
FRONTEND_GATE_DECISION_REASON_ALL_CHECKS_PASSED = "all_checks_passed"
FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY = "advisory_only"
FRONTEND_GATE_DECISION_REASON_SCOPE_OR_LINKAGE_INVALID = "scope_or_linkage_invalid"
FRONTEND_GATE_DECISION_REASON_EVIDENCE_MISSING = "evidence_missing"
FRONTEND_GATE_DECISION_REASON_TRANSIENT_RUN_FAILURE = "transient_run_failure"
FRONTEND_GATE_DECISION_REASON_ACTUAL_QUALITY_BLOCKER = "actual_quality_blocker"
FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY = "result_inconsistency"
FRONTEND_EVIDENCE_CLASS_FRAMEWORK_CAPABILITY = "framework_capability"
FRONTEND_OBSERVATION_ATTACHMENT_COVERAGE_GAP = "frontend_contract_observations"
FRONTEND_ATTACHMENT_REQUIREMENT_WAIVED = "waived_for_framework_capability"


@dataclass(frozen=True, slots=True)
class FrontendGateVerificationReport:
    """Structured frontend gate verification report for verify/gate integration."""

    gate_policy_root: str
    generation_root: str
    source_name: str
    check_objects: tuple[str, ...]
    blockers: tuple[str, ...]
    coverage_gaps: tuple[str, ...]
    advisory_checks: tuple[str, ...]
    gate_result: GateResult
    upstream_contract_verification: dict[str, object]
    visual_a11y_evidence_summary: dict[str, object] | None = None

    def to_json_dict(self) -> dict[str, object]:
        payload = {
            "gate_policy_root": self.gate_policy_root,
            "generation_root": self.generation_root,
            "source_name": self.source_name,
            "check_objects": list(self.check_objects),
            "blockers": list(self.blockers),
            "coverage_gaps": list(self.coverage_gaps),
            "advisory_checks": list(self.advisory_checks),
            "gate_verdict": self.gate_result.verdict.value,
            "gate_checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "message": check.message,
                }
                for check in self.gate_result.checks
            ],
            "upstream_contract_verification": self.upstream_contract_verification,
        }
        if self.visual_a11y_evidence_summary is not None:
            payload["visual_a11y_evidence_summary"] = self.visual_a11y_evidence_summary
        return payload


@dataclass(frozen=True, slots=True)
class FrontendGateExecuteDecision:
    """Decision projection for runtime/frontend execute gating."""

    execute_gate_state: str
    decision_reason: str
    blockers: tuple[str, ...] = ()
    recheck_required: bool = False
    recheck_reason_codes: tuple[str, ...] = ()
    remediation_hints: tuple[str, ...] = ()
    remediation_reason_codes: tuple[str, ...] = ()
    source_linkage_refs: dict[str, str] = field(default_factory=dict)


def build_frontend_gate_verification_report(
    root: Path,
    observations: list[PageImplementationObservation],
    *,
    observation_artifact_status: str = (
        FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    ),
    observation_artifact_path: Path | None = None,
    observation_artifact_error: str | None = None,
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None = None,
) -> FrontendGateVerificationReport:
    """Translate artifact presence and contract prerequisite into gate summary fields."""

    gate_root = frontend_gate_policy_root(root)
    generation_root = frontend_generation_governance_root(root)
    contract_report = build_frontend_contract_verification_report(
        frontend_contracts_root(root),
        observations,
        observation_artifact_status=observation_artifact_status,
        observation_artifact_path=observation_artifact_path,
        observation_artifact_error=observation_artifact_error,
    )

    gate_present, gate_message = _required_artifacts_present(
        gate_root,
        (
            "gate.manifest.yaml",
            "gate-matrix.yaml",
            "compatibility-policies.yaml",
            "report-types.yaml",
        ),
    )
    visual_a11y_required = _requires_visual_a11y_policy_artifacts(gate_root)
    visual_a11y_present = True
    visual_a11y_message = ""
    if visual_a11y_required:
        visual_a11y_present, visual_a11y_message = _required_artifacts_present(
            gate_root,
            (
                "visual-foundation-coverage-matrix.yaml",
                "a11y-foundation-coverage-matrix.yaml",
                "visual-a11y-evidence-boundary.yaml",
                "visual-a11y-feedback-boundary.yaml",
            ),
        )
    generation_present, generation_message = _required_artifacts_present(
        generation_root,
        (
            "generation.manifest.yaml",
            "hard-rules.yaml",
            "token-rules.yaml",
            "whitelist.yaml",
        ),
    )
    contract_clear = (
        contract_report.gate_result.verdict == GateVerdict.PASS
        and not contract_report.blockers
        and not contract_report.coverage_gaps
    )
    visual_a11y_evidence_clear = True
    visual_a11y_evidence_message = ""
    visual_a11y_evidence_summary: dict[str, object] | None = None
    if visual_a11y_required:
        (
            visual_a11y_evidence_clear,
            visual_a11y_evidence_message,
            visual_a11y_evidence_summary,
        ) = _evaluate_visual_a11y_evidence_artifact(
            visual_a11y_evidence_artifact,
            prerequisites_clear=gate_present
            and visual_a11y_present
            and generation_present
            and contract_clear,
        )

    checks = [
        GateCheck(
            name="gate_policy_artifacts_present",
            passed=gate_present,
            message=gate_message,
        ),
        GateCheck(
            name="generation_governance_artifacts_present",
            passed=generation_present,
            message=generation_message,
        ),
    ]
    if visual_a11y_required:
        checks.append(
            GateCheck(
                name="visual_a11y_policy_artifacts_present",
                passed=visual_a11y_present,
                message=visual_a11y_message,
            )
        )
        checks.append(
            GateCheck(
                name="visual_a11y_evidence_clear",
                passed=visual_a11y_evidence_clear,
                message=visual_a11y_evidence_message,
            )
        )
    checks.append(
        GateCheck(
            name="frontend_contract_prerequisite_clear",
            passed=contract_clear,
            message=""
            if contract_clear
            else _contract_prerequisite_message(contract_report),
        ),
    )
    gate_result = GateResult(
        stage="frontend_gate",
        verdict=GateVerdict.PASS if all(check.passed for check in checks) else GateVerdict.RETRY,
        checks=checks,
    )

    blockers: list[str] = []
    coverage_gaps: list[str] = []

    if not gate_present:
        blockers.append(
            "BLOCKER: frontend gate policy artifacts unavailable: "
            f"{gate_message}"
        )
        coverage_gaps.append("frontend_gate_policy_artifacts")

    if visual_a11y_required and not visual_a11y_present:
        blockers.append(
            "BLOCKER: frontend visual / a11y policy artifacts unavailable: "
            f"{visual_a11y_message}"
        )
        coverage_gaps.append(FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT)

    if not generation_present:
        blockers.append(
            "BLOCKER: frontend generation governance artifacts unavailable: "
            f"{generation_message}"
        )
        coverage_gaps.append("frontend_generation_governance_artifacts")

    if not contract_clear:
        blockers.append(
            "BLOCKER: frontend gate prerequisite failed: "
            "frontend contract verification not clear: "
            f"{_contract_prerequisite_message(contract_report)}"
        )
        coverage_gaps.extend(_contract_coverage_gaps(contract_report))

    if visual_a11y_required and not visual_a11y_evidence_clear:
        blockers.append(
            "BLOCKER: frontend visual / a11y evidence unavailable: "
            f"{visual_a11y_evidence_message}"
        )
        if visual_a11y_evidence_summary is not None:
            coverage_gaps.extend(
                _coverage_gaps_from_visual_a11y_evidence_summary(
                    visual_a11y_evidence_summary
                )
            )

    return FrontendGateVerificationReport(
        gate_policy_root=str(gate_root),
        generation_root=str(generation_root),
        source_name=FRONTEND_GATE_SOURCE_NAME,
        check_objects=(
            *FRONTEND_GATE_CHECK_OBJECTS,
            *(
                (
                    FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT,
                    FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT,
                )
                if visual_a11y_required
                else ()
            ),
        ),
        blockers=tuple(_unique_strings(blockers)),
        coverage_gaps=tuple(_unique_strings(coverage_gaps)),
        advisory_checks=(),
        gate_result=gate_result,
        upstream_contract_verification=contract_report.to_json_dict(),
        visual_a11y_evidence_summary=visual_a11y_evidence_summary,
    )


def build_frontend_gate_execute_decision(
    *,
    attachment_status: str,
    gate_report: FrontendGateVerificationReport | None,
    attachment_blockers: tuple[str, ...] | list[str] = (),
    attachment_coverage_gaps: tuple[str, ...] | list[str] = (),
    frontend_evidence_class: str = "",
) -> FrontendGateExecuteDecision:
    """Project frontend gate verification into an execute-time decision."""

    blockers = tuple(_unique_strings([*attachment_blockers]))
    coverage_gaps = tuple(_unique_strings([*attachment_coverage_gaps]))
    source_linkage_refs = {"runtime_attachment_status": attachment_status}
    if frontend_evidence_class:
        source_linkage_refs["frontend_evidence_class"] = frontend_evidence_class

    if attachment_status != "attached":
        if _framework_capability_observation_gap_can_be_waived(
            attachment_status=attachment_status,
            blockers=blockers,
            coverage_gaps=coverage_gaps,
            frontend_evidence_class=frontend_evidence_class,
        ):
            return FrontendGateExecuteDecision(
                execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_READY,
                decision_reason=FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY,
                source_linkage_refs={
                    **source_linkage_refs,
                    "frontend_attachment_requirement": (
                        FRONTEND_ATTACHMENT_REQUIREMENT_WAIVED
                    ),
                },
            )
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_SCOPE_OR_LINKAGE_INVALID,
            blockers=blockers,
            remediation_hints=blockers,
            remediation_reason_codes=coverage_gaps,
            source_linkage_refs=source_linkage_refs,
        )

    if gate_report is None:
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
            blockers=blockers,
            remediation_hints=blockers,
            remediation_reason_codes=coverage_gaps,
            source_linkage_refs=source_linkage_refs,
        )

    source_linkage_refs = {
        **source_linkage_refs,
        "frontend_gate_verdict": gate_report.gate_result.verdict.value,
    }
    blockers = tuple(_unique_strings([*blockers, *gate_report.blockers]))
    coverage_gaps = tuple(_unique_strings([*coverage_gaps, *gate_report.coverage_gaps]))
    visual_a11y_status = _visual_a11y_summary_status(gate_report)

    if gate_report.gate_result.verdict == GateVerdict.PASS:
        if blockers or coverage_gaps:
            return FrontendGateExecuteDecision(
                execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
                decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
                blockers=blockers,
                remediation_hints=blockers,
                remediation_reason_codes=coverage_gaps,
                source_linkage_refs=source_linkage_refs,
            )
        decision_reason = (
            FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY
            if gate_report.advisory_checks
            else FRONTEND_GATE_DECISION_REASON_ALL_CHECKS_PASSED
        )
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_READY,
            decision_reason=decision_reason,
            source_linkage_refs=source_linkage_refs,
        )

    if _has_visual_a11y_issue(gate_report):
        remediation_reason_codes = coverage_gaps or (
            "frontend_visual_a11y_issue_review",
        )
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
            decision_reason=FRONTEND_GATE_DECISION_REASON_ACTUAL_QUALITY_BLOCKER,
            blockers=blockers,
            remediation_hints=blockers,
            remediation_reason_codes=remediation_reason_codes,
            source_linkage_refs=source_linkage_refs,
        )

    recheck_reason_codes = {
        "frontend_visual_a11y_evidence_input",
        "frontend_visual_a11y_evidence_stable_empty",
    }
    has_non_recheck_gap = any(code not in recheck_reason_codes for code in coverage_gaps)
    if (
        not has_non_recheck_gap
        and (
            visual_a11y_status in {"missing_input", "stable_empty"}
            or any(code in recheck_reason_codes for code in coverage_gaps)
        )
    ):
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_EVIDENCE_MISSING,
            blockers=blockers,
            recheck_required=True,
            recheck_reason_codes=coverage_gaps,
            remediation_hints=blockers,
            remediation_reason_codes=coverage_gaps,
            source_linkage_refs=source_linkage_refs,
        )

    if blockers or coverage_gaps:
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
            blockers=blockers,
            remediation_hints=blockers,
            remediation_reason_codes=coverage_gaps,
            source_linkage_refs=source_linkage_refs,
        )

    return FrontendGateExecuteDecision(
        execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
        decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
        blockers=blockers,
        remediation_hints=blockers,
        remediation_reason_codes=coverage_gaps,
        source_linkage_refs=source_linkage_refs,
    )


def build_frontend_browser_gate_execute_decision(
    *,
    execution_context: BrowserQualityGateExecutionContext,
    bundle: BrowserQualityBundleMaterializationInput,
    artifact_path: str,
    probe_runtime_state: str = "",
    apply_artifact_path: str = "",
) -> FrontendGateExecuteDecision:
    """Project a materialized browser gate bundle into execute-time decision truth."""

    source_linkage_refs = {
        "frontend_execute_gate_source": "frontend_browser_gate_artifact",
        "frontend_browser_gate_artifact_path": artifact_path,
        "frontend_browser_gate_gate_run_id": bundle.gate_run_id,
        "frontend_browser_gate_apply_result_id": bundle.apply_result_id,
        "frontend_browser_gate_overall_status": bundle.overall_gate_status,
    }
    if probe_runtime_state:
        source_linkage_refs["frontend_browser_gate_probe_runtime_state"] = (
            probe_runtime_state
        )

    reason_codes = tuple(
        _unique_strings(
            [
                *bundle.blocking_reason_codes,
                *(
                    code
                    for receipt in bundle.check_receipts
                    for code in receipt.blocking_reason_codes
                ),
            ]
        )
    )
    remediation_hints = tuple(
        _unique_strings(
            hint
            for receipt in bundle.check_receipts
            for hint in receipt.remediation_hints
        )
    )
    blockers = tuple(_browser_gate_blockers(bundle.check_receipts, remediation_hints))

    if _browser_gate_scope_or_linkage_invalid(execution_context, bundle):
        diagnostics = blockers or (
            "browser gate artifact scope or linkage is inconsistent with execution context",
        )
        diagnostic_codes = reason_codes or ("browser_gate_scope_linkage_invalid",)
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_SCOPE_OR_LINKAGE_INVALID,
            blockers=diagnostics,
            remediation_hints=diagnostics,
            remediation_reason_codes=diagnostic_codes,
            source_linkage_refs=source_linkage_refs,
        )

    if not _browser_gate_receipts_match_required_probe_set(
        execution_context.required_probe_set,
        bundle.check_receipts,
    ):
        diagnostics = blockers or (
            "browser gate bundle is missing required probe receipts or contains unexpected checks",
        )
        diagnostic_codes = reason_codes or ("browser_gate_required_probe_receipts_incomplete",)
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
            blockers=diagnostics,
            remediation_hints=diagnostics,
            remediation_reason_codes=diagnostic_codes,
            source_linkage_refs=source_linkage_refs,
        )

    if apply_artifact_path and bundle.source_artifact_ref != apply_artifact_path:
        diagnostics = blockers or (
            "browser gate bundle source artifact does not match the canonical apply artifact linkage",
        )
        diagnostic_codes = reason_codes or ("browser_gate_apply_artifact_linkage_invalid",)
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_SCOPE_OR_LINKAGE_INVALID,
            blockers=diagnostics,
            remediation_hints=diagnostics,
            remediation_reason_codes=diagnostic_codes,
            source_linkage_refs=source_linkage_refs,
        )

    expected_status = _expected_browser_gate_status(bundle.check_receipts)
    if bundle.overall_gate_status != expected_status:
        diagnostics = blockers or (
            "browser gate bundle overall status does not match per-check receipts",
        )
        diagnostic_codes = reason_codes or ("browser_gate_result_inconsistency",)
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
            decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
            blockers=diagnostics,
            remediation_hints=diagnostics,
            remediation_reason_codes=diagnostic_codes,
            source_linkage_refs=source_linkage_refs,
        )

    if bundle.overall_gate_status == "passed":
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_READY,
            decision_reason=FRONTEND_GATE_DECISION_REASON_ALL_CHECKS_PASSED,
            source_linkage_refs=source_linkage_refs,
        )

    if bundle.overall_gate_status == "passed_with_advisories":
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_READY,
            decision_reason=FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY,
            remediation_hints=remediation_hints,
            source_linkage_refs=source_linkage_refs,
        )

    if bundle.overall_gate_status == "incomplete":
        decision_reason = (
            FRONTEND_GATE_DECISION_REASON_TRANSIENT_RUN_FAILURE
            if any(
                receipt.classification_candidate == "transient_run_failure"
                for receipt in bundle.check_receipts
            )
            and not any(
                receipt.classification_candidate == "evidence_missing"
                for receipt in bundle.check_receipts
            )
            else FRONTEND_GATE_DECISION_REASON_EVIDENCE_MISSING
        )
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED,
            decision_reason=decision_reason,
            blockers=blockers,
            recheck_required=True,
            recheck_reason_codes=reason_codes,
            remediation_hints=remediation_hints,
            remediation_reason_codes=reason_codes,
            source_linkage_refs=source_linkage_refs,
        )

    if bundle.overall_gate_status == "blocked":
        return FrontendGateExecuteDecision(
            execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION,
            decision_reason=FRONTEND_GATE_DECISION_REASON_ACTUAL_QUALITY_BLOCKER,
            blockers=blockers,
            remediation_hints=remediation_hints or blockers,
            remediation_reason_codes=reason_codes,
            source_linkage_refs=source_linkage_refs,
        )

    diagnostics = blockers or ("browser gate bundle overall status is unsupported",)
    diagnostic_codes = reason_codes or ("browser_gate_result_inconsistency",)
    return FrontendGateExecuteDecision(
        execute_gate_state=FRONTEND_GATE_EXECUTE_STATE_BLOCKED,
        decision_reason=FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY,
        blockers=diagnostics,
        remediation_hints=diagnostics,
        remediation_reason_codes=diagnostic_codes,
        source_linkage_refs=source_linkage_refs,
    )


def _framework_capability_observation_gap_can_be_waived(
    *,
    attachment_status: str,
    blockers: tuple[str, ...],
    coverage_gaps: tuple[str, ...],
    frontend_evidence_class: str,
) -> bool:
    if frontend_evidence_class != FRONTEND_EVIDENCE_CLASS_FRAMEWORK_CAPABILITY:
        return False
    if attachment_status != "missing_artifact":
        return False
    if set(coverage_gaps) != {FRONTEND_OBSERVATION_ATTACHMENT_COVERAGE_GAP}:
        return False
    return all("missing canonical observation artifact" in blocker for blocker in blockers)


def build_frontend_gate_verification_context(
    root: Path,
    observations: list[PageImplementationObservation],
    *,
    observation_artifact_status: str = (
        FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED
    ),
    observation_artifact_path: Path | None = None,
    observation_artifact_error: str | None = None,
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None = None,
) -> dict[str, object]:
    """Build a verification-compatible context fragment for frontend gate summary."""

    report = build_frontend_gate_verification_report(
        root,
        observations,
        observation_artifact_status=observation_artifact_status,
        observation_artifact_path=observation_artifact_path,
        observation_artifact_error=observation_artifact_error,
        visual_a11y_evidence_artifact=visual_a11y_evidence_artifact,
    )
    return {
        "verification_sources": (report.source_name,),
        "verification_check_objects": report.check_objects,
        "constraint_blockers": report.blockers,
        "coverage_gaps": report.coverage_gaps,
        "frontend_gate_verification": report.to_json_dict(),
    }


def _required_artifacts_present(
    base_dir: Path,
    required_files: tuple[str, ...],
) -> tuple[bool, str]:
    if not base_dir.is_dir():
        return False, f"{base_dir} not found"

    missing = [
        name for name in required_files if not (base_dir / name).is_file()
    ]
    if missing:
        return False, "missing required artifacts: " + ", ".join(missing[:3])
    return True, ""


def _requires_visual_a11y_policy_artifacts(gate_root: Path) -> bool:
    manifest_path = gate_root / "gate.manifest.yaml"
    if not manifest_path.is_file():
        return False

    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return False

    work_item_id = str(raw.get("work_item_id", "")).strip()
    return work_item_id == "071" or work_item_id.startswith("071-")


def _contract_prerequisite_message(
    report: FrontendContractVerificationReport,
) -> str:
    if report.blockers:
        return report.blockers[0]
    if report.coverage_gaps:
        return "coverage gaps: " + ", ".join(report.coverage_gaps)
    return "frontend contract verification not clear"


def _contract_coverage_gaps(
    report: FrontendContractVerificationReport,
) -> tuple[str, ...]:
    projection = report.diagnostic.policy_projection
    report_family_member = projection.report_family_member
    gaps = [gap for gap in report.coverage_gaps if gap != report_family_member]
    if projection.coverage_effect == "gap":
        gaps.append(report_family_member)
    return tuple(_unique_strings(gaps))


def _browser_gate_scope_or_linkage_invalid(
    execution_context: BrowserQualityGateExecutionContext,
    bundle: BrowserQualityBundleMaterializationInput,
) -> bool:
    return any(
        (
            not bundle.gate_run_id,
            not bundle.apply_result_id,
            not bundle.spec_dir,
            not bundle.attachment_scope_ref,
            not bundle.managed_frontend_target,
            not bundle.readiness_subject_id,
            not bundle.source_artifact_ref,
            execution_context.solution_snapshot_id != bundle.solution_snapshot_id,
            execution_context.gate_run_id != bundle.gate_run_id,
            execution_context.apply_result_id != bundle.apply_result_id,
            execution_context.spec_dir != bundle.spec_dir,
            execution_context.attachment_scope_ref != bundle.attachment_scope_ref,
            execution_context.managed_frontend_target
            != bundle.managed_frontend_target,
            execution_context.readiness_subject_id != bundle.readiness_subject_id,
        )
    )


def _browser_gate_receipts_match_required_probe_set(
    required_probe_set: list[str],
    receipts: list[BrowserProbeExecutionReceipt],
) -> bool:
    required = {str(name).strip() for name in required_probe_set if str(name).strip()}
    present = {
        str(receipt.check_name).strip()
        for receipt in receipts
        if str(receipt.check_name).strip()
    }
    return bool(required) and present == required


def _expected_browser_gate_status(
    receipts: list[BrowserProbeExecutionReceipt],
) -> str:
    verdicts = {receipt.classification_candidate for receipt in receipts}
    if {"evidence_missing", "transient_run_failure"} & verdicts:
        return "incomplete"
    if "actual_quality_blocker" in verdicts:
        return "blocked"
    if "advisory_only" in verdicts:
        return "passed_with_advisories"
    return "passed"


def _browser_gate_blockers(
    receipts: list[BrowserProbeExecutionReceipt],
    remediation_hints: tuple[str, ...],
) -> list[str]:
    blockers: list[str] = []
    for receipt in receipts:
        if receipt.classification_candidate in {
            "pass",
            "advisory_only",
        }:
            continue
        hint = (
            receipt.remediation_hints[0]
            if receipt.remediation_hints
            else (
                receipt.blocking_reason_codes[0]
                if receipt.blocking_reason_codes
                else "review browser gate receipt"
            )
        )
        blockers.append(
            f"browser gate check {receipt.check_name}: {hint}"
        )
    if not blockers and remediation_hints:
        blockers.extend(remediation_hints)
    return _unique_strings(blockers)


def _evaluate_visual_a11y_evidence_artifact(
    artifact: FrontendVisualA11yEvidenceArtifact | None,
    *,
    prerequisites_clear: bool,
) -> tuple[bool, str, dict[str, object] | None]:
    if artifact is None:
        summary = {
            "status": "missing_input",
            "coverage_gaps": ["frontend_visual_a11y_evidence_input"],
            "evaluation_count": 0,
            "issue_count": 0,
            "pass_count": 0,
        }
        if prerequisites_clear:
            return False, "missing explicit evidence input", summary
        return True, "", summary

    issue_count = sum(
        1 for evaluation in artifact.evaluations if evaluation.outcome == "issue"
    )
    pass_count = sum(
        1 for evaluation in artifact.evaluations if evaluation.outcome == "pass"
    )
    summary = {
        "status": "clear",
        "coverage_gaps": [],
        "evaluation_count": len(artifact.evaluations),
        "issue_count": issue_count,
        "pass_count": pass_count,
        "provider_kind": artifact.provenance.provider_kind,
        "provider_name": artifact.provenance.provider_name,
        "generated_at": artifact.freshness.generated_at,
    }

    if not artifact.evaluations:
        summary["status"] = "stable_empty"
        summary["coverage_gaps"] = ["frontend_visual_a11y_evidence_stable_empty"]
        if prerequisites_clear:
            return False, "stable empty evidence", summary
        return True, "", summary

    if issue_count:
        summary["status"] = "issue"
        summary["coverage_gaps"] = ["frontend_visual_a11y_issue_review"]
        if prerequisites_clear:
            return False, "visual / a11y issues detected", summary
        return True, "", summary

    summary["status"] = "pass"
    return True, "", summary


def _coverage_gaps_from_visual_a11y_evidence_summary(
    summary: dict[str, object],
) -> tuple[str, ...]:
    raw = summary.get("coverage_gaps")
    if not isinstance(raw, list):
        return ()
    gaps: list[str] = []
    for item in raw:
        text = str(item).strip()
        if text and text not in gaps:
            gaps.append(text)
    return tuple(gaps)


def _visual_a11y_summary_status(
    report: FrontendGateVerificationReport,
) -> str:
    summary = report.visual_a11y_evidence_summary
    if not isinstance(summary, dict):
        return ""
    return str(summary.get("status", "")).strip()


def _has_visual_a11y_issue(
    report: FrontendGateVerificationReport,
) -> bool:
    if "frontend_visual_a11y_issue_review" in report.coverage_gaps:
        return True
    return _visual_a11y_summary_status(report) == "issue"


def _unique_strings(values: list[str] | tuple[str, ...]) -> list[str]:
    unique: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in unique:
            unique.append(text)
    return unique


__all__ = [
    "FRONTEND_GATE_CHECK_OBJECTS",
    "FRONTEND_GATE_DECISION_REASON_ACTUAL_QUALITY_BLOCKER",
    "FRONTEND_GATE_DECISION_REASON_ADVISORY_ONLY",
    "FRONTEND_GATE_DECISION_REASON_ALL_CHECKS_PASSED",
    "FRONTEND_GATE_DECISION_REASON_EVIDENCE_MISSING",
    "FRONTEND_GATE_DECISION_REASON_RESULT_INCONSISTENCY",
    "FRONTEND_GATE_DECISION_REASON_SCOPE_OR_LINKAGE_INVALID",
    "FRONTEND_GATE_EXECUTE_STATE_BLOCKED",
    "FRONTEND_GATE_EXECUTE_STATE_NEEDS_REMEDIATION",
    "FRONTEND_GATE_EXECUTE_STATE_READY",
    "FRONTEND_GATE_EXECUTE_STATE_RECHECK_REQUIRED",
    "FRONTEND_GATE_SOURCE_NAME",
    "FRONTEND_GATE_VISUAL_A11Y_CHECK_OBJECT",
    "FRONTEND_GATE_VISUAL_A11Y_EVIDENCE_OBJECT",
    "FrontendGateExecuteDecision",
    "FrontendGateVerificationReport",
    "build_frontend_gate_execute_decision",
    "build_frontend_gate_verification_context",
    "build_frontend_gate_verification_report",
]
