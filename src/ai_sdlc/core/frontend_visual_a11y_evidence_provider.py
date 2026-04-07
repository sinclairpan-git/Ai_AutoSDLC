"""Frontend visual / a11y evidence provider artifact helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME = "frontend-visual-a11y-evidence.json"
FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION = "frontend-visual-a11y-evidence/v1"
FRONTEND_VISUAL_A11Y_REPORT_TYPES = (
    "violation-report",
    "coverage-report",
    "drift-report",
    "legacy-expansion-report",
)


@dataclass(frozen=True, slots=True)
class FrontendVisualA11yEvidenceProvenance:
    """Structured provenance for one visual / a11y evidence producer."""

    provider_kind: str
    provider_name: str
    provider_version: str | None = None
    source_ref: str | None = None


@dataclass(frozen=True, slots=True)
class FrontendVisualA11yEvidenceFreshness:
    """Structured freshness marker for one visual / a11y evidence artifact."""

    generated_at: str
    source_digest: str | None = None
    source_revision: str | None = None


@dataclass(frozen=True, slots=True)
class FrontendVisualA11yEvidenceEvaluation:
    """One visual / a11y evidence evaluation entry."""

    evaluation_id: str
    target_id: str
    surface_id: str
    outcome: str
    report_type: str | None = None
    severity: str | None = None
    location_anchor: str | None = None
    quality_hint: str | None = None
    changed_scope_explanation: str | None = None

    def to_json_dict(self) -> dict[str, object]:
        return {
            "evaluation_id": self.evaluation_id,
            "target_id": self.target_id,
            "surface_id": self.surface_id,
            "outcome": self.outcome,
            "report_type": self.report_type,
            "severity": self.severity,
            "location_anchor": self.location_anchor,
            "quality_hint": self.quality_hint,
            "changed_scope_explanation": self.changed_scope_explanation,
        }


@dataclass(frozen=True, slots=True)
class FrontendVisualA11yEvidenceArtifact:
    """Canonical provider artifact envelope for explicit visual / a11y evidence."""

    schema_version: str
    provenance: FrontendVisualA11yEvidenceProvenance
    freshness: FrontendVisualA11yEvidenceFreshness
    evaluations: tuple[FrontendVisualA11yEvidenceEvaluation, ...]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "provenance": {
                "provider_kind": self.provenance.provider_kind,
                "provider_name": self.provenance.provider_name,
                "provider_version": self.provenance.provider_version,
                "source_ref": self.provenance.source_ref,
            },
            "freshness": {
                "generated_at": self.freshness.generated_at,
                "source_digest": self.freshness.source_digest,
                "source_revision": self.freshness.source_revision,
            },
            "evaluations": [
                evaluation.to_json_dict() for evaluation in self.evaluations
            ],
        }


def visual_a11y_evidence_artifact_path(spec_dir: Path) -> Path:
    """Return the canonical visual / a11y evidence artifact path."""

    return spec_dir / FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME


def build_frontend_visual_a11y_evidence_artifact(
    *,
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
    provider_kind: str,
    provider_name: str,
    generated_at: str,
    provider_version: str | None = None,
    source_ref: str | None = None,
    source_digest: str | None = None,
    source_revision: str | None = None,
) -> FrontendVisualA11yEvidenceArtifact:
    """Build the canonical visual / a11y evidence envelope."""

    return FrontendVisualA11yEvidenceArtifact(
        schema_version=FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION,
        provenance=FrontendVisualA11yEvidenceProvenance(
            provider_kind=_require_non_empty_text(provider_kind, "provider_kind"),
            provider_name=_require_non_empty_text(provider_name, "provider_name"),
            provider_version=_optional_text(provider_version, "provider_version"),
            source_ref=_optional_text(source_ref, "source_ref"),
        ),
        freshness=FrontendVisualA11yEvidenceFreshness(
            generated_at=_require_non_empty_text(generated_at, "generated_at"),
            source_digest=_optional_text(source_digest, "source_digest"),
            source_revision=_optional_text(source_revision, "source_revision"),
        ),
        evaluations=tuple(_coerce_evaluations(evaluations)),
    )


def write_frontend_visual_a11y_evidence_artifact(
    spec_dir: Path,
    artifact: FrontendVisualA11yEvidenceArtifact,
) -> Path:
    """Write one canonical visual / a11y evidence artifact into a spec directory."""

    path = visual_a11y_evidence_artifact_path(spec_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact.to_json_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_frontend_visual_a11y_evidence_artifact(
    path: Path,
) -> FrontendVisualA11yEvidenceArtifact:
    """Load and validate one canonical visual / a11y evidence artifact file."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON ({exc.msg})") from exc

    if not isinstance(raw, dict):
        raise ValueError("expected top-level visual / a11y evidence artifact object")

    schema_version = _require_mapping_text(raw, "schema_version", context="artifact")
    if schema_version != FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION:
        raise ValueError(
            "unsupported schema_version "
            f"{schema_version!r}; expected {FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION!r}"
        )

    provenance_raw = _require_mapping(raw, "provenance", context="artifact")
    freshness_raw = _require_mapping(raw, "freshness", context="artifact")
    evaluations_raw = raw.get("evaluations")
    if not isinstance(evaluations_raw, list):
        raise ValueError("artifact.evaluations must be a list")

    evaluations: list[FrontendVisualA11yEvidenceEvaluation] = []
    for index, item in enumerate(evaluations_raw):
        if not isinstance(item, dict):
            raise ValueError(f"evaluations[{index}] must be an object")
        evaluations.append(_load_evaluation(item, index=index))

    return FrontendVisualA11yEvidenceArtifact(
        schema_version=schema_version,
        provenance=FrontendVisualA11yEvidenceProvenance(
            provider_kind=_require_mapping_text(
                provenance_raw,
                "provider_kind",
                context="provenance",
            ),
            provider_name=_require_mapping_text(
                provenance_raw,
                "provider_name",
                context="provenance",
            ),
            provider_version=_optional_mapping_text(
                provenance_raw,
                "provider_version",
                context="provenance",
            ),
            source_ref=_optional_mapping_text(
                provenance_raw,
                "source_ref",
                context="provenance",
            ),
        ),
        freshness=FrontendVisualA11yEvidenceFreshness(
            generated_at=_require_mapping_text(
                freshness_raw,
                "generated_at",
                context="freshness",
            ),
            source_digest=_optional_mapping_text(
                freshness_raw,
                "source_digest",
                context="freshness",
            ),
            source_revision=_optional_mapping_text(
                freshness_raw,
                "source_revision",
                context="freshness",
            ),
        ),
        evaluations=tuple(evaluations),
    )


