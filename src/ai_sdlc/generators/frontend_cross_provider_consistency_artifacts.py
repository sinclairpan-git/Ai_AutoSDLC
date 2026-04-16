"""Frontend cross-provider consistency artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_cross_provider_consistency import (
    FrontendCrossProviderConsistencySet,
)


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

    return paths


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


__all__ = [
    "frontend_cross_provider_consistency_root",
    "materialize_frontend_cross_provider_consistency_artifacts",
]
