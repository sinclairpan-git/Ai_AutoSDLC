"""Unit tests for frontend page/UI schema validation and handoff."""

from __future__ import annotations

from ai_sdlc.core.frontend_page_ui_schema import (
    build_frontend_page_ui_schema_handoff,
    validate_frontend_page_ui_schema_set,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import build_mvp_solution_snapshot
from ai_sdlc.models.frontend_ui_kernel import (
    build_p1_frontend_ui_kernel_page_recipe_expansion,
)


def test_validate_frontend_page_ui_schema_set_passes_for_builtin_baseline() -> None:
    schema_set = build_p2_frontend_page_ui_schema_baseline()
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()

    result = validate_frontend_page_ui_schema_set(schema_set, kernel)

    assert result.passed is True
    assert result.blockers == []
    assert result.page_schema_ids == [
        "dashboard-workspace",
        "search-list-workspace",
        "wizard-workspace",
    ]


def test_validate_frontend_page_ui_schema_set_blocks_unknown_recipe_component_and_state() -> None:
    schema_set = build_p2_frontend_page_ui_schema_baseline()
    broken_page = schema_set.page_schemas[0].model_copy(update={"page_recipe_id": "UnknownPage"})
    broken_slot = schema_set.ui_schemas[0].render_slots[0].model_copy(
        update={
            "component_id": "UiUnknown",
            "required_state_ids": ["unknown-state"],
        }
    )
    broken_ui = schema_set.ui_schemas[0].model_copy(
        update={"render_slots": [broken_slot, *schema_set.ui_schemas[0].render_slots[1:]]}
    )
    broken_schema_set = schema_set.model_copy(
        update={
            "page_schemas": [broken_page, *schema_set.page_schemas[1:]],
            "ui_schemas": [broken_ui, *schema_set.ui_schemas[1:]],
        }
    )
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()

    result = validate_frontend_page_ui_schema_set(broken_schema_set, kernel)

    assert result.passed is False
    assert any("UnknownPage" in blocker for blocker in result.blockers)
    assert any("UiUnknown" in blocker for blocker in result.blockers)
    assert any("unknown-state" in blocker for blocker in result.blockers)


def test_build_frontend_page_ui_schema_handoff_packages_provider_style_and_schema_refs() -> None:
    schema_set = build_p2_frontend_page_ui_schema_baseline()
    kernel = build_p1_frontend_ui_kernel_page_recipe_expansion()
    snapshot = build_mvp_solution_snapshot(
        requested_frontend_stack="vue3",
        effective_frontend_stack="vue3",
        recommended_frontend_stack="vue3",
        requested_provider_id="public-primevue",
        effective_provider_id="public-primevue",
        recommended_provider_id="public-primevue",
        requested_style_pack_id="modern-saas",
        effective_style_pack_id="modern-saas",
        recommended_style_pack_id="modern-saas",
        style_fidelity_status="full",
    )

    handoff = build_frontend_page_ui_schema_handoff(
        schema_set,
        kernel=kernel,
        solution_snapshot=snapshot,
    )

    assert handoff.state == "ready"
    assert handoff.schema_version == "1.0"
    assert handoff.effective_provider_id == "public-primevue"
    assert handoff.effective_style_pack_id == "modern-saas"
    assert [entry.page_schema_id for entry in handoff.entries] == [
        "dashboard-workspace",
        "search-list-workspace",
        "wizard-workspace",
    ]
    assert handoff.entries[0].ui_schema_id == "dashboard-workspace-default"
    assert "page-shell" in handoff.entries[0].slot_ids