def _load_evaluation(
    raw: dict[str, object],
    *,
    index: int,
) -> FrontendVisualA11yEvidenceEvaluation:
    outcome = _require_mapping_text(raw, "outcome", context=f"evaluations[{index}]")
    if outcome not in {"pass", "issue"}:
        raise ValueError(
            f"evaluations[{index}].outcome must be one of 'pass' or 'issue'"
        )

    report_type = _optional_mapping_text(
        raw,
        "report_type",
        context=f"evaluations[{index}]",
    )
    if outcome == "issue":
        if report_type is None:
            raise ValueError(
                f"evaluations[{index}].report_type must be a non-empty string for issue outcome"
            )
        if report_type not in FRONTEND_VISUAL_A11Y_REPORT_TYPES:
            raise ValueError(
                f"evaluations[{index}].report_type must be one of "
                f"{', '.join(FRONTEND_VISUAL_A11Y_REPORT_TYPES)}"
            )

    return FrontendVisualA11yEvidenceEvaluation(
        evaluation_id=_require_mapping_text(
            raw,
            "evaluation_id",
            context=f"evaluations[{index}]",
        ),
        target_id=_require_mapping_text(
            raw,
            "target_id",
            context=f"evaluations[{index}]",
        ),
        surface_id=_require_mapping_text(
            raw,
            "surface_id",
            context=f"evaluations[{index}]",
        ),
        outcome=outcome,
        report_type=report_type,
        severity=_optional_mapping_text(
            raw,
            "severity",
            context=f"evaluations[{index}]",
        ),
        location_anchor=_optional_mapping_text(
            raw,
            "location_anchor",
            context=f"evaluations[{index}]",
        ),
        quality_hint=_optional_mapping_text(
            raw,
            "quality_hint",
            context=f"evaluations[{index}]",
        ),
        changed_scope_explanation=_optional_mapping_text(
            raw,
            "changed_scope_explanation",
            context=f"evaluations[{index}]",
        ),
    )


def _coerce_evaluations(
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
) -> list[FrontendVisualA11yEvidenceEvaluation]:
    items: list[FrontendVisualA11yEvidenceEvaluation] = []
    for index, evaluation in enumerate(evaluations):
        if not isinstance(evaluation, FrontendVisualA11yEvidenceEvaluation):
            raise ValueError(
                "evaluations must contain FrontendVisualA11yEvidenceEvaluation items; "
                f"item {index} was {type(evaluation).__name__}"
            )
        items.append(evaluation)
    return items


def _require_mapping(
    value: dict[str, object],
    field_name: str,
    *,
    context: str,
) -> dict[str, object]:
    nested = value.get(field_name)
    if not isinstance(nested, dict):
        raise ValueError(f"{context}.{field_name} must be an object")
    return nested


def _require_mapping_text(
    value: dict[str, object],
    field_name: str,
    *,
    context: str,
) -> str:
    return _require_non_empty_text(value.get(field_name), f"{context}.{field_name}")


def _optional_mapping_text(
    value: dict[str, object],
    field_name: str,
    *,
    context: str,
) -> str | None:
    return _optional_text(value.get(field_name), f"{context}.{field_name}")


def _require_non_empty_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string when provided")
    text = value.strip()
    return text or None


__all__ = [
    "FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME",
    "FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION",
    "FRONTEND_VISUAL_A11Y_REPORT_TYPES",
    "FrontendVisualA11yEvidenceArtifact",
    "FrontendVisualA11yEvidenceEvaluation",
    "FrontendVisualA11yEvidenceFreshness",
    "FrontendVisualA11yEvidenceProvenance",
    "build_frontend_visual_a11y_evidence_artifact",
    "load_frontend_visual_a11y_evidence_artifact",
    "visual_a11y_evidence_artifact_path",
    "write_frontend_visual_a11y_evidence_artifact",
]
