"""Thin backend routing coordinator for document generation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

_BACKEND_ROUTE_BYPASS_KEY = "_ai_sdlc_backend_route_bypass"

if TYPE_CHECKING:  # pragma: no cover - import cycle guard for typing only.
    from ai_sdlc.backends.native import (
        BackendFailureEvidence,
        BackendRegistry,
        BackendSelectionDecision,
        BackendSelectionPolicy,
    )


class BackendRoutingBlockedError(RuntimeError):
    """Raised when backend selection blocks a routed document generation request."""

    def __init__(self, decision: BackendSelectionDecision) -> None:
        super().__init__(decision.reason)
        self.decision = decision


class BackendRoutingExecutionError(RuntimeError):
    """Raised when the selected backend fails during routed document generation."""

    def __init__(self, backend_name: str, error: str) -> None:
        super().__init__(error)
        self.backend_name = backend_name
        self.error = error


class BackendExecutionError(RuntimeError):
    """Typed backend execution failure that may safely fall back."""

    def __init__(
        self,
        message: str,
        *,
        backend_name: str,
        safe_to_fallback: bool,
        evidence: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message)
        self.backend_name = backend_name
        self.safe_to_fallback = safe_to_fallback
        self.evidence = evidence


class BackendRoutingOperation(str, Enum):
    """Supported routed document generation operations."""

    SPEC = "generate_spec"
    PLAN = "generate_plan"
    TASKS = "generate_tasks"


@dataclass(frozen=True, slots=True)
class RoutedDocument:
    """Rendered document content and its backend decision."""

    content: str
    backend_decision: BackendSelectionDecision | None = None


class BackendRoutingCoordinator:
    """Coordinate runtime backend selection for document generation."""

    _required_capabilities: dict[BackendRoutingOperation, tuple[str, ...]] = {
        BackendRoutingOperation.SPEC: ("generate_spec",),
        BackendRoutingOperation.PLAN: ("generate_plan",),
        BackendRoutingOperation.TASKS: ("generate_tasks",),
    }

    def __init__(
        self,
        registry: BackendRegistry | None = None,
        *,
        requested_backend: str | None = None,
        policy: BackendSelectionPolicy | None = None,
    ) -> None:
        import ai_sdlc.backends.native as native_backend

        self._registry = registry or native_backend.BackendRegistry()
        self._requested_backend = requested_backend
        self._policy = policy or native_backend.BackendSelectionPolicy()

    def generate_spec(
        self,
        context: dict[str, Any],
        *,
        requested_backend: str | None = None,
        policy: BackendSelectionPolicy | None = None,
    ) -> RoutedDocument:
        return self._route(BackendRoutingOperation.SPEC, context, requested_backend, policy)

    def generate_plan(
        self,
        context: dict[str, Any],
        *,
        requested_backend: str | None = None,
        policy: BackendSelectionPolicy | None = None,
    ) -> RoutedDocument:
        return self._route(BackendRoutingOperation.PLAN, context, requested_backend, policy)

    def generate_tasks(
        self,
        context: dict[str, Any],
        *,
        requested_backend: str | None = None,
        policy: BackendSelectionPolicy | None = None,
    ) -> RoutedDocument:
        return self._route(BackendRoutingOperation.TASKS, context, requested_backend, policy)

    def _route(
        self,
        operation: BackendRoutingOperation,
        context: dict[str, Any],
        requested_backend: str | None,
        policy: BackendSelectionPolicy | None,
    ) -> RoutedDocument:
        from ai_sdlc.backends.native import BackendDecisionKind, BackendFailureEvidence

        required_capabilities = self._required_capabilities[operation]
        selection = self._registry.select_backend(
            required_capabilities,
            requested_backend=requested_backend or self._requested_backend,
            policy=policy or self._policy,
        )
        if selection.decision_kind == BackendDecisionKind.BLOCK:
            raise BackendRoutingBlockedError(selection)

        return self._invoke_selected_backend(
            operation=operation,
            context=context,
            selection=selection,
            policy=policy or self._policy,
            failure_cls=BackendFailureEvidence,
        )

    def _invoke_selected_backend(
        self,
        *,
        operation: BackendRoutingOperation,
        context: dict[str, Any],
        selection: BackendSelectionDecision,
        policy: BackendSelectionPolicy,
        failure_cls: type[BackendFailureEvidence],
    ) -> RoutedDocument:
        backend_method_name = operation.value
        backend = self._registry.get(selection.selected_backend)
        render_context = dict(context)
        render_context[_BACKEND_ROUTE_BYPASS_KEY] = True
        try:
            content = getattr(backend, backend_method_name)(render_context)
        except BackendExecutionError as exc:
            return self._handle_backend_failure(
                operation=operation,
                context=render_context,
                selection=selection,
                policy=policy,
                failure=failure_cls(
                    backend_name=exc.backend_name,
                    error=str(exc),
                    safe_to_fallback=exc.safe_to_fallback,
                    evidence=exc.evidence,
                ),
            )
        except Exception as exc:
            if selection.selected_backend == self._registry.get_default().capability_declaration().backend_name:
                raise BackendRoutingExecutionError(selection.selected_backend, str(exc)) from exc
            return self._handle_backend_failure(
                operation=operation,
                context=render_context,
                selection=selection,
                policy=policy,
                failure=failure_cls(
                    backend_name=selection.selected_backend,
                    error=str(exc),
                    safe_to_fallback=False,
                    evidence=(exc.__class__.__name__,),
                ),
            )

        return RoutedDocument(content=content, backend_decision=selection)

    def _handle_backend_failure(
        self,
        *,
        operation: BackendRoutingOperation,
        context: dict[str, Any],
        selection: BackendSelectionDecision,
        policy: BackendSelectionPolicy,
        failure: BackendFailureEvidence,
    ) -> RoutedDocument:
        from ai_sdlc.backends.native import BackendDecisionKind

        required_capabilities = self._required_capabilities[operation]
        retry = self._registry.select_backend(
            required_capabilities,
            requested_backend=selection.selected_backend,
            policy=policy,
            plugin_failure=failure,
        )
        if retry.decision_kind == BackendDecisionKind.BLOCK:
            raise BackendRoutingBlockedError(retry)
        if retry.selected_backend == selection.selected_backend:
            raise BackendRoutingExecutionError(selection.selected_backend, failure.error)

        backend = self._registry.get(retry.selected_backend)
        try:
            content = getattr(backend, operation.value)(context)
        except Exception as exc:
            raise BackendRoutingExecutionError(retry.selected_backend, str(exc)) from exc
        return RoutedDocument(content=content, backend_decision=retry)
