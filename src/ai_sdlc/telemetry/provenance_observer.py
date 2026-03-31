"""Read-only provenance observer enrichments for Phase 1."""

from __future__ import annotations

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
    for payload in store._read_ndjson(nodes_path):
        subject_ref = f"provenance_node:{payload['node_id']}"
        report = resolver.resolve_subject(subject_ref)
        if report.assessment is not None:
            assessments.append(report.assessment)
        derived_gaps.extend(report.gaps)

    explicit_gaps: list[ProvenanceGapFinding] = []
    gap_dir = scope_root / "gaps"
    if gap_dir.exists():
        for path in sorted(gap_dir.glob("*.json")):
            explicit_gaps.append(ProvenanceGapFinding.model_validate(store._read_json(path)))

    gap_map = {gap.gap_id: gap for gap in explicit_gaps}
    for gap in derived_gaps:
        gap_map.setdefault(gap.gap_id, gap)
    return ProvenanceObserverResult(
        assessments=tuple(sorted(assessments, key=lambda item: item.subject_ref)),
        gaps=tuple(gap_map.values()),
        overrides_default_blocker=False,
    )
