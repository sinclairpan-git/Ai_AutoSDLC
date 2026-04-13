"""Frontend browser gate runtime materialization helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceArtifact,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserGateProbeRuntimeSession,
    BrowserProbeArtifactRecord,
    BrowserProbeExecutionReceipt,
    BrowserQualityBundleMaterializationInput,
    BrowserQualityGateExecutionContext,
)
from ai_sdlc.models.frontend_solution_confirmation import FrontendSolutionSnapshot

BROWSER_GATE_REQUIRED_PROBE_SET = (
    "playwright_smoke",
    "visual_expectation",
    "basic_a11y",
    "interaction_anti_pattern_checks",
)


def build_browser_quality_gate_execution_context(
    *,
    apply_payload: dict[str, object],
    solution_snapshot: FrontendSolutionSnapshot,
    gate_run_id: str,
) -> BrowserQualityGateExecutionContext:
    """Build the frozen execution context from apply truth and solution truth."""

    result_status = str(apply_payload.get("result_status", "")).strip()
    if result_status != "apply_succeeded_pending_browser_gate":
        raise ValueError("apply_result_not_browser_gate_eligible")
    if not bool(apply_payload.get("browser_gate_required", False)):
        raise ValueError("browser_gate_not_required")

    execution_view = apply_payload.get("execution_view")
    if not isinstance(execution_view, dict):
        raise ValueError("execution_view_missing_from_apply_artifact")

    spec_dir = str(execution_view.get("spec_dir", "")).strip()
    attachment_scope_ref = str(execution_view.get("attachment_scope_ref", "")).strip()
    readiness_subject_id = str(execution_view.get("readiness_subject_id", "")).strip()
    managed_frontend_target = (
        str(execution_view.get("managed_target_path", "")).strip()
        or str(execution_view.get("managed_target_ref", "")).strip()
    )
    apply_result_id = str(apply_payload.get("apply_result_id", "")).strip()
    if not (
        spec_dir
        and attachment_scope_ref
        and readiness_subject_id
        and managed_frontend_target
        and apply_result_id
    ):
        raise ValueError("browser_gate_scope_linkage_incomplete")

    browser_entry_ref = managed_frontend_target
    return BrowserQualityGateExecutionContext(
        gate_run_id=gate_run_id,
        apply_result_id=apply_result_id,
        solution_snapshot_id=solution_snapshot.snapshot_id,
        spec_dir=spec_dir,
        attachment_scope_ref=attachment_scope_ref,
        managed_frontend_target=managed_frontend_target,
        readiness_subject_id=readiness_subject_id,
        effective_provider=solution_snapshot.effective_provider_id,
        effective_style_pack=solution_snapshot.effective_style_pack_id,
        style_fidelity_status=solution_snapshot.style_fidelity_status,
        required_probe_set=list(BROWSER_GATE_REQUIRED_PROBE_SET),
        browser_entry_ref=browser_entry_ref,
        source_linkage_refs={
            "apply_result_status": result_status,
            "solution_snapshot_id": solution_snapshot.snapshot_id,
        },
    )


def materialize_browser_gate_probe_runtime(
    *,
    root: Path,
    context: BrowserQualityGateExecutionContext,
    apply_artifact_path: str,
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None,
    generated_at: str,
    write_artifacts: bool = True,
) -> tuple[
    BrowserGateProbeRuntimeSession,
    list[BrowserProbeArtifactRecord],
    list[BrowserProbeExecutionReceipt],
    BrowserQualityBundleMaterializationInput,
]:
    """Materialize one gate-run scoped runtime session and bundle input."""

    artifact_root_rel = (
        f".ai-sdlc/artifacts/frontend-browser-gate/{context.gate_run_id}"
    )
    artifact_root = root / artifact_root_rel
    if write_artifacts:
        artifact_root.mkdir(parents=True, exist_ok=True)

    artifact_records: list[BrowserProbeArtifactRecord] = []
    receipts: list[BrowserProbeExecutionReceipt] = []

    smoke_records = _materialize_missing_probe_artifacts(
        root=root,
        artifact_root=artifact_root,
        gate_run_id=context.gate_run_id,
        check_name="playwright_smoke",
        artifact_specs=(
            ("playwright_trace", "shared-runtime/playwright-trace.yaml"),
            ("navigation_screenshot", "shared-runtime/navigation-screenshot.yaml"),
        ),
        generated_at=generated_at,
        reason="playwright_probe_not_materialized_in_runtime_baseline",
        write_artifacts=write_artifacts,
    )
    artifact_records.extend(smoke_records)
    receipts.append(
        BrowserProbeExecutionReceipt(
            check_name="playwright_smoke",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="incomplete",
            artifact_ids=[record.artifact_id for record in smoke_records],
            classification_candidate="evidence_missing",
            recheck_required=True,
            remediation_hints=["materialize shared Playwright runtime evidence"],
            blocking_reason_codes=["playwright_probe_evidence_missing"],
            requirement_linkage=["browser_quality_gate:playwright_smoke"],
        )
    )

    visual_records, visual_receipt, a11y_receipt = _materialize_visual_and_a11y_receipts(
        root=root,
        artifact_root=artifact_root,
        gate_run_id=context.gate_run_id,
        visual_a11y_evidence_artifact=visual_a11y_evidence_artifact,
        generated_at=generated_at,
        write_artifacts=write_artifacts,
    )
    artifact_records.extend(visual_records)
    receipts.extend([visual_receipt, a11y_receipt])

    interaction_records = _materialize_missing_probe_artifacts(
        root=root,
        artifact_root=artifact_root,
        gate_run_id=context.gate_run_id,
        check_name="interaction_anti_pattern_checks",
        artifact_specs=(
            ("interaction_snapshot", "interaction/anti-pattern-snapshot.yaml"),
        ),
        generated_at=generated_at,
        reason="interaction_probe_not_materialized_in_runtime_baseline",
        write_artifacts=write_artifacts,
    )
    artifact_records.extend(interaction_records)
    receipts.append(
        BrowserProbeExecutionReceipt(
            check_name="interaction_anti_pattern_checks",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="incomplete",
            artifact_ids=[record.artifact_id for record in interaction_records],
            classification_candidate="evidence_missing",
            recheck_required=True,
            remediation_hints=["materialize interaction anti-pattern probe evidence"],
            blocking_reason_codes=["interaction_probe_evidence_missing"],
            requirement_linkage=["browser_quality_gate:interaction_anti_pattern_checks"],
        )
    )

    overall_gate_status = _overall_gate_status(receipts)
    session_status = "completed" if overall_gate_status in {"passed", "passed_with_advisories"} else "incomplete"
    session = BrowserGateProbeRuntimeSession(
        probe_runtime_session_id=f"{context.gate_run_id}-session",
        gate_run_id=context.gate_run_id,
        apply_result_id=context.apply_result_id,
        solution_snapshot_id=context.solution_snapshot_id,
        spec_dir=context.spec_dir,
        attachment_scope_ref=context.attachment_scope_ref,
        managed_frontend_target=context.managed_frontend_target,
        readiness_subject_id=context.readiness_subject_id,
        browser_entry_ref=context.browser_entry_ref,
        artifact_root_ref=artifact_root_rel,
        status=session_status,
        started_at=generated_at,
        updated_at=generated_at,
        finished_at=generated_at,
        source_linkage_refs={
            **context.source_linkage_refs,
            "apply_artifact_path": apply_artifact_path,
        },
    )

    bundle = BrowserQualityBundleMaterializationInput(
        bundle_id=f"{context.gate_run_id}-bundle",
        gate_run_id=context.gate_run_id,
        apply_result_id=context.apply_result_id,
        solution_snapshot_id=context.solution_snapshot_id,
        spec_dir=context.spec_dir,
        attachment_scope_ref=context.attachment_scope_ref,
        managed_frontend_target=context.managed_frontend_target,
        source_artifact_ref=apply_artifact_path,
        readiness_subject_id=context.readiness_subject_id,
        playwright_trace_refs=[
            record.artifact_ref
            for record in artifact_records
            if record.artifact_type == "playwright_trace"
        ],
        screenshot_refs=[
            record.artifact_ref
            for record in artifact_records
            if record.artifact_type.endswith("screenshot")
        ],
        check_receipts=receipts,
        smoke_verdict=_receipt_verdict(receipts, "playwright_smoke"),
        visual_verdict=_receipt_verdict(receipts, "visual_expectation"),
        a11y_verdict=_receipt_verdict(receipts, "basic_a11y"),
        interaction_anti_pattern_verdict=_receipt_verdict(
            receipts,
            "interaction_anti_pattern_checks",
        ),
        overall_gate_status=overall_gate_status,
        requirement_linkage=_unique_strings(
            requirement
            for receipt in receipts
            for requirement in receipt.requirement_linkage
        ),
        blocking_reason_codes=_unique_strings(
            code
            for receipt in receipts
            for code in receipt.blocking_reason_codes
        ),
        advisory_reason_codes=_unique_strings(
            code
            for receipt in receipts
            for code in receipt.advisory_reason_codes
        ),
        generated_at=generated_at,
        source_linkage_refs={
            **context.source_linkage_refs,
            "probe_runtime_session_id": session.probe_runtime_session_id,
            "artifact_root_ref": artifact_root_rel,
        },
    )
    return session, artifact_records, receipts, bundle


def _materialize_missing_probe_artifacts(
    *,
    root: Path,
    artifact_root: Path,
    gate_run_id: str,
    check_name: str,
    artifact_specs: tuple[tuple[str, str], ...],
    generated_at: str,
    reason: str,
    write_artifacts: bool,
) -> list[BrowserProbeArtifactRecord]:
    records: list[BrowserProbeArtifactRecord] = []
    for index, (artifact_type, relative_artifact_path) in enumerate(artifact_specs, start=1):
        artifact_path = artifact_root / relative_artifact_path
        if write_artifacts:
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                yaml.safe_dump(
                    {
                        "gate_run_id": gate_run_id,
                        "check_name": check_name,
                        "artifact_type": artifact_type,
                        "capture_status": "missing",
                        "reason": reason,
                        "generated_at": generated_at,
                    },
                    sort_keys=False,
                    allow_unicode=True,
                ),
                encoding="utf-8",
            )
        relative_ref = str(artifact_path.relative_to(root))
        records.append(
            BrowserProbeArtifactRecord(
                artifact_id=f"{gate_run_id}-{check_name}-{index}",
                gate_run_id=gate_run_id,
                check_name=check_name,
                artifact_type=artifact_type,
                artifact_ref=relative_ref,
                capture_status="missing",
                captured_at=generated_at,
                source_linkage_refs={"artifact_reason": reason},
            )
        )
    return records


def _materialize_visual_and_a11y_receipts(
    *,
    root: Path,
    artifact_root: Path,
    gate_run_id: str,
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None,
    generated_at: str,
    write_artifacts: bool,
) -> tuple[list[BrowserProbeArtifactRecord], BrowserProbeExecutionReceipt, BrowserProbeExecutionReceipt]:
    if visual_a11y_evidence_artifact is None:
        records = _materialize_missing_probe_artifacts(
            root=root,
            artifact_root=artifact_root,
            gate_run_id=gate_run_id,
            check_name="visual_expectation",
            artifact_specs=(("checkpoint_screenshot", "visual/expectation-missing.yaml"),),
            generated_at=generated_at,
            reason="visual_a11y_evidence_missing",
            write_artifacts=write_artifacts,
        )
        a11y_records = _materialize_missing_probe_artifacts(
            root=root,
            artifact_root=artifact_root,
            gate_run_id=gate_run_id,
            check_name="basic_a11y",
            artifact_specs=(("a11y_scan", "a11y/scan-missing.yaml"),),
            generated_at=generated_at,
            reason="visual_a11y_evidence_missing",
            write_artifacts=write_artifacts,
        )
        all_records = [*records, *a11y_records]
        return (
            all_records,
            BrowserProbeExecutionReceipt(
                check_name="visual_expectation",
                started_at=generated_at,
                finished_at=generated_at,
                runtime_status="incomplete",
                artifact_ids=[records[0].artifact_id],
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=["materialize frontend visual / a11y evidence input"],
                blocking_reason_codes=["visual_expectation_evidence_missing"],
                requirement_linkage=["browser_quality_gate:visual_expectation"],
            ),
            BrowserProbeExecutionReceipt(
                check_name="basic_a11y",
                started_at=generated_at,
                finished_at=generated_at,
                runtime_status="incomplete",
                artifact_ids=[a11y_records[0].artifact_id],
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=["materialize frontend visual / a11y evidence input"],
                blocking_reason_codes=["basic_a11y_evidence_missing"],
                requirement_linkage=["browser_quality_gate:basic_a11y"],
            ),
        )

    outcome_set = {evaluation.outcome for evaluation in visual_a11y_evidence_artifact.evaluations}
    classification = "pass"
    runtime_status = "completed"
    blocking_reason_codes: list[str] = []
    remediation_hints: list[str] = []
    if any(outcome.lower() not in {"pass", "info"} for outcome in outcome_set):
        classification = "actual_quality_blocker"
        blocking_reason_codes = ["visual_a11y_quality_blocker"]
        remediation_hints = ["review frontend visual / a11y issue findings"]
    artifact_payload = {
        "gate_run_id": gate_run_id,
        "generated_at": generated_at,
        "evidence_generated_at": visual_a11y_evidence_artifact.freshness.generated_at,
        "evaluation_count": len(visual_a11y_evidence_artifact.evaluations),
        "outcomes": sorted(outcome_set),
    }
    visual_path = artifact_root / "visual" / "expectation-evidence.yaml"
    if write_artifacts:
        visual_path.parent.mkdir(parents=True, exist_ok=True)
        visual_path.write_text(
            yaml.safe_dump(artifact_payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    a11y_path = artifact_root / "a11y" / "scan-evidence.yaml"
    if write_artifacts:
        a11y_path.parent.mkdir(parents=True, exist_ok=True)
        a11y_path.write_text(
            yaml.safe_dump(artifact_payload, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
    visual_record = BrowserProbeArtifactRecord(
        artifact_id=f"{gate_run_id}-visual-1",
        gate_run_id=gate_run_id,
        check_name="visual_expectation",
        artifact_type="checkpoint_screenshot",
        artifact_ref=str(visual_path.relative_to(root)),
        capture_status="captured",
        captured_at=generated_at,
        source_linkage_refs={"evidence_provider": visual_a11y_evidence_artifact.provenance.provider_name},
    )
    a11y_record = BrowserProbeArtifactRecord(
        artifact_id=f"{gate_run_id}-a11y-1",
        gate_run_id=gate_run_id,
        check_name="basic_a11y",
        artifact_type="a11y_scan",
        artifact_ref=str(a11y_path.relative_to(root)),
        capture_status="captured",
        captured_at=generated_at,
        source_linkage_refs={"evidence_provider": visual_a11y_evidence_artifact.provenance.provider_name},
    )
    return (
        [visual_record, a11y_record],
        BrowserProbeExecutionReceipt(
            check_name="visual_expectation",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status=runtime_status,
            artifact_ids=[visual_record.artifact_id],
            classification_candidate=classification,
            recheck_required=False,
            remediation_hints=list(remediation_hints),
            blocking_reason_codes=list(blocking_reason_codes),
            requirement_linkage=["browser_quality_gate:visual_expectation"],
        ),
        BrowserProbeExecutionReceipt(
            check_name="basic_a11y",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status=runtime_status,
            artifact_ids=[a11y_record.artifact_id],
            classification_candidate=classification,
            recheck_required=False,
            remediation_hints=list(remediation_hints),
            blocking_reason_codes=list(blocking_reason_codes),
            requirement_linkage=["browser_quality_gate:basic_a11y"],
        ),
    )


def _overall_gate_status(receipts: list[BrowserProbeExecutionReceipt]) -> str:
    verdicts = {receipt.classification_candidate for receipt in receipts}
    if {"evidence_missing", "transient_run_failure"} & verdicts:
        return "incomplete"
    if "actual_quality_blocker" in verdicts:
        return "blocked"
    if "advisory_only" in verdicts:
        return "passed_with_advisories"
    return "passed"


def _receipt_verdict(receipts: list[BrowserProbeExecutionReceipt], check_name: str) -> str:
    for receipt in receipts:
        if receipt.check_name == check_name:
            return receipt.classification_candidate
    raise ValueError(f"missing receipt for check {check_name}")


def _unique_strings(values) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered
