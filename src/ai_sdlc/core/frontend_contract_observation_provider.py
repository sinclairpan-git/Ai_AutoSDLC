"""Frontend contract observation provider artifact helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation

FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME = "frontend-contract-observations.json"
FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION = "frontend-contract-observations/v1"
FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED = "attached"
FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT = "missing_artifact"
FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT = "invalid_artifact"


@dataclass(frozen=True, slots=True)
class ObservationProviderProvenance:
    """Structured provenance for one observation artifact producer."""

    provider_kind: str
    provider_name: str
    provider_version: str | None = None
    source_ref: str | None = None


@dataclass(frozen=True, slots=True)
class ObservationFreshnessMarker:
    """Structured freshness marker for one observation artifact."""

    generated_at: str
    source_digest: str | None = None
    source_revision: str | None = None


@dataclass(frozen=True, slots=True)
class FrontendContractObservationArtifact:
    """Canonical provider artifact envelope for structured frontend observations."""

    schema_version: str
    provenance: ObservationProviderProvenance
    freshness: ObservationFreshnessMarker
    observations: tuple[PageImplementationObservation, ...]

    def to_json_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "provenance": {
                "provider_kind": self.provenance.provider_kind,
                "provider_name": self.provenance.provider_name,
                "provider_version": self.provenance.provider_version,
                "source_ref": self.provenance.source_ref,
            },
            "freshness": {
                "generated_at": self.freshness.generated_at,
                "source_digest": self.freshness.source_digest,
                "source_revision": self.freshness.source_revision,
            },
            "observations": [
                {
                    "page_id": observation.page_id,
                    "recipe_id": observation.recipe_id,
                    "i18n_keys": list(observation.i18n_keys),
                    "validation_fields": list(observation.validation_fields),
                    "new_legacy_usages": list(observation.new_legacy_usages),
                }
                for observation in self.observations
            ],
        }


def observation_artifact_path(spec_dir: Path) -> Path:
    """Return the canonical observation artifact path for one spec directory."""

    return spec_dir / FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME


def build_frontend_contract_observation_artifact(
    *,
    observations: list[PageImplementationObservation],
    provider_kind: str,
    provider_name: str,
    generated_at: str,
    provider_version: str | None = None,
    source_ref: str | None = None,
    source_digest: str | None = None,
    source_revision: str | None = None,
) -> FrontendContractObservationArtifact:
    """Build the canonical observation artifact envelope."""

    provenance = ObservationProviderProvenance(
        provider_kind=_require_non_empty_text(provider_kind, "provider_kind"),
        provider_name=_require_non_empty_text(provider_name, "provider_name"),
        provider_version=_optional_text(provider_version, "provider_version"),
        source_ref=_optional_text(source_ref, "source_ref"),
    )
    freshness = ObservationFreshnessMarker(
        generated_at=_require_non_empty_text(generated_at, "generated_at"),
        source_digest=_optional_text(source_digest, "source_digest"),
        source_revision=_optional_text(source_revision, "source_revision"),
    )
    return FrontendContractObservationArtifact(
        schema_version=FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION,
        provenance=provenance,
        freshness=freshness,
        observations=tuple(_coerce_observations(observations)),
    )


def write_frontend_contract_observation_artifact(
    spec_dir: Path,
    artifact: FrontendContractObservationArtifact,
) -> Path:
    """Write one canonical observation artifact into a spec directory."""

    path = observation_artifact_path(spec_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact.to_json_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_frontend_contract_observation_artifact(
    path: Path,
) -> FrontendContractObservationArtifact:
    """Load and validate one canonical observation artifact file."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON ({exc.msg})") from exc

    if not isinstance(raw, dict):
        raise ValueError("expected top-level observation artifact object")

    schema_version = _require_mapping_text(raw, "schema_version", context="artifact")
    if schema_version != FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION:
        raise ValueError(
            "unsupported schema_version "
            f"{schema_version!r}; expected {FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION!r}"
        )

    provenance_raw = _require_mapping(raw, "provenance", context="artifact")
    freshness_raw = _require_mapping(raw, "freshness", context="artifact")
    observations_raw = raw.get("observations")
    if not isinstance(observations_raw, list):
        raise ValueError("artifact.observations must be a list")

    observations: list[PageImplementationObservation] = []
    for index, item in enumerate(observations_raw):
        if not isinstance(item, dict):
            raise ValueError(f"observations[{index}] must be an object")
        try:
            observations.append(PageImplementationObservation(**item))
        except TypeError as exc:
            raise ValueError(f"observations[{index}] invalid: {exc}") from exc

    return FrontendContractObservationArtifact(
        schema_version=schema_version,
        provenance=ObservationProviderProvenance(
            provider_kind=_require_mapping_text(
                provenance_raw,
                "provider_kind",
                context="provenance",
            ),
            provider_name=_require_mapping_text(
                provenance_raw,
                "provider_name",
                context="provenance",
            ),
            provider_version=_optional_mapping_text(
                provenance_raw,
                "provider_version",
                context="provenance",
            ),
            source_ref=_optional_mapping_text(
                provenance_raw,
                "source_ref",
                context="provenance",
            ),
        ),
        freshness=ObservationFreshnessMarker(
            generated_at=_require_mapping_text(
                freshness_raw,
                "generated_at",
                context="freshness",
            ),
            source_digest=_optional_mapping_text(
                freshness_raw,
                "source_digest",
                context="freshness",
            ),
            source_revision=_optional_mapping_text(
                freshness_raw,
                "source_revision",
                context="freshness",
            ),
        ),
        observations=tuple(observations),
    )


def _coerce_observations(
    observations: list[PageImplementationObservation],
) -> list[PageImplementationObservation]:
    items: list[PageImplementationObservation] = []
    for index, observation in enumerate(observations):
        if not isinstance(observation, PageImplementationObservation):
            raise ValueError(
                "observations must contain PageImplementationObservation items; "
                f"item {index} was {type(observation).__name__}"
            )
        items.append(observation)
    return items


def _require_mapping(
    value: dict[str, object],
    field_name: str,
    *,
    context: str,
) -> dict[str, object]:
    nested = value.get(field_name)
    if not isinstance(nested, dict):
        raise ValueError(f"{context}.{field_name} must be an object")
    return nested


def _require_mapping_text(
    value: dict[str, object],
    field_name: str,
    *,
    context: str,
) -> str:
    return _require_non_empty_text(value.get(field_name), f"{context}.{field_name}")


def _optional_mapping_text(
    value: dict[str, object],
    field_name: str,
    *,
    context: str,
) -> str | None:
    return _optional_text(value.get(field_name), f"{context}.{field_name}")


def _require_non_empty_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string when provided")
    text = value.strip()
    return text or None


__all__ = [
    "FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_NAME",
    "FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_ATTACHED",
    "FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_INVALID_ARTIFACT",
    "FRONTEND_CONTRACT_OBSERVATION_ARTIFACT_STATUS_MISSING_ARTIFACT",
    "FRONTEND_CONTRACT_OBSERVATION_SCHEMA_VERSION",
    "FrontendContractObservationArtifact",
    "ObservationFreshnessMarker",
    "ObservationProviderProvenance",
    "build_frontend_contract_observation_artifact",
    "load_frontend_contract_observation_artifact",
    "observation_artifact_path",
    "write_frontend_contract_observation_artifact",
]
