"""Frontend theme token governance artifact instantiation helpers."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.models.frontend_theme_token_governance import (
    CustomThemeTokenOverride,
    FrontendThemeTokenGovernanceSet,
    StyleEditorBoundaryContract,
    ThemeGovernanceHandoffContract,
    ThemeTokenMapping,
    build_p2_frontend_theme_token_governance_baseline,
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
    return _dedupe_paths([
        _write_json(artifact_root / file_name, payload)
        for file_name, payload in payloads.items()
    ])


def load_frontend_theme_token_governance_artifacts(
    root: Path,
) -> FrontendThemeTokenGovernanceSet:
    """Load the canonical theme/token governance artifact set from disk."""

    artifact_root = frontend_theme_token_governance_root(root)
    baseline = build_p2_frontend_theme_token_governance_baseline()
    manifest = _read_json_mapping(artifact_root / "theme-governance-manifest.json")
    token_mapping = _read_json_mapping(artifact_root / "token-mapping.json")
    override_policy = _read_json_mapping(artifact_root / "override-policy.json")
    boundary = _read_json_mapping(artifact_root / "style-editor-boundary.json")

    try:
        raw_mappings = token_mapping.get("mappings", [])
        if not isinstance(raw_mappings, list):
            raise ValueError("token mapping artifact `mappings` must be a list")
        raw_overrides = override_policy.get("custom_overrides", [])
        if not isinstance(raw_overrides, list):
            raise ValueError("override policy artifact `custom_overrides` must be a list")
        governance = FrontendThemeTokenGovernanceSet(
            work_item_id=str(manifest.get("work_item_id", baseline.work_item_id)),
            source_work_item_ids=_dedupe_text_items(
                manifest.get("source_work_item_ids", baseline.source_work_item_ids)
            ),
            token_floor_disallowed_naked_values=_dedupe_text_items(
                manifest.get(
                    "token_floor_disallowed_naked_values",
                    baseline.token_floor_disallowed_naked_values,
                )
            ),
            style_pack_ids=_dedupe_text_items(
                manifest.get("style_pack_ids", baseline.style_pack_ids)
            ),
            override_precedence=_dedupe_text_items(
                override_policy.get(
                    "override_precedence",
                    baseline.override_precedence,
                )
            ),
            token_mappings=[
                ThemeTokenMapping.model_validate(item)
                for item in _dedupe_mapping_items(raw_mappings)
            ],
            custom_overrides=[
                CustomThemeTokenOverride.model_validate(item)
                for item in _dedupe_mapping_items(raw_overrides)
            ],
            style_editor_boundary=StyleEditorBoundaryContract.model_validate(boundary),
            handoff_contract=ThemeGovernanceHandoffContract(
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
            ),
        )
    except Exception as exc:  # pragma: no cover - surfaced in callers
        raise ValueError(
            f"invalid frontend theme token governance artifact set: {exc}"
        ) from exc
    return governance


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _read_json_mapping(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise ValueError(
            f"missing frontend theme token governance artifact: {path.as_posix()}"
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid frontend theme token governance artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            "invalid frontend theme token governance artifact "
            f"{path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_theme_token_governance_root",
    "load_frontend_theme_token_governance_artifacts",
    "materialize_frontend_theme_token_governance_artifacts",
]
