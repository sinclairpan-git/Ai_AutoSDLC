"""Frontend provider runtime adapter artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_provider_runtime_adapter import (
    FrontendProviderRuntimeAdapterSet,
)


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
    "frontend_provider_runtime_adapter_root",
    "materialize_frontend_provider_runtime_adapter_artifacts",
]
