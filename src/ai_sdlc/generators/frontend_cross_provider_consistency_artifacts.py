"""Frontend cross-provider consistency artifact instantiation helpers."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from ai_sdlc.models.frontend_cross_provider_consistency import (
    ConsistencyDiffRecord,
    ConsistencyHandoffContract,
    ConsistencyReadinessGate,
    CoverageGapRecord,
    FrontendCrossProviderConsistencySet,
    ProviderPairCertificationBundle,
    ProviderPairTruthSurfacingRecord,
    ReadinessGateRule,
    build_p2_frontend_cross_provider_consistency_baseline,
)


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
    return deduped


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


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def frontend_cross_provider_consistency_root(root: Path) -> Path:
    """Return the canonical root for cross-provider consistency artifacts."""

    return root / "governance" / "frontend" / "cross-provider-consistency"


def materialize_frontend_cross_provider_consistency_artifacts(
    root: Path,
    *,
    consistency: FrontendCrossProviderConsistencySet,
) -> list[Path]:
    """Write the minimal Track D pair-centric artifact set to disk."""

    artifact_root = frontend_cross_provider_consistency_root(root)
    paths = [
        _write_yaml(
            artifact_root / "consistency.manifest.yaml",
            {
                "work_item_id": consistency.work_item_id,
                "source_work_item_ids": consistency.source_work_item_ids,
                "artifact_root": consistency.handoff_contract.artifact_root,
                "schema_family": consistency.handoff_contract.schema_family,
                "current_version": consistency.handoff_contract.current_version,
                "pair_ids": [
                    bundle.pair_id for bundle in consistency.certification_bundles
                ],
            },
        ),
        _write_yaml(
            artifact_root / "handoff.schema.yaml",
            consistency.handoff_contract.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            artifact_root / "truth-surfacing.yaml",
            {
                "items": [
                    record.model_dump(mode="json", exclude_none=True)
                    for record in consistency.truth_surfacing_records
                ]
            },
        ),
        _write_yaml(
            artifact_root / "readiness-gate.yaml",
            {
                "gate_id": consistency.readiness_gate.gate_id,
                "required_coverage_scope": consistency.readiness_gate.required_coverage_scope,
                "optional_coverage_scope": consistency.readiness_gate.optional_coverage_scope,
                "ux_equivalence_clause_ids": consistency.readiness_gate.ux_equivalence_clause_ids,
                "rules": [
                    rule.model_dump(mode="json", exclude_none=True)
                    for rule in consistency.readiness_gate.rules
                ],
            },
        ),
    ]

    diff_records_by_pair: dict[str, list[dict[str, object]]] = {}
    for record in consistency.diff_records:
        diff_records_by_pair.setdefault(record.pair_id, []).append(
            record.model_dump(mode="json", exclude_none=True)
        )

    coverage_gaps_by_pair: dict[str, list[dict[str, object]]] = {}
    for gap in consistency.coverage_gaps:
        coverage_gaps_by_pair.setdefault(gap.pair_id, []).append(
            gap.model_dump(mode="json", exclude_none=True)
        )

    for bundle in consistency.certification_bundles:
        pair_root = artifact_root / "provider-pairs" / bundle.pair_id
        diff_records = diff_records_by_pair.get(bundle.pair_id, [])
        coverage_gaps = coverage_gaps_by_pair.get(bundle.pair_id, [])
        paths.extend(
            [
                _write_yaml(
                    pair_root / "diff-summary.yaml",
                    {
                        "pair_id": bundle.pair_id,
                        "baseline_provider_id": bundle.baseline_provider_id,
                        "candidate_provider_id": bundle.candidate_provider_id,
                        "page_schema_id": bundle.page_schema_id,
                        "compared_style_pack_id": bundle.compared_style_pack_id,
                        "final_verdict": bundle.state_vector.final_verdict,
                        "comparability_state": bundle.state_vector.comparability_state,
                        "blocking_state": bundle.state_vector.blocking_state,
                        "evidence_state": bundle.state_vector.evidence_state,
                        "diffs": diff_records,
                        "coverage_gaps": coverage_gaps,
                    },
                ),
                _write_yaml(
                    pair_root / "certification.yaml",
                    {
                        "pair_id": bundle.pair_id,
                        "baseline_provider_id": bundle.baseline_provider_id,
                        "candidate_provider_id": bundle.candidate_provider_id,
                        "page_schema_id": bundle.page_schema_id,
                        "compared_style_pack_id": bundle.compared_style_pack_id,
                        "required_journey_ids": bundle.required_journey_ids,
                        "final_verdict": bundle.state_vector.final_verdict,
                        "comparability_state": bundle.state_vector.comparability_state,
                        "blocking_state": bundle.state_vector.blocking_state,
                        "evidence_state": bundle.state_vector.evidence_state,
                        "certification_gate": bundle.certification_gate,
                        "diff_refs": [
                            f"artifact:{consistency.handoff_contract.artifact_root}/provider-pairs/{bundle.pair_id}/diff-summary.yaml#{diff_id}"
                            for diff_id in bundle.diff_record_ids
                        ],
                        "coverage_gap_refs": [
                            f"artifact:{consistency.handoff_contract.artifact_root}/provider-pairs/{bundle.pair_id}/diff-summary.yaml#{gap_id}"
                            for gap_id in bundle.coverage_gap_ids
                        ],
                    },
                ),
                _write_yaml(
                    pair_root / "evidence-index.yaml",
                    {
                        "pair_id": bundle.pair_id,
                        "diff_evidence_refs": [
                            ref
                            for record in diff_records
                            for ref in record.get("evidence_refs", [])
                        ],
                        "upstream_truth_refs": [
                            ref
                            for gap in coverage_gaps
                            for ref in gap.get("upstream_truth_refs", [])
                        ],
                    },
                ),
            ]
        )

    return _dedupe_paths(paths)


def load_frontend_cross_provider_consistency_artifacts(
    root: Path,
) -> FrontendCrossProviderConsistencySet:
    """Load the canonical cross-provider consistency artifact set from disk."""

    artifact_root = frontend_cross_provider_consistency_root(root)
    baseline = build_p2_frontend_cross_provider_consistency_baseline()
    manifest = _read_yaml_mapping(artifact_root / "consistency.manifest.yaml")
    handoff_schema = _read_yaml_mapping(artifact_root / "handoff.schema.yaml")
    truth_surfacing = _read_yaml_mapping(artifact_root / "truth-surfacing.yaml")
    readiness_gate = _read_yaml_mapping(artifact_root / "readiness-gate.yaml")

    try:
        raw_truth_items = truth_surfacing.get("items", [])
        raw_rules = readiness_gate.get("rules", [])
        if not isinstance(raw_truth_items, list):
            raise ValueError("truth surfacing artifact `items` must be a list")
        if not isinstance(raw_rules, list):
            raise ValueError("readiness gate artifact `rules` must be a list")

        pair_ids = manifest.get(
            "pair_ids",
            [bundle.pair_id for bundle in baseline.certification_bundles],
        )
        if not isinstance(pair_ids, list):
            raise ValueError("consistency manifest `pair_ids` must be a list")
        pair_ids = _dedupe_text_items(pair_ids)

        diff_records: list[ConsistencyDiffRecord] = []
        coverage_gaps: list[CoverageGapRecord] = []
        certification_bundles: list[ProviderPairCertificationBundle] = []

        for pair_id in pair_ids:
            if not isinstance(pair_id, str) or not pair_id:
                raise ValueError("consistency manifest `pair_ids` contains invalid item")
            pair_root = artifact_root / "provider-pairs" / pair_id
            diff_summary = _read_yaml_mapping(pair_root / "diff-summary.yaml")
            certification = _read_yaml_mapping(pair_root / "certification.yaml")
            evidence_index = _read_yaml_mapping(pair_root / "evidence-index.yaml")

            raw_diffs = diff_summary.get("diffs", [])
            raw_gaps = diff_summary.get("coverage_gaps", [])
            raw_diff_refs = certification.get("diff_refs", [])
            raw_gap_refs = certification.get("coverage_gap_refs", [])
            raw_diff_evidence_refs = evidence_index.get("diff_evidence_refs", [])
            raw_upstream_truth_refs = evidence_index.get("upstream_truth_refs", [])
            if not isinstance(raw_diffs, list):
                raise ValueError("diff summary artifact `diffs` must be a list")
            if not isinstance(raw_gaps, list):
                raise ValueError("diff summary artifact `coverage_gaps` must be a list")
            if not isinstance(raw_diff_refs, list):
                raise ValueError("certification artifact `diff_refs` must be a list")
            if not isinstance(raw_gap_refs, list):
                raise ValueError("certification artifact `coverage_gap_refs` must be a list")
            if not isinstance(raw_diff_evidence_refs, list):
                raise ValueError("evidence index artifact `diff_evidence_refs` must be a list")
            if not isinstance(raw_upstream_truth_refs, list):
                raise ValueError(
                    "evidence index artifact `upstream_truth_refs` must be a list"
                )

            pair_diff_records = [
                ConsistencyDiffRecord.model_validate(item)
                for item in _dedupe_mapping_items(raw_diffs)
            ]
            pair_coverage_gaps = [
                CoverageGapRecord.model_validate(item)
                for item in _dedupe_mapping_items(raw_gaps)
            ]
            raw_diff_refs = _dedupe_text_items(raw_diff_refs)
            raw_gap_refs = _dedupe_text_items(raw_gap_refs)
            raw_diff_evidence_refs = _dedupe_text_items(raw_diff_evidence_refs)
            raw_upstream_truth_refs = _dedupe_text_items(raw_upstream_truth_refs)
            derived_diff_evidence_refs = _dedupe_text_items(
                [
                ref for record in pair_diff_records for ref in record.evidence_refs
                ]
            )
            derived_upstream_truth_refs = _dedupe_text_items(
                [
                ref for gap in pair_coverage_gaps for ref in gap.upstream_truth_refs
                ]
            )
            if list(raw_diff_evidence_refs) != derived_diff_evidence_refs:
                raise ValueError(
                    f"evidence index diff_evidence_refs must match diff summary: {pair_id}"
                )
            if list(raw_upstream_truth_refs) != derived_upstream_truth_refs:
                raise ValueError(
                    f"evidence index upstream_truth_refs must match diff summary: {pair_id}"
                )
            if str(diff_summary.get("pair_id", pair_id)) != pair_id:
                raise ValueError(f"diff summary pair_id must match manifest pair_id: {pair_id}")
            if str(certification.get("pair_id", pair_id)) != pair_id:
                raise ValueError(
                    f"certification pair_id must match manifest pair_id: {pair_id}"
                )
            if str(evidence_index.get("pair_id", pair_id)) != pair_id:
                raise ValueError(
                    f"evidence index pair_id must match manifest pair_id: {pair_id}"
                )

            diff_records.extend(pair_diff_records)
            coverage_gaps.extend(pair_coverage_gaps)
            certification_bundles.append(
                ProviderPairCertificationBundle(
                    pair_id=str(certification.get("pair_id", pair_id)),
                    baseline_provider_id=str(
                        certification.get("baseline_provider_id", "")
                    ),
                    candidate_provider_id=str(
                        certification.get("candidate_provider_id", "")
                    ),
                    page_schema_id=str(certification.get("page_schema_id", "")),
                    compared_style_pack_id=str(
                        certification.get("compared_style_pack_id", "")
                    ),
                    required_journey_ids=_dedupe_text_items(
                        certification.get("required_journey_ids", ())
                    ),
                    state_vector={
                        "final_verdict": str(
                            certification.get(
                                "final_verdict",
                                diff_summary.get("final_verdict", "consistent"),
                            )
                        ),
                        "comparability_state": str(
                            certification.get(
                                "comparability_state",
                                diff_summary.get("comparability_state", "comparable"),
                            )
                        ),
                        "blocking_state": str(
                            certification.get(
                                "blocking_state",
                                diff_summary.get("blocking_state", "ready"),
                            )
                        ),
                        "evidence_state": str(
                            certification.get(
                                "evidence_state",
                                diff_summary.get("evidence_state", "fresh"),
                            )
                        ),
                    },
                    diff_record_ids=[
                        str(ref).rsplit("#", 1)[-1] for ref in raw_diff_refs if str(ref)
                    ],
                    coverage_gap_ids=[
                        str(ref).rsplit("#", 1)[-1] for ref in raw_gap_refs if str(ref)
                    ],
                    certification_gate=str(
                        certification.get("certification_gate", "blocked")
                    ),
                )
            )

        consistency = FrontendCrossProviderConsistencySet(
            work_item_id=str(manifest.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=_dedupe_text_items(
                manifest.get("source_work_item_ids", baseline.source_work_item_ids)
            ),
            ux_equivalence_clauses=list(baseline.ux_equivalence_clauses),
            diff_records=diff_records,
            coverage_gaps=coverage_gaps,
            certification_bundles=certification_bundles,
            truth_surfacing_records=[
                ProviderPairTruthSurfacingRecord.model_validate(item)
                for item in _dedupe_mapping_items(raw_truth_items)
            ],
            readiness_gate=ConsistencyReadinessGate(
                gate_id=str(
                    readiness_gate.get("gate_id", baseline.readiness_gate.gate_id)
                ),
                required_coverage_scope=_dedupe_text_items(
                    readiness_gate.get(
                        "required_coverage_scope",
                        baseline.readiness_gate.required_coverage_scope,
                    )
                ),
                optional_coverage_scope=_dedupe_text_items(
                    readiness_gate.get(
                        "optional_coverage_scope",
                        baseline.readiness_gate.optional_coverage_scope,
                    )
                ),
                ux_equivalence_clause_ids=_dedupe_text_items(
                    readiness_gate.get(
                        "ux_equivalence_clause_ids",
                        baseline.readiness_gate.ux_equivalence_clause_ids,
                    )
                ),
                rules=[
                    ReadinessGateRule.model_validate(item)
                    for item in _dedupe_mapping_items(raw_rules)
                ],
            ),
            handoff_contract=ConsistencyHandoffContract(
                schema_family=str(
                    handoff_schema.get(
                        "schema_family",
                        baseline.handoff_contract.schema_family,
                    )
                ),
                current_version=str(
                    handoff_schema.get(
                        "current_version",
                        baseline.handoff_contract.current_version,
                    )
                ),
                compatible_versions=_dedupe_text_items(
                    handoff_schema.get(
                        "compatible_versions",
                        baseline.handoff_contract.compatible_versions,
                    )
                ),
                artifact_root=str(
                    handoff_schema.get(
                        "artifact_root",
                        baseline.handoff_contract.artifact_root,
                    )
                ),
                canonical_files=list(baseline.handoff_contract.canonical_files),
                program_service_fields=list(
                    baseline.handoff_contract.program_service_fields
                ),
                cli_fields=list(baseline.handoff_contract.cli_fields),
                verify_fields=list(baseline.handoff_contract.verify_fields),
            ),
        )
    except Exception as exc:  # pragma: no cover - surfaced in callers
        raise ValueError(
            f"invalid frontend cross-provider consistency artifact set: {exc}"
        ) from exc
    return consistency


def _write_yaml(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            payload,
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _read_yaml_mapping(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(
            f"missing frontend cross-provider consistency artifact: {path.as_posix()}"
        )
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(
            f"invalid frontend cross-provider consistency artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            "invalid frontend cross-provider consistency artifact "
            f"{path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_cross_provider_consistency_root",
    "load_frontend_cross_provider_consistency_artifacts",
    "materialize_frontend_cross_provider_consistency_artifacts",
]
