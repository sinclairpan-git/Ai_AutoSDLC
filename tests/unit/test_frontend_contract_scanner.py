"""Unit tests for frontend contract scanner candidate helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
    load_frontend_contract_observation_artifact,
)
from ai_sdlc.scanners.frontend_contract_scanner import (
    FRONTEND_CONTRACT_OBSERVATION_MARKER,
    FRONTEND_CONTRACT_SCANNER_PROVIDER_KIND,
    FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME,
    build_frontend_contract_scanner_artifact,
    scan_frontend_contract_observations,
    write_frontend_contract_scanner_artifact,
)

SAMPLE_FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "frontend-contract-sample-src"
)


def test_scan_frontend_contract_observations_reads_structured_comment_blocks(
    tmp_path,
) -> None:
    src = tmp_path / "src" / "pages"
    src.mkdir(parents=True)
    (src / "UserCreate.vue").write_text(
        """
        <template><div /></template>
        <!-- ai-sdlc:frontend-contract-observation
        {
          "page_id": "user-create",
          "recipe_id": "form-create",
          "i18n_keys": ["user.create.submit"],
          "validation_fields": ["username"]
        }
        -->
        """,
        encoding="utf-8",
    )
    (src / "AccountEdit.tsx").write_text(
        """
        /* ai-sdlc:frontend-contract-observation
        {
          "page_id": "account-edit",
          "recipe_id": "form-edit",
          "i18n_keys": ["account.edit.save"],
          "validation_fields": ["email"],
          "new_legacy_usages": ["window.legacyModal.open"]
        }
        */
        export function AccountEdit() { return null; }
        """,
        encoding="utf-8",
    )

    result = scan_frontend_contract_observations(tmp_path)

    assert result.matched_files == (
        "src/pages/AccountEdit.tsx",
        "src/pages/UserCreate.vue",
    )
    assert [item.page_id for item in result.observations] == [
        "account-edit",
        "user-create",
    ]
    assert result.observations[0].new_legacy_usages == ["window.legacyModal.open"]
    assert result.observations[1].validation_fields == ["username"]


def test_build_frontend_contract_scanner_artifact_sets_scanner_provenance(
    tmp_path,
) -> None:
    (tmp_path / "frontend.ts").write_text(
        """
        /* ai-sdlc:frontend-contract-observation
        {
          "page_id": "user-create",
          "recipe_id": "form-create",
          "i18n_keys": ["user.create.submit"],
          "validation_fields": ["username"]
        }
        */
        """,
        encoding="utf-8",
    )

    artifact = build_frontend_contract_scanner_artifact(
        tmp_path,
        generated_at="2026-04-02T13:30:00Z",
        source_revision="HEAD",
    )

    assert artifact.provenance.provider_kind == FRONTEND_CONTRACT_SCANNER_PROVIDER_KIND
    assert artifact.provenance.provider_name == FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME
    assert artifact.provenance.source_ref == str(tmp_path)
    assert artifact.freshness.generated_at == "2026-04-02T13:30:00Z"
    assert artifact.freshness.source_revision == "HEAD"
    assert artifact.freshness.source_digest is not None
    assert artifact.freshness.source_digest.startswith("sha256:")
    assert [item.page_id for item in artifact.observations] == ["user-create"]


def test_write_frontend_contract_scanner_artifact_materializes_canonical_file(
    tmp_path,
) -> None:
    source_root = tmp_path / "workspace"
    source_root.mkdir()
    (source_root / "page.tsx").write_text(
        """
        /* ai-sdlc:frontend-contract-observation
        {
          "page_id": "account-edit",
          "recipe_id": "form-edit",
          "validation_fields": ["email"]
        }
        */
        """,
        encoding="utf-8",
    )
    spec_dir = tmp_path / "specs" / "013-frontend-contract-observation-provider-baseline"

    artifact_path = write_frontend_contract_scanner_artifact(
        source_root,
        spec_dir,
        generated_at="2026-04-02T13:45:00Z",
    )
    loaded = load_frontend_contract_observation_artifact(artifact_path)

    assert artifact_path.name == "frontend-contract-observations.json"
    assert [item.page_id for item in loaded.observations] == ["account-edit"]
    assert loaded.provenance.provider_name == FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME


def test_scan_frontend_contract_observations_rejects_duplicate_page_ids(
    tmp_path,
) -> None:
    first = tmp_path / "src" / "first.ts"
    first.parent.mkdir(parents=True)
    first.write_text(
        """
        /* ai-sdlc:frontend-contract-observation
        {"page_id":"user-create","recipe_id":"form-create"}
        */
        """,
        encoding="utf-8",
    )
    (tmp_path / "src" / "second.ts").write_text(
        """
        /* ai-sdlc:frontend-contract-observation
        {"page_id":"user-create","recipe_id":"form-edit"}
        */
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate page_id"):
        scan_frontend_contract_observations(tmp_path)


