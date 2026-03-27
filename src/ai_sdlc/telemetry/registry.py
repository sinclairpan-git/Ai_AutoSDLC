"""Critical Control Point registry for telemetry governance."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CriticalControlPoint(BaseModel):
    """A telemetry critical control point and its minimum evidence closure."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str
    primary_writer: str
    minimum_evidence_closure: tuple[str, ...] = Field(default_factory=tuple)
    enabled: bool = True
    description: str = ""


_DEFAULT_CONTROL_POINTS: dict[str, dict[str, Any]] = {
    "session_created": {
        "name": "session_created",
        "primary_writer": "runtime/dispatcher facade",
        "minimum_evidence_closure": ("event",),
    },
    "workflow_run_started": {
        "name": "workflow_run_started",
        "primary_writer": "runner",
        "minimum_evidence_closure": ("event",),
    },
    "workflow_run_ended": {
        "name": "workflow_run_ended",
        "primary_writer": "runner",
        "minimum_evidence_closure": ("event",),
    },
    "workflow_step_transitioned": {
        "name": "workflow_step_transitioned",
        "primary_writer": "dispatcher/state-machine layer",
        "minimum_evidence_closure": ("event",),
    },
    "command_completed": {
        "name": "command_completed",
        "primary_writer": "tool/runtime hook",
        "minimum_evidence_closure": ("event", "stdout_stderr_evidence"),
    },
    "patch_applied": {
        "name": "patch_applied",
        "primary_writer": "tool/runtime hook",
        "minimum_evidence_closure": ("event", "diff_file_evidence"),
    },
    "file_written": {
        "name": "file_written",
        "primary_writer": "tool/runtime hook",
        "minimum_evidence_closure": ("event", "diff_file_evidence"),
    },
    "test_result_recorded": {
        "name": "test_result_recorded",
        "primary_writer": "tool/evaluation hook",
        "minimum_evidence_closure": ("event", "test_result_evidence"),
    },
    "gate_hit": {
        "name": "gate_hit",
        "primary_writer": "runner/dispatcher gate hook",
        "minimum_evidence_closure": ("event", "gate_reason_evidence"),
    },
    "gate_blocked": {
        "name": "gate_blocked",
        "primary_writer": "runner/dispatcher gate hook",
        "minimum_evidence_closure": ("event", "gate_reason_evidence"),
    },
    "audit_report_generated": {
        "name": "audit_report_generated",
        "primary_writer": "governance publisher",
        "minimum_evidence_closure": ("event", "artifact_ref"),
    },
}


class CCPRegistry(BaseModel):
    """Config-driven registry of critical control points."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    control_points: dict[str, CriticalControlPoint] = Field(default_factory=dict)

    @classmethod
    def from_config(cls, config: dict[str, Any] | None = None) -> CCPRegistry:
        payload = {
            "control_points": {
                name: dict(values) for name, values in _DEFAULT_CONTROL_POINTS.items()
            }
        }
        if config and config.get("control_points"):
            for name, override in config["control_points"].items():
                default_cp = payload["control_points"].get(name, {})
                payload["control_points"][name] = {**default_cp, **dict(override)}
        return cls.model_validate(payload)


def build_default_ccp_registry(config: dict[str, Any] | None = None) -> CCPRegistry:
    """Return the frozen V1 CCP registry defaults."""
    return CCPRegistry.from_config(config)
