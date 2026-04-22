"""Validation helpers for frontend theme token governance baseline."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ai_sdlc.models.frontend_generation_constraints import (
    FrontendGenerationConstraintSet,
)
from ai_sdlc.models.frontend_page_ui_schema import FrontendPageUiSchemaSet
from ai_sdlc.models.frontend_provider_profile import EnterpriseVue2ProviderProfile
from ai_sdlc.models.frontend_solution_confirmation import FrontendSolutionSnapshot
from ai_sdlc.models.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceSet,
)

_HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_RGB_COLOR_PATTERN = re.compile(r"^rgb\(", re.IGNORECASE)
_RGBA_COLOR_PATTERN = re.compile(r"^rgba\(", re.IGNORECASE)
_SIZE_PATTERN = re.compile(r"^\d+(?:\.\d+)?(?:px|rem|em|%)$")
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
class FrontendThemeTokenGovernanceValidationResult:
    """Structured validation result for theme/token governance truth."""

    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact_root: str = ""
    provider_id: str = ""
    effective_style_pack_id: str = ""
    referenced_anchor_ids: list[str] = field(default_factory=list)
    referenced_slot_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "blockers", _dedupe_text_items(self.blockers))
        object.__setattr__(self, "warnings", _dedupe_text_items(self.warnings))
        object.__setattr__(
            self,
            "referenced_anchor_ids",
            _dedupe_text_items(self.referenced_anchor_ids),
        )
        object.__setattr__(
            self,
            "referenced_slot_ids",
            _dedupe_text_items(self.referenced_slot_ids),
        )


def validate_frontend_theme_token_governance(
    governance: FrontendThemeTokenGovernanceSet,
    *,
    constraints: FrontendGenerationConstraintSet,
    page_ui_schema: FrontendPageUiSchemaSet,
    provider_profile: EnterpriseVue2ProviderProfile,
    solution_snapshot: FrontendSolutionSnapshot,
) -> FrontendThemeTokenGovernanceValidationResult:
    """Validate theme/token governance truth against 017, 073, and 147 upstream inputs."""

    blockers: list[str] = []
    warnings: list[str] = []
    known_page_schema_ids = {
        page_schema.page_schema_id for page_schema in page_ui_schema.page_schemas
    }
    known_anchor_ids = {
        anchor.anchor_id
        for page_schema in page_ui_schema.page_schemas
        for anchor in page_schema.section_anchors
    }
    known_slot_ids = {
        slot.slot_id
        for ui_schema in page_ui_schema.ui_schemas
        for slot in ui_schema.render_slots
    }

    for mapping in governance.token_mappings:
        if mapping.page_schema_id and mapping.page_schema_id not in known_page_schema_ids:
            blockers.append(f"unknown page schema: {mapping.page_schema_id}")
        if mapping.schema_anchor_id and mapping.schema_anchor_id not in known_anchor_ids:
            blockers.append(f"unknown schema anchor: {mapping.schema_anchor_id}")
        if mapping.render_slot_id and mapping.render_slot_id not in known_slot_ids:
            blockers.append(f"unknown render slot: {mapping.render_slot_id}")

    disallowed_naked_values = set(constraints.token_rules.disallowed_naked_values)
    for override in governance.custom_overrides:
        if override.page_schema_id and override.page_schema_id not in known_page_schema_ids:
            blockers.append(f"unknown page schema: {override.page_schema_id}")
        if override.schema_anchor_id and override.schema_anchor_id not in known_anchor_ids:
            blockers.append(f"unknown schema anchor: {override.schema_anchor_id}")
        if override.render_slot_id and override.render_slot_id not in known_slot_ids:
            blockers.append(f"unknown render slot: {override.render_slot_id}")
        if override.namespace not in _ALLOWED_OVERRIDE_NAMESPACES:
            blockers.append(f"illegal override namespace: {override.namespace}")

        for value in (override.requested_value, override.effective_value):
            naked_value_kind = _classify_naked_value(value)
            if naked_value_kind in disallowed_naked_values:
                blockers.append(
                    "token floor bypass: "
                    f"{override.override_id} uses forbidden {naked_value_kind}"
                )

    style_support_by_id = {
        entry.style_pack_id: entry for entry in provider_profile.style_support_matrix
    }
    style_support = style_support_by_id.get(solution_snapshot.effective_style_pack_id)
    if style_support is None or style_support.fidelity_status == "unsupported":
        blockers.append(
            "unsupported provider/style pair: "
            f"{solution_snapshot.effective_provider_id}/"
            f"{solution_snapshot.effective_style_pack_id}"
        )
    elif style_support.fidelity_status in {"partial", "degraded"}:
        warnings.append(
            "degraded provider/style pair: "
            f"{solution_snapshot.effective_provider_id}/"
            f"{solution_snapshot.effective_style_pack_id}"
        )

    return FrontendThemeTokenGovernanceValidationResult(
        passed=not blockers,
        blockers=_dedupe_text_items(blockers),
        warnings=_dedupe_text_items(warnings),
        artifact_root=governance.handoff_contract.artifact_root,
        provider_id=solution_snapshot.effective_provider_id,
        effective_style_pack_id=solution_snapshot.effective_style_pack_id,
        referenced_anchor_ids=sorted(
            _dedupe_text_items(
                [
                    mapping.schema_anchor_id
                    for mapping in governance.token_mappings
                    if mapping.schema_anchor_id
                ]
                + [
                    override.schema_anchor_id
                    for override in governance.custom_overrides
                    if override.schema_anchor_id
                ]
            )
        ),
        referenced_slot_ids=sorted(
            _dedupe_text_items(
                [
                    mapping.render_slot_id
                    for mapping in governance.token_mappings
                    if mapping.render_slot_id
                ]
                + [
                    override.render_slot_id
                    for override in governance.custom_overrides
                    if override.render_slot_id
                ]
            )
        ),
    )


def _classify_naked_value(value: str) -> str | None:
    stripped = value.strip()
    if _HEX_COLOR_PATTERN.fullmatch(stripped):
        return "hex-color"
    if _RGBA_COLOR_PATTERN.match(stripped):
        return "rgba-color"
    if _RGB_COLOR_PATTERN.match(stripped):
        return "rgb-color"
    if "shadow" in stripped.lower():
        return "shadow"
    if _SIZE_PATTERN.fullmatch(stripped):
        return "spacing-or-size"
    return None


__all__ = [
    "FrontendThemeTokenGovernanceValidationResult",
    "validate_frontend_theme_token_governance",
]
