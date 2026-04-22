"""Frontend provider expansion artifact instantiation helpers."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from ai_sdlc.models.frontend_provider_expansion import (
    ChoiceSurfacePolicy,
    FrontendProviderExpansionSet,
    PairCertificationReference,
    ProviderAdmissionBundle,
    ProviderCertificationAggregate,
    ProviderExpansionHandoffContract,
    ProviderExpansionTruthSurfacingRecord,
    ReactExposureBoundary,
    build_p3_frontend_provider_expansion_baseline,
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

    return _dedupe_paths(paths)


def load_frontend_provider_expansion_artifacts(root: Path) -> FrontendProviderExpansionSet:
    """Load the canonical provider expansion artifact set from disk."""

    artifact_root = frontend_provider_expansion_root(root)
    baseline = build_p3_frontend_provider_expansion_baseline()
    manifest = _read_yaml_mapping(artifact_root / "provider-expansion.manifest.yaml")
    handoff_schema = _read_yaml_mapping(artifact_root / "handoff.schema.yaml")
    truth_surfacing = _read_yaml_mapping(artifact_root / "truth-surfacing.yaml")
    choice_surface_policy = _read_yaml_mapping(artifact_root / "choice-surface-policy.yaml")
    react_boundary = _read_yaml_mapping(artifact_root / "react-exposure-boundary.yaml")

    try:
        raw_truth_items = truth_surfacing.get("items", [])
        if not isinstance(raw_truth_items, list):
            raise ValueError("truth surfacing artifact `items` must be a list")

        provider_ids = manifest.get(
            "provider_ids",
            [provider.provider_id for provider in baseline.providers],
        )
        if not isinstance(provider_ids, list):
            raise ValueError("provider expansion manifest `provider_ids` must be a list")
        provider_ids = _dedupe_text_items(provider_ids)

        providers: list[ProviderAdmissionBundle] = []
        for provider_id in provider_ids:
            if not isinstance(provider_id, str) or not provider_id:
                raise ValueError("provider expansion manifest `provider_ids` contains invalid item")
            provider_root = artifact_root / "providers" / provider_id
            admission = _read_yaml_mapping(provider_root / "admission.yaml")
            roster_state = _read_yaml_mapping(provider_root / "roster-state.yaml")
            certification_ref = _read_yaml_mapping(provider_root / "certification-ref.yaml")
            certification_aggregate = _read_yaml_mapping(
                provider_root / "provider-certification-aggregate.yaml"
            )

            raw_pairs = certification_ref.get("items", [])
            if not isinstance(raw_pairs, list):
                raise ValueError("certification ref artifact `items` must be a list")
            pair_refs = [
                PairCertificationReference.model_validate(item)
                for item in _dedupe_mapping_items(raw_pairs)
            ]
            aggregate_payload = dict(certification_aggregate)
            aggregate_payload["pair_certifications"] = [
                item.model_dump(mode="json", exclude_none=True) for item in pair_refs
            ]
            aggregate = ProviderCertificationAggregate.model_validate(
                aggregate_payload
            )
            if aggregate.provider_id != str(admission.get("provider_id", provider_id)):
                raise ValueError(
                    "provider certification aggregate provider_id must match admission"
                )
            if aggregate.pair_certifications != pair_refs:
                raise ValueError(
                    "provider certification aggregate pair_certifications must match certification ref"
                )
            if str(
                roster_state.get(
                    "roster_admission_state",
                    admission.get("roster_admission_state", "candidate"),
                )
            ) != str(admission.get("roster_admission_state", "candidate")):
                raise ValueError(
                    "roster-state roster_admission_state must match admission"
                )
            if str(
                roster_state.get(
                    "choice_surface_visibility",
                    admission.get("choice_surface_visibility", "hidden"),
                )
            ) != str(admission.get("choice_surface_visibility", "hidden")):
                raise ValueError(
                    "roster-state choice_surface_visibility must match admission"
                )

            providers.append(
                ProviderAdmissionBundle(
                    provider_id=str(admission.get("provider_id", provider_id)),
                    certification_aggregate=aggregate,
                    roster_admission_state=str(
                        admission.get("roster_admission_state", "candidate")
                    ),
                    choice_surface_visibility=str(
                        admission.get("choice_surface_visibility", "hidden")
                    ),
                    caveat_codes=_dedupe_text_items(
                        admission.get("caveat_codes", ())
                    ),
                    artifact_root_ref=str(
                        admission.get(
                            "artifact_root_ref",
                            baseline.handoff_contract.artifact_root,
                        )
                    ),
                )
            )

        expansion = FrontendProviderExpansionSet(
            work_item_id=str(manifest.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=_dedupe_text_items(
                manifest.get("source_work_item_ids", baseline.source_work_item_ids)
            ),
            choice_surface_policy=ChoiceSurfacePolicy.model_validate(
                choice_surface_policy
            ),
            providers=providers,
            react_exposure_boundary=ReactExposureBoundary.model_validate(react_boundary),
            truth_surfacing_records=[
                ProviderExpansionTruthSurfacingRecord.model_validate(item)
                for item in _dedupe_mapping_items(raw_truth_items)
            ],
            handoff_contract=ProviderExpansionHandoffContract(
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
            f"invalid frontend provider expansion artifact set: {exc}"
        ) from exc
    return expansion


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
        raise ValueError(f"missing frontend provider expansion artifact: {path.as_posix()}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(
            f"invalid frontend provider expansion artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            "invalid frontend provider expansion artifact "
            f"{path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_provider_expansion_root",
    "load_frontend_provider_expansion_artifacts",
    "materialize_frontend_provider_expansion_artifacts",
]
