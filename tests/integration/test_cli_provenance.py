"""Integration tests for the read-only provenance CLI."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_sdlc.cli.main import app
from ai_sdlc.routers.bootstrap import init_project
from ai_sdlc.telemetry.contracts import (
    CaptureMode,
    Confidence,
    Evidence,
    ScopeLevel,
    TelemetryEvent,
)
from ai_sdlc.telemetry.enums import (
    IngressKind,
    ProvenanceNodeKind,
    ProvenanceRelationKind,
)
from ai_sdlc.telemetry.provenance_contracts import ProvenanceEdgeFact, ProvenanceNodeFact
from ai_sdlc.telemetry.store import TelemetryStore
from ai_sdlc.telemetry.writer import TelemetryWriter

runner = CliRunner()


def _write_cli_fixture(root: Path) -> str:
    store = TelemetryStore(root)
    writer = TelemetryWriter(store)
    writer.write_event(
        TelemetryEvent(
            event_id="evt_0123456789abcdef0123456789abcdef",
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            capture_mode=CaptureMode.AUTO,
            created_at="2026-03-31T10:00:00Z",
            updated_at="2026-03-31T10:00:00Z",
            timestamp="2026-03-31T10:00:00Z",
        )
    )
    writer.write_evidence(
        Evidence(
            evidence_id="evd_11111111111111111111111111111111",
            scope_level=ScopeLevel.STEP,
            goal_session_id="gs_0123456789abcdef0123456789abcdef",
            workflow_run_id="wr_0123456789abcdef0123456789abcdef",
            step_id="st_0123456789abcdef0123456789abcdef",
            locator="prov://conversation/message-001",
            digest="sha256:message",
            created_at="2026-03-31T10:00:00Z",
            updated_at="2026-03-31T10:00:00Z",
        )
    )
    writer.write_provenance_node(
        ProvenanceNodeFact(
            node_id="pn_11111111111111111111111111111111",
            node_kind=ProvenanceNodeKind.CONVERSATION_MESSAGE,
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            scope_level=ScopeLevel.STEP,
            trace_context={
                "goal_session_id": "gs_0123456789abcdef0123456789abcdef",
                "workflow_run_id": "wr_0123456789abcdef0123456789abcdef",
                "step_id": "st_0123456789abcdef0123456789abcdef",
                "parent_event_id": "evt_0123456789abcdef0123456789abcdef",
            },
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_11111111111111111111111111111111",),
        )
    )
    writer.write_provenance_edge(
        ProvenanceEdgeFact(
            edge_id="pe_11111111111111111111111111111111",
            relation_kind=ProvenanceRelationKind.TRIGGERED_BY,
            from_ref="event:evt_0123456789abcdef0123456789abcdef",
            to_ref="provenance_node:pn_11111111111111111111111111111111",
            ingress_kind=IngressKind.INJECTED,
            confidence=Confidence.MEDIUM,
            observed_at="2026-03-31T10:00:00Z",
            ingestion_order=0,
            source_object_refs=("event:evt_0123456789abcdef0123456789abcdef",),
            source_evidence_refs=("evd_11111111111111111111111111111111",),
        ),
        scope_level=ScopeLevel.STEP,
        goal_session_id="gs_0123456789abcdef0123456789abcdef",
        workflow_run_id="wr_0123456789abcdef0123456789abcdef",
        step_id="st_0123456789abcdef0123456789abcdef",
    )
    return "provenance_node:pn_11111111111111111111111111111111"


def test_help_exposes_read_only_provenance_surface() -> None:
    result = runner.invoke(app, ["provenance", "--help"])

    assert result.exit_code == 0
    out = result.output.lower()
    assert "summary" in out
    assert "explain" in out
    assert "gaps" in out
    assert "read-only" in out


def test_provenance_summary_supports_text_and_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    subject_ref = _write_cli_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)

    with patch("ai_sdlc.cli.main.run_ide_adapter_if_initialized"):
        text_result = runner.invoke(
            app,
            ["provenance", "summary", "--subject-ref", subject_ref],
        )
        json_result = runner.invoke(
            app,
            ["provenance", "summary", "--subject-ref", subject_ref, "--json"],
        )

    assert text_result.exit_code == 0
    assert "Triggered by: prov://conversation/message-001" in text_result.output
    assert json_result.exit_code == 0
    payload = json.loads(json_result.output)
    assert list(payload) == [
        "subject_ref",
        "triggered_by",
        "invoked",
        "cited",
        "chain_modes",
        "blocking_gap",
        "assessment",
        "failures",
    ]
    assert payload["subject_ref"] == subject_ref
    assert payload["triggered_by"] == ["prov://conversation/message-001"]


def test_provenance_summary_does_not_trigger_ide_adapter_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    init_project(tmp_path)
    subject_ref = _write_cli_fixture(tmp_path)
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".vscode").mkdir(exist_ok=True)

    result = runner.invoke(
        app,
        ["provenance", "summary", "--subject-ref", subject_ref],
    )

    assert result.exit_code == 0
    assert not (tmp_path / ".vscode" / "AI-SDLC.md").exists()
