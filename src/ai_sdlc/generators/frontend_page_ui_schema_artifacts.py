"""Frontend page/UI schema artifact instantiation helpers."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.models.frontend_page_ui_schema import (
    FrontendPageUiSchemaSet,
    PageSchemaDefinition,
    SchemaVersioningContract,
    UiSchemaDefinition,
    build_p2_frontend_page_ui_schema_baseline,
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

    return _dedupe_paths(output_paths)


def load_frontend_page_ui_schema_artifacts(root: Path) -> FrontendPageUiSchemaSet:
    """Load the canonical page/UI schema artifact set from disk."""

    artifact_root = frontend_page_ui_schema_root(root)
    baseline = build_p2_frontend_page_ui_schema_baseline()
    manifest = _read_yaml_mapping(artifact_root / "schema.manifest.yaml")
    versioning = _read_yaml_mapping(artifact_root / "schema-versioning.yaml")

    try:
        raw_page_schema_ids = manifest.get(
            "page_schemas",
            [page.page_schema_id for page in baseline.page_schemas],
        )
        raw_ui_schema_ids = manifest.get(
            "ui_schemas",
            [ui.ui_schema_id for ui in baseline.ui_schemas],
        )
        if not isinstance(raw_page_schema_ids, list):
            raise ValueError("page UI schema manifest `page_schemas` must be a list")
        if not isinstance(raw_ui_schema_ids, list):
            raise ValueError("page UI schema manifest `ui_schemas` must be a list")

        page_schemas = [
            PageSchemaDefinition.model_validate(
                _read_yaml_mapping(
                    artifact_root / "page-schemas" / f"{page_schema_id}.yaml"
                )
            )
            for page_schema_id in _dedupe_text_items(raw_page_schema_ids)
            if isinstance(page_schema_id, str) and page_schema_id
        ]
        ui_schemas = [
            UiSchemaDefinition.model_validate(
                _read_yaml_mapping(
                    artifact_root / "ui-schemas" / f"{ui_schema_id}.yaml"
                )
            )
            for ui_schema_id in _dedupe_text_items(raw_ui_schema_ids)
            if isinstance(ui_schema_id, str) and ui_schema_id
        ]

        schema_set = FrontendPageUiSchemaSet(
            work_item_id=str(manifest.get("work_item_id", baseline.work_item_id)),
            versioning=SchemaVersioningContract.model_validate(versioning),
            page_schemas=page_schemas,
            ui_schemas=ui_schemas,
        )
    except Exception as exc:  # pragma: no cover - surfaced in callers
        raise ValueError(
            f"invalid frontend page UI schema artifact set: {exc}"
        ) from exc
    return schema_set


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
        raise ValueError(f"missing frontend page UI schema artifact: {path.as_posix()}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(
            f"invalid frontend page UI schema artifact {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise ValueError(
            "invalid frontend page UI schema artifact "
            f"{path.as_posix()}: expected mapping"
        )
    return raw


__all__ = [
    "frontend_page_ui_schema_root",
    "load_frontend_page_ui_schema_artifacts",
    "materialize_frontend_page_ui_schema_artifacts",
]
