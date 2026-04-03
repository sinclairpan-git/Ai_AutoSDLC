"""Unit tests for program manifest service."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.frontend_contract_drift import PageImplementationObservation
from ai_sdlc.core.frontend_contract_observation_provider import (
    build_frontend_contract_observation_artifact,
    write_frontend_contract_observation_artifact,
)
from ai_sdlc.core.program_service import ProgramService
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
