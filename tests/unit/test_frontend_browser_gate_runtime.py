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
        delivery_entry_id="vue3-public-primevue",
        component_library_packages=["primevue", "@primeuix/themes"],
        provider_theme_adapter_id="public-primevue-theme-bridge",
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
        delivery_entry_id="vue3-public-primevue",
        component_library_packages=["primevue", "@primeuix/themes"],
        provider_theme_adapter_id="public-primevue-theme-bridge",
    )

    assert context.browser_entry_ref == "managed/frontend/index.html"
    assert context.delivery_entry_id == "vue3-public-primevue"
    assert context.component_library_packages == ["primevue", "@primeuix/themes"]
    assert context.provider_theme_adapter_id == "public-primevue-theme-bridge"


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
    assert bundle.delivery_entry_id == "vue3-public-primevue"
    assert bundle.component_library_packages == ["primevue", "@primeuix/themes"]
    assert bundle.provider_theme_adapter_id == "public-primevue-theme-bridge"


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
                return {
                  bodyText: html.replace(/<[^>]+>/g, " ").trim(),
                  elementCount: packageMatches.length + pageMatches.length + 1,
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
      <ul>
        <li class="package-item">primevue</li>
        <li class="package-item">@primeuix/themes</li>
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
