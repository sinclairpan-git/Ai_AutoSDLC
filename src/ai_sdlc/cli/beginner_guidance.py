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


def render_project_required_guidance(command: str = "ai-sdlc init .") -> str:
    """Render a consistent message for commands run outside a project."""

    return render_single_next_step(
        result_zh="未找到 AI-SDLC 项目配置；当前目录还没有初始化。",
        result_en="No AI-SDLC project configuration was found in this directory.",
        next_command=command,
        next_zh="请先进入业务项目根目录并初始化；如果已经初始化，请切换到包含 .ai-sdlc/ 的目录再重试。",
        next_en="Go to the project root and initialize first; if it is already initialized, switch to the directory that contains .ai-sdlc/ and retry.",
    )


def render_command_missing_guidance(example: str) -> str:
    """Render a consistent message for wrapper commands missing child command."""

    return render_single_next_step(
        result_zh="命令不完整：`--` 后面缺少要执行的子命令。",
        result_en="The command is incomplete: no child command was provided after `--`.",
        next_command=example,
        next_zh="把要执行的真实命令放在 `--` 后面。",
        next_en="Put the real command to run after `--`.",
    )


def _verified_run_command(payload: dict[str, object]) -> str | None:
    target = str(payload.get("agent_target") or "").strip().lower()
    key = _VERIFICATION_ENV_FOR_TARGET.get(target)
    if key is None:
        return None
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
            f"正常：{target} 项目规则已准备好。",
            f"OK: {target} project instructions are ready.",
        )
    if ingress == "materialized":
        return (
            f"正常：{target} 项目规则已准备好（{path}）。",
            f"OK: {target} project instructions are ready at {path}.",
        )
    if ingress == "degraded":
        return (
            "需要处理：项目规则文件不完整，需要重新选择 AI 入口。",
            "Action needed: project instruction files are incomplete; select the AI entry again.",
        )
    return (
        "需要处理：项目规则文件尚未准备好。",
        "Action needed: project instruction files are not ready yet.",
    )


def render_adapter_status_for_beginner(payload: dict[str, object]) -> str:
    """Render default adapter status without exposing internal governance fields."""

    result_zh, result_en = adapter_result_text(payload)
    ingress = str(payload.get("adapter_ingress_state") or "")
    target = str(payload.get("agent_target") or "codex")
    if payload.get("adapter_target_mismatch"):
        detected = str(payload.get("detected_ide") or target)
        return render_single_next_step(
            result_zh=(
                f"{result_zh} 检测到的宿主是 {detected}，但项目 target 是 {target}。"
            ),
            result_en=(
                f"{result_en} The detected host is {detected}, but the project target is {target}."
            ),
            next_command=f"ai-sdlc adapter select --agent-target {detected}",
            next_zh="如果这是当前聊天宿主，先重选 adapter target 并刷新 canonical 文件。",
            next_en="If this is the current chat host, reselect the adapter target and refresh canonical files.",
        )
    if ingress == "verified_loaded":
        return render_single_next_step(
            result_zh=result_zh,
            result_en=result_en,
            next_command=None,
            next_zh="回到 Codex/AI 对话输入需求即可；写代码前会先确认当前可执行任务。",
            next_en="Return to Codex/AI chat and describe the requirement; code changes will be checked against the current executable task first.",
        )
    if ingress == "materialized":
        prompt = _adapter_bootstrap_prompt(payload)
        return render_single_next_step(
            result_zh=result_zh,
            result_en=result_en,
            next_command=prompt,
            next_zh="在 AI 对话里发送上面这句话后，直接输入需求；不需要反复运行 dry-run。",
            next_en="Send the line above in the AI chat, then describe the requirement directly; repeated dry-run commands are not needed.",
        )
    select_command = "ai-sdlc adapter select"
    if target in _VERIFICATION_ENV_FOR_TARGET:
        select_command = f"{select_command} --agent-target {target}"
    return render_single_next_step(
        result_zh=result_zh,
        result_en=result_en,
        next_command=select_command,
        next_zh="重新选择实际用于聊天开发的 AI 入口；完成后回到 AI 对话继续需求，只有排查时再运行 dry-run。",
        next_en="Select the AI entry you actually use for chat development; then return to AI chat, using dry-run only for troubleshooting.",
    )


def render_mutating_run_blocker(payload: dict[str, object]) -> str:
    """Render a run-unblocking command for mutating runs."""

    result_zh, result_en = adapter_result_text(payload)
    command = _verified_run_command(payload)
    if command is None:
        return render_single_next_step(
            result_zh=result_zh,
            result_en=result_en,
            next_command="ai-sdlc adapter select",
            next_zh="当前入口无法用环境信号验证。请重新选择实际用于聊天开发的 AI 工具入口，然后再运行正式流程。",
            next_en="The current entry cannot be verified with an environment signal. Select the AI tool you actually use for chat development, then run the full flow again.",
        )
    return render_single_next_step(
        result_zh=result_zh,
        result_en=result_en,
        next_command=command,
        next_zh="正式执行前需要确认当前入口就是实际聊天开发入口。请在实际 AI 工具终端中重新运行，或使用上面的命令后再运行。",
        next_en="Before a full run, confirm this is the AI entry used for chat development. Rerun from that AI-tool terminal, or use the command above first.",
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
    ingress = str(adapter_payload.get("adapter_ingress_state") or "")
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

    if ingress == "verified_loaded":
        return render_single_next_step(
            result_zh=f"初始化完成。{adapter_zh} {dry_zh}",
            result_en=f"Initialization complete. {adapter_en} {dry_en}",
            next_command=None,
            next_zh="不用再手动执行初始化命令；现在切换到 Codex/AI 对话中输入你的需求即可。",
            next_en="No more setup commands are needed; switch to Codex/AI chat and describe your requirement.",
            notes=notes,
        )
    if ingress == "materialized":
        prompt = _adapter_bootstrap_prompt(adapter_payload)
        return render_single_next_step(
            result_zh=f"初始化完成。{adapter_zh} {dry_zh}",
            result_en=f"Initialization complete. {adapter_en} {dry_en}",
            next_command=prompt,
            next_zh="不用再手动执行初始化命令；在 AI 对话里先发送上面这句话，再直接输入需求。",
            next_en="No more CLI setup commands are needed; send the line above in the AI chat, then describe the requirement directly.",
            notes=notes,
        )
    return render_single_next_step(
        result_zh=f"初始化完成。{adapter_zh} {dry_zh}",
        result_en=f"Initialization complete. {adapter_en} {dry_en}",
        next_command="ai-sdlc adapter select",
        next_zh="如果当前 AI 入口不是你正在使用的聊天工具，先重新选择；否则回到 AI 对话直接输入需求。",
        next_en="If the current AI entry is not the chat tool you are using, select it first; otherwise return to AI chat and describe the requirement.",
        notes=notes,
    )


def _adapter_bootstrap_prompt(payload: dict[str, object]) -> str:
    path = str(payload.get("adapter_canonical_path") or "AGENTS.md").strip()
    target = str(payload.get("agent_target") or "AI").strip()
    return f"请先读取 {path}，并在继续前按 AI-SDLC 约束执行本项目任务。（target: {target}）"
