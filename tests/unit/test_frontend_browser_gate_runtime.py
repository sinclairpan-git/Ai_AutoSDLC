"""Unit tests for real frontend browser gate probe runtime."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.frontend_browser_gate_runtime import (
    BrowserGateInteractionProbeCapture,
    BrowserGateProbeRunnerResult,
    BrowserGateSharedRuntimeCapture,
    build_browser_quality_gate_execution_context,
    materialize_browser_gate_probe_runtime,
)
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
)
from ai_sdlc.models.frontend_browser_gate import BrowserQualityGateExecutionContext
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
        required_probe_set=[
            "playwright_smoke",
            "visual_expectation",
            "basic_a11y",
            "interaction_anti_pattern_checks",
        ],
        browser_entry_ref="managed/frontend/index.html",
        source_linkage_refs={"apply_result_status": "apply_succeeded_pending_browser_gate"},
    )


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
            },
        },
        solution_snapshot=build_mvp_solution_snapshot(),
        gate_run_id="gate-run-ctx",
    )

    assert context.browser_entry_ref == "managed/frontend/index.html"


def test_materialize_browser_gate_probe_runtime_executes_real_runner_and_captures_artifacts(
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
    smoke_receipt = next(item for item in receipts if item.check_name == "playwright_smoke")
    interaction_receipt = next(
        item for item in receipts if item.check_name == "interaction_anti_pattern_checks"
    )
    assert smoke_receipt.classification_candidate == "pass"
    assert interaction_receipt.classification_candidate == "pass"
    assert any(record.artifact_type == "playwright_trace" for record in records)
    assert any(record.artifact_type == "interaction_snapshot" for record in records)


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
