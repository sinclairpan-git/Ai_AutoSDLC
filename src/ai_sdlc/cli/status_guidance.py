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
        current_status_zh="接入真值尚未确认；先检查 adapter 状态。",
        current_status_en="Adapter ingress truth is not yet confirmed. Check adapter status first.",
        next_steps=(
            (
                "ai-sdlc run --dry-run",
                "继续安全预演；如 adapter 未验证，输出会直接给出恢复动作。",
                "Continue with the safe rehearsal; if adapter verification is missing, the output will give one recovery action.",
            ),
        ),
        notes=(
            "如果当前 shell 找不到 ai-sdlc，再使用 python -m ai_sdlc run --dry-run 作为等价入口。",
        ),
    )