def test_scan_frontend_contract_observations_rejects_invalid_json_block(
    tmp_path,
) -> None:
    (tmp_path / "broken.vue").write_text(
        """
        <!-- ai-sdlc:frontend-contract-observation
        {"page_id":"user-create","recipe_id":
        -->
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid JSON"):
        scan_frontend_contract_observations(tmp_path)


def test_scan_frontend_contract_observations_ignores_unmarked_files(
    tmp_path,
) -> None:
    (tmp_path / "plain.tsx").write_text(
        "export function PlainPage() { return null; }\n",
        encoding="utf-8",
    )

    result = scan_frontend_contract_observations(tmp_path)

    assert result.observations == ()
    assert result.matched_files == ()
    assert FRONTEND_CONTRACT_OBSERVATION_MARKER == "ai-sdlc:frontend-contract-observation"


def test_repository_sample_match_fixture_scans_expected_observations() -> None:
    source_root = SAMPLE_FIXTURE_ROOT / "match"

    assert source_root.is_dir()

    result = scan_frontend_contract_observations(source_root)

    assert result.matched_files == ("AccountEdit.tsx", "UserCreate.vue")
    assert [item.page_id for item in result.observations] == [
        "account-edit",
        "user-create",
    ]
    assert result.observations[0].new_legacy_usages == ["window.legacyModal.open"]
    assert result.observations[1].i18n_keys == [
        "user.create.title",
        "user.create.submit",
    ]
    assert result.observations[1].validation_fields == ["username", "email"]


def test_repository_sample_drift_fixture_scans_expected_mismatch_observation() -> None:
    source_root = SAMPLE_FIXTURE_ROOT / "drift"

    assert source_root.is_dir()

    result = scan_frontend_contract_observations(source_root)

    assert result.matched_files == ("UserCreate.vue",)
    assert [item.page_id for item in result.observations] == ["user-create"]
    assert result.observations[0].recipe_id == "form-edit"
    assert result.observations[0].i18n_keys == ["user.create.submit"]
    assert result.observations[0].validation_fields == ["username"]


def test_write_frontend_contract_scanner_artifact_from_empty_fixture_keeps_stable_envelope(
    tmp_path,
) -> None:
    source_root = SAMPLE_FIXTURE_ROOT / "empty"
    spec_dir = tmp_path / "specs" / "065-frontend-contract-sample-source-selfcheck-baseline"

    assert source_root.is_dir()

    artifact_path = write_frontend_contract_scanner_artifact(
        source_root,
        spec_dir,
        generated_at="2026-04-06T12:00:00Z",
    )
    loaded = load_frontend_contract_observation_artifact(artifact_path)

    expected_json = {
        "schema_version": FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
        "provenance": {
            "provider_kind": FRONTEND_CONTRACT_SCANNER_PROVIDER_KIND,
            "provider_name": FRONTEND_CONTRACT_SCANNER_PROVIDER_NAME,
            "provider_version": None,
            "source_ref": str(source_root),
        },
        "freshness": {
            "generated_at": "2026-04-06T12:00:00Z",
            "source_digest": f"sha256:{hashlib.sha256().hexdigest()}",
            "source_revision": None,
        },
        "observations": [],
    }

    assert loaded.observations == ()
    assert loaded.to_json_dict() == expected_json
    assert artifact_path.read_text(encoding="utf-8") == (
        json.dumps(expected_json, ensure_ascii=False, indent=2) + "\n"
    )
