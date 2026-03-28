"""Unit tests for backend protocol, native backend, and registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.backends.native import (
    BACKEND_CAPABILITY_TOKEN,
    BACKEND_DELEGATION_TOKEN,
    BACKEND_FALLBACK_TOKEN,
    BackendCapabilityDeclaration,
    BackendDecisionKind,
    BackendFailureEvidence,
    BackendNotFoundError,
    BackendProtocol,
    BackendRegistry,
    BackendSelectionPolicy,
    NativeBackend,
)


class TestBackendProtocol:
    def test_native_is_backend(self) -> None:
        assert isinstance(NativeBackend(), BackendProtocol)


class TestNativeBackend:
    def test_capability_declaration_includes_contract_markers(self) -> None:
        nb = NativeBackend()
        declaration = nb.capability_declaration()

        assert declaration.backend_name == "native"
        assert declaration.covers(("generate_spec", "generate_index"))
        assert BACKEND_CAPABILITY_TOKEN in declaration.evidence_tokens()
        assert BACKEND_DELEGATION_TOKEN in declaration.evidence_tokens()
        assert BACKEND_FALLBACK_TOKEN in declaration.evidence_tokens()

    def test_generate_spec(self) -> None:
        nb = NativeBackend()
        result = nb.generate_spec(
            {
                "project_name": "Test",
                "work_item_id": "WI-2026-001",
                "created_at": "2026-03-22",
            }
        )
        assert "WI-2026-001" in result
        assert "功能规格" in result

    def test_generate_plan(self) -> None:
        nb = NativeBackend()
        result = nb.generate_plan(
            {
                "project_name": "Test",
                "work_item_id": "WI-2026-001",
                "created_at": "2026-03-22",
                "modules": [],
            }
        )
        assert "实现计划" in result

    def test_generate_tasks(self) -> None:
        nb = NativeBackend()
        result = nb.generate_tasks(
            {
                "work_item_id": "WI-2026-001",
                "created_at": "2026-03-22",
                "tasks": [],
            }
        )
        assert "任务分解" in result

    def test_execute_task_returns_pending(self) -> None:
        nb = NativeBackend()
        assert nb.execute_task("T001", {}) == "pending"

    def test_generate_index_empty_project(self, tmp_path: Path) -> None:
        nb = NativeBackend()
        result = nb.generate_index(tmp_path)
        assert "error" in result  # no .ai-sdlc dir


class TestBackendRegistry:
    def test_default_is_native(self) -> None:
        reg = BackendRegistry()
        default = reg.get_default()
        assert isinstance(default, NativeBackend)

    def test_get_native(self) -> None:
        reg = BackendRegistry()
        assert isinstance(reg.get("native"), NativeBackend)

    def test_get_missing_raises(self) -> None:
        reg = BackendRegistry()
        with pytest.raises(BackendNotFoundError):
            reg.get("nonexistent")

    def test_register_custom(self) -> None:
        reg = BackendRegistry()

        class CustomBackend:
            def capability_declaration(self) -> BackendCapabilityDeclaration:
                return BackendCapabilityDeclaration(
                    backend_name="custom",
                    provided_capabilities=("generate_spec", "generate_plan"),
                )

            def generate_spec(self, context: dict) -> str:
                return "custom"

            def generate_plan(self, context: dict) -> str:
                return "custom"

            def generate_tasks(self, context: dict) -> str:
                return "custom"

            def execute_task(self, task_id: str, context: dict) -> str:
                return "custom"

            def generate_index(self, root: Path) -> dict:
                return {}

        custom = CustomBackend()
        reg.register("custom", custom)
        assert reg.get("custom") is custom

    def test_set_default(self) -> None:
        reg = BackendRegistry()

        class Stub:
            def generate_spec(self, context: dict) -> str:
                return ""

            def generate_plan(self, context: dict) -> str:
                return ""

            def generate_tasks(self, context: dict) -> str:
                return ""

            def execute_task(self, task_id: str, context: dict) -> str:
                return ""

            def generate_index(self, root: Path) -> dict:
                return {}

        reg.register("stub", Stub())
        reg.set_default("stub")
        assert isinstance(reg.get_default(), Stub)

    def test_set_default_unregistered_raises(self) -> None:
        reg = BackendRegistry()
        with pytest.raises(BackendNotFoundError):
            reg.set_default("nope")

    def test_available(self) -> None:
        reg = BackendRegistry()
        assert "native" in reg.available

    def test_select_backend_delegates_when_plugin_covers_required_capabilities(
        self,
    ) -> None:
        reg = BackendRegistry()

        class PluginBackend:
            def capability_declaration(self) -> BackendCapabilityDeclaration:
                return BackendCapabilityDeclaration(
                    backend_name="plugin",
                    provided_capabilities=("generate_spec", "generate_plan"),
                )

            def generate_spec(self, context: dict) -> str:
                return "plugin"

            def generate_plan(self, context: dict) -> str:
                return "plugin"

            def generate_tasks(self, context: dict) -> str:
                return "plugin"

            def execute_task(self, task_id: str, context: dict) -> str:
                return "plugin"

            def generate_index(self, root: Path) -> dict:
                return {}

        reg.register("plugin", PluginBackend())
        decision = reg.select_backend(("generate_spec",), requested_backend="plugin")

        assert decision.decision_kind == BackendDecisionKind.DELEGATE
        assert decision.selected_backend == "plugin"
        assert decision.missing_capabilities == ()
        assert BACKEND_DELEGATION_TOKEN in decision.evidence
        assert decision.to_status_view()["decision_kind"] == "delegate"
        assert decision.to_status_view()["capability_declaration"] == "plugin"

    def test_select_backend_falls_back_to_native_when_plugin_missing(self) -> None:
        reg = BackendRegistry()
        decision = reg.select_backend(("generate_spec",), requested_backend="plugin")

        assert decision.decision_kind == BackendDecisionKind.FALLBACK_NATIVE
        assert decision.selected_backend == "native"
        assert "missing_backend" in decision.evidence

    def test_select_backend_blocks_when_fallback_disallowed(self) -> None:
        reg = BackendRegistry()
        policy = BackendSelectionPolicy(allow_plugin=False, allow_native_fallback=False)
        reg.register(
            "plugin",
            type(
                "PluginBackend",
                (),
                {
                    "capability_declaration": lambda self: BackendCapabilityDeclaration(
                        backend_name="plugin",
                        provided_capabilities=("generate_spec",),
                    ),
                    "generate_spec": lambda self, context: "plugin",
                    "generate_plan": lambda self, context: "plugin",
                    "generate_tasks": lambda self, context: "plugin",
                    "execute_task": lambda self, task_id, context: "plugin",
                    "generate_index": lambda self, root: {},
                },
            )(),
        )

        decision = reg.select_backend(
            ("generate_spec",),
            requested_backend="plugin",
            policy=policy,
        )

        assert decision.decision_kind == BackendDecisionKind.BLOCK
        assert decision.selected_backend == "plugin"
        assert "plugin selection forbidden" in decision.reason

    def test_select_backend_blocks_when_plugin_missing_and_native_also_missing(
        self,
    ) -> None:
        reg = BackendRegistry()

        class PluginBackend:
            def capability_declaration(self) -> BackendCapabilityDeclaration:
                return BackendCapabilityDeclaration(
                    backend_name="plugin",
                    provided_capabilities=("generate_spec",),
                )

            def generate_spec(self, context: dict) -> str:
                return "plugin"

            def generate_plan(self, context: dict) -> str:
                return "plugin"

            def generate_tasks(self, context: dict) -> str:
                return "plugin"

            def execute_task(self, task_id: str, context: dict) -> str:
                return "plugin"

            def generate_index(self, root: Path) -> dict:
                return {}

        reg.register("plugin", PluginBackend())
        decision = reg.select_backend(("mystery_capability",), requested_backend="plugin")

        assert decision.decision_kind == BackendDecisionKind.BLOCK
        assert decision.selected_backend == "plugin"
        assert decision.missing_capabilities == ("mystery_capability",)
        assert "native_insufficient" in decision.evidence

    def test_select_backend_blocks_when_missing_backend_and_native_also_missing(
        self,
    ) -> None:
        reg = BackendRegistry()
        decision = reg.select_backend(
            ("mystery_capability",),
            requested_backend="plugin",
        )

        assert decision.decision_kind == BackendDecisionKind.BLOCK
        assert decision.selected_backend == "plugin"
        assert decision.missing_capabilities == ("mystery_capability",)
        assert "native_insufficient" in decision.evidence

    def test_select_backend_falls_back_when_plugin_failure_is_safe(self) -> None:
        reg = BackendRegistry()
        reg.register(
            "plugin",
            type(
                "PluginBackend",
                (),
                {
                    "capability_declaration": lambda self: BackendCapabilityDeclaration(
                        backend_name="plugin",
                        provided_capabilities=("generate_spec",),
                    ),
                    "generate_spec": lambda self, context: "plugin",
                    "generate_plan": lambda self, context: "plugin",
                    "generate_tasks": lambda self, context: "plugin",
                    "execute_task": lambda self, task_id, context: "plugin",
                    "generate_index": lambda self, root: {},
                },
            )(),
        )
        failure = BackendFailureEvidence(
            backend_name="plugin",
            error="plugin timed out",
            safe_to_fallback=True,
            evidence=("plugin_timeout",),
        )

        decision = reg.select_backend(
            ("generate_spec",),
            requested_backend="plugin",
            plugin_failure=failure,
        )

        assert decision.decision_kind == BackendDecisionKind.FALLBACK_NATIVE
        assert decision.selected_backend == "native"
        assert decision.failure == failure
        assert "plugin_timeout" in decision.evidence

    def test_select_backend_blocks_when_safe_plugin_failure_cannot_fallback_to_native(
        self,
    ) -> None:
        reg = BackendRegistry()
        reg.register(
            "plugin",
            type(
                "PluginBackend",
                (),
                {
                    "capability_declaration": lambda self: BackendCapabilityDeclaration(
                        backend_name="plugin",
                        provided_capabilities=("generate_spec",),
                    ),
                    "generate_spec": lambda self, context: "plugin",
                    "generate_plan": lambda self, context: "plugin",
                    "generate_tasks": lambda self, context: "plugin",
                    "execute_task": lambda self, task_id, context: "plugin",
                    "generate_index": lambda self, root: {},
                },
            )(),
        )
        failure = BackendFailureEvidence(
            backend_name="plugin",
            error="plugin timed out",
            safe_to_fallback=True,
            evidence=("plugin_timeout",),
        )

        decision = reg.select_backend(
            ("mystery_capability",),
            requested_backend="plugin",
            plugin_failure=failure,
        )

        assert decision.decision_kind == BackendDecisionKind.BLOCK
        assert decision.selected_backend == "plugin"
        assert decision.failure == failure
        assert "native backend does not cover required capabilities" in decision.reason

    def test_select_backend_blocks_when_plugin_failure_is_unsafe(self) -> None:
        reg = BackendRegistry()
        reg.register(
            "plugin",
            type(
                "PluginBackend",
                (),
                {
                    "capability_declaration": lambda self: BackendCapabilityDeclaration(
                        backend_name="plugin",
                        provided_capabilities=("generate_spec",),
                    ),
                    "generate_spec": lambda self, context: "plugin",
                    "generate_plan": lambda self, context: "plugin",
                    "generate_tasks": lambda self, context: "plugin",
                    "execute_task": lambda self, task_id, context: "plugin",
                    "generate_index": lambda self, root: {},
                },
            )(),
        )
        failure = BackendFailureEvidence(
            backend_name="plugin",
            error="plugin crashed",
            safe_to_fallback=False,
            evidence=("plugin_crash",),
        )

        decision = reg.select_backend(
            ("generate_spec",),
            requested_backend="plugin",
            plugin_failure=failure,
        )

        assert decision.decision_kind == BackendDecisionKind.BLOCK
        assert decision.selected_backend == "plugin"
        assert decision.failure == failure
        assert "plugin_crash" in decision.evidence
