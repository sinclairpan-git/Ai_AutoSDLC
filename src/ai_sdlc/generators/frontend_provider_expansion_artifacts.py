"""Frontend provider expansion artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_provider_expansion import FrontendProviderExpansionSet


def frontend_provider_expansion_root(root: Path) -> Path:
    """Return the canonical root for provider expansion artifacts."""

    return root / "governance" / "frontend" / "provider-expansion"


def materialize_frontend_provider_expansion_artifacts(
    root: Path,
    *,
    expansion: FrontendProviderExpansionSet,
) -> list[Path]:
    """Write the minimal provider expansion artifact set to disk."""

    artifact_root = frontend_provider_expansion_root(root)
    paths = [
        _write_yaml(
            artifact_root / "provider-expansion.manifest.yaml",
            {
                "work_item_id": expansion.work_item_id,
                "source_work_item_ids": expansion.source_work_item_ids,
                "artifact_root": expansion.handoff_contract.artifact_root,
                "schema_family": expansion.handoff_contract.schema_family,
                "current_version": expansion.handoff_contract.current_version,
                "provider_ids": [
                    provider.provider_id for provider in expansion.providers
                ],
            },
        ),
        _write_yaml(
            artifact_root / "handoff.schema.yaml",
            expansion.handoff_contract.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            artifact_root / "truth-surfacing.yaml",
            {
                "items": [
                    record.model_dump(mode="json", exclude_none=True)
                    for record in expansion.truth_surfacing_records
                ]
            },
        ),
        _write_yaml(
            artifact_root / "choice-surface-policy.yaml",
            expansion.choice_surface_policy.model_dump(
                mode="json",
                exclude_none=True,
            ),
        ),
        _write_yaml(
            artifact_root / "react-exposure-boundary.yaml",
            expansion.react_exposure_boundary.model_dump(
                mode="json",
                exclude_none=True,
            ),
        ),
    ]

    for provider in expansion.providers:
        provider_root = artifact_root / "providers" / provider.provider_id
        paths.extend(
            [
                _write_yaml(
                    provider_root / "admission.yaml",
                    {
                        "provider_id": provider.provider_id,
                        "certification_gate": provider.certification_gate,
                        "roster_admission_state": provider.roster_admission_state,
                        "choice_surface_visibility": provider.choice_surface_visibility,
                        "caveat_codes": provider.caveat_codes,
                        "artifact_root_ref": provider.artifact_root_ref,
                    },
                ),
                _write_yaml(
                    provider_root / "roster-state.yaml",
                    {
                        "provider_id": provider.provider_id,
                        "roster_admission_state": provider.roster_admission_state,
                        "choice_surface_visibility": provider.choice_surface_visibility,
                    },
                ),
                _write_yaml(
                    provider_root / "certification-ref.yaml",
                    {
                        "provider_id": provider.provider_id,
                        "items": [
                            pair.model_dump(mode="json", exclude_none=True)
                            for pair in provider.certification_aggregate.pair_certifications
                        ],
                    },
                ),
                _write_yaml(
                    provider_root / "provider-certification-aggregate.yaml",
                    provider.certification_aggregate.model_dump(
                        mode="json",
                        exclude_none=True,
                    ),
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
    "frontend_provider_expansion_root",
    "materialize_frontend_provider_expansion_artifacts",
]
