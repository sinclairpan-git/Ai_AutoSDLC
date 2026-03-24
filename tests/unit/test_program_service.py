"""Unit tests for program manifest service."""

from __future__ import annotations

from pathlib import Path

from ai_sdlc.core.program_service import ProgramService
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
    svc = ProgramService(tmp_path)
    gates = svc.evaluate_execute_gates(_manifest(), allow_dirty=True)
    assert gates.passed is True
