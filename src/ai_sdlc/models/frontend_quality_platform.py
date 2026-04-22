"""Frontend quality platform baseline models for work item 149."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ai_sdlc.models.frontend_page_ui_schema import (
    FrontendPageUiSchemaSet,
    build_p2_frontend_page_ui_schema_baseline,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceSet,
    build_p2_frontend_theme_token_governance_baseline,
)

QualityVerdictFamily = Literal[
    "visual-regression",
    "complete-a11y",
    "interaction-quality",
]
QualityGateState = Literal["pass", "advisory", "recheck", "block"]
QualityEvidenceState = Literal["complete", "partial", "missing"]
QualitySeverity = Literal["info", "low", "medium", "high"]
BrowserId = Literal["chromium", "webkit", "firefox"]
ViewportId = Literal["desktop-1440", "tablet-834", "mobile-390"]
TruthLayer = Literal["planning-truth", "runtime-truth", "release-gate-input"]

_ARTIFACT_ROOT = "governance/frontend/quality-platform"
_CANONICAL_FILES = [
    "quality-platform.manifest.yaml",
    "handoff.schema.yaml",
    "coverage-matrix.yaml",
    "evidence-platform.yaml",
    "interaction-quality.yaml",
    "truth-surfacing.yaml",
]
_REQUIRED_PROGRAM_SERVICE_FIELDS = {
    "matrix_id",
    "page_schema_id",
    "browser_id",
    "viewport_id",
    "style_pack_id",
    "gate_state",
}
_REQUIRED_CLI_FIELDS = {
    "matrix_id",
    "page_schema_id",
    "browser_id",
    "viewport_id",
    "gate_state",
}
_REQUIRED_VERIFY_FIELDS = {
    "matrix_id",
    "page_schema_id",
    "browser_id",
    "viewport_id",
    "style_pack_id",
    "gate_state",
    "evidence_state",
}


def _find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _dedupe_strings(value: object) -> list[str]:
    if value is None:
        return []
    unique: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item)
        if text in seen:
            continue
        seen.add(text)
        unique.append(text)
    return unique


class FrontendQualityPlatformModel(BaseModel):
    """Base model for structured quality-platform artifacts."""

    model_config = ConfigDict(extra="forbid")


class QualityCoverageMatrixEntry(FrontendQualityPlatformModel):
    """One structured quality coverage cell across page/theme/browser/device dimensions."""

    matrix_id: str
    page_schema_id: str
    browser_id: BrowserId
    viewport_id: ViewportId
    style_pack_id: str
    interaction_flow_id: str
    evidence_contract_ids: list[str] = Field(default_factory=list)

    @field_validator("evidence_contract_ids", mode="before")
    @classmethod
    def _dedupe_evidence_contract_ids(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_entry(self) -> QualityCoverageMatrixEntry:
        if not self.evidence_contract_ids:
            raise ValueError("evidence_contract_ids must not be empty")
        return self


class QualityEvidenceContract(FrontendQualityPlatformModel):
    """Machine-verifiable evidence contract carried by the quality platform."""

    evidence_contract_id: str
    evidence_kind: QualityVerdictFamily
    artifact_rel_path: str
    required_payload_fields: list[str] = Field(default_factory=list)

    @field_validator("required_payload_fields", mode="before")
    @classmethod
    def _dedupe_required_payload_fields(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_contract(self) -> QualityEvidenceContract:
        if not self.artifact_rel_path.startswith(_ARTIFACT_ROOT):
            raise ValueError("artifact_rel_path must stay inside governance/frontend/quality-platform")
        if not self.required_payload_fields:
            raise ValueError("required_payload_fields must not be empty")
        return self


class InteractionQualityFlow(FrontendQualityPlatformModel):
    """Structured interaction flow contract for richer runtime probing."""

    flow_id: str
    page_schema_id: str
    required_probe_sources: list[str] = Field(default_factory=list)
    focus_areas: list[str] = Field(default_factory=list)
    remediation_hints: list[str] = Field(default_factory=list)

    @field_validator(
        "required_probe_sources",
        "focus_areas",
        "remediation_hints",
        mode="before",
    )
    @classmethod
    def _dedupe_flow_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_flow(self) -> InteractionQualityFlow:
        if not self.required_probe_sources:
            raise ValueError("required_probe_sources must not be empty")
        if not self.focus_areas:
            raise ValueError("focus_areas must not be empty")
        return self


class QualityVerdictEnvelope(FrontendQualityPlatformModel):
    """Unified quality verdict surfaced to Track D, CLI, and verify consumers."""

    verdict_id: str
    matrix_id: str
    verdict_family: QualityVerdictFamily
    gate_state: QualityGateState
    evidence_state: QualityEvidenceState
    severity: QualitySeverity
    evidence_refs: list[str] = Field(default_factory=list)
    remediation_hint: str | None = None

    @field_validator("evidence_refs", mode="before")
    @classmethod
    def _dedupe_evidence_refs(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_verdict(self) -> QualityVerdictEnvelope:
        if not self.evidence_refs:
            raise ValueError("evidence_refs must not be empty")
        if any(not ref.startswith("artifact:") for ref in self.evidence_refs):
            raise ValueError("evidence_refs must use artifact: references")
        if self.gate_state == "block" and self.severity in {"info", "low"}:
            raise ValueError("block verdicts require medium-or-higher severity")
        return self


class QualityTruthSurfacingRecord(FrontendQualityPlatformModel):
    """Stable truth-surfacing payload for global truth and Track D consumers."""

    matrix_id: str
    truth_layer: TruthLayer
    gate_state: QualityGateState
    evidence_state: QualityEvidenceState
    artifact_root_ref: str
    verdict_ref: str


class QualityPlatformHandoffContract(FrontendQualityPlatformModel):
    """Versioned handoff schema and minimum consumer field contract."""

    schema_family: str
    current_version: str
    compatible_versions: list[str] = Field(default_factory=list)
    artifact_root: str
    canonical_files: list[str] = Field(default_factory=list)
    program_service_fields: list[str] = Field(default_factory=list)
    cli_fields: list[str] = Field(default_factory=list)
    verify_fields: list[str] = Field(default_factory=list)

    @field_validator(
        "compatible_versions",
        "canonical_files",
        "program_service_fields",
        "cli_fields",
        "verify_fields",
        mode="before",
    )
    @classmethod
    def _dedupe_handoff_lists(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_contract(self) -> QualityPlatformHandoffContract:
        if self.current_version not in self.compatible_versions:
            raise ValueError("current_version must be included in compatible_versions")
        if not self.canonical_files:
            raise ValueError("canonical_files must not be empty")
        if not _REQUIRED_PROGRAM_SERVICE_FIELDS.issubset(self.program_service_fields):
            raise ValueError("program_service_fields missing required fields")
        if not _REQUIRED_CLI_FIELDS.issubset(self.cli_fields):
            raise ValueError("cli_fields missing required fields")
        if not _REQUIRED_VERIFY_FIELDS.issubset(self.verify_fields):
            raise ValueError("verify_fields missing required fields")
        return self


class FrontendQualityPlatformSet(FrontendQualityPlatformModel):
    """Top-level baseline for Track C quality truth."""

    work_item_id: str
    source_work_item_ids: list[str] = Field(default_factory=list)
    coverage_matrix: list[QualityCoverageMatrixEntry] = Field(default_factory=list)
    evidence_contracts: list[QualityEvidenceContract] = Field(default_factory=list)
    interaction_flows: list[InteractionQualityFlow] = Field(default_factory=list)
    verdict_envelopes: list[QualityVerdictEnvelope] = Field(default_factory=list)
    truth_surfacing_records: list[QualityTruthSurfacingRecord] = Field(default_factory=list)
    handoff_contract: QualityPlatformHandoffContract

    @field_validator("source_work_item_ids", mode="before")
    @classmethod
    def _dedupe_source_work_item_ids(cls, value: object) -> list[str]:
        return _dedupe_strings(value)

    @model_validator(mode="after")
    def _validate_set(self) -> FrontendQualityPlatformSet:
        duplicate_matrix_ids = _find_duplicates(
            [entry.matrix_id for entry in self.coverage_matrix]
        )
        if duplicate_matrix_ids:
            joined = ", ".join(duplicate_matrix_ids)
            raise ValueError(f"duplicate matrix ids: {joined}")

        duplicate_contract_ids = _find_duplicates(
            [contract.evidence_contract_id for contract in self.evidence_contracts]
        )
        if duplicate_contract_ids:
            joined = ", ".join(duplicate_contract_ids)
            raise ValueError(f"duplicate evidence contract ids: {joined}")

        duplicate_flow_ids = _find_duplicates(
            [flow.flow_id for flow in self.interaction_flows]
        )
        if duplicate_flow_ids:
            joined = ", ".join(duplicate_flow_ids)
            raise ValueError(f"duplicate interaction flow ids: {joined}")

        duplicate_verdict_ids = _find_duplicates(
            [verdict.verdict_id for verdict in self.verdict_envelopes]
        )
        if duplicate_verdict_ids:
            joined = ", ".join(duplicate_verdict_ids)
            raise ValueError(f"duplicate verdict ids: {joined}")

        known_contract_ids = {
            contract.evidence_contract_id for contract in self.evidence_contracts
        }
        unknown_contract_ids = sorted(
            {
                contract_id
                for entry in self.coverage_matrix
                for contract_id in entry.evidence_contract_ids
                if contract_id not in known_contract_ids
            }
        )
        if unknown_contract_ids:
            joined = ", ".join(unknown_contract_ids)
            raise ValueError(f"unknown evidence contract ids: {joined}")

        known_flow_ids = {flow.flow_id for flow in self.interaction_flows}
        unknown_flow_ids = sorted(
            {
                entry.interaction_flow_id
                for entry in self.coverage_matrix
                if entry.interaction_flow_id not in known_flow_ids
            }
        )
        if unknown_flow_ids:
            joined = ", ".join(unknown_flow_ids)
            raise ValueError(f"unknown interaction flow ids: {joined}")

        known_matrix_ids = {entry.matrix_id for entry in self.coverage_matrix}
        unknown_matrix_ids = sorted(
            {
                verdict.matrix_id
                for verdict in self.verdict_envelopes
                if verdict.matrix_id not in known_matrix_ids
            }
        )
        if unknown_matrix_ids:
            joined = ", ".join(unknown_matrix_ids)
            raise ValueError(f"unknown matrix ids: {joined}")

        known_verdict_ids = {verdict.verdict_id for verdict in self.verdict_envelopes}
        for record in self.truth_surfacing_records:
            if not record.verdict_ref.startswith("verdict:"):
                raise ValueError("truth surfacing verdict_ref must use verdict: references")
            verdict_id = record.verdict_ref.split(":", 1)[1]
            if verdict_id not in known_verdict_ids:
                raise ValueError(f"truth surfacing references unknown verdict: {verdict_id}")
            if record.matrix_id not in known_matrix_ids:
                raise ValueError(f"truth surfacing references unknown matrix: {record.matrix_id}")

        return self


def _require_page_schema(
    page_ui_schema: FrontendPageUiSchemaSet,
    page_schema_id: str,
) -> str:
    for page_schema in page_ui_schema.page_schemas:
        if page_schema.page_schema_id == page_schema_id:
            return page_schema_id
    raise ValueError(f"missing required page schema for 149 baseline: {page_schema_id}")


def _require_style_pack(
    theme_governance: FrontendThemeTokenGovernanceSet,
    style_pack_id: str,
) -> str:
    if style_pack_id not in theme_governance.style_pack_ids:
        raise ValueError(f"missing required style pack for 149 baseline: {style_pack_id}")
    return style_pack_id


def build_p2_frontend_quality_platform_baseline(
    *,
    page_ui_schema: FrontendPageUiSchemaSet | None = None,
    theme_governance: FrontendThemeTokenGovernanceSet | None = None,
) -> FrontendQualityPlatformSet:
    """Build the Track C quality platform baseline defined by work item 149."""

    effective_page_ui_schema = page_ui_schema or build_p2_frontend_page_ui_schema_baseline()
    effective_theme_governance = (
        theme_governance or build_p2_frontend_theme_token_governance_baseline()
    )

    dashboard_page = _require_page_schema(effective_page_ui_schema, "dashboard-workspace")
    search_page = _require_page_schema(
        effective_page_ui_schema,
        "search-list-workspace",
    )
    modern_saas = _require_style_pack(effective_theme_governance, "modern-saas")
    enterprise_default = _require_style_pack(
        effective_theme_governance,
        "enterprise-default",
    )

    evidence_contracts = [
        QualityEvidenceContract(
            evidence_contract_id="visual-regression-evidence",
            evidence_kind="visual-regression",
            artifact_rel_path=(
                "governance/frontend/quality-platform/evidence/visual-regression"
            ),
            required_payload_fields=["screenshot_ref", "diff_ratio"],
        ),
        QualityEvidenceContract(
            evidence_contract_id="a11y-matrix-evidence",
            evidence_kind="complete-a11y",
            artifact_rel_path="governance/frontend/quality-platform/evidence/a11y",
            required_payload_fields=["axe_summary_ref", "issue_count"],
        ),
        QualityEvidenceContract(
            evidence_contract_id="interaction-quality-evidence",
            evidence_kind="interaction-quality",
            artifact_rel_path="governance/frontend/quality-platform/evidence/interaction",
            required_payload_fields=["trace_ref", "focus_jumps", "feedback_latency_ms"],
        ),
    ]
    interaction_flows = [
        InteractionQualityFlow(
            flow_id="dashboard-review-flow",
            page_schema_id=dashboard_page,
            required_probe_sources=["143:browser-probe", "144:host-remediation"],
            focus_areas=["focus-continuity", "feedback-timing"],
            remediation_hints=[
                "stabilize async loading placeholders",
                "preserve keyboard focus across review actions",
            ],
        ),
        InteractionQualityFlow(
            flow_id="search-filter-flow",
            page_schema_id=search_page,
            required_probe_sources=["143:browser-probe", "144:workspace-runtime"],
            focus_areas=["input-continuity", "result-feedback-ordering"],
            remediation_hints=[
                "keep filter inputs mounted during result refresh",
                "surface loading and empty states deterministically",
            ],
        ),
    ]
    coverage_matrix = [
        QualityCoverageMatrixEntry(
            matrix_id="dashboard-modern-saas-desktop-chromium",
            page_schema_id=dashboard_page,
            browser_id="chromium",
            viewport_id="desktop-1440",
            style_pack_id=modern_saas,
            interaction_flow_id="dashboard-review-flow",
            evidence_contract_ids=[
                "visual-regression-evidence",
                "a11y-matrix-evidence",
            ],
        ),
        QualityCoverageMatrixEntry(
            matrix_id="dashboard-modern-saas-mobile-webkit",
            page_schema_id=dashboard_page,
            browser_id="webkit",
            viewport_id="mobile-390",
            style_pack_id=modern_saas,
            interaction_flow_id="dashboard-review-flow",
            evidence_contract_ids=[
                "a11y-matrix-evidence",
                "interaction-quality-evidence",
            ],
        ),
        QualityCoverageMatrixEntry(
            matrix_id="search-enterprise-default-desktop-chromium",
            page_schema_id=search_page,
            browser_id="chromium",
            viewport_id="desktop-1440",
            style_pack_id=enterprise_default,
            interaction_flow_id="search-filter-flow",
            evidence_contract_ids=[
                "visual-regression-evidence",
                "interaction-quality-evidence",
            ],
        ),
    ]
    verdict_envelopes = [
        QualityVerdictEnvelope(
            verdict_id="dashboard-visual-pass",
            matrix_id="dashboard-modern-saas-desktop-chromium",
            verdict_family="visual-regression",
            gate_state="pass",
            evidence_state="complete",
            severity="info",
            evidence_refs=[
                "artifact:governance/frontend/quality-platform/evidence/visual-regression/dashboard-visual-pass.yaml"
            ],
        ),
        QualityVerdictEnvelope(
            verdict_id="dashboard-a11y-advisory",
            matrix_id="dashboard-modern-saas-mobile-webkit",
            verdict_family="complete-a11y",
            gate_state="advisory",
            evidence_state="partial",
            severity="medium",
            evidence_refs=[
                "artifact:governance/frontend/quality-platform/evidence/a11y/dashboard-a11y-advisory.yaml"
            ],
            remediation_hint="verify mobile dialog semantics and heading hierarchy",
        ),
        QualityVerdictEnvelope(
            verdict_id="search-interaction-pass",
            matrix_id="search-enterprise-default-desktop-chromium",
            verdict_family="interaction-quality",
            gate_state="pass",
            evidence_state="complete",
            severity="info",
            evidence_refs=[
                "artifact:governance/frontend/quality-platform/evidence/interaction/search-interaction-pass.yaml"
            ],
        ),
    ]
    truth_surfacing_records = [
        QualityTruthSurfacingRecord(
            matrix_id=verdict.matrix_id,
            truth_layer="runtime-truth",
            gate_state=verdict.gate_state,
            evidence_state=verdict.evidence_state,
            artifact_root_ref=_ARTIFACT_ROOT,
            verdict_ref=f"verdict:{verdict.verdict_id}",
        )
        for verdict in verdict_envelopes
    ]

    return FrontendQualityPlatformSet(
        work_item_id="149",
        source_work_item_ids=["071", "137", "143", "144", "147", "148"],
        coverage_matrix=coverage_matrix,
        evidence_contracts=evidence_contracts,
        interaction_flows=interaction_flows,
        verdict_envelopes=verdict_envelopes,
        truth_surfacing_records=truth_surfacing_records,
        handoff_contract=QualityPlatformHandoffContract(
            schema_family="frontend-quality-platform",
            current_version="1.0",
            compatible_versions=["1.0"],
            artifact_root=_ARTIFACT_ROOT,
            canonical_files=list(_CANONICAL_FILES),
            program_service_fields=sorted(_REQUIRED_PROGRAM_SERVICE_FIELDS),
            cli_fields=sorted(_REQUIRED_CLI_FIELDS),
            verify_fields=sorted(_REQUIRED_VERIFY_FIELDS),
        ),
    )


__all__ = [
    "BrowserId",
    "FrontendQualityPlatformSet",
    "InteractionQualityFlow",
    "QualityCoverageMatrixEntry",
    "QualityEvidenceContract",
    "QualityEvidenceState",
    "QualityGateState",
    "QualityPlatformHandoffContract",
    "QualitySeverity",
    "QualityTruthSurfacingRecord",
    "QualityVerdictEnvelope",
    "QualityVerdictFamily",
    "ViewportId",
    "build_p2_frontend_quality_platform_baseline",
]
