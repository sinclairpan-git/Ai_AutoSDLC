"""Unit tests for managed delivery apply runtime."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

from ai_sdlc.core.managed_delivery_apply import (
    _default_dependency_installer,
    run_managed_delivery_apply,
    verify_dependency_installation,
)
from ai_sdlc.models.frontend_managed_delivery import (
    ConfirmedActionPlanExecutionView,
    DeliveryApplyDecisionReceipt,
    DependencyInstallExecutionPayload,
    FrontendActionPlanAction,
    ManagedDeliveryApplyResult,
    ManagedDeliveryExecutionSession,
    ManagedDeliveryExecutorContext,
    RuntimeRemediationExecutionPayload,
    WorkspaceIntegrationItem,
)
from tests.support.managed_delivery import (
    build_dependency_install_subprocess_side_effect,
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
    effective_payload = executor_payload or {}
    if not effective_payload and action_type == "runtime_remediation":
        effective_payload = {
            "managed_runtime_root": ".ai-sdlc/runtime",
            "required_runtime_entries": ["node_runtime"],
            "install_profile_id": "offline_bundle_darwin_shell",
            "acquisition_mode": "managed_runtime_install",
            "will_download": ["node_runtime"],
            "will_install": [],
            "will_modify": [".ai-sdlc/runtime"],
            "manual_prerequisites": [],
            "reentry_condition": "rerun managed delivery apply",
        }
    if not effective_payload and action_type == "managed_target_prepare":
        effective_payload = {
            "directories": ["src"],
            "files": [
                {
                    "path": "package.json",
                    "content": '{\n  "name": "managed-frontend",\n  "private": true\n}\n',
                }
            ],
        }
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
        executor_payload=effective_payload,
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
    view = _build_view(_build_action(action_id="a1", action_type="custom_shell_execute"))
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
            action_type="custom_optional_action",
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


def test_run_managed_delivery_apply_deduplicates_blocked_action_ids() -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="custom_optional_action",
            required=False,
            depends_on_action_ids=["a1"],
        ),
        _build_action(
            action_id="a2",
            action_type="runtime_remediation",
            depends_on_action_ids=["a1"],
        ),
    )
    receipt = _build_receipt(selected_action_ids=["a1", "a2", "a2"])

    result = run_managed_delivery_apply(view, receipt, ManagedDeliveryExecutorContext())

    assert result.result_status == "blocked_before_start"
    assert result.blocked_action_ids == ["a1", "a2"]


def test_frontend_managed_delivery_models_deduplicate_set_like_lists() -> None:
    install_payload = DependencyInstallExecutionPayload(
        install_strategy_id="public-primevue-default",
        package_manager="pnpm",
        registry_url="https://registry.npmjs.org",
        packages=["primevue", "primevue", "@primeuix/themes"],
    )
    remediation_payload = RuntimeRemediationExecutionPayload(
        managed_runtime_root=".ai-sdlc/runtime",
        required_runtime_entries=["node_runtime", "node_runtime"],
        install_profile_id="offline_bundle_darwin_shell",
        acquisition_mode="managed_runtime_install",
        will_download=["node_runtime", "node_runtime"],
        will_install=["node_runtime", "node_runtime"],
        will_modify=["managed_runtime_root", "managed_runtime_root"],
        manual_prerequisites=["approve", "approve"],
        reentry_condition="rerun managed delivery apply",
    )
    action = FrontendActionPlanAction(
        action_id="a1",
        effect_kind="mutate",
        action_type="dependency_install",
        required=True,
        selected=True,
        default_selected=True,
        depends_on_action_ids=["setup", "setup"],
        rollback_ref="rollback:a1",
        retry_ref="retry:a1",
        cleanup_ref="cleanup:a1",
        risk_flags=["touches-lockfile", "touches-lockfile"],
        source_linkage_refs={"spec": "specs/001-auth"},
        executor_payload={
            "install_strategy_id": "public-primevue-default",
            "package_manager": "pnpm",
            "registry_url": "https://registry.npmjs.org",
            "working_directory": ".",
            "packages": ["primevue", "@primeuix/themes"],
        },
    )
    view = ConfirmedActionPlanExecutionView(
        action_plan_id="plan-001",
        confirmation_surface_id="surface-001",
        plan_fingerprint="fp-001",
        protocol_version="1",
        managed_target_ref="managed://frontend/app",
        managed_target_path="managed/frontend",
        attachment_scope_ref="scope://001-auth",
        readiness_subject_id="001-auth",
        spec_dir="specs/001-auth",
        action_items=[action],
        will_not_touch=["legacy-root", "legacy-root"],
    )
    receipt = DeliveryApplyDecisionReceipt(
        decision_receipt_id="receipt-001",
        action_plan_id="plan-001",
        confirmation_surface_id="surface-001",
        decision="continue",
        selected_action_ids=["a1", "a1"],
        deselected_optional_action_ids=["optional-1", "optional-1"],
        risk_acknowledgement_ids=["risk-1", "risk-1"],
        second_confirmation_acknowledged=True,
        confirmed_plan_fingerprint="fp-001",
        created_at="2026-04-13T13:30:00Z",
    )
    session = ManagedDeliveryExecutionSession(
        execution_session_id="session-001",
        action_plan_id="plan-001",
        confirmation_surface_id="surface-001",
        decision_receipt_id="receipt-001",
        plan_fingerprint="fp-001",
        managed_target_ref="managed://frontend/app",
        attachment_scope_ref="scope://001-auth",
        readiness_subject_id="001-auth",
        spec_dir="specs/001-auth",
        status="blocked_before_start",
        blocking_reason_codes=["risk_acknowledgement_missing"] * 2,
    )
    result = ManagedDeliveryApplyResult(
        apply_result_id="apply-001",
        execution_session_id="session-001",
        action_plan_id="plan-001",
        plan_fingerprint="fp-001",
        result_status="blocked_before_start",
        blockers=["risk_acknowledgement_missing"] * 2,
        executed_action_ids=["a1", "a1"],
        succeeded_action_ids=["a1", "a1"],
        failed_action_ids=["a2", "a2"],
        blocked_action_ids=["a3", "a3"],
        skipped_action_ids=["a4", "a4"],
        remediation_hints=["acknowledge-risk", "acknowledge-risk"],
    )
    item = WorkspaceIntegrationItem(
        integration_id="lockfile-write",
        target_class="lockfile",
        target_path="pnpm-lock.yaml",
        mutation_kind="overwrite_existing",
        content="lockfile",
        will_not_touch_refs=["package.json", "package.json"],
    )

    assert install_payload.packages == ["primevue", "@primeuix/themes"]
    assert install_payload.registry_url == "https://registry.npmjs.org"
    assert remediation_payload.required_runtime_entries == ["node_runtime"]
    assert remediation_payload.will_download == ["node_runtime"]
    assert remediation_payload.will_install == ["node_runtime"]
    assert remediation_payload.will_modify == ["managed_runtime_root"]
    assert remediation_payload.manual_prerequisites == ["approve"]
    assert action.depends_on_action_ids == ["setup"]
    assert action.risk_flags == ["touches-lockfile"]
    assert view.will_not_touch == ["legacy-root"]
    assert receipt.selected_action_ids == ["a1", "a1"]
    assert receipt.deselected_optional_action_ids == ["optional-1", "optional-1"]
    assert receipt.risk_acknowledgement_ids == ["risk-1", "risk-1"]
    assert session.blocking_reason_codes == ["risk_acknowledgement_missing"]
    assert result.blockers == ["risk_acknowledgement_missing"]
    assert result.executed_action_ids == ["a1", "a1"]
    assert result.succeeded_action_ids == ["a1", "a1"]
    assert result.failed_action_ids == ["a2", "a2"]
    assert result.blocked_action_ids == ["a3", "a3"]
    assert result.skipped_action_ids == ["a4", "a4"]
    assert result.remediation_hints == ["acknowledge-risk"]
    assert item.will_not_touch_refs == ["package.json"]


def test_run_managed_delivery_apply_executes_dependency_install_with_plan_payload(
    tmp_path: Path,
) -> None:
    recorded: list[tuple[str, str, str, list[str]]] = []
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "public-primevue-default",
            "package_manager": "pnpm",
            "registry_url": "https://registry.npmjs.org",
            "working_directory": ".",
            "packages": ["primevue", "@primeuix/themes"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    def _installer(payload, working_directory: Path) -> dict[str, str]:
        recorded.append(
            (
                payload.package_manager,
                payload.registry_url,
                str(working_directory),
                payload.packages,
            )
        )
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
    assert recorded == [
        (
            "pnpm",
            "https://registry.npmjs.org",
            str((tmp_path / "managed/frontend").resolve()),
            ["primevue", "@primeuix/themes"],
        )
    ]
    assert result.ledger_entries[0].after_state["command"] == "pnpm add primevue @primeuix/themes"


def test_run_managed_delivery_apply_passes_registry_url_to_default_dependency_installer(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "enterprise-vue2-company-registry",
            "package_manager": "npm",
            "registry_url": "http://npm.uedc.sangfor.com.cn/",
            "working_directory": ".",
            "packages": ["@sxf/er-components"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])
    recorded_commands: list[list[str]] = []

    def _side_effect(command, *args, **kwargs):
        command_parts = [str(part) for part in command]
        recorded_commands.append(command_parts)
        return build_dependency_install_subprocess_side_effect()(
            command,
            *args,
            **kwargs,
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_side_effect,
    ):
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
    assert recorded_commands[0] == [
        "npm",
        "install",
        "--registry",
        "http://npm.uedc.sangfor.com.cn/",
        "@sxf/er-components",
    ]


def test_run_managed_delivery_apply_configures_yarn_registry_without_add_flag(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "enterprise-vue2-company-registry",
            "package_manager": "yarn",
            "registry_url": "http://npm.uedc.sangfor.com.cn/",
            "working_directory": ".",
            "packages": ["@sxf/er-components"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])
    recorded_commands: list[list[str]] = []
    recorded_env: list[dict[str, str] | None] = []

    def _side_effect(command, *args, **kwargs):
        command_parts = [str(part) for part in command]
        recorded_commands.append(command_parts)
        recorded_env.append(kwargs.get("env"))
        return build_dependency_install_subprocess_side_effect()(
            command,
            *args,
            **kwargs,
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_side_effect,
    ):
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
    assert recorded_commands[0] == ["yarn", "add", "@sxf/er-components"]
    assert "--registry" not in recorded_commands[0]
    assert recorded_env[0] is not None
    assert recorded_env[0]["npm_config_registry"] == "http://npm.uedc.sangfor.com.cn/"
    assert recorded_env[0]["YARN_NPM_REGISTRY_SERVER"] == "http://npm.uedc.sangfor.com.cn/"
    assert result.ledger_entries[0].after_state["registry_env_var"] == (
        "npm_config_registry,YARN_NPM_REGISTRY_SERVER"
    )


def test_run_managed_delivery_apply_retries_transient_registry_failures(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "enterprise-vue2-company-registry",
            "package_manager": "npm",
            "registry_url": "http://npm.uedc.sangfor.com.cn/",
            "working_directory": ".",
            "packages": ["@sxf/er-components"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])
    attempts = {"count": 0}

    def _side_effect(command, *args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise subprocess.CalledProcessError(
                returncode=1,
                cmd=command,
                stderr="npm ERR! code E503\nnpm ERR! 503 Service Unavailable - GET http://npm.uedc.sangfor.com.cn/graphql",
            )
        return build_dependency_install_subprocess_side_effect()(
            command,
            *args,
            **kwargs,
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_side_effect,
    ):
        result = run_managed_delivery_apply(
            view,
            receipt,
            ManagedDeliveryExecutorContext(
                host_ingress_allowed=True,
                execute_actions=True,
                repo_root=tmp_path,
            ),
        )

    assert attempts["count"] == 3
    assert result.result_status == "apply_succeeded_pending_browser_gate"


def test_run_managed_delivery_apply_verifies_dependency_install_footprint(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "public-primevue-default",
            "package_manager": "npm",
            "working_directory": ".",
            "packages": ["primevue", "@primeuix/themes"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=build_dependency_install_subprocess_side_effect(),
    ):
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
    after_state = result.ledger_entries[0].after_state
    assert (
        after_state["verification_state"]
        == "package_manifest_lockfile_dependency_resolution_verified"
    )
    assert after_state["lockfile_path"].endswith("package-lock.json")
    assert "primevue" in after_state["resolved_package_manifests"]
    assert "node_modules" in after_state["resolved_package_manifests"]


def test_verify_dependency_installation_normalizes_package_specs(
    tmp_path: Path,
) -> None:
    (tmp_path / "node_modules" / "primevue").mkdir(parents=True)
    (tmp_path / "node_modules" / "@primeuix" / "themes").mkdir(parents=True)
    (tmp_path / "node_modules" / "ui-kit").mkdir(parents=True)
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {
                    "primevue": "^4.0.0",
                    "@primeuix/themes": "^1.2.3",
                    "ui-kit": "npm:real-ui-kit@2.0.0",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "node_modules" / "primevue" / "package.json").write_text(
        json.dumps({"name": "primevue", "version": "4.0.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "node_modules" / "@primeuix" / "themes" / "package.json").write_text(
        json.dumps({"name": "@primeuix/themes", "version": "1.2.3"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "node_modules" / "ui-kit" / "package.json").write_text(
        json.dumps({"name": "ui-kit", "version": "2.0.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package-lock.json").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="public-primevue-default",
        package_manager="npm",
        working_directory=".",
        packages=["primevue@latest", "@primeuix/themes@1.2.3", "ui-kit@npm:real-ui-kit@2"],
    )

    result = verify_dependency_installation(payload, tmp_path)

    assert (
        result["verification_state"]
        == "package_manifest_lockfile_dependency_resolution_verified"
    )
    resolved = json.loads(result["resolved_package_manifests"])
    assert sorted(resolved) == ["@primeuix/themes", "primevue", "ui-kit"]


def test_verify_dependency_installation_uses_yarn_node_for_pnp_resolution(
    tmp_path: Path,
) -> None:
    manifest_ref = tmp_path / ".yarn" / "cache" / "primevue" / "package.json"
    manifest_ref.parent.mkdir(parents=True, exist_ok=True)
    manifest_ref.write_text(
        json.dumps({"name": "primevue", "version": "4.0.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {"primevue": "^4.0.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "yarn.lock").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="public-primevue-default",
        package_manager="yarn",
        working_directory=".",
        packages=["primevue"],
    )

    def _resolution_check(command, *args, **kwargs):
        assert command[:3] == ["yarn", "node", "-e"]
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps({"primevue": str(manifest_ref)}),
            stderr="",
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_resolution_check,
    ):
        result = verify_dependency_installation(payload, tmp_path)

    resolved = json.loads(result["resolved_package_manifests"])
    assert resolved == {"primevue": str(manifest_ref.resolve())}


def test_verify_dependency_installation_requires_playwright_browser_runtime(
    tmp_path: Path,
) -> None:
    (tmp_path / "node_modules" / "playwright").mkdir(parents=True)
    (tmp_path / "node_modules" / "playwright" / "package.json").write_text(
        json.dumps({"name": "playwright", "version": "1.38.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {"playwright": "^1.38.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package-lock.json").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="browser-runtime",
        package_manager="npm",
        working_directory=".",
        packages=["playwright"],
    )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=subprocess.CalledProcessError(42, ["node"]),
    ):
        try:
            verify_dependency_installation(payload, tmp_path)
        except ValueError as exc:
            assert str(exc) == "dependency_install_playwright_browser_runtime_missing"
        else:  # pragma: no cover - defensive assertion path
            raise AssertionError("expected missing Playwright browser runtime blocker")


def test_verify_dependency_installation_records_playwright_browser_runtime(
    tmp_path: Path,
) -> None:
    (tmp_path / "node_modules" / "playwright").mkdir(parents=True)
    (tmp_path / "node_modules" / "playwright" / "package.json").write_text(
        json.dumps({"name": "playwright", "version": "1.38.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {"playwright": "^1.38.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package-lock.json").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="browser-runtime",
        package_manager="npm",
        working_directory=".",
        packages=["playwright"],
    )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["node"],
            returncode=0,
            stdout="/ms-playwright/chromium/chrome",
            stderr="",
        ),
    ):
        result = verify_dependency_installation(payload, tmp_path)

    assert result["playwright_browser_runtime"] == "/ms-playwright/chromium/chrome"


def test_verify_dependency_installation_uses_yarn_node_for_playwright_runtime(
    tmp_path: Path,
) -> None:
    manifest_ref = tmp_path / ".yarn" / "cache" / "@playwright" / "test" / "package.json"
    manifest_ref.parent.mkdir(parents=True, exist_ok=True)
    manifest_ref.write_text(
        json.dumps({"name": "@playwright/test", "version": "1.38.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {"@playwright/test": "^1.38.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "yarn.lock").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="browser-runtime",
        package_manager="yarn",
        working_directory=".",
        packages=["@playwright/test"],
    )

    def _runtime_check(command, *args, **kwargs):
        assert command[:3] == ["yarn", "node", "-e"]
        script = command[3]
        if "process.argv.slice(1)" in script:
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout=json.dumps({"@playwright/test": str(manifest_ref)}),
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="/virtual/.cache/ms-playwright/chromium/chrome",
            stderr="",
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_runtime_check,
    ):
        result = verify_dependency_installation(payload, tmp_path)

    assert (
        result["playwright_browser_runtime"]
        == "/virtual/.cache/ms-playwright/chromium/chrome"
    )


def test_default_dependency_installer_bootstraps_playwright_browser_runtime(
    tmp_path: Path,
) -> None:
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="browser-runtime",
        package_manager="npm",
        working_directory=".",
        packages=["playwright"],
    )

    with (
        patch(
            "ai_sdlc.core.managed_delivery_apply.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=["npm", "install", "playwright"],
                returncode=0,
                stdout="",
                stderr="",
            ),
        ),
        patch(
            "ai_sdlc.core.managed_delivery_apply._install_playwright_browser_runtime"
        ) as install_runtime,
        patch(
            "ai_sdlc.core.managed_delivery_apply.verify_dependency_installation",
            return_value={},
        ),
    ):
        result = _default_dependency_installer(payload, tmp_path)

    install_runtime.assert_called_once()
    assert result["playwright_runtime_installed"] == "chromium"


def test_verify_dependency_installation_accepts_playwright_test_runtime_layout(
    tmp_path: Path,
) -> None:
    (tmp_path / "node_modules" / "@playwright" / "test").mkdir(parents=True)
    (tmp_path / "node_modules" / "@playwright" / "test" / "package.json").write_text(
        json.dumps({"name": "@playwright/test", "version": "1.38.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {"@playwright/test": "^1.38.0"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package-lock.json").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="browser-runtime",
        package_manager="npm",
        working_directory=".",
        packages=["@playwright/test"],
    )

    def _runtime_check(command, *args, **kwargs):
        script = command[-1]
        assert "@playwright/test" in script
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="/ms-playwright/chromium/chrome",
            stderr="",
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_runtime_check,
    ):
        result = verify_dependency_installation(payload, tmp_path)

    assert result["playwright_browser_runtime"] == "/ms-playwright/chromium/chrome"


def test_verify_dependency_installation_skips_playwright_runtime_for_unrequested_package(
    tmp_path: Path,
) -> None:
    (tmp_path / "node_modules" / "primevue").mkdir(parents=True)
    (tmp_path / "node_modules" / "primevue" / "package.json").write_text(
        json.dumps({"name": "primevue", "version": "4.0.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "managed-frontend",
                "private": True,
                "dependencies": {
                    "primevue": "^4.0.0",
                    "playwright": "^1.38.0",
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "package-lock.json").write_text("# fixture lockfile\n", encoding="utf-8")
    payload = DependencyInstallExecutionPayload(
        install_strategy_id="public-primevue-default",
        package_manager="npm",
        working_directory=".",
        packages=["primevue"],
    )

    def _node_side_effect(command, *args, **kwargs):
        script = str(command[-2] if command[-1] == "primevue" else command[-1])
        if "chromium.executablePath" in script:
            raise AssertionError("Playwright runtime check should not run")
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(
                {
                    "primevue": str(
                        tmp_path / "node_modules" / "primevue" / "package.json"
                    )
                }
            ),
            stderr="",
        )

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=_node_side_effect,
    ):
        result = verify_dependency_installation(payload, tmp_path)

    assert result["playwright_browser_runtime"] == ""


def test_run_managed_delivery_apply_fails_when_dependency_lockfile_verification_is_missing(
    tmp_path: Path,
) -> None:
    action = _build_action(
        action_id="a1",
        action_type="dependency_install",
        executor_payload={
            "install_strategy_id": "public-primevue-default",
            "package_manager": "npm",
            "working_directory": ".",
            "packages": ["primevue"],
        },
    )
    view = _build_view(action)
    receipt = _build_receipt(selected_action_ids=["a1"])

    with patch(
        "ai_sdlc.core.managed_delivery_apply.subprocess.run",
        side_effect=build_dependency_install_subprocess_side_effect(
            lockfile_required=False
        ),
    ):
        result = run_managed_delivery_apply(
            view,
            receipt,
            ManagedDeliveryExecutorContext(
                host_ingress_allowed=True,
                execute_actions=True,
                repo_root=tmp_path,
            ),
        )

    assert result.result_status == "manual_recovery_required"
    assert result.failed_action_ids == ["a1"]
    assert result.blockers == ["dependency_install_lockfile_missing:npm"]
    assert result.ledger_entries[0].result_status == "failed"


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


def test_run_managed_delivery_apply_materializes_runtime_remediation_truth(
    tmp_path: Path,
) -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="runtime_remediation",
            executor_payload={
                "managed_runtime_root": ".ai-sdlc/runtime",
                "required_runtime_entries": ["node_runtime", "package_manager"],
                "install_profile_id": "offline_bundle_darwin_shell",
                "acquisition_mode": "managed_runtime_install",
                "will_download": ["node_runtime"],
                "will_install": ["package_manager"],
                "will_modify": [".ai-sdlc/runtime"],
                "manual_prerequisites": [],
                "reentry_condition": "rerun managed delivery apply",
            },
        )
    )
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
    entry = result.ledger_entries[0]
    assert entry.after_state["managed_runtime_root"].endswith(".ai-sdlc/runtime")
    assert entry.after_state["required_runtime_entries"] == "node_runtime,package_manager"


def test_run_managed_delivery_apply_materializes_managed_target_prepare_truth(
    tmp_path: Path,
) -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="managed_target_prepare",
            executor_payload={
                "directories": ["src"],
                "files": [
                    {
                        "path": "package.json",
                        "content": '{\n  "name": "managed-frontend",\n  "private": true\n}\n',
                    }
                ],
            },
        )
    )
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
    target_root = tmp_path / "managed" / "frontend"
    assert (target_root / "src").is_dir()
    assert (target_root / "package.json").is_file()
    assert result.ledger_entries[0].after_state["target_root"] == str(target_root.resolve())


def test_run_managed_delivery_apply_executes_workspace_integration_when_selected(
    tmp_path: Path,
) -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="workspace_integration",
            required=False,
            executor_payload={
                "items": [
                    {
                        "integration_id": "workspace-package-json",
                        "target_class": "workspace",
                        "target_path": "package.json",
                        "mutation_kind": "write_new",
                        "content": '{\n  "name": "root-app"\n}\n',
                        "requires_explicit_confirmation": True,
                        "will_not_touch_refs": ["legacy-root"],
                    }
                ]
            },
        )
    )
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
    assert (tmp_path / "package.json").read_text(encoding="utf-8") == '{\n  "name": "root-app"\n}\n'
    assert result.ledger_entries[0].after_state["applied_integrations"] == "workspace-package-json"


def test_run_managed_delivery_apply_executes_workspace_integration_overwrite_existing(
    tmp_path: Path,
) -> None:
    (tmp_path / "package.json").write_text('{\n  "name": "old-root-app"\n}\n', encoding="utf-8")
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="workspace_integration",
            required=False,
            executor_payload={
                "items": [
                    {
                        "integration_id": "workspace-package-json",
                        "target_class": "workspace",
                        "target_path": "package.json",
                        "mutation_kind": "overwrite_existing",
                        "content": '{\n  "name": "root-app"\n}\n',
                        "requires_explicit_confirmation": True,
                        "will_not_touch_refs": ["legacy-root"],
                    }
                ]
            },
        )
    )
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
    assert (tmp_path / "package.json").read_text(encoding="utf-8") == '{\n  "name": "root-app"\n}\n'
    assert result.ledger_entries[0].after_state["applied_integrations"] == "workspace-package-json"


def test_run_managed_delivery_apply_blocks_workspace_integration_on_mixed_target_classes(
    tmp_path: Path,
) -> None:
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="workspace_integration",
            required=False,
            executor_payload={
                "items": [
                    {
                        "integration_id": "workspace-package-json",
                        "target_class": "workspace",
                        "target_path": "package.json",
                        "mutation_kind": "write_new",
                        "content": "{}\n",
                        "requires_explicit_confirmation": True,
                        "will_not_touch_refs": [],
                    },
                    {
                        "integration_id": "route-config",
                        "target_class": "route",
                        "target_path": "router/index.ts",
                        "mutation_kind": "write_new",
                        "content": "export {}\n",
                        "requires_explicit_confirmation": True,
                        "will_not_touch_refs": [],
                    },
                ]
            },
        )
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
    assert result.blockers == ["workspace_integration_mixed_target_classes"]


def test_run_managed_delivery_apply_blocks_workspace_integration_on_symlink_escape(
    tmp_path: Path,
) -> None:
    outside_root = tmp_path.parent / "outside-workspace"
    outside_root.mkdir(parents=True, exist_ok=True)
    symlink_root = tmp_path / "links"
    symlink_root.mkdir(parents=True, exist_ok=True)
    (symlink_root / "escape").symlink_to(outside_root, target_is_directory=True)
    view = _build_view(
        _build_action(
            action_id="a1",
            action_type="workspace_integration",
            required=False,
            executor_payload={
                "items": [
                    {
                        "integration_id": "escaped-write",
                        "target_class": "workspace",
                        "target_path": "links/escape/package.json",
                        "mutation_kind": "write_new",
                        "content": "{}\n",
                        "requires_explicit_confirmation": True,
                        "will_not_touch_refs": [],
                    }
                ]
            },
        )
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
    assert result.blockers == ["workspace_integration_outside_repo_root"]


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
