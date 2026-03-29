"""Unit tests for DocScaffolder, TasksParser, and related templates."""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_sdlc.backends.native import (
    BackendCapabilityDeclaration,
    BackendDecisionKind,
    BackendRegistry,
    BackendSelectionPolicy,
)
from ai_sdlc.backends.routing import BackendRoutingBlockedError
from ai_sdlc.generators.doc_gen import DocScaffolder, TasksParser
from ai_sdlc.generators.template_gen import TemplateGenerator

TEMPLATES = [
    "spec.md.j2",
    "plan.md.j2",
    "tasks.md.j2",
    "execution-log.md.j2",
]


class FakeTemplateGenerator:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def render(self, template_name: str, context: dict[str, object]) -> str:
        self.calls.append(template_name)
        return f"template:{template_name}"


class RecordingBackend:
    def __init__(
        self,
        backend_name: str,
        *,
        capabilities: tuple[str, ...],
        responses: dict[str, str],
    ) -> None:
        self.backend_name = backend_name
        self.capabilities = capabilities
        self.responses = responses
        self.calls: list[tuple[str, dict[str, object]]] = []

    def capability_declaration(self) -> BackendCapabilityDeclaration:
        return BackendCapabilityDeclaration(
            backend_name=self.backend_name,
            provided_capabilities=self.capabilities,
        )

    def generate_spec(self, context: dict[str, object]) -> str:
        return self._call("generate_spec", context)

    def generate_plan(self, context: dict[str, object]) -> str:
        return self._call("generate_plan", context)

    def generate_tasks(self, context: dict[str, object]) -> str:
        return self._call("generate_tasks", context)

    def execute_task(self, task_id: str, context: dict[str, object]) -> str:
        return "pending"

    def generate_index(self, root: Path) -> dict[str, object]:
        return {}

    def _call(self, method_name: str, context: dict[str, object]) -> str:
        self.calls.append((method_name, dict(context)))
        return self.responses[method_name]


def _registry_with_native_and_plugin(
    *,
    plugin_capabilities: tuple[str, ...] = ("generate_spec", "generate_plan", "generate_tasks"),
    native_responses: dict[str, str] | None = None,
    plugin_responses: dict[str, str] | None = None,
) -> tuple[BackendRegistry, RecordingBackend, RecordingBackend]:
    registry = BackendRegistry()
    native = RecordingBackend(
        "native-test",
        capabilities=("generate_spec", "generate_plan", "generate_tasks"),
        responses=native_responses or {
            "generate_spec": "native spec",
            "generate_plan": "native plan",
            "generate_tasks": "native tasks",
        },
    )
    plugin = RecordingBackend(
        "plugin",
        capabilities=plugin_capabilities,
        responses=plugin_responses or {
            "generate_spec": "plugin spec",
            "generate_plan": "plugin plan",
            "generate_tasks": "plugin tasks",
        },
    )
    registry.register("native-test", native)
    registry.set_default("native-test")
    registry.register("plugin", plugin)
    return registry, native, plugin


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
        assert "待定" in out


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


def _public_context(
    registry: BackendRegistry,
    *,
    requested_backend: str = "plugin",
    policy: BackendSelectionPolicy | None = None,
    backend_decisions: dict[str, object | None] | None = None,
) -> dict[str, object]:
    context: dict[str, object] = {
        "work_item_id": "WI-CTX-001",
        "backend_registry": registry,
        "requested_backend": requested_backend,
        "backend_policy": policy or BackendSelectionPolicy(),
    }
    if backend_decisions is not None:
        context["backend_decisions"] = backend_decisions
    return context


def test_render_uses_context_backend_selection_and_records_decisions() -> None:
    registry, _, plugin = _registry_with_native_and_plugin()
    template_gen = FakeTemplateGenerator()
    decisions: dict[str, object | None] = {}
    scaffolder = DocScaffolder(template_gen=template_gen)

    spec = scaffolder.render("spec.md.j2", _public_context(registry, backend_decisions=decisions))
    plan = scaffolder.render("plan.md.j2", _public_context(registry, backend_decisions=decisions))
    tasks = scaffolder.render("tasks.md.j2", _public_context(registry, backend_decisions=decisions))
    execution_log = scaffolder.render(
        "execution-log.md.j2",
        _public_context(registry, backend_decisions=decisions),
    )

    assert spec == "plugin spec"
    assert plan == "plugin plan"
    assert tasks == "plugin tasks"
    assert execution_log == "template:execution-log.md.j2"
    assert template_gen.calls == ["execution-log.md.j2"]
    assert decisions["spec.md"].decision_kind == BackendDecisionKind.DELEGATE
    assert decisions["plan.md"].decision_kind == BackendDecisionKind.DELEGATE
    assert decisions["tasks.md"].decision_kind == BackendDecisionKind.DELEGATE
    assert decisions["execution-log.md"] is None
    assert [call[0] for call in plugin.calls] == [
        "generate_spec",
        "generate_plan",
        "generate_tasks",
    ]


