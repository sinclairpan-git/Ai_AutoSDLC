"""Unit tests for bounded telemetry display summaries."""

from __future__ import annotations

from ai_sdlc.telemetry.display import (
    summarize_capability_closure_focus_for_display,
    summarize_frontend_delivery_status_for_display,
    summarize_frontend_inheritance_status_for_display,
    summarize_guard_surface_for_display,
    summarize_next_action_for_display,
    summarize_status_surface_detail,
    summarize_truth_ledger_explain_for_display,
    summarize_truth_ledger_focus_for_display,
    summarize_truth_ledger_frontend_delivery_for_display,
    summarize_truth_ledger_frontend_inheritance_for_display,
    summarize_truth_ledger_next_steps_for_display,
    summarize_workitem_findings_for_display,
    summarize_workitem_reason_for_display,
)


def test_summarize_next_action_for_display_shortens_branch_disposition() -> None:
    action = (
        "decide whether codex/001-status-drift should be merged, deleted, or archived, "
        "then record that branch disposition in task-execution-log.md"
    )

    assert summarize_next_action_for_display(action) == (
        "decide codex/001-status-drift disposition; task-execution-log.md"
    )


def test_summarize_next_action_for_display_shortens_adapter_verify_rerun() -> None:
    action = (
        "verify adapter canonical consumption and rerun "
        "python -m ai_sdlc program truth audit"
    )

    assert summarize_next_action_for_display(action) == (
        "verify adapter canonical consumption; "
        "python -m ai_sdlc program truth audit"
    )


def test_summarize_workitem_reason_for_display_branch_lifecycle() -> None:
    reason = (
        "BLOCKER: branch lifecycle unresolved: codex/001-status-drift is associated "
        "with 001-wi, ahead of main by 1 commit(s), and branch disposition is unresolved"
    )

    assert summarize_workitem_reason_for_display(
        reason,
        source="branch_lifecycle",
    ) == "branch lifecycle unresolved: codex/001-status-drift; ahead of main by 1 commit(s)"


def test_summarize_workitem_reason_for_display_execute_authorization() -> None:
    reason = (
        "active work item has tasks.md, but repo truth has not entered execute; "
        "remain in review-to-decompose; current_stage=verify"
    )

    assert summarize_workitem_reason_for_display(
        reason,
        source="execute_authorization",
    ) == "execute not authorized; review-to-decompose; current_stage=verify"


def test_summarize_workitem_reason_for_display_program_truth() -> None:
    reason = (
        "capability_blocked: frontend-mainline-delivery (blocked) | explain: "
        "capability closure remains capability_open; close check is not satisfied"
    )

    assert summarize_workitem_reason_for_display(
        reason,
        source="program_truth",
    ) == "capability_blocked: frontend-mainline-delivery (blocked)"


def test_summarize_workitem_reason_for_display_backlog_breach_guard() -> None:
    reason = (
        "breach_detected_but_not_logged: referenced framework defect ids are "
        "missing from docs/framework-defect-backlog.zh-CN.md"
    )

    assert summarize_workitem_reason_for_display(
        reason,
        source="backlog_breach_guard",
    ) == "breach_detected_but_not_logged"


def test_summarize_workitem_reason_for_display_frontend_evidence_class() -> None:
    reason = "frontend_evidence_class_mirror_drift: mirror_missing"

    assert summarize_workitem_reason_for_display(
        reason,
        source="frontend_evidence_class",
    ) == "frontend_evidence_class_mirror_drift: mirror_missing"


def test_summarize_workitem_findings_for_display() -> None:
    assert summarize_workitem_findings_for_display(
        blocking_count=2,
        actionable_count=3,
    ) == "blocking=2, actionable=3"


def test_summarize_truth_ledger_focus_for_display() -> None:
    release_capabilities = [
        {"capability_id": "frontend-mainline-delivery", "audit_state": "blocked"},
        {"capability_id": "runtime-adapter", "audit_state": "ready"},
        {"capability_id": "docs-governance", "audit_state": "blocked"},
        {"capability_id": "extra-capability", "audit_state": "ready"},
    ]

    assert summarize_truth_ledger_focus_for_display(release_capabilities) == (
        "frontend-mainline-delivery (blocked), runtime-adapter (ready), "
        "docs-governance (blocked), ..."
    )


