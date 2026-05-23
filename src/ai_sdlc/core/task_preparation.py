"""Build minimal task candidates when code execution is not yet authorized."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MinimalTaskCandidate:
    """A generated candidate that can be shown or materialized by a later command."""

    work_item_id: str
    task_id: str
    title: str
    goal: str
    scope: tuple[str, ...]
    acceptance: tuple[str, ...]
    verify: tuple[str, ...]

    def to_markdown(self) -> str:
        lines = [
            f"### Task 1.1 {self.title}",
            "",
            f"- task_id: {self.task_id}",
            "- status: todo",
            f"- goal: {self.goal}",
            "- scope:",
            *[f"  - {item}" for item in self.scope],
            "- acceptance:",
            *[f"  - {item}" for item in self.acceptance],
            "- verify:",
            *[f"  - {item}" for item in self.verify],
        ]
        return "\n".join(lines) + "\n"


def build_minimal_task_candidate(
    *,
    work_item_id: str = "pending-work-item",
    request_text: str = "处理当前用户请求",
    scope: tuple[str, ...] = ("src/**", "tests/**"),
    verify: tuple[str, ...] = ("uv run pytest -q",),
) -> MinimalTaskCandidate:
    """Return a conservative executable task candidate without writing files."""
    goal = request_text.strip() or "处理当前用户请求"
    return MinimalTaskCandidate(
        work_item_id=work_item_id,
        task_id="T11",
        title=goal[:80],
        goal=goal,
        scope=scope,
        acceptance=("完成当前请求对应的最小可验证改动。",),
        verify=verify,
    )


def minimal_formal_doc_actions(spec_dir: Path | None) -> tuple[str, ...]:
    """Describe the smallest docs needed before product code can be changed."""
    if spec_dir is None:
        return (
            "创建或选择当前工作项",
            "生成最小 plan.md 和 tasks.md",
            "确认下一条可执行任务后再修改产品代码",
        )
    rel = spec_dir.as_posix()
    return (
        f"补齐 {rel}/plan.md",
        f"补齐 {rel}/tasks.md",
        "确认下一条可执行任务后再修改产品代码",
    )