@pytest.mark.parametrize(
    ("template_name", "output_name"),
    [
        ("spec.md.j2", "spec.md"),
        ("plan.md.j2", "plan.md"),
        ("tasks.md.j2", "tasks.md"),
    ],
)
def test_render_falls_back_to_native_using_custom_template_gen(
    template_name: str,
    output_name: str,
) -> None:
    registry = BackendRegistry()
    plugin = RecordingBackend(
        "plugin",
        capabilities=(),
        responses={
            "generate_spec": "plugin spec",
            "generate_plan": "plugin plan",
            "generate_tasks": "plugin tasks",
        },
    )
    registry.register("plugin", plugin)
    template_gen = FakeTemplateGenerator()
    decisions: dict[str, object | None] = {}
    scaffolder = DocScaffolder(template_gen=template_gen)

    rendered = scaffolder.render(
        template_name,
        _public_context(registry, backend_decisions=decisions),
    )

    assert rendered == f"template:{template_name}"
    assert template_gen.calls == [template_name]
    assert decisions[output_name].decision_kind == BackendDecisionKind.FALLBACK_NATIVE
    assert plugin.calls == []


def test_render_blocks_when_context_policy_disallows_plugin() -> None:
    registry, _, _ = _registry_with_native_and_plugin()
    scaffolder = DocScaffolder(template_gen=FakeTemplateGenerator())

    with pytest.raises(BackendRoutingBlockedError):
        scaffolder.render(
            "spec.md.j2",
            _public_context(
                registry,
                policy=BackendSelectionPolicy(allow_plugin=False, allow_native_fallback=False),
            ),
        )


def test_scaffold_populates_backend_decisions_via_context(tmp_path: Path) -> None:
    registry, _, plugin = _registry_with_native_and_plugin()
    template_gen = FakeTemplateGenerator()
    decisions: dict[str, object | None] = {}
    scaffolder = DocScaffolder(template_gen=template_gen)

    created = scaffolder.scaffold(
        tmp_path,
        "WI-AUDIT-001",
        _public_context(registry, backend_decisions=decisions),
    )

    assert len(created) == 4
    assert decisions["spec.md"].decision_kind == BackendDecisionKind.DELEGATE
    assert decisions["plan.md"].decision_kind == BackendDecisionKind.DELEGATE
    assert decisions["tasks.md"].decision_kind == BackendDecisionKind.DELEGATE
    assert decisions["execution-log.md"] is None
    assert (tmp_path / "specs" / "WI-AUDIT-001" / "spec.md").read_text(encoding="utf-8") == "plugin spec"
    assert (tmp_path / "specs" / "WI-AUDIT-001" / "plan.md").read_text(encoding="utf-8") == "plugin plan"
    assert (tmp_path / "specs" / "WI-AUDIT-001" / "tasks.md").read_text(encoding="utf-8") == "plugin tasks"
    assert (tmp_path / "specs" / "WI-AUDIT-001" / "execution-log.md").read_text(encoding="utf-8") == "template:execution-log.md.j2"
    assert [call[0] for call in plugin.calls] == [
        "generate_spec",
        "generate_plan",
        "generate_tasks",
    ]


# --- TasksParser ---


def write_sample_tasks_md(tmp_path: Path, content: str) -> Path:
    """Write markdown content to tmp_path/tasks.md and return the path."""
    path = tmp_path / "tasks.md"
    path.write_text(content, encoding="utf-8")
    return path


