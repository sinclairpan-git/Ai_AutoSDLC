"""Unit tests for frontend solution confirmation models."""

from __future__ import annotations

from ai_sdlc.models.frontend_solution_confirmation import (
    AvailabilitySummary,
    FrontendSolutionSnapshot,
    InstallStrategy,
    StylePackManifest,
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
    assert fallback.provider_theme_adapter_config == {
        "adapter_id": "public-primevue-theme-bridge",
        "preset": "macos-glass",
    }


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
    assert original.provider_theme_adapter_config == {
        "adapter_id": "public-primevue-theme-bridge",
        "preset": "modern-saas",
    }
    assert derived.provider_theme_adapter_config == original.provider_theme_adapter_config


def test_build_mvp_solution_snapshot_preserves_unknown_style_tokens_without_keyerror() -> None:
    original = build_mvp_solution_snapshot(
        requested_style_pack_id="brand-x",
        effective_style_pack_id="brand-x",
        resolved_style_tokens={
            "surface_mode": "brand-x-surface",
            "accent_mode": "brand-x-accent",
        },
    )

    derived = build_mvp_solution_snapshot(previous_snapshot=original)

    assert original.effective_style_pack_id == "brand-x"
    assert original.resolved_style_tokens == {
        "surface_mode": "brand-x-surface",
        "accent_mode": "brand-x-accent",
    }
    assert derived.effective_style_pack_id == "brand-x"
    assert derived.resolved_style_tokens == original.resolved_style_tokens


def test_frontend_solution_confirmation_models_deduplicate_set_like_lists() -> None:
    summary = AvailabilitySummary(
        overall_status="blocked",
        passed_check_ids=["registry", "registry", "token"],
        failed_check_ids=["network", "network"],
        blocking_reason_codes=["private_registry", "private_registry"],
    )
    manifest = StylePackManifest(
        style_pack_id="modern-saas",
        display_name="Modern SaaS",
        description="Soft brand-led SaaS visuals.",
        recommended_for=["marketing-sites", "marketing-sites", "self-serve-saas"],
        not_recommended_for=["legacy-enterprise-lockstep"] * 2,
    )
    strategy = InstallStrategy(
        strategy_id="public-primevue-default",
        provider_id="public-primevue",
        access_mode="public",
        packages=["primevue", "primevue", "@primeuix/themes"],
        registry_requirements=["npmjs", "npmjs"],
        credential_requirements=["token", "token"],
    )
    snapshot = FrontendSolutionSnapshot(
        snapshot_id="solution-snapshot-001",
        project_id="demo",
        version=1,
        created_at="2026-04-21T00:00:00Z",
        confirmed_at="2026-04-21T00:00:00Z",
        confirmed_by_mode="dry-run",
        decision_status="user_confirmed",
        recommended_project_shape="single-page-app",
        recommended_frontend_stack="vue3",
        recommended_provider_id="public-primevue",
        recommended_backend_stack="bff",
        recommended_api_collab_mode="contract-first",
        recommended_style_pack_id="modern-saas",
        recommendation_source="default",
        recommendation_reason_codes=["preferred", "preferred", "available"],
        recommendation_reason_text="Preferred and available.",
        requested_project_shape="single-page-app",
        requested_frontend_stack="vue3",
        requested_provider_id="public-primevue",
        requested_backend_stack="bff",
        requested_api_collab_mode="contract-first",
        requested_style_pack_id="modern-saas",
        effective_project_shape="single-page-app",
        effective_frontend_stack="vue3",
        effective_provider_id="public-primevue",
        effective_backend_stack="bff",
        effective_api_collab_mode="contract-first",
        effective_style_pack_id="modern-saas",
        enterprise_provider_eligible=False,
        availability_checks=["registry", "registry", "token"],
        availability_summary=summary,
        availability_reason_text="Ready.",
        preflight_status="warning",
        preflight_reason_codes=["network", "network", "slow"],
        user_overrode_recommendation=True,
        user_override_fields=["provider_id", "provider_id", "style_pack_id"],
        resolved_style_tokens={"surface_mode": "soft-gradient"},
        provider_theme_adapter_config={"adapter_id": "primevue-theme-bridge"},
        style_fidelity_status="partial",
        style_degradation_reason_codes=["token_gap", "token_gap"],
    )

    assert summary.passed_check_ids == ["registry", "token"]
    assert summary.failed_check_ids == ["network"]
    assert summary.blocking_reason_codes == ["private_registry"]
    assert manifest.recommended_for == ["marketing-sites", "self-serve-saas"]
    assert manifest.not_recommended_for == ["legacy-enterprise-lockstep"]
    assert strategy.packages == ["primevue", "@primeuix/themes"]
    assert strategy.registry_requirements == ["npmjs"]
    assert strategy.credential_requirements == ["token"]
    assert snapshot.recommendation_reason_codes == ["preferred", "available"]
    assert snapshot.availability_checks == ["registry", "token"]
    assert snapshot.preflight_reason_codes == ["network", "slow"]
    assert snapshot.user_override_fields == ["provider_id", "style_pack_id"]
    assert snapshot.style_degradation_reason_codes == ["token_gap"]
