"""Unit tests for frontend page/UI schema models."""

from __future__ import annotations

import pytest

from ai_sdlc.models.frontend_page_ui_schema import (
    FieldBlockDefinition,
    FrontendPageUiSchemaSet,
    PageSchemaDefinition,
    RenderSlotDefinition,
    SchemaVersioningContract,
    SectionAnchorDefinition,
    UiSchemaDefinition,
    build_p2_frontend_page_ui_schema_baseline,
)


def _anchors(*anchor_ids: str) -> list[SectionAnchorDefinition]:
    return [
        SectionAnchorDefinition(
            anchor_id=anchor_id,
            semantic_role=anchor_id.replace("-", "_"),
            layout_role="section",
        )
        for anchor_id in anchor_ids
    ]


def test_build_p2_frontend_page_ui_schema_baseline_contains_expected_schema_layers() -> None:
    schema_set = build_p2_frontend_page_ui_schema_baseline()

    assert schema_set.work_item_id == "147"
    assert schema_set.versioning.schema_family == "frontend-page-ui-schema"
    assert schema_set.versioning.current_version == "1.0"
    assert schema_set.versioning.compatible_versions == ["1.0"]
    assert [page.page_schema_id for page in schema_set.page_schemas] == [
        "dashboard-workspace",
        "search-list-workspace",
        "wizard-workspace",
    ]
    assert [ui.ui_schema_id for ui in schema_set.ui_schemas] == [
        "dashboard-workspace-default",
        "search-list-workspace-default",
        "wizard-workspace-default",
    ]


def test_page_schema_requires_primary_anchor_in_declared_section_anchors() -> None:
    with pytest.raises(ValueError, match="primary_anchor_id references unknown section anchor"):
        PageSchemaDefinition(
            page_schema_id="broken-page",
            page_recipe_id="DashboardPage",
            schema_version="1.0",
            primary_anchor_id="missing-anchor",
            section_anchors=_anchors("page-shell", "hero"),
        )


def test_page_schema_rejects_unknown_field_block_anchor() -> None:
    with pytest.raises(ValueError, match="field_blocks reference unknown section anchors"):
        PageSchemaDefinition(
            page_schema_id="broken-fields",
            page_recipe_id="SearchListPage",
            schema_version="1.0",
            primary_anchor_id="page-shell",
            section_anchors=_anchors("page-shell", "search-area"),
            field_blocks=[
                FieldBlockDefinition(
                    block_id="search-form",
                    anchor_id="missing-anchor",
                    field_semantics=["query"],
                )
            ],
        )


def test_ui_schema_rejects_duplicate_render_slot_ids() -> None:
    with pytest.raises(ValueError, match="duplicate render slot ids"):
        UiSchemaDefinition(
            ui_schema_id="dashboard-default",
            page_schema_id="dashboard-workspace",
            schema_version="1.0",
            root_slot_id="page-shell",
            render_slots=[
                RenderSlotDefinition(
                    slot_id="page-shell",
                    anchor_id="page-shell",
                    component_id="UiSection",
                ),
                RenderSlotDefinition(
                    slot_id="page-shell",
                    anchor_id="hero",
                    component_id="UiPageHeader",
                    parent_slot_id="page-shell",
                ),
            ],
        )


def test_schema_set_rejects_ui_schema_reference_for_unknown_page_schema() -> None:
    with pytest.raises(ValueError, match="ui_schemas reference unknown page_schema_id"):
        FrontendPageUiSchemaSet(
            work_item_id="147",
            versioning=SchemaVersioningContract(
                schema_family="frontend-page-ui-schema",
                current_version="1.0",
                compatible_versions=["1.0"],
                forward_extension_policy="additive-only",
                breaking_change_policy="new-version-required",
            ),
            page_schemas=[
                PageSchemaDefinition(
                    page_schema_id="dashboard-workspace",
                    page_recipe_id="DashboardPage",
                    schema_version="1.0",
                    primary_anchor_id="page-shell",
                    section_anchors=_anchors("page-shell", "hero"),
                )
            ],
            ui_schemas=[
                UiSchemaDefinition(
                    ui_schema_id="unknown-page-default",
                    page_schema_id="missing-page",
                    schema_version="1.0",
                    root_slot_id="page-shell",
                    render_slots=[
                        RenderSlotDefinition(
                            slot_id="page-shell",
                            anchor_id="page-shell",
                            component_id="UiSection",
                        )
                    ],
                )
            ],
        )


def test_frontend_page_ui_schema_models_deduplicate_set_like_lists() -> None:
    versioning = SchemaVersioningContract(
        current_version="1.0",
        compatible_versions=["1.0", "1.0", "1.1"],
    )
    page = PageSchemaDefinition(
        page_schema_id="dashboard-workspace",
        page_recipe_id="DashboardPage",
        schema_version="1.0",
        primary_anchor_id="page-shell",
        section_anchors=_anchors("page-shell", "hero"),
        field_blocks=[
            FieldBlockDefinition(
                block_id="hero-summary",
                anchor_id="hero",
                field_semantics=["summary", "summary", "stats"],
            )
        ],
    )
    ui = UiSchemaDefinition(
        ui_schema_id="dashboard-workspace-default",
        page_schema_id="dashboard-workspace",
        schema_version="1.0",
        root_slot_id="page-shell",
        render_slots=[
            RenderSlotDefinition(
                slot_id="page-shell",
                anchor_id="page-shell",
                component_id="UiSection",
                required_state_ids=["loaded", "loaded", "ready"],
            )
        ],
    )

    assert versioning.compatible_versions == ["1.0", "1.1"]
    assert page.field_blocks[0].field_semantics == ["summary", "stats"]
    assert ui.render_slots[0].required_state_ids == ["loaded", "ready"]
