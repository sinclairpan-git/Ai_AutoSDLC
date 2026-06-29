"""Tests for Loop Engine policy loading and model resolution."""

from __future__ import annotations

import pytest

from ai_sdlc.core.loop_models import LoopPolicyProfile
from ai_sdlc.core.loop_policy import (
    LOOP_POLICY_PATH,
    LoopPolicyError,
    ModelResolutionRequest,
    PolicyDecisionStatus,
    evaluate_code_egress_policy,
    load_loop_policy,
    resolve_model_for_review,
)
from ai_sdlc.core.pr_review_models import (
    ModelResolutionSource,
    ModelResolutionStatus,
)


def test_load_loop_policy_returns_safe_defaults_when_file_missing(tmp_path) -> None:
    policy = load_loop_policy(tmp_path)

    assert policy.default_provider == "local-agent"
    assert policy.default_model == "current"
    assert policy.remote_model_policy == "disclose"
    assert policy.high_risk_secret_policy == "needs_user"
    assert policy.max_rounds == 2
    assert policy.default_close_mode == "strict"


def test_load_loop_policy_reads_project_config_file(tmp_path) -> None:
    path = tmp_path / LOOP_POLICY_PATH
    path.parent.mkdir(parents=True)
    path.write_text(
        "\n".join(
            [
                "profile_id: team-default",
                "default_provider: local-agent",
                "default_model: claude-sonnet-4",
                "remote_model_policy: require_confirmation",
                "high_risk_secret_policy: allow-with-waiver",
            ]
        ),
        encoding="utf-8",
    )

    policy = load_loop_policy(tmp_path)

    assert policy.profile_id == "team-default"
    assert policy.default_model == "claude-sonnet-4"
    assert policy.remote_model_policy == "require_confirmation"
    assert policy.high_risk_secret_policy == "allow-with-waiver"


def test_load_loop_policy_rejects_malformed_project_config(tmp_path) -> None:
    path = tmp_path / LOOP_POLICY_PATH
    path.parent.mkdir(parents=True)
    path.write_text("remote_model_policy: strict\n", encoding="utf-8")

    with pytest.raises(LoopPolicyError, match="Loop policy is malformed"):
        load_loop_policy(tmp_path)


def test_resolve_model_priority_uses_explicit_cli_then_policy_then_provider() -> None:
    policy = LoopPolicyProfile(default_model="claude-sonnet-4")

    explicit = resolve_model_for_review(
        policy,
        ModelResolutionRequest(
            requested_model="gpt-5",
            provider_default_model="deepseek-r1",
            current_model="glm-4.5",
        ),
    )
    policy_default = resolve_model_for_review(
        policy,
        ModelResolutionRequest(
            provider_default_model="deepseek-r1",
            current_model="glm-4.5",
        ),
    )
    provider_default = resolve_model_for_review(
        LoopPolicyProfile(default_model="current"),
        ModelResolutionRequest(
            provider_default_model="deepseek-r1",
            current_model="glm-4.5",
        ),
    )

    assert explicit.resolved_model == "gpt-5"
    assert explicit.resolution_source == ModelResolutionSource.EXPLICIT_CLI
    assert policy_default.resolved_model == "claude-sonnet-4"
    assert policy_default.resolution_source == ModelResolutionSource.PROJECT_POLICY
    assert provider_default.resolved_model == "deepseek-r1"
    assert provider_default.resolution_source == ModelResolutionSource.PROVIDER_CONFIG


def test_resolve_model_current_falls_back_to_current_agent() -> None:
    resolution = resolve_model_for_review(
        LoopPolicyProfile(default_model="current"),
        ModelResolutionRequest(current_model="glm-4.5-air"),
    )

    assert resolution.status == ModelResolutionStatus.RESOLVED
    assert resolution.model_selector == "current"
    assert resolution.resolved_model == "glm-4.5-air"
    assert resolution.resolution_source == ModelResolutionSource.CURRENT_AGENT


def test_resolve_model_returns_needs_user_when_current_cannot_be_resolved() -> None:
    resolution = resolve_model_for_review(LoopPolicyProfile(default_model="current"))

    assert resolution.status == ModelResolutionStatus.NEEDS_USER
    assert resolution.resolved_model == ""
    assert "Unable to resolve model=current" in resolution.blocker


def test_allowed_model_selectors_block_disallowed_cli_model() -> None:
    resolution = resolve_model_for_review(
        LoopPolicyProfile(allowed_model_selectors=["claude-sonnet-4"]),
        ModelResolutionRequest(requested_model="gpt-5", current_model="gpt-5"),
    )

    assert resolution.status == ModelResolutionStatus.BLOCKED
    assert "does not allow model" in resolution.blocker


def test_code_egress_policy_requires_confirmation_when_configured() -> None:
    decision = evaluate_code_egress_policy(
        LoopPolicyProfile(remote_model_policy="require_confirmation"),
        code_egress=True,
        confirmed=False,
    )

    assert decision.status == PolicyDecisionStatus.NEEDS_USER
    assert "requires confirmation" in decision.blocker


def test_code_egress_policy_can_forbid_remote_model_services() -> None:
    resolution = resolve_model_for_review(
        LoopPolicyProfile(default_model="gpt-5", remote_model_policy="forbid"),
        ModelResolutionRequest(code_egress=True),
    )

    assert resolution.status == ModelResolutionStatus.BLOCKED
    assert "forbids sending code" in resolution.blocker


def test_remote_model_policy_rejects_unhandled_values() -> None:
    with pytest.raises(ValueError, match="unsupported policy value"):
        LoopPolicyProfile(remote_model_policy="strict")
