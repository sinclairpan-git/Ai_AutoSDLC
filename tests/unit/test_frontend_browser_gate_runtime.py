"""Unit tests for real frontend browser gate probe runtime."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from ai_sdlc.core.frontend_browser_gate_runtime import (
    BrowserGateInteractionProbeCapture,
    BrowserGateProbeRunnerResult,
    BrowserGateProbeRuntimeSession,
    BrowserGateSharedRuntimeCapture,
    BrowserProbeArtifactRecord,
    BrowserProbeExecutionReceipt,
    BrowserQualityBundleMaterializationInput,
    build_browser_quality_gate_execution_context,
    materialize_browser_gate_probe_runtime,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
    load_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.models.frontend_browser_gate import (
    BrowserGateQualityCapture,
    BrowserQualityGateExecutionContext,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot


def _context() -> BrowserQualityGateExecutionContext:
    return BrowserQualityGateExecutionContext(
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="solution-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        readiness_subject_id="001-auth",
        effective_provider="public-primevue",
        effective_style_pack="modern-saas",
        style_fidelity_status="full",
        delivery_entry_id="vue3-public-primevue",
        component_library_packages=["primevue", "@primeuix/themes"],
        provider_theme_adapter_id="public-primevue-theme-bridge",
        provider_runtime_adapter_carrier_mode="target-project-adapter-layer",
        provider_runtime_adapter_delivery_state="scaffolded",
        provider_runtime_adapter_evidence_state="missing",
        page_schema_ids=["dashboard-workspace", "search-list-workspace"],
        required_probe_set=[
            "playwright_smoke",
            "visual_expectation",
            "visual_regression",
            "basic_a11y",
            "interaction_anti_pattern_checks",
        ],
        browser_entry_ref="managed/frontend/index.html",
        source_linkage_refs={"apply_result_status": "apply_succeeded_pending_browser_gate"},
    )


def test_browser_gate_quality_capture_keeps_absent_optional_telemetry_nullable() -> None:
    capture = BrowserGateQualityCapture.model_validate(
        {
            "gate_run_id": "gate-run-001",
            "page_title": "frontend-browser-entry",
            "final_url": "http://localhost:4173/",
            "screenshot_ref": "artifact:screenshot.png",
            "body_text_char_count": 420,
            "heading_count": 2,
            "landmark_count": 3,
            "interactive_count": 4,
            "unlabeled_button_count": 0,
            "unlabeled_input_count": 0,
            "image_missing_alt_count": 0,
        }
    )

    assert capture.viewport_width is None
    assert capture.document_scroll_width is None
    assert capture.horizontal_overflow_count is None
    assert capture.low_contrast_text_count is None
    assert capture.focusable_count is None
    assert capture.focusable_without_visible_focus_count is None


def _visual_a11y_pass_artifact():
    return build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-pass",
                target_id="page:user-create",
                surface_id="page:user-create",
                outcome="pass",
                report_type="coverage-report",
                severity="info",
                location_anchor="specs",
                quality_hint="fixture pass",
                changed_scope_explanation="runtime fixture",
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-14T15:00:00Z",
    )


def test_build_browser_quality_gate_execution_context_derives_index_html_entry_ref() -> None:
    context = build_browser_quality_gate_execution_context(
        apply_payload={
            "result_status": "apply_succeeded_pending_browser_gate",
            "browser_gate_required": True,
            "apply_result_id": "apply-result-001",
            "execution_view": {
                "spec_dir": "specs/001-auth",
                "attachment_scope_ref": "scope://001-auth",
                "readiness_subject_id": "001-auth",
                "managed_target_path": "managed/frontend",
                "action_items": [
                    {
                        "action_type": "dependency_install",
                        "executor_payload": {"package_manager": "pnpm"},
                    }
                ],
            },
        },
        solution_snapshot=build_mvp_solution_snapshot(),
        gate_run_id="gate-run-ctx",
        delivery_entry_id="vue3-public-primevue",
        component_library_packages=["primevue", "primevue", "@primeuix/themes"],
        provider_theme_adapter_id="public-primevue-theme-bridge",
        provider_runtime_adapter_carrier_mode="target-project-adapter-layer",
        provider_runtime_adapter_delivery_state="scaffolded",
        provider_runtime_adapter_evidence_state="missing",
        page_schema_ids=[
            "dashboard-workspace",
            "dashboard-workspace",
            "search-list-workspace",
        ],
        visual_regression_matrix_id="dashboard-modern-saas-desktop-chromium",
        visual_regression_viewport_id="desktop-1440",
    )

    assert context.browser_entry_ref == "managed/frontend/index.html"
    assert context.delivery_entry_id == "vue3-public-primevue"
    assert context.package_manager == "pnpm"
    assert context.component_library_packages == ["primevue", "@primeuix/themes"]
    assert context.provider_theme_adapter_id == "public-primevue-theme-bridge"
    assert context.provider_runtime_adapter_carrier_mode == "target-project-adapter-layer"
    assert context.provider_runtime_adapter_delivery_state == "scaffolded"
    assert context.provider_runtime_adapter_evidence_state == "missing"
    assert context.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]
    assert context.visual_regression_matrix_id == "dashboard-modern-saas-desktop-chromium"
    assert context.visual_regression_viewport_id == "desktop-1440"
    assert "visual_regression" in context.required_probe_set


def test_build_browser_quality_gate_execution_context_skips_visual_regression_without_matrix() -> None:
    context = build_browser_quality_gate_execution_context(
        apply_payload={
            "result_status": "apply_succeeded_pending_browser_gate",
            "browser_gate_required": True,
            "apply_result_id": "apply-result-001",
            "execution_view": {
                "spec_dir": "specs/001-auth",
                "attachment_scope_ref": "scope://001-auth",
                "readiness_subject_id": "001-auth",
                "managed_target_path": "managed/frontend",
            },
        },
        solution_snapshot=build_mvp_solution_snapshot(),
        gate_run_id="gate-run-ctx",
        delivery_entry_id="vue3-public-primevue",
    )

    assert context.visual_regression_matrix_id == ""
    assert context.visual_regression_viewport_id == ""
    assert "visual_regression" not in context.required_probe_set


def test_materialize_browser_gate_probe_runtime_executes_real_runner_and_captures_artifacts(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        diff_path = artifact_root / "diff" / "diff.png"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        diff_path.write_bytes(b"png")
        return BrowserGateProbeRunnerResult(
            runtime_status="completed",
            shared_capture=BrowserGateSharedRuntimeCapture(
                gate_run_id=execution_context.gate_run_id,
                trace_artifact_ref=str(trace_path.relative_to(tmp_path)),
                navigation_screenshot_ref=str(screenshot_path.relative_to(tmp_path)),
                capture_status="captured",
                final_url="http://localhost:4173/",
                anchor_refs=["page:landing"],
                diagnostic_codes=[],
            ),
            interaction_capture=BrowserGateInteractionProbeCapture(
                gate_run_id=execution_context.gate_run_id,
                interaction_probe_id="primary-action",
                artifact_refs=[str(interaction_path.relative_to(tmp_path))],
                capture_status="captured",
                classification_candidate="pass",
                blocking_reason_codes=[],
                anchor_refs=["interaction:primary-action"],
            ),
            visual_regression_capture={
                "matrix_id": "",
                "gate_run_id": execution_context.gate_run_id,
                "capture_status": "missing",
                "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                "baseline_ref": "",
                "baseline_metadata_ref": "",
                "diff_image_ref": "",
                "diff_ratio": 1.0,
                "threshold": 0.03,
                "region_summaries": [],
                "change_summary": "baseline-missing",
                "capture_protocol_ref": "",
                "bootstrap_ref": "",
                "verdict": "evidence_missing",
            },
            diagnostic_codes=[],
            warnings=[],
        )

    session, records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    assert session.status == "incomplete"
    assert bundle.overall_gate_status == "incomplete"
    smoke_receipt = next(item for item in receipts if item.check_name == "playwright_smoke")
    interaction_receipt = next(
        item for item in receipts if item.check_name == "interaction_anti_pattern_checks"
    )
    visual_regression_receipt = next(
        item for item in receipts if item.check_name == "visual_regression"
    )
    assert smoke_receipt.classification_candidate == "pass"
    assert interaction_receipt.classification_candidate == "pass"
    assert visual_regression_receipt.classification_candidate == "evidence_missing"
    assert any(record.artifact_type == "playwright_trace" for record in records)
    assert any(record.artifact_type == "interaction_snapshot" for record in records)
    assert bundle.delivery_entry_id == "vue3-public-primevue"
    assert bundle.component_library_packages == ["primevue", "@primeuix/themes"]
    assert bundle.provider_theme_adapter_id == "public-primevue-theme-bridge"
    assert bundle.provider_runtime_adapter_carrier_mode == "target-project-adapter-layer"
    assert bundle.provider_runtime_adapter_delivery_state == "scaffolded"
    assert bundle.provider_runtime_adapter_evidence_state == "missing"
    assert bundle.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]


def test_materialize_browser_gate_probe_runtime_can_pass_without_visual_regression_matrix(
    tmp_path: Path,
) -> None:
    context = _context().model_copy(
        update={
            "visual_regression_matrix_id": "",
            "visual_regression_viewport_id": "",
            "required_probe_set": [
                "playwright_smoke",
                "visual_expectation",
                "basic_a11y",
                "interaction_anti_pattern_checks",
            ],
        }
    )

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult(
            runtime_status="completed",
            shared_capture=BrowserGateSharedRuntimeCapture(
                gate_run_id=execution_context.gate_run_id,
                trace_artifact_ref=str(trace_path.relative_to(tmp_path)),
                navigation_screenshot_ref=str(screenshot_path.relative_to(tmp_path)),
                capture_status="captured",
                final_url="http://localhost:4173/",
                anchor_refs=["page:landing"],
                diagnostic_codes=[],
            ),
            interaction_capture=BrowserGateInteractionProbeCapture(
                gate_run_id=execution_context.gate_run_id,
                interaction_probe_id="primary-action",
                artifact_refs=[str(interaction_path.relative_to(tmp_path))],
                capture_status="captured",
                classification_candidate="pass",
                blocking_reason_codes=[],
                anchor_refs=["interaction:primary-action"],
            ),
            diagnostic_codes=[],
            warnings=[],
        )

    session, records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    assert session.status == "completed"
    assert bundle.overall_gate_status == "passed"
    assert bundle.visual_verdict == "pass"
    assert {receipt.check_name for receipt in receipts} == set(context.required_probe_set)
    assert not any(record.check_name == "visual_regression" for record in records)


def test_materialize_browser_gate_probe_runtime_prefers_visual_regression_verdict_when_available(
    tmp_path: Path,
) -> None:
    context = _context()
    visual_a11y_block_artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-block",
                target_id="page:user-create",
                surface_id="page:user-create",
                outcome="issue",
                report_type="coverage-report",
                severity="high",
                location_anchor="specs",
                quality_hint="fixture block",
                changed_scope_explanation="runtime fixture",
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-14T15:00:00Z",
    )

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        diff_path = artifact_root / "diff" / "diff.png"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        diff_path.write_bytes(b"png")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "quality_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "page_title": "frontend-browser-entry",
                    "final_url": "http://localhost:4173/",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "body_text_char_count": 420,
                    "heading_count": 2,
                    "landmark_count": 3,
                    "interactive_count": 4,
                    "unlabeled_button_count": 0,
                    "unlabeled_input_count": 0,
                    "image_missing_alt_count": 0,
                    "viewport_width": 1280,
                    "viewport_height": 720,
                    "document_scroll_width": 1280,
                    "document_scroll_height": 720,
                    "horizontal_overflow_count": 0,
                    "low_contrast_text_count": 0,
                    "focusable_count": 4,
                    "focusable_without_visible_focus_count": 0,
                    "console_error_messages": [],
                    "page_error_messages": [],
                },
                "visual_regression_capture": {
                    "matrix_id": "dashboard-modern-saas-desktop-chromium",
                    "gate_run_id": execution_context.gate_run_id,
                    "capture_status": "captured",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "baseline_ref": "governance/frontend/quality-platform/evidence/visual-regression/baselines/dashboard-modern-saas-desktop-chromium/baseline.png",
                    "baseline_metadata_ref": "governance/frontend/quality-platform/evidence/visual-regression/baselines/dashboard-modern-saas-desktop-chromium/baseline.yaml",
                    "diff_image_ref": str(diff_path.relative_to(tmp_path)),
                    "diff_ratio": 0.0,
                    "threshold": 0.03,
                    "region_summaries": [],
                    "change_summary": "identical",
                    "capture_protocol_ref": "matrix:dashboard-modern-saas-desktop-chromium",
                    "bootstrap_ref": "artifact:.ai-sdlc/artifacts/frontend-browser-gate/gate-run-001/bootstrap/bootstrap-receipt.yaml",
                    "verdict": "pass",
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=visual_a11y_block_artifact,
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    assert bundle.visual_verdict == "pass"


def test_materialize_browser_gate_probe_runtime_fails_closed_when_visual_diff_missing(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        missing_diff_path = artifact_root / "visual-regression" / "missing-diff.png"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "visual_regression_capture": {
                    "matrix_id": "dashboard-modern-saas-desktop-chromium",
                    "gate_run_id": execution_context.gate_run_id,
                    "capture_status": "captured",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "baseline_ref": "governance/frontend/baseline.png",
                    "baseline_metadata_ref": "governance/frontend/baseline.yaml",
                    "diff_image_ref": str(missing_diff_path.relative_to(tmp_path)),
                    "diff_ratio": 0.0,
                    "threshold": 0.03,
                    "region_summaries": [],
                    "change_summary": "identical",
                    "capture_protocol_ref": (
                        "matrix:dashboard-modern-saas-desktop-chromium"
                    ),
                    "bootstrap_ref": "",
                    "verdict": "pass",
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    _session, records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    visual_record = next(record for record in records if record.check_name == "visual_regression")
    visual_receipt = next(item for item in receipts if item.check_name == "visual_regression")
    assert visual_record.capture_status == "missing"
    assert visual_receipt.classification_candidate == "evidence_missing"
    assert visual_receipt.recheck_required is True
    assert "visual_regression_evidence_missing" in visual_receipt.blocking_reason_codes
    assert bundle.overall_gate_status == "incomplete"
    assert bundle.visual_verdict == "evidence_missing"


def test_materialize_browser_gate_probe_runtime_marks_visual_transient_as_failed_session(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "visual_regression_capture": {
                    "matrix_id": "dashboard-modern-saas-desktop-chromium",
                    "gate_run_id": execution_context.gate_run_id,
                    "capture_status": "capture_failed",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "baseline_ref": "governance/frontend/baseline.png",
                    "baseline_metadata_ref": "governance/frontend/baseline.yaml",
                    "diff_image_ref": "",
                    "diff_ratio": 0.0,
                    "threshold": 0.03,
                    "region_summaries": [],
                    "change_summary": "visual-regression-dependencies-unavailable",
                    "capture_protocol_ref": (
                        "matrix:dashboard-modern-saas-desktop-chromium"
                    ),
                    "bootstrap_ref": "",
                    "verdict": "transient_run_failure",
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    visual_receipt = next(item for item in receipts if item.check_name == "visual_regression")
    assert visual_receipt.runtime_status == "failed_transient"
    assert visual_receipt.classification_candidate == "transient_run_failure"
    assert "visual_regression_transient_failure" in visual_receipt.blocking_reason_codes
    assert session.status == "failed"
    assert bundle.overall_gate_status == "incomplete"
    assert bundle.visual_verdict == "transient_run_failure"


def test_materialize_browser_gate_probe_runtime_normalizes_artifact_prefixed_visual_regression_refs(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        diff_path = artifact_root / "visual-regression" / "diff.png"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        diff_path.write_bytes(b"png")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "visual_regression_capture": {
                    "matrix_id": "dashboard-modern-saas-desktop-chromium",
                    "gate_run_id": execution_context.gate_run_id,
                    "capture_status": "captured",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "baseline_ref": "artifact:governance/frontend/quality-platform/evidence/visual-regression/baselines/dashboard-modern-saas-desktop-chromium/baseline.png",
                    "baseline_metadata_ref": "artifact:governance/frontend/quality-platform/evidence/visual-regression/baselines/dashboard-modern-saas-desktop-chromium/baseline.yaml",
                    "diff_image_ref": f"artifact:{diff_path.relative_to(tmp_path)}",
                    "diff_ratio": 0.0,
                    "threshold": 0.03,
                    "region_summaries": [],
                    "change_summary": "identical",
                    "capture_protocol_ref": "matrix:dashboard-modern-saas-desktop-chromium",
                    "bootstrap_ref": f"artifact:{(artifact_root / 'bootstrap' / 'bootstrap-receipt.yaml').relative_to(tmp_path)}",
                    "verdict": "pass",
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    _session, records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    visual_record = next(record for record in records if record.check_name == "visual_regression")
    visual_receipt = next(item for item in receipts if item.check_name == "visual_regression")
    assert (
        visual_record.artifact_ref
        == ".ai-sdlc/artifacts/frontend-browser-gate/gate-run-001/visual-regression/diff.png"
    )
    assert visual_record.source_linkage_refs["bootstrap_ref"] == (
        ".ai-sdlc/artifacts/frontend-browser-gate/gate-run-001/bootstrap/bootstrap-receipt.yaml"
    )
    assert visual_receipt.classification_candidate == "pass"
    assert bundle.overall_gate_status == "passed"


def test_materialize_browser_gate_probe_runtime_normalizes_visual_regression_recheck_verdict(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        bootstrap_path = artifact_root / "bootstrap" / "bootstrap-receipt.yaml"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        bootstrap_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        bootstrap_path.write_text("state: recheck\n", encoding="utf-8")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(
                        screenshot_path.relative_to(tmp_path)
                    ),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "visual_regression_capture": {
                    "matrix_id": "dashboard-modern-saas-desktop-chromium",
                    "gate_run_id": execution_context.gate_run_id,
                    "capture_status": "captured",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "baseline_ref": "governance/frontend/baseline.png",
                    "baseline_metadata_ref": "governance/frontend/baseline.yaml",
                    "diff_image_ref": "",
                    "diff_ratio": 0.0,
                    "threshold": 0.03,
                    "region_summaries": [],
                    "change_summary": "recheck requested",
                    "capture_protocol_ref": (
                        "matrix:dashboard-modern-saas-desktop-chromium"
                    ),
                    "bootstrap_ref": str(bootstrap_path.relative_to(tmp_path)),
                    "verdict": "recheck",
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    _session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    visual_record = next(
        record
        for record in _records
        if record.artifact_type == "visual_regression_bootstrap"
    )
    visual_receipt = next(
        item for item in receipts if item.check_name == "visual_regression"
    )
    assert visual_record.capture_status == "captured"
    assert visual_record.artifact_ref == (
        ".ai-sdlc/artifacts/frontend-browser-gate/"
        "gate-run-001/bootstrap/bootstrap-receipt.yaml"
    )
    assert visual_receipt.artifact_ids == [visual_record.artifact_id]
    assert visual_receipt.classification_candidate == "evidence_missing"
    assert visual_receipt.recheck_required is True
    assert "visual_regression_recheck_required" in visual_receipt.blocking_reason_codes
    assert bundle.overall_gate_status == "incomplete"
    assert bundle.visual_verdict == "recheck"


def test_materialize_browser_gate_probe_runtime_marks_missing_runner_artifact_as_evidence_missing(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult(
            runtime_status="completed",
            shared_capture=BrowserGateSharedRuntimeCapture(
                gate_run_id=execution_context.gate_run_id,
                trace_artifact_ref=str(
                    (artifact_root / "shared-runtime" / "playwright-trace.zip").relative_to(
                        tmp_path
                    )
                ),
                navigation_screenshot_ref=str(screenshot_path.relative_to(tmp_path)),
                capture_status="captured",
                final_url="http://localhost:4173/",
                anchor_refs=["page:landing"],
                diagnostic_codes=[],
            ),
            interaction_capture=BrowserGateInteractionProbeCapture(
                gate_run_id=execution_context.gate_run_id,
                interaction_probe_id="primary-action",
                artifact_refs=[str(interaction_path.relative_to(tmp_path))],
                capture_status="captured",
                classification_candidate="pass",
                blocking_reason_codes=[],
                anchor_refs=["interaction:primary-action"],
            ),
            diagnostic_codes=[],
            warnings=[],
        )

    _session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    smoke_receipt = next(item for item in receipts if item.check_name == "playwright_smoke")
    assert smoke_receipt.classification_candidate == "evidence_missing"
    assert bundle.overall_gate_status == "incomplete"


def test_materialize_browser_gate_probe_runtime_deduplicates_context_lists_and_warnings(
    tmp_path: Path,
) -> None:
    context = _context().model_copy(
        update={
            "component_library_packages": [
                "primevue",
                "primevue",
                "@primeuix/themes",
            ],
            "page_schema_ids": [
                "dashboard-workspace",
                "dashboard-workspace",
                "search-list-workspace",
            ],
        }
    )

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult(
            runtime_status="completed",
            shared_capture=BrowserGateSharedRuntimeCapture(
                gate_run_id=execution_context.gate_run_id,
                trace_artifact_ref=str(trace_path.relative_to(tmp_path)),
                navigation_screenshot_ref=str(screenshot_path.relative_to(tmp_path)),
                capture_status="captured",
                final_url="http://localhost:4173/",
                anchor_refs=["page:landing", "page:landing"],
                diagnostic_codes=[],
            ),
            interaction_capture=BrowserGateInteractionProbeCapture(
                gate_run_id=execution_context.gate_run_id,
                interaction_probe_id="primary-action",
                artifact_refs=[str(interaction_path.relative_to(tmp_path))],
                capture_status="captured",
                classification_candidate="pass",
                blocking_reason_codes=[],
                anchor_refs=["interaction:primary-action", "interaction:primary-action"],
            ),
            diagnostic_codes=[],
            warnings=["runner warning", "runner warning"],
        )

    session, records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=_visual_a11y_pass_artifact(),
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    assert session.warnings == ["runner warning"]
    assert bundle.component_library_packages == ["primevue", "@primeuix/themes"]
    assert bundle.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]


def test_materialize_browser_gate_probe_runtime_auto_materializes_visual_a11y_evidence_from_runner_quality_capture(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "quality_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "page_title": "frontend-browser-entry",
                    "final_url": "http://localhost:4173/",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "body_text_char_count": 420,
                    "heading_count": 2,
                    "landmark_count": 3,
                    "interactive_count": 4,
                    "unlabeled_button_count": 0,
                    "unlabeled_input_count": 0,
                    "image_missing_alt_count": 0,
                    "viewport_width": 1280,
                    "viewport_height": 720,
                    "document_scroll_width": 1280,
                    "document_scroll_height": 720,
                    "horizontal_overflow_count": 0,
                    "low_contrast_text_count": 0,
                    "focusable_count": 4,
                    "focusable_without_visible_focus_count": 0,
                    "console_error_messages": [],
                    "page_error_messages": [],
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=None,
        generated_at="2026-04-22T16:25:00Z",
        probe_runner=_runner,
        execute_probe=True,
        auto_visual_a11y_provider=True,
    )

    assert session.status == "incomplete"
    assert bundle.overall_gate_status == "incomplete"
    evidence_path = (
        tmp_path / "specs" / "001-auth" / "frontend-visual-a11y-evidence.json"
    )
    assert evidence_path.is_file()
    visual_receipt = next(item for item in receipts if item.check_name == "visual_expectation")
    a11y_receipt = next(item for item in receipts if item.check_name == "basic_a11y")
    visual_regression_receipt = next(
        item for item in receipts if item.check_name == "visual_regression"
    )
    assert visual_receipt.classification_candidate == "pass"
    assert a11y_receipt.classification_candidate == "pass"
    assert visual_regression_receipt.classification_candidate == "evidence_missing"
    loaded_artifact = load_frontend_visual_a11y_evidence_artifact(evidence_path)
    assert any(
        item.evaluation_id == "auto-visual-text-contrast" and item.outcome == "pass"
        for item in loaded_artifact.evaluations
    )
    assert any(
        item.evaluation_id == "auto-a11y-focus-visible" and item.outcome == "pass"
        for item in loaded_artifact.evaluations
    )


def test_materialize_browser_gate_probe_runtime_rejects_outside_spec_dir_for_auto_visual_a11y_evidence(
    tmp_path: Path,
) -> None:
    outside_dir_name = f"{tmp_path.name}-outside-spec"
    context = _context().model_copy(update={"spec_dir": f"../{outside_dir_name}"})

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(
                        screenshot_path.relative_to(tmp_path)
                    ),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "quality_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "page_title": "frontend-browser-entry",
                    "final_url": "http://localhost:4173/",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "body_text_char_count": 420,
                    "heading_count": 2,
                    "landmark_count": 3,
                    "interactive_count": 4,
                    "unlabeled_button_count": 0,
                    "unlabeled_input_count": 0,
                    "image_missing_alt_count": 0,
                    "viewport_width": 1280,
                    "viewport_height": 720,
                    "document_scroll_width": 1280,
                    "document_scroll_height": 720,
                    "horizontal_overflow_count": 0,
                    "low_contrast_text_count": 0,
                    "focusable_count": 4,
                    "focusable_without_visible_focus_count": 0,
                    "console_error_messages": [],
                    "page_error_messages": [],
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    _session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=None,
        generated_at="2026-04-22T16:27:00Z",
        probe_runner=_runner,
        execute_probe=True,
        auto_visual_a11y_provider=True,
    )

    escaped_evidence_path = (
        tmp_path.parent / outside_dir_name / "frontend-visual-a11y-evidence.json"
    )
    assert not escaped_evidence_path.exists()
    visual_receipt = next(
        item for item in receipts if item.check_name == "visual_expectation"
    )
    assert visual_receipt.classification_candidate == "evidence_missing"
    assert bundle.overall_gate_status == "incomplete"


def test_materialize_browser_gate_probe_runtime_regenerates_invalid_auto_visual_a11y_evidence(
    tmp_path: Path,
) -> None:
    context = _context()
    spec_dir = tmp_path / "specs" / "001-auth"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "frontend-visual-a11y-evidence.json").write_text(
        '{"schema_version":"frontend-visual-a11y-evidence/v1","provenance":',
        encoding="utf-8",
    )

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult.model_validate(
            {
                "runtime_status": "completed",
                "shared_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "trace_artifact_ref": str(trace_path.relative_to(tmp_path)),
                    "navigation_screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "capture_status": "captured",
                    "final_url": "http://localhost:4173/",
                    "anchor_refs": ["page:landing"],
                    "diagnostic_codes": [],
                },
                "interaction_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "interaction_probe_id": "primary-action",
                    "artifact_refs": [str(interaction_path.relative_to(tmp_path))],
                    "capture_status": "captured",
                    "classification_candidate": "pass",
                    "blocking_reason_codes": [],
                    "anchor_refs": ["interaction:primary-action"],
                },
                "quality_capture": {
                    "gate_run_id": execution_context.gate_run_id,
                    "page_title": "frontend-browser-entry",
                    "final_url": "http://localhost:4173/",
                    "screenshot_ref": str(screenshot_path.relative_to(tmp_path)),
                    "body_text_char_count": 420,
                    "heading_count": 2,
                    "landmark_count": 3,
                    "interactive_count": 4,
                    "unlabeled_button_count": 0,
                    "unlabeled_input_count": 0,
                    "image_missing_alt_count": 0,
                    "viewport_width": 1280,
                    "viewport_height": 720,
                    "document_scroll_width": 1280,
                    "document_scroll_height": 720,
                    "horizontal_overflow_count": 0,
                    "low_contrast_text_count": 0,
                    "focusable_count": 4,
                    "focusable_without_visible_focus_count": 0,
                    "console_error_messages": [],
                    "page_error_messages": [],
                },
                "diagnostic_codes": [],
                "warnings": [],
            }
        )

    _session, _records, receipts, bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=None,
        generated_at="2026-04-22T16:30:00Z",
        probe_runner=_runner,
        execute_probe=True,
        auto_visual_a11y_provider=True,
    )

    evidence_path = spec_dir / "frontend-visual-a11y-evidence.json"
    regenerated_artifact = load_frontend_visual_a11y_evidence_artifact(evidence_path)
    assert bundle.overall_gate_status == "incomplete"
    assert any(
        item.evaluation_id == "auto-visual-text-contrast" and item.outcome == "pass"
        for item in regenerated_artifact.evaluations
    )
    assert any(
        item.evaluation_id == "auto-a11y-focus-visible" and item.outcome == "pass"
        for item in regenerated_artifact.evaluations
    )
    visual_receipt = next(item for item in receipts if item.check_name == "visual_expectation")
    a11y_receipt = next(item for item in receipts if item.check_name == "basic_a11y")
    assert visual_receipt.classification_candidate == "pass"
    assert a11y_receipt.classification_candidate == "pass"


def test_frontend_browser_gate_models_deduplicate_set_like_lists() -> None:
    context = BrowserQualityGateExecutionContext(
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="solution-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        readiness_subject_id="001-auth",
        effective_provider="public-primevue",
        effective_style_pack="modern-saas",
        style_fidelity_status="full",
        component_library_packages=["primevue", "primevue", "@primeuix/themes"],
        page_schema_ids=["dashboard", "dashboard", "search"],
        required_probe_set=["playwright_smoke", "playwright_smoke", "basic_a11y"],
        browser_entry_ref="managed/frontend/index.html",
    )
    session = BrowserGateProbeRuntimeSession(
        probe_runtime_session_id="runtime-001",
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="solution-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        readiness_subject_id="001-auth",
        browser_entry_ref="managed/frontend/index.html",
        artifact_root_ref="artifacts/browser-gate",
        status="running_checks",
        started_at="2026-04-21T00:00:00Z",
        updated_at="2026-04-21T00:00:00Z",
        warnings=["probe-delayed", "probe-delayed"],
    )
    shared_capture = BrowserGateSharedRuntimeCapture(
        gate_run_id="gate-run-001",
        trace_artifact_ref="trace.zip",
        navigation_screenshot_ref="nav.png",
        capture_status="captured",
        final_url="http://localhost:4173/",
        anchor_refs=["page:landing", "page:landing"],
        diagnostic_codes=["nav_ok", "nav_ok"],
    )
    interaction_capture = BrowserGateInteractionProbeCapture(
        gate_run_id="gate-run-001",
        interaction_probe_id="primary-action",
        artifact_refs=["interaction.json", "interaction.json"],
        capture_status="captured",
        classification_candidate="pass",
        blocking_reason_codes=["interaction_blocked", "interaction_blocked"],
        anchor_refs=["interaction:primary", "interaction:primary"],
    )
    runner_result = BrowserGateProbeRunnerResult(
        runtime_status="completed",
        shared_capture=shared_capture,
        interaction_capture=interaction_capture,
        diagnostic_codes=["runner_ok", "runner_ok"],
        warnings=["slow", "slow"],
    )
    record = BrowserProbeArtifactRecord(
        artifact_id="artifact-001",
        gate_run_id="gate-run-001",
        check_name="playwright_smoke",
        artifact_type="playwright_trace",
        artifact_ref="trace.zip",
        anchor_refs=["page:landing", "page:landing"],
        capture_status="captured",
        captured_at="2026-04-21T00:00:00Z",
    )
    receipt = BrowserProbeExecutionReceipt(
        check_name="playwright_smoke",
        started_at="2026-04-21T00:00:00Z",
        finished_at="2026-04-21T00:01:00Z",
        runtime_status="completed",
        artifact_ids=["artifact-001", "artifact-001"],
        anchor_refs=["page:landing", "page:landing"],
        requirement_linkage=["req:smoke", "req:smoke"],
        classification_candidate="pass",
        remediation_hints=["rerun", "rerun"],
        blocking_reason_codes=["runtime_missing", "runtime_missing"],
        advisory_reason_codes=["slow", "slow"],
    )
    bundle = BrowserQualityBundleMaterializationInput(
        bundle_id="bundle-001",
        gate_run_id="gate-run-001",
        apply_result_id="apply-result-001",
        solution_snapshot_id="solution-001",
        spec_dir="specs/001-auth",
        attachment_scope_ref="scope://001-auth",
        managed_frontend_target="managed/frontend",
        source_artifact_ref="artifacts/bundle.json",
        readiness_subject_id="001-auth",
        component_library_packages=["primevue", "primevue", "@primeuix/themes"],
        page_schema_ids=["dashboard", "dashboard", "search"],
        playwright_trace_refs=["trace.zip", "trace.zip"],
        screenshot_refs=["nav.png", "nav.png"],
        check_receipts=[receipt],
        smoke_verdict="pass",
        visual_verdict="pass",
        a11y_verdict="pass",
        interaction_anti_pattern_verdict="pass",
        overall_gate_status="passed_with_advisories",
        requirement_linkage=["req:smoke", "req:smoke"],
        blocking_reason_codes=["runtime_missing", "runtime_missing"],
        advisory_reason_codes=["slow", "slow"],
        generated_at="2026-04-21T00:02:00Z",
    )

    assert context.component_library_packages == ["primevue", "@primeuix/themes"]
    assert context.page_schema_ids == ["dashboard", "search"]
    assert context.required_probe_set == ["playwright_smoke", "basic_a11y"]
    assert session.warnings == ["probe-delayed"]
    assert shared_capture.anchor_refs == ["page:landing"]
    assert shared_capture.diagnostic_codes == ["nav_ok"]
    assert interaction_capture.artifact_refs == ["interaction.json"]
    assert interaction_capture.blocking_reason_codes == ["interaction_blocked"]
    assert interaction_capture.anchor_refs == ["interaction:primary"]
    assert runner_result.diagnostic_codes == ["runner_ok"]
    assert runner_result.warnings == ["slow"]
    assert record.anchor_refs == ["page:landing"]
    assert receipt.artifact_ids == ["artifact-001"]
    assert receipt.anchor_refs == ["page:landing"]
    assert receipt.requirement_linkage == ["req:smoke"]
    assert receipt.remediation_hints == ["rerun"]
    assert receipt.blocking_reason_codes == ["runtime_missing"]
    assert receipt.advisory_reason_codes == ["slow"]
    assert bundle.component_library_packages == ["primevue", "@primeuix/themes"]
    assert bundle.page_schema_ids == ["dashboard", "search"]
    assert bundle.playwright_trace_refs == ["trace.zip"]
    assert bundle.screenshot_refs == ["nav.png"]
    assert bundle.requirement_linkage == ["req:smoke"]
    assert bundle.blocking_reason_codes == ["runtime_missing"]
    assert bundle.advisory_reason_codes == ["slow"]


def test_materialize_visual_and_a11y_receipts_deduplicates_remediation_lists(
    tmp_path: Path,
) -> None:
    context = _context()

    def _runner(*, artifact_root: Path, execution_context, generated_at: str):
        trace_path = artifact_root / "shared-runtime" / "playwright-trace.zip"
        screenshot_path = artifact_root / "shared-runtime" / "navigation-screenshot.png"
        interaction_path = artifact_root / "interaction" / "interaction-snapshot.json"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        interaction_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text('{"trace":"ok"}\n', encoding="utf-8")
        screenshot_path.write_bytes(b"png")
        interaction_path.write_text('{"interaction":"ok"}\n', encoding="utf-8")
        return BrowserGateProbeRunnerResult(
            runtime_status="completed",
            shared_capture=BrowserGateSharedRuntimeCapture(
                gate_run_id=execution_context.gate_run_id,
                trace_artifact_ref=str(trace_path.relative_to(tmp_path)),
                navigation_screenshot_ref=str(screenshot_path.relative_to(tmp_path)),
                capture_status="captured",
                final_url="http://localhost:4173/",
                anchor_refs=["page:landing"],
                diagnostic_codes=[],
            ),
            interaction_capture=BrowserGateInteractionProbeCapture(
                gate_run_id=execution_context.gate_run_id,
                interaction_probe_id="primary-action",
                artifact_refs=[str(interaction_path.relative_to(tmp_path))],
                capture_status="captured",
                classification_candidate="pass",
                blocking_reason_codes=[],
                anchor_refs=["interaction:primary-action"],
            ),
            diagnostic_codes=[],
            warnings=[],
        )

    failing_artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=[
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-fail-1",
                target_id="page:user-create",
                surface_id="page:user-create",
                outcome="issue",
                report_type="coverage-report",
                severity="error",
                location_anchor="specs",
                quality_hint="fixture fail",
                changed_scope_explanation="runtime fixture",
            ),
            FrontendVisualA11yEvidenceEvaluation(
                evaluation_id="001-auth-fail-2",
                target_id="page:user-create",
                surface_id="page:user-create",
                outcome="issue",
                report_type="coverage-report",
                severity="error",
                location_anchor="specs",
                quality_hint="fixture fail",
                changed_scope_explanation="runtime fixture",
            ),
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-14T15:00:00Z",
    )

    _session, _records, receipts, _bundle = materialize_browser_gate_probe_runtime(
        root=tmp_path,
        context=context,
        apply_artifact_path=".ai-sdlc/memory/frontend-managed-delivery/latest.yaml",
        visual_a11y_evidence_artifact=failing_artifact,
        generated_at="2026-04-14T15:05:00Z",
        probe_runner=_runner,
        execute_probe=True,
    )

    visual_receipt = next(item for item in receipts if item.check_name == "visual_expectation")
    a11y_receipt = next(item for item in receipts if item.check_name == "basic_a11y")
    assert visual_receipt.remediation_hints == [
        "review frontend visual / a11y issue findings"
    ]
    assert visual_receipt.blocking_reason_codes == ["visual_a11y_quality_blocker"]
    assert a11y_receipt.remediation_hints == visual_receipt.remediation_hints
    assert a11y_receipt.blocking_reason_codes == visual_receipt.blocking_reason_codes


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_maps_goto_failure_to_navigation_failed(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop() {},
          },
          async newPage() {
            return {
              async goto() {
                throw new Error("net::ERR_CONNECTION_REFUSED");
              },
              url() {
                return "http://127.0.0.1:4173/";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "http://127.0.0.1:4173/",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["runtime_status"] == "failed_transient"
    assert result["diagnostic_codes"] == ["navigation_failed"]
    assert result["shared_capture"]["diagnostic_codes"] == ["navigation_failed"]
    assert result["interaction_capture"]["blocking_reason_codes"] == ["navigation_failed"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_persists_delivery_context_in_interaction_snapshot(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
import { mkdir, writeFile } from "node:fs/promises";

let evaluateCallCount = 0;

export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop({ path }) {
              await mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
              await writeFile(path, "trace");
            },
          },
          async newPage() {
            return {
              async goto() {},
              url() {
                return "http://127.0.0.1:4173/";
              },
              async screenshot({ path }) {
                await writeFile(path, "png");
              },
              async evaluate() {
                evaluateCallCount += 1;
                if (evaluateCallCount === 1) {
                  return { bodyText: "ok", elementCount: 1 };
                }
                return {
                  interaction_probe_id: "primary-action",
                  anchor_refs: ["interaction:primary-action"],
                  classification_candidate: "pass",
                  blocking_reason_codes: [],
                  detail: "clicked-primary-candidate",
                };
              },
              async title() {
                return "Demo";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "http://127.0.0.1:4173/",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "provider_theme_adapter_id": "public-primevue-theme-bridge",
        "provider_runtime_adapter_carrier_mode": "target-project-adapter-layer",
        "provider_runtime_adapter_delivery_state": "scaffolded",
        "provider_runtime_adapter_evidence_state": "missing",
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
        "effective_provider": "public-primevue",
        "effective_style_pack": "modern-saas",
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["runtime_status"] == "completed"
    interaction_snapshot = json.loads(
        (artifact_root / "interaction" / "interaction-snapshot.json").read_text(
            encoding="utf-8"
        )
    )
    assert interaction_snapshot["delivery_entry_id"] == "vue3-public-primevue"
    assert interaction_snapshot["component_library_packages"] == [
        "primevue",
        "@primeuix/themes",
    ]
    assert (
        interaction_snapshot["provider_theme_adapter_id"]
        == "public-primevue-theme-bridge"
    )
    assert (
        interaction_snapshot["provider_runtime_adapter_carrier_mode"]
        == "target-project-adapter-layer"
    )
    assert interaction_snapshot["provider_runtime_adapter_delivery_state"] == "scaffolded"
    assert interaction_snapshot["provider_runtime_adapter_evidence_state"] == "missing"
    assert interaction_snapshot["page_schema_ids"] == [
        "dashboard-workspace",
        "search-list-workspace",
    ]


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_can_navigate_generated_index_html(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
import { mkdir, readFile, writeFile } from "node:fs/promises";

let currentUrl = "";
let html = "";

export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop({ path }) {
              await mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
              await writeFile(path, "trace");
            },
          },
          async newPage() {
            return {
              async goto(targetUrl) {
                currentUrl = targetUrl;
                html = await readFile(new URL(targetUrl), "utf8");
              },
              url() {
                return currentUrl;
              },
              async screenshot({ path }) {
                await writeFile(path, "png");
              },
              async evaluate() {
                if (!html) {
                  return { bodyText: "", elementCount: 0 };
                }
                const packageMatches = [...html.matchAll(/<li class="package-item">([^<]+)<\\/li>/g)].map((match) => match[1]);
                const pageMatches = [...html.matchAll(/<li class="page-item">([^<]+)<\\/li>/g)].map((match) => match[1]);
                const deliveryEntryMatch = html.match(/<p class="entry-eyebrow">([^<]+)<\\/p>/);
                const validationMissingCodes = [];
                if (!deliveryEntryMatch || deliveryEntryMatch[1] !== "vue3-public-primevue") {
                  validationMissingCodes.push("delivery_entry_render_mismatch");
                }
                for (const pkg of ["primevue", "@primeuix/themes"]) {
                  if (!packageMatches.includes(pkg)) {
                    validationMissingCodes.push("component_library_package_render_mismatch");
                    break;
                  }
                }
                for (const schemaId of ["dashboard-workspace", "search-list-workspace"]) {
                  if (!pageMatches.includes(schemaId)) {
                    validationMissingCodes.push("page_schema_render_mismatch");
                    break;
                  }
                }
                return validationMissingCodes.length === 0
                  ? {
                      interaction_probe_id: "primary-action",
                      anchor_refs: ["interaction:primary-action"],
                      classification_candidate: "pass",
                      blocking_reason_codes: [],
                      rendered_delivery_entry_id: deliveryEntryMatch ? deliveryEntryMatch[1] : "",
                      rendered_component_library_packages: packageMatches,
                      rendered_page_schema_ids: pageMatches,
                      delivery_context_validation_status: "passed",
                      detail: "clicked-primary-candidate",
                    }
                  : {
                      interaction_probe_id: "primary-action",
                      anchor_refs: ["interaction:primary-action"],
                      classification_candidate: "actual_quality_blocker",
                      blocking_reason_codes: validationMissingCodes,
                      rendered_delivery_entry_id: deliveryEntryMatch ? deliveryEntryMatch[1] : "",
                      rendered_component_library_packages: packageMatches,
                      rendered_page_schema_ids: pageMatches,
                      delivery_context_validation_status: "failed",
                      detail: "delivery-context-render-mismatch",
                    };
              },
              async title() {
                const match = html.match(/<title>([^<]+)<\\/title>/);
                return match ? match[1] : "";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    managed_root = tmp_path / "managed" / "frontend"
    managed_root.mkdir(parents=True)
    (managed_root / "index.html").write_text(
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>frontend-browser-entry</title>
  </head>
  <body>
    <main id="frontend-browser-entry">
      <p class="entry-eyebrow">vue3-public-primevue</p>
      <ul>
        <li class="package-item">primevue</li>
        <li class="package-item">@primeuix/themes</li>
      </ul>
      <ul>
        <li class="page-item">dashboard-workspace</li>
        <li class="page-item">search-list-workspace</li>
      </ul>
      <button type="button">Open</button>
    </main>
  </body>
</html>
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "managed/frontend/index.html",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "provider_theme_adapter_id": "public-primevue-theme-bridge",
        "provider_runtime_adapter_carrier_mode": "target-project-adapter-layer",
        "provider_runtime_adapter_delivery_state": "scaffolded",
        "provider_runtime_adapter_evidence_state": "missing",
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["runtime_status"] == "completed"
    assert result["shared_capture"]["capture_status"] == "captured"
    assert result["interaction_capture"]["classification_candidate"] == "pass"
    interaction_snapshot = json.loads(
        (artifact_root / "interaction" / "interaction-snapshot.json").read_text(
            encoding="utf-8"
        )
    )
    assert interaction_snapshot["delivery_context_validation_status"] == "passed"
    assert interaction_snapshot["rendered_component_library_packages"] == [
        "primevue",
        "@primeuix/themes",
    ]
    assert interaction_snapshot["rendered_page_schema_ids"] == [
        "dashboard-workspace",
        "search-list-workspace",
    ]


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_blocks_when_rendered_delivery_context_mismatches(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
import { mkdir, readFile, writeFile } from "node:fs/promises";

let currentUrl = "";
let html = "";
let evaluateCallCount = 0;

export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop({ path }) {
              await mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
              await writeFile(path, "trace");
            },
          },
          async newPage() {
            return {
              async goto(targetUrl) {
                currentUrl = targetUrl;
                html = await readFile(new URL(targetUrl), "utf8");
              },
              url() {
                return currentUrl;
              },
              async screenshot({ path }) {
                await writeFile(path, "png");
              },
              async evaluate() {
                evaluateCallCount += 1;
                if (evaluateCallCount === 1) {
                  return {
                    bodyText: html.replace(/<[^>]+>/g, " ").trim(),
                    elementCount: 3,
                  };
                }
                const packageMatches = [...html.matchAll(/<li class="package-item">([^<]+)<\\/li>/g)].map((match) => match[1]);
                const pageMatches = [...html.matchAll(/<li class="page-item">([^<]+)<\\/li>/g)].map((match) => match[1]);
                return {
                  interaction_probe_id: "primary-action",
                  anchor_refs: ["interaction:primary-action"],
                  classification_candidate: "actual_quality_blocker",
                  blocking_reason_codes: [
                    ...(!packageMatches.includes("@primeuix/themes") ? ["component_library_package_render_mismatch"] : []),
                    ...(!pageMatches.includes("search-list-workspace") ? ["page_schema_render_mismatch"] : []),
                  ],
                  rendered_component_library_packages: packageMatches,
                  rendered_page_schema_ids: pageMatches,
                  delivery_context_validation_status: "failed",
                  detail: "delivery-context-render-mismatch",
                };
              },
              async title() {
                return "frontend-browser-entry";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    managed_root = tmp_path / "managed" / "frontend"
    managed_root.mkdir(parents=True)
    (managed_root / "index.html").write_text(
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>frontend-browser-entry</title>
  </head>
  <body>
    <main id="frontend-browser-entry">
      <p class="entry-eyebrow">vue3-public-primevue</p>
      <ul>
        <li class="package-item">primevue</li>
      </ul>
      <ul>
        <li class="page-item">dashboard-workspace</li>
      </ul>
      <button type="button">Open</button>
    </main>
  </body>
</html>
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "managed/frontend/index.html",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "provider_theme_adapter_id": "public-primevue-theme-bridge",
        "provider_runtime_adapter_carrier_mode": "target-project-adapter-layer",
        "provider_runtime_adapter_delivery_state": "scaffolded",
        "provider_runtime_adapter_evidence_state": "missing",
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["runtime_status"] == "completed"
    assert result["interaction_capture"]["classification_candidate"] == "actual_quality_blocker"
    assert "component_library_package_render_mismatch" in result["interaction_capture"][
        "blocking_reason_codes"
    ]
    assert "page_schema_render_mismatch" in result["interaction_capture"][
        "blocking_reason_codes"
    ]


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_reads_visual_baseline_metadata_as_yaml(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
import { mkdir, writeFile } from "node:fs/promises";

export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop({ path }) {
              await mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
              await writeFile(path, "trace");
            },
          },
          async newPage() {
            return {
              async goto() {},
              url() {
                return "http://127.0.0.1:4173/";
              },
              async screenshot({ path }) {
                await writeFile(path, "current");
              },
              async evaluate() {
                return {
                  interaction_probe_id: "primary-action",
                  anchor_refs: ["interaction:primary-action"],
                  classification_candidate: "pass",
                  blocking_reason_codes: [],
                  rendered_delivery_entry_id: "vue3-public-primevue",
                  rendered_component_library_packages: ["primevue", "@primeuix/themes"],
                  rendered_page_schema_ids: ["dashboard-workspace", "search-list-workspace"],
                  delivery_context_validation_status: "passed",
                  detail: "clicked-primary-candidate",
                };
              },
              async title() {
                return "frontend-browser-entry";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    fake_pngjs_dir = tmp_path / "node_modules" / "pngjs"
    fake_pngjs_dir.mkdir()
    (fake_pngjs_dir / "index.js").write_text(
        """
