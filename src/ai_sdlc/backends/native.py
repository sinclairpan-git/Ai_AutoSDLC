"""Native backend — default file-system-driven implementation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from ai_sdlc.generators.doc_scaffold import DocScaffolder
from ai_sdlc.generators.index_gen import generate_index as gen_index

logger = logging.getLogger(__name__)


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
