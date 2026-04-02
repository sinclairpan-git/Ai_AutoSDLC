"""Frontend contract runtime attachment helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ai_sdlc.context.state import load_checkpoint
from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    FrontendContractObservationArtifact,
    load_frontend_contract_observation_artifact,
    observation_artifact_path,
)
from ai_sdlc.models.state import Checkpoint

FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT = "checkpoint"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_EXPLICIT_SPEC_DIR = "explicit_spec_dir"

FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED = "attached"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_SCOPE = "missing_scope"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_SCOPE_OUTSIDE_ROOT = "scope_outside_root"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT = "missing_artifact"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT = "invalid_artifact"

FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_UNKNOWN = "unknown"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_VERIFIABLE = "verifiable"
FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_TIMESTAMP_ONLY = "timestamp_only"

FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_WRITE_POLICY_EXPLICIT_OPT_IN = (
    "explicit_opt_in_required"
)


@dataclass(frozen=True, slots=True)
class FrontendContractRuntimeAttachmentScope:
    """Resolved scope for runtime attachment."""

    spec_dir: Path | None
    scope_source: str
    work_item_id: str
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class FrontendContractRuntimeAttachment:
    """Resolved runtime attachment state for one active spec scope."""

    status: str
    scope: FrontendContractRuntimeAttachmentScope
    artifact_path: Path | None
    artifact: FrontendContractObservationArtifact | None
    blockers: tuple[str, ...] = ()
    advisories: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    freshness_status: str = FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_UNKNOWN
    allow_artifact_write: bool = False
    write_policy: str = FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_WRITE_POLICY_EXPLICIT_OPT_IN

    @property
    def observations(self) -> tuple[PageImplementationObservation, ...]:
        if self.artifact is None:
            return ()
        return self.artifact.observations


def resolve_frontend_contract_runtime_attachment_scope(
    root: Path,
    *,
    checkpoint: Checkpoint | None = None,
    explicit_spec_dir: Path | str | None = None,
) -> FrontendContractRuntimeAttachmentScope:
    """Resolve the active spec scope for frontend contract runtime attachment."""

    resolved_root = root.resolve()
    if explicit_spec_dir is not None:
        return _resolve_explicit_scope(resolved_root, explicit_spec_dir)

    effective_checkpoint = checkpoint or load_checkpoint(resolved_root)
    return _resolve_checkpoint_scope(resolved_root, effective_checkpoint)


def build_frontend_contract_runtime_attachment(
    root: Path,
    *,
    checkpoint: Checkpoint | None = None,
    explicit_spec_dir: Path | str | None = None,
    allow_artifact_write: bool = False,
) -> FrontendContractRuntimeAttachment:
    """Build the read-mostly runtime attachment state for one active spec scope."""

    scope = resolve_frontend_contract_runtime_attachment_scope(
        root,
        checkpoint=checkpoint,
        explicit_spec_dir=explicit_spec_dir,
    )
    if scope.blockers:
        return FrontendContractRuntimeAttachment(
            status=_scope_failure_status(scope),
            scope=scope,
            artifact_path=None,
            artifact=None,
            blockers=scope.blockers,
            coverage_gaps=("frontend_contract_runtime_scope",),
            allow_artifact_write=allow_artifact_write,
        )

    if scope.spec_dir is None:
        raise ValueError("scope.spec_dir must be present when blockers are empty")

    path = observation_artifact_path(scope.spec_dir)
    if not path.is_file():
        return FrontendContractRuntimeAttachment(
            status=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT,
            scope=scope,
            artifact_path=path,
            artifact=None,
            blockers=(
                "frontend contract runtime attachment unavailable: "
                f"missing canonical observation artifact {path.as_posix()}",
            ),
            coverage_gaps=("frontend_contract_observations",),
            allow_artifact_write=allow_artifact_write,
        )

    try:
        artifact = load_frontend_contract_observation_artifact(path)
    except ValueError as exc:
        return FrontendContractRuntimeAttachment(
            status=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT,
            scope=scope,
            artifact_path=path,
            artifact=None,
            blockers=(
                "frontend contract runtime attachment unavailable: "
                "invalid structured observation input "
                f"{path.as_posix()}: {exc}",
            ),
            coverage_gaps=("frontend_contract_observations",),
            allow_artifact_write=allow_artifact_write,
        )

    freshness_status = _freshness_status(artifact)
    advisories: tuple[str, ...] = ()
    coverage_gaps: tuple[str, ...] = ()
    if (
        freshness_status
        == FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_TIMESTAMP_ONLY
    ):
        advisories = (
            "frontend contract runtime attachment loaded from "
            f"{path.as_posix()} but freshness is timestamp-only; "
            "source_digest/source_revision missing",
        )
        coverage_gaps = ("frontend_contract_observation_freshness",)

    return FrontendContractRuntimeAttachment(
        status=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED,
        scope=scope,
        artifact_path=path,
        artifact=artifact,
        advisories=advisories,
        coverage_gaps=coverage_gaps,
        freshness_status=freshness_status,
        allow_artifact_write=allow_artifact_write,
    )


def _resolve_explicit_scope(
    root: Path,
    explicit_spec_dir: Path | str,
) -> FrontendContractRuntimeAttachmentScope:
    raw_path = Path(explicit_spec_dir).expanduser()
    if not raw_path.is_absolute():
        raw_path = root / raw_path
    spec_dir = raw_path.resolve()
    if not _is_within_root(spec_dir, root):
        return FrontendContractRuntimeAttachmentScope(
            spec_dir=None,
            scope_source=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_EXPLICIT_SPEC_DIR,
            work_item_id="",
            blockers=(
                "frontend contract runtime attachment unavailable: "
                f"explicit spec_dir is outside project root ({spec_dir.as_posix()})",
            ),
        )
    return FrontendContractRuntimeAttachmentScope(
        spec_dir=spec_dir,
        scope_source=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_EXPLICIT_SPEC_DIR,
        work_item_id=spec_dir.name,
    )


def _resolve_checkpoint_scope(
    root: Path,
    checkpoint: Checkpoint | None,
) -> FrontendContractRuntimeAttachmentScope:
    if checkpoint is None or checkpoint.feature is None:
        return _missing_scope(
            FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT,
            "active spec_dir is unresolved",
        )

    spec_dir_raw = (checkpoint.feature.spec_dir or "").strip()
    if not spec_dir_raw or spec_dir_raw == "specs/unknown":
        return _missing_scope(
            FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT,
            "active spec_dir is unresolved",
        )

    spec_dir = (root / spec_dir_raw).resolve()
    if not _is_within_root(spec_dir, root):
        return FrontendContractRuntimeAttachmentScope(
            spec_dir=None,
            scope_source=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT,
            work_item_id="",
            blockers=(
                "frontend contract runtime attachment unavailable: "
                f"checkpoint spec_dir is outside project root ({spec_dir.as_posix()})",
            ),
        )
    return FrontendContractRuntimeAttachmentScope(
        spec_dir=spec_dir,
        scope_source=FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT,
        work_item_id=spec_dir.name,
    )


def _missing_scope(scope_source: str, reason: str) -> FrontendContractRuntimeAttachmentScope:
    return FrontendContractRuntimeAttachmentScope(
        spec_dir=None,
        scope_source=scope_source,
        work_item_id="",
        blockers=(
            "frontend contract runtime attachment unavailable: "
            f"{reason}",
        ),
    )


def _scope_failure_status(
    scope: FrontendContractRuntimeAttachmentScope,
) -> str:
    if any("outside project root" in blocker for blocker in scope.blockers):
        return FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_SCOPE_OUTSIDE_ROOT
    return FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_SCOPE


def _freshness_status(
    artifact: FrontendContractObservationArtifact,
) -> str:
    if artifact.freshness.source_digest or artifact.freshness.source_revision:
        return FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_VERIFIABLE
    return FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_TIMESTAMP_ONLY


def _is_within_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


__all__ = [
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_TIMESTAMP_ONLY",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_UNKNOWN",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_FRESHNESS_VERIFIABLE",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_CHECKPOINT",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_SCOPE_EXPLICIT_SPEC_DIR",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_ATTACHED",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_INVALID_ARTIFACT",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_ARTIFACT",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_MISSING_SCOPE",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_STATUS_SCOPE_OUTSIDE_ROOT",
    "FRONTEND_CONTRACT_RUNTIME_ATTACHMENT_WRITE_POLICY_EXPLICIT_OPT_IN",
    "FrontendContractRuntimeAttachment",
    "FrontendContractRuntimeAttachmentScope",
    "build_frontend_contract_runtime_attachment",
    "resolve_frontend_contract_runtime_attachment_scope",
]
