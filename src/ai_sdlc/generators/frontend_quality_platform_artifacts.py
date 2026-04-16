"""Frontend quality platform artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_quality_platform import FrontendQualityPlatformSet


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
    "frontend_quality_platform_root",
    "materialize_frontend_quality_platform_artifacts",
]
