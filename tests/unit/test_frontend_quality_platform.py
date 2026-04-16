"""Unit tests for frontend quality platform validation helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_quality_platform import validate_frontend_quality_platform
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)


def test_validate_frontend_quality_platform_passes_for_builtin_baseline() -> None:
    platform = build_p2_frontend_quality_platform_baseline()

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.matrix_coverage_count == 3
    assert result.page_schema_ids == ["dashboard-workspace", "search-list-workspace"]


def test_validate_frontend_quality_platform_blocks_unknown_page_schema_and_theme_pack() -> None:
    platform = build_p2_frontend_quality_platform_baseline()
    mutated_matrix = list(platform.coverage_matrix)
    mutated_matrix[0] = mutated_matrix[0].model_copy(
        update={
            "page_schema_id": "unknown-page",
            "style_pack_id": "unknown-pack",
        }
    )
    platform = platform.model_copy(update={"coverage_matrix": mutated_matrix})

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="modern-saas",
            effective_style_pack_id="modern-saas",
            recommended_style_pack_id="modern-saas",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.passed is False
    assert "unknown page schema: unknown-page" in result.blockers
    assert "unknown style pack: unknown-pack" in result.blockers


def test_validate_frontend_quality_platform_blocks_snapshot_style_pack_outside_governance() -> None:
    platform = build_p2_frontend_quality_platform_baseline()

    result = validate_frontend_quality_platform(
        platform,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        solution_snapshot=build_mvp_solution_snapshot(
            requested_provider_id="public-primevue",
            effective_provider_id="public-primevue",
            recommended_provider_id="public-primevue",
            requested_style_pack_id="unsupported-pack",
            effective_style_pack_id="unsupported-pack",
            recommended_style_pack_id="unsupported-pack",
            requested_frontend_stack="vue3",
            effective_frontend_stack="vue3",
            recommended_frontend_stack="vue3",
            style_fidelity_status="full",
        ),
    )

    assert result.passed is False
    assert "effective style pack outside theme governance: unsupported-pack" in result.blockers
