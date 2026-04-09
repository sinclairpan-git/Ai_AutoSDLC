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
from ai_sdlc.core.frontend_visual_a11y_evidence_provider import (
    FrontendVisualA11yEvidenceEvaluation,
    build_frontend_visual_a11y_evidence_artifact,
    write_frontend_visual_a11y_evidence_artifact,
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
from ai_sdlc.models.frontend_gate_policy import (
    build_mvp_frontend_gate_policy,
    build_p1_frontend_gate_policy_visual_a11y_foundation,
)
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


def _write_frontend_evidence_class_spec(
    root: Path,
    *,
    spec_rel: str,
    frontend_evidence_class: str,
) -> None:
    spec_dir = root / spec_rel
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text(
        "# Spec\n\n"
        "---\n"
        f'frontend_evidence_class: "{frontend_evidence_class}"\n'
        "---\n",
        encoding="utf-8",
    )


def _write_manifest_yaml(root: Path, text: str) -> None:
    (root / "program-manifest.yaml").write_text(
        text.strip() + "\n",
        encoding="utf-8",
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


def test_validate_manifest_frontend_evidence_class_mirror_missing(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                )
            ]
        )
    )

    assert res.valid is False
    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in err
        and "error_kind=mirror_missing" in err
        for err in res.errors
    )


def test_validate_manifest_frontend_evidence_class_mirror_invalid_value(
    tmp_path: Path,
) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                    frontend_evidence_class="framework",
                )
            ]
        )
    )

    assert res.valid is False
    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in err
        and "error_kind=mirror_invalid_value" in err
        for err in res.errors
    )


def test_validate_manifest_frontend_evidence_class_mirror_stale(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                    frontend_evidence_class="consumer_adoption",
                )
            ]
        )
    )

    assert res.valid is False
    assert any(
        "problem_family=frontend_evidence_class_mirror_drift" in err
        and "error_kind=mirror_stale" in err
        for err in res.errors
    )


def test_validate_manifest_frontend_evidence_class_mirror_valid(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    svc = ProgramService(tmp_path)

    res = svc.validate_manifest(
        ProgramManifest(
            specs=[
                ProgramSpecRef(
                    id="082-frontend-example",
                    path="specs/082-frontend-example",
                    depends_on=[],
                    frontend_evidence_class="framework_capability",
                )
            ]
        )
    )

    assert res.valid is True
    assert res.errors == []


def test_sync_frontend_evidence_class_manifest_execute_targeted(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
    owner: "team-a"
  - id: "050-non-frontend"
    path: "specs/050-non-frontend"
    depends_on: []
    owner: "team-b"
""",
    )
    (tmp_path / "specs" / "050-non-frontend").mkdir(parents=True, exist_ok=True)
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        spec_id="082-frontend-example",
        confirmed=True,
    )

    assert result.passed is True
    assert result.sync_result == "updated"
    assert result.updated_specs == ["082-frontend-example"]

    payload = yaml.safe_load((tmp_path / "program-manifest.yaml").read_text(encoding="utf-8"))
    specs = {item["id"]: item for item in payload["specs"]}
    assert specs["082-frontend-example"]["frontend_evidence_class"] == "framework_capability"
    assert specs["082-frontend-example"]["owner"] == "team-a"
    assert "frontend_evidence_class" not in specs["050-non-frontend"]
    assert specs["050-non-frontend"]["owner"] == "team-b"


def test_sync_frontend_evidence_class_manifest_execute_bulk(tmp_path: Path) -> None:
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/082-frontend-example",
        frontend_evidence_class="framework_capability",
    )
    _write_frontend_evidence_class_spec(
        tmp_path,
        spec_rel="specs/083-frontend-adoption",
        frontend_evidence_class="consumer_adoption",
    )
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
  - id: "083-frontend-adoption"
    path: "specs/083-frontend-adoption"
    depends_on: []
    frontend_evidence_class: "framework_capability"
""",
    )
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        confirmed=True,
    )

    assert result.passed is True
    assert result.sync_result == "updated"
    assert result.updated_specs == [
        "082-frontend-example",
        "083-frontend-adoption",
    ]

    payload = yaml.safe_load((tmp_path / "program-manifest.yaml").read_text(encoding="utf-8"))
    specs = {item["id"]: item for item in payload["specs"]}
    assert specs["082-frontend-example"]["frontend_evidence_class"] == "framework_capability"
    assert specs["083-frontend-adoption"]["frontend_evidence_class"] == "consumer_adoption"


def test_sync_frontend_evidence_class_manifest_blocks_when_footer_missing(
    tmp_path: Path,
) -> None:
    spec_dir = tmp_path / "specs" / "082-frontend-example"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "spec.md").write_text("# Spec\n", encoding="utf-8")
    _write_manifest_yaml(
        tmp_path,
        """
schema_version: "1"
specs:
  - id: "082-frontend-example"
    path: "specs/082-frontend-example"
    depends_on: []
""",
    )
    svc = ProgramService(tmp_path)

    result = svc.execute_frontend_evidence_class_sync(
        svc.load_manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.sync_result == "blocked"
    assert result.updated_specs == []
    assert any("082-frontend-example" in blocker for blocker in result.remaining_blockers)


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
        "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
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
        "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
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

    assert result.passed is False
    assert not observation_artifact_path(tmp_path / "specs" / "001-auth").is_file()
    assert (tmp_path / "governance" / "frontend" / "gates" / "gate.manifest.yaml").is_file()
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).is_file()
    assert (
        tmp_path / "governance" / "frontend" / "generation" / "generation.manifest.yaml"
    ).is_file()
    assert any(
        item.command
        == "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
        and item.status == "failed"
        and "explicit <frontend-source-root> required" in item.summary
        for item in result.command_results
    )
    assert any(
        item.command == "uv run ai-sdlc rules materialize-frontend-mvp"
        and item.status == "executed"
        for item in result.command_results
    )
    assert all(
        item.command != "uv run ai-sdlc verify constraints"
        for item in result.command_results
    )
    assert any(
        "explicit <frontend-source-root> required" in blocker
        for blocker in result.blockers
    )


