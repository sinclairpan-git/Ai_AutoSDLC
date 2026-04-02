"""Unit tests for frontend contract observation provider helpers."""

from __future__ import annotations

import json

import pytest

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME,
    FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
    build_frontend_contract_observation_artifact,
    load_frontend_contract_observation_artifact,
    observation_artifact_path,
    write_frontend_contract_observation_artifact,
)


def test_write_and_load_frontend_contract_observation_artifact_round_trips(
    tmp_path,
) -> None:
    spec_dir = tmp_path / "specs" / "013-frontend-contract-observation-provider-baseline"
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
                i18n_keys=["user.create.submit"],
                validation_fields=["username"],
            )
        ],
        provider_kind="scanner",
        provider_name="frontend-contract-scanner",
        provider_version="0.1.0",
        generated_at="2026-04-02T12:00:00Z",
        source_digest="sha256:provider-input",
        source_ref="src/pages/user-create.vue",
    )

    artifact_path = write_frontend_contract_observation_artifact(spec_dir, artifact)
    loaded = load_frontend_contract_observation_artifact(artifact_path)

    assert artifact_path == spec_dir / FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME
    assert loaded == artifact

    raw = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert raw["schema_version"] == FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION
    assert raw["provenance"]["provider_kind"] == "scanner"
    assert raw["freshness"]["source_digest"] == "sha256:provider-input"


def test_observation_artifact_path_uses_canonical_filename(tmp_path) -> None:
    spec_dir = tmp_path / "specs" / "013-demo"

    path = observation_artifact_path(spec_dir)

    assert path == spec_dir / FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME


def test_load_frontend_contract_observation_artifact_requires_provenance(
    tmp_path,
) -> None:
    artifact_path = tmp_path / FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
                "freshness": {"generated_at": "2026-04-02T12:00:00Z"},
                "observations": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="provenance"):
        load_frontend_contract_observation_artifact(artifact_path)


def test_load_frontend_contract_observation_artifact_requires_freshness_generated_at(
    tmp_path,
) -> None:
    artifact_path = tmp_path / FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
                "provenance": {
                    "provider_kind": "manual",
                    "provider_name": "contract-export",
                },
                "freshness": {},
                "observations": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="generated_at"):
        load_frontend_contract_observation_artifact(artifact_path)


def test_load_frontend_contract_observation_artifact_rejects_invalid_observation_shape(
    tmp_path,
) -> None:
    artifact_path = tmp_path / FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
                "provenance": {
                    "provider_kind": "export_tool",
                    "provider_name": "manual-export",
                },
                "freshness": {"generated_at": "2026-04-02T12:00:00Z"},
                "observations": [{"page_id": "user-create"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="observations\\[0\\] invalid"):
        load_frontend_contract_observation_artifact(artifact_path)
