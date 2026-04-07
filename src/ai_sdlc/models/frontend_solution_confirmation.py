"""Frontend solution confirmation models for work item 073."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_SNAPSHOT_ID_PATTERN = re.compile(r"^(?P<prefix>.*?)(?P<number>\d+)$")


class FrontendSolutionConfirmationModel(BaseModel):
    """Base model for structured frontend solution confirmation truth."""

    model_config = ConfigDict(extra="forbid")


class AvailabilitySummary(FrontendSolutionConfirmationModel):
    """Machine-readable availability summary for recommendation and preflight."""

    overall_status: Literal["ready", "attention", "blocked"]
    passed_check_ids: list[str] = Field(default_factory=list)
    failed_check_ids: list[str] = Field(default_factory=list)
    blocking_reason_codes: list[str] = Field(default_factory=list)


class StylePackManifest(FrontendSolutionConfirmationModel):
    """Canonical style pack manifest."""

    style_pack_id: str
    display_name: str
    status: str = "active"
    visibility: str = "internal"
    description: str
    recommended_for: list[str] = Field(default_factory=list)
    not_recommended_for: list[str] = Field(default_factory=list)
    design_tokens: dict[str, str] = Field(default_factory=dict)


class InstallStrategy(FrontendSolutionConfirmationModel):
    """Install strategy truth for one provider distribution path."""

    strategy_id: str
    provider_id: str
    access_mode: Literal["public", "private"]
    package_manager: Literal["npm", "pnpm", "yarn"] = "pnpm"
    packages: list[str] = Field(default_factory=list)
    registry_requirements: list[str] = Field(default_factory=list)
    credential_requirements: list[str] = Field(default_factory=list)
    private_package_required: bool = False


class FrontendSolutionSnapshot(FrontendSolutionConfirmationModel):
    """Versioned solution snapshot for confirmation and fallback audit."""

    snapshot_id: str
    project_id: str
    version: int
    created_at: str
    confirmed_at: str
    confirmed_by_mode: str
    decision_status: Literal[
        "recommended",
        "user_confirmed",
        "fallback_required",
        "fallback_confirmed",
        "blocked",
    ]
    recommended_project_shape: str
    recommended_frontend_stack: str
    recommended_provider_id: str
    recommended_backend_stack: str
    recommended_api_collab_mode: str
    recommended_style_pack_id: str
    recommendation_source: str
    recommendation_reason_codes: list[str] = Field(default_factory=list)
    recommendation_reason_text: str
    requested_project_shape: str
    requested_frontend_stack: str
    requested_provider_id: str
    requested_backend_stack: str
    requested_api_collab_mode: str
    requested_style_pack_id: str
    effective_project_shape: str
    effective_frontend_stack: str
    effective_provider_id: str
    effective_backend_stack: str
    effective_api_collab_mode: str
    effective_style_pack_id: str
    enterprise_provider_eligible: bool
    availability_checks: list[str] = Field(default_factory=list)
    availability_summary: AvailabilitySummary
    availability_reason_text: str
    preflight_status: Literal["ready", "warning", "blocked"]
    preflight_reason_codes: list[str] = Field(default_factory=list)
    user_overrode_recommendation: bool
    user_override_fields: list[str] = Field(default_factory=list)
    provider_mode: Literal["normal", "cross_stack_fallback"] = "normal"
    fallback_reason_code: str | None = None
    fallback_reason_text: str | None = None
    resolved_style_tokens: dict[str, str] = Field(default_factory=dict)
    provider_theme_adapter_config: dict[str, str] = Field(default_factory=dict)
    style_fidelity_status: Literal["full", "partial", "degraded", "unsupported"]
    style_degradation_reason_codes: list[str] = Field(default_factory=list)
    changed_from_snapshot_id: str | None = None


def build_builtin_style_pack_manifests() -> list[StylePackManifest]:
    """Return the canonical P2 built-in style packs."""

    return [
        StylePackManifest(
            style_pack_id="enterprise-default",
            display_name="Enterprise Default",
            description="Conservative enterprise console baseline.",
            recommended_for=["ops-consoles", "internal-admin"],
            not_recommended_for=["brand-led-marketing"],
            design_tokens={
                "surface_mode": "flat-neutral",
                "density": "balanced",
                "accent_mode": "subtle-enterprise",
            },
        ),
        StylePackManifest(
            style_pack_id="data-console",
            display_name="Data Console",
            description="Dense, analysis-oriented control room styling.",
            recommended_for=["analytics", "monitoring"],
            not_recommended_for=["storytelling-landing-pages"],
            design_tokens={
                "surface_mode": "high-contrast-panel",
                "density": "dense",
                "accent_mode": "signal-coded",
            },
        ),
        StylePackManifest(
            style_pack_id="high-clarity",
            display_name="High Clarity",
            description="Accessibility-first, high-legibility presentation.",
            recommended_for=["compliance-heavy-ui", "long-form-forms"],
            not_recommended_for=["ornamental-brand-showcase"],
            design_tokens={
                "surface_mode": "clean-solid",
                "density": "comfortable",
                "accent_mode": "clarity-first",
            },
        ),
        StylePackManifest(
            style_pack_id="modern-saas",
            display_name="Modern SaaS",
            description="Soft brand-led SaaS visuals for product marketing and app chrome.",
            recommended_for=["marketing-sites", "self-serve-saas"],
            not_recommended_for=["legacy-enterprise-lockstep"],
            design_tokens={
                "surface_mode": "soft-gradient",
                "density": "balanced",
                "accent_mode": "brand-forward",
            },
        ),
        StylePackManifest(
            style_pack_id="macos-glass",
            display_name="macOS Glass",
            description="Translucent layered surfaces with glassmorphism bias.",
            recommended_for=["premium-dashboard", "design-forward-prototype"],
            not_recommended_for=["strict-enterprise-baseline"],
            design_tokens={
                "surface_mode": "translucent-glass",
                "density": "comfortable",
                "accent_mode": "frosted-depth",
            },
        ),
    ]


def build_builtin_install_strategies() -> list[InstallStrategy]:
    """Return the minimal built-in install strategies."""

    return [
        InstallStrategy(
            strategy_id="enterprise-vue2-private-registry",
            provider_id="enterprise-vue2",
            access_mode="private",
            packages=["@company/enterprise-vue2-ui"],
            registry_requirements=["company-private-registry"],
            credential_requirements=["company-registry-token"],
            private_package_required=True,
        ),
        InstallStrategy(
            strategy_id="public-primevue-default",
            provider_id="public-primevue",
            access_mode="public",
            packages=["primevue", "@primeuix/themes"],
        ),
    ]


def _default_provider_theme_adapter_config(
    effective_provider_id: str,
    effective_style_pack_id: str,
    *,
    previous_config: dict[str, object] | None = None,
    preserve_existing_adapter: bool = False,
) -> dict[str, str]:
    adapter_id = f"{effective_provider_id}-theme-bridge"
    if preserve_existing_adapter and previous_config is not None:
        adapter_id = str(previous_config.get("adapter_id", adapter_id))

    return {
        "adapter_id": adapter_id,
        "preset": effective_style_pack_id,
    }


def build_mvp_solution_snapshot(
    previous_snapshot: FrontendSolutionSnapshot | None = None,
    **overrides: object,
) -> FrontendSolutionSnapshot:
    """Build the minimal MVP solution snapshot with optional overrides."""

    style_tokens_by_id = {
        manifest.style_pack_id: manifest.design_tokens
        for manifest in build_builtin_style_pack_manifests()
    }
    snapshot_id = (
        "solution-snapshot-001"
        if previous_snapshot is None
        else _next_snapshot_id(previous_snapshot.snapshot_id)
    )
    if previous_snapshot is None:
        effective_style_pack_id = str(
            overrides.get("effective_style_pack_id", "enterprise-default")
        )
        base_payload: dict[str, object] = {
            "project_id": "073-demo",
            "created_at": "2026-04-08T00:00:00Z",
            "confirmed_at": "2026-04-08T00:05:00Z",
            "confirmed_by_mode": "guided",
            "decision_status": "recommended",
            "recommended_project_shape": "frontend-heavy",
            "recommended_frontend_stack": "vue2",
            "recommended_provider_id": "enterprise-vue2",
            "recommended_backend_stack": "fastapi",
            "recommended_api_collab_mode": "typed-bff",
            "recommended_style_pack_id": "enterprise-default",
            "recommendation_source": "simple-mode",
            "recommendation_reason_codes": ["enterprise-provider-preferred"],
            "recommendation_reason_text": "Enterprise baseline is available and preferred.",
            "requested_project_shape": "frontend-heavy",
            "requested_frontend_stack": "vue2",
            "requested_provider_id": "enterprise-vue2",
            "requested_backend_stack": "fastapi",
            "requested_api_collab_mode": "typed-bff",
            "requested_style_pack_id": effective_style_pack_id,
            "effective_project_shape": "frontend-heavy",
            "effective_frontend_stack": "vue2",
            "effective_provider_id": "enterprise-vue2",
            "effective_backend_stack": "fastapi",
            "effective_api_collab_mode": "typed-bff",
            "effective_style_pack_id": effective_style_pack_id,
            "enterprise_provider_eligible": True,
            "availability_checks": [
                "company-registry-network",
                "company-registry-token",
            ],
            "availability_summary": AvailabilitySummary(
                overall_status="ready",
                passed_check_ids=["company-registry-network", "company-registry-token"],
                failed_check_ids=[],
                blocking_reason_codes=[],
            ),
            "availability_reason_text": "Enterprise provider prerequisites satisfied.",
            "preflight_status": "ready",
            "preflight_reason_codes": [],
            "user_overrode_recommendation": False,
            "user_override_fields": [],
            "provider_mode": "normal",
            "fallback_reason_code": None,
            "fallback_reason_text": None,
            "resolved_style_tokens": style_tokens_by_id[effective_style_pack_id],
            "provider_theme_adapter_config": _default_provider_theme_adapter_config(
                "enterprise-vue2",
                effective_style_pack_id,
            ),
            "style_fidelity_status": "full",
            "style_degradation_reason_codes": [],
        }
    else:
        base_payload = previous_snapshot.model_dump(mode="json")

    base_payload.update(
        {
            "snapshot_id": snapshot_id,
            "version": 1 if previous_snapshot is None else previous_snapshot.version + 1,
            "changed_from_snapshot_id": (
                None if previous_snapshot is None else previous_snapshot.snapshot_id
            ),
        }
    )
    base_payload.update(overrides)

    effective_style_pack_id = str(base_payload["effective_style_pack_id"])
    effective_provider_id = str(base_payload["effective_provider_id"])
    if "resolved_style_tokens" not in overrides:
        base_payload["resolved_style_tokens"] = style_tokens_by_id[effective_style_pack_id]
    if "provider_theme_adapter_config" not in overrides:
        previous_adapter_config = None
        preserve_existing_adapter = False
        if previous_snapshot is not None:
            previous_adapter_config = previous_snapshot.model_dump(mode="json").get(
                "provider_theme_adapter_config"
            )
            preserve_existing_adapter = (
                effective_provider_id == previous_snapshot.effective_provider_id
            )

        base_payload["provider_theme_adapter_config"] = (
            _default_provider_theme_adapter_config(
                effective_provider_id,
                effective_style_pack_id,
                previous_config=(
                    previous_adapter_config
                    if isinstance(previous_adapter_config, dict)
                    else None
                ),
                preserve_existing_adapter=preserve_existing_adapter,
            )
        )

    return FrontendSolutionSnapshot(**base_payload)


def _next_snapshot_id(snapshot_id: str) -> str:
    match = _SNAPSHOT_ID_PATTERN.match(snapshot_id)
    if match is None:
        return f"{snapshot_id}-next"

    prefix = match.group("prefix")
    current_number = match.group("number")
    return f"{prefix}{int(current_number) + 1:0{len(current_number)}d}"


__all__ = [
    "AvailabilitySummary",
    "FrontendSolutionSnapshot",
    "InstallStrategy",
    "StylePackManifest",
    "build_builtin_install_strategies",
    "build_builtin_style_pack_manifests",
    "build_mvp_solution_snapshot",
]
