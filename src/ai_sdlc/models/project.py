"""Project-level data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, field_validator

from ai_sdlc.telemetry.enums import TelemetryMode, TelemetryProfile


class ProjectStatus(str, Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZED = "initialized"


class ActivationState(str, Enum):
    """Observed activation depth for the selected IDE adapter."""

    INSTALLED = "installed"
    ACKNOWLEDGED = "acknowledged"
    ACTIVATED = "activated"


class AdapterSupportTier(str, Enum):
    """How strongly the selected adapter can enforce the workflow."""

    SOFT_INSTALLED = "soft_installed"
    ACKNOWLEDGED_ACTIVATION = "acknowledged_activation"
    VERIFIED_ACTIVATION = "verified_activation"
    HARD_ACTIVATED = "hard_activated"


class AdapterIngressState(str, Enum):
    """Observed repo-local host ingress truth for the selected adapter."""

    MATERIALIZED = "materialized"
    VERIFIED_LOADED = "verified_loaded"
    DEGRADED = "degraded"
    UNSUPPORTED = "unsupported"


class AdapterVerificationResult(str, Enum):
    """Verification result for the selected adapter target."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DEGRADED = "degraded"
    UNSUPPORTED = "unsupported"


class ProjectState(BaseModel):
    """Represents the project initialization state stored in project-state.yaml."""

    status: ProjectStatus = ProjectStatus.UNINITIALIZED
    project_name: str = ""
    initialized_at: str | None = None
    last_updated: str | None = None
    next_work_item_seq: int = 1
    version: str = "1.0"

    @field_validator("status", mode="before")
    @classmethod
    def _normalize_legacy_status(cls, value: object) -> object:
        # Backward compatibility: early builds wrote `planning`.
        if isinstance(value, str) and value.strip().lower() == "planning":
            return ProjectStatus.INITIALIZED
        return value


class ProjectConfig(BaseModel):
    """Project-level configuration stored in ``project-config.yaml`` (often gitignored).

    When the file is absent, loaders return this model with field defaults.
    """

    product_form: str = "hybrid"
    default_execution_mode: str = "auto"
    default_branch_strategy: str = "dual"
    max_parallel_agents: int = 3
    #: Default language for human-readable generated docs (Markdown). Use zh-CN for 简体中文.
    document_locale: str = "zh-CN"
    # Auto IDE adapter (first command + init)
    detected_ide: str = ""
    agent_target: str = ""
    adapter_applied: str = ""
    adapter_version: str = ""
    adapter_applied_at: str = ""
    adapter_activation_state: str = ""
    adapter_support_tier: str = ""
    agent_target_source: str = ""
    adapter_activation_source: str = ""
    adapter_activation_evidence: str = ""
    adapter_activated_at: str = ""
    adapter_ingress_state: str = ""
    adapter_verification_result: str = ""
    adapter_canonical_path: str = ""
    adapter_canonical_content_digest: str = ""
    adapter_canonical_consumption_result: str = ""
    adapter_canonical_consumption_evidence: str = ""
    adapter_canonical_consumed_at: str = ""
    adapter_degrade_reason: str = ""
    adapter_verification_evidence: str = ""
    adapter_verified_at: str = ""
    telemetry_profile: TelemetryProfile = TelemetryProfile.SELF_HOSTING
    telemetry_mode: TelemetryMode = TelemetryMode.LITE
