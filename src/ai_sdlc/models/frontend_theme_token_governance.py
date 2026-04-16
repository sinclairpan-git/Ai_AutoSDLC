"""Frontend theme token governance baseline models for work item 148."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ai_sdlc.models.frontend_generation_constraints import (
    FrontendGenerationConstraintSet,
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    FrontendPageUiSchemaSet,
    PageSchemaDefinition,
    UiSchemaDefinition,
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    StylePackManifest,
    build_builtin_style_pack_manifests,
)

ThemeScope = Literal["global", "page", "section", "slot"]

_CANONICAL_IA = [
    "theme-list",
    "effective-state-summary",
    "diff-override-drawer",
    "revert-approve-path",
]
_ALLOWED_OVERRIDE_NAMESPACES = {
    "surface",
    "accent",
    "density",
    "border",
    "typography",
    "spacing",
    "radius",
    "shadow",
    "motion",
    "glass",
}


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


class FrontendThemeTokenGovernanceModel(BaseModel):
    """Base model for structured theme/token governance artifacts."""

    model_config = ConfigDict(extra="forbid")


class ThemeTokenMapping(FrontendThemeTokenGovernanceModel):
    """Reference-based mapping from semantic theme token to upstream style pack tokens."""

    mapping_id: str
    style_pack_id: str
    scope: ThemeScope
    page_schema_id: str | None = None
    schema_anchor_id: str | None = None
    render_slot_id: str | None = None
    token_refs: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_scope_contract(self) -> ThemeTokenMapping:
        if not self.token_refs:
            raise ValueError("token_refs must not be empty")
        for token_ref in self.token_refs.values():
            if not token_ref.startswith("style-pack:"):
                raise ValueError("token_refs must use style-pack references")
        if self.scope in {"page", "section", "slot"} and not self.page_schema_id:
            raise ValueError(f"{self.scope} mappings require page_schema_id")
        if self.scope == "section" and not self.schema_anchor_id:
            raise ValueError("section mappings require schema_anchor_id")
        if self.scope == "slot" and not self.render_slot_id:
            raise ValueError("slot mappings require render_slot_id")
        return self


class CustomThemeTokenOverride(FrontendThemeTokenGovernanceModel):
    """Structured override envelope used by the read-only diagnostics/proposal flow."""

    override_id: str
    scope: ThemeScope
    page_schema_id: str | None = None
    schema_anchor_id: str | None = None
    render_slot_id: str | None = None
    namespace: str
    token_key: str
    requested_value: str
    effective_value: str
    fallback_reason_code: str | None = None

    @model_validator(mode="after")
    def _validate_override_contract(self) -> CustomThemeTokenOverride:
        if self.namespace not in _ALLOWED_OVERRIDE_NAMESPACES:
            raise ValueError(f"unsupported override namespace: {self.namespace}")
        if self.scope in {"page", "section", "slot"} and not self.page_schema_id:
            raise ValueError(f"{self.scope} overrides require page_schema_id")
        if self.scope == "section" and not self.schema_anchor_id:
            raise ValueError("section overrides require schema_anchor_id")
        if self.scope == "slot" and not self.render_slot_id:
            raise ValueError("slot overrides require render_slot_id")
        if (
            self.requested_value != self.effective_value
            and not self.fallback_reason_code
        ):
            raise ValueError(
                "fallback_reason_code is required when requested/effective mismatch"
            )
        return self


class StyleEditorBoundaryContract(FrontendThemeTokenGovernanceModel):
    """Frozen v1 style editor boundary from the formal baseline."""

    surface_mode: Literal["read_only_diagnostics_structured_proposal"]
    canonical_information_architecture: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_boundary_contract(self) -> StyleEditorBoundaryContract:
        if self.canonical_information_architecture != _CANONICAL_IA:
            raise ValueError("canonical_information_architecture must match v1 flow")
        if "direct-runtime-write" in self.allowed_actions:
            raise ValueError("direct-runtime-write cannot be an allowed style editor action")
        if "direct-runtime-write" not in self.forbidden_actions:
            raise ValueError("direct-runtime-write must remain forbidden in v1 boundary")
        return self


class ThemeGovernanceHandoffContract(FrontendThemeTokenGovernanceModel):
    """Versioned machine-verifiable handoff schema for later artifact materialization."""

    schema_family: str
    current_version: str
    compatible_versions: list[str] = Field(default_factory=list)
    artifact_root: str
    canonical_files: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_handoff_contract(self) -> ThemeGovernanceHandoffContract:
        if self.current_version not in self.compatible_versions:
            raise ValueError(
                "current_version must be included in compatible_versions"
            )
        if not self.canonical_files:
            raise ValueError("canonical_files must not be empty")
        return self


class FrontendThemeTokenGovernanceSet(FrontendThemeTokenGovernanceModel):
    """Top-level baseline for theme/token governance truth."""

    work_item_id: str
    source_work_item_ids: list[str] = Field(default_factory=list)
    token_floor_disallowed_naked_values: list[str] = Field(default_factory=list)
    style_pack_ids: list[str] = Field(default_factory=list)
    override_precedence: list[ThemeScope] = Field(default_factory=list)
    token_mappings: list[ThemeTokenMapping] = Field(default_factory=list)
    custom_overrides: list[CustomThemeTokenOverride] = Field(default_factory=list)
    style_editor_boundary: StyleEditorBoundaryContract
    handoff_contract: ThemeGovernanceHandoffContract

    @model_validator(mode="after")
    def _validate_governance_set(self) -> FrontendThemeTokenGovernanceSet:
        duplicate_style_pack_ids = _find_duplicates(self.style_pack_ids)
        if duplicate_style_pack_ids:
            joined = ", ".join(duplicate_style_pack_ids)
            raise ValueError(f"duplicate style pack ids: {joined}")

        if self.override_precedence != ["global", "page", "section", "slot"]:
            raise ValueError(
                "override_precedence must be frozen to global -> page -> section -> slot"
            )

        duplicate_mapping_ids = _find_duplicates(
            [mapping.mapping_id for mapping in self.token_mappings]
        )
        if duplicate_mapping_ids:
            joined = ", ".join(duplicate_mapping_ids)
            raise ValueError(f"duplicate mapping ids: {joined}")

        duplicate_override_ids = _find_duplicates(
            [override.override_id for override in self.custom_overrides]
        )
        if duplicate_override_ids:
            joined = ", ".join(duplicate_override_ids)
            raise ValueError(f"duplicate override ids: {joined}")

        known_style_pack_ids = set(self.style_pack_ids)
        unknown_style_pack_ids = [
            mapping.style_pack_id
            for mapping in self.token_mappings
            if mapping.style_pack_id not in known_style_pack_ids
        ]
        if unknown_style_pack_ids:
            joined = ", ".join(sorted(set(unknown_style_pack_ids)))
            raise ValueError(f"token_mappings reference unknown style_pack_id: {joined}")
        return self


def _select_page_schema(
    page_ui_schema: FrontendPageUiSchemaSet, page_schema_id: str
) -> PageSchemaDefinition:
    for page_schema in page_ui_schema.page_schemas:
        if page_schema.page_schema_id == page_schema_id:
            return page_schema
    raise ValueError(f"missing required page schema for 148 baseline: {page_schema_id}")


def _select_ui_schema(
    page_ui_schema: FrontendPageUiSchemaSet, page_schema_id: str
) -> UiSchemaDefinition:
    for ui_schema in page_ui_schema.ui_schemas:
        if ui_schema.page_schema_id == page_schema_id:
            return ui_schema
    raise ValueError(f"missing required ui schema for 148 baseline: {page_schema_id}")


def _build_style_pack_token_refs(style_pack: StylePackManifest) -> dict[str, str]:
    return {
        token_key: f"style-pack:{style_pack.style_pack_id}:{token_key}"
        for token_key in style_pack.design_tokens
    }


def build_p2_frontend_theme_token_governance_baseline(
    *,
    constraints: FrontendGenerationConstraintSet | None = None,
    style_packs: list[StylePackManifest] | None = None,
    page_ui_schema: FrontendPageUiSchemaSet | None = None,
) -> FrontendThemeTokenGovernanceSet:
    """Build the provider-neutral theme/token governance baseline defined by work item 148."""

    effective_constraints = constraints or build_mvp_frontend_generation_constraints()
    effective_style_packs = style_packs or build_builtin_style_pack_manifests()
    effective_page_ui_schema = page_ui_schema or build_p2_frontend_page_ui_schema_baseline()

    dashboard_page_schema = _select_page_schema(
        effective_page_ui_schema, "dashboard-workspace"
    )
    dashboard_ui_schema = _select_ui_schema(
        effective_page_ui_schema, dashboard_page_schema.page_schema_id
    )
    header_anchor_id = next(
        (
            anchor.anchor_id
            for anchor in dashboard_page_schema.section_anchors
            if anchor.anchor_id == "page-header"
        ),
        dashboard_page_schema.section_anchors[0].anchor_id,
    )
    section_anchor_id = next(
        (
            anchor.anchor_id
            for anchor in dashboard_page_schema.section_anchors
            if anchor.anchor_id == "summary-band"
        ),
        dashboard_page_schema.section_anchors[0].anchor_id,
    )
    slot_id = next(
        (
            slot.slot_id
            for slot in dashboard_ui_schema.render_slots
            if slot.parent_slot_id == dashboard_ui_schema.root_slot_id
        ),
        dashboard_ui_schema.root_slot_id,
    )

    global_mappings = [
        ThemeTokenMapping(
            mapping_id=f"{style_pack.style_pack_id}-global",
            style_pack_id=style_pack.style_pack_id,
            scope="global",
            token_refs=_build_style_pack_token_refs(style_pack),
        )
        for style_pack in effective_style_packs
    ]

    scoped_mappings = [
        ThemeTokenMapping(
            mapping_id="dashboard-workspace-page-theme",
            style_pack_id="enterprise-default",
            scope="page",
            page_schema_id=dashboard_page_schema.page_schema_id,
            token_refs={"surface_mode": "style-pack:enterprise-default:surface_mode"},
        ),
        ThemeTokenMapping(
            mapping_id="dashboard-page-header-section-theme",
            style_pack_id="enterprise-default",
            scope="section",
            page_schema_id=dashboard_page_schema.page_schema_id,
            schema_anchor_id=header_anchor_id,
            token_refs={"accent_mode": "style-pack:enterprise-default:accent_mode"},
        ),
        ThemeTokenMapping(
            mapping_id="dashboard-summary-slot-theme",
            style_pack_id="enterprise-default",
            scope="slot",
            page_schema_id=dashboard_page_schema.page_schema_id,
            render_slot_id=slot_id,
            token_refs={"density": "style-pack:enterprise-default:density"},
        ),
    ]

    return FrontendThemeTokenGovernanceSet(
        work_item_id="148",
        source_work_item_ids=["017", "073", "147"],
        token_floor_disallowed_naked_values=list(
            effective_constraints.token_rules.disallowed_naked_values
        ),
        style_pack_ids=[style_pack.style_pack_id for style_pack in effective_style_packs],
        override_precedence=["global", "page", "section", "slot"],
        token_mappings=global_mappings + scoped_mappings,
        custom_overrides=[
            CustomThemeTokenOverride(
                override_id="dashboard-page-header-accent-proposal",
                scope="section",
                page_schema_id=dashboard_page_schema.page_schema_id,
                schema_anchor_id=section_anchor_id,
                namespace="accent",
                token_key="accent_mode",
                requested_value="brand-accent",
                effective_value="style-pack:enterprise-default:accent_mode",
                fallback_reason_code="style-editor-read-only-proposal",
            )
        ],
        style_editor_boundary=StyleEditorBoundaryContract(
            surface_mode="read_only_diagnostics_structured_proposal",
            canonical_information_architecture=list(_CANONICAL_IA),
            allowed_actions=[
                "inspect-effective-theme",
                "inspect-token-mapping",
                "submit-structured-proposal",
            ],
            forbidden_actions=[
                "direct-runtime-write",
                "freeform-css-entry",
                "provider-token-edit",
            ],
        ),
        handoff_contract=ThemeGovernanceHandoffContract(
            schema_family="frontend-theme-token-governance",
            current_version="1.0",
            compatible_versions=["1.0"],
            artifact_root="governance/frontend/theme-token-governance",
            canonical_files=[
                "theme-governance-manifest.json",
                "token-mapping.json",
                "override-policy.json",
                "style-editor-boundary.json",
            ],
        ),
    )
