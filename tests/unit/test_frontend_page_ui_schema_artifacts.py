"""Unit tests for frontend page/UI schema artifact materialization."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.generators.frontend_page_ui_schema_artifacts import (
    frontend_page_ui_schema_root,
    materialize_frontend_page_ui_schema_artifacts,
)
from ai_sdlc.models.frontend_page_ui_schema import (
    build_p2_frontend_page_ui_schema_baseline,
)


def _read_yaml(path: Path) -> dict[str, object]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_page_ui_schema_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    schema_set = build_p2_frontend_page_ui_schema_baseline()

    paths = materialize_frontend_page_ui_schema_artifacts(tmp_path, schema_set)
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "kernel/frontend/page-ui-schema/schema.manifest.yaml",
        "kernel/frontend/page-ui-schema/schema-versioning.yaml",
        "kernel/frontend/page-ui-schema/page-schemas/dashboard-workspace.yaml",
        "kernel/frontend/page-ui-schema/page-schemas/search-list-workspace.yaml",
        "kernel/frontend/page-ui-schema/page-schemas/wizard-workspace.yaml",
        "kernel/frontend/page-ui-schema/ui-schemas/dashboard-workspace-default.yaml",
        "kernel/frontend/page-ui-schema/ui-schemas/search-list-workspace-default.yaml",
        "kernel/frontend/page-ui-schema/ui-schemas/wizard-workspace-default.yaml",
    }


def test_frontend_page_ui_schema_artifacts_preserve_manifest_and_schema_payloads(
    tmp_path,
) -> None:
    schema_set = build_p2_frontend_page_ui_schema_baseline()

    materialize_frontend_page_ui_schema_artifacts(tmp_path, schema_set)

    schema_root = frontend_page_ui_schema_root(tmp_path)
    manifest = _read_yaml(schema_root / "schema.manifest.yaml")
    versioning = _read_yaml(schema_root / "schema-versioning.yaml")
    dashboard_page = _read_yaml(schema_root / "page-schemas" / "dashboard-workspace.yaml")
    search_ui = _read_yaml(
        schema_root / "ui-schemas" / "search-list-workspace-default.yaml"
    )

    assert manifest == {
        "work_item_id": "147",
        "schema_family": "frontend-page-ui-schema",
        "current_version": "1.0",
        "page_schemas": [
            "dashboard-workspace",
            "search-list-workspace",
            "wizard-workspace",
        ],
        "ui_schemas": [
            "dashboard-workspace-default",
            "search-list-workspace-default",
            "wizard-workspace-default",
        ],
    }
    assert versioning["compatible_versions"] == ["1.0"]
    assert dashboard_page["page_recipe_id"] == "DashboardPage"
    assert dashboard_page["primary_anchor_id"] == "page-shell"
    assert [anchor["anchor_id"] for anchor in dashboard_page["section_anchors"]] == [
        "page-shell",
        "page-header",
        "summary-band",
        "filter-scope",
        "main-insight",
        "secondary-section",
        "state-feedback",
    ]
    assert search_ui["root_slot_id"] == "page-shell"
    assert [slot["slot_id"] for slot in search_ui["render_slots"]] == [
        "page-shell",
        "page-header",
        "search-area",
        "result-summary",
        "content-area",
        "pagination-area",
        "state-feedback",
    ]


def test_frontend_page_ui_schema_root_is_stable(tmp_path) -> None:
    assert frontend_page_ui_schema_root(tmp_path) == (
        tmp_path / "kernel" / "frontend" / "page-ui-schema"
    )
