"""Unit tests for document scaffolding templates and DocScaffolder."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.generators.doc_scaffold import DocScaffolder
from ai_sdlc.generators.template_gen import TemplateGenerator

TEMPLATES = [
    "spec.md.j2",
    "plan.md.j2",
    "tasks.md.j2",
    "execution-log.md.j2",
]


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_template_renders_minimal_context(template_name: str) -> None:
    gen = TemplateGenerator()
    ctx: dict[str, object] = {
        "work_item_id": "WI-MIN-001",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    out = gen.render(template_name, ctx)
    assert "WI-MIN-001" in out
    if template_name != "execution-log.md.j2":
        assert "2026-01-01T00:00:00+00:00" in out
    else:
        assert "TBD" in out


@pytest.mark.parametrize("template_name", TEMPLATES)
def test_template_renders_full_context(template_name: str) -> None:
    gen = TemplateGenerator()
    modules: list[dict[str, str]] = [
        {"name": "core", "description": "Core module"},
        {"name": "api", "description": "API layer"},
    ]
    tasks: list[dict[str, object]] = [
        {
            "phase": 1,
            "title": "Setup",
            "task_id": "T-1",
            "depends_on": [],
            "file_paths": ["a.py"],
            "parallelizable": True,
        },
        {
            "phase": 2,
            "title": "Implement",
            "task_id": "T-2",
            "depends_on": ["T-1"],
            "file_paths": ["b.py", "c.py"],
            "parallelizable": False,
        },
    ]
    batches: list[dict[str, object]] = [
        {
            "batch_id": "B1",
            "phase": 1,
            "tasks": ["T-1", "T-2"],
            "status": "done",
            "started_at": "2026-01-02T10:00:00+00:00",
            "completed_at": "2026-01-02T11:00:00+00:00",
        }
    ]
    ctx: dict[str, object] = {
        "work_item_id": "WI-FULL-001",
        "created_at": "2026-03-22T12:00:00+00:00",
        "project_name": "DemoProj",
        "goals": "Ship feature",
        "scope_in": "In scope",
        "scope_out": "Out of scope",
        "acceptance_criteria": "All tests pass",
        "architecture_notes": "Layered",
        "modules": modules,
        "implementation_order": "Core then API",
        "tasks": tasks,
        "started_at": "2026-03-22T09:00:00+00:00",
        "batches": batches,
    }
    out = gen.render(template_name, ctx)
    assert "WI-FULL-001" in out
    assert "DemoProj" in out or template_name in (
        "execution-log.md.j2",
        "tasks.md.j2",
    )
    if template_name == "spec.md.j2":
        assert "Ship feature" in out
        assert "In scope" in out
    if template_name == "plan.md.j2":
        assert "Layered" in out
        assert "Core" in out
    if template_name == "tasks.md.j2":
        assert "T-1" in out
        assert "T-2" in out
        assert "Setup" in out
    if template_name == "execution-log.md.j2":
        assert "B1" in out
        assert "T-1" in out


def test_scaffold_creates_four_files(tmp_path: Path) -> None:
    scaffolder = DocScaffolder()
    created = scaffolder.scaffold(tmp_path, "WI-SCAFF-001")
    spec_dir = tmp_path / "specs" / "WI-SCAFF-001"
    assert len(created) == 4
    assert {p.name for p in created} == {
        "spec.md",
        "plan.md",
        "tasks.md",
        "execution-log.md",
    }
    for name in ("spec.md", "plan.md", "tasks.md", "execution-log.md"):
        assert (spec_dir / name).is_file()


def test_scaffold_skips_existing_idempotent(tmp_path: Path) -> None:
    scaffolder = DocScaffolder()
    wid = "WI-IDEM-001"
    first = scaffolder.scaffold(tmp_path, wid)
    assert len(first) == 4
    second = scaffolder.scaffold(tmp_path, wid)
    assert second == []


def test_scaffold_returns_only_newly_created_paths(tmp_path: Path) -> None:
    scaffolder = DocScaffolder()
    wid = "WI-PART-001"
    spec_dir = tmp_path / "specs" / wid
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# existing\n", encoding="utf-8")

    created = scaffolder.scaffold(tmp_path, wid)
    assert len(created) == 3
    assert {p.name for p in created} == {"plan.md", "tasks.md", "execution-log.md"}
    assert (spec_dir / "spec.md").read_text(encoding="utf-8") == "# existing\n"
