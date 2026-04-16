"""Validation helpers for frontend quality platform baseline."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_sdlc.models.frontend_page_ui_schema import FrontendPageUiSchemaSet
from ai_sdlc.models.frontend_quality_platform import FrontendQualityPlatformSet
from ai_sdlc.models.frontend_solution_confirmation import FrontendSolutionSnapshot
from ai_sdlc.models.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceSet,
)

_ALLOWED_BROWSERS = {"chromium", "webkit", "firefox"}
_ALLOWED_VIEWPORTS = {"desktop-1440", "tablet-834", "mobile-390"}


@dataclass(frozen=True, slots=True)
class FrontendQualityPlatformValidationResult:
    """Structured validation result for Track C quality truth."""

    passed: bool
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact_root: str = ""
    matrix_coverage_count: int = 0
    page_schema_ids: list[str] = field(default_factory=list)
    evidence_contract_ids: list[str] = field(default_factory=list)


def validate_frontend_quality_platform(
    platform: FrontendQualityPlatformSet,
    *,
    page_ui_schema: FrontendPageUiSchemaSet,
    theme_governance: FrontendThemeTokenGovernanceSet,
    solution_snapshot: FrontendSolutionSnapshot,
) -> FrontendQualityPlatformValidationResult:
    """Validate Track C quality truth against 147 and 148 upstream inputs."""

    blockers: list[str] = []
    warnings: list[str] = []
    known_page_schema_ids = {
        page_schema.page_schema_id for page_schema in page_ui_schema.page_schemas
    }
    known_style_pack_ids = set(theme_governance.style_pack_ids)
    known_flow_ids = {flow.flow_id for flow in platform.interaction_flows}
    known_matrix_ids = {entry.matrix_id for entry in platform.coverage_matrix}

    for entry in platform.coverage_matrix:
        if entry.page_schema_id not in known_page_schema_ids:
            blockers.append(f"unknown page schema: {entry.page_schema_id}")
        if entry.style_pack_id not in known_style_pack_ids:
            blockers.append(f"unknown style pack: {entry.style_pack_id}")
        if entry.browser_id not in _ALLOWED_BROWSERS:
            blockers.append(f"unsupported browser id: {entry.browser_id}")
        if entry.viewport_id not in _ALLOWED_VIEWPORTS:
            blockers.append(f"unsupported viewport id: {entry.viewport_id}")
        if entry.interaction_flow_id not in known_flow_ids:
            blockers.append(f"unknown interaction flow: {entry.interaction_flow_id}")

    for flow in platform.interaction_flows:
        if flow.page_schema_id not in known_page_schema_ids:
            blockers.append(f"unknown page schema: {flow.page_schema_id}")

    for verdict in platform.verdict_envelopes:
        if verdict.matrix_id not in known_matrix_ids:
            blockers.append(f"unknown matrix id: {verdict.matrix_id}")
        if verdict.gate_state == "advisory":
            warnings.append(f"advisory quality verdict: {verdict.verdict_id}")

    if solution_snapshot.effective_style_pack_id not in known_style_pack_ids:
        blockers.append(
            "effective style pack outside theme governance: "
            f"{solution_snapshot.effective_style_pack_id}"
        )

    return FrontendQualityPlatformValidationResult(
        passed=not blockers,
        blockers=blockers,
        warnings=warnings,
        artifact_root=platform.handoff_contract.artifact_root,
        matrix_coverage_count=len(platform.coverage_matrix),
        page_schema_ids=sorted({entry.page_schema_id for entry in platform.coverage_matrix}),
        evidence_contract_ids=sorted(
            contract.evidence_contract_id for contract in platform.evidence_contracts
        ),
    )


__all__ = [
    "FrontendQualityPlatformValidationResult",
    "validate_frontend_quality_platform",
]
