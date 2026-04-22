"""Unit tests for CLI status table helpers."""

from __future__ import annotations

from types import SimpleNamespace

from rich.table import Table

import ai_sdlc.cli.commands as commands_module
from ai_sdlc.models.state import Checkpoint, CompletedStage, FeatureInfo


def test_add_truth_ledger_rows_deduplicates_release_targets() -> None:
    table = Table(title="AI-SDLC Status")
    table.add_column("Property")
    table.add_column("Value")

    commands_module._add_truth_ledger_rows(
        table,
        {
            "state": "blocked",
            "snapshot_state": "fresh",
            "detail": "ledger blocked",
            "release_targets": [
                "frontend-mainline-delivery",
                "frontend-mainline-delivery",
                "runtime-adapter",
            ],
            "release_capabilities": [],
        },
    )

    with commands_module.console.capture() as capture:
        commands_module.console.print(table)

    output = capture.get()
    assert "frontend-mainline-delivery, runtime-adapter" in output
    assert "frontend-mainline-delivery, frontend-mainline-delivery" not in output


def test_add_truth_ledger_rows_collects_later_frontend_truth_items() -> None:
    table = Table(title="AI-SDLC Status")
    table.add_column("Property")
    table.add_column("Value")

    commands_module._add_truth_ledger_rows(
        table,
        {
            "state": "blocked",
            "snapshot_state": "fresh",
            "detail": "ledger blocked",
            "release_targets": [],
            "release_capabilities": [
                {},
                {"frontend_delivery_status": {}},
                {"frontend_inheritance_status": {}},
                {
                    "capability_id": "frontend-mainline-delivery",
                    "audit_state": "blocked",
                    "frontend_delivery_status": {
                        "provider_id": "public-primevue",
                        "package_names": "primevue,@primeuix/themes",
                        "runtime_delivery_state": "scaffolded",
                        "download": "installed",
                        "integration": "integrated",
                        "browser_gate": "pending",
                        "delivery": "apply_succeeded_pending_browser_gate",
                    },
                    "frontend_inheritance_status": {
                        "generation": "inherited",
                        "quality": "blocked",
                    },
                },
            ],
        },
    )

    with commands_module.console.capture() as capture:
        commands_module.console.print(table)

    output = capture.get()
    assert "selected provider public-primevue" in output
    assert "codegen inherited; frontend tests blocked" in output


def test_add_guard_rows_deduplicates_reason_codes() -> None:
    table = Table(title="AI-SDLC Status")
    table.add_column("Property")
    table.add_column("Value")

    commands_module._add_guard_rows(
        table,
        title="Formal Artifact Target",
        detail_title="Formal Artifact Target Detail",
        reasons_title="Formal Artifact Target Reasons",
        surface={
            "state": "blocked",
            "detail": "",
            "reason_codes": [
                "misplaced_formal_artifact_detected",
                "misplaced_formal_artifact_detected",
                "missing_formal_doc",
            ],
        },
    )

    with commands_module.console.capture() as capture:
        commands_module.console.print(table)

    output = capture.get()
    assert output.count("misplaced_formal_artifact_detected") == 1
    assert output.count("missing_formal_doc") == 1
    assert (
        "misplaced_formal_artifact_detected, misplaced_formal_artifact_detected"
        not in output
    )


def test_resolve_guard_surface_deduplicates_evaluator_reason_codes() -> None:
    surface = commands_module._resolve_guard_surface(
        None,
        evaluator=lambda: SimpleNamespace(
            state="blocked",
            detail="guard detail",
            reason_codes=[
                "misplaced_formal_artifact_detected",
                "misplaced_formal_artifact_detected",
                "missing_formal_doc",
            ],
        ),
    )

    assert surface == {
        "state": "blocked",
        "detail": "guard detail",
        "reason_codes": [
            "misplaced_formal_artifact_detected",
            "missing_formal_doc",
        ],
    }


def test_resolve_guard_surface_deduplicates_provided_reason_codes() -> None:
    surface = commands_module._resolve_guard_surface(
        {
            "state": "blocked",
            "detail": "guard detail",
            "reason_codes": [
                "misplaced_formal_artifact_detected",
                "misplaced_formal_artifact_detected",
                "missing_formal_doc",
            ],
        },
        evaluator=lambda: SimpleNamespace(
            state="ready",
            detail="should not be used",
            reason_codes=[],
        ),
    )

    assert surface == {
        "state": "blocked",
        "detail": "guard detail",
        "reason_codes": [
            "misplaced_formal_artifact_detected",
            "missing_formal_doc",
        ],
    }


def test_print_reconcile_guidance_deduplicates_detected_files() -> None:
    hint = SimpleNamespace(
        layout="legacy_root",
        detected_files=[
            "legacy/a.md",
            "legacy/a.md",
            "legacy/b.md",
        ],
        checkpoint_stage="missing",
        checkpoint_feature_id="001-wi",
        current_stage="review",
        spec_dir="specs/001-wi",
        feature_id="001-wi",
        reason="legacy artifacts detected",
    )

    with commands_module.console.capture() as capture:
        commands_module._print_reconcile_guidance(
            hint,
            current_command="status",
            blocking=True,
        )

    output = capture.get()
    assert "legacy/a.md, legacy/b.md" in output
    assert "legacy/a.md, legacy/a.md" not in output


