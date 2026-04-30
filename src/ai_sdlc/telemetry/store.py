"""Local filesystem-backed telemetry store for V1."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from ai_sdlc.telemetry.contracts import (
    Artifact,
    Evaluation,
    Evidence,
    ScopeLevel,
    TelemetryEvent,
    Violation,
)
from ai_sdlc.telemetry.enums import HardFailCategory
from ai_sdlc.telemetry.paths import (
    run_root,
    scope_id_from_dir_name,
    session_root,
    step_root,
    telemetry_id_file_name,
    telemetry_indexes_root,
    telemetry_local_root,
    telemetry_manifest_path,
    telemetry_reports_root,
)

_MUTABLE_KIND_DIRS = {
    "evaluation": "evaluations",
    "violation": "violations",
    "artifact": "artifacts",
}
_ID_FIELD_BY_KIND = {
    "evaluation": "evaluation_id",
    "violation": "violation_id",
    "artifact": "artifact_id",
    "telemetry_event": "event_id",
    "evidence": "evidence_id",
}


def _path_is_within(path: str, parent: str) -> bool:
    return path == parent or path.startswith(f"{parent.rstrip('/')}/")


def _choose_longer_scope_match(
    current: tuple[int, tuple[ScopeLevel, str, str | None, str | None]] | None,
    entry_path: str,
    candidate: tuple[ScopeLevel, str, str | None, str | None],
) -> tuple[int, tuple[ScopeLevel, str, str | None, str | None]]:
    length = len(entry_path)
    if current is None or length > current[0]:
        return (length, candidate)
    return current


class TelemetryStore:
    """Minimal local telemetry storage and rebuild helpers."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root)
        self.local_root = telemetry_local_root(self.repo_root)
        self.reports_root = telemetry_reports_root(self.repo_root)
        self.manifest_path = telemetry_manifest_path(self.repo_root)
        self.indexes_root = telemetry_indexes_root(self.repo_root)

    def ensure_initialized(self) -> dict[str, Any]:
        """Create the minimal telemetry root and manifest if needed."""
        self.local_root.mkdir(parents=True, exist_ok=True)
        if not self.manifest_path.exists():
            manifest = {
                "version": 1,
                "sessions": {},
                "runs": {},
                "steps": {},
            }
            self._write_json(self.manifest_path, manifest)
            return manifest
        return self._read_json(self.manifest_path)

    def load_manifest(self) -> dict[str, Any]:
        """Load the telemetry manifest."""
        if not self.manifest_path.exists():
            return self.ensure_initialized()
        return self._read_json(self.manifest_path)

    def classify_hard_fail(self, error: Exception) -> str | None:
        """Classify storage-layer integrity failures that should hard-fail by default."""
        if isinstance(error, OSError):
            return HardFailCategory.HARD_FAIL_DEFAULT.value
        if isinstance(error, ValueError) and "parent chain mismatch" in str(error):
            return HardFailCategory.HARD_FAIL_DEFAULT.value
        return None

    def event_stream_path(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        """Return the append-only event stream path for a scope."""
        return self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        ) / "events.ndjson"

    def evidence_stream_path(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        """Return the append-only evidence stream path for a scope."""
        return self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        ) / "evidence.ndjson"

    def current_object_path(self, record: Evaluation | Violation | Artifact) -> Path:
        """Return the current snapshot path for a mutable telemetry object."""
        kind = self._kind_for_record(record)
        id_field = _ID_FIELD_BY_KIND[kind]
        return (
            self._scope_root_for_record(record)
            / _MUTABLE_KIND_DIRS[kind]
            / telemetry_id_file_name(getattr(record, id_field))
        )

    def revisions_path(self, record: Evaluation | Violation | Artifact) -> Path:
        """Return the revisions path for a mutable telemetry object."""
        kind = self._kind_for_record(record)
        return self._scope_root_for_record(record) / f"{_MUTABLE_KIND_DIRS[kind]}.revisions.ndjson"

    def register_scope(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        """Register a scope in the manifest and reject parent-chain mismatches."""
        self._validate_scope_arguments(
            scope_level=scope_level,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        manifest = self.load_manifest()
        session_path = session_root(self.repo_root, goal_session_id)
        session_rel = session_path.relative_to(self.local_root).as_posix()
        session_entry = manifest["sessions"].get(goal_session_id)
        if session_entry is None:
            manifest["sessions"][goal_session_id] = {"path": session_rel}
        elif session_entry["path"] != session_rel:
            raise ValueError("parent chain mismatch for goal_session_id")

        if workflow_run_id is not None:
            run_path = run_root(self.repo_root, goal_session_id, workflow_run_id)
            run_rel = run_path.relative_to(self.local_root).as_posix()
            run_entry = manifest["runs"].get(workflow_run_id)
            if run_entry is None:
                manifest["runs"][workflow_run_id] = {
                    "goal_session_id": goal_session_id,
                    "path": run_rel,
                }
            elif run_entry["goal_session_id"] != goal_session_id or run_entry["path"] != run_rel:
                raise ValueError("parent chain mismatch for workflow_run_id")

        if step_id is not None:
            if workflow_run_id is None:
                raise ValueError("step scope requires workflow_run_id")
            step_path = step_root(self.repo_root, goal_session_id, workflow_run_id, step_id)
            step_rel = step_path.relative_to(self.local_root).as_posix()
            step_entry = manifest["steps"].get(step_id)
            if step_entry is None:
                manifest["steps"][step_id] = {
                    "goal_session_id": goal_session_id,
                    "workflow_run_id": workflow_run_id,
                    "path": step_rel,
                }
            elif (
                step_entry["goal_session_id"] != goal_session_id
                or step_entry["workflow_run_id"] != workflow_run_id
                or step_entry["path"] != step_rel
            ):
                raise ValueError("parent chain mismatch for step_id")

        self._write_json(self.manifest_path, manifest)
        root = self._scope_root(
            scope_level=scope_level,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        root.mkdir(parents=True, exist_ok=True)
        return root

    def delete_indexes(self) -> None:
        """Delete the telemetry indexes directory if it exists."""
        shutil.rmtree(self.indexes_root, ignore_errors=True)

    def rebuild_indexes(self) -> dict[str, Path]:
        """Rebuild the derived telemetry indexes from authoritative local traces."""
        self.ensure_initialized()
        self.indexes_root.mkdir(parents=True, exist_ok=True)
        index_payloads = self.derive_index_payloads()

        open_violations_path = self.indexes_root / "open-violations.json"
        latest_artifacts_path = self.indexes_root / "latest-artifacts.json"
        timeline_cursor_path = self.indexes_root / "timeline-cursor.json"

        self._write_json(open_violations_path, index_payloads["open_violations"])
        self._write_json(latest_artifacts_path, index_payloads["latest_artifacts"])
        self._write_json(timeline_cursor_path, index_payloads["timeline_cursor"])

        return {
            "open_violations_path": open_violations_path,
            "latest_artifacts_path": latest_artifacts_path,
            "timeline_cursor_path": timeline_cursor_path,
        }

    def derive_index_payloads(self) -> dict[str, dict[str, Any]]:
        """Return canonical index payloads without mutating the filesystem."""
        open_violation_ids = [
            payload["violation_id"]
            for payload in self._iter_mutable_snapshots("violation")
            if payload["status"] not in {"fixed", "dismissed"}
        ]
        latest_artifacts = sorted(
            self._iter_mutable_snapshots("artifact"),
            key=lambda payload: (payload["updated_at"], payload["artifact_id"]),
            reverse=True,
        )
        events = sorted(
            self._iter_event_payloads(),
            key=lambda payload: (payload["timestamp"], payload["event_id"]),
        )
        latest_scope_ids = self._latest_scope_ids()
        return {
            "open_violations": {"violation_ids": open_violation_ids},
            "latest_artifacts": {
                "artifact_ids": [payload["artifact_id"] for payload in latest_artifacts]
            },
            "timeline_cursor": {
                "event_count": len(events),
                "last_event_id": events[-1]["event_id"] if events else None,
                "last_timestamp": events[-1]["timestamp"] if events else None,
                "latest_goal_session_id": latest_scope_ids["latest_goal_session_id"],
                "latest_workflow_run_id": latest_scope_ids["latest_workflow_run_id"],
                "latest_step_id": latest_scope_ids["latest_step_id"],
            },
        }

    def governance_report_path(self, artifact_id: str) -> Path:
        """Return the canonical governance report path for an artifact."""
        return self.reports_root / f"{artifact_id}.json"

    def write_governance_report(self, artifact_id: str, payload: dict[str, Any]) -> Path:
        """Write a canonical governance report JSON payload."""
        report_path = self.governance_report_path(artifact_id)
        self._write_json(report_path, payload)
        return report_path

    def load_governance_report(self, artifact_id: str) -> dict[str, Any] | None:
        """Load a canonical governance report payload when available."""
        report_path = self.governance_report_path(artifact_id)
        if not report_path.exists():
            return None
        return self._read_json(report_path)

    def load_current_snapshots(
        self,
        kind: str,
        *,
        goal_session_id: str | None = None,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Load current snapshots filtered by an exact parent chain prefix."""
        if kind not in _MUTABLE_KIND_DIRS:
            raise ValueError(f"unsupported mutable kind: {kind!r}")
        snapshots = self._iter_mutable_snapshots(kind)
        matches = snapshots
        if goal_session_id is not None:
            matches = [payload for payload in matches if payload.get("goal_session_id") == goal_session_id]
        if workflow_run_id is not None:
            matches = [payload for payload in matches if payload.get("workflow_run_id") == workflow_run_id]
        if step_id is not None:
            matches = [payload for payload in matches if payload.get("step_id") == step_id]
        return matches

    def load_canonical_evidence_payloads(
        self,
        *,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Load canonical evidence payloads for a parent-chain prefix."""
        grouped: dict[str, list[tuple[Path, dict[str, Any]]]] = {}
        for path in sorted(self.local_root.rglob("evidence.ndjson")):
            for payload in self._read_ndjson(path):
                if payload.get("goal_session_id") != goal_session_id:
                    continue
                if workflow_run_id is not None and payload.get("workflow_run_id") != workflow_run_id:
                    continue
                if step_id is not None and payload.get("step_id") != step_id:
                    continue
                evidence_id = payload["evidence_id"]
                grouped.setdefault(evidence_id, []).append((path, payload))

        canonical: list[dict[str, Any]] = []
        for evidence_id in sorted(grouped):
            _, payload = self._canonicalize_evidence_matches(evidence_id, grouped[evidence_id])
            canonical.append(payload)
        return canonical

    def find_current_object_path(self, kind: str, source_ref: str) -> Path | None:
        """Return the snapshot path for a mutable object id if it exists."""
        if kind not in _MUTABLE_KIND_DIRS:
            return None
        file_name = telemetry_id_file_name(source_ref)
        matches = list(self.local_root.rglob(f"{_MUTABLE_KIND_DIRS[kind]}/{file_name}"))
        if not matches and file_name != f"{source_ref}.json":
            matches = list(
                self.local_root.rglob(f"{_MUTABLE_KIND_DIRS[kind]}/{source_ref}.json")
            )
        if not matches:
            return None
        if len(matches) > 1:
            raise ValueError(f"duplicate telemetry object snapshots for {source_ref!r}")
        return matches[0]

    def find_append_only_payload(self, kind: str, source_ref: str) -> tuple[Path, dict[str, Any]] | None:
        """Return the append-only payload for an event or evidence id if it exists."""
        if kind == "evidence":
            try:
                return self.canonical_evidence_payload(source_ref)
            except ValueError as exc:
                raise LookupError(str(exc)) from exc
        matches = self.find_append_only_matches(kind, source_ref)
        if not matches:
            return None
        if len(matches) > 1:
            raise LookupError(f"ambiguous source_ref for {kind}:{source_ref}")
        return matches[0]

    def find_append_only_matches(self, kind: str, source_ref: str) -> list[tuple[Path, dict[str, Any]]]:
        """Return all append-only payload matches for an event or evidence id."""
        file_name = "events.ndjson" if kind == "telemetry_event" else "evidence.ndjson"
        id_field = _ID_FIELD_BY_KIND[kind]
        matches: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(self.local_root.rglob(file_name)):
            for payload in self._read_ndjson(path):
                if payload.get(id_field) == source_ref:
                    matches.append((path, payload))
        return self._dedupe_append_only_matches(matches)

    def canonical_evidence_payload(self, source_ref: str) -> tuple[Path, dict[str, Any]] | None:
        """Return the latest legal evidence payload for an evidence id."""
        matches = self.find_append_only_matches("evidence", source_ref)
        if not matches:
            return None
        return self._canonicalize_evidence_matches(source_ref, matches)

    def validate_evidence_transition(
        self,
        current_record: Evidence,
        candidate: Evidence,
    ) -> Evidence:
        """Validate a same-chain evidence backfill against append-only enrichment rules."""
        current_updated_at = datetime.fromisoformat(
            (current_record.updated_at or current_record.created_at).removesuffix("Z") + "+00:00"
        )
        candidate_updated_at = datetime.fromisoformat(
            (candidate.updated_at or candidate.created_at).removesuffix("Z") + "+00:00"
        )
        if candidate_updated_at < current_updated_at:
            raise ValueError(f"illegal evidence history for {candidate.evidence_id}")

        for field_name in ("locator", "digest"):
            current_value = getattr(current_record, field_name)
            candidate_value = getattr(candidate, field_name)
            if current_value is not None and candidate_value != current_value:
                raise ValueError(
                    f"illegal evidence history for {candidate.evidence_id}"
                )

        expected = current_record.validated_update(
            locator=candidate.locator,
            digest=candidate.digest,
            updated_at=candidate.updated_at,
        )
        if candidate.model_dump(mode="json") != expected.model_dump(mode="json"):
            raise ValueError(f"illegal evidence history for {candidate.evidence_id}")
        return expected

    def _scope_root(
        self,
        *,
        scope_level: ScopeLevel,
        goal_session_id: str,
        workflow_run_id: str | None = None,
        step_id: str | None = None,
    ) -> Path:
        if scope_level is ScopeLevel.SESSION:
            return session_root(self.repo_root, goal_session_id)
        if scope_level is ScopeLevel.RUN:
            if workflow_run_id is None:
                raise ValueError("run scope requires workflow_run_id")
            return run_root(self.repo_root, goal_session_id, workflow_run_id)
        if step_id is None or workflow_run_id is None:
            raise ValueError("step scope requires workflow_run_id and step_id")
        return step_root(self.repo_root, goal_session_id, workflow_run_id, step_id)

    def _validate_scope_arguments(
        self,
        *,
        scope_level: ScopeLevel,
        workflow_run_id: str | None,
        step_id: str | None,
    ) -> None:
        if scope_level is ScopeLevel.SESSION:
            if workflow_run_id is not None or step_id is not None:
                raise ValueError("scope level session must not include child IDs")
            return
        if scope_level is ScopeLevel.RUN:
            if workflow_run_id is None:
                raise ValueError("scope level run requires workflow_run_id")
            if step_id is not None:
                raise ValueError("scope level run must not include step_id")
            return
        if workflow_run_id is None or step_id is None:
            raise ValueError("scope level step requires workflow_run_id and step_id")

    def _scope_root_for_record(
        self, record: TelemetryEvent | Evidence | Evaluation | Violation | Artifact
    ) -> Path:
        return self._scope_root(
            scope_level=record.scope_level,
            goal_session_id=record.goal_session_id,
            workflow_run_id=record.workflow_run_id,
            step_id=record.step_id,
        )

    def scope_chain_from_path(self, path: Path) -> tuple[ScopeLevel, str, str | None, str | None]:
        """Derive the canonical scope chain from an on-disk telemetry path."""
        relative = path.resolve().relative_to(self.local_root.resolve())
        parts = relative.parts
        if len(parts) < 2 or parts[0] not in {"sessions", "s"}:
            raise ValueError(f"path is outside telemetry sessions root: {path}")

        from_manifest = self._scope_chain_from_manifest(relative)
        if from_manifest is not None:
            return from_manifest

        goal_session_id = scope_id_from_dir_name(parts[1])
        workflow_run_id: str | None = None
        step_id: str | None = None

        if len(parts) >= 4 and parts[2] in {"runs", "r"}:
            workflow_run_id = scope_id_from_dir_name(parts[3])
        if len(parts) >= 6 and parts[4] in {"steps", "t"}:
            step_id = scope_id_from_dir_name(parts[5])

        if step_id is not None:
            return (ScopeLevel.STEP, goal_session_id, workflow_run_id, step_id)
        if workflow_run_id is not None:
            return (ScopeLevel.RUN, goal_session_id, workflow_run_id, None)
        return (ScopeLevel.SESSION, goal_session_id, None, None)

    def _scope_chain_from_manifest(
        self, relative: Path
    ) -> tuple[ScopeLevel, str, str | None, str | None] | None:
        """Resolve compact scope directories through the manifest when available."""
        if not self.manifest_path.exists():
            return None
        try:
            manifest = self._read_json(self.manifest_path)
        except (OSError, json.JSONDecodeError):
            return None
        relative_posix = relative.as_posix()
        best: tuple[int, tuple[ScopeLevel, str, str | None, str | None]] | None = None
        for session_id, entry in (manifest.get("sessions") or {}).items():
            entry_path = str((entry or {}).get("path", "")).strip()
            if entry_path and _path_is_within(relative_posix, entry_path):
                candidate = (ScopeLevel.SESSION, str(session_id), None, None)
                best = _choose_longer_scope_match(best, entry_path, candidate)
        for run_id, entry in (manifest.get("runs") or {}).items():
            entry_path = str((entry or {}).get("path", "")).strip()
            session_id = str((entry or {}).get("goal_session_id", "")).strip()
            if entry_path and session_id and _path_is_within(relative_posix, entry_path):
                candidate = (ScopeLevel.RUN, session_id, str(run_id), None)
                best = _choose_longer_scope_match(best, entry_path, candidate)
        for step_id, entry in (manifest.get("steps") or {}).items():
            entry_path = str((entry or {}).get("path", "")).strip()
            session_id = str((entry or {}).get("goal_session_id", "")).strip()
            run_id = str((entry or {}).get("workflow_run_id", "")).strip()
            if (
                entry_path
                and session_id
                and run_id
                and _path_is_within(relative_posix, entry_path)
            ):
                candidate = (ScopeLevel.STEP, session_id, run_id, str(step_id))
                best = _choose_longer_scope_match(best, entry_path, candidate)
        return best[1] if best is not None else None

    def _kind_for_record(self, record: TelemetryEvent | Evidence | Evaluation | Violation | Artifact) -> str:
        if isinstance(record, TelemetryEvent):
            return "telemetry_event"
        if isinstance(record, Evidence):
            return "evidence"
        if isinstance(record, Evaluation):
            return "evaluation"
        if isinstance(record, Violation):
            return "violation"
        if isinstance(record, Artifact):
            return "artifact"
        raise TypeError(f"unsupported telemetry record type: {type(record)!r}")

    def _iter_mutable_snapshots(self, kind: str) -> list[dict[str, Any]]:
        directory = _MUTABLE_KIND_DIRS[kind]
        return [self._read_json(path) for path in sorted(self.local_root.rglob(f"{directory}/*.json"))]

    def _iter_event_payloads(self) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []
        for path in sorted(self.local_root.rglob("events.ndjson")):
            payloads.extend(
                payload
                for _path, payload in self._dedupe_append_only_matches(
                    [(path, item) for item in self._read_ndjson(path)]
                )
            )
        return payloads

    def _iter_evidence_payloads(self) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []
        for path in sorted(self.local_root.rglob("evidence.ndjson")):
            payloads.extend(
                payload
                for _path, payload in self._dedupe_append_only_matches(
                    [(path, item) for item in self._read_ndjson(path)]
                )
            )
        return payloads

    def _latest_scope_ids(self) -> dict[str, str | None]:
        activity_records: list[tuple[str, dict[str, Any]]] = []
        for payload in self._iter_event_payloads():
            timestamp = payload.get("timestamp")
            if isinstance(timestamp, str):
                activity_records.append((timestamp, payload))
        for payload in self._iter_evidence_payloads():
            timestamp = payload.get("updated_at") or payload.get("created_at")
            if isinstance(timestamp, str):
                activity_records.append((timestamp, payload))
        for kind in _MUTABLE_KIND_DIRS:
            for payload in self._iter_mutable_snapshots(kind):
                timestamp = payload.get("updated_at") or payload.get("created_at")
                if isinstance(timestamp, str):
                    activity_records.append((timestamp, payload))
        return {
            "latest_goal_session_id": self._latest_scope_id(activity_records, "goal_session_id"),
            "latest_workflow_run_id": self._latest_scope_id(activity_records, "workflow_run_id"),
            "latest_step_id": self._latest_scope_id(activity_records, "step_id"),
        }

    def _latest_scope_id(
        self,
        activity_records: list[tuple[str, dict[str, Any]]],
        field_name: str,
    ) -> str | None:
        candidates = [
            (timestamp, str(payload[field_name]))
            for timestamp, payload in activity_records
            if payload.get(field_name) is not None
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda item: (item[0], item[1]))[1]

    def _canonicalize_evidence_matches(
        self,
        source_ref: str,
        matches: list[tuple[Path, dict[str, Any]]],
    ) -> tuple[Path, dict[str, Any]]:
        canonical_path = matches[0][0]
        current_record = Evidence.model_validate(matches[0][1])

        for path, payload in matches[1:]:
            if path != canonical_path:
                raise ValueError(f"ambiguous source_ref for evidence:{source_ref}")

            candidate = Evidence.model_validate(payload)
            try:
                expected = self.validate_evidence_transition(current_record, candidate)
            except ValueError as exc:
                raise ValueError(f"illegal evidence history for {source_ref}") from exc

            current_record = expected

        return canonical_path, current_record.model_dump(mode="json")

    def _append_ndjson(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
            handle.write("\n")

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _read_json(self, path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_ndjson(self, path: Path) -> list[dict[str, Any]]:
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @staticmethod
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
