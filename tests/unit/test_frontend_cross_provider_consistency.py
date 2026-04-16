"""Unit tests for frontend cross-provider consistency validation helpers."""

from __future__ import annotations

from ai_sdlc.core.frontend_cross_provider_consistency import (
    validate_frontend_cross_provider_consistency,
)
from ai_sdlc.models.frontend_cross_provider_consistency import (
    build_p2_frontend_cross_provider_consistency_baseline,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_quality_platform import (
    build_p2_frontend_quality_platform_baseline,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)


def test_validate_frontend_cross_provider_consistency_passes_for_builtin_baseline() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert result.passed is True
    assert result.blockers == []
    assert result.pair_count == 3
    assert result.certification_gates == {
        "enterprise-vue2__public-primevue__search-list-workspace": "ready",
        "enterprise-vue2__public-primevue__dashboard-workspace": "conditional",
        "enterprise-vue2__public-primevue__wizard-workspace": "blocked",
    }


def test_validate_frontend_cross_provider_consistency_blocks_unknown_page_schema_and_style_pack() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    bundles = list(consistency.certification_bundles)
    bundles[0] = bundles[0].model_copy(
        update={
            "page_schema_id": "unknown-page",
            "compared_style_pack_id": "unknown-pack",
        }
    )
    consistency = consistency.model_copy(update={"certification_bundles": bundles})

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert result.passed is False
    assert "unknown page schema in pair bundle: unknown-page" in result.blockers
    assert "unknown style pack in pair bundle: unknown-pack" in result.blockers


def test_validate_frontend_cross_provider_consistency_blocks_inconsistent_gap_and_truth_surface_contract() -> None:
    consistency = build_p2_frontend_cross_provider_consistency_baseline()
    bundles = list(consistency.certification_bundles)
    bundles[1] = bundles[1].model_copy(update={"coverage_gap_ids": []})
    truth_records = [
        record
        for record in consistency.truth_surfacing_records
        if not (
            record.pair_id == "enterprise-vue2__public-primevue__search-list-workspace"
            and record.truth_layer == "release-gate-input"
        )
    ]
    consistency = consistency.model_copy(
        update={
            "certification_bundles": bundles,
            "truth_surfacing_records": truth_records,
        }
    )

    result = validate_frontend_cross_provider_consistency(
        consistency,
        page_ui_schema=build_p2_frontend_page_ui_schema_baseline(),
        theme_governance=build_p2_frontend_theme_token_governance_baseline(),
        quality_platform=build_p2_frontend_quality_platform_baseline(),
    )

    assert result.passed is False
    assert (
        "coverage-gap pair bundle missing coverage_gap_ids: "
        "enterprise-vue2__public-primevue__dashboard-workspace"
    ) in result.blockers
    assert (
        "truth surfacing missing required layers for pair: "
        "enterprise-vue2__public-primevue__search-list-workspace"
    ) in result.blockers
