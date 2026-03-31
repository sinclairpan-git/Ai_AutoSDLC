"""Telemetry profile/mode resolution for runtime entrypoints."""

from __future__ import annotations

from dataclasses import dataclass

from ai_sdlc.models.project import ProjectConfig
from ai_sdlc.telemetry.clock import utc_now_z
from ai_sdlc.telemetry.contracts import ModeChangeRecord
from ai_sdlc.telemetry.enums import ScopeLevel, TelemetryMode, TelemetryProfile


@dataclass(frozen=True)
class ResolvedRuntimeTelemetryPolicy:
    """Resolved telemetry profile/mode plus any explicit transition record."""

    profile: TelemetryProfile
    mode: TelemetryMode
    mode_change: ModeChangeRecord | None = None


def resolve_runtime_telemetry_policy(
    config: ProjectConfig,
    *,
    mode_override: TelemetryMode | None = None,
    changed_by: str = "runtime",
    reason: str = "explicit mode override",
    applicable_scope: ScopeLevel = ScopeLevel.RUN,
) -> ResolvedRuntimeTelemetryPolicy:
    """Resolve the active runtime telemetry profile and mode."""
    profile = config.telemetry_profile
    mode = mode_override or config.telemetry_mode
    mode_change: ModeChangeRecord | None = None
    if mode_override is not None and mode_override is not config.telemetry_mode:
        mode_change = ModeChangeRecord(
            old_mode=config.telemetry_mode,
            new_mode=mode_override,
            changed_at=utc_now_z(),
            changed_by=changed_by,
            reason=reason,
            applicable_scope=applicable_scope,
        )
    return ResolvedRuntimeTelemetryPolicy(
        profile=profile,
        mode=mode,
        mode_change=mode_change,
    )