def test_execute_frontend_remediation_runbook_passes_when_only_visual_a11y_policy_artifact_gap_remains(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_constitution(tmp_path)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).unlink()
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        spec_dir = tmp_path / "specs" / spec
        _write_frontend_contract_observations(spec_dir)
        _write_frontend_visual_a11y_evidence(
            spec_dir,
            [
                FrontendVisualA11yEvidenceEvaluation(
                    evaluation_id=f"{spec}-visual-a11y-pass",
                    target_id="user-create",
                    surface_id="page:user-create",
                    outcome="pass",
                    report_type="coverage-report",
                    severity="info",
                    location_anchor="specs",
                    quality_hint="fixture evidence",
                    changed_scope_explanation="071 pass fixture",
                )
            ],
        )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_remediation_runbook(
        _manifest(),
        generated_at="2026-04-07T16:00:00Z",
    )

    assert result.passed is True
    assert (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
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
    assert payload["passed"] is False
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert any(
        "explicit <frontend-source-root> required" in blocker
        for blocker in payload["remaining_blockers"]
    )
    assert payload["follow_up_commands"] == ["uv run ai-sdlc verify constraints"]
    assert payload["written_paths"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert any(
        item["command"]
        == "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
        and item["status"] == "failed"
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


def test_build_frontend_provider_handoff_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "stable_empty_artifact",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert handoff.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert (
        handoff.steps[0].source_linkage["runtime_attachment_status"]
        == "stable_empty_artifact"
    )


def test_build_frontend_provider_handoff_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "artifact_attached",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert handoff.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert handoff.steps[0].source_linkage["runtime_attachment_status"] == (
        "artifact_attached"
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


def test_build_frontend_provider_runtime_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "stable_empty_artifact",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert (
        request.steps[0].source_linkage["provider_runtime_state"] == "not_started"
    )


def test_build_frontend_provider_runtime_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_remediation_writeback_artifact(
        tmp_path,
        passed=False,
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "state": "required",
                "fix_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "action_commands": [],
                "source_linkage": {
                    "runtime_attachment_status": "artifact_attached",
                    "frontend_gate_verdict": "RETRY",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_runtime_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
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


def test_build_frontend_provider_patch_handoff_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "deferred",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert handoff.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert handoff.steps[0].patch_availability_state == "deferred"


def test_build_frontend_provider_patch_handoff_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "deferred",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    handoff = svc.build_frontend_provider_patch_handoff(_manifest())

    assert handoff.required is True
    assert [step.spec_id for step in handoff.steps] == ["001-auth"]
    assert handoff.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert handoff.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert handoff.steps[0].patch_availability_state == "deferred"


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


def test_build_frontend_provider_patch_apply_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "deferred",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].patch_availability_state == "deferred"


def test_build_frontend_provider_patch_apply_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_runtime_artifact(
        tmp_path,
        invocation_result="deferred",
        provider_execution_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "writeback_artifact_path": ".ai-sdlc/memory/frontend-remediation/latest.yaml",
                    "provider_runtime_state": "deferred",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_provider_patch_apply_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].patch_availability_state == "deferred"


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


def test_build_frontend_cross_spec_writeback_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "deferred",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].writeback_state == "not_started"


def test_build_frontend_cross_spec_writeback_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "deferred",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_cross_spec_writeback_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].writeback_state == "not_started"


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


def test_write_frontend_cross_spec_writeback_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "deferred",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_cross_spec_writeback_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_provider_patch_apply_artifact(
        tmp_path,
        apply_result="deferred",
        patch_apply_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "patch_availability_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "provider_runtime_artifact_path": ".ai-sdlc/memory/frontend-provider-runtime/latest.yaml",
                    "patch_apply_state": "deferred",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


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


def test_build_frontend_guarded_registry_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].registry_state == "not_started"


def test_build_frontend_guarded_registry_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_guarded_registry_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].registry_state == "not_started"


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


def test_write_frontend_guarded_registry_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_guarded_registry_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_cross_spec_writeback_artifact(
        tmp_path,
        orchestration_result="deferred",
        writeback_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "writeback_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "cross_spec_writeback_state": "deferred",
                    "provider_patch_apply_artifact_path": ".ai-sdlc/memory/frontend-provider-patch-apply/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


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


def test_build_frontend_broader_governance_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].governance_state == "not_started"


def test_build_frontend_broader_governance_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_broader_governance_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert [step.spec_id for step in request.steps] == ["001-auth"]
    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]
    assert request.steps[0].governance_state == "not_started"


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


def test_write_frontend_broader_governance_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_broader_governance_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_guarded_registry_artifact(
        tmp_path,
        registry_result="deferred",
        registry_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "registry_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "registry_state": "deferred",
                    "cross_spec_writeback_artifact_path": ".ai-sdlc/memory/frontend-cross-spec-writeback/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


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


def test_build_frontend_final_governance_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_governance_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_governance_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_governance_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_governance_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_broader_governance_artifact(
        tmp_path,
        governance_result="deferred",
        governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "governance_state": "deferred",
                    "guarded_registry_artifact_path": ".ai-sdlc/memory/frontend-guarded-registry/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


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


def test_build_frontend_writeback_persistence_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_writeback_persistence_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_writeback_persistence_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_writeback_persistence_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_writeback_persistence_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_governance_artifact(
        tmp_path,
        final_governance_result="deferred",
        final_governance_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "final_governance_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "broader_governance_artifact_path": ".ai-sdlc/memory/frontend-broader-governance/latest.yaml",
                },
            }
        ],
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

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


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


def test_build_frontend_persisted_write_proof_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.proof_state == "not_started"
    assert request.persistence_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T01:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].proof_state == "not_started"
    assert request.steps[0].source_linkage["proof_state"] == "not_started"


def test_execute_frontend_persisted_write_proof_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_persisted_write_proof(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.proof_state == "deferred"
    assert result.proof_result == "deferred"
    assert result.proof_summaries == [
        "no persisted write proof actions executed in persisted write proof baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["proof_state"] == "deferred"


def test_execute_frontend_persisted_write_proof_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_persisted_write_proof(_manifest(), confirmed=True)

    assert result.proof_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-persisted-write-proof"
        / "latest.yaml"
    ).exists()


def test_write_frontend_persisted_write_proof_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_persisted_write_proof_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-persisted-write-proof"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml"
    )
    assert payload["proof_state"] == "deferred"
    assert payload["proof_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["proof_summaries"] == [
        "no persisted write proof actions executed in persisted write proof baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["persisted_write_proof_artifact_path"]
        == ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
    )


def test_build_frontend_persisted_write_proof_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_persisted_write_proof_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_persisted_write_proof_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_persisted_write_proof_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_persisted_write_proof_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_writeback_persistence_artifact(
        tmp_path,
        persistence_result="deferred",
        persistence_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "persistence_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "persistence_state": "deferred",
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_persisted_write_proof_request(_manifest())
    result = svc.execute_frontend_persisted_write_proof(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_persisted_write_proof_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_publication_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_publication_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_publication_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_publication_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_publication_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "proof_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "proof_state": "deferred",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_publication_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_publication_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.publication_state == "not_started"
    assert request.proof_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T02:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].publication_state == "not_started"
    assert request.steps[0].source_linkage["publication_state"] == "not_started"


def test_execute_frontend_final_proof_publication_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_publication(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.publication_state == "deferred"
    assert result.publication_result == "deferred"
    assert result.publication_summaries == [
        "no final proof publication actions executed in final proof publication baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["publication_state"] == "deferred"


def test_execute_frontend_final_proof_publication_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_publication(_manifest(), confirmed=True)

    assert result.publication_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-publication"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_publication_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_persisted_write_proof_artifact(
        tmp_path,
        proof_result="deferred",
        proof_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_publication_request(_manifest())
    result = svc.execute_frontend_final_proof_publication(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_publication_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-publication"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml"
    )
    assert payload["publication_state"] == "deferred"
    assert payload["publication_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["publication_summaries"] == [
        "no final proof publication actions executed in final proof publication baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert (
        payload["source_linkage"]["final_proof_publication_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )


def test_build_frontend_final_proof_closure_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_closure_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_closure_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_closure_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_closure_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "publication_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "publication_state": "deferred",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_closure_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_closure_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.closure_state == "not_started"
    assert request.publication_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T03:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].closure_state == "not_started"
    assert request.steps[0].source_linkage["closure_state"] == "not_started"


def test_execute_frontend_final_proof_closure_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_closure(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.closure_state == "deferred"
    assert result.closure_result == "deferred"
    assert result.closure_summaries == [
        "no final proof closure actions executed in final proof closure baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["closure_state"] == "deferred"


def test_execute_frontend_final_proof_closure_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_closure(_manifest(), confirmed=True)

    assert result.closure_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-closure"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_closure_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_publication_artifact(
        tmp_path,
        publication_result="deferred",
        publication_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_closure_request(_manifest())
    result = svc.execute_frontend_final_proof_closure(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_closure_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-closure"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )
    assert payload["artifact_generated_at"] == "2026-04-04T03:00:00Z"
    assert payload["publication_state"] == "deferred"
    assert payload["closure_state"] == "deferred"
    assert payload["closure_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["closure_summaries"] == [
        "no final proof closure actions executed in final proof closure baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert payload["steps"][0]["closure_state"] == "not_started"
    assert (
        payload["source_linkage"]["final_proof_publication_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml"
    )
    assert (
        payload["source_linkage"]["final_proof_closure_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )


def test_build_frontend_final_proof_archive_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_archive_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_archive_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "closure_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "closure_state": "deferred",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_request_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.archive_state == "not_started"
    assert request.closure_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T04:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].archive_state == "not_started"
    assert request.steps[0].source_linkage["archive_state"] == "not_started"


def test_execute_frontend_final_proof_archive_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive(_manifest(), confirmed=True)

    assert result.passed is False
    assert result.confirmed is True
    assert result.archive_state == "deferred"
    assert result.archive_result == "deferred"
    assert result.archive_summaries == [
        "no final proof archive actions executed in final proof archive baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["archive_state"] == "deferred"


def test_build_frontend_final_proof_archive_thread_archive_request_uses_archive_artifact(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.thread_archive_state == "not_started"
    assert request.archive_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T05:00:00Z"
    assert request.written_paths == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].thread_archive_state == "not_started"
    assert (
        request.steps[0].source_linkage["final_proof_archive_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )


def test_build_frontend_final_proof_archive_thread_archive_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_thread_archive_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_thread_archive_request(_manifest())

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_final_proof_archive_thread_archive_returns_deferred_result_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_thread_archive(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.confirmed is True
    assert result.thread_archive_state == "deferred"
    assert result.thread_archive_result == "deferred"
    assert result.thread_archive_summaries == [
        "no thread archive actions executed in final proof archive thread archive baseline"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == ["spec 001-auth remediation still required"]
    assert result.source_linkage["thread_archive_state"] == "deferred"
    assert "project_cleanup_state" not in result.source_linkage
    assert any(
        "does not execute project cleanup actions yet" in item
        for item in result.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_uses_thread_archive_execute_truth(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.required is True
    assert request.confirmation_required is True
    assert request.project_cleanup_state == "not_started"
    assert request.thread_archive_state == "deferred"
    assert (
        request.artifact_source_path
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )
    assert request.artifact_generated_at == "2026-04-04T05:00:00Z"
    assert request.written_paths == []
    assert request.cleanup_targets_state == "missing"
    assert request.cleanup_targets == []
    assert request.cleanup_target_eligibility_state == "missing"
    assert request.cleanup_target_eligibility == []
    assert request.cleanup_preview_plan_state == "missing"
    assert request.cleanup_preview_plan == []
    assert request.cleanup_mutation_proposal_state == "missing"
    assert request.cleanup_mutation_proposal == []
    assert request.cleanup_mutation_proposal_approval_state == "missing"
    assert request.cleanup_mutation_proposal_approval == []
    assert request.cleanup_mutation_execution_gating_state == "missing"
    assert request.cleanup_mutation_execution_gating == []
    assert request.steps[0].spec_id == "001-auth"
    assert request.steps[0].project_cleanup_state == "not_started"
    assert (
        request.steps[0].source_linkage["thread_archive_result"] == "deferred"
    )
    assert (
        request.steps[0].source_linkage["final_proof_archive_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )
    assert request.source_linkage["cleanup_targets_state"] == "missing"
    assert request.source_linkage["cleanup_target_eligibility_state"] == "missing"
    assert request.source_linkage["cleanup_preview_plan_state"] == "missing"
    assert request.source_linkage["cleanup_mutation_proposal_state"] == "missing"
    assert (
        request.source_linkage["cleanup_mutation_proposal_approval_state"] == "missing"
    )
    assert (
        request.source_linkage["cleanup_mutation_execution_gating_state"] == "missing"
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )

    assert request.steps[0].pending_inputs == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert request.steps[0].suggested_next_actions == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_project_cleanup_request_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )

    assert request.steps[0].pending_inputs == ["frontend_visual_a11y_issue_review"]
    assert request.steps[0].suggested_next_actions == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_build_frontend_final_proof_archive_project_cleanup_request_uses_explicit_empty_cleanup_targets(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[],
        cleanup_mutation_proposal_approval=[],
        cleanup_mutation_execution_gating=[],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_targets_state == "empty"
    assert request.cleanup_targets == []
    assert request.cleanup_target_eligibility_state == "empty"
    assert request.cleanup_target_eligibility == []
    assert request.cleanup_preview_plan_state == "empty"
    assert request.cleanup_preview_plan == []
    assert request.cleanup_mutation_proposal_state == "empty"
    assert request.cleanup_mutation_proposal == []
    assert request.cleanup_mutation_proposal_approval_state == "empty"
    assert request.cleanup_mutation_proposal_approval == []
    assert request.cleanup_mutation_execution_gating_state == "empty"
    assert request.cleanup_mutation_execution_gating == []
    assert request.warnings == [
        "final proof archive baseline defers thread archive and cleanup actions",
        "final proof archive thread archive baseline does not execute project cleanup actions yet",
    ]


def test_build_frontend_final_proof_archive_project_cleanup_request_preserves_listed_cleanup_targets(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    cleanup_targets = [
        {
            "target_id": "cleanup-thread-archive-report",
            "path": "specs/001-auth/threads/archive-001.md",
            "kind": "thread_archive",
        },
        {
            "target_id": "cleanup-spec-dir",
            "path": "specs/002-course",
            "kind": "spec_dir",
        },
    ]
    cleanup_target_eligibility = [
        {
            "target_id": "cleanup-thread-archive-report",
            "eligibility": "eligible",
            "reason": "thread archive report may proceed to preview planning truth",
        },
        {
            "target_id": "cleanup-spec-dir",
            "eligibility": "eligible",
            "reason": "explicit cleanup target may proceed to future planning truth",
        },
    ]
    cleanup_preview_plan = [
        {
            "target_id": "cleanup-thread-archive-report",
            "planned_action": "archive_thread_report",
            "reason": "preview canonical archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "planned_action": "remove_spec_dir",
            "reason": "preview canonical spec cleanup action",
        },
    ]
    cleanup_mutation_proposal = [
        {
            "target_id": "cleanup-thread-archive-report",
            "proposed_action": "archive_thread_report",
            "reason": "proposal mirrors previewed archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "proposed_action": "remove_spec_dir",
            "reason": "proposal mirrors previewed spec cleanup action",
        },
    ]
    cleanup_mutation_proposal_approval = [
        {
            "target_id": "cleanup-thread-archive-report",
            "approved_action": "archive_thread_report",
            "reason": "explicit approval matches the proposed archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "approved_action": "remove_spec_dir",
            "reason": "explicit approval matches the proposed spec cleanup action",
        },
    ]
    cleanup_mutation_execution_gating = [
        {
            "target_id": "cleanup-thread-archive-report",
            "gated_action": "archive_thread_report",
            "reason": "execution gating matches the approved archive-only cleanup action",
        },
        {
            "target_id": "cleanup-spec-dir",
            "gated_action": "remove_spec_dir",
            "reason": "execution gating matches the approved spec cleanup action",
        },
    ]
    cleanup_targets[0]["cleanup_action"] = "archive_thread_report"
    cleanup_targets[1]["cleanup_action"] = "remove_spec_dir"
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=cleanup_targets,
        cleanup_target_eligibility=cleanup_target_eligibility,
        cleanup_preview_plan=cleanup_preview_plan,
        cleanup_mutation_proposal=cleanup_mutation_proposal,
        cleanup_mutation_proposal_approval=cleanup_mutation_proposal_approval,
        cleanup_mutation_execution_gating=cleanup_mutation_execution_gating,
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_targets_state == "listed"
    assert request.cleanup_targets == cleanup_targets
    assert request.cleanup_target_eligibility_state == "listed"
    assert request.cleanup_target_eligibility == cleanup_target_eligibility
    assert request.cleanup_preview_plan_state == "listed"
    assert request.cleanup_preview_plan == cleanup_preview_plan
    assert request.cleanup_mutation_proposal_state == "listed"
    assert request.cleanup_mutation_proposal == cleanup_mutation_proposal
    assert request.cleanup_mutation_proposal_approval_state == "listed"
    assert (
        request.cleanup_mutation_proposal_approval
        == cleanup_mutation_proposal_approval
    )
    assert request.cleanup_mutation_execution_gating_state == "listed"
    assert (
        request.cleanup_mutation_execution_gating
        == cleanup_mutation_execution_gating
    )
    assert request.source_linkage["cleanup_target_eligibility_state"] == "listed"
    assert request.source_linkage["cleanup_preview_plan_state"] == "listed"
    assert request.source_linkage["cleanup_mutation_proposal_state"] == "listed"
    assert (
        request.source_linkage["cleanup_mutation_proposal_approval_state"] == "listed"
    )
    assert (
        request.source_linkage["cleanup_mutation_execution_gating_state"] == "listed"
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_target_eligibility_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_target_eligibility_state == "missing"
    assert request.cleanup_target_eligibility == []
    assert any(
        "cleanup_target_eligibility must be a list" in item for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_misaligned_cleanup_target_eligibility(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-spec-dir",
                "eligibility": "eligible",
                "reason": "wrong target id",
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_target_eligibility_state == "listed"
    assert len(request.cleanup_target_eligibility) == 1
    assert any(
        "cleanup_target_eligibility target_id set does not match cleanup_targets"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_preview_plan_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_preview_plan_state == "missing"
    assert request.cleanup_preview_plan == []
    assert any(
        "cleanup_preview_plan must be a list" in item for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_preview_plan_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-thread-archive-report",
                "planned_action": "remove_spec_dir",
                "reason": "preview incorrectly proposes destructive cleanup",
            },
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_preview_plan_state == "listed"
    assert len(request.cleanup_preview_plan) == 2
    assert any(
        "cleanup_preview_plan target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_preview_plan target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_preview_plan target_id=cleanup-thread-archive-report planned_action does not match cleanup_action"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_state == "missing"
    assert request.cleanup_mutation_proposal == []
    assert any(
        "cleanup_mutation_proposal must be a list" in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            }
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal incorrectly changes cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_state == "listed"
    assert len(request.cleanup_mutation_proposal) == 2
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-thread-archive-report proposed_action does not match cleanup_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_approval_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[],
        cleanup_mutation_proposal_approval="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_approval_state == "missing"
    assert request.cleanup_mutation_proposal_approval == []
    assert any(
        "cleanup_mutation_proposal_approval must be a list" in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_proposal_approval_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            }
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "remove_spec_dir",
                "reason": "approval incorrectly changes cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "approved_action": "remove_spec_dir",
                "reason": "approval references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_proposal_approval_state == "listed"
    assert len(request.cleanup_mutation_proposal_approval) == 2
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report approved_action does not match cleanup_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-thread-archive-report approved_action does not match proposed_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_proposal_approval target_id=cleanup-spec-dir does not appear in cleanup_mutation_proposal"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_execution_gating_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[],
        cleanup_target_eligibility=[],
        cleanup_preview_plan=[],
        cleanup_mutation_proposal=[],
        cleanup_mutation_proposal_approval=[],
        cleanup_mutation_execution_gating="cleanup-thread-archive-report",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_execution_gating_state == "missing"
    assert request.cleanup_mutation_execution_gating == []
    assert any(
        "cleanup_mutation_execution_gating must be a list" in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_mutation_execution_gating_alignment(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            }
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "blocked",
                "reason": "thread archive artifact remains deferred",
            }
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview references unknown target",
            }
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "approval mirrors the canonical cleanup action",
            }
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating incorrectly changes cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating references unknown target",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_mutation_execution_gating_state == "listed"
    assert len(request.cleanup_mutation_execution_gating) == 2
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report is not eligible"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report does not appear in cleanup_preview_plan"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report gated_action does not match cleanup_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-thread-archive-report gated_action does not match approved_action"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-spec-dir does not exist in cleanup_targets"
        in item
        for item in request.warnings
    )
    assert any(
        "cleanup_mutation_execution_gating target_id=cleanup-spec-dir does not appear in cleanup_mutation_proposal_approval"
        in item
        for item in request.warnings
    )


def test_build_frontend_final_proof_archive_project_cleanup_request_warns_on_invalid_cleanup_targets_structure(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets="specs/001-auth",
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())

    assert request.cleanup_targets_state == "missing"
    assert request.cleanup_targets == []
    assert request.cleanup_target_eligibility_state == "missing"
    assert request.cleanup_target_eligibility == []
    assert any(
        "cleanup_targets must be a list" in item for item in request.warnings
    )


def test_execute_frontend_final_proof_archive_project_cleanup_executes_canonical_gated_targets_when_confirmed(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    archive_report = tmp_path / "specs" / "001-auth" / "threads" / "archive-001.md"
    archive_report.parent.mkdir(parents=True, exist_ok=True)
    archive_report.write_text("# archived thread\n", encoding="utf-8")
    spec_dir = tmp_path / "specs" / "002-course"
    (spec_dir / "notes").mkdir(parents=True, exist_ok=True)
    (spec_dir / "notes" / "todo.md").write_text("cleanup me\n", encoding="utf-8")
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            },
            {
                "target_id": "cleanup-spec-dir",
                "path": "specs/002-course",
                "kind": "spec_dir",
                "cleanup_action": "remove_spec_dir",
            },
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "eligible",
                "reason": "thread archive report may proceed to preview planning truth",
            },
            {
                "target_id": "cleanup-spec-dir",
                "eligibility": "eligible",
                "reason": "explicit cleanup target may proceed to future planning truth",
            },
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-thread-archive-report",
                "planned_action": "archive_thread_report",
                "reason": "preview canonical archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview canonical spec cleanup action",
            },
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors previewed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal mirrors previewed spec cleanup action",
            },
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "explicit approval matches the proposed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "approved_action": "remove_spec_dir",
                "reason": "explicit approval matches the proposed spec cleanup action",
            },
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "archive_thread_report",
                "reason": "execution gating matches the approved archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating matches the approved spec cleanup action",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is True
    assert result.confirmed is True
    assert result.project_cleanup_state == "completed"
    assert result.project_cleanup_result == "completed"
    assert result.project_cleanup_summaries == [
        "executed 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
    ]
    assert result.cleanup_targets_state == "listed"
    assert len(result.cleanup_targets) == 2
    assert result.cleanup_target_eligibility_state == "listed"
    assert len(result.cleanup_target_eligibility) == 2
    assert result.cleanup_preview_plan_state == "listed"
    assert len(result.cleanup_preview_plan) == 2
    assert result.cleanup_mutation_proposal_state == "listed"
    assert len(result.cleanup_mutation_proposal) == 2
    assert result.cleanup_mutation_proposal_approval_state == "listed"
    assert len(result.cleanup_mutation_proposal_approval) == 2
    assert result.cleanup_mutation_execution_gating_state == "listed"
    assert len(result.cleanup_mutation_execution_gating) == 2
    assert result.written_paths == [
        "specs/001-auth/threads/archive-001.md",
        "specs/002-course",
    ]
    assert result.remaining_blockers == []
    assert result.source_linkage["thread_archive_state"] == "deferred"
    assert result.source_linkage["project_cleanup_state"] == "completed"
    assert result.source_linkage["project_cleanup_result"] == "completed"
    assert result.source_linkage["cleanup_targets_state"] == "listed"
    assert result.source_linkage["cleanup_target_eligibility_state"] == "listed"
    assert result.source_linkage["cleanup_preview_plan_state"] == "listed"
    assert result.source_linkage["cleanup_mutation_proposal_state"] == "listed"
    assert (
        result.source_linkage["cleanup_mutation_proposal_approval_state"] == "listed"
    )
    assert (
        result.source_linkage["cleanup_mutation_execution_gating_state"] == "listed"
    )
    assert result.warnings == []
    assert not archive_report.exists()
    assert not spec_dir.exists()


def test_execute_frontend_final_proof_archive_project_cleanup_returns_partial_result_when_a_target_is_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    spec_dir = tmp_path / "specs" / "002-course"
    (spec_dir / "notes").mkdir(parents=True, exist_ok=True)
    (spec_dir / "notes" / "todo.md").write_text("cleanup me\n", encoding="utf-8")
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )
    _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
        tmp_path,
        cleanup_targets=[
            {
                "target_id": "cleanup-thread-archive-report",
                "path": "specs/001-auth/threads/archive-001.md",
                "kind": "thread_archive",
                "cleanup_action": "archive_thread_report",
            },
            {
                "target_id": "cleanup-spec-dir",
                "path": "specs/002-course",
                "kind": "spec_dir",
                "cleanup_action": "remove_spec_dir",
            },
        ],
        cleanup_target_eligibility=[
            {
                "target_id": "cleanup-thread-archive-report",
                "eligibility": "eligible",
                "reason": "thread archive report may proceed to preview planning truth",
            },
            {
                "target_id": "cleanup-spec-dir",
                "eligibility": "eligible",
                "reason": "explicit cleanup target may proceed to future planning truth",
            },
        ],
        cleanup_preview_plan=[
            {
                "target_id": "cleanup-thread-archive-report",
                "planned_action": "archive_thread_report",
                "reason": "preview canonical archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "planned_action": "remove_spec_dir",
                "reason": "preview canonical spec cleanup action",
            },
        ],
        cleanup_mutation_proposal=[
            {
                "target_id": "cleanup-thread-archive-report",
                "proposed_action": "archive_thread_report",
                "reason": "proposal mirrors previewed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "proposed_action": "remove_spec_dir",
                "reason": "proposal mirrors previewed spec cleanup action",
            },
        ],
        cleanup_mutation_proposal_approval=[
            {
                "target_id": "cleanup-thread-archive-report",
                "approved_action": "archive_thread_report",
                "reason": "explicit approval matches the proposed archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "approved_action": "remove_spec_dir",
                "reason": "explicit approval matches the proposed spec cleanup action",
            },
        ],
        cleanup_mutation_execution_gating=[
            {
                "target_id": "cleanup-thread-archive-report",
                "gated_action": "archive_thread_report",
                "reason": "execution gating matches the approved archive-only cleanup action",
            },
            {
                "target_id": "cleanup-spec-dir",
                "gated_action": "remove_spec_dir",
                "reason": "execution gating matches the approved spec cleanup action",
            },
        ],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.passed is False
    assert result.confirmed is True
    assert result.project_cleanup_state == "partial"
    assert result.project_cleanup_result == "partial"
    assert result.project_cleanup_summaries == [
        "executed 1 of 2 cleanup mutation(s) from canonical cleanup_mutation_execution_gating"
    ]
    assert result.written_paths == ["specs/002-course"]
    assert result.remaining_blockers == ["cleanup-thread-archive-report"]
    assert result.source_linkage["project_cleanup_state"] == "partial"
    assert result.source_linkage["project_cleanup_result"] == "partial"
    assert any(
        "cleanup target cleanup-thread-archive-report is missing at specs/001-auth/threads/archive-001.md"
        in item
        for item in result.warnings
    )
    assert not spec_dir.exists()


def test_execute_frontend_final_proof_archive_project_cleanup_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        confirmed=True,
    )

    assert result.project_cleanup_state == "blocked"
    assert result.project_cleanup_result == "blocked"
    assert result.project_cleanup_summaries == [
        "no cleanup mutations listed in canonical cleanup_mutation_execution_gating"
    ]
    assert result.written_paths == []
    assert result.remaining_blockers == []
    assert result.warnings == []
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive-project-cleanup"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_archive_project_cleanup_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(_manifest())
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_project_cleanup_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive-project-cleanup"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["project_cleanup_result"] == "blocked"
    assert payload["project_cleanup_state"] == "blocked"
    assert payload["project_cleanup_summaries"] == [
        "no cleanup mutations listed in canonical cleanup_mutation_execution_gating"
    ]
    assert payload["thread_archive_state"] == "deferred"
    assert payload["cleanup_targets_state"] == "missing"
    assert payload["cleanup_targets"] == []
    assert payload["cleanup_target_eligibility_state"] == "missing"
    assert payload["cleanup_target_eligibility"] == []
    assert payload["cleanup_preview_plan_state"] == "missing"
    assert payload["cleanup_preview_plan"] == []
    assert payload["cleanup_mutation_proposal_state"] == "missing"
    assert payload["cleanup_mutation_proposal"] == []
    assert payload["cleanup_mutation_proposal_approval_state"] == "missing"
    assert payload["cleanup_mutation_proposal_approval"] == []
    assert payload["cleanup_mutation_execution_gating_state"] == "missing"
    assert payload["cleanup_mutation_execution_gating"] == []
    assert payload["confirmed"] is True
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == []
    assert (
        payload["source_linkage"]["final_proof_archive_project_cleanup_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml"
    )
    assert payload["source_linkage"]["project_cleanup_state"] == "blocked"
    assert payload["source_linkage"]["project_cleanup_result"] == "blocked"


def test_write_frontend_final_proof_archive_project_cleanup_artifact_preserves_stable_empty_visual_a11y_pending_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_evidence_stable_empty"],
                "suggested_next_actions": [
                    "review stable empty frontend visual / a11y evidence",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_project_cleanup_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == [
        "frontend_visual_a11y_evidence_stable_empty"
    ]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review stable empty frontend visual / a11y evidence",
        "re-run ai-sdlc verify constraints",
    ]


def test_write_frontend_final_proof_archive_project_cleanup_artifact_preserves_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_archive_artifact(
        tmp_path,
        archive_result="deferred",
        archive_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
        steps=[
            {
                "spec_id": "001-auth",
                "path": "specs/001-auth",
                "archive_state": "deferred",
                "pending_inputs": ["frontend_visual_a11y_issue_review"],
                "suggested_next_actions": [
                    "review frontend visual / a11y issue findings",
                    "re-run ai-sdlc verify constraints",
                ],
                "source_linkage": {
                    "archive_state": "deferred",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            }
        ],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_project_cleanup_request(
        _manifest()
    )
    result = svc.execute_frontend_final_proof_archive_project_cleanup(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_project_cleanup_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["steps"][0]["pending_inputs"] == ["frontend_visual_a11y_issue_review"]
    assert payload["steps"][0]["suggested_next_actions"] == [
        "review frontend visual / a11y issue findings",
        "re-run ai-sdlc verify constraints",
    ]


def test_execute_frontend_final_proof_archive_does_not_write_artifact_by_default(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    result = svc.execute_frontend_final_proof_archive(_manifest(), confirmed=True)

    assert result.archive_state == "deferred"
    assert not (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive"
        / "latest.yaml"
    ).exists()


def test_write_frontend_final_proof_archive_artifact_emits_canonical_yaml(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_frontend_final_proof_closure_artifact(
        tmp_path,
        closure_result="deferred",
        closure_state="deferred",
        remaining_blockers=["spec 001-auth remediation still required"],
    )

    svc = ProgramService(tmp_path)
    request = svc.build_frontend_final_proof_archive_request(_manifest())
    result = svc.execute_frontend_final_proof_archive(
        _manifest(),
        request=request,
        confirmed=True,
    )

    artifact_path = svc.write_frontend_final_proof_archive_artifact(
        _manifest(),
        request=request,
        result=result,
    )

    assert artifact_path == (
        tmp_path
        / ".ai-sdlc"
        / "memory"
        / "frontend-final-proof-archive"
        / "latest.yaml"
    )
    payload = yaml.safe_load(artifact_path.read_text(encoding="utf-8"))
    assert payload["manifest_path"] == "program-manifest.yaml"
    assert (
        payload["artifact_source_path"]
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )
    assert payload["artifact_generated_at"] == "2026-04-04T04:00:00Z"
    assert payload["closure_state"] == "deferred"
    assert payload["archive_state"] == "deferred"
    assert payload["archive_result"] == "deferred"
    assert payload["confirmed"] is True
    assert payload["archive_summaries"] == [
        "no final proof archive actions executed in final proof archive baseline"
    ]
    assert payload["written_paths"] == []
    assert payload["remaining_blockers"] == ["spec 001-auth remediation still required"]
    assert payload["steps"][0]["spec_id"] == "001-auth"
    assert payload["steps"][0]["archive_state"] == "not_started"
    assert (
        payload["source_linkage"]["final_proof_closure_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml"
    )
    assert (
        payload["source_linkage"]["final_proof_archive_artifact_path"]
        == ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml"
    )


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


def test_build_status_surfaces_frontend_readiness_gap_when_071_visual_a11y_evidence_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
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
    assert readiness.state == "retry"
    assert "frontend_visual_a11y_evidence_input" in readiness.coverage_gaps
    assert any("missing explicit evidence input" in blocker for blocker in readiness.blockers)
    assert readiness.source_linkage["frontend_gate_verdict"] == "RETRY"


def test_build_integration_dry_run_surfaces_visual_a11y_evidence_remediation_input_when_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_evidence_input" in remediation.fix_inputs
    assert (
        "materialize frontend visual / a11y evidence input"
        in remediation.suggested_actions
    )
    assert remediation.recommended_commands == ["uv run ai-sdlc verify constraints"]


def test_build_integration_dry_run_surfaces_stable_empty_visual_a11y_evidence_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        spec_dir = tmp_path / "specs" / spec
        _write_frontend_contract_observations(spec_dir)
        _write_frontend_visual_a11y_evidence(spec_dir, [])

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_evidence_stable_empty" in remediation.fix_inputs
    assert (
        "review stable empty frontend visual / a11y evidence"
        in remediation.suggested_actions
    )
    assert "materialize frontend visual / a11y evidence input" not in remediation.suggested_actions
    assert remediation.recommended_commands == ["uv run ai-sdlc verify constraints"]


def test_build_integration_dry_run_surfaces_visual_a11y_issue_review_input(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        spec_dir = tmp_path / "specs" / spec
        _write_frontend_contract_observations(spec_dir)
        _write_frontend_visual_a11y_evidence(
            spec_dir,
            [
                FrontendVisualA11yEvidenceEvaluation(
                    evaluation_id=f"{spec}-visual-a11y-issue",
                    target_id="user-create",
                    surface_id="success-feedback",
                    outcome="issue",
                    report_type="violation-report",
                    severity="medium",
                    location_anchor="feedback.banner",
                    quality_hint="review success feedback visibility and semantics",
                    changed_scope_explanation="071 issue fixture",
                )
            ],
        )

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_issue_review" in remediation.fix_inputs
    assert (
        "review frontend visual / a11y issue findings"
        in remediation.suggested_actions
    )
    assert "frontend_visual_a11y_evidence_stable_empty" not in remediation.fix_inputs
    assert remediation.recommended_commands == ["uv run ai-sdlc verify constraints"]


def test_build_integration_dry_run_surfaces_visual_a11y_policy_artifact_remediation_input_when_missing(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)
    _write_minimal_frontend_contract_page_artifacts(tmp_path)
    materialize_frontend_gate_policy_artifacts(
        tmp_path,
        build_p1_frontend_gate_policy_visual_a11y_foundation(),
    )
    (
        tmp_path
        / "governance"
        / "frontend"
        / "gates"
        / "visual-a11y-evidence-boundary.yaml"
    ).unlink()
    materialize_frontend_generation_constraint_artifacts(
        tmp_path,
        build_mvp_frontend_generation_constraints(),
    )
    for spec in ("001-auth", "002-course", "003-enroll"):
        _write_frontend_contract_observations(tmp_path / "specs" / spec)

    svc = ProgramService(tmp_path)
    plan = svc.build_integration_dry_run(_manifest())

    step = next(item for item in plan.steps if item.spec_id == "001-auth")
    remediation = step.frontend_remediation_input
    assert remediation is not None
    assert "frontend_visual_a11y_policy_artifacts" in remediation.fix_inputs
    assert (
        "materialize frontend visual / a11y policy artifacts"
        in remediation.suggested_actions
    )
    assert remediation.recommended_commands == [
        "uv run ai-sdlc rules materialize-frontend-mvp",
        "uv run ai-sdlc verify constraints",
    ]


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


def test_build_frontend_solution_confirmation_recommends_enterprise_defaults_in_simple_mode(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(_manifest())

    assert snapshot.decision_status == "recommended"
    assert snapshot.preflight_status == "ready"
    assert snapshot.recommended_frontend_stack == "vue2"
    assert snapshot.recommended_provider_id == "enterprise-vue2"
    assert snapshot.recommended_style_pack_id == "enterprise-default"
    assert snapshot.requested_frontend_stack == "vue2"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.requested_style_pack_id == "enterprise-default"
    assert snapshot.effective_frontend_stack == "vue2"
    assert snapshot.effective_provider_id == "enterprise-vue2"
    assert snapshot.effective_style_pack_id == "enterprise-default"
    assert snapshot.recommended_backend_stack == "fastapi"
    assert snapshot.recommended_api_collab_mode == "typed-bff"
    assert snapshot.style_fidelity_status == "full"
    assert snapshot.provider_mode == "normal"


def test_build_frontend_solution_confirmation_recommends_public_fallback_in_simple_mode_when_enterprise_not_eligible(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
    )

    assert snapshot.decision_status == "recommended"
    assert snapshot.preflight_status == "ready"
    assert snapshot.recommended_frontend_stack == "vue3"
    assert snapshot.recommended_provider_id == "public-primevue"
    assert snapshot.recommended_style_pack_id == "modern-saas"
    assert snapshot.requested_frontend_stack == "vue3"
    assert snapshot.requested_provider_id == "public-primevue"
    assert snapshot.requested_style_pack_id == "modern-saas"
    assert snapshot.effective_frontend_stack == "vue3"
    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_style_pack_id == "modern-saas"
    assert snapshot.availability_summary.failed_check_ids == [
        "company-registry-token"
    ]
    assert snapshot.style_fidelity_status == "full"
    assert snapshot.provider_mode == "normal"


def test_build_frontend_solution_confirmation_requires_explicit_cross_stack_fallback_for_enterprise_request(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_frontend_stack="vue2",
        requested_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
    )

    assert snapshot.decision_status == "fallback_required"
    assert snapshot.preflight_status == "warning"
    assert snapshot.requested_frontend_stack == "vue2"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.requested_style_pack_id == "enterprise-default"
    assert snapshot.effective_frontend_stack == "vue3"
    assert snapshot.effective_provider_id == "public-primevue"
    assert snapshot.effective_style_pack_id == "modern-saas"
    assert snapshot.provider_mode == "cross_stack_fallback"
    assert snapshot.fallback_reason_code == "enterprise_provider_unavailable"
    assert snapshot.availability_summary.failed_check_ids == [
        "company-registry-token"
    ]


def test_build_frontend_solution_confirmation_blocks_when_enterprise_unavailable_and_no_fallback_candidate(
    tmp_path: Path,
) -> None:
    for p in ("specs/001-auth", "specs/002-course", "specs/003-enroll"):
        (tmp_path / p).mkdir(parents=True)

    svc = ProgramService(tmp_path)
    snapshot = svc.build_frontend_solution_confirmation(
        _manifest(),
        requested_frontend_stack="vue2",
        requested_provider_id="enterprise-vue2",
        requested_style_pack_id="enterprise-default",
        enterprise_provider_eligible=False,
        failed_preflight_check_ids=["company-registry-token"],
        fallback_candidate_available=False,
    )

    assert snapshot.decision_status == "blocked"
    assert snapshot.preflight_status == "blocked"
    assert snapshot.requested_frontend_stack == "vue2"
    assert snapshot.requested_provider_id == "enterprise-vue2"
    assert snapshot.requested_style_pack_id == "enterprise-default"
    assert snapshot.effective_frontend_stack == "vue2"
    assert snapshot.effective_provider_id == "enterprise-vue2"
    assert snapshot.effective_style_pack_id == "enterprise-default"
    assert snapshot.provider_mode == "normal"
    assert snapshot.fallback_reason_code == "enterprise_provider_unavailable"


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


def _write_frontend_visual_a11y_evidence(
    spec_dir: Path,
    evaluations: list[FrontendVisualA11yEvidenceEvaluation],
) -> None:
    artifact = build_frontend_visual_a11y_evidence_artifact(
        evaluations=evaluations,
        provider_kind="manual",
        provider_name="test-fixture",
        generated_at="2026-04-07T15:00:00Z",
    )
    write_frontend_visual_a11y_evidence_artifact(spec_dir, artifact)


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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
                "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
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
            "suggested_actions": ["materialize frontend gate policy artifacts"],
            "action_commands": ["uv run ai-sdlc rules materialize-frontend-mvp"],
            "source_linkage": {
                "runtime_attachment_status": "attached",
                "frontend_gate_verdict": "RETRY",
            },
        },
    ]
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
                "steps": list(steps or default_steps),
                "action_commands": [
                    "uv run ai-sdlc scan <frontend-source-root> --frontend-contract-spec-dir specs/001-auth"
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    default_steps: list[dict[str, object]] = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-broader-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
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
    ]
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
                "steps": list(steps or default_steps),
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
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-governance" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
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
    ]
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
                "steps": list(steps or default_steps),
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


def _write_frontend_writeback_persistence_artifact(
    root: Path,
    *,
    persistence_result: str,
    persistence_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-writeback-persistence" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "persistence_state": persistence_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize persisted write proof review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "persistence_state": persistence_state,
                "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T01:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                "artifact_generated_at": "2026-04-04T00:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "final_governance_state": "deferred",
                "persistence_state": persistence_state,
                "persistence_result": persistence_result,
                "persistence_summaries": [
                    "no writeback persistence actions executed in writeback persistence baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "writeback persistence baseline does not produce persisted write proof yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "final_governance_state": "deferred",
                    "persistence_state": persistence_state,
                    "persistence_result": persistence_result,
                    "final_governance_artifact_path": ".ai-sdlc/memory/frontend-final-governance/latest.yaml",
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_persisted_write_proof_artifact(
    root: Path,
    *,
    proof_result: str,
    proof_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-persisted-write-proof" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "proof_state": proof_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof publication review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "proof_state": proof_state,
                "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T02:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                "artifact_generated_at": "2026-04-04T01:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "persistence_state": "deferred",
                "proof_state": proof_state,
                "proof_result": proof_result,
                "proof_summaries": [
                    "no persisted write proof actions executed in persisted write proof baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "persisted write proof baseline does not persist proof artifacts yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "persistence_state": "deferred",
                    "proof_state": proof_state,
                    "proof_result": proof_result,
                    "writeback_persistence_artifact_path": ".ai-sdlc/memory/frontend-writeback-persistence/latest.yaml",
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_publication_artifact(
    root: Path,
    *,
    publication_result: str,
    publication_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-publication" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "publication_state": publication_state,
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof closure review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "publication_state": publication_state,
                "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T03:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                "artifact_generated_at": "2026-04-04T02:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "proof_state": "deferred",
                "publication_state": publication_state,
                "publication_result": publication_result,
                "publication_summaries": [
                    "no final proof publication actions executed in final proof publication baseline"
                ],
                "existing_written_paths": [],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof publication baseline does not persist publication artifacts yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "proof_state": "deferred",
                    "publication_state": publication_state,
                    "publication_result": publication_result,
                    "persisted_write_proof_artifact_path": ".ai-sdlc/memory/frontend-persisted-write-proof/latest.yaml",
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_closure_artifact(
    root: Path,
    *,
    closure_result: str,
    closure_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-closure" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "closure_state": "not_started",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize final proof archive review context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "closure_state": closure_state,
                "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T04:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                "artifact_generated_at": "2026-04-04T03:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "publication_state": "deferred",
                "closure_state": closure_state,
                "closure_result": closure_result,
                "closure_summaries": [
                    "no final proof closure actions executed in final proof closure baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof closure baseline does not persist closure artifacts yet"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "publication_state": "deferred",
                    "closure_state": closure_state,
                    "closure_result": closure_result,
                    "final_proof_publication_artifact_path": ".ai-sdlc/memory/frontend-final-proof-publication/latest.yaml",
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_archive_artifact(
    root: Path,
    *,
    archive_result: str,
    archive_state: str,
    remaining_blockers: list[str],
    steps: list[dict[str, object]] | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-archive" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    default_steps = [
        {
            "spec_id": "001-auth",
            "path": "specs/001-auth",
            "archive_state": "not_started",
            "pending_inputs": ["frontend_contract_observations"],
            "suggested_next_actions": [
                "materialize bounded thread archive context",
                "re-run ai-sdlc verify constraints",
            ],
            "source_linkage": {
                "archive_state": archive_state,
                "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
            },
        }
    ]
    artifact_path.write_text(
        yaml.safe_dump(
            {
                "generated_at": "2026-04-04T05:00:00Z",
                "manifest_path": "program-manifest.yaml",
                "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                "artifact_generated_at": "2026-04-04T04:00:00Z",
                "required": True,
                "confirmation_required": True,
                "confirmed": True,
                "closure_state": "deferred",
                "archive_state": archive_state,
                "archive_result": archive_result,
                "archive_summaries": [
                    "no final proof archive actions executed in final proof archive baseline"
                ],
                "written_paths": [],
                "remaining_blockers": list(remaining_blockers),
                "warnings": [
                    "final proof archive baseline defers thread archive and cleanup actions"
                ],
                "steps": list(steps or default_steps),
                "source_linkage": {
                    "closure_state": "deferred",
                    "archive_state": archive_state,
                    "archive_result": archive_result,
                    "final_proof_closure_artifact_path": ".ai-sdlc/memory/frontend-final-proof-closure/latest.yaml",
                    "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
                },
            },
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def _write_frontend_final_proof_archive_project_cleanup_seed_artifact(
    root: Path,
    *,
    cleanup_targets: object,
    cleanup_target_eligibility: object | None = None,
    cleanup_preview_plan: object | None = None,
    cleanup_mutation_proposal: object | None = None,
    cleanup_mutation_proposal_approval: object | None = None,
    cleanup_mutation_execution_gating: object | None = None,
) -> None:
    artifact_path = (
        root / ".ai-sdlc" / "memory" / "frontend-final-proof-archive-project-cleanup" / "latest.yaml"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": "2026-04-04T07:00:00Z",
        "manifest_path": "program-manifest.yaml",
        "artifact_source_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
        "artifact_generated_at": "2026-04-04T05:00:00Z",
        "required": True,
        "confirmation_required": True,
        "confirmed": True,
        "thread_archive_state": "deferred",
        "thread_archive_result": "deferred",
        "project_cleanup_state": "deferred",
        "project_cleanup_result": "deferred",
        "cleanup_targets_state": "seeded",
        "cleanup_targets": cleanup_targets,
        "project_cleanup_summaries": [
            "seeded cleanup target truth for consumption tests"
        ],
        "written_paths": [],
        "remaining_blockers": ["spec 001-auth remediation still required"],
        "warnings": [],
        "steps": [],
        "source_linkage": {
            "thread_archive_state": "deferred",
            "thread_archive_result": "deferred",
            "project_cleanup_state": "deferred",
            "project_cleanup_result": "deferred",
            "final_proof_archive_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive/latest.yaml",
            "final_proof_archive_project_cleanup_artifact_path": ".ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml",
        },
    }
    if cleanup_target_eligibility is not None:
        payload["cleanup_target_eligibility"] = cleanup_target_eligibility
    if cleanup_preview_plan is not None:
        payload["cleanup_preview_plan"] = cleanup_preview_plan
    if cleanup_mutation_proposal is not None:
        payload["cleanup_mutation_proposal"] = cleanup_mutation_proposal
    if cleanup_mutation_proposal_approval is not None:
        payload["cleanup_mutation_proposal_approval"] = (
            cleanup_mutation_proposal_approval
        )
    if cleanup_mutation_execution_gating is not None:
        payload["cleanup_mutation_execution_gating"] = (
            cleanup_mutation_execution_gating
        )
    artifact_path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