class PNG {
  constructor({ width, height }) {
    this.width = width;
    this.height = height;
    this.data = Buffer.from([0, 0, 0, 0]);
  }
}
PNG.sync = {
  read() {
    return { width: 1, height: 1, data: Buffer.from([0, 0, 0, 0]) };
  },
  write() {
    return Buffer.from("diff");
  },
};
module.exports = { PNG };
""".strip(),
        encoding="utf-8",
    )
    fake_pixelmatch_dir = tmp_path / "node_modules" / "pixelmatch"
    fake_pixelmatch_dir.mkdir()
    (fake_pixelmatch_dir / "index.js").write_text(
        "module.exports = function pixelmatch() { return 0; };\n",
        encoding="utf-8",
    )
    fake_yaml_dir = tmp_path / "node_modules" / "yaml"
    fake_yaml_dir.mkdir()
    (fake_yaml_dir / "index.js").write_text(
        """
module.exports = {
  parse(raw) {
    if (!raw.includes('"threshold"')) {
      throw new Error("expected_yaml_parser_input");
    }
    return {
      matrix_id: "yaml-matrix",
      threshold: 0.42,
      critical_regions: [{ region_id: "overall" }],
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    baseline_root = (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "evidence"
        / "visual-regression"
        / "baselines"
        / "yaml-matrix"
    )
    baseline_root.mkdir(parents=True)
    (baseline_root / "baseline.png").write_text("baseline", encoding="utf-8")
    (baseline_root / "baseline.yaml").write_text(
        """
---
matrix_id: yaml-matrix
"threshold": 0.42
critical_regions:
  - region_id: overall
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "http://127.0.0.1:4173/",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
        "visual_regression_matrix_id": "yaml-matrix",
        "visual_regression_viewport_id": "desktop-1440",
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["visual_regression_capture"]["threshold"] == 0.42
    assert result["visual_regression_capture"]["verdict"] == "pass"


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_rejects_visual_threshold_above_one(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
import { mkdir, writeFile } from "node:fs/promises";

export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop({ path }) {
              await mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
              await writeFile(path, "trace");
            },
          },
          async newPage() {
            return {
              async goto() {},
              url() {
                return "http://127.0.0.1:4173/";
              },
              async screenshot({ path }) {
                await writeFile(path, "current");
              },
              async evaluate() {
                return {
                  interaction_probe_id: "primary-action",
                  anchor_refs: ["interaction:primary-action"],
                  classification_candidate: "pass",
                  blocking_reason_codes: [],
                  rendered_delivery_entry_id: "vue3-public-primevue",
                  rendered_component_library_packages: ["primevue", "@primeuix/themes"],
                  rendered_page_schema_ids: ["dashboard-workspace", "search-list-workspace"],
                  delivery_context_validation_status: "passed",
                  detail: "clicked-primary-candidate",
                };
              },
              async title() {
                return "frontend-browser-entry";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    baseline_root = (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "evidence"
        / "visual-regression"
        / "baselines"
        / "unsafe-threshold-matrix"
    )
    baseline_root.mkdir(parents=True)
    (baseline_root / "baseline.png").write_text("baseline", encoding="utf-8")
    (baseline_root / "baseline.yaml").write_text(
        """
matrix_id: unsafe-threshold-matrix
threshold: 1.01
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "http://127.0.0.1:4173/",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
        "visual_regression_matrix_id": "unsafe-threshold-matrix",
        "visual_regression_viewport_id": "desktop-1440",
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["visual_regression_capture"]["capture_status"] == "capture_failed"
    assert result["visual_regression_capture"]["change_summary"] == "baseline-threshold-invalid"
    assert result["visual_regression_capture"]["verdict"] == "recheck"


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_reports_visual_decode_failures(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    fake_playwright_dir = tmp_path / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
const { mkdir, writeFile } = require("node:fs/promises");

module.exports = {
  chromium: {
    async launch() {
      return {
        async newContext() {
          return {
            tracing: {
              async start() {},
              async stop({ path }) {
                await mkdir(require("node:path").dirname(path), { recursive: true });
                await writeFile(path, "trace");
              },
            },
            async newPage() {
              return {
                async goto() {},
                url() {
                  return "http://127.0.0.1:4173/";
                },
                async screenshot({ path }) {
                  await writeFile(path, "not-a-png");
                },
                async evaluate() {
                  return {
                    interaction_probe_id: "primary-action",
                    anchor_refs: ["interaction:primary-action"],
                    classification_candidate: "pass",
                    blocking_reason_codes: [],
                    rendered_delivery_entry_id: "vue3-public-primevue",
                    rendered_component_library_packages: ["primevue", "@primeuix/themes"],
                    rendered_page_schema_ids: ["dashboard-workspace", "search-list-workspace"],
                    delivery_context_validation_status: "passed",
                    detail: "clicked-primary-candidate",
                  };
                },
                async title() {
                  return "frontend-browser-entry";
                },
                async close() {},
              };
            },
            async close() {},
          };
        },
        async close() {},
      };
    },
  },
};
""".strip(),
        encoding="utf-8",
    )
    fake_pngjs_dir = tmp_path / "node_modules" / "pngjs"
    fake_pngjs_dir.mkdir()
    (fake_pngjs_dir / "index.js").write_text(
        """
class PNG {}
PNG.sync = {
  read() {
    throw new Error("decode failed");
  },
  write() {
    return Buffer.from("diff");
  },
};
module.exports = { PNG };
""".strip(),
        encoding="utf-8",
    )
    fake_pixelmatch_dir = tmp_path / "node_modules" / "pixelmatch"
    fake_pixelmatch_dir.mkdir()
    (fake_pixelmatch_dir / "index.js").write_text(
        "module.exports = function pixelmatch() { return 0; };\n",
        encoding="utf-8",
    )
    baseline_root = (
        tmp_path
        / "governance"
        / "frontend"
        / "quality-platform"
        / "evidence"
        / "visual-regression"
        / "baselines"
        / "decode-failure-matrix"
    )
    baseline_root.mkdir(parents=True)
    (baseline_root / "baseline.png").write_text("not-a-png", encoding="utf-8")
    (baseline_root / "baseline.yaml").write_text(
        "matrix_id: decode-failure-matrix\nthreshold: 0.03\n",
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "http://127.0.0.1:4173/",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
        "visual_regression_matrix_id": "decode-failure-matrix",
        "visual_regression_viewport_id": "desktop-1440",
        "package_manager": "pnpm",
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    capture = result["visual_regression_capture"]
    assert capture["capture_status"] == "capture_failed"
    assert capture["change_summary"] == "visual-regression-image-decode-failed"
    assert capture["verdict"] == "recheck"
    assert result["runtime_status"] == "completed"
    bootstrap_payload = json.loads(
        (artifact_root / "bootstrap" / "bootstrap-receipt.yaml").read_text(
            encoding="utf-8"
        )
    )
    assert bootstrap_payload["package_manager"] == "pnpm"
    assert bootstrap_payload["lockfile_ref"] == "managed/frontend/pnpm-lock.yaml"


@pytest.mark.skipif(shutil.which("node") is None, reason="node runtime unavailable")
def test_frontend_browser_gate_probe_runner_resolves_playwright_from_managed_frontend_node_modules(
    tmp_path: Path,
) -> None:
    source_script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "frontend_browser_gate_probe_runner.mjs"
    )
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    script_path = script_dir / "frontend_browser_gate_probe_runner.mjs"
    script_path.write_text(source_script_path.read_text(encoding="utf-8"), encoding="utf-8")
    managed_root = tmp_path / "managed" / "frontend"
    fake_playwright_dir = managed_root / "node_modules" / "playwright"
    fake_playwright_dir.mkdir(parents=True)
    (fake_playwright_dir / "package.json").write_text(
        json.dumps({"name": "playwright", "type": "module"}),
        encoding="utf-8",
    )
    (fake_playwright_dir / "index.js").write_text(
        """
import { mkdir, readFile, writeFile } from "node:fs/promises";

let currentUrl = "";
let html = "";

export const chromium = {
  async launch() {
    return {
      async newContext() {
        return {
          tracing: {
            async start() {},
            async stop({ path }) {
              await mkdir(new URL(".", `file://${path}`).pathname, { recursive: true }).catch(() => {});
              await writeFile(path, "trace");
            },
          },
          async newPage() {
            return {
              async goto(targetUrl) {
                currentUrl = targetUrl;
                html = await readFile(new URL(targetUrl), "utf8");
              },
              url() {
                return currentUrl;
              },
              async screenshot({ path }) {
                await writeFile(path, "png");
              },
              async evaluate() {
                if (!html) {
                  return { bodyText: "", elementCount: 0 };
                }
                return {
                  interaction_probe_id: "primary-action",
                  anchor_refs: ["interaction:primary-action"],
                  classification_candidate: "pass",
                  blocking_reason_codes: [],
                  rendered_delivery_entry_id: "vue3-public-primevue",
                  rendered_component_library_packages: ["primevue", "@primeuix/themes"],
                  rendered_page_schema_ids: ["dashboard-workspace", "search-list-workspace"],
                  delivery_context_validation_status: "passed",
                  detail: "clicked-primary-candidate",
                };
              },
              async title() {
                return "frontend-browser-entry";
              },
              async close() {},
            };
          },
          async close() {},
        };
      },
      async close() {},
    };
  },
};
""".strip(),
        encoding="utf-8",
    )
    managed_root.mkdir(parents=True, exist_ok=True)
    (managed_root / "index.html").write_text(
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>frontend-browser-entry</title>
  </head>
  <body>
    <main id="frontend-browser-entry">
      <p class="entry-eyebrow">vue3-public-primevue</p>
      <ul>
        <li class="package-item">primevue</li>
        <li class="package-item">@primeuix/themes</li>
      </ul>
      <ul>
        <li class="page-item">dashboard-workspace</li>
        <li class="page-item">search-list-workspace</li>
      </ul>
      <button type="button">Open</button>
    </main>
  </body>
</html>
""".strip(),
        encoding="utf-8",
    )
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    payload = {
        "artifact_root": str(artifact_root),
        "artifact_root_ref": "artifacts",
        "browser_entry_ref": "managed/frontend/index.html",
        "managed_frontend_target": "managed/frontend",
        "gate_run_id": "gate-run-001",
        "generated_at": "2026-04-18T11:00:00Z",
        "delivery_entry_id": "vue3-public-primevue",
        "component_library_packages": ["primevue", "@primeuix/themes"],
        "provider_theme_adapter_id": "public-primevue-theme-bridge",
        "provider_runtime_adapter_carrier_mode": "target-project-adapter-layer",
        "provider_runtime_adapter_delivery_state": "scaffolded",
        "provider_runtime_adapter_evidence_state": "missing",
        "page_schema_ids": ["dashboard-workspace", "search-list-workspace"],
    }

    completed = subprocess.run(
        ["node", str(script_path)],
        cwd=tmp_path,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
    )

    result = json.loads(completed.stdout)
    assert result["runtime_status"] == "completed"
    assert result["shared_capture"]["capture_status"] == "captured"
    assert result["interaction_capture"]["classification_candidate"] == "pass"
