"""Unit tests for telemetry runtime policy resolution."""

from __future__ import annotations

import importlib

import pytest

from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.telemetry.enums import ScopeLevel, TelemetryMode, TelemetryProfile


def _load_policy_module():
    try:
        return importlib.import_module("ai_sdlc.telemetry.policy")
    except ModuleNotFoundError as exc:  # pragma: no cover - red phase expectation
        pytest.fail(f"missing telemetry policy module: {exc}")


def test_resolve_runtime_telemetry_policy_uses_project_defaults() -> None:
    policy_module = _load_policy_module()
    policy = policy_module.resolve_runtime_telemetry_policy(ProjectConfig())

    assert policy.profile is TelemetryProfile.SELF_HOSTING
    assert policy.mode is TelemetryMode.LITE
    assert policy.mode_change is None


def test_resolve_runtime_telemetry_policy_records_explicit_mode_change() -> None:
    policy_module = _load_policy_module()
    policy = policy_module.resolve_runtime_telemetry_policy(
        ProjectConfig(
            telemetry_profile=TelemetryProfile.SELF_HOSTING,
            telemetry_mode=TelemetryMode.LITE,
        ),
        mode_override=TelemetryMode.STRICT,
        changed_by="runner",
        reason="verify-stage escalation",
        applicable_scope=ScopeLevel.RUN,
    )

    assert policy.profile is TelemetryProfile.SELF_HOSTING
    assert policy.mode is TelemetryMode.STRICT
    assert policy.mode_change is not None
    assert policy.mode_change.old_mode is TelemetryMode.LITE
    assert policy.mode_change.new_mode is TelemetryMode.STRICT
    assert policy.mode_change.changed_by == "runner"
    assert policy.mode_change.reason == "verify-stage escalation"
    assert policy.mode_change.applicable_scope is ScopeLevel.RUN
