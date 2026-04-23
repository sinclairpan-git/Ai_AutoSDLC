"""Frontend browser gate runtime materialization helpers."""

from __future__ import annotations

import inspect
import json
import subprocess
from collections.abc import Callable, Iterable
from pathlib import Path

import yaml

from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_KIND,
    FrontendVisualA11yEvidenceArtifact,
    build_auto_frontend_visual_a11y_evidence_artifact,
    load_frontend_visual_a11y_evidence_artifact,
    visual_a11y_evidence_artifact_path,
    write_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserGateInteractionProbeCapture,
    BrowserGateProbeRunnerResult,
    BrowserGateProbeRuntimeSession,
    BrowserGateQualityCapture,
    BrowserGateSharedRuntimeCapture,
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
_PLAYWRIGHT_TRACE_REL_PATH = "shared-runtime/playwright-trace.zip"
_PLAYWRIGHT_SCREENSHOT_REL_PATH = "shared-runtime/navigation-screenshot.png"
_INTERACTION_SNAPSHOT_REL_PATH = "interaction/interaction-snapshot.json"
_DEFAULT_BROWSER_GATE_PROBE_TIMEOUT_SECONDS = 30


BrowserGateProbeRunner = Callable[
    ...,
    BrowserGateProbeRunnerResult,
]


def build_browser_quality_gate_execution_context(
    *,
    apply_payload: dict[str, object],
    solution_snapshot: FrontendSolutionSnapshot,
    gate_run_id: str,
    delivery_entry_id: str = "",
    component_library_packages: list[str] | None = None,
    provider_theme_adapter_id: str = "",
    provider_runtime_adapter_carrier_mode: str = "",
    provider_runtime_adapter_delivery_state: str = "",
    provider_runtime_adapter_evidence_state: str = "",
    page_schema_ids: list[str] | None = None,
    visual_regression_matrix_id: str = "",
    visual_regression_viewport_id: str = "",
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

    browser_entry_ref = _derive_browser_entry_ref(managed_frontend_target)
    required_probe_set = list(BROWSER_GATE_REQUIRED_PROBE_SET)
    if visual_regression_matrix_id.strip() and visual_regression_viewport_id.strip():
        required_probe_set.insert(2, "visual_regression")

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
        delivery_entry_id=delivery_entry_id,
        component_library_packages=_unique_strings(component_library_packages or []),
        provider_theme_adapter_id=provider_theme_adapter_id,
        provider_runtime_adapter_carrier_mode=provider_runtime_adapter_carrier_mode,
        provider_runtime_adapter_delivery_state=provider_runtime_adapter_delivery_state,
        provider_runtime_adapter_evidence_state=provider_runtime_adapter_evidence_state,
        page_schema_ids=_unique_strings(page_schema_ids or []),
        visual_regression_matrix_id=visual_regression_matrix_id,
        visual_regression_viewport_id=visual_regression_viewport_id,
        required_probe_set=_unique_strings(required_probe_set),
        browser_entry_ref=browser_entry_ref,
        source_linkage_refs={
            "apply_result_status": result_status,
            "solution_snapshot_id": solution_snapshot.snapshot_id,
        },
    )


