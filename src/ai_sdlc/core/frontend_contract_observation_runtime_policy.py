"""Runtime policy helpers for frontend contract observation artifact sources."""

from __future__ import annotations

from dataclasses import dataclass

from ai_sdlc.core.frontend_contract_observation_provider import (
    FrontendContractObservationArtifact,
)

FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_SAMPLE_SELFCHECK = "sample_selfcheck"
FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_CONSUMER_EVIDENCE = "consumer_evidence"
FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_OPAQUE = "opaque"

FRONTEND_CONTRACT_OBSERVATION_SOURCE_REQUIREMENT_ALLOWED = "allowed"
FRONTEND_CONTRACT_OBSERVATION_SOURCE_REQUIREMENT_SAMPLE_SELFCHECK_ONLY = (
    "sample_selfcheck_only"
)

_SAMPLE_SELFCHECK_WORK_ITEM_PREFIXES = (
    "012",
    "018",
)
_SAMPLE_FIXTURE_SEGMENT = "/tests/fixtures/frontend-contract-sample-src/"


@dataclass(frozen=True, slots=True)
class FrontendContractObservationSourceAssessment:
    """Resolved runtime assessment for one observation artifact source."""

    source_profile: str
    requirement_state: str
    issue_message: str | None = None


def classify_frontend_contract_observation_source(
    artifact: FrontendContractObservationArtifact,
) -> str:
    """Classify one canonical observation artifact into a runtime source profile."""

    provider_kind = artifact.provenance.provider_kind.strip()
    source_ref = _normalize_source_ref(artifact.provenance.source_ref)
    if _looks_like_sample_fixture_source_ref(source_ref):
        return FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_SAMPLE_SELFCHECK
    if provider_kind == "scanner" and source_ref:
        return FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_CONSUMER_EVIDENCE
    return FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_OPAQUE


def assess_frontend_contract_observation_source(
    artifact: FrontendContractObservationArtifact,
    *,
    work_item_id: str,
) -> FrontendContractObservationSourceAssessment:
    """Assess whether an observation artifact source profile is acceptable at runtime."""

    source_profile = classify_frontend_contract_observation_source(artifact)
    if (
        source_profile == FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_SAMPLE_SELFCHECK
        and not _allows_sample_selfcheck_for_work_item(work_item_id)
    ):
        return FrontendContractObservationSourceAssessment(
            source_profile=source_profile,
            requirement_state=(
                FRONTEND_CONTRACT_OBSERVATION_SOURCE_REQUIREMENT_SAMPLE_SELFCHECK_ONLY
            ),
            issue_message=(
                "sample self-check observation artifact cannot satisfy this spec; "
                "materialize consumer evidence from a real frontend source root"
            ),
        )
    return FrontendContractObservationSourceAssessment(
        source_profile=source_profile,
        requirement_state=FRONTEND_CONTRACT_OBSERVATION_SOURCE_REQUIREMENT_ALLOWED,
    )


def _allows_sample_selfcheck_for_work_item(work_item_id: str) -> bool:
    normalized = (work_item_id or "").strip()
    return normalized.startswith(_SAMPLE_SELFCHECK_WORK_ITEM_PREFIXES)


def _looks_like_sample_fixture_source_ref(source_ref: str) -> bool:
    if not source_ref:
        return False
    normalized = f"/{source_ref.strip('/')}/"
    return _SAMPLE_FIXTURE_SEGMENT in normalized


def _normalize_source_ref(source_ref: str | None) -> str:
    if not source_ref:
        return ""
    return source_ref.replace("\\", "/").strip()


__all__ = [
    "FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_CONSUMER_EVIDENCE",
    "FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_OPAQUE",
    "FRONTEND_CONTRACT_OBSERVATION_SOURCE_PROFILE_SAMPLE_SELFCHECK",
    "FRONTEND_CONTRACT_OBSERVATION_SOURCE_REQUIREMENT_ALLOWED",
    "FRONTEND_CONTRACT_OBSERVATION_SOURCE_REQUIREMENT_SAMPLE_SELFCHECK_ONLY",
    "FrontendContractObservationSourceAssessment",
    "assess_frontend_contract_observation_source",
    "classify_frontend_contract_observation_source",
]