def test_summarize_truth_ledger_focus_for_display_deduplicates_repeated_capabilities() -> None:
    release_capabilities = [
        {"capability_id": "frontend-mainline-delivery", "audit_state": "blocked"},
        {"capability_id": "frontend-mainline-delivery", "audit_state": "blocked"},
        {"capability_id": "runtime-adapter", "audit_state": "ready"},
        {"capability_id": "runtime-adapter", "audit_state": "ready"},
        {"capability_id": "docs-governance", "audit_state": "blocked"},
        {"capability_id": "extra-capability", "audit_state": "ready"},
    ]

    assert summarize_truth_ledger_focus_for_display(release_capabilities) == (
        "frontend-mainline-delivery (blocked), runtime-adapter (ready), "
        "docs-governance (blocked), ..."
    )


def test_summarize_truth_ledger_explain_for_display() -> None:
    release_capabilities = [
        {"plain_language_blockers": ["browser gate evidence is still missing"]},
        {"plain_language_blockers": ["adapter canonical consumption is not verified"]},
    ]

    assert summarize_truth_ledger_explain_for_display(release_capabilities) == (
        "browser gate evidence is still missing; "
        "adapter canonical consumption is not verified"
    )


def test_summarize_truth_ledger_explain_for_display_deduplicates_repeated_items() -> None:
    release_capabilities = [
        {
            "plain_language_blockers": [
                "browser gate evidence is still missing",
                "browser gate evidence is still missing",
            ]
        },
        {
            "plain_language_blockers": [
                "browser gate evidence is still missing",
                "adapter canonical consumption is not verified",
            ]
        },
    ]

    assert summarize_truth_ledger_explain_for_display(release_capabilities) == (
        "browser gate evidence is still missing; "
        "adapter canonical consumption is not verified"
    )


def test_summarize_truth_ledger_explain_for_display_collects_later_unique_items() -> None:
    release_capabilities = [
        {"plain_language_blockers": ["browser gate evidence is still missing"]},
        {"plain_language_blockers": ["browser gate evidence is still missing"]},
        {"plain_language_blockers": ["browser gate evidence is still missing"]},
        {"plain_language_blockers": ["adapter canonical consumption is not verified"]},
    ]

    assert summarize_truth_ledger_explain_for_display(release_capabilities) == (
        "browser gate evidence is still missing; "
        "adapter canonical consumption is not verified"
    )


def test_summarize_truth_ledger_next_steps_for_display() -> None:
    release_capabilities = [
        {
            "recommended_next_steps": [
                "verify adapter canonical consumption and rerun "
                "python -m ai_sdlc program truth audit"
            ]
        },
        {
            "recommended_next_steps": [
                "decide whether codex/001-status-drift should be merged, deleted, "
                "or archived, then record that branch disposition in task-execution-log.md"
            ]
        },
    ]

    assert summarize_truth_ledger_next_steps_for_display(release_capabilities) == (
        "verify adapter canonical consumption; python -m ai_sdlc program truth audit; "
        "decide codex/001-status-drift disposition; task-execution-log.md"
    )


def test_summarize_truth_ledger_next_steps_for_display_deduplicates_repeated_items() -> None:
    release_capabilities = [
        {
            "recommended_next_steps": [
                "verify adapter canonical consumption and rerun "
                "python -m ai_sdlc program truth audit",
                "verify adapter canonical consumption and rerun "
                "python -m ai_sdlc program truth audit",
            ]
        },
        {
            "recommended_next_steps": [
                "decide whether codex/001-status-drift should be merged, deleted, "
                "or archived, then record that branch disposition in task-execution-log.md",
                "decide whether codex/001-status-drift should be merged, deleted, "
                "or archived, then record that branch disposition in task-execution-log.md",
            ]
        },
    ]

    assert summarize_truth_ledger_next_steps_for_display(release_capabilities) == (
        "verify adapter canonical consumption; python -m ai_sdlc program truth audit; "
        "decide codex/001-status-drift disposition; task-execution-log.md"
    )


