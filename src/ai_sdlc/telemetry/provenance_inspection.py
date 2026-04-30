"""Read-only provenance inspection views for Phase 1."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ai_sdlc.telemetry.enums import ProvenanceChainStatus, ProvenanceNodeKind
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceGapFinding,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.provenance_resolver import ProvenanceResolver
from ai_sdlc.telemetry.provenance_store import ProvenanceStore
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore

_NODE_KIND_ORDER = {
    ProvenanceNodeKind.CONVERSATION_MESSAGE.value: 0,
    ProvenanceNodeKind.SKILL_INVOCATION.value: 1,
    ProvenanceNodeKind.EXEC_COMMAND_BRIDGE.value: 2,
    ProvenanceNodeKind.RULE_REFERENCE.value: 3,
    ProvenanceNodeKind.TRIGGER_POINT.value: 4,
}


def _dedupe_text_items(values: object) -> tuple[str, ...]:
    deduped: list[str] = []
    for value in values or ():
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return tuple(deduped)


def _dedupe_model_items(values: object) -> tuple[object, ...]:
    deduped: list[object] = []
    seen: set[str] = set()
    for value in values or ():
        if not isinstance(value, BaseModel):
            continue
        key = value.__class__.__name__ + ":" + value.model_dump_json()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return tuple(deduped)


def _dedupe_mapping_items(values: object) -> tuple[dict[str, Any], ...]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for value in values or ():
        if not isinstance(value, dict):
            continue
        key = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(value))
    return tuple(deduped)


class ProvenanceChainModeView(BaseModel):
    """Stable machine-readable chain mode entry."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: str
    mode: str
    ref: str


class ProvenanceBlockingGapView(BaseModel):
    """Stable machine-readable blocking-gap summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    gap_ref: str
    gap_kind: str
    gap_location: str


class ProvenanceAssessmentView(BaseModel):
    """Stable machine-readable assessment summary section."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    overall_chain_status: str
    highest_confidence_source: str
    key_gaps: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("key_gaps", mode="after")
    @classmethod
    def _dedupe_key_gaps(cls, value: object) -> tuple[str, ...]:
        return _dedupe_text_items(value)


