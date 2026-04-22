"""Read-only provenance observer enrichments for Phase 1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.telemetry.contracts import ScopeLevel
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceGapFinding,
)
from ai_sdlc.telemetry.provenance_resolver import ProvenanceResolver
from ai_sdlc.telemetry.provenance_store import ProvenanceStore
from ai_sdlc.telemetry.store import TelemetryStore


@dataclass(frozen=True, slots=True)
class ProvenanceObserverResult:
    """Read-only provenance enrichments for one scope replay."""

    assessments: tuple[ProvenanceAssessment, ...] = ()
    gaps: tuple[ProvenanceGapFinding, ...] = ()
    overrides_default_blocker: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "assessments",
            tuple(_dedupe_provenance_models(self.assessments)),
        )
        object.__setattr__(
            self,
            "gaps",
            tuple(_dedupe_provenance_models(self.gaps)),
        )


def observe_provenance_step(
    store: TelemetryStore,
    *,
    goal_session_id: str,
    workflow_run_id: str,
    step_id: str,
) -> ProvenanceObserverResult:
    """Replay one step scope into provenance assessments and gaps."""
    provenance_store = ProvenanceStore(store)
    resolver = ProvenanceResolver(store)
    node_path = provenance_store.node_stream_path(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=workflow_run_id,
        step_id=step_id,
    )
    return _observe_step_with_scope_path(
        store,
        resolver,
        node_path.parent,
    )


def _observe_step_with_scope_path(
    store: TelemetryStore,
    resolver: ProvenanceResolver,
    scope_root: Path,
) -> ProvenanceObserverResult:
    nodes_path = scope_root / "nodes.ndjson"
    if not nodes_path.exists():
        return ProvenanceObserverResult()

    assessments: list[ProvenanceAssessment] = []
    derived_gaps: list[ProvenanceGapFinding] = []
    for payload in _dedupe_ndjson_payloads(store._read_ndjson(nodes_path)):
        subject_ref = f"provenance_node:{payload['node_id']}"
        report = resolver.resolve_subject(subject_ref)
        if report.assessment is not None:
            assessments.append(report.assessment)
        derived_gaps.extend(report.gaps)

    explicit_gaps: list[ProvenanceGapFinding] = []
    gap_dir = scope_root / "gaps"
    if gap_dir.exists():
        seen_gaps: set[str] = set()
        for path in sorted(gap_dir.glob("*.json")):
            gap = ProvenanceGapFinding.model_validate(store._read_json(path))
            marker = json.dumps(gap.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
            if marker in seen_gaps:
                continue
            seen_gaps.add(marker)
            explicit_gaps.append(gap)

    gap_map = {gap.gap_id: gap for gap in explicit_gaps}
    for gap in derived_gaps:
        gap_map.setdefault(gap.gap_id, gap)
    assessment_map = {assessment.subject_ref: assessment for assessment in assessments}
    return ProvenanceObserverResult(
        assessments=tuple(
            sorted(assessment_map.values(), key=lambda item: item.subject_ref)
        ),
        gaps=tuple(gap_map.values()),
        overrides_default_blocker=False,
    )


def _dedupe_ndjson_payloads(payloads: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[str] = set()
    for payload in payloads:
        marker = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(payload)
    return deduped


def _dedupe_provenance_models(values: object) -> list[object]:
    deduped: list[object] = []
    seen: set[str] = set()
    for value in values or ():
        if not hasattr(value, "model_dump"):
            continue
        marker = json.dumps(
            value.model_dump(mode="json"),
            sort_keys=True,
            ensure_ascii=False,
        )
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(value)
    return deduped