def test_summarize_truth_ledger_next_steps_for_display_collects_later_unique_items() -> None:
    repeated_step = (
        "verify adapter canonical consumption and rerun "
        "python -m ai_sdlc program truth audit"
    )
    release_capabilities = [
        {"recommended_next_steps": [repeated_step]},
        {"recommended_next_steps": [repeated_step]},
        {"recommended_next_steps": [repeated_step]},
        {
            "recommended_next_steps": [
                "decide whether codex/001-status-drift should be merged, deleted, "
                "or archived, then record that branch disposition in task-execution-log.md"
            ]
        },
    ]

    assert summarize_truth_ledger_next_steps_for_display(release_capabilities) == (
        "verify adapter canonical consumption; python -m ai_sdlc program truth audit; "
        "decide codex/001-status-drift disposition; task-execution-log.md"
    )


def test_summarize_truth_ledger_frontend_delivery_for_display_omits_package_noise() -> None:
    release_capabilities = [
        {
            "frontend_delivery_status": {
                "provider_id": "public-primevue",
                "package_names": "primevue,@primeuix/themes",
                "runtime_delivery_state": "scaffolded",
                "download": "installed",
                "integration": "integrated",
                "browser_gate": "pending",
                "delivery": "apply_succeeded_pending_browser_gate",
            },
            "frontend_delivery_summary": (
                "provider=legacy | packages=legacy-ui | runtime=legacy | "
                "download=not downloaded | integration=not integrated | "
                "browser_gate=not started | delivery=not applied"
            ),
        }
    ]

    assert summarize_truth_ledger_frontend_delivery_for_display(release_capabilities) == (
        "selected provider public-primevue; packages primevue,@primeuix/themes; "
        "download downloaded; integration integrated; "
        "browser check waiting for evidence; "
        "delivery applied, waiting for browser gate"
    )


def test_summarize_truth_ledger_frontend_delivery_for_display_collects_later_unique_item() -> None:
    release_capabilities = [
        {},
        {"frontend_delivery_status": {}},
        {"frontend_delivery_summary": ""},
        {
            "frontend_delivery_status": {
                "provider_id": "public-primevue",
                "package_names": "primevue,@primeuix/themes",
                "runtime_delivery_state": "scaffolded",
                "download": "installed",
                "integration": "integrated",
                "browser_gate": "pending",
                "delivery": "apply_succeeded_pending_browser_gate",
            }
        },
    ]

    assert summarize_truth_ledger_frontend_delivery_for_display(release_capabilities) == (
        "selected provider public-primevue; packages primevue,@primeuix/themes; "
        "download downloaded; integration integrated; "
        "browser check waiting for evidence; "
        "delivery applied, waiting for browser gate"
    )


def test_summarize_frontend_delivery_status_for_display() -> None:
    status_surface = {
        "download": "installed",
        "integration": "integrated",
        "browser_gate": "pending",
        "delivery": "apply_succeeded_pending_browser_gate",
        "provider_id": "ignored",
        "package_names": "primevue,@primeuix/themes",
    }

    assert summarize_frontend_delivery_status_for_display(status_surface) == (
        "selected provider ignored; packages primevue,@primeuix/themes; "
        "download downloaded; integration integrated; "
        "browser check waiting for evidence; "
        "delivery applied, waiting for browser gate"
    )


def test_summarize_frontend_inheritance_status_for_display() -> None:
    status_surface = {
        "generation": "inherited",
        "quality": "blocked",
    }

    assert summarize_frontend_inheritance_status_for_display(status_surface) == (
        "codegen inherited; frontend tests blocked"
    )


def test_summarize_frontend_inheritance_status_for_display_unknown() -> None:
    status_surface = {
        "generation": "unknown",
        "quality": "unknown",
    }

    assert summarize_frontend_inheritance_status_for_display(status_surface) == (
        "codegen unknown; frontend tests unknown"
    )


