"""Frontend theme token governance artifact instantiation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.models.frontend_theme_token_governance import (
    FrontendThemeTokenGovernanceSet,
)


def frontend_theme_token_governance_root(root: Path) -> Path:
    """Return the canonical root for theme/token governance artifacts."""

    return root / "governance" / "frontend" / "theme-token-governance"


def materialize_frontend_theme_token_governance_artifacts(
    root: Path,
    *,
    governance: FrontendThemeTokenGovernanceSet,
) -> list[Path]:
    """Write the minimal theme/token governance artifact set to disk."""

    artifact_root = frontend_theme_token_governance_root(root)
    manifest_payload = {
        "work_item_id": governance.work_item_id,
        "source_work_item_ids": governance.source_work_item_ids,
        "token_floor_disallowed_naked_values": governance.token_floor_disallowed_naked_values,
        "style_pack_ids": governance.style_pack_ids,
        "artifact_root": governance.handoff_contract.artifact_root,
        "schema_family": governance.handoff_contract.schema_family,
        "current_version": governance.handoff_contract.current_version,
    }
    token_mapping_payload = {
        "mappings": [
            mapping.model_dump(mode="json", exclude_none=True)
            for mapping in governance.token_mappings
        ]
    }
    override_policy_payload = {
        "override_precedence": governance.override_precedence,
        "custom_overrides": [
            override.model_dump(mode="json", exclude_none=True)
            for override in governance.custom_overrides
        ],
    }
    boundary_payload = governance.style_editor_boundary.model_dump(
        mode="json",
        exclude_none=True,
    )

    payloads = {
        "theme-governance-manifest.json": manifest_payload,
        "token-mapping.json": token_mapping_payload,
        "override-policy.json": override_policy_payload,
        "style-editor-boundary.json": boundary_payload,
    }
    return [
        _write_json(artifact_root / file_name, payload)
        for file_name, payload in payloads.items()
    ]


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


__all__ = [
    "frontend_theme_token_governance_root",
    "materialize_frontend_theme_token_governance_artifacts",
]
