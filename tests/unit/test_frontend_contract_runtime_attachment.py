"""Unit tests for frontend contract runtime attachment helpers."""

from __future__ import annotations

import json
from pathlib import Path

from ai_sdlc.context.state import save_checkpoint
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    observation_artifact_path,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.frontend_contract_runtime_attachment import (
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_TIMESTAMP_ONLY,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_EXPLICIT_SPEC_DIR,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_SCOPE,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_SCOPE_OUTSIDE_ROOT,
    FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_WRITE_POLICY_EXPLICIT_OPT_IN,
    FrontendContractRuntimeAttachment,
    FrontendContractRuntimeAttachmentScope,
    build_frontend_contract_runtime_attachment,
    resolve_frontend_contract_runtime_attachment_scope,
)
from ai_sdlc.models.state import Checkpoint, FeatureInfo


def test_resolve_runtime_attachment_scope_from_checkpoint(tmp_path: Path) -> None:
    spec_dir = tmp_path / "specs" / "014-demo"
    save_checkpoint(
        tmp_path,
        _checkpoint_with_spec_dir("specs/014-demo"),
    )

    scope = resolve_frontend_contract_runtime_attachment_scope(tmp_path)

    assert scope.scope_source == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT
    assert scope.spec_dir == spec_dir
    assert scope.work_item_id == "014-demo"
    assert scope.blockers == ()


def test_build_runtime_attachment_prefers_explicit_spec_dir_and_loads_artifact(
    tmp_path: Path,
) -> None:
    save_checkpoint(
        tmp_path,
        _checkpoint_with_spec_dir("specs/014-other"),
    )
    spec_dir = tmp_path / "specs" / "014-helper"
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
        generated_at="2026-04-03T09:00:00Z",
        source_digest="sha256:runtime-attachment",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)

    attachment = build_frontend_contract_runtime_attachment(
        tmp_path,
        explicit_spec_dir=spec_dir,
        allow_artifact_write=True,
    )

    assert (
        attachment.scope.scope_source
        == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_EXPLICIT_SPEC_DIR
    )
    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
    assert attachment.artifact_path == observation_artifact_path(spec_dir)
    assert attachment.observations == artifact.observations
    assert attachment.allow_artifact_write is True
    assert (
        attachment.write_policy
        == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_WRITE_POLICY_EXPLICIT_OPT_IN
    )
    assert attachment.blockers == ()


def test_build_runtime_attachment_classifies_sample_selfcheck_source_profile(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "001-auth"
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
            )
        ],
        provider_kind="scanner",
        provider_name="frontend_contract_scanner",
        generated_at="2026-04-14T07:00:00Z",
        source_ref="tests/fixtures/frontend-contract-sample-src/match",
        source_digest="sha256:sample-selfcheck",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)

    attachment = build_frontend_contract_runtime_attachment(
        tmp_path,
        explicit_spec_dir=spec_dir,
    )

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
    assert attachment.observation_source_profile == "sample_selfcheck"
    assert attachment.observation_source_requirement == "sample_selfcheck_only"
    assert attachment.observation_source_issue is not None
    assert "sample self-check observation artifact cannot satisfy this spec" in (
        attachment.observation_source_issue
    )


def test_build_runtime_attachment_allows_sample_selfcheck_for_012_scope(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "012-frontend-contract-verify-integration"
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
            )
        ],
        provider_kind="scanner",
        provider_name="frontend_contract_scanner",
        generated_at="2026-04-14T07:05:00Z",
        source_ref="tests/fixtures/frontend-contract-sample-src/match",
        source_digest="sha256:sample-selfcheck-012",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)

    attachment = build_frontend_contract_runtime_attachment(
        tmp_path,
        explicit_spec_dir=spec_dir,
    )

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
    assert attachment.observation_source_profile == "sample_selfcheck"
    assert attachment.observation_source_requirement == "allowed"
    assert attachment.observation_source_issue is None


def test_build_runtime_attachment_flags_manual_sample_source_ref_as_sample_selfcheck(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "001-auth"
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id="user-create",
                recipe_id="form-create",
            )
        ],
        provider_kind="manual",
        provider_name="fixture-export",
        generated_at="2026-04-14T07:10:00Z",
        source_ref="tests/fixtures/frontend-contract-sample-src/match",
        source_digest="sha256:manual-sample-selfcheck",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)

    attachment = build_frontend_contract_runtime_attachment(
        tmp_path,
        explicit_spec_dir=spec_dir,
    )

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
    assert attachment.observation_source_profile == "sample_selfcheck"
    assert attachment.observation_source_requirement == "sample_selfcheck_only"
    assert attachment.observation_source_issue is not None


def test_build_runtime_attachment_requires_scope(tmp_path: Path) -> None:
    attachment = build_frontend_contract_runtime_attachment(tmp_path)

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_SCOPE
    assert attachment.artifact_path is None
    assert attachment.coverage_gaps == ("frontend_contract_runtime_scope",)
    assert "active spec_dir is unresolved" in attachment.blockers[0]


