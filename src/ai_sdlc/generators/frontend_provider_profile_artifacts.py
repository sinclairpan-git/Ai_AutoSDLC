"""enterprise-vue2 Provider profile artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_provider_profile import EnterpriseVue2ProviderProfile


def frontend_provider_profile_root(root: Path, provider_id: str) -> Path:
    """Return the canonical root for instantiated Provider profile artifacts."""

    return root / "providers" / "frontend" / provider_id


def materialize_frontend_provider_profile_artifacts(
    root: Path,
    profile: EnterpriseVue2ProviderProfile,
) -> list[Path]:
    """Write the minimal Provider profile artifact set to disk."""

    base_dir = frontend_provider_profile_root(root, profile.provider_id)

    return [
        _write_yaml(
            base_dir / "provider.manifest.yaml",
            {
                "work_item_id": profile.work_item_id,
                "provider_id": profile.provider_id,
                "kernel_artifact_ref": profile.kernel_artifact_ref,
                "mapped_components": [
                    mapping.component_id for mapping in profile.mappings
                ],
                "whitelist_components": [
                    entry.component_id for entry in profile.whitelist
                ],
            },
        ),
        _write_yaml(
            base_dir / "mappings.yaml",
            {
                "items": [
                    mapping.model_dump(mode="json", exclude_none=True)
                    for mapping in profile.mappings
                ]
            },
        ),
        _write_yaml(
            base_dir / "whitelist.yaml",
            {
                "items": [
                    entry.model_dump(mode="json", exclude_none=True)
                    for entry in profile.whitelist
                ]
            },
        ),
        _write_yaml(
            base_dir / "risk-isolation.yaml",
            profile.risk_isolation.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            base_dir / "legacy-adapter.yaml",
            profile.legacy_adapter.model_dump(mode="json", exclude_none=True),
        ),
    ]


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
    "frontend_provider_profile_root",
    "materialize_frontend_provider_profile_artifacts",
]
