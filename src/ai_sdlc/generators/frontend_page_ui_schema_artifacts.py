"""Frontend page/UI schema artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_page_ui_schema import FrontendPageUiSchemaSet


def frontend_page_ui_schema_root(root: Path) -> Path:
    """Return the canonical root for page/UI schema artifacts."""

    return root / "kernel" / "frontend" / "page-ui-schema"


def materialize_frontend_page_ui_schema_artifacts(
    root: Path,
    schema_set: FrontendPageUiSchemaSet,
) -> list[Path]:
    """Write the canonical page/UI schema artifact set to disk."""

    base_dir = frontend_page_ui_schema_root(root)
    output_paths = [
        _write_yaml(
            base_dir / "schema.manifest.yaml",
            {
                "work_item_id": schema_set.work_item_id,
                "schema_family": schema_set.versioning.schema_family,
                "current_version": schema_set.versioning.current_version,
                "page_schemas": [
                    page.page_schema_id for page in schema_set.page_schemas
                ],
                "ui_schemas": [ui.ui_schema_id for ui in schema_set.ui_schemas],
            },
        ),
        _write_yaml(
            base_dir / "schema-versioning.yaml",
            schema_set.versioning.model_dump(mode="json", exclude_none=True),
        ),
    ]

    for page_schema in schema_set.page_schemas:
        output_paths.append(
            _write_yaml(
                base_dir / "page-schemas" / f"{page_schema.page_schema_id}.yaml",
                page_schema.model_dump(mode="json", exclude_none=True),
            )
        )

    for ui_schema in schema_set.ui_schemas:
        output_paths.append(
            _write_yaml(
                base_dir / "ui-schemas" / f"{ui_schema.ui_schema_id}.yaml",
                ui_schema.model_dump(mode="json", exclude_none=True),
            )
        )

    return output_paths


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
    "frontend_page_ui_schema_root",
    "materialize_frontend_page_ui_schema_artifacts",
]
