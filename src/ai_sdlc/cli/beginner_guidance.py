"""Beginner-facing bilingual CLI guidance.

These helpers keep default CLI output focused on the user's next action while
machine-readable commands keep exposing the full framework state.
"""

from __future__ import annotations

from collections.abc import Sequence

_VERIFICATION_ENV_FOR_TARGET = {
    "codex": "OPENAI_CODEX",
    "cursor": "CURSOR_AGENT",
    "vscode": "VSCODE_IPC_HOOK_CLI",
    "claude_code": "CLAUDE_CODE_ENTRYPOINT",
}


def render_single_next_step(
    *,
    result_zh: str,
    result_en: str,
    next_command: str | None,
    next_zh: str,
    next_en: str,
    notes: Sequence[tuple[str, str]] = (),
) -> str:
    """Render a compact bilingual result with at most one next command."""

    lines = [
        "[bold]当前结果 / Result[/bold]",
        f"  {result_zh}",
        f"  {result_en}",
        "",
        "[bold]下一步 / Next[/bold]",
    ]
    if next_command:
        lines.append(f"  [cyan]{next_command}[/cyan]")
    lines.append(f"  {next_zh}")
    lines.append(f"  {next_en}")

    if notes:
        lines.append("")
        lines.append("[bold]说明 / Notes[/bold]")
        for zh, en in notes:
            lines.append(f"  {zh}")
            lines.append(f"  {en}")

    return "\n".join(lines)


def _verified_run_command(payload: dict[str, object]) -> str:
    target = str(payload.get("agent_target") or "").strip().lower()
    key = _VERIFICATION_ENV_FOR_TARGET.get(target, "AI_SDLC_ADAPTER_VERIFIED")
    shell = str(
        payload.get("preferred_shell") or payload.get("preferred_shell_recommended") or ""
    ).strip().lower()
    if shell == "powershell":
        return f"$env:{key}='1'; ai-sdlc run"
    if shell == "cmd":
        return f"set {key}=1 && ai-sdlc run"
    return f"{key}=1 ai-sdlc run"


def adapter_result_text(payload: dict[str, object]) -> tuple[str, str]:
    """Return a beginner-facing adapter status sentence."""

    target = str(payload.get("agent_target") or "adapter")
    path = str(payload.get("adapter_canonical_path") or "adapter instructions")
    ingress = str(payload.get("adapter_ingress_state") or "")
    if ingress == "verified_loaded":
        return (
            f"正常：{target} 规则已安装并完成宿主验证。",
            f"OK: {target} instructions are installed and host verification passed.",
        )
    if ingress == "materialized":
        return (
            f"正常：{target} 规则已安装到 {path}。当前终端无法证明 AI 宿主已加载它，这在普通终端里是常见情况。",
            f"OK: {target} instructions are installed at {path}. This terminal cannot prove the AI host loaded them; that is common in a regular terminal.",
        )
    if ingress == "degraded":
        return (
            "需要处理：当前 adapter 只能以降级方式运行。",
            "Action needed: the current adapter is running in degraded mode.",
        )
    return (
        "需要处理：adapter 规则文件尚未安装到可用位置。",
        "Action needed: adapter instructions are not installed at a usable path.",
    )


def render_adapter_status_for_beginner(payload: dict[str, object]) -> str:
    """Render default adapter status without exposing internal governance fields."""

    result_zh, result_en = adapter_result_text(payload)
    ingress = str(payload.get("adapter_ingress_state") or "")
    target = str(payload.get("agent_target") or "codex")
    if ingress in {"verified_loaded", "materialized"}:
        return render_single_next_step(
            result_zh=result_zh,
            result_en=result_en,
            next_command="ai-sdlc run --dry-run",
            next_zh="继续安全预演；预演会检查初始化路径，但不会真正执行开发改动。",
            next_en="Continue with the safe rehearsal; it checks startup flow without making development changes.",
        )
    return render_single_next_step(
        result_zh=result_zh,
        result_en=result_en,
        next_command=f"ai-sdlc adapter select --agent-target {target}",
        next_zh="重新选择实际用于聊天开发的 AI 入口，然后再运行安全预演。",
        next_en="Select the AI entry you actually use for chat development, then run the safe rehearsal.",
    )


def render_mutating_run_blocker(payload: dict[str, object]) -> str:
    """Render a run-unblocking command for mutating runs."""

    result_zh, result_en = adapter_result_text(payload)
    return render_single_next_step(
        result_zh=result_zh,
        result_en=result_en,
        next_command=_verified_run_command(payload),
        next_zh="正式执行需要宿主验证信号。请在实际 AI 工具终端中重新运行，或在当前 shell 用上面的命令带上验证信号后再运行。",
        next_en="A mutating run needs host verification. Run it from the actual AI-tool terminal, or use the command above to pass the verification signal in this shell.",
    )


def render_dry_run_open_gate_guidance(reasons: Sequence[str]) -> str:
    """Render dry-run guidance for a project that has open gates."""

    notes = tuple(
        (f"未完成项：{reason}", f"Open item: {reason}") for reason in reasons[:2]
    )
    return render_single_next_step(
        result_zh="安全预演已完成；还有未完成门禁。这在新项目或需求尚未完成时是正常的。",
        result_en="Safe rehearsal completed with open gates. This is normal for a new project or unfinished work.",
        next_command=None,
        next_zh="现在可以切换到 Codex/AI 对话中输入需求，让 AI 按项目规则继续细化、分解与开发。",
        next_en="Switch to Codex/AI chat and describe the requirement; the AI can continue refinement, breakdown, and development using the project instructions.",
        notes=notes,
    )


def render_dry_run_pass_guidance() -> str:
    """Render dry-run guidance when all gates pass."""

    return render_single_next_step(
        result_zh="安全预演已通过，阶段路由和基础门禁正常。",
        result_en="Safe rehearsal passed; stage routing and basic gates are ready.",
        next_command="ai-sdlc run",
        next_zh="确认要让框架正式推进流水线时，再执行完整运行。",
        next_en="Run the full pipeline when you are ready for the framework to proceed.",
    )


def render_init_complete_guidance(
    *,
    adapter_payload: dict[str, object],
    dry_run_passed: bool,
    open_reasons: Sequence[str],
) -> str:
    """Render the final beginner-facing init summary."""

    adapter_zh, adapter_en = adapter_result_text(adapter_payload)
    if dry_run_passed:
        dry_zh = "安全预演已自动通过。"
        dry_en = "Safe rehearsal passed automatically."
        notes: tuple[tuple[str, str], ...] = ()
    else:
        dry_zh = "安全预演已自动执行；当前仍有开放门禁。新项目或未完成需求出现这个结果是正常的。"
        dry_en = "Safe rehearsal ran automatically; open gates remain. This is normal for a new project or unfinished requirement."
        notes = tuple(
            (f"未完成项：{reason}", f"Open item: {reason}") for reason in open_reasons[:2]
        )

    return render_single_next_step(
        result_zh=f"初始化完成。{adapter_zh} {dry_zh}",
        result_en=f"Initialization complete. {adapter_en} {dry_en}",
        next_command=None,
        next_zh="不用再手动执行初始化命令；现在切换到 Codex/AI 对话中输入你的需求即可。",
        next_en="No more setup commands are needed; switch to Codex/AI chat and describe your requirement.",
        notes=notes,
    )