def test_summarize_frontend_inheritance_status_for_display_not_inherited() -> None:
    status_surface = {
        "generation": "not_inherited",
        "quality": "not_inherited",
    }

    assert summarize_frontend_inheritance_status_for_display(status_surface) == (
        "codegen not inherited yet (risk); "
        "frontend tests not inherited yet (risk)"
    )


def test_summarize_truth_ledger_frontend_inheritance_for_display_collects_later_unique_item() -> None:
    release_capabilities = [
        {},
        {"frontend_inheritance_status": {}},
        {"frontend_inheritance_status": {"generation": "", "quality": ""}},
        {"frontend_inheritance_status": {"generation": "inherited", "quality": "blocked"}},
    ]

    assert summarize_truth_ledger_frontend_inheritance_for_display(release_capabilities) == (
        "codegen inherited; frontend tests blocked"
    )


def test_summarize_capability_closure_focus_for_display() -> None:
    open_clusters = [
        {"cluster_id": "project-meta-foundations", "closure_state": "formal_only"},
        {"cluster_id": "frontend-mainline-delivery", "closure_state": "capability_open"},
        {"cluster_id": "runtime-adapter", "closure_state": "partial"},
        {"cluster_id": "docs-governance", "closure_state": "formal_only"},
    ]

    assert summarize_capability_closure_focus_for_display(open_clusters) == (
        "project-meta-foundations (formal_only), "
        "frontend-mainline-delivery (capability_open), "
        "runtime-adapter (partial), ..."
    )


def test_summarize_capability_closure_focus_for_display_deduplicates_repeated_clusters() -> None:
    open_clusters = [
        {"cluster_id": "project-meta-foundations", "closure_state": "formal_only"},
        {"cluster_id": "project-meta-foundations", "closure_state": "formal_only"},
        {"cluster_id": "frontend-mainline-delivery", "closure_state": "capability_open"},
        {"cluster_id": "frontend-mainline-delivery", "closure_state": "capability_open"},
        {"cluster_id": "runtime-adapter", "closure_state": "partial"},
        {"cluster_id": "docs-governance", "closure_state": "formal_only"},
    ]

    assert summarize_capability_closure_focus_for_display(open_clusters) == (
        "project-meta-foundations (formal_only), "
        "frontend-mainline-delivery (capability_open), "
        "runtime-adapter (partial), ..."
    )


def test_summarize_guard_surface_for_display() -> None:
    surface = {
        "state": "blocked",
        "detail": "current_stage=verify",
    }

    assert summarize_guard_surface_for_display(surface) == "blocked | current_stage=verify"


def test_summarize_guard_surface_for_display_deduplicates_repeated_parts() -> None:
    surface = {
        "state": "blocked",
        "detail": "blocked",
    }

    assert summarize_guard_surface_for_display(surface) == "blocked"


