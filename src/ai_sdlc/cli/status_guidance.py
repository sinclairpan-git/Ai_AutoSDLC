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
    """Render a compact bilingual status block for CLI surfaces."""

    lines = [
        "[bold]当前状态 / Current status[/bold]",
        f"  {current_status_zh}",
        f"  {current_status_en}",
        "",
        "[bold]下一步命令 / Next command[/bold]",
    ]

    for command, _zh, _en in next_steps:
        lines.append(f"  [cyan]{command}[/cyan]")

    lines.extend(
        [
            "",
            "[bold]命令作用 / What this command does[/bold]",
        ]
    )

    for command, zh, en in next_steps:
        lines.append(f"  [cyan]{command}[/cyan]")
        lines.append(f"    {zh}")
        lines.append(f"    {en}")

    if notes:
        lines.append("")
        lines.extend(f"  {note}" for note in notes)

    return "\n".join(lines)


def render_startup_guidance() -> str:
    """Render the startup guidance required after init/bootstrap entrypoints."""

    return render_status_guidance(
        current_status_zh="接入真值尚未确认；先检查 adapter 状态。",
        current_status_en="Adapter ingress truth is not yet confirmed. Check adapter status first.",
        next_steps=(
            (
                "ai-sdlc adapter status",
                "检查接入真值、验证结果和当前治理状态。",
                "Inspect adapter ingress truth, verification result, and current governance state.",
            ),
            (
                "ai-sdlc run --dry-run",
                "执行安全预演；只校验启动与阶段路由，不作为治理激活证明。",
                "Start framework with safe startup rehearsal only; this does not prove governance activation.",
            ),
            (
                "ai-sdlc stage run init --dry-run",
                "只预演 init 阶段，便于按阶段排查问题。",
                "Preview the init stage only for stage-by-stage troubleshooting.",
            ),
            (
                "python -m ai_sdlc adapter status",
                "当 `ai-sdlc` 不在 PATH 时，用模块入口检查接入状态。",
                "Use the module entry to inspect adapter status when `ai-sdlc` is not on PATH.",
            ),
            (
                "python -m ai_sdlc run --dry-run",
                "当 `ai-sdlc` 不在 PATH 时，用模块入口执行安全预演。",
                "Use the module entry to run the safe startup rehearsal when `ai-sdlc` is not on PATH.",
            ),
        ),
        notes=(
            "Current startup rehearsal is not verified host-ingress proof; check adapter status before mutating runs.",
        ),
    )

