"""Frontend provider runtime adapter artifact instantiation helpers."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from ai_sdlc.models.frontend_provider_runtime_adapter import (
    AdapterScaffoldContract,
    FrontendProviderRuntimeAdapterSet,
    ProviderRuntimeAdapterHandoffContract,
    ProviderRuntimeAdapterTarget,
    RuntimeBoundaryReceipt,
    build_p3_target_project_adapter_scaffold_baseline,
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


def frontend_provider_runtime_adapter_root(root: Path) -> Path:
    """Return the canonical root for provider runtime adapter artifacts."""

    return root / "governance" / "frontend" / "provider-runtime-adapter"


def materialize_frontend_provider_runtime_adapter_artifacts(
    root: Path,
    *,
    runtime_adapter: FrontendProviderRuntimeAdapterSet,
) -> list[Path]:
    """Write the minimal provider runtime adapter artifact set to disk."""

    artifact_root = frontend_provider_runtime_adapter_root(root)
    paths = [
        _write_yaml(
            artifact_root / "provider-runtime-adapter.manifest.yaml",
            {
                "work_item_id": runtime_adapter.work_item_id,
                "source_work_item_ids": runtime_adapter.source_work_item_ids,
                "artifact_root": runtime_adapter.handoff_contract.artifact_root,
                "schema_family": runtime_adapter.handoff_contract.schema_family,
                "provider_ids": [
                    target.provider_id for target in runtime_adapter.adapter_targets
                ],
            },
        ),
        _write_yaml(
            artifact_root / "handoff.schema.yaml",
            runtime_adapter.handoff_contract.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            artifact_root / "adapter-targets.yaml",
            {
                "items": [
                    {
                        "provider_id": target.provider_id,
                        "target_frontend_stack": target.boundary_receipt.target_frontend_stack,
                        "carrier_mode": target.boundary_receipt.carrier_mode,
                        "runtime_delivery_state": target.boundary_receipt.runtime_delivery_state,
                        "evidence_return_state": target.boundary_receipt.evidence_return_state,
                        "certification_gate": target.boundary_receipt.certification_gate,
                        "scaffold_id": target.scaffold_contract.scaffold_id,
                    }
                    for target in runtime_adapter.adapter_targets
                ]
            },
        ),
    ]

    for target in runtime_adapter.adapter_targets:
        provider_root = artifact_root / "providers" / target.provider_id
        paths.extend(
            [
                _write_yaml(
                    provider_root / "adapter-scaffold.yaml",
                    target.scaffold_contract.model_dump(mode="json", exclude_none=True),
                ),
                _write_yaml(
                    provider_root / "runtime-boundary-receipt.yaml",
                    target.boundary_receipt.model_dump(mode="json", exclude_none=True),
                ),
            ]
        )

    return _dedupe_paths(paths)


def load_frontend_provider_runtime_adapter_artifacts(
    root: Path,
) -> FrontendProviderRuntimeAdapterSet:
    """Load the canonical provider runtime adapter artifact set from disk."""

    artifact_root = frontend_provider_runtime_adapter_root(root)
    baseline = build_p3_target_project_adapter_scaffold_baseline()
    manifest = _read_yaml_mapping(artifact_root / "provider-runtime-adapter.manifest.yaml")
    handoff_schema = _read_yaml_mapping(artifact_root / "handoff.schema.yaml")
    adapter_targets = _read_yaml_mapping(artifact_root / "adapter-targets.yaml")

    try:
        provider_ids = manifest.get(
            "provider_ids",
            [target.provider_id for target in baseline.adapter_targets],
        )
        if not isinstance(provider_ids, list):
            raise ValueError(
                "provider runtime adapter manifest `provider_ids` must be a list"
            )
        provider_ids = _dedupe_text_items(provider_ids)

        raw_target_items = adapter_targets.get("items", [])
        if not isinstance(raw_target_items, list):
            raise ValueError("adapter targets artifact `items` must be a list")
        targets_by_provider_id = {
            item.get("provider_id"): item
            for item in raw_target_items
            if isinstance(item, dict) and item.get("provider_id")
        }

        targets: list[ProviderRuntimeAdapterTarget] = []
        for provider_id in provider_ids:
            if not isinstance(provider_id, str) or not provider_id:
                raise ValueError(
                    "provider runtime adapter manifest `provider_ids` contains invalid item"
                )
            provider_root = artifact_root / "providers" / provider_id
            scaffold = _read_yaml_mapping(provider_root / "adapter-scaffold.yaml")
            boundary_receipt = _read_yaml_mapping(
                provider_root / "runtime-boundary-receipt.yaml"
            )
            target_summary = targets_by_provider_id.get(provider_id, {})
            targets.append(
                ProviderRuntimeAdapterTarget(
                    provider_id=provider_id,
                    scaffold_contract=AdapterScaffoldContract.model_validate(
                        {
                            **scaffold,
                            "required_layer_ids": _dedupe_text_items(
                                scaffold.get("required_layer_ids", ())
                            ),
                            "files": _dedupe_mapping_items(scaffold.get("files", ())),
                            "boundary_violation_codes": _dedupe_text_items(
                                scaffold.get("boundary_violation_codes", ())
                            ),
                        }
                    ),
                    boundary_receipt=RuntimeBoundaryReceipt.model_validate(
                        {
                            **boundary_receipt,
                            "provider_id": boundary_receipt.get("provider_id", provider_id),
                            "source_work_item_ids": _dedupe_text_items(
                                boundary_receipt.get("source_work_item_ids", ())
                            ),
                            "boundary_constraints": _dedupe_text_items(
                                boundary_receipt.get("boundary_constraints", ())
                            ),
                            "carrier_mode": boundary_receipt.get(
                                "carrier_mode",
                                target_summary.get("carrier_mode"),
                            ),
                            "runtime_delivery_state": boundary_receipt.get(
                                "runtime_delivery_state",
                                target_summary.get("runtime_delivery_state"),
                            ),
                            "evidence_return_state": boundary_receipt.get(
                                "evidence_return_state",
                                target_summary.get("evidence_return_state"),
                            ),
                        }
                    ),
                )
            )

        runtime_adapter = FrontendProviderRuntimeAdapterSet(
            work_item_id=str(manifest.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=_dedupe_text_items(
                manifest.get("source_work_item_ids", baseline.source_work_item_ids)
            ),
            adapter_targets=targets,
            handoff_contract=ProviderRuntimeAdapterHandoffContract(
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
            f"invalid frontend provider runtime adapter artifact set: {exc}"
        ) from exc
    return runtime_adapter


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
            f"missing frontend provider runtime adapter artifact: {path.as_posix()}"
        )
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(
            f"invalid frontend provider runtime adapter artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            "invalid frontend provider runtime adapter artifact "
            f"{path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_provider_runtime_adapter_root",
    "load_frontend_provider_runtime_adapter_artifacts",
    "materialize_frontend_provider_runtime_adapter_artifacts",
]
