"""Frontend UI Kernel data models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


class FrontendUiKernelModel(BaseModel):
    """Base model for frontend UI Kernel artifacts."""

    model_config = ConfigDict(extra="forbid")


class UiProtocolComponent(FrontendUiKernelModel):
    """Semantic component protocol defined by the UI Kernel."""

    component_id: str
    semantic_role: str
    supported_states: list[str] = Field(default_factory=list)
    supported_events: list[str] = Field(default_factory=list)
    disallowed_capabilities: list[str] = Field(default_factory=list)


class PageRecipeStandard(FrontendUiKernelModel):
    """Canonical recipe body for one page shape."""

    recipe_id: str
    required_areas: list[str] = Field(default_factory=list)
    optional_areas: list[str] = Field(default_factory=list)
    required_protocols: list[str] = Field(default_factory=list)
    forbidden_patterns: list[str] = Field(default_factory=list)
    interaction_rules: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _reject_overlapping_areas(self) -> PageRecipeStandard:
        overlap = [area for area in self.required_areas if area in self.optional_areas]
        if overlap:
            joined = ", ".join(overlap)
            raise ValueError(f"required_areas and optional_areas overlap: {joined}")
        return self


class KernelStateBaseline(FrontendUiKernelModel):
    """Page-level state baseline required by the Kernel."""

    required_states: list[str] = Field(default_factory=list)
    state_priority_scope: str = "page_or_recipe"


class KernelInteractionBaseline(FrontendUiKernelModel):
    """Interaction and minimum accessibility baseline for the Kernel."""

    rules: list[str] = Field(default_factory=list)
    minimum_a11y_rules: list[str] = Field(default_factory=list)


class FrontendUiKernelSet(FrontendUiKernelModel):
    """Top-level UI Kernel baseline for one work item."""

    work_item_id: str
    format_version: str = "1.0"
    semantic_components: list[UiProtocolComponent] = Field(default_factory=list)
    page_recipes: list[PageRecipeStandard] = Field(default_factory=list)
    state_baseline: KernelStateBaseline
    interaction_baseline: KernelInteractionBaseline

    @model_validator(mode="after")
    def _enforce_unique_ids(self) -> FrontendUiKernelSet:
        duplicate_component_ids = _find_duplicates(
            [component.component_id for component in self.semantic_components]
        )
        if duplicate_component_ids:
            joined = ", ".join(duplicate_component_ids)
            raise ValueError(f"duplicate component_id values: {joined}")

        duplicate_recipe_ids = _find_duplicates(
            [recipe.recipe_id for recipe in self.page_recipes]
        )
        if duplicate_recipe_ids:
            joined = ", ".join(duplicate_recipe_ids)
            raise ValueError(f"duplicate recipe_id values: {joined}")
        return self


def build_mvp_frontend_ui_kernel() -> FrontendUiKernelSet:
    """Build the MVP UI Kernel baseline defined by work item 015."""

    return FrontendUiKernelSet(
        work_item_id="015",
        semantic_components=[
            UiProtocolComponent(
                component_id="UiButton",
                semantic_role="action_trigger",
                supported_states=["disabled"],
                supported_events=["click"],
                disallowed_capabilities=["raw provider api passthrough"],
            ),
            UiProtocolComponent(
                component_id="UiInput",
                semantic_role="text_input",
                supported_states=["disabled", "error"],
                supported_events=["change", "blur"],
                disallowed_capabilities=["unstyled naked input fallback"],
            ),
            UiProtocolComponent(
                component_id="UiSelect",
                semantic_role="selection_input",
                supported_states=["disabled", "error"],
                supported_events=["change"],
                disallowed_capabilities=["provider specific option rendering contract"],
            ),
            UiProtocolComponent(
                component_id="UiForm",
                semantic_role="form_container",
                supported_states=["disabled", "error"],
                supported_events=["submit", "reset"],
                disallowed_capabilities=["freeform layout masquerading as form"],
            ),
            UiProtocolComponent(
                component_id="UiFormItem",
                semantic_role="form_field_slot",
                supported_states=["error", "disabled"],
                supported_events=["validate"],
                disallowed_capabilities=["unstructured validation copy only"],
            ),
            UiProtocolComponent(
                component_id="UiTable",
                semantic_role="structured_list_content",
                supported_states=["loading", "empty", "error"],
                supported_events=["row-select", "paginate"],
                disallowed_capabilities=["arbitrary div list replacing table semantics"],
            ),
            UiProtocolComponent(
                component_id="UiDialog",
                semantic_role="modal_confirmation",
                supported_states=["disabled"],
                supported_events=["open", "close", "confirm"],
                disallowed_capabilities=["implicit destructive action execution"],
            ),
            UiProtocolComponent(
                component_id="UiDrawer",
                semantic_role="side_panel_container",
                supported_states=["disabled"],
                supported_events=["open", "close"],
                disallowed_capabilities=["layout-only provider passthrough"],
            ),
            UiProtocolComponent(
                component_id="UiEmpty",
                semantic_role="empty_state_expression",
                supported_states=["empty"],
                disallowed_capabilities=["silent absence of feedback"],
            ),
            UiProtocolComponent(
                component_id="UiSpinner",
                semantic_role="loading_state_expression",
                supported_states=["loading"],
                disallowed_capabilities=["invisible loading transition"],
            ),
            UiProtocolComponent(
                component_id="UiPageHeader",
                semantic_role="page_header_shell",
                supported_events=["back", "primary-action"],
                disallowed_capabilities=["content area ownership"],
            ),
        ],
        page_recipes=[
            PageRecipeStandard(
                recipe_id="ListPage",
                required_areas=[
                    "PageHeader",
                    "Filter / Search Area",
                    "Primary Action Area",
                    "Content Area",
                    "State Area",
                    "Pagination Area",
                ],
                required_protocols=["UiPageHeader", "UiTable"],
                optional_areas=["Bulk Action Area", "Row Detail Area"],
                forbidden_patterns=[
                    "mix primary actions into filter area",
                    "replace list content with arbitrary raw structure",
                ],
                interaction_rules=[
                    "loading, empty, and error states must be explicit",
                    "primary action and filtering semantics stay separated",
                ],
            ),
            PageRecipeStandard(
                recipe_id="FormPage",
                required_areas=[
                    "PageHeader",
                    "Form Content Area",
                    "Action Area",
                    "State Area",
                ],
                required_protocols=["UiForm", "UiFormItem"],
                optional_areas=["Help Area", "Grouped Section Area", "Submission Feedback Area"],
                forbidden_patterns=[
                    "replace structured validation with prose-only guidance",
                    "compose pseudo forms without UiForm or UiFormItem",
                ],
                interaction_rules=[
                    "form fields are driven by validation contract",
                    "submit and cancel actions remain semantically distinct",
                ],
            ),
            PageRecipeStandard(
                recipe_id="DetailPage",
                required_areas=[
                    "PageHeader",
                    "Summary Area",
                    "Detail Content Area",
                    "Action Area",
                    "State Area",
                ],
                required_protocols=["UiPageHeader"],
                optional_areas=["Associated Data Area", "Extended Information Area"],
                forbidden_patterns=[
                    "mix page actions into detail content",
                    "force read-only detail flow into form semantics",
                ],
                interaction_rules=[
                    "detail partitions remain explicit",
                    "empty and error states remain perceivable",
                ],
            ),
        ],
        state_baseline=KernelStateBaseline(
            required_states=["loading", "empty", "error", "disabled", "no-permission"]
        ),
        interaction_baseline=KernelInteractionBaseline(
            rules=[
                "primary and secondary actions remain semantically distinct",
                "submit, cancel, and back behaviors are explicit",
                "validation errors must have explicit feedback",
                "dangerous actions require explicit confirmation",
                "recipe areas must not be broken by arbitrary layout drift",
            ],
            minimum_a11y_rules=[
                "form error feedback must be perceivable",
                "state transitions must be perceivable",
                "critical state may not rely only on visual position",
                "interactive components keep recognizable semantics",
            ],
        ),
    )


__all__ = [
    "FrontendUiKernelSet",
    "KernelInteractionBaseline",
    "KernelStateBaseline",
    "PageRecipeStandard",
    "UiProtocolComponent",
    "build_mvp_frontend_ui_kernel",
]
