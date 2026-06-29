"""Policy loading and model resolution for local PR review loops."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from ai_sdlc.core.config import YamlStore
from ai_sdlc.core.loop_models import LoopPolicyProfile
from ai_sdlc.core.pr_review_models import (
    ModelResolution,
    ModelResolutionSource,
    ModelResolutionStatus,
    ProviderMode,
)
from ai_sdlc.utils.helpers import AI_SDLC_DIR

LOOP_POLICY_PATH = Path(AI_SDLC_DIR) / "project" / "config" / "loop-policy.yaml"


class PolicyDecisionStatus(StrEnum):
    """Policy decision outcome values."""

    ALLOWED = "allowed"
    NEEDS_USER = "needs_user"
    BLOCKED = "blocked"


class LoopPolicyDecision(BaseModel):
    """Plain-language policy decision used by CLI/service layers."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    status: PolicyDecisionStatus = PolicyDecisionStatus.ALLOWED
    reason: str = ""
    blocker: str = ""
    next_action: str = ""


@dataclass(frozen=True, slots=True)
class ModelResolutionRequest:
    """Inputs used to resolve the model selected for local review."""

    requested_provider: str | None = None
    requested_model: str | None = None
    provider_default_model: str = ""
    current_model: str = ""
    provider_mode: ProviderMode = ProviderMode.LOCAL_AGENT
    code_egress: bool = False
    code_egress_confirmed: bool = False


def load_loop_policy(root: Path) -> LoopPolicyProfile:
    """Load project loop policy, returning safe defaults when absent."""

    path = root / LOOP_POLICY_PATH
    return YamlStore.load(path, LoopPolicyProfile, default=LoopPolicyProfile())


def resolve_model_for_review(
    policy: LoopPolicyProfile,
    request: ModelResolutionRequest | None = None,
) -> ModelResolution:
    """Resolve provider/model according to the P0 priority contract."""

    resolved_request = request or ModelResolutionRequest()
    provider_id = (resolved_request.requested_provider or policy.default_provider).strip()
    if not provider_id:
        provider_id = "local-agent"

    selector, resolved_model, source = _resolve_model_value(policy, resolved_request)
    allowed_decision = _enforce_allowed_model_selectors(policy, selector, resolved_model)
    if allowed_decision.status == PolicyDecisionStatus.BLOCKED:
        return ModelResolution(
            provider_id=provider_id,
            provider_mode=resolved_request.provider_mode,
            model_selector=selector or "current",
            resolved_model="",
            status=ModelResolutionStatus.BLOCKED,
            code_egress=resolved_request.code_egress,
            blocker=allowed_decision.blocker,
        )

    if not resolved_model:
        return ModelResolution(
            provider_id=provider_id,
            provider_mode=resolved_request.provider_mode,
            model_selector=selector or "current",
            resolved_model="",
            status=ModelResolutionStatus.NEEDS_USER,
            code_egress=resolved_request.code_egress,
            blocker="Unable to resolve model=current. Configure a default model or pass --model.",
        )

    egress_decision = evaluate_code_egress_policy(
        policy,
        code_egress=resolved_request.code_egress,
        confirmed=resolved_request.code_egress_confirmed,
    )
    if egress_decision.status != PolicyDecisionStatus.ALLOWED:
        status = (
            ModelResolutionStatus.BLOCKED
            if egress_decision.status == PolicyDecisionStatus.BLOCKED
            else ModelResolutionStatus.NEEDS_USER
        )
        return ModelResolution(
            provider_id=provider_id,
            provider_mode=resolved_request.provider_mode,
            model_selector=selector,
            resolved_model="",
            resolution_source=source,
            status=status,
            code_egress=resolved_request.code_egress,
            blocker=egress_decision.blocker,
        )

    return ModelResolution(
        provider_id=provider_id,
        provider_mode=resolved_request.provider_mode,
        model_selector=selector,
        resolved_model=resolved_model,
        resolution_source=source,
        status=ModelResolutionStatus.RESOLVED,
        code_egress=resolved_request.code_egress,
    )


def evaluate_code_egress_policy(
    policy: LoopPolicyProfile,
    *,
    code_egress: bool,
    confirmed: bool = False,
) -> LoopPolicyDecision:
    """Apply policy to remote code egress for model calls."""

    if not code_egress:
        return LoopPolicyDecision(
            status=PolicyDecisionStatus.ALLOWED,
            reason="Provider/model does not send code to a remote model service.",
        )

    if policy.remote_model_policy == "forbid":
        return LoopPolicyDecision(
            status=PolicyDecisionStatus.BLOCKED,
            blocker="Project policy forbids sending code to remote model services.",
            next_action="Choose a non-egress provider/model or update loop-policy.yaml.",
        )
    if policy.remote_model_policy == "require_confirmation" and not confirmed:
        return LoopPolicyDecision(
            status=PolicyDecisionStatus.NEEDS_USER,
            blocker="Project policy requires confirmation before sending code to a remote model service.",
            next_action="Confirm code egress or choose a non-egress provider/model.",
        )

    return LoopPolicyDecision(
        status=PolicyDecisionStatus.ALLOWED,
        reason="Remote model service code egress is disclosed by policy.",
    )


def _resolve_model_value(
    policy: LoopPolicyProfile,
    request: ModelResolutionRequest,
) -> tuple[str, str, ModelResolutionSource | None]:
    requested = (request.requested_model or "").strip()
    if requested and requested != "current":
        return requested, requested, ModelResolutionSource.EXPLICIT_CLI

    policy_default = (policy.default_model or "").strip()
    if policy_default and policy_default != "current":
        return policy_default, policy_default, ModelResolutionSource.PROJECT_POLICY

    provider_default = request.provider_default_model.strip()
    if provider_default:
        return "current", provider_default, ModelResolutionSource.PROVIDER_CONFIG

    current_model = request.current_model.strip()
    if current_model:
        return "current", current_model, ModelResolutionSource.CURRENT_AGENT

    return requested or policy_default or "current", "", None


def _enforce_allowed_model_selectors(
    policy: LoopPolicyProfile,
    model_selector: str,
    resolved_model: str,
) -> LoopPolicyDecision:
    allowed = {item.strip() for item in policy.allowed_model_selectors if item.strip()}
    if not allowed:
        return LoopPolicyDecision(status=PolicyDecisionStatus.ALLOWED)
    if model_selector in allowed or resolved_model in allowed:
        return LoopPolicyDecision(status=PolicyDecisionStatus.ALLOWED)
    return LoopPolicyDecision(
        status=PolicyDecisionStatus.BLOCKED,
        blocker=(
            "Project policy does not allow model "
            f"{resolved_model or model_selector!r}."
        ),
        next_action="Choose an allowed model or update loop-policy.yaml.",
    )


__all__ = [
    "LOOP_POLICY_PATH",
    "LoopPolicyDecision",
    "ModelResolutionRequest",
    "PolicyDecisionStatus",
    "evaluate_code_egress_policy",
    "load_loop_policy",
    "resolve_model_for_review",
]