def test_build_runtime_attachment_reports_missing_artifact_honestly(
    tmp_path: Path,
) -> None:
    save_checkpoint(
        tmp_path,
        _checkpoint_with_spec_dir("specs/014-demo"),
    )

    attachment = build_frontend_contract_runtime_attachment(tmp_path)

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT
    assert attachment.artifact_path == observation_artifact_path(
        tmp_path / "specs" / "014-demo"
    )
    assert attachment.coverage_gaps == ("frontend_contract_observations",)
    assert "missing canonical observation artifact" in attachment.blockers[0]


def test_runtime_attachment_to_json_dict_deduplicates_lists() -> None:
    payload = FrontendContractRuntimeAttachment(
        status="missing_artifact",
        scope=FrontendContractRuntimeAttachmentScope(
            spec_dir=None,
            scope_source="checkpoint",
            work_item_id="014-demo",
            blockers=("scope blocker", "scope blocker"),
        ),
        artifact_path=None,
        artifact=None,
        blockers=("attachment blocker", "attachment blocker"),
        advisories=("attachment advisory", "attachment advisory"),
        coverage_gaps=("frontend_contract_observations", "frontend_contract_observations"),
    ).to_json_dict()

    assert payload["scope"]["blockers"] == ["scope blocker"]
    assert payload["blockers"] == ["attachment blocker"]
    assert payload["advisories"] == ["attachment advisory"]
    assert payload["coverage_gaps"] == ["frontend_contract_observations"]


def test_runtime_attachment_runtime_objects_canonicalize_lists() -> None:
    scope = FrontendContractRuntimeAttachmentScope(
        spec_dir=None,
        scope_source="checkpoint",
        work_item_id="014-demo",
        blockers=("scope blocker", "scope blocker"),
    )
    attachment = FrontendContractRuntimeAttachment(
        status="missing_artifact",
        scope=scope,
        artifact_path=None,
        artifact=None,
        blockers=("attachment blocker", "attachment blocker"),
        advisories=("attachment advisory", "attachment advisory"),
        coverage_gaps=("frontend_contract_observations", "frontend_contract_observations"),
    )

    assert scope.blockers == ("scope blocker",)
    assert attachment.blockers == ("attachment blocker",)
    assert attachment.advisories == ("attachment advisory",)
    assert attachment.coverage_gaps == ("frontend_contract_observations",)


def test_build_runtime_attachment_reports_invalid_artifact_honestly(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "014-demo"
    spec_dir.mkdir(parents=True)
    save_checkpoint(
        tmp_path,
        _checkpoint_with_spec_dir("specs/014-demo"),
    )
    artifact_path = observation_artifact_path(spec_dir)
    artifact_path.write_text(
        json.dumps(
            {
                "schema_version": "frontend-contract-observations/v999",
                "provenance": {
                    "provider_kind": "scanner",
                    "provider_name": "frontend-contract-scanner",
                },
                "freshness": {"generated_at": "2026-04-03T09:00:00Z"},
                "observations": [],
            }
        ),
        encoding="utf-8",
    )

    attachment = build_frontend_contract_runtime_attachment(tmp_path)

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT
    assert attachment.coverage_gaps == ("frontend_contract_observations",)
    assert "invalid structured observation input" in attachment.blockers[0]


def test_build_runtime_attachment_flags_timestamp_only_freshness(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "014-demo"
    save_checkpoint(
        tmp_path,
        _checkpoint_with_spec_dir("specs/014-demo"),
    )
    artifact = build_frontend_contract_observation_artifact(
        observations=[],
        provider_kind="manual",
        provider_name="manual-export",
        generated_at="2026-04-03T09:30:00Z",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)

    attachment = build_frontend_contract_runtime_attachment(tmp_path)

    assert attachment.status == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED
    assert (
        attachment.freshness_status
        == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_TIMESTAMP_ONLY
    )
    assert attachment.coverage_gaps == ("frontend_contract_observation_freshness",)
    assert "timestamp-only" in attachment.advisories[0]


def test_build_runtime_attachment_rejects_explicit_spec_dir_outside_root(
    tmp_path: Path,
) -> None:
    outside_spec_dir = tmp_path.parent / "014-outside"
    outside_spec_dir.mkdir(parents=True, exist_ok=True)

    attachment = build_frontend_contract_runtime_attachment(
        tmp_path,
        explicit_spec_dir=outside_spec_dir,
    )

    assert (
        attachment.status
        == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_SCOPE_OUTSIDE_ROOT
    )
    assert attachment.artifact_path is None
    assert attachment.coverage_gaps == ("frontend_contract_runtime_scope",)
    assert "outside project root" in attachment.blockers[0]


def _checkpoint_with_spec_dir(spec_dir: str) -> Checkpoint:
    return Checkpoint(
        current_stage="execute",
        feature=FeatureInfo(
            id=Path(spec_dir).name,
            spec_dir=spec_dir,
            design_branch="design/demo",
            feature_branch="feature/demo",
            current_branch="feature/demo",
        ),
    )
