"""Backend protocol, native implementation, and registry."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from ai_sdlc.generators.doc_gen import DocScaffolder
from ai_sdlc.generators.index_gen import generate_index as gen_index
from ai_sdlc.telemetry.enums import TelemetryEventStatus
from ai_sdlc.telemetry.runtime import RuntimeTelemetry

logger = logging.getLogger(__name__)

BACKEND_CAPABILITY_TOKEN = "backend_capability"
BACKEND_DELEGATION_TOKEN = "delegation"
BACKEND_FALLBACK_TOKEN = "fallback"


# ── protocol ──


@runtime_checkable
class BackendProtocol(Protocol):
    """Interface that all SDLC backends must implement."""

    def capability_declaration(self) -> BackendCapabilityDeclaration: ...
    def generate_spec(self, context: dict[str, Any]) -> str: ...
    def generate_plan(self, context: dict[str, Any]) -> str: ...
    def generate_tasks(self, context: dict[str, Any]) -> str: ...
    def execute_task(self, task_id: str, context: dict[str, Any]) -> str: ...
    def generate_index(self, root: Path) -> dict[str, Any]: ...


class BackendDecisionKind(str, Enum):
    """Outcome of backend selection."""

    DELEGATE = "delegate"
    FALLBACK_NATIVE = "fallback_native"
    BLOCK = "block"


@dataclass(frozen=True, slots=True)
class BackendCapabilityDeclaration:
    """Formal backend capability declaration contract."""

    backend_name: str
    provided_capabilities: tuple[str, ...]
    delegation: tuple[str, ...] = (BACKEND_DELEGATION_TOKEN,)
    fallback: tuple[str, ...] = (BACKEND_FALLBACK_TOKEN,)
    can_delegate: bool = True
    can_fallback_to_native: bool = True

    def covers(self, required_capabilities: tuple[str, ...]) -> bool:
        """Return True when the declaration covers every required capability."""
        provided = set(self.provided_capabilities)
        return all(capability in provided for capability in required_capabilities)

    def evidence_tokens(self) -> tuple[str, ...]:
        """Return literal markers used by verify / close-check surfaces."""
        return (
            BACKEND_CAPABILITY_TOKEN,
            *self.provided_capabilities,
            *self.delegation,
            *self.fallback,
        )


@dataclass(frozen=True, slots=True)
class BackendSelectionPolicy:
    """Policy gates that influence backend selection."""

    allow_plugin: bool = True
    allow_native_fallback: bool = True


@dataclass(frozen=True, slots=True)
class BackendFailureEvidence:
    """Structured failure evidence for a plugin backend attempt."""

    backend_name: str
    error: str
    safe_to_fallback: bool
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class BackendSelectionDecision:
    """Structured backend selection result readable by later gates."""

    decision_kind: BackendDecisionKind
    requested_backend: str
    selected_backend: str
    required_capabilities: tuple[str, ...]
    available_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    policy_allow_plugin: bool
    policy_allow_native_fallback: bool
    reason: str
    evidence: tuple[str, ...]
    capability_declaration: BackendCapabilityDeclaration | None = None
    failure: BackendFailureEvidence | None = None

    def to_status_view(self) -> dict[str, object]:
        """Return a read-only summary for verify / close-check consumers."""
        return {
            "decision_kind": self.decision_kind.value,
            "requested_backend": self.requested_backend,
            "selected_backend": self.selected_backend,
            "required_capabilities": list(self.required_capabilities),
            "available_capabilities": list(self.available_capabilities),
            "missing_capabilities": list(self.missing_capabilities),
            "policy_allow_plugin": self.policy_allow_plugin,
            "policy_allow_native_fallback": self.policy_allow_native_fallback,
            "reason": self.reason,
            "evidence": list(self.evidence),
            "capability_declaration": (
                self.capability_declaration.backend_name
                if self.capability_declaration is not None
                else None
            ),
            "safe_to_fallback": (
                self.failure.safe_to_fallback if self.failure is not None else None
            ),
            "failure_error": self.failure.error if self.failure is not None else None,
        }


# ── native backend ──


class NativeBackend:
    """Default backend using file-system-based generators.

    Wraps existing generators (DocScaffolder, index_gen) into
    the BackendProtocol interface. For execute_task, returns
    "pending" since actual execution is done by the AI Agent.
    """

    def __init__(self) -> None:
        self._scaffolder = DocScaffolder()

    def capability_declaration(self) -> BackendCapabilityDeclaration:
        """Declare the native backend's full built-in capability surface."""
        return BackendCapabilityDeclaration(
            backend_name=_DEFAULT_NAME,
            provided_capabilities=(
                "generate_spec",
                "generate_plan",
                "generate_tasks",
                "execute_task",
                "generate_index",
            ),
        )

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
        self._record_delegation_boundary(task_id, context)
        return "pending"

    def generate_index(self, root: Path) -> dict[str, Any]:
        """Generate project index using built-in scanner."""
        return gen_index(root)

    def _record_delegation_boundary(self, task_id: str, context: dict[str, Any]) -> None:
        telemetry = context.get("telemetry")
        step_id = context.get("step_id")
        worker_id = context.get("worker_id")
        if not isinstance(telemetry, RuntimeTelemetry):
            return
        worker_token = worker_id if isinstance(worker_id, str) and worker_id else "worker-unknown"
        telemetry.record_tool_event(
            step_id=step_id,
            status=TelemetryEventStatus.STARTED,
        )
        telemetry.record_tool_evidence(
            step_id=step_id,
            locator=f"trace://native-delegation/{task_id}/{worker_token}",
            digest=f"sha256:{sha256(f'{task_id}:{worker_token}:pending'.encode()).hexdigest()}",
        )


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

    def capability_declaration(self, name: str) -> BackendCapabilityDeclaration:
        """Return the formal capability declaration for a registered backend."""
        return self.get(name).capability_declaration()

    def select_backend(
        self,
        required_capabilities: tuple[str, ...],
        *,
        requested_backend: str | None = None,
        policy: BackendSelectionPolicy | None = None,
        plugin_failure: BackendFailureEvidence | None = None,
    ) -> BackendSelectionDecision:
        """Select a backend using capability coverage, policy, and safety rules."""
        policy = policy or BackendSelectionPolicy()
        backend_name = requested_backend or self._default
        native_backend = self.get_default()
        native_declaration = native_backend.capability_declaration()
        native_missing_capabilities = self._missing_capabilities(
            required_capabilities,
            native_declaration.provided_capabilities,
        )
        native_can_cover = not native_missing_capabilities

        if backend_name != self._default and not policy.allow_plugin:
            return self._fallback_or_block(
                requested_backend=backend_name,
                required_capabilities=required_capabilities,
                policy=policy,
                reason="plugin selection forbidden by policy",
                evidence=("policy_forbidden", BACKEND_DELEGATION_TOKEN),
                native_declaration=native_declaration,
                native_missing_capabilities=native_missing_capabilities,
                native_can_cover=native_can_cover,
            )

        if backend_name not in self._backends:
            return self._fallback_or_block(
                requested_backend=backend_name,
                required_capabilities=required_capabilities,
                policy=policy,
                reason=f"backend not registered: {backend_name}",
                evidence=("missing_backend", backend_name),
                native_declaration=native_declaration,
                native_missing_capabilities=native_missing_capabilities,
                native_can_cover=native_can_cover,
            )

        backend = self._backends[backend_name]
        declaration = backend.capability_declaration()
        missing_capabilities = tuple(
            capability
            for capability in required_capabilities
            if capability not in declaration.provided_capabilities
        )

        if plugin_failure is not None:
            if (
                plugin_failure.safe_to_fallback
                and policy.allow_native_fallback
                and native_can_cover
            ):
                return self._build_decision(
                    decision_kind=BackendDecisionKind.FALLBACK_NATIVE,
                    requested_backend=backend_name,
                    selected_backend=self._default,
                    required_capabilities=required_capabilities,
                    available_capabilities=native_declaration.provided_capabilities,
                    missing_capabilities=(),
                    policy=policy,
                    reason=f"plugin failure safe to fallback: {plugin_failure.error}",
                    evidence=(
                        BACKEND_FALLBACK_TOKEN,
                        *plugin_failure.evidence,
                        plugin_failure.backend_name,
                    ),
                    capability_declaration=native_declaration,
                    failure=plugin_failure,
                )
            if (
                plugin_failure.safe_to_fallback
                and policy.allow_native_fallback
                and not native_can_cover
            ):
                return self._build_decision(
                    decision_kind=BackendDecisionKind.BLOCK,
                    requested_backend=backend_name,
                    selected_backend=self._default,
                    required_capabilities=required_capabilities,
                    available_capabilities=native_declaration.provided_capabilities,
                    missing_capabilities=native_missing_capabilities,
                    policy=policy,
                    reason=(
                        "plugin failure is safe to fallback, but native backend "
                        "does not cover required capabilities"
                    ),
                    evidence=(
                        BACKEND_CAPABILITY_TOKEN,
                        BACKEND_FALLBACK_TOKEN,
                        plugin_failure.backend_name,
                        *plugin_failure.evidence,
                    ),
                    capability_declaration=native_declaration,
                    failure=plugin_failure,
                )
            if plugin_failure.safe_to_fallback and not policy.allow_native_fallback:
                return self._build_decision(
                    decision_kind=BackendDecisionKind.BLOCK,
                    requested_backend=backend_name,
                    selected_backend=backend_name,
                    required_capabilities=required_capabilities,
                    available_capabilities=declaration.provided_capabilities,
                    missing_capabilities=(),
                    policy=policy,
                    reason=(
                        "plugin failure is safe to fallback, but native fallback "
                        "is disabled by policy"
                    ),
                    evidence=(
                        BACKEND_CAPABILITY_TOKEN,
                        BACKEND_DELEGATION_TOKEN,
                        plugin_failure.backend_name,
                        "policy_forbidden",
                        *plugin_failure.evidence,
                    ),
                    capability_declaration=declaration,
                    failure=plugin_failure,
                )
            return self._build_decision(
                decision_kind=BackendDecisionKind.BLOCK,
                requested_backend=backend_name,
                selected_backend=backend_name,
                required_capabilities=required_capabilities,
                available_capabilities=declaration.provided_capabilities,
                missing_capabilities=missing_capabilities,
                policy=policy,
                reason=(
                    f"plugin failure unsafe to fallback: {plugin_failure.error}"
                    + (
                        ""
                        if native_can_cover
                        else "; native backend also cannot replace required capabilities"
                    )
                ),
                evidence=(
                    BACKEND_CAPABILITY_TOKEN,
                    BACKEND_DELEGATION_TOKEN,
                    plugin_failure.backend_name,
                    *plugin_failure.evidence,
                    *(
                        ()
                        if native_can_cover
                        else ("native_insufficient", *native_missing_capabilities)
                    ),
                ),
                capability_declaration=declaration,
                failure=plugin_failure,
            )

        if missing_capabilities:
            if policy.allow_native_fallback and native_can_cover:
                return self._build_decision(
                    decision_kind=BackendDecisionKind.FALLBACK_NATIVE,
                    requested_backend=backend_name,
                    selected_backend=self._default,
                    required_capabilities=required_capabilities,
                    available_capabilities=native_declaration.provided_capabilities,
                    missing_capabilities=native_missing_capabilities,
                    policy=policy,
                    reason=(
                        "plugin capability coverage incomplete: "
                        f"{', '.join(missing_capabilities)}"
                    ),
                    evidence=(
                        BACKEND_CAPABILITY_TOKEN,
                        BACKEND_FALLBACK_TOKEN,
                        backend_name,
                        *declaration.evidence_tokens(),
                    ),
                    capability_declaration=native_declaration,
                )
            if not policy.allow_native_fallback:
                return self._build_decision(
                    decision_kind=BackendDecisionKind.BLOCK,
                    requested_backend=backend_name,
                    selected_backend=backend_name,
                    required_capabilities=required_capabilities,
                    available_capabilities=declaration.provided_capabilities,
                    missing_capabilities=missing_capabilities,
                    policy=policy,
                    reason=(
                        "plugin capability coverage incomplete and native fallback "
                        f"disabled: {', '.join(missing_capabilities)}"
                    ),
                    evidence=(
                        *declaration.evidence_tokens(),
                        "policy_forbidden",
                        BACKEND_FALLBACK_TOKEN,
                    ),
                    capability_declaration=declaration,
                )
            return self._build_decision(
                decision_kind=BackendDecisionKind.BLOCK,
                requested_backend=backend_name,
                selected_backend=backend_name,
                required_capabilities=required_capabilities,
                available_capabilities=declaration.provided_capabilities,
                missing_capabilities=native_missing_capabilities,
                policy=policy,
                reason=(
                    "plugin capability coverage incomplete and native fallback disabled "
                    "or native backend cannot cover required capabilities: "
                    f"{', '.join(native_missing_capabilities)}"
                ),
                evidence=(
                    *declaration.evidence_tokens(),
                    *native_declaration.evidence_tokens(),
                    "native_insufficient",
                    *native_missing_capabilities,
                ),
                capability_declaration=declaration,
            )

        return self._build_decision(
            decision_kind=BackendDecisionKind.DELEGATE,
            requested_backend=backend_name,
            selected_backend=backend_name,
            required_capabilities=required_capabilities,
            available_capabilities=declaration.provided_capabilities,
            missing_capabilities=(),
            policy=policy,
            reason=f"backend {backend_name} covers all required capabilities",
            evidence=(
                BACKEND_CAPABILITY_TOKEN,
                BACKEND_DELEGATION_TOKEN,
                backend_name,
                *declaration.evidence_tokens(),
            ),
            capability_declaration=declaration,
        )

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

    def _fallback_or_block(
        self,
        *,
        requested_backend: str,
        required_capabilities: tuple[str, ...],
        policy: BackendSelectionPolicy,
        reason: str,
        evidence: tuple[str, ...],
        native_declaration: BackendCapabilityDeclaration,
        native_missing_capabilities: tuple[str, ...],
        native_can_cover: bool,
    ) -> BackendSelectionDecision:
        if policy.allow_native_fallback and native_can_cover:
            return self._build_decision(
                decision_kind=BackendDecisionKind.FALLBACK_NATIVE,
                requested_backend=requested_backend,
                selected_backend=self._default,
                required_capabilities=required_capabilities,
                available_capabilities=native_declaration.provided_capabilities,
                missing_capabilities=(),
                policy=policy,
                reason=reason,
                evidence=(BACKEND_FALLBACK_TOKEN, *evidence, BACKEND_DELEGATION_TOKEN),
                capability_declaration=native_declaration,
            )
        return self._build_decision(
            decision_kind=BackendDecisionKind.BLOCK,
            requested_backend=requested_backend,
            selected_backend=requested_backend,
            required_capabilities=required_capabilities,
            available_capabilities=native_declaration.provided_capabilities,
            missing_capabilities=native_missing_capabilities,
            policy=policy,
            reason=(
                reason
                if native_can_cover
                else "native backend does not cover required capabilities: "
                f"{', '.join(native_missing_capabilities)}"
            ),
            evidence=evidence
            + (
                ()
                if native_can_cover
                else ("native_insufficient", *native_missing_capabilities)
            ),
            capability_declaration=native_declaration if native_can_cover else None,
        )

    @staticmethod
    def _build_decision(
        *,
        decision_kind: BackendDecisionKind,
        requested_backend: str,
        selected_backend: str,
        required_capabilities: tuple[str, ...],
        available_capabilities: tuple[str, ...],
        missing_capabilities: tuple[str, ...],
        policy: BackendSelectionPolicy,
        reason: str,
        evidence: tuple[str, ...],
        capability_declaration: BackendCapabilityDeclaration | None = None,
        failure: BackendFailureEvidence | None = None,
    ) -> BackendSelectionDecision:
        return BackendSelectionDecision(
            decision_kind=decision_kind,
            requested_backend=requested_backend,
            selected_backend=selected_backend,
            required_capabilities=required_capabilities,
            available_capabilities=available_capabilities,
            missing_capabilities=missing_capabilities,
            policy_allow_plugin=policy.allow_plugin,
            policy_allow_native_fallback=policy.allow_native_fallback,
            reason=reason,
            evidence=evidence,
            capability_declaration=capability_declaration,
            failure=failure,
        )

    @staticmethod
    def _missing_capabilities(
        required_capabilities: tuple[str, ...],
        provided_capabilities: tuple[str, ...],
    ) -> tuple[str, ...]:
        provided = set(provided_capabilities)
        return tuple(
            capability
            for capability in required_capabilities
            if capability not in provided
        )