def run_default_browser_gate_probe(
    *,
    root: Path,
    artifact_root: Path,
    execution_context: BrowserQualityGateExecutionContext,
    generated_at: str,
) -> BrowserGateProbeRunnerResult:
    """Run the default Playwright-backed browser gate probe."""

    artifact_root_rel = str(artifact_root.relative_to(root))
    script_path = root / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    if not script_path.is_file():
        return _transient_probe_runner_result(
            gate_run_id=execution_context.gate_run_id,
            artifact_root_rel=artifact_root_rel,
            diagnostic_code="playwright_runner_script_missing",
            warning="Playwright probe runner is not available in this installation.",
        )

    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": artifact_root_rel,
        "browser_entry_ref": execution_context.browser_entry_ref,
        "gate_run_id": execution_context.gate_run_id,
        "generated_at": generated_at,
        "managed_frontend_target": execution_context.managed_frontend_target,
        "delivery_entry_id": execution_context.delivery_entry_id,
        "component_library_packages": _unique_strings(
            execution_context.component_library_packages
        ),
        "provider_theme_adapter_id": execution_context.provider_theme_adapter_id,
        "provider_runtime_adapter_carrier_mode": (
            execution_context.provider_runtime_adapter_carrier_mode
        ),
        "provider_runtime_adapter_delivery_state": (
            execution_context.provider_runtime_adapter_delivery_state
        ),
        "provider_runtime_adapter_evidence_state": (
            execution_context.provider_runtime_adapter_evidence_state
        ),
        "page_schema_ids": _unique_strings(execution_context.page_schema_ids),
        "visual_regression_matrix_id": execution_context.visual_regression_matrix_id,
        "visual_regression_viewport_id": execution_context.visual_regression_viewport_id,
        "effective_provider": execution_context.effective_provider,
        "effective_style_pack": execution_context.effective_style_pack,
    }
    try:
        completed = subprocess.run(
            ["node", str(script_path)],
            cwd=root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            timeout=_DEFAULT_BROWSER_GATE_PROBE_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return _transient_probe_runner_result(
            gate_run_id=execution_context.gate_run_id,
            artifact_root_rel=artifact_root_rel,
            diagnostic_code="playwright_runtime_unavailable",
            warning=(
                "Playwright runtime is not available on this host. Install Playwright and its browsers for this frontend host, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            ),
        )
    except subprocess.TimeoutExpired:
        return _transient_probe_runner_result(
            gate_run_id=execution_context.gate_run_id,
            artifact_root_rel=artifact_root_rel,
            diagnostic_code="browser_probe_timeout",
            warning=(
                "Browser gate probe timed out before completion. Confirm the frontend host is ready, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            ),
        )
    stdout = completed.stdout.strip()
    if not stdout:
        warning = completed.stderr.strip() or "Playwright runtime is not available on this host."
        return _transient_probe_runner_result(
            gate_run_id=execution_context.gate_run_id,
            artifact_root_rel=artifact_root_rel,
            diagnostic_code="playwright_runtime_unavailable",
            warning=warning,
        )
    try:
        raw_payload = json.loads(stdout)
        return BrowserGateProbeRunnerResult.model_validate(raw_payload)
    except Exception as exc:
        warning = completed.stderr.strip() or f"browser gate runner output invalid: {exc}"
        return _transient_probe_runner_result(
            gate_run_id=execution_context.gate_run_id,
            artifact_root_rel=artifact_root_rel,
            diagnostic_code="playwright_runner_output_invalid",
            warning=warning,
        )


def materialize_browser_gate_probe_runtime(
    *,
    root: Path,
    context: BrowserQualityGateExecutionContext,
    apply_artifact_path: str,
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None,
    generated_at: str,
    write_artifacts: bool = True,
    probe_runner: BrowserGateProbeRunner | None = None,
    execute_probe: bool = False,
    auto_visual_a11y_provider: bool = False,
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
    runner_warnings: list[str] = []
    runner_result: BrowserGateProbeRunnerResult | None = None

    if execute_probe:
        (
            smoke_records,
            smoke_receipt,
            interaction_records,
            interaction_receipt,
            runner_warnings,
            runner_result,
        ) = _materialize_real_probe_receipts(
            root=root,
            artifact_root=artifact_root,
            artifact_root_rel=artifact_root_rel,
            context=context,
            generated_at=generated_at,
            probe_runner=probe_runner or run_default_browser_gate_probe,
        )
    else:
        smoke_records = _materialize_missing_probe_artifacts(
            root=root,
            artifact_root=artifact_root,
            gate_run_id=context.gate_run_id,
            check_name="playwright_smoke",
            artifact_specs=(
                ("playwright_trace", _PLAYWRIGHT_TRACE_REL_PATH),
                ("navigation_screenshot", _PLAYWRIGHT_SCREENSHOT_REL_PATH),
            ),
            generated_at=generated_at,
            reason="playwright_probe_not_materialized_in_runtime_baseline",
            write_artifacts=write_artifacts,
        )
        smoke_receipt = BrowserProbeExecutionReceipt(
            check_name="playwright_smoke",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="incomplete",
            artifact_ids=_unique_strings(record.artifact_id for record in smoke_records),
            classification_candidate="evidence_missing",
            recheck_required=True,
            remediation_hints=_unique_strings(
                ["materialize shared Playwright runtime evidence"]
            ),
            blocking_reason_codes=_unique_strings(["playwright_probe_evidence_missing"]),
            requirement_linkage=_unique_strings(["browser_quality_gate:playwright_smoke"]),
        )
        interaction_records = _materialize_missing_probe_artifacts(
            root=root,
            artifact_root=artifact_root,
            gate_run_id=context.gate_run_id,
            check_name="interaction_anti_pattern_checks",
            artifact_specs=(("interaction_snapshot", _INTERACTION_SNAPSHOT_REL_PATH),),
            generated_at=generated_at,
            reason="interaction_probe_not_materialized_in_runtime_baseline",
            write_artifacts=write_artifacts,
        )
        interaction_receipt = BrowserProbeExecutionReceipt(
            check_name="interaction_anti_pattern_checks",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="incomplete",
            artifact_ids=_unique_strings(
                record.artifact_id for record in interaction_records
            ),
            classification_candidate="evidence_missing",
            recheck_required=True,
            remediation_hints=_unique_strings(
                ["materialize interaction anti-pattern probe evidence"]
            ),
            blocking_reason_codes=_unique_strings(
                ["interaction_probe_evidence_missing"]
            ),
            requirement_linkage=_unique_strings(
                ["browser_quality_gate:interaction_anti_pattern_checks"]
            ),
        )

    artifact_records.extend(smoke_records)
    receipts.append(smoke_receipt)

    effective_visual_a11y_evidence_artifact = _resolve_visual_a11y_evidence_artifact(
        root=root,
        context=context,
        generated_at=generated_at,
        visual_a11y_evidence_artifact=visual_a11y_evidence_artifact,
        runner_result=runner_result,
        write_artifacts=write_artifacts,
        auto_visual_a11y_provider=auto_visual_a11y_provider,
    )
    visual_records, visual_receipt, a11y_receipt = _materialize_visual_and_a11y_receipts(
        root=root,
        artifact_root=artifact_root,
        gate_run_id=context.gate_run_id,
        visual_a11y_evidence_artifact=effective_visual_a11y_evidence_artifact,
        generated_at=generated_at,
        write_artifacts=write_artifacts,
    )
    artifact_records.extend(visual_records)
    receipts.extend([visual_receipt, a11y_receipt])
    if "visual_regression" in context.required_probe_set:
        visual_regression_records, visual_regression_receipt = (
            _materialize_visual_regression_receipt(
                root=root,
                artifact_root=artifact_root,
                gate_run_id=context.gate_run_id,
                visual_regression_capture=(
                    runner_result.visual_regression_capture if runner_result is not None else None
                ),
                generated_at=generated_at,
                write_artifacts=write_artifacts,
            )
        )
        artifact_records.extend(visual_regression_records)
        receipts.append(visual_regression_receipt)

    artifact_records.extend(interaction_records)
    receipts.append(interaction_receipt)

    overall_gate_status = _overall_gate_status(receipts)
    session_status = _session_status(
        overall_gate_status,
        receipts=receipts,
    )
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
        warnings=_unique_strings(runner_warnings),
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
        delivery_entry_id=context.delivery_entry_id,
        component_library_packages=_unique_strings(context.component_library_packages),
        provider_theme_adapter_id=context.provider_theme_adapter_id,
        provider_runtime_adapter_carrier_mode=(
            context.provider_runtime_adapter_carrier_mode
        ),
        provider_runtime_adapter_delivery_state=(
            context.provider_runtime_adapter_delivery_state
        ),
        provider_runtime_adapter_evidence_state=(
            context.provider_runtime_adapter_evidence_state
        ),
        page_schema_ids=_unique_strings(context.page_schema_ids),
        playwright_trace_refs=[
            record.artifact_ref
            for record in artifact_records
            if record.artifact_type == "playwright_trace"
            and record.capture_status == "captured"
        ],
        screenshot_refs=[
            record.artifact_ref
            for record in artifact_records
            if record.artifact_type.endswith("screenshot")
            and record.capture_status == "captured"
        ],
        check_receipts=receipts,
        smoke_verdict=_receipt_verdict(receipts, "playwright_smoke"),
        visual_verdict=_resolve_visual_verdict(
            runner_result=runner_result,
            receipts=receipts,
        ),
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


def _materialize_real_probe_receipts(
    *,
    root: Path,
    artifact_root: Path,
    artifact_root_rel: str,
    context: BrowserQualityGateExecutionContext,
    generated_at: str,
    probe_runner: BrowserGateProbeRunner,
) -> tuple[
    list[BrowserProbeArtifactRecord],
    BrowserProbeExecutionReceipt,
    list[BrowserProbeArtifactRecord],
    BrowserProbeExecutionReceipt,
    list[str],
    BrowserGateProbeRunnerResult,
]:
    runner_result = _invoke_probe_runner(
        probe_runner,
        root=root,
        artifact_root=artifact_root,
        execution_context=context,
        generated_at=generated_at,
    )
    smoke_records, smoke_receipt = _materialize_real_smoke_receipt(
        root=root,
        artifact_root=artifact_root,
        artifact_root_rel=artifact_root_rel,
        gate_run_id=context.gate_run_id,
        generated_at=generated_at,
        runner_result=runner_result,
    )
    interaction_records, interaction_receipt = _materialize_real_interaction_receipt(
        root=root,
        artifact_root=artifact_root,
        artifact_root_rel=artifact_root_rel,
        gate_run_id=context.gate_run_id,
        generated_at=generated_at,
        runner_result=runner_result,
    )
    warnings = _unique_strings(
        runner_result.warnings
        or _diagnostic_warning_messages(runner_result.diagnostic_codes)
    )
    return (
        smoke_records,
        smoke_receipt,
        interaction_records,
        interaction_receipt,
        warnings,
        runner_result,
    )


def _resolve_visual_a11y_evidence_artifact(
    *,
    root: Path,
    context: BrowserQualityGateExecutionContext,
    generated_at: str,
    visual_a11y_evidence_artifact: FrontendVisualA11yEvidenceArtifact | None,
    runner_result: BrowserGateProbeRunnerResult | None,
    write_artifacts: bool,
    auto_visual_a11y_provider: bool,
) -> FrontendVisualA11yEvidenceArtifact | None:
    if not auto_visual_a11y_provider or runner_result is None:
        return visual_a11y_evidence_artifact
    quality_capture = runner_result.quality_capture
    if quality_capture is None:
        return visual_a11y_evidence_artifact

    try:
        spec_dir = _resolve_repo_relative_path(root, context.spec_dir)
    except ValueError:
        return None
    evidence_path = visual_a11y_evidence_artifact_path(spec_dir)
    existing_artifact = visual_a11y_evidence_artifact
    if existing_artifact is None and evidence_path.is_file():
        try:
            existing_artifact = load_frontend_visual_a11y_evidence_artifact(evidence_path)
        except ValueError:
            existing_artifact = None

    if (
        existing_artifact is not None
        and existing_artifact.provenance.provider_kind
        != AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_KIND
    ):
        return existing_artifact

    auto_artifact = _build_auto_visual_a11y_evidence_artifact(
        context=context,
        generated_at=generated_at,
        quality_capture=quality_capture,
        runner_result=runner_result,
    )
    if write_artifacts:
        write_frontend_visual_a11y_evidence_artifact(spec_dir, auto_artifact)
    return auto_artifact


def _resolve_repo_relative_path(root: Path, relative_path: str) -> Path:
    raw_path = Path(str(relative_path).strip())
    if raw_path.is_absolute():
        raise ValueError("path_outside_repo_root")
    resolved_root = root.resolve()
    resolved = (resolved_root / raw_path).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("path_outside_repo_root") from exc
    return resolved


def _build_auto_visual_a11y_evidence_artifact(
    *,
    context: BrowserQualityGateExecutionContext,
    generated_at: str,
    quality_capture: BrowserGateQualityCapture,
    runner_result: BrowserGateProbeRunnerResult,
) -> FrontendVisualA11yEvidenceArtifact:
    return build_auto_frontend_visual_a11y_evidence_artifact(
        target_id=context.delivery_entry_id or context.readiness_subject_id,
        surface_id=context.browser_entry_ref or context.managed_frontend_target,
        generated_at=generated_at,
        screenshot_ref=(
            quality_capture.screenshot_ref
            or runner_result.shared_capture.navigation_screenshot_ref
        ),
        final_url=quality_capture.final_url or runner_result.shared_capture.final_url,
        page_title=quality_capture.page_title,
        body_text_char_count=quality_capture.body_text_char_count,
        heading_count=quality_capture.heading_count,
        landmark_count=quality_capture.landmark_count,
        interactive_count=quality_capture.interactive_count,
        unlabeled_button_count=quality_capture.unlabeled_button_count,
        unlabeled_input_count=quality_capture.unlabeled_input_count,
        image_missing_alt_count=quality_capture.image_missing_alt_count,
        viewport_width=quality_capture.viewport_width,
        viewport_height=quality_capture.viewport_height,
        document_scroll_width=quality_capture.document_scroll_width,
        document_scroll_height=quality_capture.document_scroll_height,
        horizontal_overflow_count=quality_capture.horizontal_overflow_count,
        low_contrast_text_count=quality_capture.low_contrast_text_count,
        focusable_count=quality_capture.focusable_count,
        focusable_without_visible_focus_count=(
            quality_capture.focusable_without_visible_focus_count
        ),
        console_error_messages=list(quality_capture.console_error_messages),
        page_error_messages=list(quality_capture.page_error_messages),
    )


def _materialize_real_smoke_receipt(
    *,
    root: Path,
    artifact_root: Path,
    artifact_root_rel: str,
    gate_run_id: str,
    generated_at: str,
    runner_result: BrowserGateProbeRunnerResult,
) -> tuple[list[BrowserProbeArtifactRecord], BrowserProbeExecutionReceipt]:
    capture = runner_result.shared_capture
    diagnostic_codes = _unique_strings(
        [*runner_result.diagnostic_codes, *capture.diagnostic_codes]
    )
    refs = [
        (
            "playwright_trace",
            capture.trace_artifact_ref or f"{artifact_root_rel}/{_PLAYWRIGHT_TRACE_REL_PATH}",
        ),
        (
            "navigation_screenshot",
            capture.navigation_screenshot_ref
            or f"{artifact_root_rel}/{_PLAYWRIGHT_SCREENSHOT_REL_PATH}",
        ),
    ]
    records: list[BrowserProbeArtifactRecord] = []
    missing_artifact = False
    for index, (artifact_type, artifact_ref) in enumerate(refs, start=1):
        normalized_artifact_ref = _normalize_runner_artifact_ref(artifact_ref)
        resolved_status = capture.capture_status
        if resolved_status == "captured" and not _runner_artifact_exists(
            root=root,
            artifact_root=artifact_root,
            artifact_ref=normalized_artifact_ref,
        ):
            resolved_status = "missing"
            missing_artifact = True
        elif resolved_status == "missing":
            missing_artifact = True
        records.append(
            BrowserProbeArtifactRecord(
                artifact_id=f"{gate_run_id}-playwright_smoke-{index}",
                gate_run_id=gate_run_id,
                check_name="playwright_smoke",
                artifact_type=artifact_type,
                artifact_ref=normalized_artifact_ref,
                anchor_refs=_unique_strings(capture.anchor_refs),
                capture_status=resolved_status,
                captured_at=generated_at,
                source_linkage_refs={"artifact_reason": ",".join(diagnostic_codes)},
            )
        )

    if runner_result.runtime_status == "failed_transient" or capture.capture_status == "capture_failed":
        return records, BrowserProbeExecutionReceipt(
            check_name="playwright_smoke",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="failed_transient",
            artifact_ids=_unique_strings(record.artifact_id for record in records),
            anchor_refs=_unique_strings(capture.anchor_refs),
            requirement_linkage=_unique_strings(["browser_quality_gate:playwright_smoke"]),
            classification_candidate="transient_run_failure",
            recheck_required=True,
            remediation_hints=_unique_strings(
                ["re-run the browser gate probe after restoring the Playwright runtime"]
            ),
            blocking_reason_codes=diagnostic_codes or ["playwright_probe_transient_failure"],
        )

    if missing_artifact:
        return records, BrowserProbeExecutionReceipt(
            check_name="playwright_smoke",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="incomplete",
            artifact_ids=_unique_strings(record.artifact_id for record in records),
            anchor_refs=_unique_strings(capture.anchor_refs),
            requirement_linkage=_unique_strings(["browser_quality_gate:playwright_smoke"]),
            classification_candidate="evidence_missing",
            recheck_required=True,
            remediation_hints=_unique_strings(
                ["materialize shared Playwright runtime evidence"]
            ),
            blocking_reason_codes=diagnostic_codes or ["playwright_probe_evidence_missing"],
        )

    return records, BrowserProbeExecutionReceipt(
        check_name="playwright_smoke",
        started_at=generated_at,
        finished_at=generated_at,
        runtime_status="completed",
        artifact_ids=_unique_strings(record.artifact_id for record in records),
        anchor_refs=_unique_strings(capture.anchor_refs),
        requirement_linkage=_unique_strings(["browser_quality_gate:playwright_smoke"]),
        classification_candidate="pass",
    )


def _materialize_real_interaction_receipt(
    *,
    root: Path,
    artifact_root: Path,
    artifact_root_rel: str,
    gate_run_id: str,
    generated_at: str,
    runner_result: BrowserGateProbeRunnerResult,
) -> tuple[list[BrowserProbeArtifactRecord], BrowserProbeExecutionReceipt]:
    capture = runner_result.interaction_capture
    diagnostic_codes = _unique_strings(
        [*runner_result.diagnostic_codes, *capture.blocking_reason_codes]
    )
    artifact_refs = _unique_strings(capture.artifact_refs) or [
        f"{artifact_root_rel}/{_INTERACTION_SNAPSHOT_REL_PATH}"
    ]
    records: list[BrowserProbeArtifactRecord] = []
    missing_artifact = False
    for index, artifact_ref in enumerate(artifact_refs, start=1):
        normalized_artifact_ref = _normalize_runner_artifact_ref(artifact_ref)
        resolved_status = capture.capture_status
        if resolved_status == "captured" and not _runner_artifact_exists(
            root=root,
            artifact_root=artifact_root,
            artifact_ref=normalized_artifact_ref,
        ):
            resolved_status = "missing"
            missing_artifact = True
        elif resolved_status == "missing":
            missing_artifact = True
        records.append(
            BrowserProbeArtifactRecord(
                artifact_id=f"{gate_run_id}-interaction-{index}",
                gate_run_id=gate_run_id,
                check_name="interaction_anti_pattern_checks",
                artifact_type="interaction_snapshot",
                artifact_ref=normalized_artifact_ref,
                anchor_refs=_unique_strings(capture.anchor_refs),
                capture_status=resolved_status,
                captured_at=generated_at,
                source_linkage_refs={"interaction_probe_id": capture.interaction_probe_id},
            )
        )

    if (
        runner_result.runtime_status == "failed_transient"
        or capture.capture_status == "capture_failed"
        or capture.classification_candidate == "transient_run_failure"
    ):
        return records, BrowserProbeExecutionReceipt(
            check_name="interaction_anti_pattern_checks",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="failed_transient",
            artifact_ids=_unique_strings(record.artifact_id for record in records),
            anchor_refs=_unique_strings(capture.anchor_refs),
            requirement_linkage=_unique_strings(
                ["browser_quality_gate:interaction_anti_pattern_checks"]
            ),
            classification_candidate="transient_run_failure",
            recheck_required=True,
            remediation_hints=_unique_strings(
                ["re-run the browser gate probe after restoring the interaction runtime"]
            ),
            blocking_reason_codes=diagnostic_codes or ["interaction_probe_transient_failure"],
        )

    if missing_artifact or capture.classification_candidate == "evidence_missing":
        return records, BrowserProbeExecutionReceipt(
            check_name="interaction_anti_pattern_checks",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="incomplete",
            artifact_ids=_unique_strings(record.artifact_id for record in records),
            anchor_refs=_unique_strings(capture.anchor_refs),
            requirement_linkage=_unique_strings(
                ["browser_quality_gate:interaction_anti_pattern_checks"]
            ),
            classification_candidate="evidence_missing",
            recheck_required=True,
            remediation_hints=_unique_strings(
                ["materialize interaction anti-pattern probe evidence"]
            ),
            blocking_reason_codes=diagnostic_codes or ["interaction_probe_evidence_missing"],
        )

    if capture.classification_candidate == "actual_quality_blocker":
        return records, BrowserProbeExecutionReceipt(
            check_name="interaction_anti_pattern_checks",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status="completed",
            artifact_ids=_unique_strings(record.artifact_id for record in records),
            anchor_refs=_unique_strings(capture.anchor_refs),
            requirement_linkage=_unique_strings(
                ["browser_quality_gate:interaction_anti_pattern_checks"]
            ),
            classification_candidate="actual_quality_blocker",
            remediation_hints=_unique_strings(
                ["review interaction anti-pattern issue findings"]
            ),
            blocking_reason_codes=diagnostic_codes or ["interaction_probe_quality_blocker"],
        )

    return records, BrowserProbeExecutionReceipt(
        check_name="interaction_anti_pattern_checks",
        started_at=generated_at,
        finished_at=generated_at,
        runtime_status="completed",
        artifact_ids=_unique_strings(record.artifact_id for record in records),
        anchor_refs=_unique_strings(capture.anchor_refs),
        requirement_linkage=_unique_strings(
            ["browser_quality_gate:interaction_anti_pattern_checks"]
        ),
        classification_candidate="pass",
    )


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
                artifact_ids=_unique_strings([records[0].artifact_id]),
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=_unique_strings(
                    ["materialize frontend visual / a11y evidence input"]
                ),
                blocking_reason_codes=_unique_strings(
                    ["visual_expectation_evidence_missing"]
                ),
                requirement_linkage=_unique_strings(
                    ["browser_quality_gate:visual_expectation"]
                ),
            ),
            BrowserProbeExecutionReceipt(
                check_name="basic_a11y",
                started_at=generated_at,
                finished_at=generated_at,
                runtime_status="incomplete",
                artifact_ids=_unique_strings([a11y_records[0].artifact_id]),
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=_unique_strings(
                    ["materialize frontend visual / a11y evidence input"]
                ),
                blocking_reason_codes=_unique_strings(["basic_a11y_evidence_missing"]),
                requirement_linkage=_unique_strings(["browser_quality_gate:basic_a11y"]),
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
            artifact_ids=_unique_strings([visual_record.artifact_id]),
            classification_candidate=classification,
            recheck_required=False,
            remediation_hints=_unique_strings(remediation_hints),
            blocking_reason_codes=_unique_strings(blocking_reason_codes),
            requirement_linkage=_unique_strings(["browser_quality_gate:visual_expectation"]),
        ),
        BrowserProbeExecutionReceipt(
            check_name="basic_a11y",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status=runtime_status,
            artifact_ids=_unique_strings([a11y_record.artifact_id]),
            classification_candidate=classification,
            recheck_required=False,
            remediation_hints=_unique_strings(remediation_hints),
            blocking_reason_codes=_unique_strings(blocking_reason_codes),
            requirement_linkage=_unique_strings(["browser_quality_gate:basic_a11y"]),
        ),
    )


def _materialize_visual_regression_receipt(
    *,
    root: Path,
    artifact_root: Path,
    gate_run_id: str,
    visual_regression_capture: object | None,
    generated_at: str,
    write_artifacts: bool,
) -> tuple[list[BrowserProbeArtifactRecord], BrowserProbeExecutionReceipt]:
    if visual_regression_capture is None:
        return (
            [],
            BrowserProbeExecutionReceipt(
                check_name="visual_regression",
                started_at=generated_at,
                finished_at=generated_at,
                runtime_status="incomplete",
                artifact_ids=[],
                classification_candidate="evidence_missing",
                recheck_required=True,
                remediation_hints=_unique_strings(
                    ["materialize visual regression baseline"]
                ),
                blocking_reason_codes=_unique_strings(
                    ["visual_regression_evidence_missing"]
                ),
                requirement_linkage=_unique_strings(
                    ["browser_quality_gate:visual_regression"]
                ),
            ),
        )

    capture = visual_regression_capture
    artifact_ref = _normalize_runner_artifact_ref(
        str(getattr(capture, "diff_image_ref", "")).strip()
    )
    bootstrap_ref = _normalize_runner_artifact_ref(
        str(getattr(capture, "bootstrap_ref", "")).strip()
    )
    artifact_ids: list[str] = []
    records: list[BrowserProbeArtifactRecord] = []
    missing_artifact = False
    if artifact_ref:
        resolved_status = str(getattr(capture, "capture_status", "missing")).strip()
        if resolved_status == "captured" and not _runner_artifact_exists(
            root=root,
            artifact_root=artifact_root,
            artifact_ref=artifact_ref,
        ):
            resolved_status = "missing"
            missing_artifact = True
        elif resolved_status == "missing":
            missing_artifact = True
        artifact_ids.append(f"{gate_run_id}-visual-regression-1")
        records.append(
            BrowserProbeArtifactRecord(
                artifact_id=f"{gate_run_id}-visual-regression-1",
                gate_run_id=gate_run_id,
                check_name="visual_regression",
                artifact_type="visual_diff",
                artifact_ref=artifact_ref,
                capture_status=resolved_status,
                captured_at=generated_at,
                source_linkage_refs={
                    "matrix_id": str(getattr(capture, "matrix_id", "")).strip(),
                    "bootstrap_ref": bootstrap_ref,
                },
            )
        )
    elif bootstrap_ref:
        resolved_status = (
            "captured"
            if _runner_artifact_exists(
                root=root,
                artifact_root=artifact_root,
                artifact_ref=bootstrap_ref,
            )
            else "missing"
        )
        artifact_ids.append(f"{gate_run_id}-visual-regression-bootstrap-1")
        records.append(
            BrowserProbeArtifactRecord(
                artifact_id=f"{gate_run_id}-visual-regression-bootstrap-1",
                gate_run_id=gate_run_id,
                check_name="visual_regression",
                artifact_type="visual_regression_bootstrap",
                artifact_ref=bootstrap_ref,
                capture_status=resolved_status,
                captured_at=generated_at,
                source_linkage_refs={
                    "matrix_id": str(getattr(capture, "matrix_id", "")).strip(),
                    "diff_image_ref": artifact_ref,
                },
            )
        )
    elif str(getattr(capture, "capture_status", "missing")).strip() == "captured":
        missing_artifact = True

    verdict = str(getattr(capture, "verdict", "evidence_missing")).strip()
    if missing_artifact and verdict == "pass":
        verdict = "evidence_missing"
    classification_candidate = (
        "evidence_missing" if verdict == "recheck" else verdict
    )
    runtime_status = (
        "failed_transient"
        if verdict == "transient_run_failure"
        else "incomplete"
        if verdict in {"evidence_missing", "recheck"}
        else "completed"
    )
    return (
        records,
        BrowserProbeExecutionReceipt(
            check_name="visual_regression",
            started_at=generated_at,
            finished_at=generated_at,
            runtime_status=runtime_status,
            artifact_ids=_unique_strings(artifact_ids),
            classification_candidate=classification_candidate,  # type: ignore[arg-type]
            recheck_required=verdict in {"evidence_missing", "recheck"},
            remediation_hints=_unique_strings(
                ["review visual regression diff output"]
                if verdict == "actual_quality_blocker"
                else ["materialize visual regression baseline"]
                if verdict == "evidence_missing"
                else ["rerun visual regression after recheck signal"]
                if verdict == "recheck"
                else []
            ),
            blocking_reason_codes=_unique_strings(
                ["visual_regression_quality_blocker"]
                if verdict == "actual_quality_blocker"
                else ["visual_regression_evidence_missing"]
                if verdict == "evidence_missing"
                else ["visual_regression_recheck_required"]
                if verdict == "recheck"
                else ["visual_regression_transient_failure"]
                if verdict == "transient_run_failure"
                else []
            ),
            requirement_linkage=_unique_strings(
                ["browser_quality_gate:visual_regression"]
            ),
        ),
    )


def _normalize_runner_artifact_ref(artifact_ref: str) -> str:
    ref = artifact_ref.strip()
    if ref.startswith("artifact:"):
        ref = ref.removeprefix("artifact:").strip()
    return ref


def _runner_artifact_exists(*, root: Path, artifact_root: Path, artifact_ref: str) -> bool:
    normalized_ref = _normalize_runner_artifact_ref(artifact_ref)
    if not normalized_ref:
        return False
    artifact_path = (root / normalized_ref).resolve()
    try:
        artifact_path.relative_to(artifact_root.resolve())
    except ValueError:
        return False
    return artifact_path.is_file()


def _derive_browser_entry_ref(managed_frontend_target: str) -> str:
    target = managed_frontend_target.strip()
    if not target:
        return ""
    if "://" in target:
        return target
    candidate = Path(target)
    if candidate.suffix:
        return candidate.as_posix()
    return (candidate / "index.html").as_posix()


def _invoke_probe_runner(
    probe_runner: BrowserGateProbeRunner,
    *,
    root: Path,
    artifact_root: Path,
    execution_context: BrowserQualityGateExecutionContext,
    generated_at: str,
) -> BrowserGateProbeRunnerResult:
    signature_target = probe_runner
    side_effect = getattr(probe_runner, "side_effect", None)
    if callable(side_effect):
        signature_target = side_effect

    try:
        signature = inspect.signature(signature_target)
    except (TypeError, ValueError):
        signature = None

    if signature is None:
        return probe_runner(
            root=root,
            artifact_root=artifact_root,
            execution_context=execution_context,
            generated_at=generated_at,
        )

    parameters = signature.parameters
    supports_var_keyword = any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    kwargs: dict[str, object] = {
        "artifact_root": artifact_root,
        "execution_context": execution_context,
        "generated_at": generated_at,
    }
    if supports_var_keyword or "root" in parameters:
        kwargs["root"] = root
    return probe_runner(**kwargs)


def _transient_probe_runner_result(
    *,
    gate_run_id: str,
    artifact_root_rel: str,
    diagnostic_code: str,
    warning: str,
) -> BrowserGateProbeRunnerResult:
    return BrowserGateProbeRunnerResult(
        runtime_status="failed_transient",
        shared_capture=BrowserGateSharedRuntimeCapture(
            gate_run_id=gate_run_id,
            trace_artifact_ref=f"{artifact_root_rel}/{_PLAYWRIGHT_TRACE_REL_PATH}",
            navigation_screenshot_ref=f"{artifact_root_rel}/{_PLAYWRIGHT_SCREENSHOT_REL_PATH}",
            capture_status="capture_failed",
            final_url="",
            diagnostic_codes=[diagnostic_code],
        ),
        interaction_capture=BrowserGateInteractionProbeCapture(
            gate_run_id=gate_run_id,
            interaction_probe_id="primary-action",
            artifact_refs=_unique_strings([f"{artifact_root_rel}/{_INTERACTION_SNAPSHOT_REL_PATH}"]),
            capture_status="capture_failed",
            classification_candidate="transient_run_failure",
            blocking_reason_codes=_unique_strings([diagnostic_code]),
        ),
        diagnostic_codes=_unique_strings([diagnostic_code]),
        warnings=_unique_strings([warning]),
    )


def _diagnostic_warning_messages(codes: Iterable[str]) -> list[str]:
    messages: list[str] = []
    for code in codes:
        if code == "playwright_runtime_unavailable":
            messages.append(
                "Playwright runtime is not available on this host. Install Playwright and its browsers for this frontend host, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            )
        elif code == "browser_launch_failed":
            messages.append(
                "Browser launch failed before the probe could complete. Restore the frontend browser runtime, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            )
        elif code == "navigation_failed":
            messages.append(
                "Browser navigation failed before the probe could complete. Confirm the browser entry exists and is loadable, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            )
        elif code == "browser_entry_unavailable":
            messages.append(
                "The managed frontend target did not resolve to a loadable browser entry. Materialize a browser entry such as `index.html`, or point the apply artifact at a navigable URL, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            )
        elif code == "browser_probe_timeout":
            messages.append(
                "Browser gate probe timed out before completion. Confirm the frontend host is ready, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            )
        elif code == "playwright_runner_script_missing":
            messages.append(
                "Playwright probe runner is missing from this installation. Restore the AI-SDLC runner assets, then re-run `uv run ai-sdlc program browser-gate-probe --execute`."
            )
        elif code == "playwright_probe_evidence_missing":
            messages.append("Shared Playwright artifacts were not fully captured.")
        elif code == "interaction_probe_evidence_missing":
            messages.append("Interaction probe artifacts were not fully captured.")
    return _unique_strings(messages)


def _session_status(
    overall_gate_status: str,
    *,
    receipts: list[BrowserProbeExecutionReceipt],
) -> str:
    if any(
        receipt.runtime_status == "failed_transient"
        or receipt.classification_candidate == "transient_run_failure"
        for receipt in receipts
    ):
        return "failed"
    if overall_gate_status in {"passed", "passed_with_advisories"}:
        return "completed"
    return "incomplete"


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


def _resolve_visual_verdict(
    *,
    runner_result: BrowserGateProbeRunnerResult | None,
    receipts: list[BrowserProbeExecutionReceipt],
) -> str:
    visual_regression_capture = (
        runner_result.visual_regression_capture if runner_result is not None else None
    )
    if visual_regression_capture is not None:
        visual_regression_receipt = next(
            (receipt for receipt in receipts if receipt.check_name == "visual_regression"),
            None,
        )
        if visual_regression_receipt is None:
            return _receipt_verdict(receipts, "visual_expectation")
        if (
            visual_regression_capture.verdict != "recheck"
            and visual_regression_receipt.classification_candidate
            != visual_regression_capture.verdict
        ):
            return visual_regression_receipt.classification_candidate
        return visual_regression_capture.verdict
    return _receipt_verdict(receipts, "visual_expectation")


def _unique_strings(values: Iterable[object]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered
