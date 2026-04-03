"""Unit tests for program manifest service."""

from __future__ import annotations

from pathlib import Path

import yaml

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    observation_artifact_path,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.program_service import (
    ProgramFrontendRemediationCommandResult,
    ProgramFrontendRemediationExecutionResult,
    ProgramService,
)
from ai_sdlc.generators.frontend_gate_policy_artifacts import (
    materialize_frontend_gate_policy_artifacts,
)
from ai_sdlc.generators.frontend_generation_constraint_artifacts import (
    materialize_frontend_generation_constraint_artifacts,
)
from ai_sdlc.models.frontend_gate_policy import build_mvp_frontend_gate_policy
from ai_sdlc.models.frontend_generation_constraints import (
    build_mvp_frontend_generation_constraints,
)
from ai_sdlc.models.program import ProgramManifest, ProgramSpecRef


def _manifest() -> ProgramManifest:
    return ProgramManifest(
        schema_version="1",
        prd_path="PRD.md",
        specs=[
            ProgramSpecRef(id="001-auth", path="specs/001-auth", depends_on=[]),
            ProgramSpecRef(
                id="002-course",
                path="specs/002-course",
                depends_on=[],
            ),
            ProgramSpecRef(
                id="003-enroll",
                path="specs/003-enroll",
                depends_on=["001-auth", "002-course"],
            ),
        ],
    )


def test_validate_manifest_ok(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    (tmp_path / "PRD.md").write_text("# prd\n", encoding="utf-8")
    svc = ProgramService(tmp_path)
    res = svc.validate_manifest(_manifest())
    assert res.valid is True
    assert res.errors == []


def test_validate_manifest_cycle(tmp_path: Path) -> None:
    (tmp_path / "specs" / "a").mkdir(parents=True)
    (tmp_path / "specs" / "b").mkdir(parents=True)
    mf = ProgramManifest(
        specs=[
            ProgramSpecRef(id="a", path="specs/a", depends_on=["b"]),
            ProgramSpecRef(id="b", path="specs/b", depends_on=["a"]),
        ]
    )
    svc = ProgramService(tmp_path)
    res = svc.validate_manifest(mf)
    assert res.valid is False
    assert any("cycle" in e for e in res.errors)


def test_topo_tiers(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    svc = ProgramService(tmp_path)
    tiers = svc.topo_tiers(_manifest())
    assert tiers[0] == ["001-auth", "002-course"]
    assert tiers[1] == ["003-enroll"]


def test_build_status_counts_and_blockers(tmp_path: Path) -> None:
    auth = tmp_path / "specs" / "001-auth"
    course = tmp_path / "specs" / "002-course"
    enroll = tmp_path / "specs" / "003-enroll"
    for p in (auth, course, enroll):
        p.mkdir(parents=True)

    (auth / "spec.md").write_text("# spec\n", encoding="utf-8")
    (auth / "plan.md").write_text("# plan\n", encoding="utf-8")
    (auth / "tasks.md").write_text("- [x] done\n- [ ] todo\n", encoding="utf-8")

    (course / "development-summary.md").write_text("ok\n", encoding="utf-8")

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    assert by["001-auth"].completed_tasks == 1
    assert by["001-auth"].total_tasks == 2
    assert by["002-course"].stage_hint == "close"
    assert by["003-enroll"].blocked_by == ["001-auth"]


def test_build_integration_dry_run(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    (tmp_path / "specs" / "001-auth" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    (tmp_path / "specs" / "002-course" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())
    assert len(plan.steps) == 3
    assert plan.steps[0].tier == 0
    assert plan.steps[2].spec_id == "003-enroll"
    assert plan.steps[2].tier == 1


def test_build_integration_dry_run_surfaces_frontend_recheck_handoff_when_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    handoff = step.frontend_recheck_handoff
    assert handoff is not None
    assert handoff.required is True
    assert "re-run frontend verification after execute" in handoff.reason
    assert handoff.recommended_commands == ["uv run ai-sdlc verify constraints"]
    assert handoff.source_linkage["frontend_gate_verdict"] == "PASS"


def test_build_integration_dry_run_skips_frontend_recheck_handoff_when_not_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_recheck_handoff is None


def test_build_integration_dry_run_surfaces_frontend_remediation_input_when_not_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert remediation.state == "required"
    assert "frontend_contract_observations" in remediation.fix_inputs
    assert "materialize frontend contract observations" in remediation.suggested_actions
    assert (
        "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
        in remediation.recommended_commands
    )
    assert remediation.recommended_commands[-1] == "uv run ai-sdlc verify constraints"
    assert remediation.source_linkage["runtime_attachment_status"] == "missing_artifact"


def test_build_integration_dry_run_skips_frontend_remediation_input_when_ready(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    assert step.frontend_remediation_input is None


def test_build_integration_dry_run_binds_governance_materialization_command_when_gaps_present(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_gate_policy_artifacts" in remediation.fix_inputs
    assert (
        "uv run ai-sdlc rules materialize-frontend-mvp"
        in remediation.recommended_commands
    )
    assert remediation.recommended_commands[-1] == "uv run ai-sdlc verify constraints"


def test_build_frontend_remediation_runbook_collects_action_commands_and_follow_up_verify(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_frontend_contract_source_annotation(tmp_path)
    for spec in ("002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    runbook = svc.build_frontend_remediation_runbook(_manifest())

    assert [step.spec_id for step in runbook.steps] == [
        "001-auth",
        "002-course",
        "003-enroll",
    ]
    assert (
        "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
        in runbook.action_commands
    )
    assert "uv run ai-sdlc rules materialize-frontend-mvp" in runbook.action_commands
    assert runbook.follow_up_commands == ["uv run ai-sdlc verify constraints"]


def test_execute_frontend_remediation_runbook_materializes_bounded_commands_and_verifies(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_constitution(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_frontend_contract_source_annotation(tmp_path)
    for spec in ("002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_remediation_runbook(
        _manifest(),
        generated_at="2026-04-03T17:30:00Z",
    )

    assert result.passed is True
    assert (
        observation_artifact_path(tmp_path / "specs" / "001-auth").is_file()
    )
    assert (tmp_path / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()
    assert (
        tmp_path / "governance" / "frontend" / "generation" / "generation.manifest.yaml"
    ).is_file()
    assert any(
        item.command == "uv run ai-sdlc rules materialize-frontend-mvp"
        and item.status == "executed"
        for item in result.command_results
    )
    assert any(
        item.command == "uv run ai-sdlc verify constraints"
        and item.status == "passed"
        for item in result.command_results
    )
    assert result.blockers == []


def test_write_frontend_remediation_writeback_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_constitution(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    _write_frontend_contract_source_annotation(tmp_path)
    for spec in ("002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    runbook = svc.build_frontend_remediation_runbook(_manifest())
    execution = svc.execute_frontend_remediation_runbook(
        _manifest(),
        generated_at="2026-04-03T16:00:00Z",
    )

    writeback_path = svc.write_frontend_remediation_writeback_artifact(
        _manifest(),
        runbook=runbook,
        execution_result=execution,
        generated_at="2026-04-03T16:00:00Z",
    )

    assert writeback_path == (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
    )
    payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
    assert payload["generated_at"] == "2026-04-03T16:00:00Z"
    assert payload["passed"] is True
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert payload["remaining_blockers"] == []
    assert payload["follow_up_commands"] == ["uv run ai-sdlc verify constraints"]
    assert payload["written_paths"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert any(
        item["command"] == "uv run ai-sdlc verify constraints"
        for item in payload["command_results"]
    )


def test_write_frontend_remediation_writeback_artifact_reuses_provided_execution_result(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    execution = ProgramFrontendRemediationExecutionResult(
        passed=False,
        command_results=[
            ProgramFrontendRemediationCommandResult(
                command="sentinel-command",
                status="passed",
                written_paths=["sentinel/path.yaml"],
                summary="sentinel summary",
            )
        ],
        blockers=["sentinel blocker"],
    )

    writeback_path = svc.write_frontend_remediation_writeback_artifact(
        _manifest(),
        execution_result=execution,
        generated_at="2026-04-03T16:05:00Z",
    )

    payload = yaml.safe_load(writeback_path.read_text(encoding="utf-8"))
    assert payload["command_results"] == [
        {
            "command": "sentinel-command",
            "status": "passed",
            "written_paths": ["sentinel/path.yaml"],
            "blockers": [],
            "summary": "sentinel summary",
        }
    ]
    assert payload["remaining_blockers"] == ["sentinel blocker"]


def test_build_frontend_provider_handoff_packages_pending_inputs_from_writeback_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is True
    assert handoff.provider_execution_state == "not_started"
    assert (
        handoff.writeback_artifact_path
        == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    )
    assert handoff.writeback_generated_at == "2026-04-03T18:00:00Z"
    assert handoff.remaining_blockers == ["spec 001-auth remediation still required"]
    assert [step.spec_id for step in handoff.steps] == ["001-auth", "002-course"]
    assert handoff.steps[0].pending_inputs == ["frontend_contract_observations"]
    assert (
        handoff.steps[0].source_linkage["writeback_artifact_path"]
        == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    )
    assert (
        handoff.steps[0].source_linkage["provider_execution_state"] == "not_started"
    )


def test_build_frontend_provider_handoff_is_not_required_when_writeback_is_clean(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=True,
        remaining_blockers=[],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is False
    assert handoff.provider_execution_state == "not_started"
    assert handoff.steps == []
    assert handoff.remaining_blockers == []


def test_build_frontend_provider_runtime_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.provider_execution_state == "not_started"
    assert request.handoff_source_path == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    assert request.handoff_generated_at == "2026-04-03T18:00:00Z"
    assert request.remaining_blockers == ["spec 001-auth remediation still required"]
    assert [step.spec_id for step in request.steps] == ["001-auth", "002-course"]
    assert request.steps[0].pending_inputs == ["frontend_contract_observations"]
    assert (
        request.steps[0].source_linkage["provider_runtime_state"] == "not_started"
    )


def test_execute_frontend_provider_runtime_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_runtime(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.provider_execution_state == "deferred"
    assert result.invocation_result == "deferred"
    assert result.patch_summaries == [
        "no patches generated in guarded provider runtime baseline"
    ]
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["provider_runtime_state"] == "deferred"


def test_write_frontend_provider_runtime_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())
    result = svc.execute_frontend_provider_runtime(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_provider_runtime_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["handoff_source_path"]
        == ".ai-sdlc/memory/frontend-remediation/latest.yaml"
    )
    assert payload["provider_execution_state"] == "deferred"
    assert payload["invocation_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["patch_summaries"] == [
        "no patches generated in guarded provider runtime baseline"
    ]
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["provider_runtime_artifact_path"]
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )


def test_execute_frontend_provider_runtime_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_runtime(_manifest(), confirmed=True)

    assert result.provider_execution_state == "deferred"
    assert not (
        tmp_path / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    ).exists()


def test_build_frontend_provider_patch_handoff_packages_runtime_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is True
    assert handoff.patch_availability_state == "deferred"
    assert (
        handoff.runtime_artifact_path
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )
    assert handoff.runtime_generated_at == "2026-04-03T19:00:00Z"
    assert handoff.patch_summaries == [
        "no patches generated in guarded provider runtime baseline"
    ]
    assert handoff.remaining_blockers == ["spec 001-auth remediation still required"]
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == ["frontend_contract_observations"]
    assert (
        handoff.steps[0].source_linkage["provider_patch_handoff_state"] == "deferred"
    )
    assert (
        handoff.source_linkage["provider_runtime_artifact_path"]
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )


def test_build_frontend_provider_patch_handoff_warns_when_runtime_artifact_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is False
    assert handoff.patch_availability_state == "missing_artifact"
    assert handoff.steps == []
    assert handoff.runtime_generated_at == ""
    assert "missing provider runtime artifact" in handoff.warnings[0]


def test_build_frontend_provider_patch_apply_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.patch_apply_state == "not_started"
    assert (
        request.handoff_source_path
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )
    assert request.handoff_generated_at == "2026-04-03T19:00:00Z"
    assert request.patch_availability_state == "deferred"
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].patch_availability_state == "deferred"
    assert (
        request.steps[0].source_linkage["patch_apply_state"] == "not_started"
    )


def test_execute_frontend_provider_patch_apply_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_patch_apply(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.patch_apply_state == "deferred"
    assert result.apply_result == "deferred"
    assert result.apply_summaries == ["no files written in guarded patch apply baseline"]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["patch_apply_state"] == "deferred"


def test_write_frontend_provider_patch_apply_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())
    result = svc.execute_frontend_provider_patch_apply(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_provider_patch_apply_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["handoff_source_path"]
        == ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml"
    )
    assert payload["patch_apply_state"] == "deferred"
    assert payload["apply_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["apply_summaries"] == [
        "no files written in guarded patch apply baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["provider_patch_apply_artifact_path"]
        == ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
    )


def test_execute_frontend_provider_patch_apply_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_provider_patch_apply(_manifest(), confirmed=True)

    assert result.patch_apply_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-provider-patch-apply"
        / "latest.yaml"
    ).exists()


def test_build_frontend_cross_spec_writeback_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.writeback_state == "not_started"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T20:00:00Z"
    assert request.apply_result == "deferred"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].writeback_state == "not_started"
    assert (
        request.steps[0].source_linkage["cross_spec_writeback_state"] == "not_started"
    )


def test_execute_frontend_cross_spec_writeback_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_cross_spec_writeback(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.writeback_state == "deferred"
    assert result.orchestration_result == "deferred"
    assert result.orchestration_summaries == [
        "no cross-spec writes executed in guarded writeback baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["cross_spec_writeback_state"] == "deferred"


def test_write_frontend_cross_spec_writeback_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())
    result = svc.execute_frontend_cross_spec_writeback(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_cross_spec_writeback_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-cross-spec-writeback"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml"
    )
    assert payload["writeback_state"] == "deferred"
    assert payload["orchestration_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["orchestration_summaries"] == [
        "no cross-spec writes executed in guarded writeback baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["cross_spec_writeback_artifact_path"]
        == ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
    )


def test_execute_frontend_cross_spec_writeback_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_cross_spec_writeback(_manifest(), confirmed=True)

    assert result.writeback_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-cross-spec-writeback"
        / "latest.yaml"
    ).exists()


def test_build_frontend_guarded_registry_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.registry_state == "not_started"
    assert request.writeback_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T21:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].registry_state == "not_started"
    assert request.steps[0].source_linkage["registry_state"] == "not_started"


def test_execute_frontend_guarded_registry_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.registry_state == "deferred"
    assert result.registry_result == "deferred"
    assert result.registry_summaries == [
        "no registry updates executed in guarded registry baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["registry_state"] == "deferred"


def test_write_frontend_guarded_registry_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())
    result = svc.execute_frontend_guarded_registry(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_guarded_registry_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-guarded-registry"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml"
    )
    assert payload["registry_state"] == "deferred"
    assert payload["registry_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["registry_summaries"] == [
        "no registry updates executed in guarded registry baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["guarded_registry_artifact_path"]
        == ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
    )


def test_execute_frontend_guarded_registry_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_guarded_registry(_manifest(), confirmed=True)

    assert result.registry_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-guarded-registry"
        / "latest.yaml"
    ).exists()


def test_build_frontend_broader_governance_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.governance_state == "not_started"
    assert request.registry_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T22:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].governance_state == "not_started"
    assert request.steps[0].source_linkage["governance_state"] == "not_started"


def test_execute_frontend_broader_governance_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.governance_state == "deferred"
    assert result.governance_result == "deferred"
    assert result.governance_summaries == [
        "no broader governance actions executed in broader governance baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["governance_state"] == "deferred"


def test_write_frontend_broader_governance_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())
    result = svc.execute_frontend_broader_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_broader_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-broader-governance"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml"
    )
    assert payload["governance_state"] == "deferred"
    assert payload["governance_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["governance_summaries"] == [
        "no broader governance actions executed in broader governance baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["broader_governance_artifact_path"]
        == ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
    )


def test_execute_frontend_broader_governance_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_broader_governance(_manifest(), confirmed=True)

    assert result.governance_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-broader-governance"
        / "latest.yaml"
    ).exists()


def test_build_frontend_final_governance_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.final_governance_state == "not_started"
    assert request.governance_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-03T23:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].final_governance_state == "not_started"
    assert request.steps[0].source_linkage["final_governance_state"] == "not_started"


def test_execute_frontend_final_governance_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.final_governance_state == "deferred"
    assert result.final_governance_result == "deferred"
    assert result.final_governance_summaries == [
        "no final governance actions executed in final governance baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["final_governance_state"] == "deferred"


def test_write_frontend_final_governance_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())
    result = svc.execute_frontend_final_governance(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_governance_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-governance"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-broader-governance/latest.yaml"
    )
    assert payload["final_governance_state"] == "deferred"
    assert payload["final_governance_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["final_governance_summaries"] == [
        "no final governance actions executed in final governance baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["final_governance_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
    )


def test_execute_frontend_final_governance_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_governance(_manifest(), confirmed=True)

    assert result.final_governance_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-governance"
        / "latest.yaml"
    ).exists()


def test_build_frontend_writeback_persistence_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.persistence_state == "not_started"
    assert request.final_governance_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T00:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].persistence_state == "not_started"
    assert request.steps[0].source_linkage["persistence_state"] == "not_started"


def test_execute_frontend_writeback_persistence_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.persistence_state == "deferred"
    assert result.persistence_result == "deferred"
    assert result.persistence_summaries == [
        "no writeback persistence actions executed in writeback persistence baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["persistence_state"] == "deferred"


def test_write_frontend_writeback_persistence_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())
    result = svc.execute_frontend_writeback_persistence(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_writeback_persistence_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-writeback-persistence"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-final-governance/latest.yaml"
    )
    assert payload["persistence_state"] == "deferred"
    assert payload["persistence_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["persistence_summaries"] == [
        "no writeback persistence actions executed in writeback persistence baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["writeback_persistence_artifact_path"]
        == ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
    )


def test_execute_frontend_writeback_persistence_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_writeback_persistence(_manifest(), confirmed=True)

    assert result.persistence_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-writeback-persistence"
        / "latest.yaml"
    ).exists()


def test_build_status_surfaces_ready_frontend_readiness_per_spec(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    _write_frontend_contract_observations(tmp_path / "specs" / "001-auth")

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "ready"
    assert readiness.coverage_gaps == []
    assert readiness.blockers == []
    assert readiness.source_linkage["runtime_attachment_status"] == "attached"
    assert readiness.source_linkage["frontend_gate_verdict"] == "PASS"


def test_build_status_surfaces_frontend_readiness_gap_when_attachment_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    rows = svc.build_status(_manifest())
    by = {r.spec_id: r for r in rows}

    readiness = by["001-auth"].frontend_readiness
    assert readiness is not None
    assert readiness.state == "missing_artifact"
    assert "frontend_contract_observations" in readiness.coverage_gaps
    assert "missing canonical observation artifact" in readiness.blockers[0]
    assert readiness.source_linkage["runtime_attachment_status"] == "missing_artifact"
    assert readiness.source_linkage["frontend_gate_verdict"] == "UNRESOLVED"


def test_execution_gates_require_all_specs_closed(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    (tmp_path / "specs" / "001-auth" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    (tmp_path / "specs" / "002-course" / "development-summary.md").write_text(
        "ok\n", encoding="utf-8"
    )
    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)
    assert gates.passed is False
    assert any("not closed" in item for item in gates.failed)


def test_execution_gates_pass_when_closed(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)
    assert gates.passed is True


def test_execution_gates_fail_when_frontend_readiness_not_clear(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )

    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)

    assert gates.passed is False
    assert any("frontend execute gate not clear" in item for item in gates.failed)
    assert any("missing_artifact" in item for item in gates.failed)


def test_execution_gates_pass_when_closed_and_frontend_ready(tmp_path: Path) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    for spec in ("001-auth", "002-course", "003-enroll"):
        (tmp_path / "specs" / spec / "development-summary.md").write_text(
            "ok\n", encoding="utf-8"
        )
        _write_frontend_contract_observations(tmp_path / "specs" / spec)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_mvp_frontend_gate_policy(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )

    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)

    assert gates.passed is True
    assert not any("frontend execute gate not clear" in item for item in gates.failed)


def _write_minimal_frontend_contract_page_artifacts(
    root: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    page_dir = root / "contracts" / "frontend" / "pages" / page_id
    page_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "page.metadata.yaml").write_text(
        f"page_id: {page_id}\npage_type: form\n",
        encoding="utf-8",
    )
    (page_dir / "page.recipe.yaml").write_text(
        f"recipe_id: {recipe_id}\nrequired_regions:\n  - form\n",
        encoding="utf-8",
    )


def _write_frontend_contract_observations(
    spec_dir: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    artifact = build_frontend_contract_observation_artifact(
        observations=[
            PageImplementationObservation(
                page_id=page_id,
                recipe_id=recipe_id,
                i18n_keys=[],
                validation_fields=[],
                new_legacy_usages=[],
            )
        ],
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-03T15:00:00Z",
        source_digest="sha256:program-service",
        source_revision="rev-program-service",
    )
    write_frontend_contract_observation_artifact(spec_dir, artifact)


def _write_frontend_contract_source_annotation(
    root: Path,
    *,
    page_id: str = "user-create",
    recipe_id: str = "form-create",
) -> None:
    src_dir = root / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "UserCreate.vue").write_text(
        f"""
        <!-- ai-sdlc:frontend-contract-observation
        {{
          "page_id": "{page_id}",
          "recipe_id": "{recipe_id}",
          "i18n_keys": ["user.create.submit"],
          "validation_fields": ["username"]
        }}
        -->
        """,
        encoding="utf-8",
    )


def _write_minimal_constitution(root: Path) -> None:
    memory_dir = root / ".ai-sdlc" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "constitution.md").write_text("# Constitution\n", encoding="utf-8")


def _write_frontend_remediation_writeback_artifact(
    root: Path,
    *,
    passed: bool,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-remediation" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T18:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "passed": passed,
                "source_linkage": {
                    "runbook_source": "program frontend remediation runbook",
                    "execution_source": "program frontend remediation execution",
                },
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "state": "required",
                        "fix_inputs": ["frontend_contract_observations"],
                        "suggested_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "action_commands": [
                            "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
                        ],
                        "source_linkage": {
                            "runtime_attachment_status": "missing_artifact",
                            "frontend_gate_verdict": "UNRESOLVED",
                        },
                    },
                    {
                        "spec_id": "002-course",
                        "path": "specs/002-course",
                        "state": "required",
                        "fix_inputs": ["frontend_gate_policy_artifacts"],
                        "suggested_actions": [
                            "materialize frontend gate policy artifacts"
                        ],
                        "action_commands": [
                            "uv run ai-sdlc rules materialize-frontend-mvp"
                        ],
                        "source_linkage": {
                            "runtime_attachment_status": "attached",
                            "frontend_gate_verdict": "RETRY",
                        },
                    },
                ],
                "action_commands": [
                    "uv run ai-sdlc scan . --frontend-contract-spec-dir specs/001-auth"
                ],
                "follow_up_commands": ["uv run ai-sdlc verify constraints"],
                "command_results": [
                    {
                        "command": "uv run ai-sdlc verify constraints",
                        "status": "failed" if remaining_blockers else "passed",
                        "written_paths": [],
                        "blockers": list(remaining_blockers),
                        "summary": "verify constraints result",
                    }
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_provider_runtime_artifact(
    root: Path,
    *,
    invocation_result: str,
    provider_execution_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-provider-runtime" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T19:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "handoff_source_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                "handoff_generated_at": "2026-04-03T18:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "provider_execution_state": provider_execution_state,
                "invocation_result": invocation_result,
                "patch_summaries": [
                    "no patches generated in guarded provider runtime baseline"
                ],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded provider runtime baseline does not invoke provider yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                            "provider_runtime_state": provider_execution_state,
                        },
                    }
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": provider_execution_state,
                    "invocation_result": invocation_result,
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_provider_patch_apply_artifact(
    root: Path,
    *,
    apply_result: str,
    patch_apply_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-provider-patch-apply" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T20:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "handoff_source_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                "handoff_generated_at": "2026-04-03T19:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "patch_availability_state": "deferred",
                "patch_apply_state": patch_apply_state,
                "apply_result": apply_result,
                "apply_summaries": [
                    "no files written in guarded patch apply baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded patch apply baseline does not apply patches yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "patch_availability_state": "deferred",
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                            "patch_apply_state": patch_apply_state,
                        },
                    }
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": patch_apply_state,
                    "apply_result": apply_result,
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_cross_spec_writeback_artifact(
    root: Path,
    *,
    orchestration_result: str,
    writeback_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-cross-spec-writeback" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T21:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                "artifact_generated_at": "2026-04-03T20:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "apply_result": "deferred",
                "writeback_state": writeback_state,
                "orchestration_result": orchestration_result,
                "orchestration_summaries": [
                    "no cross-spec writes executed in guarded writeback baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded cross-spec writeback baseline does not execute writes yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "writeback_state": writeback_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "cross_spec_writeback_state": writeback_state,
                            "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": writeback_state,
                    "orchestration_result": orchestration_result,
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_guarded_registry_artifact(
    root: Path,
    *,
    registry_result: str,
    registry_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-guarded-registry" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T22:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                "artifact_generated_at": "2026-04-03T21:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "writeback_state": "deferred",
                "registry_state": registry_state,
                "registry_result": registry_result,
                "registry_summaries": [
                    "no registry updates executed in guarded registry baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "guarded registry baseline does not update registries yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "registry_state": registry_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize frontend contract observations",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "registry_state": registry_state,
                            "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "registry_state": registry_state,
                    "registry_result": registry_result,
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_broader_governance_artifact(
    root: Path,
    *,
    governance_result: str,
    governance_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-broader-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-03T23:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                "artifact_generated_at": "2026-04-03T22:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "registry_state": "deferred",
                "governance_state": governance_state,
                "governance_result": governance_result,
                "governance_summaries": [
                    "no broader governance actions executed in broader governance baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "broader governance baseline does not execute final governance actions yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "governance_state": governance_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize broader governance review context",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "governance_state": governance_state,
                            "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "governance_state": governance_state,
                    "governance_result": governance_result,
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_governance_artifact(
    root: Path,
    *,
    final_governance_result: str,
    final_governance_state: str,
    remaining_blockers: list[str],
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T00:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                "artifact_generated_at": "2026-04-03T23:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "governance_state": "deferred",
                "final_governance_state": final_governance_state,
                "final_governance_result": final_governance_result,
                "final_governance_summaries": [
                    "no final governance actions executed in final governance baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final governance baseline does not execute code rewrite persistence yet"
                ],
                "steps": [
                    {
                        "spec_id": "001-auth",
                        "path": "specs/001-auth",
                        "final_governance_state": final_governance_state,
                        "pending_inputs": ["frontend_contract_observations"],
                        "suggested_next_actions": [
                            "materialize writeback persistence review context",
                            "re-run ai-sdlc verify constraints",
                        ],
                        "source_linkage": {
                            "final_governance_state": final_governance_state,
                            "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                        },
                    }
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "final_governance_state": final_governance_state,
                    "final_governance_result": final_governance_result,
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
