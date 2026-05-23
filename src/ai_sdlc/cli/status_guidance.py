"""Shared bilingual status and next-step guidance renderers."""

from __future__ import annotations

from collections.abc import Sequence


def render_status_guidance(
    *,
    current_status_zh: str,
    current_status_en: str,
    next_steps: Sequence[tuple[str, str, str]],
    notes: Sequence[str] = (),
) -> str:
    """Render a compact bilingual status block with one primary next command."""

    primary = next_steps[0] if next_steps else None
    lines = [
        "[bold]当前结果 / Result[/bold]",
        f"  {current_status_zh}",
        f"  {current_status_en}",
        "",
        "[bold]下一步 / Next[/bold]",
    ]

    if primary is None:
        lines.append("  无需继续执行命令。")
        lines.append("  No follow-up command is needed.")
    else:
        command, zh, en = primary
        lines.append(f"  [cyan]{command}[/cyan]")
        lines.append(f"  {zh}")
        lines.append(f"  {en}")

    if notes:
        lines.append("")
        lines.append("[bold]说明 / Notes[/bold]")
        lines.extend(f"  {note}" for note in notes)

    return "\n".join(lines)


def render_startup_guidance() -> str:
    """Render the startup guidance required after init/bootstrap entrypoints."""

    return render_status_guidance(
        current_status_zh="项目规则准备就绪后，开发会先确认当前可执行任务。",
        current_status_en="After project instructions are ready, development is guarded by the current executable task.",
        next_steps=(
            (
                "ai-sdlc status",
                "查看当前项目状态；普通开发不需要手动证明 AI 宿主已加载规则。",
                "Check current project status; normal development does not require manually proving the AI host loaded instructions.",
            ),
        ),
        notes=(
            "排查时才需要运行 adapter status 或 run --dry-run；主流程可以回到 AI 对话继续需求细化和任务分解。",
        ),
    )
