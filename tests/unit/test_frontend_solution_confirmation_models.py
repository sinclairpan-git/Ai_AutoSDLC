"""Unit tests for frontend solution confirmation models."""

from __future__ import annotations

from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_install_strategies,
    build_builtin_style_pack_manifests,
    build_mvp_solution_snapshot,
)


def test_build_builtin_style_pack_manifests_covers_five_canonical_styles() -> None:
    manifests = build_builtin_style_pack_manifests()

    assert [manifest.style_pack_id for manifest in manifests] == [
        "enterprise-default",
        "data-console",
        "high-clarity",
        "modern-saas",
        "macos-glass",
    ]
    modern_saas = next(
        manifest for manifest in manifests if manifest.style_pack_id == "modern-saas"
    )
    assert modern_saas.design_tokens["surface_mode"] == "soft-gradient"
    assert modern_saas.recommended_for == ["marketing-sites", "self-serve-saas"]


def test_build_builtin_install_strategies_preserves_private_and_public_distribution_modes() -> None:
    strategies = build_builtin_install_strategies()

    assert [strategy.strategy_id for strategy in strategies] == [
        "enterprise-vue2-private-registry",
        "public-primevue-default",
    ]
    assert strategies[0].access_mode == "private"
    assert strategies[0].private_package_required is True
    assert strategies[1].access_mode == "public"
    assert strategies[1].packages == ["primevue", "@primeuix/themes"]


def test_build_mvp_solution_snapshot_creates_versioned_requested_effective_chain() -> None:
    original = build_mvp_solution_snapshot()
    fallback = build_mvp_solution_snapshot(
        previous_snapshot=original,
        decision_status="fallback_confirmed",
        requested_frontend_stack="vue2",
        requested_provider_id="enterprise-vue2",
        requested_style_pack_id="macos-glass",
        effective_frontend_stack="vue3",
        effective_provider_id="public-primevue",
        effective_style_pack_id="macos-glass",
        provider_mode="cross_stack_fallback",
        fallback_reason_code="enterprise-provider-unavailable",
        style_fidelity_status="full",
        preflight_reason_codes=["private-registry-unavailable"],
    )

    assert original.version == 1
    assert original.changed_from_snapshot_id is None
    assert original.decision_status == "recommended"
    assert original.availability_summary.overall_status == "ready"
    assert fallback.version == 2
    assert fallback.changed_from_snapshot_id == original.snapshot_id
    assert fallback.requested_provider_id == "enterprise-vue2"
    assert fallback.effective_provider_id == "public-primevue"
    assert fallback.provider_mode == "cross_stack_fallback"
    assert fallback.fallback_reason_code == "enterprise-provider-unavailable"
    assert fallback.snapshot_id == "solution-snapshot-002"


def test_build_mvp_solution_snapshot_assigns_new_snapshot_id_for_derived_versions() -> None:
    original = build_mvp_solution_snapshot()
    derived = build_mvp_solution_snapshot(previous_snapshot=original)

    assert original.snapshot_id == "solution-snapshot-001"
    assert derived.version == original.version + 1
    assert derived.snapshot_id == "solution-snapshot-002"
    assert derived.changed_from_snapshot_id == original.snapshot_id


def test_build_mvp_solution_snapshot_preserves_previous_state_when_versioning() -> None:
    original = build_mvp_solution_snapshot(
        project_id="customer-portal",
        confirmed_by_mode="manual-confirmation",
        decision_status="user_confirmed",
        requested_frontend_stack="vue3",
        requested_provider_id="public-primevue",
        requested_style_pack_id="modern-saas",
        effective_frontend_stack="vue3",
        effective_provider_id="public-primevue",
        effective_style_pack_id="modern-saas",
        provider_mode="cross_stack_fallback",
        fallback_reason_code="enterprise-provider-unavailable",
        fallback_reason_text="Private registry unavailable during setup.",
        preflight_status="warning",
        preflight_reason_codes=["private-registry-unavailable"],
        user_overrode_recommendation=True,
        user_override_fields=["frontend_stack", "provider_id", "style_pack_id"],
        style_fidelity_status="partial",
        style_degradation_reason_codes=["provider-theme-token-gap"],
    )

    derived = build_mvp_solution_snapshot(previous_snapshot=original)

    assert derived.snapshot_id == "solution-snapshot-002"
    assert derived.version == 2
    assert derived.changed_from_snapshot_id == original.snapshot_id
    assert derived.project_id == "customer-portal"
    assert derived.confirmed_by_mode == "manual-confirmation"
    assert derived.decision_status == "user_confirmed"
    assert derived.requested_frontend_stack == "vue3"
    assert derived.requested_provider_id == "public-primevue"
    assert derived.effective_frontend_stack == "vue3"
    assert derived.effective_provider_id == "public-primevue"
    assert derived.effective_style_pack_id == "modern-saas"
    assert derived.provider_mode == "cross_stack_fallback"
    assert derived.fallback_reason_code == "enterprise-provider-unavailable"
    assert derived.fallback_reason_text == "Private registry unavailable during setup."
    assert derived.preflight_status == "warning"
    assert derived.preflight_reason_codes == ["private-registry-unavailable"]
    assert derived.user_overrode_recommendation is True
    assert derived.user_override_fields == [
        "frontend_stack",
        "provider_id",
        "style_pack_id",
    ]
    assert derived.style_fidelity_status == "partial"
    assert derived.style_degradation_reason_codes == ["provider-theme-token-gap"]
    assert derived.resolved_style_tokens == original.resolved_style_tokens
    assert derived.provider_theme_adapter_config == original.provider_theme_adapter_config