def test_add_active_work_item_status_rows_deduplicates_active_files(tmp_path) -> None:
    table = Table(title="AI-SDLC Status")
    table.add_column("Property")
    table.add_column("Value")

    original_load_execution_plan = commands_module.load_execution_plan
    original_load_runtime_state = commands_module.load_runtime_state
    original_load_working_set = commands_module.load_working_set
    original_load_latest_summary = commands_module.load_latest_summary
    original_load_latest_reviewer_decision = commands_module.load_latest_reviewer_decision
    original_load_resume_point = commands_module.load_resume_point
    original_load_execution_path = commands_module.load_execution_path
    original_load_parallel_coordination_artifact = (
        commands_module.load_parallel_coordination_artifact
    )

    try:
        commands_module.load_execution_plan = lambda *_args, **_kwargs: None
        commands_module.load_runtime_state = lambda *_args, **_kwargs: None
        commands_module.load_working_set = lambda *_args, **_kwargs: SimpleNamespace(
            active_files=[
                "src/app.ts",
                "src/app.ts",
                "tests/app.test.ts",
            ]
        )
        commands_module.load_latest_summary = lambda *_args, **_kwargs: None
        commands_module.load_latest_reviewer_decision = lambda *_args, **_kwargs: None
        commands_module.load_resume_point = lambda *_args, **_kwargs: None
        commands_module.load_execution_path = lambda *_args, **_kwargs: None
        commands_module.load_parallel_coordination_artifact = (
            lambda *_args, **_kwargs: None
        )

        commands_module._add_active_work_item_status_rows(
            table,
            root=tmp_path,
            active_work_item="001-wi",
        )
    finally:
        commands_module.load_execution_plan = original_load_execution_plan
        commands_module.load_runtime_state = original_load_runtime_state
        commands_module.load_working_set = original_load_working_set
        commands_module.load_latest_summary = original_load_latest_summary
        commands_module.load_latest_reviewer_decision = (
            original_load_latest_reviewer_decision
        )
        commands_module.load_resume_point = original_load_resume_point
        commands_module.load_execution_path = original_load_execution_path
        commands_module.load_parallel_coordination_artifact = (
            original_load_parallel_coordination_artifact
        )

    with commands_module.console.capture() as capture:
        commands_module.console.print(table)

    output = capture.get()
    assert "src/app.ts, tests/app.test.ts" in output
    assert "src/app.ts, src/app.ts" not in output


def test_add_checkpoint_progress_rows_deduplicates_completed_stages() -> None:
    table = Table(title="AI-SDLC Status")
    table.add_column("Property")
    table.add_column("Value")

    checkpoint = Checkpoint(
        current_stage="verify",
        feature=FeatureInfo(
            id="001",
            spec_dir="specs/001-wi",
            design_branch="design/001-wi",
            feature_branch="feature/001-wi",
            current_branch="feature/001-wi",
        ),
        completed_stages=[
            CompletedStage(stage="clarify", completed_at="2026-04-22T00:00:00Z"),
            CompletedStage(stage="clarify", completed_at="2026-04-22T00:00:01Z"),
            CompletedStage(stage="plan", completed_at="2026-04-22T00:00:02Z"),
        ],
    )

    commands_module._add_checkpoint_progress_rows(
        table,
        checkpoint=checkpoint,
        resume_pack=None,
    )

    with commands_module.console.capture() as capture:
        commands_module.console.print(table)

    output = capture.get()
    assert "clarify, plan" in output
    assert "clarify, clarify" not in output


def test_add_checkpoint_progress_rows_hides_terminally_merged_binding() -> None:
    table = Table(title="AI-SDLC Status")
    table.add_column("Property")
    table.add_column("Value")

    checkpoint = Checkpoint(
        current_stage="close",
        feature=FeatureInfo(
            id="159-agent-adapter-canonical-consumption-proof-runtime-baseline",
            spec_dir="specs/159-agent-adapter-canonical-consumption-proof-runtime-baseline",
            design_branch="design/159-agent-adapter-canonical-consumption-proof-runtime-baseline-docs",
            feature_branch="feature/159-agent-adapter-canonical-consumption-proof-runtime-baseline-dev",
            current_branch="codex/159-agent-adapter-canonical-consumption-proof",
        ),
        linked_wi_id="159-agent-adapter-canonical-consumption-proof-runtime-baseline",
        completed_stages=[
            CompletedStage(stage="execute", completed_at="2026-04-22T00:00:00Z"),
            CompletedStage(stage="close", completed_at="2026-04-22T00:00:01Z"),
        ],
    )

    commands_module._add_checkpoint_progress_rows(
        table,
        checkpoint=checkpoint,
        resume_pack=None,
        show_active_binding=False,
        current_branch_override="main",
    )

    with commands_module.console.capture() as capture:
        commands_module.console.print(table)

    output = capture.get()
    assert "Feature ID" not in output
    assert "Linked WI ID" not in output
    assert "Current Branch" in output
    assert "main" in output
    assert "codex/159-agent-adapter-canonical-consumption-proof" not in output