SAMPLE_FOUR_TASKS = """# 任务分解：WI-2026-001

### Task 1.1 Setup project structure

- **Task ID**: T001
- **Phase**: 1
- **依赖**: 无
- **文件**: src/main.py, src/config.py
- **可并行**: 否

### Task 1.2 Add CLI framework

- **Task ID**: T002
- **Phase**: 1
- **依赖**: T001
- **文件**: src/cli.py
- **可并行**: 否

### Task 2.1 Implement core logic

- **Task ID**: T003
- **Phase**: 2
- **依赖**: T001, T002
- **文件**: src/core.py
- **可并行**: 是

### Task 2.2 Add tests

- **Task ID**: T004
- **Phase**: 2
- **depends**: T003
- **files**: tests/test_core.py
- **parallelizable**: yes
"""


class TestTasksParser:
    """Scenarios for tasks.md parsing."""

    def test_normal_parse_four_tasks_two_phases(self, tmp_path: Path) -> None:
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, SAMPLE_FOUR_TASKS))
        assert plan.total_tasks == 4
        assert plan.total_batches == 2

        t1, t2, t3, t4 = plan.tasks
        assert t1.task_id == "T001"
        assert t1.title == "Setup project structure"
        assert t1.phase == 1
        assert t1.depends_on == []
        assert t1.file_paths == ["src/main.py", "src/config.py"]
        assert t1.parallelizable is False

        assert t2.task_id == "T002"
        assert t2.title == "Add CLI framework"
        assert t2.phase == 1
        assert t2.depends_on == ["T001"]
        assert t2.file_paths == ["src/cli.py"]
        assert t2.parallelizable is False

        assert t3.task_id == "T003"
        assert t3.title == "Implement core logic"
        assert t3.phase == 2
        assert t3.depends_on == ["T001", "T002"]
        assert t3.file_paths == ["src/core.py"]
        assert t3.parallelizable is True

        assert t4.task_id == "T004"
        assert t4.title == "Add tests"
        assert t4.phase == 2
        assert t4.depends_on == ["T003"]
        assert t4.file_paths == ["tests/test_core.py"]
        assert t4.parallelizable is True

    def test_missing_optional_fields_defaults(self, tmp_path: Path) -> None:
        content = """### Task 1.1 Simple task

Some description line.
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert plan.total_tasks == 1
        t = plan.tasks[0]
        assert t.task_id == "T11"
        assert t.title == "Simple task"
        assert t.phase == 1
        assert t.depends_on == []
        assert t.file_paths == []
        assert t.parallelizable is False

    def test_empty_file_returns_empty_plan(self, tmp_path: Path) -> None:
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, ""))
        assert plan.total_tasks == 0
        assert plan.total_batches == 0
        assert plan.tasks == []
        assert plan.batches == []

    def test_file_not_found_returns_empty_plan(self, tmp_path: Path) -> None:
        plan = TasksParser().parse(tmp_path / "missing.md")
        assert plan.total_tasks == 0
        assert plan.total_batches == 0

    @pytest.mark.parametrize(
        ("depends_key", "files_key", "parallel_key"),
        [
            ("依赖", "文件", "可并行"),
            ("depends", "files", "parallelizable"),
        ],
    )
    def test_chinese_and_english_field_names(
        self,
        tmp_path: Path,
        depends_key: str,
        files_key: str,
        parallel_key: str,
    ) -> None:
        content = f"""### Task 1.1 Mixed fields

- **Task ID**: TX1
- **{depends_key}**: T001
- **{files_key}**: src/a.py, src/b.py
- **{parallel_key}**: yes
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert len(plan.tasks) == 1
        t = plan.tasks[0]
        assert t.task_id == "TX1"
        assert t.depends_on == ["T001"]
        assert t.file_paths == ["src/a.py", "src/b.py"]
        assert t.parallelizable is True

    def test_depends_wu_is_empty_list(self, tmp_path: Path) -> None:
        content = """### Task 1.1 No deps

- **Task ID**: T001
- **依赖**: 无
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert plan.tasks[0].depends_on == []

    def test_batch_grouping_same_phase_same_batch(self, tmp_path: Path) -> None:
        content = """### Task 1.1 A

- **Task ID**: TA
- **Phase**: 1

### Task 1.2 B

- **Task ID**: TB
- **Phase**: 1
"""
        plan = TasksParser().parse(write_sample_tasks_md(tmp_path, content))
        assert plan.total_batches == 1
        assert plan.batches[0].phase == 1
        assert plan.batches[0].tasks == ["TA", "TB"]
