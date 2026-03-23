"""Backend protocol, native implementation, and registry."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from ai_sdlc.generators.doc_gen import DocScaffolder
from ai_sdlc.generators.index_gen import generate_index as gen_index

logger = logging.getLogger(__name__)


# ── protocol ──


@runtime_checkable
class BackendProtocol(Protocol):
    """Interface that all SDLC backends must implement."""

    def generate_spec(self, context: dict[str, Any]) -> str: ...
    def generate_plan(self, context: dict[str, Any]) -> str: ...
    def generate_tasks(self, context: dict[str, Any]) -> str: ...
    def execute_task(self, task_id: str, context: dict[str, Any]) -> str: ...
    def generate_index(self, root: Path) -> dict[str, Any]: ...


# ── native backend ──


class NativeBackend:
    """Default backend using file-system-based generators.

    Wraps existing generators (DocScaffolder, index_gen) into
    the BackendProtocol interface. For execute_task, returns
    "pending" since actual execution is done by the AI Agent.
    """

    def __init__(self) -> None:
        self._scaffolder = DocScaffolder()

    def generate_spec(self, context: dict[str, Any]) -> str:
        """Render spec template with given context."""
        return self._scaffolder.render("spec.md.j2", context)

    def generate_plan(self, context: dict[str, Any]) -> str:
        """Render plan template with given context."""
        return self._scaffolder.render("plan.md.j2", context)

    def generate_tasks(self, context: dict[str, Any]) -> str:
        """Render tasks template with given context."""
        return self._scaffolder.render("tasks.md.j2", context)

    def execute_task(self, task_id: str, context: dict[str, Any]) -> str:
        """Return pending — Agent handles actual execution."""
        logger.debug("Native backend: task %s execution delegated to Agent", task_id)
        return "pending"

    def generate_index(self, root: Path) -> dict[str, Any]:
        """Generate project index using built-in scanner."""
        return gen_index(root)


# ── registry ──

_DEFAULT_NAME = "native"


class BackendNotFoundError(Exception):
    """Raised when a requested backend is not registered."""


class BackendRegistry:
    """Registry for SDLC execution backends.

    The native backend is always registered by default.
    Plugin backends can be registered to override or extend it.
    """

    def __init__(self) -> None:
        self._backends: dict[str, BackendProtocol] = {}
        self._default = _DEFAULT_NAME
        self.register(_DEFAULT_NAME, NativeBackend())

    def register(self, name: str, backend: BackendProtocol) -> None:
        """Register a backend by name."""
        self._backends[name] = backend
        logger.info("Backend registered: %s", name)

    def get(self, name: str) -> BackendProtocol:
        """Retrieve a backend by name.

        Raises:
            BackendNotFoundError: If the backend is not registered.
        """
        if name not in self._backends:
            raise BackendNotFoundError(f"Backend not found: {name}")
        return self._backends[name]

    def get_default(self) -> BackendProtocol:
        """Return the default backend (native unless overridden)."""
        return self._backends[self._default]

    def set_default(self, name: str) -> None:
        """Set the default backend.

        Raises:
            BackendNotFoundError: If the backend is not registered.
        """
        if name not in self._backends:
            raise BackendNotFoundError(f"Cannot set default to unregistered: {name}")
        self._default = name

    @property
    def available(self) -> list[str]:
        """Return sorted list of registered backend names."""
        return sorted(self._backends)
