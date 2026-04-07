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


def _find_unknown_references(values: list[str], known_values: set[str]) -> list[str]:
    unknown: list[str] = []
    for value in values:
        if value not in known_values and value not in unknown:
            unknown.append(value)
    return unknown


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
    consumed_protocols: list[str] = Field(default_factory=list)
    minimum_state_expectations: list[str] = Field(default_factory=list)
    forbidden_patterns: list[str] = Field(default_factory=list)
    interaction_rules: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_recipe_structure(self) -> PageRecipeStandard:
        overlap = [area for area in self.required_areas if area in self.optional_areas]
        if overlap:
            joined = ", ".join(overlap)
            raise ValueError(f"required_areas and optional_areas overlap: {joined}")

        if self.consumed_protocols:
            missing_required_protocols = [
                protocol
                for protocol in self.required_protocols
                if protocol not in self.consumed_protocols
            ]
            if missing_required_protocols:
                joined = ", ".join(missing_required_protocols)
                raise ValueError(
                    "required_protocols must be included in consumed_protocols: "
                    f"{joined}"
                )
        return self


class KernelStateSemantic(FrontendUiKernelModel):
    """Structured semantic meaning for one page-level state."""

    state_id: str
    semantic_meaning: str
    boundary: str


class KernelStateBaseline(FrontendUiKernelModel):
    """Page-level state baseline required by the Kernel."""

    required_states: list[str] = Field(default_factory=list)
    state_priority_scope: str = "page_or_recipe"
    state_semantics: list[KernelStateSemantic] | None = None

    @model_validator(mode="after")
    def _enforce_state_semantics_reference_declared_states(self) -> KernelStateBaseline:
        if self.state_semantics is None:
            return self

        duplicate_state_ids = _find_duplicates(
            [semantic.state_id for semantic in self.state_semantics]
        )
        if duplicate_state_ids:
            joined = ", ".join(duplicate_state_ids)
            raise ValueError(f"duplicate state_semantics state_id values: {joined}")

        unknown_state_ids = [
            semantic.state_id
            for semantic in self.state_semantics
            if semantic.state_id not in self.required_states
        ]
        if unknown_state_ids:
            joined = ", ".join(unknown_state_ids)
            raise ValueError(f"state_semantics reference unknown required_states: {joined}")
        return self


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

        component_ids = {
            component.component_id for component in self.semantic_components
        }
        unknown_required_protocols = _find_unknown_references(
            [
                protocol
                for recipe in self.page_recipes
                for protocol in recipe.required_protocols
            ],
            component_ids,
        )
        if unknown_required_protocols:
            joined = ", ".join(unknown_required_protocols)
            raise ValueError(
                f"page_recipes reference unknown required_protocols: {joined}"
            )

        unknown_consumed_protocols = _find_unknown_references(
            [
                protocol
                for recipe in self.page_recipes
                for protocol in recipe.consumed_protocols
            ],
            component_ids,
        )
        if unknown_consumed_protocols:
            joined = ", ".join(unknown_consumed_protocols)
            raise ValueError(
                f"page_recipes reference unknown consumed_protocols: {joined}"
            )

        state_ids = set(self.state_baseline.required_states)
        unknown_minimum_state_expectations = _find_unknown_references(
            [
                state_id
                for recipe in self.page_recipes
                for state_id in recipe.minimum_state_expectations
            ],
            state_ids,
        )
        if unknown_minimum_state_expectations:
            joined = ", ".join(unknown_minimum_state_expectations)
            raise ValueError(
                "page_recipes reference unknown minimum_state_expectations: "
                f"{joined}"
            )
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
                optional_areas=[
                    "Help Area",
                    "Grouped Section Area",
                    "Submission Feedback Area",
                ],
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


