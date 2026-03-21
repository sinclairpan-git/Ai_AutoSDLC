"""Gate infrastructure — protocol and registry for stage gates."""

from __future__ import annotations

import logging
from typing import Any, Protocol

from ai_sdlc.models.gate import GateResult

logger = logging.getLogger(__name__)


class GateProtocol(Protocol):
    """Protocol that all gate implementations must satisfy."""

    def check(self, context: dict[str, Any]) -> GateResult: ...


class GateRegistry:
    """Registry for stage gate implementations."""

    def __init__(self) -> None:
        self._gates: dict[str, GateProtocol] = {}

    def register(self, stage: str, gate: GateProtocol) -> None:
        """Register a gate for a pipeline stage."""
        self._gates[stage] = gate

    def get(self, stage: str) -> GateProtocol | None:
        """Retrieve the gate for a stage, or None if not registered."""
        return self._gates.get(stage)

    def check(self, stage: str, context: dict[str, Any]) -> GateResult:
        """Run the gate check for a stage.

        Raises:
            KeyError: If no gate is registered for the stage.
        """
        gate = self._gates.get(stage)
        if gate is None:
            raise KeyError(f"No gate registered for stage: {stage}")
        return gate.check(context)

    @property
    def stages(self) -> list[str]:
        """Return all registered stage names."""
        return list(self._gates.keys())
