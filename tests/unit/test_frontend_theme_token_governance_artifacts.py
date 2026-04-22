"""Unit tests for frontend theme token governance artifact materialization."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import ai_sdlc.generators.frontend_theme_token_governance_artifacts as frontend_theme_token_governance_artifacts_module
from ai_sdlc.generators.frontend_theme_token_governance_artifacts import (
    frontend_theme_token_governance_root,
    load_frontend_theme_token_governance_artifacts,
    materialize_frontend_theme_token_governance_artifacts,
)
from ai_sdlc.models.frontend_theme_token_governance import (
    build_p2_frontend_theme_token_governance_baseline,
)


def _read_json(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError(f"expected mapping payload in {path}")
    return raw


def test_materialize_frontend_theme_token_governance_artifacts_writes_expected_file_set(
    tmp_path,
) -> None:
    paths = materialize_frontend_theme_token_governance_artifacts(
        tmp_path,
        governance=build_p2_frontend_theme_token_governance_baseline(),
    )
    rel_paths = {path.relative_to(tmp_path).as_posix() for path in paths}

    assert rel_paths == {
        "governance/frontend/theme-token-governance/override-policy.json",
        "governance/frontend/theme-token-governance/style-editor-boundary.json",
        "governance/frontend/theme-token-governance/theme-governance-manifest.json",
        "governance/frontend/theme-token-governance/token-mapping.json",
    }


def test_theme_token_governance_artifacts_preserve_reference_only_payloads(
    tmp_path,
) -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    materialize_frontend_theme_token_governance_artifacts(
        tmp_path,
        governance=governance,
    )

    artifact_root = frontend_theme_token_governance_root(tmp_path)
    manifest = _read_json(artifact_root / "theme-governance-manifest.json")
    token_mapping = _read_json(artifact_root / "token-mapping.json")
    override_policy = _read_json(artifact_root / "override-policy.json")
    boundary = _read_json(artifact_root / "style-editor-boundary.json")

    assert manifest["work_item_id"] == "148"
    assert manifest["source_work_item_ids"] == ["017", "073", "147"]
    assert manifest["artifact_root"] == "governance/frontend/theme-token-governance"
    assert override_policy["override_precedence"] == [
        "global",
        "page",
        "section",
        "slot",
    ]
    assert boundary["surface_mode"] == "read_only_diagnostics_structured_proposal"
    assert all(
        token_ref.startswith("style-pack:")
        for mapping in token_mapping["mappings"]
        for token_ref in mapping["token_refs"].values()
    )


def test_frontend_theme_token_governance_root_is_stable(tmp_path) -> None:
    assert frontend_theme_token_governance_root(tmp_path) == (
        tmp_path / "governance" / "frontend" / "theme-token-governance"
    )


def test_load_frontend_theme_token_governance_artifacts_round_trips_materialized_truth(
    tmp_path,
) -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    materialize_frontend_theme_token_governance_artifacts(
        tmp_path,
        governance=governance,
    )

    loaded = load_frontend_theme_token_governance_artifacts(tmp_path)

    assert loaded == governance


def test_load_frontend_theme_token_governance_artifacts_deduplicates_repeated_source_entries(
    tmp_path,
) -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    materialize_frontend_theme_token_governance_artifacts(
        tmp_path,
        governance=governance,
    )

    artifact_root = frontend_theme_token_governance_root(tmp_path)
    manifest_path = artifact_root / "theme-governance-manifest.json"
    manifest = _read_json(manifest_path)
    manifest["source_work_item_ids"] = ["017", "017", "073", "147"]
    manifest["token_floor_disallowed_naked_values"] = ["hex-color", "hex-color", "rgb-color"]
    manifest["style_pack_ids"] = [
        *governance.style_pack_ids,
        governance.style_pack_ids[0],
    ]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    mapping_path = artifact_root / "token-mapping.json"
    mapping = _read_json(mapping_path)
    first_mapping = copy.deepcopy(mapping["mappings"][0])
    mapping["mappings"] = [first_mapping, copy.deepcopy(first_mapping), *mapping["mappings"][1:]]
    mapping_path.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    override_path = artifact_root / "override-policy.json"
    override = _read_json(override_path)
    first_override = copy.deepcopy(override["custom_overrides"][0])
    override["override_precedence"] = [
        "global",
        "page",
        "section",
        "slot",
        "slot",
    ]
    override["custom_overrides"] = [
        first_override,
        copy.deepcopy(first_override),
        *override["custom_overrides"][1:],
    ]
    override_path.write_text(
        json.dumps(override, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    loaded = load_frontend_theme_token_governance_artifacts(tmp_path)

    assert loaded.source_work_item_ids == ["017", "073", "147"]
    assert loaded.token_floor_disallowed_naked_values == ["hex-color", "rgb-color"]
    assert loaded.style_pack_ids == governance.style_pack_ids
    assert loaded.override_precedence == ["global", "page", "section", "slot"]
    assert len(loaded.token_mappings) == len(governance.token_mappings)
    assert len(loaded.custom_overrides) == len(governance.custom_overrides)


def test_materialize_frontend_theme_token_governance_artifacts_deduplicates_returned_paths(
    tmp_path,
    monkeypatch,
) -> None:
    governance = build_p2_frontend_theme_token_governance_baseline()
    repeated_path = (
        tmp_path / "governance" / "frontend" / "theme-token-governance" / "theme-governance-manifest.json"
    )

    monkeypatch.setattr(
        frontend_theme_token_governance_artifacts_module,
        "_write_json",
        lambda path, payload: repeated_path,
    )

    paths = materialize_frontend_theme_token_governance_artifacts(
        tmp_path,
        governance=governance,
    )

    rel_paths = [path.relative_to(tmp_path).as_posix() for path in paths]
    assert rel_paths == list(dict.fromkeys(rel_paths))
