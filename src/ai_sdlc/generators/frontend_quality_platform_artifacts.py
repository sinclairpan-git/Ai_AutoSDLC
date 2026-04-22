"""Frontend quality platform artifact instantiation helpers."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from ai_sdlc.models.frontend_quality_platform import (
    FrontendQualityPlatformSet,
    InteractionQualityFlow,
    QualityCoverageMatrixEntry,
    QualityEvidenceContract,
    QualityPlatformHandoffContract,
    QualityTruthSurfacingRecord,
    QualityVerdictEnvelope,
    build_p2_frontend_quality_platform_baseline,
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


def frontend_quality_platform_root(root: Path) -> Path:
    """Return the canonical root for quality platform artifacts."""

    return root / "governance" / "frontend" / "quality-platform"


def materialize_frontend_quality_platform_artifacts(
    root: Path,
    *,
    platform: FrontendQualityPlatformSet,
) -> list[Path]:
    """Write the minimal quality platform artifact set to disk."""

    artifact_root = frontend_quality_platform_root(root)
    paths = [
        _write_yaml(
            artifact_root / "quality-platform.manifest.yaml",
            {
                "work_item_id": platform.work_item_id,
                "source_work_item_ids": platform.source_work_item_ids,
                "artifact_root": platform.handoff_contract.artifact_root,
                "schema_family": platform.handoff_contract.schema_family,
                "current_version": platform.handoff_contract.current_version,
                "matrix_ids": [entry.matrix_id for entry in platform.coverage_matrix],
            },
        ),
        _write_yaml(
            artifact_root / "handoff.schema.yaml",
            platform.handoff_contract.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            artifact_root / "coverage-matrix.yaml",
            {
                "items": [
                    entry.model_dump(mode="json", exclude_none=True)
                    for entry in platform.coverage_matrix
                ]
            },
        ),
        _write_yaml(
            artifact_root / "evidence-platform.yaml",
            {
                "contracts": [
                    contract.model_dump(mode="json", exclude_none=True)
                    for contract in platform.evidence_contracts
                ]
            },
        ),
        _write_yaml(
            artifact_root / "interaction-quality.yaml",
            {
                "flows": [
                    flow.model_dump(mode="json", exclude_none=True)
                    for flow in platform.interaction_flows
                ]
            },
        ),
        _write_yaml(
            artifact_root / "truth-surfacing.yaml",
            {
                "items": [
                    record.model_dump(mode="json", exclude_none=True)
                    for record in platform.truth_surfacing_records
                ]
            },
        ),
    ]

    for verdict in platform.verdict_envelopes:
        paths.append(
            _write_yaml(
                artifact_root / "verdicts" / f"{verdict.verdict_id}.yaml",
                verdict.model_dump(mode="json", exclude_none=True),
            )
        )

    return _dedupe_paths(paths)


def load_frontend_quality_platform_artifacts(root: Path) -> FrontendQualityPlatformSet:
    """Load the canonical quality platform artifact set from disk."""

    artifact_root = frontend_quality_platform_root(root)
    baseline = build_p2_frontend_quality_platform_baseline()
    manifest = _read_yaml_mapping(artifact_root / "quality-platform.manifest.yaml")
    coverage_matrix = _read_yaml_mapping(artifact_root / "coverage-matrix.yaml")
    evidence_platform = _read_yaml_mapping(artifact_root / "evidence-platform.yaml")
    interaction_quality = _read_yaml_mapping(artifact_root / "interaction-quality.yaml")
    truth_surfacing = _read_yaml_mapping(artifact_root / "truth-surfacing.yaml")

    try:
        raw_matrix = coverage_matrix.get("items", [])
        if not isinstance(raw_matrix, list):
            raise ValueError("coverage matrix artifact `items` must be a list")
        raw_contracts = evidence_platform.get("contracts", [])
        if not isinstance(raw_contracts, list):
            raise ValueError("evidence platform artifact `contracts` must be a list")
        raw_flows = interaction_quality.get("flows", [])
        if not isinstance(raw_flows, list):
            raise ValueError("interaction quality artifact `flows` must be a list")
        raw_truth = truth_surfacing.get("items", [])
        if not isinstance(raw_truth, list):
            raise ValueError("truth surfacing artifact `items` must be a list")

        verdict_envelopes: list[QualityVerdictEnvelope] = []
        for verdict in baseline.verdict_envelopes:
            verdict_path = artifact_root / "verdicts" / f"{verdict.verdict_id}.yaml"
            if not verdict_path.is_file():
                raise ValueError(
                    "frontend quality platform verdict artifact missing: "
                    f"{verdict_path.as_posix()}"
                )
            verdict_envelopes.append(
                QualityVerdictEnvelope.model_validate(_read_yaml_mapping(verdict_path))
            )

        platform = FrontendQualityPlatformSet(
            work_item_id=str(manifest.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=_dedupe_text_items(
                manifest.get("source_work_item_ids", baseline.source_work_item_ids)
            ),
            coverage_matrix=[
                QualityCoverageMatrixEntry.model_validate(item)
                for item in _dedupe_mapping_items(raw_matrix)
            ],
            evidence_contracts=[
                QualityEvidenceContract.model_validate(item)
                for item in _dedupe_mapping_items(raw_contracts)
            ],
            interaction_flows=[
                InteractionQualityFlow.model_validate(item)
                for item in _dedupe_mapping_items(raw_flows)
            ],
            verdict_envelopes=verdict_envelopes,
            truth_surfacing_records=[
                QualityTruthSurfacingRecord.model_validate(item)
                for item in _dedupe_mapping_items(raw_truth)
            ],
            handoff_contract=QualityPlatformHandoffContract(
                schema_family=str(
                    manifest.get(
                        "schema_family",
                        baseline.handoff_contract.schema_family,
                    )
                ),
                current_version=str(
                    manifest.get(
                        "current_version",
                        baseline.handoff_contract.current_version,
                    )
                ),
                compatible_versions=_dedupe_text_items(
                    [
                        manifest.get(
                            "current_version",
                            baseline.handoff_contract.current_version,
                        )
                    ]
                ),
                artifact_root=str(
                    manifest.get(
                        "artifact_root",
                        baseline.handoff_contract.artifact_root,
                    )
                ),
                canonical_files=list(baseline.handoff_contract.canonical_files),
                program_service_fields=list(baseline.handoff_contract.program_service_fields),
                cli_fields=list(baseline.handoff_contract.cli_fields),
                verify_fields=list(baseline.handoff_contract.verify_fields),
            ),
        )
    except Exception as exc:  # pragma: no cover - surfaced in callers
        raise ValueError(f"invalid frontend quality platform artifact set: {exc}") from exc
    return platform


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
        raise ValueError(f"missing frontend quality platform artifact: {path.as_posix()}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(
            f"invalid frontend quality platform artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            f"invalid frontend quality platform artifact {path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_quality_platform_root",
    "load_frontend_quality_platform_artifacts",
    "materialize_frontend_quality_platform_artifacts",
]