def test_summarize_status_surface_detail_combines_closure_truth_and_workitem() -> None:
    payload = {
        "telemetry": {"state": "ready"},
        "formal_artifact_target": {
            "state": "blocked",
            "detail": "misplaced formal artifact detected",
        },
        "backlog_breach_guard": {
            "state": "blocked",
            "detail": "breach detected but not logged",
        },
        "execute_authorization": {
            "state": "blocked",
            "detail": "current_stage=verify",
        },
        "capability_closure": {
            "state": "open",
            "detail": "2 open clusters; formal_only=1, partial=0, capability_open=1",
            "open_clusters": [
                {"cluster_id": "project-meta-foundations", "closure_state": "formal_only"},
                {"cluster_id": "frontend-mainline-delivery", "closure_state": "capability_open"},
            ],
        },
        "truth_ledger": {
            "state": "blocked",
            "detail": "release targets blocked: frontend-mainline-delivery (blocked)",
            "release_capabilities": [
                {
                    "capability_id": "frontend-mainline-delivery",
                    "audit_state": "blocked",
                    "frontend_delivery_status": {
                        "provider_id": "public-primevue",
                        "package_names": "primevue,@primeuix/themes",
                        "runtime_delivery_state": "scaffolded",
                        "download": "downloaded",
                        "integration": "integrated",
                        "browser_gate": "waiting for evidence",
                        "delivery": "applied, waiting for browser gate",
                    },
                }
            ],
            "next_required_action": (
                "verify adapter canonical consumption and rerun "
                "python -m ai_sdlc program truth audit"
            ),
        },
        "workitem_diagnostics": {
            "state": "action_required",
            "source": "branch_lifecycle",
            "truth_classification": "mainline_merged",
            "frontend_delivery_status": {
                "provider_id": "public-primevue",
                "package_names": "primevue,@primeuix/themes",
                "runtime_delivery_state": "scaffolded",
                "download": "downloaded",
                "integration": "integrated",
                "browser_gate": "waiting for evidence",
                "delivery": "applied, waiting for browser gate",
            },
            "primary_reason": (
                "BLOCKER: branch lifecycle unresolved: codex/001-status-drift is associated "
                "with 001-wi, ahead of main by 1 commit(s), and branch disposition is unresolved"
            ),
            "next_required_action": (
                "decide whether codex/001-status-drift should be merged, deleted, or archived, "
                "then record that branch disposition in task-execution-log.md"
            ),
        },
    }

    assert summarize_status_surface_detail(payload) == (
        "ready; formal=blocked | misplaced formal artifact detected; "
        "backlog=blocked | breach detected but not logged; "
        "execute=blocked | current_stage=verify; "
        "closure=open | 2 open clusters; formal_only=1, partial=0, capability_open=1; "
        "closure_focus=project-meta-foundations (formal_only), "
        "frontend-mainline-delivery (capability_open); "
        "truth=blocked | release targets blocked: frontend-mainline-delivery (blocked); "
        "truth_focus=frontend-mainline-delivery (blocked); "
        "next=verify adapter canonical consumption; python -m ai_sdlc program truth audit; "
        "truth_frontend=selected provider public-primevue; packages primevue,@primeuix/themes; "
        "download downloaded; integration integrated; "
        "browser check waiting for evidence; "
        "delivery applied, waiting for browser gate; "
        "workitem=action_required | branch lifecycle unresolved: codex/001-status-drift; "
        "ahead of main by 1 commit(s); workitem_source=branch_lifecycle; "
        "workitem_truth=mainline_merged; "
        "workitem_frontend=selected provider public-primevue; packages primevue,@primeuix/themes; "
        "download downloaded; integration integrated; "
        "browser check waiting for evidence; delivery applied, waiting for browser gate; "
        "workitem_next=decide codex/001-status-drift disposition; task-execution-log.md"
    )


def test_summarize_status_surface_detail_deduplicates_repeated_closure_items() -> None:
    payload = {
        "telemetry": {"state": "ready"},
        "capability_closure": {
            "state": "open",
            "detail": "2 open clusters",
            "open_clusters": [
                {"cluster_id": "project-meta-foundations", "closure_state": "formal_only"},
                {"cluster_id": "project-meta-foundations", "closure_state": "formal_only"},
                {"cluster_id": "frontend-mainline-delivery", "closure_state": "capability_open"},
                {"cluster_id": "frontend-mainline-delivery", "closure_state": "capability_open"},
            ],
        },
    }

    assert summarize_status_surface_detail(payload) == (
        "ready; closure=open | 2 open clusters; "
        "closure_focus=project-meta-foundations (formal_only), "
        "frontend-mainline-delivery (capability_open)"
    )


def test_summarize_status_surface_detail_deduplicates_repeated_truth_and_workitem_parts() -> None:
    payload = {
        "telemetry": {"state": "ready"},
        "truth_ledger": {
            "state": "blocked",
            "detail": "blocked",
            "release_capabilities": [],
        },
        "workitem_diagnostics": {
            "state": "blocked",
            "source": "program_truth",
            "primary_reason": "blocked",
        },
    }

    assert summarize_status_surface_detail(payload) == (
        "ready; truth=blocked; workitem=blocked; workitem_source=program_truth"
    )
