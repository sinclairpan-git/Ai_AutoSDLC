"""Unit tests for backend routing coordination."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.backends.native import (
    BackendCapabilityDeclaration,
    BackendDecisionKind,
    BackendFailureEvidence,
    BackendRegistry,
    BackendSelectionDecision,
    BackendSelectionPolicy,
)
from ai_sdlc.backends.routing import (
    BackendExecutionError,
    BackendRoutingBlockedError,
    BackendRoutingCoordinator,
)


class RecordingBackend:
    def __init__(
        self,
        backend_name: str,
        *,
        capabilities: tuple[str, ...],
        responses: dict[str, str] | None = None,
        failures: dict[str, Exception] | None = None,
    ) -> None:
        self.backend_name = backend_name
        self.capabilities = capabilities
        self.responses = responses or {}
        self.failures = failures or {}
        self.calls: list[tuple[str, dict[str, object]]] = []

    def capability_declaration(self) -> BackendCapabilityDeclaration:
        return BackendCapabilityDeclaration(
            backend_name=self.backend_name,
            provided_capabilities=self.capabilities,
        )

    def generate_spec(self, context: dict[str, object]) -> str:
        return self._call("generate_spec", context)

    def generate_plan(self, context: dict[str, object]) -> str:
        return self._call("generate_plan", context)

    def generate_tasks(self, context: dict[str, object]) -> str:
        return self._call("generate_tasks", context)

    def execute_task(self, task_id: str, context: dict[str, object]) -> str:
        return "pending"

    def generate_index(self, root: Path) -> dict[str, object]:
        return {}

    def _call(self, method_name: str, context: dict[str, object]) -> str:
        self.calls.append((method_name, dict(context)))
        failure = self.failures.get(method_name)
        if failure is not None:
            raise failure
        return self.responses.get(method_name, f"{self.backend_name}:{method_name}")


def _registry_with_native_and_plugin(
    *,
    plugin_capabilities: tuple[str, ...] = ("generate_spec", "generate_plan", "generate_tasks"),
    plugin_failures: dict[str, Exception] | None = None,
    native_responses: dict[str, str] | None = None,
    plugin_responses: dict[str, str] | None = None,
) -> tuple[BackendRegistry, RecordingBackend, RecordingBackend]:
    registry = BackendRegistry()
    native = RecordingBackend(
        "native-test",
        capabilities=("generate_spec", "generate_plan", "generate_tasks"),
        responses=native_responses or {
            "generate_spec": "native spec",
            "generate_plan": "native plan",
            "generate_tasks": "native tasks",
        },
    )
    plugin = RecordingBackend(
        "plugin",
        capabilities=plugin_capabilities,
        responses=plugin_responses or {
            "generate_spec": "plugin spec",
            "generate_plan": "plugin plan",
            "generate_tasks": "plugin tasks",
        },
        failures=plugin_failures,
    )
    registry.register("native-test", native)
    registry.set_default("native-test")
    registry.register("plugin", plugin)
    return registry, native, plugin


def test_generate_spec_delegates_to_plugin() -> None:
    registry, native, plugin = _registry_with_native_and_plugin()
    router = BackendRoutingCoordinator(registry=registry, requested_backend="plugin")

    result = router.generate_spec({"work_item_id": "WI-001"})

    assert result.content == "plugin spec"
    assert result.backend_decision is not None
    assert result.backend_decision.decision_kind == BackendDecisionKind.DELEGATE
    assert result.backend_decision.selected_backend == "plugin"
    assert len(plugin.calls) == 1
    assert plugin.calls[0][0] == "generate_spec"
    assert plugin.calls[0][1]["_ai_sdlc_backend_route_bypass"] is True
    assert native.calls == []


def test_generate_plan_falls_back_to_native_when_plugin_missing_capability() -> None:
    registry, native, plugin = _registry_with_native_and_plugin(
        plugin_capabilities=("generate_spec",),
    )
    router = BackendRoutingCoordinator(registry=registry, requested_backend="plugin")

    result = router.generate_plan({"work_item_id": "WI-002"})

    assert result.content == "native plan"
    assert result.backend_decision is not None
    assert result.backend_decision.decision_kind == BackendDecisionKind.FALLBACK_NATIVE
    assert result.backend_decision.selected_backend == "native-test"
    assert plugin.calls == []
    assert len(native.calls) == 1
    assert native.calls[0][0] == "generate_plan"


def test_generate_tasks_blocks_when_policy_disallows_plugin() -> None:
    registry, _, _ = _registry_with_native_and_plugin()
    router = BackendRoutingCoordinator(
        registry=registry,
        requested_backend="plugin",
        policy=BackendSelectionPolicy(allow_plugin=False, allow_native_fallback=False),
    )

    with pytest.raises(BackendRoutingBlockedError) as excinfo:
        router.generate_tasks({"work_item_id": "WI-003"})

    assert excinfo.value.decision.decision_kind == BackendDecisionKind.BLOCK
    assert "forbidden" in excinfo.value.decision.reason


def test_safe_plugin_failure_falls_back_to_native() -> None:
    registry, native, plugin = _registry_with_native_and_plugin(
        plugin_failures={
            "generate_spec": BackendExecutionError(
                "plugin timed out",
                backend_name="plugin",
                safe_to_fallback=True,
                evidence=("plugin_timeout",),
            )
        },
    )
    router = BackendRoutingCoordinator(registry=registry, requested_backend="plugin")

    result = router.generate_spec({"work_item_id": "WI-004"})

    assert result.content == "native spec"
    assert result.backend_decision is not None
    assert result.backend_decision.decision_kind == BackendDecisionKind.FALLBACK_NATIVE
    assert result.backend_decision.failure is not None
    assert result.backend_decision.failure.safe_to_fallback is True
    assert len(plugin.calls) == 1
    assert plugin.calls[0][0] == "generate_spec"
    assert len(native.calls) == 1
    assert native.calls[0][0] == "generate_spec"


def test_unsafe_plugin_failure_blocks() -> None:
    registry, native, plugin = _registry_with_native_and_plugin(
        plugin_failures={"generate_spec": RuntimeError("plugin crashed")},
    )
    router = BackendRoutingCoordinator(registry=registry, requested_backend="plugin")

    with pytest.raises(BackendRoutingBlockedError) as excinfo:
        router.generate_spec({"work_item_id": "WI-005"})

    assert excinfo.value.decision.decision_kind == BackendDecisionKind.BLOCK
    assert excinfo.value.decision.failure is not None
    assert excinfo.value.decision.failure.safe_to_fallback is False
    assert len(plugin.calls) == 1
    assert native.calls == []


def test_backend_runtime_objects_canonicalize_capability_and_evidence_lists() -> None:
    declaration = BackendCapabilityDeclaration(
        backend_name="plugin",
        provided_capabilities=("generate_spec", "generate_spec", "generate_plan"),
        delegation=("delegation", "delegation"),
        fallback=("fallback", "fallback"),
    )
    failure = BackendFailureEvidence(
        backend_name="plugin",
        error="plugin timed out",
        safe_to_fallback=True,
        evidence=("plugin_timeout", "plugin_timeout"),
    )
    decision = BackendSelectionDecision(
        decision_kind=BackendDecisionKind.FALLBACK_NATIVE,
        requested_backend="plugin",
        selected_backend="native-test",
        required_capabilities=("generate_spec", "generate_spec"),
        available_capabilities=("generate_spec", "generate_plan", "generate_plan"),
        missing_capabilities=("generate_tasks", "generate_tasks"),
        policy_allow_plugin=True,
        policy_allow_native_fallback=True,
        reason="fallback",
        evidence=("fallback", "fallback", "plugin_timeout"),
        capability_declaration=declaration,
        failure=failure,
    )

    assert declaration.provided_capabilities == ("generate_spec", "generate_plan")
    assert declaration.delegation == ("delegation",)
    assert declaration.fallback == ("fallback",)
    assert failure.evidence == ("plugin_timeout",)
    assert decision.required_capabilities == ("generate_spec",)
    assert decision.available_capabilities == ("generate_spec", "generate_plan")
    assert decision.missing_capabilities == ("generate_tasks",)
    assert decision.evidence == ("fallback", "plugin_timeout")
