"""Frontend UI Kernel artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_ui_kernel import FrontendUiKernelSet, PageRecipeStandard


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def frontend_ui_kernel_root(root: Path) -> Path:
    """Return the canonical root for instantiated UI Kernel artifacts."""

    return root / "kernel" / "frontend"


def materialize_frontend_ui_kernel_artifacts(
    root: Path,
    kernel_set: FrontendUiKernelSet,
) -> list[Path]:
    """Write the minimal UI Kernel artifact set to disk."""

    base_dir = frontend_ui_kernel_root(root)
    output_paths = [
        _write_yaml(
            base_dir / "kernel.manifest.yaml",
            {
                "work_item_id": kernel_set.work_item_id,
                "format_version": kernel_set.format_version,
                "semantic_components": [
                    component.component_id for component in kernel_set.semantic_components
                ],
                "page_recipes": [
                    recipe.recipe_id for recipe in kernel_set.page_recipes
                ],
            },
        ),
        _write_yaml(
            base_dir / "semantic-components.yaml",
            {
                "items": [
                    component.model_dump(mode="json", exclude_none=True)
                    for component in kernel_set.semantic_components
                ]
            },
        ),
        _write_yaml(
            base_dir / "state-baseline.yaml",
            kernel_set.state_baseline.model_dump(mode="json", exclude_none=True),
        ),
        _write_yaml(
            base_dir / "interaction-baseline.yaml",
            kernel_set.interaction_baseline.model_dump(mode="json", exclude_none=True),
        ),
    ]

    for recipe in kernel_set.page_recipes:
        output_paths.append(_write_page_recipe(base_dir, recipe))
    return _dedupe_paths(output_paths)


def _write_page_recipe(base_dir: Path, recipe: PageRecipeStandard) -> Path:
    return _write_yaml(
        base_dir / "page-recipes" / f"{recipe.recipe_id}.yaml",
        recipe.model_dump(mode="json", exclude_none=True),
    )


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
    "frontend_ui_kernel_root",
    "materialize_frontend_ui_kernel_artifacts",
]
