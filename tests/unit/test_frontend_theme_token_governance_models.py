"""Unit tests for frontend theme token governance models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_style_pack_manifests,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    CustomThemeTokenOverride,
    FrontendThemeTokenGovernanceSet,
    StyleEditorBoundaryContract,
    ThemeGovernanceHandoffContract,
    ThemeTokenMapping,
    build_p2_frontend_theme_token_governance_baseline,
)


def _boundary() -> StyleEditorBoundaryContract:
    return StyleEditorBoundaryContract(
        surface_mode="read_only_diagnostics_structured_proposal",
        canonical_information_architecture=[
            "theme-list",
            "effective-state-summary",
            "diff-override-drawer",
            "revert-approve-path",
        ],
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
    )


def _handoff() -> ThemeGovernanceHandoffContract:
    return ThemeGovernanceHandoffContract(
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
    )


def test_build_p2_frontend_theme_token_governance_baseline_inherits_upstream_truth_without_copying_inventory() -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    style_pack_ids = [
        manifest.style_pack_id for manifest in build_builtin_style_pack_manifests()
    ]
    page_ui_schema = build_p2_frontend_page_ui_schema_baseline()
    anchor_ids = {
        anchor.anchor_id
        for page in page_ui_schema.page_schemas
        for anchor in page.section_anchors
    }
    slot_ids = {
        slot.slot_id for ui_schema in page_ui_schema.ui_schemas for slot in ui_schema.render_slots
    }

    assert governance.work_item_id == "148"
    assert governance.source_work_item_ids == ["017", "073", "147"]
    assert governance.style_pack_ids == style_pack_ids
    assert governance.override_precedence == ["global", "page", "section", "slot"]
    assert governance.style_editor_boundary.surface_mode == (
        "read_only_diagnostics_structured_proposal"
    )
    assert governance.style_editor_boundary.canonical_information_architecture == [
        "theme-list",
        "effective-state-summary",
        "diff-override-drawer",
        "revert-approve-path",
    ]
    assert governance.handoff_contract.artifact_root == (
        "governance/frontend/theme-token-governance"
    )
    assert any(mapping.scope == "page" for mapping in governance.token_mappings)
    assert any(
        mapping.scope == "section" and mapping.schema_anchor_id in anchor_ids
        for mapping in governance.token_mappings
    )
    assert any(
        mapping.scope == "slot" and mapping.render_slot_id in slot_ids
        for mapping in governance.token_mappings
    )
    assert all(
        token_ref.startswith("style-pack:")
        for mapping in governance.token_mappings
        for token_ref in mapping.token_refs.values()
    )


def test_frontend_theme_token_governance_set_rejects_duplicate_mapping_ids() -> None:
    with pytest.raises(ValueError, match="duplicate mapping ids"):
        FrontendThemeTokenGovernanceSet(
            work_item_id="148",
            source_work_item_ids=["017", "073", "147"],
            token_floor_disallowed_naked_values=["hex-color", "rgb-color"],
            style_pack_ids=["enterprise-default"],
            override_precedence=["global", "page", "section", "slot"],
            token_mappings=[
                ThemeTokenMapping(
                    mapping_id="enterprise-default-global",
                    style_pack_id="enterprise-default",
                    scope="global",
                    token_refs={"surface_mode": "style-pack:enterprise-default:surface_mode"},
                ),
                ThemeTokenMapping(
                    mapping_id="enterprise-default-global",
                    style_pack_id="enterprise-default",
                    scope="global",
                    token_refs={"accent_mode": "style-pack:enterprise-default:accent_mode"},
                ),
            ],
            custom_overrides=[],
            style_editor_boundary=_boundary(),
            handoff_contract=_handoff(),
        )


def test_theme_token_mapping_rejects_unknown_scope() -> None:
    with pytest.raises(ValidationError):
        ThemeTokenMapping(
            mapping_id="bad-scope",
            style_pack_id="enterprise-default",
            scope="workspace",
            token_refs={"surface_mode": "style-pack:enterprise-default:surface_mode"},
        )


def test_custom_theme_token_override_rejects_illegal_namespace() -> None:
    with pytest.raises(ValueError, match="unsupported override namespace"):
        CustomThemeTokenOverride(
            override_id="bad-namespace",
            scope="global",
            namespace="provider-internal-token",
            token_key="accent_mode",
            requested_value="brand-accent",
            effective_value="brand-accent",
        )


def test_custom_theme_token_override_requires_resolution_reason_when_requested_and_effective_mismatch() -> None:
    with pytest.raises(ValueError, match="fallback_reason_code is required"):
        CustomThemeTokenOverride(
            override_id="mismatch-without-reason",
            scope="section",
            page_schema_id="dashboard-workspace",
            schema_anchor_id="page-header",
            namespace="accent",
            token_key="accent_mode",
            requested_value="brand-accent",
            effective_value="style-pack:enterprise-default:accent_mode",
        )
