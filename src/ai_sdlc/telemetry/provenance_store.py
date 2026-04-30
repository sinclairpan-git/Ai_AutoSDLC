"""Filesystem-backed provenance persistence helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai_sdlc.telemetry.enums import ScopeLevel
from ai_sdlc.telemetry.paths import provenance_root, telemetry_id_file_name
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceEdgeFact,
    ProvenanceGapFinding,
    ProvenanceGovernanceHook,
    ProvenanceNodeFact,
)
from ai_sdlc.telemetry.store import TelemetryStore

_APPEND_ONLY_FILE_BY_KIND = {
    "provenance_node": "nodes.ndjson",
    "provenance_edge": "edges.ndjson",
}
_APPEND_ONLY_ID_FIELD_BY_KIND = {
    "provenance_node": "node_id",
    "provenance_edge": "edge_id",
}
_MUTABLE_DIR_BY_KIND = {
    "provenance_assessment": "assessments",
    "provenance_gap": "gaps",
    "provenance_hook": "hooks",
}
_COMPACT_MUTABLE_DIR_BY_KIND = {
    "provenance_assessment": "a",
    "provenance_gap": "g",
    "provenance_hook": "h",
}


class ProvenanceStore:
    """Canonical path and lookup helpers for provenance objects."""

    def __init__(self, telemetry_store: TelemetryStore) -> None:
        self.telemetry_store = telemetry_store

    def node_stream_path(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        return self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        ) / _APPEND_ONLY_FILE_BY_KIND["provenance_node"]

    def edge_stream_path(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        return self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        ) / _APPEND_ONLY_FILE_BY_KIND["provenance_edge"]

    def current_object_path(
        self,
        kind: str,
        *,
        object_id: str,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        root = self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        directory = self._mutable_directory(kind, compact=root.name == "p")
        return (
            root
            / directory
            / telemetry_id_file_name(object_id)
        )

    def revisions_path(
        self,
        kind: str,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        root = self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        directory = self._mutable_directory(kind, compact=root.name == "p")
        return (
            root
            / f"{directory}.revisions.ndjson"
        )

    def append_fact(
        self,
        kind: str,
        record: ProvenanceNodeFact | ProvenanceEdgeFact,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        stream_path = self._append_only_stream_path(
            kind,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        self.telemetry_store.register_scope(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        self.telemetry_store._append_ndjson(stream_path, record.model_dump(mode="json"))
        return stream_path

    def write_mutable(
        self,
        kind: str,
        record: ProvenanceAssessment | ProvenanceGapFinding | ProvenanceGovernanceHook,
        *,
        object_id: str,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        snapshot_path = self.current_object_path(
            kind,
            object_id=object_id,
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        self.telemetry_store.register_scope(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        payload = record.model_dump(mode="json")
        if snapshot_path.exists():
            self.telemetry_store._append_ndjson(
                self.revisions_path(
                    kind,
                    scope_level=scope_level,
                    goal_session_id=goal_session_id,
                    workflow_run_id=workflow_run_id,
                    step_id=step_id,
                ),
                payload,
            )
        self.telemetry_store._write_json(snapshot_path, payload)
        return snapshot_path

    def find_append_only_matches(
        self, kind: str, source_ref: str
    ) -> list[tuple[Path, dict[str, Any]]]:
        file_name = _APPEND_ONLY_FILE_BY_KIND[kind]
        id_field = _APPEND_ONLY_ID_FIELD_BY_KIND[kind]
        matches: list[tuple[Path, dict[str, Any]]] = []
        paths = list(self.telemetry_store.local_root.rglob(f"provenance/{file_name}"))
        paths.extend(self.telemetry_store.local_root.rglob(f"p/{file_name}"))
        for path in sorted(paths):
            for payload in self.telemetry_store._read_ndjson(path):
                if payload.get(id_field) == source_ref:
                    matches.append((path, payload))
        return _dedupe_append_only_matches(matches)

    def find_current_object_path(self, kind: str, source_ref: str) -> Path | None:
        directory = self._mutable_directory(kind)
        compact_directory = self._mutable_directory(kind, compact=True)
        file_name = telemetry_id_file_name(source_ref)
        matches = list(
            self.telemetry_store.local_root.rglob(
                f"provenance/{directory}/{file_name}"
            )
        )
        matches.extend(
            self.telemetry_store.local_root.rglob(f"p/{compact_directory}/{file_name}")
        )
        if not matches and file_name != f"{source_ref}.json":
            matches = list(
                self.telemetry_store.local_root.rglob(
                    f"provenance/{directory}/{source_ref}.json"
                )
            )
            matches.extend(
                self.telemetry_store.local_root.rglob(
                    f"p/{compact_directory}/{source_ref}.json"
                )
            )
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(
                f"duplicate provenance object snapshots for {kind}:{source_ref}"
            )
        return matches[0]

    def next_ingestion_order(self, goal_session_id: str) -> int:
        highest = 0
        for kind in _APPEND_ONLY_FILE_BY_KIND:
            for path, payload in self.iter_append_only_payloads(kind):
                _, session_id, _, _ = self.telemetry_store.scope_chain_from_path(path)
                if session_id != goal_session_id:
                    continue
                highest = max(highest, int(payload["ingestion_order"]))
        return highest + 1

    def iter_append_only_payloads(
        self, kind: str
    ) -> list[tuple[Path, dict[str, Any]]]:
        file_name = _APPEND_ONLY_FILE_BY_KIND[kind]
        payloads: list[tuple[Path, dict[str, Any]]] = []
        paths = list(self.telemetry_store.local_root.rglob(f"provenance/{file_name}"))
        paths.extend(self.telemetry_store.local_root.rglob(f"p/{file_name}"))
        for path in sorted(paths):
            for payload in self.telemetry_store._read_ndjson(path):
                payloads.append((path, payload))
        return _dedupe_append_only_matches(payloads)

    def _append_only_stream_path(
        self,
        kind: str,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        if kind == "provenance_node":
            return self.node_stream_path(
                scope_level=scope_level,
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
                step_id=step_id,
            )
        if kind == "provenance_edge":
            return self.edge_stream_path(
                scope_level=scope_level,
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
                step_id=step_id,
            )
        raise ValueError(f"unsupported append-only provenance kind: {kind!r}")

    def _scope_root(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        return provenance_root(
            self.telemetry_store._scope_root(
                scope_level=scope_level,
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id,
                step_id=step_id,
            )
        )

    def _mutable_directory(self, kind: str, *, compact: bool = False) -> str:
        try:
            if compact:
                return _COMPACT_MUTABLE_DIR_BY_KIND[kind]
            return _MUTABLE_DIR_BY_KIND[kind]
        except KeyError as exc:  # pragma: no cover - caller-owned surface
            raise ValueError(f"unsupported mutable provenance kind: {kind!r}") from exc


def _dedupe_append_only_matches(
    items: list[tuple[Path, dict[str, Any]]],
) -> list[tuple[Path, dict[str, Any]]]:
    deduped: list[tuple[Path, dict[str, Any]]] = []
    seen: set[tuple[str, str]] = set()
    for path, payload in items:
        key = (
            str(path),
            json.dumps(payload, sort_keys=True, ensure_ascii=False),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append((path, payload))
    return deduped