def build_p1_frontend_ui_kernel_semantic_expansion() -> FrontendUiKernelSet:
    """Build the P1 Kernel semantic expansion baseline defined by work item 067."""

    kernel = build_mvp_frontend_ui_kernel()

    return FrontendUiKernelSet(
        work_item_id="067",
        format_version=kernel.format_version,
        semantic_components=[
            *[component.model_copy(deep=True) for component in kernel.semantic_components],
            UiProtocolComponent(
                component_id="UiTabs",
                semantic_role="segmented_navigation_container",
                supported_states=["disabled"],
                supported_events=["change"],
                disallowed_capabilities=["provider specific tab api passthrough"],
            ),
            UiProtocolComponent(
                component_id="UiSearchBar",
                semantic_role="search_input_and_trigger",
                supported_states=["disabled"],
                supported_events=["change", "submit", "clear"],
                disallowed_capabilities=["implicit page recipe replacement"],
            ),
            UiProtocolComponent(
                component_id="UiFilterBar",
                semantic_role="filter_condition_collection",
                supported_states=["disabled"],
                supported_events=["change", "apply", "clear"],
                disallowed_capabilities=["provider specific filter panel dominance"],
            ),
            UiProtocolComponent(
                component_id="UiResult",
                semantic_role="structured_result_feedback",
                supported_states=["success-feedback", "partial-error", "error"],
                disallowed_capabilities=["generic toast message substitution"],
            ),
            UiProtocolComponent(
                component_id="UiSection",
                semantic_role="page_section_partition",
                disallowed_capabilities=["page recipe body replacement"],
            ),
            UiProtocolComponent(
                component_id="UiToolbar",
                semantic_role="in_page_action_cluster",
                supported_states=["disabled"],
                disallowed_capabilities=["layout api passthrough"],
            ),
            UiProtocolComponent(
                component_id="UiPagination",
                semantic_role="result_set_navigation",
                supported_states=["disabled"],
                supported_events=["paginate"],
                disallowed_capabilities=["provider data table pagination api binding"],
            ),
            UiProtocolComponent(
                component_id="UiCard",
                semantic_role="structured_info_block",
                disallowed_capabilities=["pure visual box contract"],
            ),
        ],
        page_recipes=[recipe.model_copy(deep=True) for recipe in kernel.page_recipes],
        state_baseline=KernelStateBaseline(
            required_states=[
                *kernel.state_baseline.required_states,
                "refreshing",
                "submitting",
                "no-results",
                "partial-error",
                "success-feedback",
            ],
            state_priority_scope=kernel.state_baseline.state_priority_scope,
            state_semantics=[
                KernelStateSemantic(
                    state_id="refreshing",
                    semantic_meaning="refreshing existing page content",
                    boundary="supplements loading when prior content already exists",
                ),
                KernelStateSemantic(
                    state_id="submitting",
                    semantic_meaning="form or local page action submission is in progress",
                    boundary="does not replace disabled; it describes submission progress",
                ),
                KernelStateSemantic(
                    state_id="no-results",
                    semantic_meaning="search or filter results are empty",
                    boundary="distinct from empty without active query or filter context",
                ),
                KernelStateSemantic(
                    state_id="partial-error",
                    semantic_meaning="only part of the page or region failed",
                    boundary="does not collapse into global error while other content remains available",
                ),
                KernelStateSemantic(
                    state_id="success-feedback",
                    semantic_meaning="limited success acknowledgement after an action completes",
                    boundary="does not replace long-lived page state or structured result rendering",
                ),
            ],
        ),
        interaction_baseline=KernelInteractionBaseline(
            rules=[
                *kernel.interaction_baseline.rules,
                "search and filter flows must distinguish empty from no-results",
                "partial failures remain explicit without collapsing the whole page",
                "success feedback stays bounded and does not replace structured result rendering",
            ],
            minimum_a11y_rules=[
                *kernel.interaction_baseline.minimum_a11y_rules,
                "refreshing and submitting progress must stay perceivable when prior content remains visible",
                "partial error and success feedback must not rely on a single visual cue",
            ],
        ),
    )

