"""Canonical source resolver for telemetry objects and evidence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ai_sdlc.telemetry.ids import ID_PREFIXES, validate_telemetry_id
from ai_sdlc.telemetry.store import TelemetryStore

_SOURCE_KIND_PREFIX = {
    "telemetry_event": ID_PREFIXES["event_id"],
    "event": ID_PREFIXES["event_id"],
    "evidence": ID_PREFIXES["evidence_id"],
    "evaluation": ID_PREFIXES["evaluation_id"],
    "violation": ID_PREFIXES["violation_id"],
    "artifact": ID_PREFIXES["artifact_id"],
}


@dataclass(frozen=True)
class ResolvedSource:
    """Resolved source reference metadata."""

    kind: str
    source_ref: str
    path: Path
    payload: dict[str, Any]


class SourceResolver:
    """Resolve canonical telemetry source references."""

    def __init__(self, store: TelemetryStore) -> None:
        self.store = store

    def resolve(self, source_kind: str, source_ref: str) -> ResolvedSource:
        """Resolve a source reference to the on-disk telemetry payload."""
        if source_kind not in _SOURCE_KIND_PREFIX:
            raise ValueError(f"unsupported source_kind: {source_kind!r}")
        validate_telemetry_id(source_ref, _SOURCE_KIND_PREFIX[source_kind])

        canonical_kind = "telemetry_event" if source_kind == "event" else source_kind
        if canonical_kind in {"evaluation", "violation", "artifact"}:
            path = self.store.find_current_object_path(canonical_kind, source_ref)
            if path is None:
                raise LookupError(f"unable to resolve {source_kind}:{source_ref}")
            return ResolvedSource(
                kind=canonical_kind,
                source_ref=source_ref,
                path=path,
                payload=self.store._read_json(path),
            )

        resolved = self.store.find_append_only_payload(canonical_kind, source_ref)
        if resolved is None:
            raise LookupError(f"unable to resolve {source_kind}:{source_ref}")
        path, payload = resolved
        return ResolvedSource(
            kind=canonical_kind,
            source_ref=source_ref,
            path=path,
            payload=payload,
        )
