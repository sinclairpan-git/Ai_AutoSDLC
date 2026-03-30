"""Unit tests for the V1 telemetry store and writer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_sdlc.telemetry.contracts import (
    Artifact,
    Evaluation,
    Evidence,
    ScopeLevel,
    TelemetryEvent,
    Violation,
)
from ai_sdlc.telemetry.enums import (
    ArtifactRole,
    ArtifactStatus,
    ArtifactType,
    EvaluationResult,
    EvaluationStatus,
    TraceLayer,
)
from ai_sdlc.telemetry.paths import (
    telemetry_indexes_root,
    telemetry_local_root,
    telemetry_manifest_path,
    telemetry_reports_root,
)
from ai_sdlc.telemetry.resolver import SourceResolver
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_ndjson(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_lazy_init_creates_only_local_telemetry_root_and_manifest(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)

    manifest = store.ensure_initialized()

    assert telemetry_local_root(tmp_path).is_dir()
    assert telemetry_manifest_path(tmp_path).is_file()
    assert telemetry_reports_root(tmp_path).exists() is False
    assert manifest["version"] == 1
    assert manifest["sessions"] == {}
    assert manifest["runs"] == {}
    assert manifest["steps"] == {}


def test_store_classifies_hard_fail_default_integrity_failures(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)

    classifier = getattr(store, "classify_hard_fail", None)

    assert callable(classifier)
    assert classifier(PermissionError("raw trace root is not writable")) == "hard_fail_default"
    assert classifier(ValueError("parent chain mismatch for workflow_run_id")) == "hard_fail_default"


def test_store_does_not_classify_lookup_miss_as_hard_fail_default(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)

    classifier = getattr(store, "classify_hard_fail", None)

    assert callable(classifier)
    assert classifier(LookupError("unable to resolve evidence:evd_missing")) is None


@pytest.mark.parametrize(
    ("scope_level", "workflow_run_id", "step_id"),
    [
        (ScopeLevel.SESSION, "wr_0123456789abcdef0123456789abcdef", None),
        (
            ScopeLevel.RUN,
            "wr_0123456789abcdef0123456789abcdef",
            "st_0123456789abcdef0123456789abcdef",
        ),
    ],
)
def test_register_scope_rejects_child_ids_that_contradict_scope_level(
    tmp_path: Path,
    scope_level: ScopeLevel,
    workflow_run_id: str | None,
    step_id: str | None,
) -> None:
    store = TelemetryStore(tmp_path)

    with pytest.raises(ValueError, match="scope level"):
        store.register_scope(
            scope_level=scope_level,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )

    assert store.load_manifest() == {
        "version": 1,
        "sessions": {},
        "runs": {},
        "steps": {},
    }


def test_event_streams_are_append_only_ndjson(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    first_event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.WORKFLOW,
    )
    second_event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id=first_event.goal_session_id,
        workflow_run_id=first_event.workflow_run_id,
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
        timestamp="2026-03-27T10:00:01Z",
        trace_layer=TraceLayer.TOOL,
    )

    writer.write_event(first_event)
    writer.write_event(second_event)

    events_path = store.event_stream_path(
        scope_level=ScopeLevel.RUN,
        goal_session_id=first_event.goal_session_id,
        workflow_run_id=first_event.workflow_run_id,
    )
    lines = _read_ndjson(events_path)

    assert [line["event_id"] for line in lines] == [first_event.event_id, second_event.event_id]
    assert [line["timestamp"] for line in lines] == [first_event.timestamp, second_event.timestamp]


def test_event_ids_are_globally_unique_across_chains(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    first = TelemetryEvent(
        event_id="evt_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
    )
    duplicate = TelemetryEvent(
        event_id=first.event_id,
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_ffffffffffffffffffffffffffffffff",
        workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
        timestamp="2026-03-27T10:00:01Z",
    )

    writer.write_event(first)

    with pytest.raises(ValueError, match="duplicate append-only source_ref"):
        writer.write_event(duplicate)


def test_evidence_allows_same_id_backfill_on_the_same_chain(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    first = Evidence(
        evidence_id="evd_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    backfill = first.validated_update(
        locator="file:///tmp/evidence.txt",
        digest="sha256:abc123",
        updated_at="2026-03-27T10:00:05Z",
    )

    writer.write_evidence(first)
    writer.write_evidence(backfill)

    evidence_path = store.evidence_stream_path(
        scope_level=ScopeLevel.RUN,
        goal_session_id=first.goal_session_id,
        workflow_run_id=first.workflow_run_id,
    )
    lines = _read_ndjson(evidence_path)

    assert [line["evidence_id"] for line in lines] == [first.evidence_id, first.evidence_id]
    assert lines[-1]["locator"] == "file:///tmp/evidence.txt"
    assert lines[-1]["digest"] == "sha256:abc123"
    assert lines[-1]["updated_at"] == "2026-03-27T10:00:05Z"


def test_cross_chain_duplicate_evidence_ids_are_rejected(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    first = Evidence(
        evidence_id="evd_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    duplicate = Evidence(
        evidence_id=first.evidence_id,
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_ffffffffffffffffffffffffffffffff",
        workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
        created_at="2026-03-27T10:00:05Z",
        updated_at="2026-03-27T10:00:05Z",
    )

    writer.write_evidence(first)

    with pytest.raises(ValueError, match="cross-chain evidence duplicate"):
        writer.write_evidence(duplicate)

    assert "wr_ffffffffffffffffffffffffffffffff" not in store.load_manifest()["runs"]


def test_evidence_rejects_rebinding_filled_locator_or_digest_on_same_chain(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    first = Evidence(
        evidence_id="evd_dddddddddddddddddddddddddddddddd",
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    filled = first.validated_update(
        locator="file:///tmp/original.txt",
        digest="sha256:original",
        updated_at="2026-03-27T10:00:05Z",
    )
    rebound = filled.validated_update(
        locator="file:///tmp/rebound.txt",
        digest="sha256:rebound",
        updated_at="2026-03-27T10:00:10Z",
    )

    writer.write_evidence(first)
    writer.write_evidence(filled)

    with pytest.raises(ValueError, match="illegal evidence duplicate"):
        writer.write_evidence(rebound)


def test_evidence_rejects_same_chain_repeat_with_earlier_updated_at(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    first = Evidence(
        evidence_id="evd_ffffffffffffffffffffffffffffffff",
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    filled = first.validated_update(
        locator="file:///tmp/original.txt",
        digest="sha256:original",
        updated_at="2026-03-27T10:00:05Z",
    )
    stale_repeat = filled.validated_update(updated_at="2026-03-27T10:00:04Z")

    writer.write_evidence(first)
    writer.write_evidence(filled)

    with pytest.raises(ValueError, match="illegal evidence duplicate"):
        writer.write_evidence(stale_repeat)


@pytest.mark.parametrize(
    ("factory_name", "id_field", "status_field", "updated_status"),
    [
        ("write_evaluation", "evaluation_id", "status", "passed"),
        ("write_violation", "violation_id", "status", "fixed"),
        ("write_artifact", "artifact_id", "status", "reviewed"),
    ],
)
def test_mutable_objects_write_revision_before_current_snapshot(
    tmp_path: Path,
    factory_name: str,
    id_field: str,
    status_field: str,
    updated_status: str,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    order: list[str] = []

    original_append = store._append_ndjson
    original_write_json = store._write_json

    def tracking_append(path: Path, payload: dict) -> None:
        order.append(path.name)
        original_append(path, payload)

    def tracking_write_json(path: Path, payload: dict) -> None:
        order.append(path.name)
        original_write_json(path, payload)

    store._append_ndjson = tracking_append  # type: ignore[method-assign]
    store._write_json = tracking_write_json  # type: ignore[method-assign]

    base_kwargs = {
        "scope_level": ScopeLevel.STEP,
        "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
        "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
        "step_id": "st_0123456789abcdef0123456789abcdef",
        "created_at": "2026-03-27T10:00:00Z",
        "updated_at": "2026-03-27T10:00:00Z",
    }
    factories = {
        "write_evaluation": Evaluation(**base_kwargs),
        "write_violation": Violation(**base_kwargs),
        "write_artifact": Artifact(
            **base_kwargs,
            artifact_type=ArtifactType.REPORT,
            artifact_role=ArtifactRole.AUDIT,
            status=ArtifactStatus.DRAFT,
        ),
    }
    initial = factories[factory_name]
    update = initial.validated_update(**{status_field: updated_status, "updated_at": "2026-03-27T10:00:05Z"})

    getattr(writer, factory_name)(initial)
    order.clear()
    getattr(writer, factory_name)(update)

    revision_name = f"{factory_name.removeprefix('write_')}s.revisions.ndjson"
    snapshot_name = f"{getattr(initial, id_field)}.json"
    assert revision_name in order
    assert snapshot_name in order
    assert order.index(revision_name) < order.index(snapshot_name)

    snapshot_path = store.current_object_path(update)
    revisions_path = store.revisions_path(update)
    assert _read_json(snapshot_path)[status_field] == updated_status
    assert _read_ndjson(revisions_path)[-1][status_field] == updated_status


def test_cross_chain_parent_mismatches_are_rejected(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    writer.write_event(
        TelemetryEvent(
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:00Z",
            timestamp="2026-03-27T10:00:00Z",
        )
    )

    with pytest.raises(ValueError, match="parent chain mismatch"):
        writer.write_event(
            TelemetryEvent(
                scope_level=ScopeLevel.STEP,
                goal_session_id="gs_ffffffffffffffffffffffffffffffff",
                workflow_run_id="wr_0123456789abcdef0123456789abcdef",
                step_id="st_0123456789abcdef0123456789abcdef",
                created_at="2026-03-27T10:00:01Z",
                updated_at="2026-03-27T10:00:01Z",
                timestamp="2026-03-27T10:00:01Z",
            )
        )


def test_writer_rejects_direct_published_artifact_without_source_closure(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        status=ArtifactStatus.PUBLISHED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )

    with pytest.raises(ValueError, match="source closure"):
        writer.write_artifact(artifact)


def test_writer_rejects_cross_run_source_refs_for_published_artifact(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    goal_session_id = "gs_0123456789abcdef0123456789abcdef"
    source_run_id = "wr_0123456789abcdef0123456789abcdef"
    artifact_run_id = "wr_ffffffffffffffffffffffffffffffff"
    step_id = "st_0123456789abcdef0123456789abcdef"
    evidence = Evidence(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=source_run_id,
        step_id=step_id,
        locator="file:///tmp/evidence.txt",
        digest="sha256:abc123",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    evaluation = Evaluation(
        scope_level=ScopeLevel.STEP,
        goal_session_id=goal_session_id,
        workflow_run_id=source_run_id,
        step_id=step_id,
        result=EvaluationResult.PASSED,
        status=EvaluationStatus.PASSED,
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    writer.write_evidence(evidence)
    writer.write_evaluation(evaluation)
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=goal_session_id,
        workflow_run_id=artifact_run_id,
        status=ArtifactStatus.PUBLISHED,
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
        source_evidence_refs=(evidence.evidence_id,),
        source_object_refs=(f"evaluation:{evaluation.evaluation_id}",),
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )

    with pytest.raises(ValueError, match="source closure"):
        writer.write_artifact(artifact)


def test_source_resolver_uses_source_kind_and_source_ref(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    resolver = SourceResolver(store)

    evaluation = Evaluation(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    writer.write_evaluation(evaluation)

    resolved = resolver.resolve("evaluation", evaluation.evaluation_id)

    assert resolved.kind == "evaluation"
    assert resolved.source_ref == evaluation.evaluation_id
    assert resolved.payload["evaluation_id"] == evaluation.evaluation_id
    assert resolved.path == store.current_object_path(evaluation)


def test_source_resolver_returns_latest_legal_evidence_payload_after_backfill(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)
    resolver = SourceResolver(store)
    first = Evidence(
        evidence_id="evd_cccccccccccccccccccccccccccccccc",
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    backfill = first.validated_update(
        locator="file:///tmp/new-evidence.txt",
        digest="sha256:def456",
        updated_at="2026-03-27T10:00:05Z",
    )

    writer.write_evidence(first)
    writer.write_evidence(backfill)

    resolved = resolver.resolve("evidence", first.evidence_id)

    assert resolved.kind == "evidence"
    assert resolved.source_ref == first.evidence_id
    assert resolved.path == store.evidence_stream_path(
        scope_level=ScopeLevel.RUN,
        goal_session_id=first.goal_session_id,
        workflow_run_id=first.workflow_run_id,
    )
    assert resolved.payload["locator"] == "file:///tmp/new-evidence.txt"
    assert resolved.payload["digest"] == "sha256:def456"
    assert resolved.payload["updated_at"] == "2026-03-27T10:00:05Z"


def test_source_resolver_rejects_illegal_evidence_rebind_history(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    resolver = SourceResolver(store)
    evidence_id = "evd_eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

    store.register_scope(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
    )
    evidence_path = store.evidence_stream_path(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
    )
    store._append_ndjson(
        evidence_path,
        Evidence(
            evidence_id=evidence_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:00Z",
        ).model_dump(mode="json"),
    )
    store._append_ndjson(
        evidence_path,
        Evidence(
            evidence_id=evidence_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:05Z",
            locator="file:///tmp/original.txt",
            digest="sha256:original",
        ).model_dump(mode="json"),
    )
    store._append_ndjson(
        evidence_path,
        Evidence(
            evidence_id=evidence_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:10Z",
            locator="file:///tmp/rebound.txt",
            digest="sha256:rebound",
        ).model_dump(mode="json"),
    )

    with pytest.raises(LookupError, match="illegal evidence history"):
        resolver.resolve("evidence", evidence_id)


def test_source_resolver_rejects_evidence_history_with_backward_updated_at(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    resolver = SourceResolver(store)
    evidence_id = "evd_12121212121212121212121212121212"

    store.register_scope(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
    )
    evidence_path = store.evidence_stream_path(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
    )
    store._append_ndjson(
        evidence_path,
        Evidence(
            evidence_id=evidence_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:00Z",
        ).model_dump(mode="json"),
    )
    store._append_ndjson(
        evidence_path,
        Evidence(
            evidence_id=evidence_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:05Z",
            locator="file:///tmp/original.txt",
            digest="sha256:original",
        ).model_dump(mode="json"),
    )
    store._append_ndjson(
        evidence_path,
        Evidence(
            evidence_id=evidence_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:04Z",
            locator="file:///tmp/original.txt",
            digest="sha256:original",
        ).model_dump(mode="json"),
    )

    with pytest.raises(LookupError, match="illegal evidence history"):
        resolver.resolve("evidence", evidence_id)


def test_source_resolver_rejects_ambiguous_append_only_source_refs(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    resolver = SourceResolver(store)
    duplicate_event_id = "evt_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

    store.register_scope(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
    )
    store.register_scope(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_ffffffffffffffffffffffffffffffff",
        workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
    )
    store._append_ndjson(
        store.event_stream_path(
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        ),
        TelemetryEvent(
            event_id=duplicate_event_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            created_at="2026-03-27T10:00:00Z",
            updated_at="2026-03-27T10:00:00Z",
            timestamp="2026-03-27T10:00:00Z",
        ).model_dump(mode="json"),
    )
    store._append_ndjson(
        store.event_stream_path(
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_ffffffffffffffffffffffffffffffff",
            workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
        ),
        TelemetryEvent(
            event_id=duplicate_event_id,
            scope_level=ScopeLevel.RUN,
            goal_session_id="gs_ffffffffffffffffffffffffffffffff",
            workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
            created_at="2026-03-27T10:00:01Z",
            updated_at="2026-03-27T10:00:01Z",
            timestamp="2026-03-27T10:00:01Z",
        ).model_dump(mode="json"),
    )

    with pytest.raises(LookupError, match="ambiguous source_ref"):
        resolver.resolve("event", duplicate_event_id)


def test_rebuild_indexes_restores_deleted_index_directory(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    open_violation = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
    )
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=open_violation.goal_session_id,
        workflow_run_id=open_violation.workflow_run_id,
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )
    event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id=open_violation.goal_session_id,
        workflow_run_id=open_violation.workflow_run_id,
        created_at="2026-03-27T10:00:02Z",
        updated_at="2026-03-27T10:00:02Z",
        timestamp="2026-03-27T10:00:02Z",
    )

    writer.write_violation(open_violation)
    writer.write_artifact(artifact)
    writer.write_event(event)

    store.delete_indexes()
    rebuilt = store.rebuild_indexes()

    assert rebuilt["open_violations_path"].is_file()
    assert rebuilt["latest_artifacts_path"].is_file()
    assert rebuilt["timeline_cursor_path"].is_file()
    assert _read_json(rebuilt["open_violations_path"])["violation_ids"] == [open_violation.violation_id]
    assert _read_json(rebuilt["latest_artifacts_path"])["artifact_ids"] == [artifact.artifact_id]
    assert _read_json(rebuilt["timeline_cursor_path"])["last_event_id"] == event.event_id


def test_writer_refreshes_indexes_without_manual_rebuild(tmp_path: Path) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.TOOL,
    )
    violation = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        created_at="2026-03-27T10:00:01Z",
        updated_at="2026-03-27T10:00:01Z",
    )
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=event.goal_session_id,
        workflow_run_id=event.workflow_run_id,
        created_at="2026-03-27T10:00:02Z",
        updated_at="2026-03-27T10:00:02Z",
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )

    writer.write_event(event)
    writer.write_violation(violation)
    writer.write_artifact(artifact)

    indexes_root = telemetry_indexes_root(tmp_path)
    assert _read_json(indexes_root / "timeline-cursor.json")["last_event_id"] == event.event_id
    assert _read_json(indexes_root / "open-violations.json")["violation_ids"] == [violation.violation_id]
    assert _read_json(indexes_root / "latest-artifacts.json")["artifact_ids"] == [artifact.artifact_id]


def test_derive_index_payloads_match_canonical_latest_truth_without_index_files(
    tmp_path: Path,
) -> None:
    store = TelemetryStore(tmp_path)
    writer = TelemetryWriter(store)

    older_event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_ffffffffffffffffffffffffffffffff",
        workflow_run_id="wr_ffffffffffffffffffffffffffffffff",
        created_at="2026-03-27T10:00:00Z",
        updated_at="2026-03-27T10:00:00Z",
        timestamp="2026-03-27T10:00:00Z",
        trace_layer=TraceLayer.WORKFLOW,
    )
    fresh_event = TelemetryEvent(
        scope_level=ScopeLevel.RUN,
        goal_session_id="gs_00000000000000000000000000000000",
        workflow_run_id="wr_00000000000000000000000000000000",
        created_at="2026-03-27T10:00:10Z",
        updated_at="2026-03-27T10:00:10Z",
        timestamp="2026-03-27T10:00:10Z",
        trace_layer=TraceLayer.TOOL,
    )
    violation = Violation(
        scope_level=ScopeLevel.RUN,
        goal_session_id=fresh_event.goal_session_id,
        workflow_run_id=fresh_event.workflow_run_id,
        created_at="2026-03-27T10:00:11Z",
        updated_at="2026-03-27T10:00:11Z",
    )
    artifact = Artifact(
        scope_level=ScopeLevel.RUN,
        goal_session_id=fresh_event.goal_session_id,
        workflow_run_id=fresh_event.workflow_run_id,
        created_at="2026-03-27T10:00:12Z",
        updated_at="2026-03-27T10:00:12Z",
        artifact_type=ArtifactType.REPORT,
        artifact_role=ArtifactRole.AUDIT,
    )

    writer.write_event(older_event)
    writer.write_event(fresh_event)
    writer.write_violation(violation)
    writer.write_artifact(artifact)
    store.delete_indexes()

    payloads = store.derive_index_payloads()

    assert payloads["open_violations"] == {"violation_ids": [violation.violation_id]}
    assert payloads["latest_artifacts"] == {"artifact_ids": [artifact.artifact_id]}
    assert payloads["timeline_cursor"] == {
        "event_count": 2,
        "last_event_id": fresh_event.event_id,
        "last_timestamp": fresh_event.timestamp,
        "latest_goal_session_id": fresh_event.goal_session_id,
        "latest_workflow_run_id": fresh_event.workflow_run_id,
        "latest_step_id": None,
    }


def test_only_writer_exposes_public_object_persistence_api() -> None:
    store_public = {
        name
        for name in dir(TelemetryStore)
        if not name.startswith("_") and callable(getattr(TelemetryStore, name))
    }
    writer_public = {
        name
        for name in dir(TelemetryWriter)
        if not name.startswith("_") and callable(getattr(TelemetryWriter, name))
    }

    assert "write_json" not in store_public
    assert "append_ndjson" not in store_public
    assert "write_event" not in store_public
    assert "write_evaluation" not in store_public
    assert {"write_event", "write_evaluation", "write_violation", "write_artifact"} <= writer_public