class ProvenanceInspectionView(BaseModel):
    """Stable read-only provenance inspection surface."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    subject_ref: str
    triggered_by: tuple[str, ...] = Field(default_factory=tuple)
    invoked: tuple[str, ...] = Field(default_factory=tuple)
    cited: tuple[str, ...] = Field(default_factory=tuple)
    chain_modes: tuple[ProvenanceChainModeView, ...] = Field(default_factory=tuple)
    blocking_gap: ProvenanceBlockingGapView | None = None
    assessment: ProvenanceAssessmentView
    failures: tuple[dict[str, Any], ...] = Field(default_factory=tuple)

    @field_validator("triggered_by", "invoked", "cited", mode="after")
    @classmethod
    def _dedupe_locator_refs(cls, value: object) -> tuple[str, ...]:
        return _dedupe_text_items(value)

    @field_validator("chain_modes", mode="after")
    @classmethod
    def _dedupe_chain_modes(cls, value: object) -> tuple[object, ...]:
        return _dedupe_model_items(value)

    @field_validator("failures", mode="after")
    @classmethod
    def _dedupe_failures(cls, value: object) -> tuple[dict[str, Any], ...]:
        return _dedupe_mapping_items(value)


def inspect_provenance_subject(
    store: TelemetryStore, subject_ref: str
) -> ProvenanceInspectionView:
    """Build the stable read-only provenance inspection view for one subject."""
    resolver = ProvenanceResolver(store)
    provenance_store = ProvenanceStore(store)
    report = resolver.resolve_subject(subject_ref)
    scope_root = _find_scope_root(provenance_store, subject_ref)
    nodes = _load_scope_nodes(store, scope_root)
    explicit_gaps = _load_scope_gaps(store, scope_root)

    triggered_by = _collect_locators(nodes, store, {ProvenanceNodeKind.CONVERSATION_MESSAGE})
    invoked = _collect_locators(
        nodes,
        store,
        {
            ProvenanceNodeKind.SKILL_INVOCATION,
            ProvenanceNodeKind.EXEC_COMMAND_BRIDGE,
        },
    )
    cited = _collect_locators(nodes, store, {ProvenanceNodeKind.RULE_REFERENCE})
    chain_modes = _build_chain_modes(nodes, explicit_gaps)
    blocking_gap = _select_blocking_gap(explicit_gaps, tuple(report.gaps))
    overall_chain_status = report.chain_status.value
    if explicit_gaps and report.chain_status is ProvenanceChainStatus.CLOSED:
        overall_chain_status = ProvenanceChainStatus.PARTIAL.value

    if report.assessment is None:
        highest_confidence_source = "unknown"
    else:
        highest_confidence_source = report.assessment.highest_confidence_source

    key_gaps = _key_gap_strings(explicit_gaps, tuple(report.gaps))
    return ProvenanceInspectionView(
        subject_ref=subject_ref,
        triggered_by=triggered_by,
        invoked=invoked,
        cited=cited,
        chain_modes=chain_modes,
        blocking_gap=blocking_gap,
        assessment=ProvenanceAssessmentView(
            overall_chain_status=overall_chain_status,
            highest_confidence_source=highest_confidence_source,
            key_gaps=key_gaps,
        ),
        failures=tuple(failure.model_dump(mode="json") for failure in report.failures),
    )


def render_provenance_summary(view: ProvenanceInspectionView) -> str:
    """Render the compact human-oriented provenance summary."""
    return "\n".join(
        [
            f"Subject: {view.subject_ref}",
            f"Triggered by: {_join_or_dash(view.triggered_by)}",
            f"Invoked: {_join_or_dash(view.invoked)}",
            f"Cited: {_join_or_dash(view.cited)}",
            f"Blocking gap: {_render_blocking_gap(view.blocking_gap)}",
        ]
    )


def render_provenance_explain(view: ProvenanceInspectionView) -> str:
    """Render the stable human-oriented provenance explanation view."""
    return "\n".join(
        [
            f"Subject: {view.subject_ref}",
            f"Overall chain status: {view.assessment.overall_chain_status}",
            f"Highest confidence source: {view.assessment.highest_confidence_source}",
            f"Key gaps: {_join_or_dash(view.assessment.key_gaps)}",
            f"Triggered by: {_join_or_dash(view.triggered_by)}",
            f"Invoked: {_join_or_dash(view.invoked)}",
            f"Cited: {_join_or_dash(view.cited)}",
        ]
    )


def render_provenance_gaps(view: ProvenanceInspectionView) -> str:
    """Render the stable human-oriented provenance gaps view."""
    if not view.assessment.key_gaps:
        return "No gaps."
    return "\n".join(view.assessment.key_gaps)


def _find_scope_root(
    provenance_store: ProvenanceStore, subject_ref: str
) -> Path | None:
    subject_kind, object_id = subject_ref.split(":", 1)
    kind = {
        "provenance_node": "provenance_node",
        "provenance_edge": "provenance_edge",
    }.get(subject_kind)
    if kind is None:
        return None
    matches = provenance_store.find_append_only_matches(kind, object_id)
    if not matches:
        return None
    path, _payload = matches[0]
    return path.parent


def _load_scope_nodes(store: TelemetryStore, scope_root: Path | None) -> tuple[ProvenanceNodeFact, ...]:
    if scope_root is None:
        return ()
    path = scope_root / "nodes.ndjson"
    if not path.exists():
        return ()
    nodes: list[ProvenanceNodeFact] = []
    seen: set[str] = set()
    for payload in store._read_ndjson(path):
        node = ProvenanceNodeFact.model_validate(payload)
        key = json.dumps(node.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        nodes.append(node)
    return tuple(nodes)


def _load_scope_gaps(
    store: TelemetryStore, scope_root: Path | None
) -> tuple[ProvenanceGapFinding, ...]:
    if scope_root is None:
        return ()
    gaps: list[ProvenanceGapFinding] = []
    seen: set[str] = set()
    for gap_dir in _scope_gap_dirs(scope_root):
        for path in sorted(gap_dir.glob("*.json")):
            gap = ProvenanceGapFinding.model_validate(store._read_json(path))
            key = json.dumps(gap.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            gaps.append(gap)
    return tuple(gaps)


def _scope_gap_dirs(scope_root: Path) -> tuple[Path, ...]:
    return tuple(path for path in (scope_root / "gaps", scope_root / "g") if path.exists())


def _collect_locators(
    nodes: tuple[ProvenanceNodeFact, ...],
    store: TelemetryStore,
    kinds: set[ProvenanceNodeKind],
) -> tuple[str, ...]:
    locators: list[str] = []
    resolver = SourceResolver(store)
    for node in nodes:
        if node.node_kind not in kinds:
            continue
        for evidence_ref in node.source_evidence_refs:
            try:
                payload = resolver.resolve("evidence", evidence_ref).payload
            except (LookupError, ValueError):
                continue
            locator = payload.get("locator")
            if isinstance(locator, str) and locator.startswith("prov://"):
                locators.append(locator)
    return tuple(dict.fromkeys(locators))


def _build_chain_modes(
    nodes: tuple[ProvenanceNodeFact, ...],
    explicit_gaps: tuple[ProvenanceGapFinding, ...],
) -> tuple[ProvenanceChainModeView, ...]:
    node_entries = [
        ProvenanceChainModeView(
            kind=node.node_kind.value,
            mode=node.ingress_kind.value,
            ref=f"provenance_node:{node.node_id}",
        )
        for node in sorted(
            nodes,
            key=lambda item: (_NODE_KIND_ORDER.get(item.node_kind.value, 99), item.node_id),
        )
    ]
    gap_entries = [
        ProvenanceChainModeView(
            kind=gap.gap_location,
            mode=gap.gap_kind.value,
            ref=f"provenance_gap:{gap.gap_id}",
        )
        for gap in sorted(explicit_gaps, key=lambda item: (item.gap_location, item.gap_id))
    ]
    return tuple(node_entries + gap_entries)


def _select_blocking_gap(
    explicit_gaps: tuple[ProvenanceGapFinding, ...],
    resolver_gaps: tuple[ProvenanceGapFinding, ...],
) -> ProvenanceBlockingGapView | None:
    gap = explicit_gaps[0] if explicit_gaps else (resolver_gaps[0] if resolver_gaps else None)
    if gap is None:
        return None
    return ProvenanceBlockingGapView(
        gap_ref=f"provenance_gap:{gap.gap_id}",
        gap_kind=gap.gap_kind.value,
        gap_location=gap.gap_location,
    )


def _key_gap_strings(
    explicit_gaps: tuple[ProvenanceGapFinding, ...],
    resolver_gaps: tuple[ProvenanceGapFinding, ...],
) -> tuple[str, ...]:
    gaps = explicit_gaps or resolver_gaps
    return tuple(f"{gap.gap_kind.value} @ {gap.gap_location}" for gap in gaps)


def _join_or_dash(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "-"


def _render_blocking_gap(gap: ProvenanceBlockingGapView | None) -> str:
    if gap is None:
        return "-"
    return f"{gap.gap_kind} @ {gap.gap_location}"
