"""Direct-formal work item scaffold helpers (008)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ai_sdlc.core.config import load_project_state, save_project_state
from ai_sdlc.utils.helpers import PROJECT_STATE_PATH, slugify

_WI_ID_RE = re.compile(r"^(?P<seq>\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*$")
_PLACEHOLDER_RE = re.compile(r"\[[^\[\]\n]+\]")


class WorkitemScaffoldError(Exception):
    """Raised when direct-formal scaffold generation fails."""


@dataclass(frozen=True, slots=True)
class WorkitemScaffoldResult:
    """Outcome of creating the canonical direct-formal document set."""

    work_item_id: str
    title: str
    spec_dir: Path
    created_paths: tuple[Path, ...]
    created_date: str


class WorkitemScaffolder:
    """Create parser-friendly formal work item docs under ``specs/<WI>/``."""

    def __init__(self, *, template_dir: Path | None = None) -> None:
        self._template_dir = template_dir or Path(__file__).resolve().parents[3] / "templates"

    def scaffold(
        self,
        *,
        root: Path,
        title: str,
        wi_id: str | None = None,
        input_text: str | None = None,
        related_plan: str | None = None,
        related_docs: tuple[str, ...] = (),
    ) -> WorkitemScaffoldResult:
        """Create canonical formal docs for one work item."""
        title_clean = title.strip()
        if not title_clean:
            raise WorkitemScaffoldError("title is required for direct-formal init")
        state_path = root / PROJECT_STATE_PATH
        if not state_path.is_file():
            raise WorkitemScaffoldError(
                "Not inside an initialized AI-SDLC project (.ai-sdlc/project/config/project-state.yaml not found)."
            )

        state = load_project_state(root)
        work_item_id = self._resolve_work_item_id(
            title=title_clean,
            wi_id=wi_id,
            next_work_item_seq=state.next_work_item_seq,
        )
        created_date = date.today().isoformat()
        spec_dir = root / "specs" / work_item_id
        canonical_paths = (
            spec_dir / "spec.md",
            spec_dir / "plan.md",
            spec_dir / "tasks.md",
        )
        if any(path.exists() for path in canonical_paths):
            raise WorkitemScaffoldError(
                f"canonical formal docs already exist for {work_item_id}: {spec_dir}"
            )

        spec_dir.mkdir(parents=True, exist_ok=True)

        dedup_related_docs = tuple(dict.fromkeys(doc for doc in related_docs if doc.strip()))
        shared_input = self._build_input_text(
            input_text=input_text,
            related_plan=related_plan,
            related_docs=dedup_related_docs,
        )

        rendered = (
            (canonical_paths[0], self._render_spec(work_item_id, title_clean, created_date, shared_input)),
            (
                canonical_paths[1],
                self._render_plan(
                    work_item_id=work_item_id,
                    title=title_clean,
                    created_date=created_date,
                    related_plan=related_plan,
                    related_docs=dedup_related_docs,
                ),
            ),
            (
                canonical_paths[2],
                self._render_tasks(
                    work_item_id=work_item_id,
                    title=title_clean,
                    created_date=created_date,
                    related_plan=related_plan,
                    related_docs=dedup_related_docs,
                ),
            ),
        )

        for path, content in rendered:
            path.write_text(content, encoding="utf-8")

        next_seq = self._next_sequence_after(work_item_id, state.next_work_item_seq)
        if next_seq != state.next_work_item_seq:
            state.next_work_item_seq = next_seq
            save_project_state(root, state)

        return WorkitemScaffoldResult(
            work_item_id=work_item_id,
            title=title_clean,
            spec_dir=spec_dir,
            created_paths=canonical_paths,
            created_date=created_date,
        )

    def _resolve_work_item_id(
        self,
        *,
        title: str,
        wi_id: str | None,
        next_work_item_seq: int,
    ) -> str:
        if wi_id is not None and wi_id.strip():
            candidate = wi_id.strip()
        else:
            slug = slugify(title)
            if not slug:
                raise WorkitemScaffoldError("title does not produce a valid slug for work item id")
            candidate = f"{next_work_item_seq:03d}-{slug}"
        if not _WI_ID_RE.fullmatch(candidate):
            raise WorkitemScaffoldError(
                "work item id must use the canonical `NNN-short-name` form"
            )
        return candidate

    def _next_sequence_after(self, work_item_id: str, current: int) -> int:
        match = _WI_ID_RE.fullmatch(work_item_id)
        if match is None:
            return current
        seq = int(match.group("seq"))
        return max(current, seq + 1)

    def _build_input_text(
        self,
        *,
        input_text: str | None,
        related_plan: str | None,
        related_docs: tuple[str, ...],
    ) -> str:
        parts: list[str] = []
        if input_text and input_text.strip():
            parts.append(input_text.strip())
        else:
            parts.append("待补充：请补充用户描述、缺陷现象或 framework capability 背景。")
        refs: list[str] = []
        if related_plan and related_plan.strip():
            refs.append(f"`{related_plan.strip()}`")
        refs.extend(f"`{doc}`" for doc in related_docs)
        if refs:
            parts.append(f"参考：{'、'.join(refs)}")
        return " ".join(parts)

    def _render_spec(
        self,
        work_item_id: str,
        title: str,
        created_date: str,
        input_text: str,
    ) -> str:
        template = self._load_template("spec-template.md")
        replacements = {
            "[FEATURE_NAME]": title,
            "[NNN-short-name]": work_item_id,
            "[DATE]": created_date,
            "[PRD 中对应的章节或用户描述]": input_text,
            "[本功能覆盖什么、明确不覆盖什么]": "待补充：请明确覆盖范围与明确不覆盖范围。",
            "[标题]": "待补标题",
            "[作为...，我希望...，以便...]": "作为框架维护者，我希望直接生成 formal work item 文档，以便避免双轨产物。",
            "[为什么排在这个优先级]": "待补充：请说明当前用户故事的优先级依据。",
            "[如何独立验证这个故事]": "待补充：请补充独立验证方式。",
            "[边界情况 1]": "待补充边界情况 1",
            "[边界情况 2]": "待补充边界情况 2",
            "系统必须...": "系统必须待补充。",
            "[描述]": "待补充描述",
            "[可测量、可验证的成功条件]": "待补充：可测量、可验证的成功条件。",
        }
        return self._replace_template_tokens(template, replacements)

    def _render_plan(
        self,
        *,
        work_item_id: str,
        title: str,
        created_date: str,
        related_plan: str | None,
        related_docs: tuple[str, ...],
    ) -> str:
        template = self._load_template("plan-template.md")
        replacements = {
            "[FEATURE_NAME]": title,
            "[NNN-short-name]": work_item_id,
            "[DATE]": created_date,
            "[spec.md 路径]": f"specs/{work_item_id}/spec.md",
            "[一段话描述本功能的交付目标和推荐实现方式]": "待补充：请概述 direct-formal 或等价 canonical 交付目标。",
            "[从 tech-stack.yml 填充]": "待补充",
            "[从 PRD 提取]": "待补充",
            "[从 constitution.md 和 spec.md 提取]": "待补充",
            "[原则 1]": "待补宪章门禁",
            "[原则 2]": "待补宪章门禁",
            "[如何符合]": "待补计划响应",
            "[按实际项目填充]": "待补充源码结构。",
            "[解决什么问题]": "待补充阶段目标",
            "[如何验证]": "待补验证方式",
            "[如何回退]": "待补回退方式",
            "[产出什么]": "待补充产物",
            "data-model.md, contracts/, quickstart.md": "待补充产物",
            "[名称]": "待补工作流",
            "[一句话]": "待补关键路径",
            "...": "待补实施顺序",
        }
        body = self._replace_template_tokens(template, replacements)
        body = body.replace(
            "```text\n"
            "specs/NNN-feature-name/\n"
            "├── plan.md\n"
            "├── research.md\n"
            "├── data-model.md\n"
            "├── quickstart.md\n"
            "├── contracts/\n"
            "└── tasks.md\n"
            "```",
            "```text\n"
            f"specs/{work_item_id}/\n"
            "├── spec.md\n"
            "├── plan.md\n"
            "└── tasks.md\n"
            "```",
        )
        body = body.replace(
            "**产物**：research.md",
            "**产物**：spec.md / plan.md / tasks.md",
            1,
        )
        body = _PLACEHOLDER_RE.sub("待补充", body)
        return f"{self._render_frontmatter(related_plan, related_docs)}{body}"

    def _render_tasks(
        self,
        *,
        work_item_id: str,
        title: str,
        created_date: str,
        related_plan: str | None,
        related_docs: tuple[str, ...],
    ) -> str:
        template = self._load_template("tasks-template.md")
        title_line = template.splitlines()[0].replace("[FEATURE_NAME]", title).replace(
            "任务清单", "任务分解"
        )
        body = (
            f"{title_line}\n\n"
            f"**编号**：`{work_item_id}` | **日期**：{created_date}\n"
            "**来源**：plan.md + spec.md\n\n"
            "---\n\n"
            "## 分批策略\n\n"
            "```text\n"
            "Batch 1: formal baseline freeze\n"
            "Batch 2: implementation scaffold and parser-friendly structure\n"
            "Batch 3: docs alignment and focused verification\n"
            "```\n\n"
            "---\n\n"
            "## Batch 1：formal baseline freeze\n\n"
            "### Task 1.1 冻结 direct-formal 正式真值\n\n"
            "- **任务编号**：T11\n"
            "- **优先级**：P0\n"
            "- **依赖**：无\n"
            "- **文件**：spec.md, plan.md, tasks.md\n"
            "- **可并行**：否\n"
            "- **验收标准**：\n"
            f"  1. canonical formal docs 已直接位于 `specs/{work_item_id}/`\n"
            "  2. formal work item 不依赖第二套 canonical docs 才能进入 review\n"
            "- **验证**：文档对账 + `uv run ai-sdlc verify constraints`\n\n"
            "## Batch 2：implementation scaffold and parser-friendly structure\n\n"
            "### Task 2.1 实现 direct-formal 脚手架\n\n"
            "- **任务编号**：T21\n"
            "- **优先级**：P0\n"
            "- **依赖**：T11\n"
            "- **文件**：src/ai_sdlc/core/workitem_scaffold.py, tests/unit/test_workitem_scaffold.py\n"
            "- **可并行**：否\n"
            "- **验收标准**：\n"
            "  1. helper 能稳定生成 parser-friendly `spec.md / plan.md / tasks.md`\n"
            "  2. helper 只引用 external design docs，不复制正文\n"
            "- **验证**：`uv run pytest tests/unit/test_workitem_scaffold.py -q`\n\n"
            "## Batch 3：docs alignment and focused verification\n\n"
            "### Task 3.1 暴露 direct-formal CLI 并完成 focused verification\n\n"
            "- **任务编号**：T31\n"
            "- **优先级**：P1\n"
            "- **依赖**：T21\n"
            "- **文件**：src/ai_sdlc/cli/workitem_cmd.py, tests/integration/test_cli_workitem_init.py, tests/unit/test_command_names.py\n"
            "- **可并行**：否\n"
            "- **验收标准**：\n"
            "  1. CLI 能直接初始化 formal work item\n"
            "  2. command discovery 与 focused verification 一致\n"
            "- **验证**：`uv run pytest tests/integration/test_cli_workitem_init.py tests/unit/test_command_names.py -q`\n"
        )
        return f"{self._render_frontmatter(related_plan, related_docs)}{body}"

    def _render_frontmatter(
        self,
        related_plan: str | None,
        related_docs: tuple[str, ...],
    ) -> str:
        if not related_plan and not related_docs:
            return ""
        lines = ["---"]
        if related_plan and related_plan.strip():
            lines.append(f'related_plan: "{related_plan.strip()}"')
        if related_docs:
            lines.append("related_doc:")
            lines.extend(f'  - "{doc}"' for doc in related_docs)
        lines.append("---")
        return "\n".join(lines) + "\n"

    def _replace_template_tokens(self, template: str, replacements: dict[str, str]) -> str:
        rendered = template
        for old, new in replacements.items():
            rendered = rendered.replace(old, new)
        return rendered

    def _load_template(self, template_name: str) -> str:
        path = self._template_dir / template_name
        if not path.is_file():
            raise WorkitemScaffoldError(f"template not found: {path}")
        return path.read_text(encoding="utf-8")
