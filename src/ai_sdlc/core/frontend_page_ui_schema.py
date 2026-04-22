"""Validation and handoff helpers for frontend page/UI schema baseline."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_sdlc.models.frontend_page_ui_schema import FrontendPageUiSchemaSet
from ai_sdlc.models.frontend_solution_confirmation import FrontendSolutionSnapshot
from ai_sdlc.models.frontend_ui_kernel import FrontendUiKernelSet


def _dedupe_text_items(items: list[str] | tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


@dataclass(frozen=True, slots=True)
class FrontendPageUiSchemaValidationResult:
    """Structured validation result for page/UI schema truth."""

    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    page_schema_ids: list[str] = field(default_factory=list)
    ui_schema_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "blockers", _dedupe_text_items(self.blockers))
        object.__setattr__(self, "warnings", _dedupe_text_items(self.warnings))
        object.__setattr__(
            self, "page_schema_ids", _dedupe_text_items(self.page_schema_ids)
        )
        object.__setattr__(self, "ui_schema_ids", _dedupe_text_items(self.ui_schema_ids))


@dataclass(frozen=True, slots=True)
class FrontendPageUiSchemaHandoffEntry:
    """Provider/kernel handoff row for one page schema."""

    page_schema_id: str
    ui_schema_id: str
    page_recipe_id: str
    anchor_ids: list[str] = field(default_factory=list)
    slot_ids: list[str] = field(default_factory=list)
    component_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "anchor_ids", _dedupe_text_items(self.anchor_ids))
        object.__setattr__(self, "slot_ids", _dedupe_text_items(self.slot_ids))
        object.__setattr__(
            self, "component_ids", _dedupe_text_items(self.component_ids)
        )


@dataclass(frozen=True, slots=True)
class FrontendPageUiSchemaHandoff:
    """Structured downstream handoff surface for page/UI schema truth."""

    state: str
    schema_version: str
    effective_provider_id: str
    effective_style_pack_id: str
    delivery_entry_id: str = ""
    component_library_packages: list[str] = field(default_factory=list)
    provider_theme_adapter_id: str = ""
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    entries: list[FrontendPageUiSchemaHandoffEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "component_library_packages",
            _dedupe_text_items(self.component_library_packages),
        )
        object.__setattr__(self, "blockers", _dedupe_text_items(self.blockers))
        object.__setattr__(self, "warnings", _dedupe_text_items(self.warnings))


def validate_frontend_page_ui_schema_set(
    schema_set: FrontendPageUiSchemaSet,
    kernel: FrontendUiKernelSet,
) -> FrontendPageUiSchemaValidationResult:
    """Validate page/UI schema truth against kernel recipe, component, and state truth."""

    blockers: list[str] = []
    page_schema_ids = [page.page_schema_id for page in schema_set.page_schemas]
    ui_schema_ids = [ui.ui_schema_id for ui in schema_set.ui_schemas]

    known_recipe_ids = {recipe.recipe_id for recipe in kernel.page_recipes}
    unknown_recipe_ids = sorted(
        {
            page.page_recipe_id
            for page in schema_set.page_schemas
            if page.page_recipe_id not in known_recipe_ids
        }
    )
    if unknown_recipe_ids:
        blockers.append(
            "unknown page recipes: " + ", ".join(unknown_recipe_ids)
        )

    known_component_ids = {
        component.component_id for component in kernel.semantic_components
    }
    unknown_component_ids = sorted(
        {
            slot.component_id
            for ui_schema in schema_set.ui_schemas
            for slot in ui_schema.render_slots
            if slot.component_id not in known_component_ids
        }
    )
    if unknown_component_ids:
        blockers.append(
            "unknown UI Kernel components: " + ", ".join(unknown_component_ids)
        )

    known_state_ids = set(kernel.state_baseline.required_states)
    unknown_state_ids = sorted(
        {
            state_id
            for ui_schema in schema_set.ui_schemas
            for slot in ui_schema.render_slots
            for state_id in slot.required_state_ids
            if state_id not in known_state_ids
        }
    )
    if unknown_state_ids:
        blockers.append("unknown UI Kernel states: " + ", ".join(unknown_state_ids))

    ui_page_schema_ids = {ui.page_schema_id for ui in schema_set.ui_schemas}
    missing_ui_schema_ids = sorted(
        page_id for page_id in page_schema_ids if page_id not in ui_page_schema_ids
    )
    if missing_ui_schema_ids:
        blockers.append(
            "page schemas missing matching ui schema: " + ", ".join(missing_ui_schema_ids)
        )

    return FrontendPageUiSchemaValidationResult(
        passed=not blockers,
        blockers=_dedupe_text_items(blockers),
        warnings=_dedupe_text_items([]),
        page_schema_ids=_dedupe_text_items(page_schema_ids),
        ui_schema_ids=_dedupe_text_items(ui_schema_ids),
    )


def build_frontend_page_ui_schema_handoff(
    schema_set: FrontendPageUiSchemaSet,
    *,
    kernel: FrontendUiKernelSet,
    solution_snapshot: FrontendSolutionSnapshot | None,
) -> FrontendPageUiSchemaHandoff:
    """Package page/UI schema truth for downstream provider and kernel consumers."""

    validation = validate_frontend_page_ui_schema_set(schema_set, kernel)
    blockers = list(validation.blockers)
    effective_provider_id = ""
    effective_style_pack_id = ""
    if solution_snapshot is None:
        blockers.append("frontend_solution_snapshot_missing")
    else:
        effective_provider_id = solution_snapshot.effective_provider_id
        effective_style_pack_id = solution_snapshot.effective_style_pack_id

    ui_schema_by_page_id = {
        ui_schema.page_schema_id: ui_schema for ui_schema in schema_set.ui_schemas
    }
    entries = [
        FrontendPageUiSchemaHandoffEntry(
            page_schema_id=page_schema.page_schema_id,
            ui_schema_id=ui_schema_by_page_id[page_schema.page_schema_id].ui_schema_id,
            page_recipe_id=page_schema.page_recipe_id,
            anchor_ids=_dedupe_text_items(
                [anchor.anchor_id for anchor in page_schema.section_anchors]
            ),
            slot_ids=_dedupe_text_items(
                [
                    slot.slot_id
                    for slot in ui_schema_by_page_id[page_schema.page_schema_id].render_slots
                ]
            ),
            component_ids=_dedupe_text_items(
                [
                    slot.component_id
                    for slot in ui_schema_by_page_id[page_schema.page_schema_id].render_slots
                ]
            ),
        )
        for page_schema in schema_set.page_schemas
        if page_schema.page_schema_id in ui_schema_by_page_id
    ]

    return FrontendPageUiSchemaHandoff(
        state="ready" if not blockers else "blocked",
        schema_version=schema_set.versioning.current_version,
        effective_provider_id=effective_provider_id,
        effective_style_pack_id=effective_style_pack_id,
        blockers=_dedupe_text_items(blockers),
        warnings=_dedupe_text_items(validation.warnings),
        entries=entries,
    )


__all__ = [
    "FrontendPageUiSchemaHandoff",
    "FrontendPageUiSchemaHandoffEntry",
    "FrontendPageUiSchemaValidationResult",
    "build_frontend_page_ui_schema_handoff",
    "validate_frontend_page_ui_schema_set",
]
