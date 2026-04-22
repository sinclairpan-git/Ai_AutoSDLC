"""Read-only observer rerun pipeline for derived telemetry outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.telemetry.contracts import Evaluation
from ai_sdlc.telemetry.detectors import (
    MismatchFinding,
    detect_native_delegation_mismatches,
)
from ai_sdlc.telemetry.enums import ScopeLevel
from ai_sdlc.telemetry.evaluators import (
    ObserverEvaluationFinding,
    build_observer_coverage_evaluation,
    classify_unknown_family_outputs,
)
from ai_sdlc.telemetry.generators import _unique_strings, observer_facts_digest
from ai_sdlc.telemetry.provenance_contracts import (
    ProvenanceAssessment,
    ProvenanceGapFinding,
)
from ai_sdlc.telemetry.provenance_observer import observe_provenance_step
from ai_sdlc.telemetry.store import TelemetryStore


@dataclass(frozen=True, slots=True)
class ObserverConditions:
    """Fixed observer rerun conditions for reproducible derived outputs."""

    observer_version: str = "v1"
    policy: str = "default"
    profile: str = "self_hosting"
    mode: str = "lite"


@dataclass(frozen=True, slots=True)
class ObserverTrigger:
    """A queued async observer trigger emitted after step/run completion."""

    goal_session_id: str
    workflow_run_id: str
    scope_level: ScopeLevel
    step_id: str | None = None
    stage: str | None = None
    trigger_point_type: str = "observer_async"


@dataclass(frozen=True, slots=True)
class StepObserverResult:
    """Structured observer baseline outputs for one step scope."""

    conditions: ObserverConditions
    goal_session_id: str
    workflow_run_id: str
    step_id: str
    facts_digest: str
    coverage_evaluation: Evaluation
    coverage_gaps: tuple[ObserverEvaluationFinding, ...]
    unknowns: tuple[ObserverEvaluationFinding, ...]
    unobserved: tuple[ObserverEvaluationFinding, ...]
    mismatch_findings: tuple[MismatchFinding, ...]
    source_evidence_refs: tuple[str, ...]
    provenance_assessments: tuple[ProvenanceAssessment, ...] = ()
    provenance_gaps: tuple[ProvenanceGapFinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "coverage_gaps",
            _dedupe_observer_findings(self.coverage_gaps),
        )
        object.__setattr__(self, "unknowns", _dedupe_observer_findings(self.unknowns))
        object.__setattr__(
            self,
            "unobserved",
            _dedupe_observer_findings(self.unobserved),
        )
        object.__setattr__(
            self,
            "mismatch_findings",
            _dedupe_mismatch_findings(self.mismatch_findings),
        )
        object.__setattr__(
            self,
            "source_evidence_refs",
            tuple(sorted(_unique_strings(self.source_evidence_refs))),
        )
        object.__setattr__(
            self,
            "provenance_assessments",
            tuple(_dedupe_provenance_models(self.provenance_assessments)),
        )
        object.__setattr__(
            self,
            "provenance_gaps",
            tuple(_dedupe_provenance_models(self.provenance_gaps)),
        )


class TelemetryObserver:
    """Replay-derived observer outputs from the current canonical fact layer."""

    def __init__(
        self,
        repo_root: Path,
        *,
        store: TelemetryStore | None = None,
        conditions: ObserverConditions | None = None,
    ) -> None:
        self.repo_root = Path(repo_root)
        self.store = store or TelemetryStore(self.repo_root)
        self.conditions = conditions or ObserverConditions()

    def observe_step(
        self,
        *,
        goal_session_id: str,
        workflow_run_id: str,
        step_id: str,
    ) -> StepObserverResult:
        """Replay one step scope into reproducible observer findings."""
        event_payloads = self._load_step_event_payloads(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        evidence_payloads = self.store.load_canonical_evidence_payloads(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        facts_digest = observer_facts_digest(
            event_payloads=event_payloads,
            evidence_payloads=evidence_payloads,
        )
        unknown_family = classify_unknown_family_outputs(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            event_payloads=event_payloads,
            evidence_payloads=evidence_payloads,
            observer_version=self.conditions.observer_version,
            policy=self.conditions.policy,
            profile=self.conditions.profile,
            mode=self.conditions.mode,
        )
        mismatch_findings = detect_native_delegation_mismatches(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            event_payloads=event_payloads,
            evidence_payloads=evidence_payloads,
            observer_version=self.conditions.observer_version,
            policy=self.conditions.policy,
            profile=self.conditions.profile,
            mode=self.conditions.mode,
        )
        coverage_evaluation = build_observer_coverage_evaluation(
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            event_payloads=event_payloads,
            evidence_payloads=evidence_payloads,
            observer_version=self.conditions.observer_version,
            policy=self.conditions.policy,
            profile=self.conditions.profile,
            mode=self.conditions.mode,
            issue_count=len(unknown_family) + len(mismatch_findings),
        )
        coverage_gaps = _dedupe_observer_findings(
            finding for finding in unknown_family if finding.kind == "coverage_gap"
        )
        unknowns = _dedupe_observer_findings(
            finding for finding in unknown_family if finding.kind == "unknown"
        )
        unobserved = _dedupe_observer_findings(
            finding for finding in unknown_family if finding.kind == "unobserved"
        )
        source_evidence_refs = tuple(
            sorted(
                _unique_strings(
                    [
                        str(payload["evidence_id"])
                        for payload in evidence_payloads
                        if payload.get("evidence_id") is not None
                    ]
                )
            )
        )
        provenance = observe_provenance_step(
            self.store,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
        )
        return StepObserverResult(
            conditions=self.conditions,
            goal_session_id=goal_session_id,
            workflow_run_id=workflow_run_id,
            step_id=step_id,
            facts_digest=facts_digest,
            coverage_evaluation=coverage_evaluation,
            coverage_gaps=coverage_gaps,
            unknowns=unknowns,
            unobserved=unobserved,
            mismatch_findings=_dedupe_mismatch_findings(mismatch_findings),
            source_evidence_refs=source_evidence_refs,
            provenance_assessments=provenance.assessments,
            provenance_gaps=provenance.gaps,
        )

    def _load_step_event_payloads(
        self,
        *,
        goal_session_id: str,
        workflow_run_id: str,
        step_id: str,
    ) -> list[dict[str, object]]:
        payloads: list[tuple[Path, dict[str, object]]] = []
        for scope_level, scope_step_id in (
            (ScopeLevel.SESSION, None),
            (ScopeLevel.RUN, None),
            (ScopeLevel.STEP, step_id),
        ):
            stream_path = self.store.event_stream_path(
                scope_level=scope_level,
                goal_session_id=goal_session_id,
                workflow_run_id=workflow_run_id if scope_level is not ScopeLevel.SESSION else None,
                step_id=scope_step_id,
            )
            if stream_path.exists():
                payloads.extend(
                    (stream_path, payload) for payload in self.store._read_ndjson(stream_path)
                )
        return [payload for _path, payload in _dedupe_stream_payloads(payloads)]


def _dedupe_observer_findings(
    findings: tuple[ObserverEvaluationFinding, ...]
    | list[ObserverEvaluationFinding]
    | object,
) -> tuple[ObserverEvaluationFinding, ...]:
    unique: dict[tuple[str, str, str], ObserverEvaluationFinding] = {}
    for finding in findings or ():
        marker = (finding.kind, finding.subject, finding.evaluation.evaluation_id)
        unique.setdefault(marker, finding)
    return tuple(unique.values())


def _dedupe_mismatch_findings(
    findings: tuple[MismatchFinding, ...] | list[MismatchFinding] | object,
) -> tuple[MismatchFinding, ...]:
    unique: dict[tuple[str, str, str], MismatchFinding] = {}
    for finding in findings or ():
        marker = (
            finding.finding_name,
            finding.subject,
            finding.evaluation.evaluation_id,
        )
        unique.setdefault(marker, finding)
    return tuple(unique.values())


def _dedupe_stream_payloads(
    payloads: list[tuple[Path, dict[str, object]]],
) -> list[tuple[Path, dict[str, object]]]:
    deduped: list[tuple[Path, dict[str, object]]] = []
    seen: set[tuple[str, str]] = set()
    for path, payload in payloads:
        marker = (
            str(path),
            json.dumps(payload, sort_keys=True, ensure_ascii=False),
        )
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append((path, payload))
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
