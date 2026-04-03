"""Frontend generation governance artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_generation_constraints import (
    FrontendGenerationConstraintSet,
)


def frontend_generation_governance_root(root: Path) -> Path:
    """Return the canonical root for instantiated generation governance artifacts."""

    return root / "governance" / "frontend" / "generation"


def materialize_frontend_generation_constraint_artifacts(
    root: Path,
    constraints: FrontendGenerationConstraintSet,
) -> list[Path]:
    """Write the minimal frontend generation governance artifact set to disk."""

    base_dir = frontend_generation_governance_root(root)

    return [
        _write_yaml(
            base_dir / "generation.manifest.yaml",
            {
                "work_item_id": constraints.work_item_id,
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
    "frontend_generation_governance_root",
    "materialize_frontend_generation_constraint_artifacts",
]
