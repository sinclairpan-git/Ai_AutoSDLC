"""Unit tests for managed delivery apply runtime."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.managed_delivery_apply import run_managed_delivery_apply
from ai_sdlc.models.frontend_managed_delivery import (
    ConfirmedActionPlanExecutionView,
    DeliveryApplyDecisionReceipt,
    FrontendActionPlanAction,
    ManagedDeliveryExecutorContext,
)


def _build_action(
    *,
    action_id: str,
    action_type: str,
    required: bool = True,
    selected: bool = True,
    depends_on_action_ids: list[str] | None = None,
    executor_payload: dict[str, object] | None = None,
) -> FrontendActionPlanAction:
    return FrontendActionPlanAction(
        action_id=action_id,
        effect_kind="mutate",
        action_type=action_type,
        required=required,
        selected=selected,
        default_selected=selected,
        depends_on_action_ids=depends_on_action_ids or [],
        rollback_ref=f"rollback:{action_id}",
        retry_ref=f"retry:{action_id}",
        cleanup_ref=f"cleanup:{action_id}",
        risk_flags=[],
        source_linkage_refs={"spec": "specs/001-auth"},
        executor_payload=executor_payload or {},
    )


def _build_view(
    *actions: FrontendActionPlanAction,
    managed_target_path: str = "managed/frontend",
) -> ConfirmedActionPlanExecutionView:
    return ConfirmedActionPlanExecutionView(
        action_plan_id="plan-001",
        confirmation_surface_id="surface-001",
        plan_fingerprint="fp-001",
        protocol_version="1",
        managed_target_ref="managed://frontend/app",
        managed_target_path=managed_target_path,
        attachment_scope_ref="scope://001-auth",
        readiness_subject_id="001-auth",
        spec_dir="specs/001-auth",
        action_items=list(actions),
        will_not_touch=["legacy-root"],
    )


def _build_receipt(*, selected_action_ids: list[str], confirmed_plan_fingerprint: str = "fp-001") -> DeliveryApplyDecisionReceipt:
    return DeliveryApplyDecisionReceipt(
        decision_receipt_id="receipt-001",
        action_plan_id="plan-001",
        confirmation_surface_id="surface-001",
        decision="continue",
        selected_action_ids=selected_action_ids,
        deselected_optional_action_ids=[],
        risk_acknowledgement_ids=[],
        second_confirmation_acknowledged=True,
        confirmed_plan_fingerprint=confirmed_plan_fingerprint,
        created_at="2026-04-13T13:30:00Z",
    )


def test_run_managed_delivery_apply_blocks_on_plan_fingerprint_mismatch() -> None:
    view = _build_view(_build_action(action_id="a1", action_type="runtime_remediation"))
    receipt = _build_receipt(
        selected_action_ids=["a1"],
        confirmed_plan_fingerprint="fp-mismatch",
    )

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "plan_fingerprint_mismatch" in result.blockers
    assert result.ledger_entries == []


def test_run_managed_delivery_apply_blocks_on_receipt_plan_binding_mismatch() -> None:
    view = _build_view(_build_action(action_id="a1", action_type="runtime_remediation"))
    receipt = DeliveryApplyDecisionReceipt(
        decision_receipt_id="receipt-001",
        action_plan_id="plan-other",
        confirmation_surface_id="surface-001",
        decision="continue",
        selected_action_ids=["a1"],
        deselected_optional_action_ids=[],
        risk_acknowledgement_ids=[],
        second_confirmation_acknowledged=True,
        confirmed_plan_fingerprint="fp-001",
        created_at="2026-04-13T13:30:00Z",
    )

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "action_plan_binding_mismatch" in result.blockers


def test_run_managed_delivery_apply_blocks_when_risk_acknowledgement_missing() -> None:
    action = _build_action(action_id="a1", action_type="runtime_remediation")
    action = action.model_copy(update={"risk_flags": ["risk:mutates-host"]})
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "risk_acknowledgement_missing" in result.blockers


def test_run_managed_delivery_apply_blocks_when_required_unsupported_selected() -> None:
    view = _build_view(_build_action(action_id="a1", action_type="workspace_integration"))
    receipt = _build_receipt(selected_action_ids=["a1"])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "required_unsupported" in result.blockers
    assert result.failed_action_ids == []
    assert result.blocked_action_ids == ["a1"]
    assert result.ledger_entries[0].failure_classification == "required_unsupported"


def test_run_managed_delivery_apply_blocks_when_required_action_not_selected() -> None:
    view = _build_view(_build_action(action_id="a1", action_type="runtime_remediation"))
    receipt = _build_receipt(selected_action_ids=[])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "required_action_not_selected" in result.blockers
    assert result.ledger_entries == []


def test_run_managed_delivery_apply_blocks_when_dependency_is_unsupported() -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="workspace_integration",
            required=False,
        ),
        _build_action(
            action_id="a2",
            action_type="runtime_remediation",
            depends_on_action_ids=["a1"],
        ),
    )
    receipt = _build_receipt(selected_action_ids=["a1", "a2"])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "dependency_blocked_by_unsupported" in result.blockers
    assert result.failed_action_ids == []
    assert result.blocked_action_ids == ["a1", "a2"]
    assert [entry.failure_classification for entry in result.ledger_entries] == [
        "selected_optional_unsupported",
        "dependency_blocked_by_unsupported",
    ]


def test_run_managed_delivery_apply_executes_dependency_install_with_plan_payload(
    tmp_path: Path,
) -> None:
    recorded: list[tuple[str, str, list[str]]] = []
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "public-primevue-default",
            "package_manager": "pnpm",
            "working_directory": ".",
            "packages": ["primevue", "@primeuix/themes"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    def _installer(payload, working_directory: Path) -> dict[str, str]:
        recorded.append((payload.package_manager, str(working_directory), payload.packages))
        return {
            "command": "pnpm add primevue @primeuix/themes",
            "working_directory": str(working_directory),
        }

    result = run_managed_delivery_apply(
        view,
        receipt,
        ManagedDeliveryExecutorContext(
            host_ingress_allowed=True,
            execute_actions=True,
            repo_root=tmp_path,
            dependency_installer=_installer,
        ),
    )

    assert result.result_status == "apply_succeeded_pending_browser_gate"
    assert result.executed_action_ids == ["a1"]
    assert recorded == [("pnpm", str((tmp_path / "managed/frontend").resolve()), ["primevue", "@primeuix/themes"])]
    assert result.ledger_entries[0].after_state["command"] == "pnpm add primevue @primeuix/themes"


def test_run_managed_delivery_apply_blocks_dependency_install_when_manifest_is_no_touch(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "public-primevue-default",
            "package_manager": "pnpm",
            "working_directory": ".",
            "packages": ["primevue"],
        },
    )
    view = _build_view(action).model_copy(
        update={"will_not_touch": ["managed/frontend/package.json"]}
    )
    receipt = _build_receipt(selected_action_ids=["a1"])

    result = run_managed_delivery_apply(
        view,
        receipt,
        ManagedDeliveryExecutorContext(
            host_ingress_allowed=True,
            execute_actions=False,
            repo_root=tmp_path,
        ),
    )

    assert result.result_status == "blocked_before_start"
    assert result.blockers == ["dependency_install_hits_will_not_touch"]
    assert result.blocked_action_ids == ["a1"]


def test_run_managed_delivery_apply_generates_artifacts_inside_managed_target(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="artifact_generate",
        executor_payload={
            "directories": ["src"],
            "files": [
                {
                    "path": "src/App.vue",
                    "content": "<template>Hello</template>\n",
                }
            ],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    result = run_managed_delivery_apply(
        view,
        receipt,
        ManagedDeliveryExecutorContext(
            host_ingress_allowed=True,
            execute_actions=True,
            repo_root=tmp_path,
        ),
    )

    assert result.result_status == "apply_succeeded_pending_browser_gate"
    assert (tmp_path / "managed" / "frontend" / "src" / "App.vue").read_text(
        encoding="utf-8"
    ) == "<template>Hello</template>\n"


def test_run_managed_delivery_apply_blocks_artifact_generate_outside_managed_target(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="artifact_generate",
        executor_payload={
            "files": [
                {
                    "path": "../legacy-root/App.vue",
                    "content": "<template>Blocked</template>\n",
                }
            ]
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    result = run_managed_delivery_apply(
        view,
        receipt,
        ManagedDeliveryExecutorContext(
            host_ingress_allowed=True,
            execute_actions=False,
            repo_root=tmp_path,
        ),
    )

    assert result.result_status == "blocked_before_start"
    assert result.blocked_action_ids == ["a1"]
    assert result.blockers == ["artifact_generate_outside_managed_target"]


def test_run_managed_delivery_apply_does_not_execute_when_before_state_capture_fails() -> None:
    view = _build_view(_build_action(action_id="a1", action_type="runtime_remediation"))
    receipt = _build_receipt(selected_action_ids=["a1"])

    context = ManagedDeliveryExecutorContext(
        before_state_failures={"a1": "before_state_capture_failed"},
    )

    result = run_managed_delivery_apply(view, receipt, context)

    assert result.result_status == "manual_recovery_required"
    assert result.executed_action_ids == []
    assert result.failed_action_ids == ["a1"]
    entry = result.ledger_entries[0]
    assert entry.action_id == "a1"
    assert entry.result_status == "failed"
    assert entry.failure_classification == "manual_recovery_required"


def test_run_managed_delivery_apply_preserves_partial_progress_on_manual_recovery() -> None:
    view = _build_view(
        _build_action(action_id="a1", action_type="runtime_remediation"),
        _build_action(
            action_id="a2",
            action_type="managed_target_prepare",
            depends_on_action_ids=["a1"],
        ),
    )
    receipt = _build_receipt(selected_action_ids=["a1", "a2"])
    context = ManagedDeliveryExecutorContext(
        before_state_failures={"a2": "before_state_capture_failed"},
    )

    result = run_managed_delivery_apply(view, receipt, context)

    assert result.result_status == "manual_recovery_required"
    assert result.executed_action_ids == ["a1"]
    assert result.succeeded_action_ids == ["a1"]
    assert result.failed_action_ids == ["a2"]


def test_run_managed_delivery_apply_tracks_deselected_optional_actions_as_skipped() -> None:
    view = _build_view(
        _build_action(action_id="a1", action_type="runtime_remediation"),
        _build_action(
            action_id="a2",
            action_type="managed_target_prepare",
            required=False,
            selected=False,
        ),
    )
    receipt = DeliveryApplyDecisionReceipt(
        decision_receipt_id="receipt-001",
        action_plan_id="plan-001",
        confirmation_surface_id="surface-001",
        decision="continue",
        selected_action_ids=["a1"],
        deselected_optional_action_ids=["a2"],
        risk_acknowledgement_ids=[],
        second_confirmation_acknowledged=True,
        confirmed_plan_fingerprint="fp-001",
        created_at="2026-04-13T13:30:00Z",
    )

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "apply_succeeded_pending_browser_gate"
    assert result.skipped_action_ids == ["a2"]


def test_run_managed_delivery_apply_returns_pending_browser_gate_success() -> None:
    view = _build_view(
        _build_action(action_id="a1", action_type="runtime_remediation"),
        _build_action(
            action_id="a2",
            action_type="managed_target_prepare",
            depends_on_action_ids=["a1"],
        ),
    )
    receipt = _build_receipt(selected_action_ids=["a1", "a2"])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "apply_succeeded_pending_browser_gate"
    assert result.browser_gate_required is True
    assert result.executed_action_ids == ["a1", "a2"]
    assert result.succeeded_action_ids == ["a1", "a2"]
    assert [entry.result_status for entry in result.ledger_entries] == [
        "succeeded",
        "succeeded",
    ]
    assert all(entry.after_state for entry in result.ledger_entries)


def test_run_managed_delivery_apply_blocks_on_dependency_cycle() -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="runtime_remediation",
            depends_on_action_ids=["a2"],
        ),
        _build_action(
            action_id="a2",
            action_type="managed_target_prepare",
            depends_on_action_ids=["a1"],
        ),
    )
    receipt = _build_receipt(selected_action_ids=["a1", "a2"])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert "dependency_cycle_detected" in result.blockers
