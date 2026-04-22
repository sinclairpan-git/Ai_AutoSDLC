"""Frontend Provider profile artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_provider_profile import (
    EnterpriseVue2ProviderProfile,
    build_mvp_enterprise_vue2_provider_profile,
)
from ai_sdlc.models.frontend_solution_confirmation import (
    build_builtin_style_pack_manifests,
)

BUILTIN_FRONTEND_PROVIDER_PROFILE_IDS = frozenset(
    {"enterprise-vue2", "public-primevue"}
)


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def frontend_provider_profile_root(root: Path, provider_id: str) -> Path:
    """Return the canonical root for instantiated Provider profile artifacts."""

    return root / "providers" / "frontend" / provider_id


def materialize_frontend_provider_profile_artifacts(
    root: Path,
    profile: EnterpriseVue2ProviderProfile,
) -> list[Path]:
    """Write the minimal Provider profile artifact set to disk."""

    base_dir = frontend_provider_profile_root(root, profile.provider_id)

    return _dedupe_paths([
        _write_yaml(
            base_dir / "provider.manifest.yaml",
            {
                "work_item_id": profile.work_item_id,
                "provider_id": profile.provider_id,
                "kernel_artifact_ref": profile.kernel_artifact_ref,
                "access_mode": profile.access_mode,
                "install_strategy_ids": profile.install_strategy_ids,
                "availability_prerequisites": profile.availability_prerequisites,
                "default_style_pack_id": profile.default_style_pack_id,
                "mapped_components": [
                    mapping.component_id for mapping in profile.mappings
                ],
                "whitelist_components": [
                    entry.component_id for entry in profile.whitelist
                ],
                "cross_stack_fallback_targets": profile.cross_stack_fallback_targets,
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
        _write_yaml(
            base_dir / "style-support.yaml",
            {
                "items": [
                    entry.model_dump(mode="json", exclude_none=True)
                    for entry in profile.style_support_matrix
                ]
            },
        ),
    ])


def materialize_builtin_frontend_provider_profile_artifacts(
    root: Path,
    *,
    provider_id: str,
) -> list[Path]:
    """Write the minimal built-in provider artifact set required by verification."""

    if provider_id == "enterprise-vue2":
        return materialize_frontend_provider_profile_artifacts(
            root,
            build_mvp_enterprise_vue2_provider_profile(),
        )

    if provider_id == "public-primevue":
        base_dir = frontend_provider_profile_root(root, provider_id)
        return _dedupe_paths([
            _write_yaml(
                base_dir / "provider.manifest.yaml",
                {
                    "work_item_id": "073",
                    "provider_id": "public-primevue",
                    "kernel_artifact_ref": "kernel/frontend",
                    "access_mode": "public",
                    "install_strategy_ids": ["public-primevue-default"],
                    "availability_prerequisites": [],
                    "default_style_pack_id": "modern-saas",
                    "mapped_components": [],
                    "whitelist_components": [],
                    "cross_stack_fallback_targets": [],
                },
            ),
            _write_yaml(
                base_dir / "style-support.yaml",
                {
                    "items": [
                        {
                            "style_pack_id": manifest.style_pack_id,
                            "fidelity_status": "full",
                        }
                        for manifest in build_builtin_style_pack_manifests()
                    ]
                },
            ),
        ])

    raise ValueError(f"unsupported built-in provider profile: {provider_id}")


def supports_builtin_frontend_provider_profile_artifacts(provider_id: str) -> bool:
    """Return whether the provider has a built-in profile artifact materializer."""

    return provider_id in BUILTIN_FRONTEND_PROVIDER_PROFILE_IDS


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
    "BUILTIN_FRONTEND_PROVIDER_PROFILE_IDS",
    "frontend_provider_profile_root",
    "materialize_builtin_frontend_provider_profile_artifacts",
    "materialize_frontend_provider_profile_artifacts",
    "supports_builtin_frontend_provider_profile_artifacts",
]
