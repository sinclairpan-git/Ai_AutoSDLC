"""Gate infrastructure — protocol, registry, and stage-to-gate mapping."""

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


def _build_gate_by_stage() -> dict[str, GateProtocol]:
    """Lazily construct the canonical stage-name → gate-instance mapping."""
    from ai_sdlc.gates.extra_gates import KnowledgeGate, ParallelGate, PostmortemGate
    from ai_sdlc.gates.pipeline_gates import (
        CloseGate,
        DecomposeGate,
        DesignGate,
        ExecuteGate,
        InitGate,
        RefineGate,
        VerifyGate,
    )

    return {
        "init": InitGate(),
        "refine": RefineGate(),
        "design": DesignGate(),
        "decompose": DecomposeGate(),
        "verify": VerifyGate(),
        "execute": ExecuteGate(),
        "close": CloseGate(),
        "knowledge_check": KnowledgeGate(),
        "parallel_check": ParallelGate(),
        "postmortem": PostmortemGate(),
    }


def get_gate_by_stage() -> dict[str, GateProtocol]:
    """Return the canonical stage-name → gate-instance mapping.

    The mapping is built on first call and cached for the process lifetime.
    """
    global _GATE_BY_STAGE  # noqa: PLW0603
    if _GATE_BY_STAGE is None:
        _GATE_BY_STAGE = _build_gate_by_stage()
    return _GATE_BY_STAGE


_GATE_BY_STAGE: dict[str, GateProtocol] | None = None