def build_p1_frontend_ui_kernel_page_recipe_expansion() -> FrontendUiKernelSet:
    """Build the P1 page recipe expansion baseline defined by work item 068."""

    kernel = build_p1_frontend_ui_kernel_semantic_expansion()

    return FrontendUiKernelSet(
        work_item_id="068",
        format_version=kernel.format_version,
        semantic_components=[
            component.model_copy(deep=True) for component in kernel.semantic_components
        ],
        page_recipes=[
            *[recipe.model_copy(deep=True) for recipe in kernel.page_recipes],
            PageRecipeStandard(
                recipe_id="DashboardPage",
                required_areas=[
                    "PageHeader",
                    "Summary Area",
                    "Main Insight Area",
                    "State Area",
                ],
                optional_areas=[
                    "Filter Scope Area",
                    "Toolbar / Quick Action Area",
                    "Secondary Section Area",
                ],
                required_protocols=[
                    "UiPageHeader",
                    "UiSection",
                    "UiCard",
                    "UiResult",
                ],
                consumed_protocols=[
                    "UiPageHeader",
                    "UiSection",
                    "UiCard",
                    "UiResult",
                    "UiToolbar",
                ],
                minimum_state_expectations=["refreshing", "partial-error"],
                forbidden_patterns=[
                    "replace standard area structure with a freeform card wall",
                    "disguise a full form page or single list page as a dashboard",
                ],
                interaction_rules=[
                    "overview sections and cards remain structurally partitioned",
                    "dashboard refresh and partial failures stay explicit without replacing global loading or error",
                ],
            ),
            PageRecipeStandard(
                recipe_id="DialogFormPage",
                required_areas=[
                    "Overlay Shell Area",
                    "Title / Context Area",
                    "Form Area",
                    "Action Area",
                    "State / Validation Area",
                ],
                optional_areas=["Help / Description Area", "Secondary Section Area"],
                required_protocols=["UiForm", "UiFormItem", "UiResult"],
                consumed_protocols=[
                    "UiDialog",
                    "UiDrawer",
                    "UiForm",
                    "UiFormItem",
                    "UiResult",
                ],
                minimum_state_expectations=[
                    "submitting",
                    "partial-error",
                    "success-feedback",
                ],
                forbidden_patterns=[
                    "degrade into a provider modal API alias",
                    "use pagination or a freeform list area as the primary skeleton",
                    "mix multi-step flow semantics into a single-step dialog form",
                ],
                interaction_rules=[
                    "overlay shell semantics must be satisfied by UiDialog or UiDrawer without exposing provider APIs",
                    "submission, validation, and bounded success feedback remain explicit",
                ],
            ),
            PageRecipeStandard(
                recipe_id="SearchListPage",
                required_areas=[
                    "PageHeader",
                    "Search Area",
                    "Result Summary Area",
                    "Content Area",
                    "State Area",
                    "Pagination Area",
                ],
                optional_areas=["Filter Area", "Toolbar / Primary Action Area"],
                required_protocols=[
                    "UiPageHeader",
                    "UiSearchBar",
                    "UiTable",
                    "UiResult",
                    "UiPagination",
                ],
                consumed_protocols=[
                    "UiPageHeader",
                    "UiSearchBar",
                    "UiFilterBar",
                    "UiTable",
                    "UiResult",
                    "UiToolbar",
                    "UiPagination",
                ],
                minimum_state_expectations=[
                    "refreshing",
                    "no-results",
                    "partial-error",
                ],
                forbidden_patterns=[
                    "treat a list page without query context as a SearchListPage",
                    "skip result summary and assemble results as a freeform content zone",
                    "bypass pagination and state areas with arbitrary layout",
                ],
                interaction_rules=[
                    "query context, result summary, and content remain explicitly separated",
                    "filter and toolbar semantics stay subordinate to search result structure",
                ],
            ),
            PageRecipeStandard(
                recipe_id="WizardPage",
                required_areas=[
                    "PageHeader / Step Context Area",
                    "Step Progress Area",
                    "Step Content Area",
                    "Action Area",
                    "State / Feedback Area",
                ],
                optional_areas=["Review / Summary Area", "Help / Aside Area"],
                required_protocols=["UiForm", "UiFormItem", "UiResult"],
                consumed_protocols=[
                    "UiPageHeader",
                    "UiForm",
                    "UiFormItem",
                    "UiResult",
                ],
                minimum_state_expectations=[
                    "submitting",
                    "partial-error",
                    "success-feedback",
                ],
                forbidden_patterns=[
                    "use freeform tabs to impersonate step semantics",
                    "expose multiple parallel primary actions within one step",
                    "split step content into unordered freeform page fragments",
                ],
                interaction_rules=[
                    "step progression remains ordered even without introducing a dedicated stepper protocol",
                    "submission, partial failure, and bounded success feedback remain explicit across step transitions",
                ],
            ),
        ],
        state_baseline=kernel.state_baseline.model_copy(deep=True),
        interaction_baseline=kernel.interaction_baseline.model_copy(deep=True),
    )


__all__ = [
    "FrontendUiKernelSet",
    "KernelInteractionBaseline",
    "KernelStateBaseline",
    "KernelStateSemantic",
    "PageRecipeStandard",
    "UiProtocolComponent",
    "build_mvp_frontend_ui_kernel",
    "build_p1_frontend_ui_kernel_page_recipe_expansion",
    "build_p1_frontend_ui_kernel_semantic_expansion",
]
