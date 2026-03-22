"""Backend protocol — defines the interface for SDLC execution backends (FR-084)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BackendProtocol(Protocol):
    """Interface that all SDLC backends must implement.

    The Native backend is the default. Plugin backends can override
    specific methods while falling back to Native for the rest.
    """

    def generate_spec(self, context: dict[str, Any]) -> str:
        """Generate a spec document from context.

        Args:
            context: Template context variables.

        Returns:
            Rendered spec content as string.
        """
        ...

    def generate_plan(self, context: dict[str, Any]) -> str:
        """Generate a plan document from context.

        Args:
            context: Template context variables.

        Returns:
            Rendered plan content as string.
        """
        ...

    def generate_tasks(self, context: dict[str, Any]) -> str:
        """Generate a tasks document from context.

        Args:
            context: Template context variables.

        Returns:
            Rendered tasks content as string.
        """
        ...

    def execute_task(self, task_id: str, context: dict[str, Any]) -> str:
        """Execute a single task (or return its status).

        Args:
            task_id: The task identifier.
            context: Execution context.

        Returns:
            Task status string (e.g. "pending", "completed").
        """
        ...

    def generate_index(self, root: Path) -> dict[str, Any]:
        """Generate project index from filesystem.

        Args:
            root: Project root directory.

        Returns:
            Index data dictionary.
        """
        ...
