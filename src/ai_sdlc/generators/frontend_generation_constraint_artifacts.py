"""Frontend generation governance artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_generation_constraints import (
    FrontendGenerationConstraintSet,
)


def _dedupe_text_items(values: object) -> list[str]:
    deduped: list[str] = []
    for value in values or []:
        normalized = str(value).strip()
        if normalized and normalized not in deduped:
            deduped.append(normalized)
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


def frontend_generation_governance_root(root: Path) -> Path:
    """Return the canonical root for instantiated generation governance artifacts."""

    return root / "governance" / "frontend" / "generation"


def materialize_frontend_generation_constraint_artifacts(
    root: Path,
    constraints: FrontendGenerationConstraintSet,
) -> list[Path]:
    """Write the minimal frontend generation governance artifact set to disk."""

    base_dir = frontend_generation_governance_root(root)

    return _dedupe_paths([
        _write_yaml(
            base_dir / "generation.manifest.yaml",
            {
                "work_item_id": constraints.work_item_id,
                "effective_provider_id": constraints.effective_provider_id,
                "delivery_entry_id": constraints.delivery_entry_id,
                "component_library_packages": constraints.component_library_packages,
                "provider_theme_adapter_id": constraints.provider_theme_adapter_id,
                "page_schema_ids": constraints.page_schema_ids,
                "execution_order": constraints.execution_order,
            },
        ),
        _write_yaml(
            base_dir / "recipe.yaml",
            constraints.recipe.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            base_dir / "whitelist.yaml",
            constraints.whitelist.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            base_dir / "hard-rules.yaml",
            {
                "rules": [
                    rule.model_dump(mode="json", exclude_none=True)
                    for rule in constraints.hard_rules.rules
                ]
            },
        ),
        _write_yaml(
            base_dir / "token-rules.yaml",
            constraints.token_rules.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            base_dir / "exceptions.yaml",
            constraints.exceptions.model_dump(mode="json", exclude_none=True),
        ),
    ])


def load_frontend_generation_constraint_artifacts(
    root: Path,
) -> FrontendGenerationConstraintSet:
    """Load the canonical frontend generation governance artifact set from disk."""

    base_dir = frontend_generation_governance_root(root)
    manifest = _read_yaml_mapping(base_dir / "generation.manifest.yaml")
    recipe = _read_yaml_mapping(base_dir / "recipe.yaml")
    whitelist = _read_yaml_mapping(base_dir / "whitelist.yaml")
    hard_rules = _read_yaml_mapping(base_dir / "hard-rules.yaml")
    token_rules = _read_yaml_mapping(base_dir / "token-rules.yaml")
    exceptions = _read_yaml_mapping(base_dir / "exceptions.yaml")

    payload = {
        **manifest,
        "recipe": recipe,
        "whitelist": whitelist,
        "hard_rules": hard_rules,
        "token_rules": token_rules,
        "exceptions": exceptions,
    }
    payload["component_library_packages"] = _dedupe_text_items(
        payload.get("component_library_packages", ())
    )
    payload["page_schema_ids"] = _dedupe_text_items(payload.get("page_schema_ids", ()))
    payload["execution_order"] = list(payload.get("execution_order", ()))
    try:
        return FrontendGenerationConstraintSet.model_validate(payload)
    except Exception as exc:  # pragma: no cover - surfaced in caller assertions
        raise ValueError(f"invalid frontend generation artifact set: {exc}") from exc


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
        raise ValueError(f"missing frontend generation artifact: {path.as_posix()}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(
            f"invalid frontend generation artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            f"invalid frontend generation artifact {path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_generation_governance_root",
    "load_frontend_generation_constraint_artifacts",
    "materialize_frontend_generation_constraint_artifacts",
]
