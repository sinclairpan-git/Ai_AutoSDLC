"""Shared canonical event rules for telemetry critical control points."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ai_sdlc.telemetry.contracts import TelemetryEvent
from ai_sdlc.telemetry.enums import (
    ActorType,
    CaptureMode,
    Confidence,
    ScopeLevel,
    TelemetryEventStatus,
    TraceLayer,
)

_CANONICAL_EVENT_FIELDS: dict[str, dict[str, Any]] = {
    "gate_hit": {
        "scope_level": ScopeLevel.STEP,
        "trace_layer": TraceLayer.EVALUATION,
        "actor_type": ActorType.FRAMEWORK_RUNTIME,
        "capture_mode": CaptureMode.AUTO,
        "confidence": Confidence.HIGH,
        "status": TelemetryEventStatus.SUCCEEDED,
    },
    "gate_blocked": {
        "scope_level": ScopeLevel.STEP,
        "trace_layer": TraceLayer.EVALUATION,
        "actor_type": ActorType.FRAMEWORK_RUNTIME,
        "capture_mode": CaptureMode.AUTO,
        "confidence": Confidence.HIGH,
        "status": TelemetryEventStatus.BLOCKED,
    },
    "audit_report_generated": {
        "scope_level": ScopeLevel.RUN,
        "trace_layer": TraceLayer.EVALUATION,
        "actor_type": ActorType.FRAMEWORK_RUNTIME,
        "capture_mode": CaptureMode.AUTO,
        "confidence": Confidence.HIGH,
        "status": TelemetryEventStatus.SUCCEEDED,
    },
}


def build_canonical_control_point_event(
    control_point_name: str,
    *,
    goal_session_id: str,
    workflow_run_id: str | None = None,
    step_id: str | None = None,
) -> TelemetryEvent:
    """Construct the canonical event shape for a supported control point."""
    payload = canonical_control_point_event_fields(control_point_name)
    if payload is None:
        raise ValueError(f"unsupported canonical control point {control_point_name!r}")
    return TelemetryEvent(
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
        **payload,
    )


def canonical_control_point_event_fields(
    control_point_name: str,
) -> dict[str, Any] | None:
    """Return the canonical event fields for a supported control point."""
    payload = _CANONICAL_EVENT_FIELDS.get(control_point_name)
    if payload is None:
        return None
    return dict(payload)


def payload_matches_canonical_control_point_event(
    control_point_name: str,
    payload: Mapping[str, object],
) -> bool:
    """Return True when a raw payload matches the canonical control-point event shape."""
    expected = canonical_control_point_event_fields(control_point_name)
    if expected is None:
        return False
    return all(payload.get(field_name) == _payload_value(value) for field_name, value in expected.items())


def _payload_value(value: object) -> object:
    return getattr(value, "value", value)
