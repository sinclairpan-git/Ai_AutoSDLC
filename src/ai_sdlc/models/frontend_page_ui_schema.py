"""Frontend page/UI schema baseline models for work item 147."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_ui_kernel import (
    FrontendUiKernelSet,
    build_p1_frontend_ui_kernel_page_recipe_expansion,
)


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _find_unknown_references(values: list[str], known_values: set[str]) -> list[str]:
    unknown: list[str] = []
    for value in values:
        if value not in known_values and value not in unknown:
            unknown.append(value)
    return unknown


class FrontendPageUiSchemaModel(BaseModel):
    """Base model for page/UI schema artifacts."""

    model_config = ConfigDict(extra="forbid")


class SchemaVersioningContract(FrontendPageUiSchemaModel):
    """Versioning policy shared by page and UI schemas."""

    schema_family: str = "frontend-page-ui-schema"
    current_version: str = "1.0"
    compatible_versions: list[str] = Field(default_factory=lambda: ["1.0"])
    forward_extension_policy: str = "additive-only"
    breaking_change_policy: str = "new-version-required"

    @model_validator(mode="after")
    def _require_current_version_in_compatibility_list(
        self,
    ) -> SchemaVersioningContract:
        if self.current_version not in self.compatible_versions:
            raise ValueError(
                "current_version must be included in compatible_versions"
            )
        return self


class SectionAnchorDefinition(FrontendPageUiSchemaModel):
    """Stable page-level anchor shared by downstream tracks."""

    anchor_id: str
    semantic_role: str
    layout_role: str
    required: bool = True


class FieldBlockDefinition(FrontendPageUiSchemaModel):
    """Provider-neutral field block semantics bound to a section anchor."""

    block_id: str
    anchor_id: str
    field_semantics: list[str] = Field(default_factory=list)
    cardinality: Literal["single", "repeatable"] = "single"


class PageSchemaDefinition(FrontendPageUiSchemaModel):
    """Page structure intent layer."""

    page_schema_id: str
    page_recipe_id: str
    schema_version: str
    primary_anchor_id: str
    section_anchors: list[SectionAnchorDefinition] = Field(default_factory=list)
    field_blocks: list[FieldBlockDefinition] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_page_schema_structure(self) -> PageSchemaDefinition:
        duplicate_anchor_ids = _find_duplicates(
            [anchor.anchor_id for anchor in self.section_anchors]
        )
        if duplicate_anchor_ids:
            joined = ", ".join(duplicate_anchor_ids)
            raise ValueError(f"duplicate section anchor ids: {joined}")

        known_anchor_ids = {anchor.anchor_id for anchor in self.section_anchors}
        if self.primary_anchor_id not in known_anchor_ids:
            raise ValueError(
                "primary_anchor_id references unknown section anchor: "
                f"{self.primary_anchor_id}"
            )

        duplicate_block_ids = _find_duplicates(
            [block.block_id for block in self.field_blocks]
        )
        if duplicate_block_ids:
            joined = ", ".join(duplicate_block_ids)
            raise ValueError(f"duplicate field block ids: {joined}")

        unknown_anchor_refs = _find_unknown_references(
            [block.anchor_id for block in self.field_blocks],
            known_anchor_ids,
        )
        if unknown_anchor_refs:
            joined = ", ".join(unknown_anchor_refs)
            raise ValueError(
                f"field_blocks reference unknown section anchors: {joined}"
            )
        return self


class RenderSlotDefinition(FrontendPageUiSchemaModel):
    """Renderable slot truth mapped from page anchors to kernel protocols."""

    slot_id: str
    anchor_id: str
    component_id: str
    parent_slot_id: str | None = None
    cardinality: Literal["single", "repeatable"] = "single"
    required_state_ids: list[str] = Field(default_factory=list)


class UiSchemaDefinition(FrontendPageUiSchemaModel):
    """Renderable structure layer."""

    ui_schema_id: str
    page_schema_id: str
    schema_version: str
    root_slot_id: str
    render_slots: list[RenderSlotDefinition] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_ui_schema_structure(self) -> UiSchemaDefinition:
        duplicate_slot_ids = _find_duplicates(
            [slot.slot_id for slot in self.render_slots]
        )
        if duplicate_slot_ids:
            joined = ", ".join(duplicate_slot_ids)
            raise ValueError(f"duplicate render slot ids: {joined}")

        slot_ids = {slot.slot_id for slot in self.render_slots}
        if self.root_slot_id not in slot_ids:
            raise ValueError(f"root_slot_id references unknown render slot: {self.root_slot_id}")

        unknown_parent_refs = _find_unknown_references(
            [slot.parent_slot_id for slot in self.render_slots if slot.parent_slot_id],
            slot_ids,
        )
        if unknown_parent_refs:
            joined = ", ".join(unknown_parent_refs)
            raise ValueError(
                f"render_slots reference unknown parent slots: {joined}"
            )
        return self


class FrontendPageUiSchemaSet(FrontendPageUiSchemaModel):
    """Top-level provider-neutral page/UI schema baseline."""

    work_item_id: str
    versioning: SchemaVersioningContract
    page_schemas: list[PageSchemaDefinition] = Field(default_factory=list)
    ui_schemas: list[UiSchemaDefinition] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_schema_set(self) -> FrontendPageUiSchemaSet:
        duplicate_page_schema_ids = _find_duplicates(
            [page.page_schema_id for page in self.page_schemas]
        )
        if duplicate_page_schema_ids:
            joined = ", ".join(duplicate_page_schema_ids)
            raise ValueError(f"duplicate page_schema_id values: {joined}")

        duplicate_ui_schema_ids = _find_duplicates(
            [ui.ui_schema_id for ui in self.ui_schemas]
        )
        if duplicate_ui_schema_ids:
            joined = ", ".join(duplicate_ui_schema_ids)
            raise ValueError(f"duplicate ui_schema_id values: {joined}")

        supported_versions = set(self.versioning.compatible_versions)
        unknown_page_versions = _find_unknown_references(
            [page.schema_version for page in self.page_schemas],
            supported_versions,
        )
        if unknown_page_versions:
            joined = ", ".join(unknown_page_versions)
            raise ValueError(f"page_schemas use unsupported schema versions: {joined}")

        unknown_ui_versions = _find_unknown_references(
            [ui.schema_version for ui in self.ui_schemas],
            supported_versions,
        )
        if unknown_ui_versions:
            joined = ", ".join(unknown_ui_versions)
            raise ValueError(f"ui_schemas use unsupported schema versions: {joined}")

        page_schema_ids = {page.page_schema_id for page in self.page_schemas}
        unknown_ui_page_refs = _find_unknown_references(
            [ui.page_schema_id for ui in self.ui_schemas],
            page_schema_ids,
        )
        if unknown_ui_page_refs:
            joined = ", ".join(unknown_ui_page_refs)
            raise ValueError(f"ui_schemas reference unknown page_schema_id: {joined}")

        page_anchor_ids = {
            page.page_schema_id: {anchor.anchor_id for anchor in page.section_anchors}
            for page in self.page_schemas
        }
        for ui_schema in self.ui_schemas:
            anchor_ids = page_anchor_ids.get(ui_schema.page_schema_id, set())
            unknown_anchor_refs = _find_unknown_references(
                [slot.anchor_id for slot in ui_schema.render_slots],
                anchor_ids,
            )
            if unknown_anchor_refs:
                joined = ", ".join(unknown_anchor_refs)
                raise ValueError(
                    "render_slots reference unknown anchors for "
                    f"{ui_schema.page_schema_id}: {joined}"
                )
        return self


def build_p2_frontend_page_ui_schema_baseline(
    *,
    kernel: FrontendUiKernelSet | None = None,
) -> FrontendPageUiSchemaSet:
    """Build the provider-neutral page/UI schema baseline defined by work item 147."""

    effective_kernel = kernel or build_p1_frontend_ui_kernel_page_recipe_expansion()
    recipe_ids = {recipe.recipe_id for recipe in effective_kernel.page_recipes}
    required_recipe_ids = {"DashboardPage", "SearchListPage", "WizardPage"}
    missing_recipe_ids = sorted(required_recipe_ids - recipe_ids)
    if missing_recipe_ids:
        joined = ", ".join(missing_recipe_ids)
        raise ValueError(f"kernel missing required page recipes for 147 baseline: {joined}")

    versioning = SchemaVersioningContract()
    return FrontendPageUiSchemaSet(
        work_item_id="147",
        versioning=versioning,
        page_schemas=[
            PageSchemaDefinition(
                page_schema_id="dashboard-workspace",
                page_recipe_id="DashboardPage",
                schema_version=versioning.current_version,
                primary_anchor_id="page-shell",
                section_anchors=[
                    SectionAnchorDefinition(
                        anchor_id="page-shell",
                        semantic_role="page_shell",
                        layout_role="shell",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="page-header",
                        semantic_role="page_header",
                        layout_role="header",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="summary-band",
                        semantic_role="summary_band",
                        layout_role="summary",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="filter-scope",
                        semantic_role="filter_scope",
                        layout_role="toolbar",
                        required=False,
                    ),
                    SectionAnchorDefinition(
                        anchor_id="main-insight",
                        semantic_role="main_insight",
                        layout_role="content",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="secondary-section",
                        semantic_role="secondary_section",
                        layout_role="aside",
                        required=False,
                    ),
                    SectionAnchorDefinition(
                        anchor_id="state-feedback",
                        semantic_role="state_feedback",
                        layout_role="state",
                    ),
                ],
                field_blocks=[
                    FieldBlockDefinition(
                        block_id="dashboard-filter-inputs",
                        anchor_id="filter-scope",
                        field_semantics=["date_range", "segment_filter"],
                        cardinality="repeatable",
                    )
                ],
            ),
            PageSchemaDefinition(
                page_schema_id="search-list-workspace",
                page_recipe_id="SearchListPage",
                schema_version=versioning.current_version,
                primary_anchor_id="page-shell",
                section_anchors=[
                    SectionAnchorDefinition(
                        anchor_id="page-shell",
                        semantic_role="page_shell",
                        layout_role="shell",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="page-header",
                        semantic_role="page_header",
                        layout_role="header",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="search-area",
                        semantic_role="search_area",
                        layout_role="search",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="result-summary",
                        semantic_role="result_summary",
                        layout_role="summary",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="content-area",
                        semantic_role="content_area",
                        layout_role="content",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="pagination-area",
                        semantic_role="pagination_area",
                        layout_role="footer",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="state-feedback",
                        semantic_role="state_feedback",
                        layout_role="state",
                    ),
                ],
                field_blocks=[
                    FieldBlockDefinition(
                        block_id="search-query-block",
                        anchor_id="search-area",
                        field_semantics=["query", "scope_selector"],
                    )
                ],
            ),
            PageSchemaDefinition(
                page_schema_id="wizard-workspace",
                page_recipe_id="WizardPage",
                schema_version=versioning.current_version,
                primary_anchor_id="page-shell",
                section_anchors=[
                    SectionAnchorDefinition(
                        anchor_id="page-shell",
                        semantic_role="page_shell",
                        layout_role="shell",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="page-header",
                        semantic_role="page_header",
                        layout_role="header",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="step-progress",
                        semantic_role="step_progress",
                        layout_role="progress",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="step-content",
                        semantic_role="step_content",
                        layout_role="content",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="action-bar",
                        semantic_role="action_bar",
                        layout_role="footer",
                    ),
                    SectionAnchorDefinition(
                        anchor_id="state-feedback",
                        semantic_role="state_feedback",
                        layout_role="state",
                    ),
                ],
                field_blocks=[
                    FieldBlockDefinition(
                        block_id="wizard-step-fields",
                        anchor_id="step-content",
                        field_semantics=["form_fields", "step_notes"],
                        cardinality="repeatable",
                    )
                ],
            ),
        ],
        ui_schemas=[
            UiSchemaDefinition(
                ui_schema_id="dashboard-workspace-default",
                page_schema_id="dashboard-workspace",
                schema_version=versioning.current_version,
                root_slot_id="page-shell",
                render_slots=[
                    RenderSlotDefinition(
                        slot_id="page-shell",
                        anchor_id="page-shell",
                        component_id="UiSection",
                    ),
                    RenderSlotDefinition(
                        slot_id="page-header",
                        anchor_id="page-header",
                        component_id="UiPageHeader",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="summary-band",
                        anchor_id="summary-band",
                        component_id="UiSection",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="main-insight",
                        anchor_id="main-insight",
                        component_id="UiCard",
                        parent_slot_id="page-shell",
                        cardinality="repeatable",
                        required_state_ids=["refreshing"],
                    ),
                    RenderSlotDefinition(
                        slot_id="secondary-section",
                        anchor_id="secondary-section",
                        component_id="UiSection",
                        parent_slot_id="page-shell",
                        cardinality="repeatable",
                    ),
                    RenderSlotDefinition(
                        slot_id="state-feedback",
                        anchor_id="state-feedback",
                        component_id="UiResult",
                        parent_slot_id="page-shell",
                        required_state_ids=["partial-error"],
                    ),
                ],
            ),
            UiSchemaDefinition(
                ui_schema_id="search-list-workspace-default",
                page_schema_id="search-list-workspace",
                schema_version=versioning.current_version,
                root_slot_id="page-shell",
                render_slots=[
                    RenderSlotDefinition(
                        slot_id="page-shell",
                        anchor_id="page-shell",
                        component_id="UiSection",
                    ),
                    RenderSlotDefinition(
                        slot_id="page-header",
                        anchor_id="page-header",
                        component_id="UiPageHeader",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="search-area",
                        anchor_id="search-area",
                        component_id="UiSearchBar",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="result-summary",
                        anchor_id="result-summary",
                        component_id="UiResult",
                        parent_slot_id="page-shell",
                        required_state_ids=["no-results"],
                    ),
                    RenderSlotDefinition(
                        slot_id="content-area",
                        anchor_id="content-area",
                        component_id="UiTable",
                        parent_slot_id="page-shell",
                        required_state_ids=["refreshing"],
                    ),
                    RenderSlotDefinition(
                        slot_id="pagination-area",
                        anchor_id="pagination-area",
                        component_id="UiPagination",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="state-feedback",
                        anchor_id="state-feedback",
                        component_id="UiResult",
                        parent_slot_id="page-shell",
                        required_state_ids=["partial-error"],
                    ),
                ],
            ),
            UiSchemaDefinition(
                ui_schema_id="wizard-workspace-default",
                page_schema_id="wizard-workspace",
                schema_version=versioning.current_version,
                root_slot_id="page-shell",
                render_slots=[
                    RenderSlotDefinition(
                        slot_id="page-shell",
                        anchor_id="page-shell",
                        component_id="UiSection",
                    ),
                    RenderSlotDefinition(
                        slot_id="page-header",
                        anchor_id="page-header",
                        component_id="UiPageHeader",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="step-content",
                        anchor_id="step-content",
                        component_id="UiForm",
                        parent_slot_id="page-shell",
                        required_state_ids=["submitting"],
                    ),
                    RenderSlotDefinition(
                        slot_id="step-fields",
                        anchor_id="step-content",
                        component_id="UiFormItem",
                        parent_slot_id="step-content",
                        cardinality="repeatable",
                    ),
                    RenderSlotDefinition(
                        slot_id="action-bar",
                        anchor_id="action-bar",
                        component_id="UiToolbar",
                        parent_slot_id="page-shell",
                    ),
                    RenderSlotDefinition(
                        slot_id="state-feedback",
                        anchor_id="state-feedback",
                        component_id="UiResult",
                        parent_slot_id="page-shell",
                        required_state_ids=["success-feedback", "partial-error"],
                    ),
                ],
            ),
        ],
    )


__all__ = [
    "FieldBlockDefinition",
    "FrontendPageUiSchemaSet",
    "PageSchemaDefinition",
    "RenderSlotDefinition",
    "SchemaVersioningContract",
    "SectionAnchorDefinition",
    "UiSchemaDefinition",
    "build_p2_frontend_page_ui_schema_baseline",
]
