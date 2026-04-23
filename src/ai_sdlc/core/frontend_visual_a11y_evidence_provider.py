"""Frontend visual / a11y evidence provider artifact helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

FRONTEND_VISUAL_A11Y_EVIDENCE_ARTIFACT_NAME = "frontend-visual-a11y-evidence.json"
FRONTEND_VISUAL_A11Y_EVIDENCE_SCHEMA_VERSION = "frontend-visual-a11y-evidence/v1"
AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_KIND = "browser_gate_auto"
AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_NAME = "browser_gate_auto_heuristic_v1"
FRONTEND_VISUAL_A11Y_REPORT_TYPES = (
    "violation-report",
    "coverage-report",
    "drift-report",
    "legacy-expansion-report",
)


def _dedupe_mapping_items(values: object) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, dict):
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return deduped


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

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evaluations",
            tuple(_dedupe_evaluation_items(self.evaluations)),
        )

    def to_json_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "provenance": _dedupe_mapping_items(
                [
                    {
                        "provider_kind": self.provenance.provider_kind,
                        "provider_name": self.provenance.provider_name,
                        "provider_version": self.provenance.provider_version,
                        "source_ref": self.provenance.source_ref,
                    }
                ]
            )[0],
            "freshness": _dedupe_mapping_items(
                [
                    {
                        "generated_at": self.freshness.generated_at,
                        "source_digest": self.freshness.source_digest,
                        "source_revision": self.freshness.source_revision,
                    }
                ]
            )[0],
            "evaluations": _dedupe_mapping_items(
                [evaluation.to_json_dict() for evaluation in self.evaluations]
            ),
        }


def _dedupe_evaluation_items(
    values: object,
) -> list[FrontendVisualA11yEvidenceEvaluation]:
    deduped: list[FrontendVisualA11yEvidenceEvaluation] = []
    seen: set[str] = set()
    for value in values or []:
        if not isinstance(value, FrontendVisualA11yEvidenceEvaluation):
            continue
        key = json.dumps(value.to_json_dict(), sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


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


def build_auto_frontend_visual_a11y_evidence_artifact(
    *,
    target_id: str,
    surface_id: str,
    generated_at: str,
    screenshot_ref: str,
    final_url: str,
    page_title: str,
    body_text_char_count: int,
    heading_count: int,
    landmark_count: int,
    interactive_count: int,
    unlabeled_button_count: int,
    unlabeled_input_count: int,
    image_missing_alt_count: int,
    viewport_width: int | None = None,
    viewport_height: int | None = None,
    document_scroll_width: int | None = None,
    document_scroll_height: int | None = None,
    horizontal_overflow_count: int | None = None,
    low_contrast_text_count: int | None = None,
    focusable_count: int | None = None,
    focusable_without_visible_focus_count: int | None = None,
    console_error_messages: list[str] | tuple[str, ...] = (),
    page_error_messages: list[str] | tuple[str, ...] = (),
) -> FrontendVisualA11yEvidenceArtifact:
    """Build one auto-derived visual / a11y evidence artifact from browser gate capture."""

    target = _require_non_empty_text(target_id, "target_id")
    surface = _require_non_empty_text(surface_id, "surface_id")
    screenshot = _optional_text(screenshot_ref, "screenshot_ref") or ""
    url = _optional_text(final_url, "final_url") or ""
    title = _optional_text(page_title, "page_title") or ""

    normalized_console_errors = _dedupe_text_items(console_error_messages)
    normalized_page_errors = _dedupe_text_items(page_error_messages)

    evaluations: list[FrontendVisualA11yEvidenceEvaluation] = []
    shared_scope_note = "derived from browser gate auto heuristic provider"
    if screenshot and body_text_char_count > 0 and title:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-visual-coverage-screenshot",
                target_id=target,
                surface_id=surface,
                location_anchor=screenshot or url,
                quality_hint="captured a populated browser entry screenshot",
                changed_scope_explanation=shared_scope_note,
            )
        )
    else:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-visual-coverage-screenshot",
                target_id=target,
                surface_id=surface,
                report_type="coverage-report",
                severity="high",
                location_anchor=screenshot or url,
                quality_hint=(
                    "browser entry did not expose a stable screenshot, readable text, "
                    "or page title during auto verification"
                ),
                changed_scope_explanation=shared_scope_note,
            )
        )

    if heading_count > 0:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-visual-structure-heading",
                target_id=target,
                surface_id=surface,
                location_anchor=screenshot or url,
                quality_hint=f"detected {heading_count} heading anchors",
                changed_scope_explanation=shared_scope_note,
            )
        )
    else:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-visual-structure-heading",
                target_id=target,
                surface_id=surface,
                report_type="coverage-report",
                severity="medium",
                location_anchor=screenshot or url,
                quality_hint="page should expose at least one heading landmark",
                changed_scope_explanation=shared_scope_note,
            )
        )

    if landmark_count > 0:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-a11y-landmarks",
                target_id=target,
                surface_id=surface,
                location_anchor=screenshot or url,
                quality_hint=f"detected {landmark_count} semantic landmark regions",
                changed_scope_explanation=shared_scope_note,
            )
        )
    else:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-a11y-landmarks",
                target_id=target,
                surface_id=surface,
                report_type="coverage-report",
                severity="medium",
                location_anchor=screenshot or url,
                quality_hint="page should expose semantic landmark regions such as main or header",
                changed_scope_explanation=shared_scope_note,
            )
        )

    if interactive_count > 0 and unlabeled_button_count == 0:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-a11y-button-labels",
                target_id=target,
                surface_id=surface,
                location_anchor=screenshot or url,
                quality_hint="button-like controls expose accessible labels",
                changed_scope_explanation=shared_scope_note,
            )
        )
    elif unlabeled_button_count > 0:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-a11y-button-labels",
                target_id=target,
                surface_id=surface,
                report_type="violation-report",
                severity="high",
                location_anchor=screenshot or url,
                quality_hint=(
                    f"detected {unlabeled_button_count} button-like controls without "
                    "accessible labels"
                ),
                changed_scope_explanation=shared_scope_note,
            )
        )

    if interactive_count > 0 and unlabeled_input_count == 0:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-a11y-input-labels",
                target_id=target,
                surface_id=surface,
                location_anchor=screenshot or url,
                quality_hint="form controls expose labels or ARIA names",
                changed_scope_explanation=shared_scope_note,
            )
        )
    elif unlabeled_input_count > 0:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-a11y-input-labels",
                target_id=target,
                surface_id=surface,
                report_type="violation-report",
                severity="high",
                location_anchor=screenshot or url,
                quality_hint=(
                    f"detected {unlabeled_input_count} form controls without labels"
                ),
                changed_scope_explanation=shared_scope_note,
            )
        )

    if image_missing_alt_count == 0:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-a11y-image-alt",
                target_id=target,
                surface_id=surface,
                location_anchor=screenshot or url,
                quality_hint="images with alternate text coverage are clear",
                changed_scope_explanation=shared_scope_note,
            )
        )
    else:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-a11y-image-alt",
                target_id=target,
                surface_id=surface,
                report_type="violation-report",
                severity="medium",
                location_anchor=screenshot or url,
                quality_hint=(
                    f"detected {image_missing_alt_count} images missing alternate text"
                ),
                changed_scope_explanation=shared_scope_note,
            )
        )

    if low_contrast_text_count is not None:
        if int(low_contrast_text_count) == 0:
            evaluations.append(
                _auto_pass_evaluation(
                    evaluation_id="auto-visual-text-contrast",
                    target_id=target,
                    surface_id=surface,
                    location_anchor=screenshot or url,
                    quality_hint="sampled visible text meets contrast thresholds",
                    changed_scope_explanation=shared_scope_note,
                )
            )
        else:
            evaluations.append(
                _auto_issue_evaluation(
                    evaluation_id="auto-visual-text-contrast",
                    target_id=target,
                    surface_id=surface,
                    report_type="violation-report",
                    severity="medium",
                    location_anchor=screenshot or url,
                    quality_hint=(
                        f"detected {int(low_contrast_text_count)} low-contrast text "
                        "sample(s) during browser verification"
                    ),
                    changed_scope_explanation=shared_scope_note,
                )
            )

    layout_metrics_present = all(
        value is not None
        for value in (
            viewport_width,
            viewport_height,
            document_scroll_width,
            document_scroll_height,
            horizontal_overflow_count,
        )
    )
    if layout_metrics_present:
        viewport_w = int(viewport_width or 0)
        viewport_h = int(viewport_height or 0)
        scroll_w = int(document_scroll_width or 0)
        scroll_h = int(document_scroll_height or 0)
        overflow_count = int(horizontal_overflow_count or 0)
        if overflow_count == 0 and scroll_w <= viewport_w + 2:
            evaluations.append(
                _auto_pass_evaluation(
                    evaluation_id="auto-visual-layout-fit",
                    target_id=target,
                    surface_id=surface,
                    location_anchor=screenshot or url,
                    quality_hint=(
                        "page layout fits the viewport without horizontal overflow"
                    ),
                    changed_scope_explanation=shared_scope_note,
                )
            )
        else:
            overflow_px = max(0, scroll_w - viewport_w)
            evaluations.append(
                _auto_issue_evaluation(
                    evaluation_id="auto-visual-layout-fit",
                    target_id=target,
                    surface_id=surface,
                    report_type="violation-report",
                    severity="high",
                    location_anchor=screenshot or url,
                    quality_hint=(
                        "page layout exceeds the viewport horizontally by "
                        f"{overflow_px}px; observed {overflow_count} overflowing "
                        f"element(s) within a {viewport_w}x{viewport_h} viewport and "
                        f"{scroll_w}x{scroll_h} document bounds"
                    ),
                    changed_scope_explanation=shared_scope_note,
                )
            )

    if (
        focusable_count is not None
        and focusable_without_visible_focus_count is not None
        and int(focusable_count) > 0
    ):
        focusable_total = int(focusable_count)
        focusable_missing = int(focusable_without_visible_focus_count)
        if focusable_missing == 0:
            evaluations.append(
                _auto_pass_evaluation(
                    evaluation_id="auto-a11y-focus-visible",
                    target_id=target,
                    surface_id=surface,
                    location_anchor=screenshot or url,
                    quality_hint="focusable controls expose visible focus indicators",
                    changed_scope_explanation=shared_scope_note,
                )
            )
        else:
            evaluations.append(
                _auto_issue_evaluation(
                    evaluation_id="auto-a11y-focus-visible",
                    target_id=target,
                    surface_id=surface,
                    report_type="violation-report",
                    severity="medium",
                    location_anchor=screenshot or url,
                    quality_hint=(
                        f"detected {focusable_missing} of {focusable_total} focusable "
                        "control(s) without a visible keyboard focus indicator"
                    ),
                    changed_scope_explanation=shared_scope_note,
                )
            )

    runtime_error_count = len(normalized_console_errors) + len(normalized_page_errors)
    if runtime_error_count == 0:
        evaluations.append(
            _auto_pass_evaluation(
                evaluation_id="auto-runtime-console-errors",
                target_id=target,
                surface_id=surface,
                location_anchor=url or screenshot,
                quality_hint="no browser console or page errors were captured",
                changed_scope_explanation=shared_scope_note,
            )
        )
    else:
        evaluations.append(
            _auto_issue_evaluation(
                evaluation_id="auto-runtime-console-errors",
                target_id=target,
                surface_id=surface,
                report_type="violation-report",
                severity="high",
                location_anchor=url or screenshot,
                quality_hint=(
                    "browser runtime surfaced errors: "
                    + "; ".join([*normalized_console_errors, *normalized_page_errors][:3])
                ),
                changed_scope_explanation=shared_scope_note,
            )
        )

    source_signature = json.dumps(
        {
            "target_id": target,
            "surface_id": surface,
            "screenshot_ref": screenshot,
            "final_url": url,
            "page_title": title,
            "body_text_char_count": int(body_text_char_count),
            "heading_count": int(heading_count),
            "landmark_count": int(landmark_count),
            "interactive_count": int(interactive_count),
            "unlabeled_button_count": int(unlabeled_button_count),
            "unlabeled_input_count": int(unlabeled_input_count),
            "image_missing_alt_count": int(image_missing_alt_count),
            "viewport_width": None if viewport_width is None else int(viewport_width),
            "viewport_height": None if viewport_height is None else int(viewport_height),
            "document_scroll_width": (
                None if document_scroll_width is None else int(document_scroll_width)
            ),
            "document_scroll_height": (
                None if document_scroll_height is None else int(document_scroll_height)
            ),
            "horizontal_overflow_count": (
                None if horizontal_overflow_count is None else int(horizontal_overflow_count)
            ),
            "low_contrast_text_count": (
                None if low_contrast_text_count is None else int(low_contrast_text_count)
            ),
            "focusable_count": None if focusable_count is None else int(focusable_count),
            "focusable_without_visible_focus_count": (
                None
                if focusable_without_visible_focus_count is None
                else int(focusable_without_visible_focus_count)
            ),
            "console_error_messages": normalized_console_errors,
            "page_error_messages": normalized_page_errors,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    source_digest = "sha256:" + hashlib.sha256(
        source_signature.encode("utf-8")
    ).hexdigest()
    return build_frontend_visual_a11y_evidence_artifact(
        evaluations=evaluations,
        provider_kind=AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_KIND,
        provider_name=AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_NAME,
        generated_at=generated_at,
        source_ref=screenshot or url or surface,
        source_digest=source_digest,
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
        evaluations=tuple(_coerce_evaluations(evaluations)),
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
    seen: set[str] = set()
    for index, evaluation in enumerate(evaluations):
        if not isinstance(evaluation, FrontendVisualA11yEvidenceEvaluation):
            raise ValueError(
                "evaluations must contain FrontendVisualA11yEvidenceEvaluation items; "
                f"item {index} was {type(evaluation).__name__}"
            )
        key = json.dumps(
            evaluation.to_json_dict(),
            sort_keys=True,
            ensure_ascii=False,
        )
        if key in seen:
            continue
        seen.add(key)
        items.append(evaluation)
    return items


def _auto_pass_evaluation(
    *,
    evaluation_id: str,
    target_id: str,
    surface_id: str,
    location_anchor: str,
    quality_hint: str,
    changed_scope_explanation: str,
) -> FrontendVisualA11yEvidenceEvaluation:
    return FrontendVisualA11yEvidenceEvaluation(
        evaluation_id=evaluation_id,
        target_id=target_id,
        surface_id=surface_id,
        outcome="pass",
        report_type="coverage-report",
        severity="info",
        location_anchor=location_anchor or None,
        quality_hint=quality_hint,
        changed_scope_explanation=changed_scope_explanation,
    )


def _auto_issue_evaluation(
    *,
    evaluation_id: str,
    target_id: str,
    surface_id: str,
    report_type: str,
    severity: str,
    location_anchor: str,
    quality_hint: str,
    changed_scope_explanation: str,
) -> FrontendVisualA11yEvidenceEvaluation:
    return FrontendVisualA11yEvidenceEvaluation(
        evaluation_id=evaluation_id,
        target_id=target_id,
        surface_id=surface_id,
        outcome="issue",
        report_type=report_type,
        severity=severity,
        location_anchor=location_anchor or None,
        quality_hint=quality_hint,
        changed_scope_explanation=changed_scope_explanation,
    )


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


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
    "AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_KIND",
    "AUTO_FRONTEND_VISUAL_A11Y_PROVIDER_NAME",
    "FRONTEND_VISUAL_A11Y_REPORT_TYPES",
    "FrontendVisualA11yEvidenceArtifact",
    "FrontendVisualA11yEvidenceEvaluation",
    "FrontendVisualA11yEvidenceFreshness",
    "FrontendVisualA11yEvidenceProvenance",
    "build_auto_frontend_visual_a11y_evidence_artifact",
    "build_frontend_visual_a11y_evidence_artifact",
    "load_frontend_visual_a11y_evidence_artifact",
    "visual_a11y_evidence_artifact_path",
    "write_frontend_visual_a11y_evidence_artifact",
]
