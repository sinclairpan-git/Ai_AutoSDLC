"""Unit tests for backend protocol, native backend, and registry."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.backends.native import (
    BackendNotFoundError,
    BackendProtocol,
    BackendRegistry,
    NativeBackend,
)


class TestBackendProtocol:
    def test_native_is_backend(self) -> None:
        assert isinstance(NativeBackend(), BackendProtocol)


class TestNativeBackend:
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
