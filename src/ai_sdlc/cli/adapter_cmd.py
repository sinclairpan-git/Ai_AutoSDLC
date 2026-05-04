"""Adapter management CLI commands."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_sdlc.cli.beginner_guidance import (
    render_adapter_status_for_beginner,
    render_command_missing_guidance,
    render_project_required_guidance,
    render_single_next_step,
)
from ai_sdlc.core.config import load_project_config, persist_preferred_shell
from ai_sdlc.integrations.agent_target import (
    interactive_select_agent_target,
    interactive_select_preferred_shell,
    is_interactive_terminal,
    preferred_shell_label,
    recommended_shell_for_platform,
)
from ai_sdlc.integrations.ide_adapter import (
    IDEKind,
    acknowledge_adapter,
    build_adapter_governance_surface,
    build_canonical_proof_env,
    detect_ide,
    ensure_ide_adaptation,
    format_adapter_notice,
)
from ai_sdlc.models.project import PreferredShell
from ai_sdlc.utils.helpers import find_project_root

console = Console()

adapter_app = typer.Typer(
    help=(
        "Select adapters, inspect ingress truth plus verification result, "
        "and keep operator acknowledgement for compatibility/debug flows."
    )
)
_EXEC_CONTEXT_SETTINGS = {"allow_extra_args": True, "ignore_unknown_options": True}
_DEFAULT_ADAPTER_EXEC_TIMEOUT_SECONDS = 120


def _require_project_root() -> object:
    root = find_project_root()
    if root is None:
        console.print(render_project_required_guidance())
        raise typer.Exit(code=1)
    return root


def _is_interactive_terminal() -> bool:
    return is_interactive_terminal()


def _adapter_status_payload(root: Path) -> dict[str, object]:
    detected_ide = detect_ide(root)
    return build_adapter_governance_surface(
        root,
        detected_ide=detected_ide,
        environ=os.environ,
    )


def _resolve_command(ctx: typer.Context) -> list[str]:
    command = list(ctx.args)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        console.print(render_command_missing_guidance("ai-sdlc adapter exec -- ai-sdlc --help"))
        raise typer.Exit(code=2)
    return command


def _emit_process_output(stdout: str, stderr: str) -> None:
    if stdout:
        typer.echo(stdout, nl=False)
    if stderr:
        typer.echo(stderr, nl=False, err=True)


def _coerce_timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def _prepend_pythonpath(current: dict[str, str], entry: str) -> str:
    existing = current.get("PYTHONPATH", "").strip()
    if not existing:
        return entry
    parts = [item for item in existing.split(os.pathsep) if item]
    if entry in parts:
        return existing
    return os.pathsep.join([entry, *parts])


@adapter_app.command(name="select")
def adapter_select(
    agent_target: IDEKind | None = typer.Option(
        None,
        "--agent-target",
        help="Adapter target to persist for this project.",
    ),
) -> None:
    """Persist the desired adapter target and install its files."""
    root = _require_project_root()
    selected_target = agent_target
    if selected_target is None:
        if not _is_interactive_terminal():
            console.print(
                render_single_next_step(
                    result_zh="需要选择 AI 代理入口；当前终端不能交互选择。",
                    result_en="An AI agent target is required, and this terminal cannot prompt interactively.",
                    next_command="ai-sdlc adapter select --agent-target codex",
                    next_zh="把 `codex` 替换成你实际用于聊天开发的入口。",
                    next_en="Replace `codex` with the AI entry you actually use for chat development.",
                )
            )
            raise typer.Exit(code=2)
        selected_target = interactive_select_agent_target(detect_ide(root))

    result = ensure_ide_adaptation(root, agent_target=selected_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    cfg = load_project_config(root)
    console.print(
        render_single_next_step(
            result_zh=f"已选择 AI 代理入口：{cfg.agent_target}。",
            result_en=f"AI agent target selected: {cfg.agent_target}.",
            next_command="ai-sdlc run --dry-run",
            next_zh="继续安全预演；如果这是 init 自动流程的一部分，可以直接回到 init 输出继续判断。",
            next_en="Continue with the safe rehearsal; if this ran inside init, follow the init output.",
            notes=(
                (
                    f"当前接入状态：{cfg.adapter_ingress_state or 'unknown'}",
                    f"Current ingress state: {cfg.adapter_ingress_state or 'unknown'}",
                ),
            ),
        )
    )


@adapter_app.command(name="shell-select")
def adapter_shell_select(
    shell: PreferredShell | None = typer.Option(
        None,
        "--shell",
        help="Preferred shell to persist for this project.",
    ),
) -> None:
    """Persist the project shell preference and refresh adapter instructions."""
    root = _require_project_root()
    selected_shell = shell
    if selected_shell is None:
        if not _is_interactive_terminal():
            console.print(
                render_single_next_step(
                    result_zh="需要选择项目命令 shell；当前终端不能交互选择。",
                    result_en="A project command shell is required, and this terminal cannot prompt interactively.",
                    next_command="ai-sdlc adapter shell-select --shell zsh",
                    next_zh="把 `zsh` 替换成你实际执行命令的 shell。",
                    next_en="Replace `zsh` with the shell you actually use to run commands.",
                )
            )
            raise typer.Exit(code=2)
        selected_shell = interactive_select_preferred_shell(
            recommended_shell_for_platform()
        )

    persist_preferred_shell(root, selected_shell.value)
    cfg = load_project_config(root)
    current_target = cfg.agent_target or detect_ide(root).value
    result = ensure_ide_adaptation(root, agent_target=current_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    console.print(
        render_single_next_step(
            result_zh=f"已选择项目命令 shell：{preferred_shell_label(selected_shell)}。",
            result_en=f"Project command shell selected: {preferred_shell_label(selected_shell)}.",
            next_command="ai-sdlc run --dry-run",
            next_zh="继续安全预演；后续 CLI/AI 指令会优先按这个 shell 展示命令。",
            next_en="Continue with the safe rehearsal; future CLI/AI commands will prefer this shell.",
        )
    )


@adapter_app.command(name="activate")
def adapter_activate(
    agent_target: IDEKind | None = typer.Option(
        None,
        "--agent-target",
        help="Optionally override the current adapter target while acknowledging it.",
    ),
) -> None:
    """Record operator acknowledgement for compatibility/debug use only; this does not change ingress verification."""
    root = _require_project_root()
    result = acknowledge_adapter(root, agent_target=agent_target)
    note = format_adapter_notice(result)
    if note:
        console.print(note)
    cfg = _adapter_status_payload(root)
    console.print(
        render_single_next_step(
            result_zh="已记录 adapter 人工确认；这不是宿主加载验证。",
            result_en="Adapter acknowledgement was recorded; this is not host-load verification.",
            next_command="ai-sdlc adapter status",
            next_zh="查看当前是否已经 verified_loaded；默认状态页会告诉你下一步。",
            next_en="Check whether the adapter is verified_loaded; the default status view will show the next step.",
            notes=(
                (
                    f"当前入口：{cfg['agent_target']}，确认状态：{cfg['adapter_activation_state']}",
                    f"Current target: {cfg['agent_target']}, acknowledgement state: {cfg['adapter_activation_state']}",
                ),
            ),
        )
    )


@adapter_app.command(name="status")
def adapter_status(
    as_json: bool = typer.Option(False, "--json", help="Machine-readable adapter state."),
    details: bool = typer.Option(
        False,
        "--details",
        help="Show the full diagnostic table for framework developers.",
    ),
) -> None:
    """Show ingress state, verification result, and derived governance mode."""
    root = _require_project_root()
    payload = _adapter_status_payload(root)
    if as_json:
        typer.echo(json.dumps(payload))
        return

    if not details:
        console.print(render_adapter_status_for_beginner(payload))
        return

    table = Table(title="Adapter Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    for key, value in payload.items():
        table.add_row(key, str(value) if value not in ("", None) else "-")
    console.print(table)


@adapter_app.command(name="exec", context_settings=_EXEC_CONTEXT_SETTINGS)
def adapter_exec(
    ctx: typer.Context,
    timeout_seconds: int = typer.Option(
        _DEFAULT_ADAPTER_EXEC_TIMEOUT_SECONDS,
        "--timeout-seconds",
        min=1,
        help="Maximum seconds to wait for the child command.",
    ),
) -> None:
    """Execute one command with canonical proof env injected."""
    root = _require_project_root()
    command = _resolve_command(ctx)
    try:
        proof_env = build_canonical_proof_env(root)
    except (FileNotFoundError, ValueError) as exc:
        console.print(
            Panel(
                render_single_next_step(
                    result_zh=f"无法生成 adapter 执行凭证：{exc}",
                    result_en=f"Could not build adapter execution proof: {exc}",
                    next_command="ai-sdlc adapter status",
                    next_zh="先检查 adapter 状态，再按状态页给出的单一下一步处理。",
                    next_en="Check adapter status first, then follow the single next step it prints.",
                ),
                title="ai-sdlc adapter exec",
                border_style="red",
            )
        )
        raise typer.Exit(code=2) from exc

    env = os.environ.copy()
    env.update(proof_env)
    package_root = str(Path(__file__).resolve().parents[2])
    env["PYTHONPATH"] = _prepend_pythonpath(env, package_root)
    try:
        result = subprocess.run(
            command,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        _emit_process_output(
            _coerce_timeout_output(exc.output),
            _coerce_timeout_output(exc.stderr),
        )
        console.print(
            render_single_next_step(
                result_zh=f"子命令超时：超过 {timeout_seconds} 秒未结束。",
                result_en=f"Child command timed out after {timeout_seconds} second(s).",
                next_command=None,
                next_zh="检查上方子命令输出；需要更长时间时增加 `--timeout-seconds` 后重试。",
                next_en="Review the child command output above; increase `--timeout-seconds` and retry if it needs more time.",
            )
        )
        raise typer.Exit(code=124) from exc
    _emit_process_output(result.stdout, result.stderr)
    raise typer.Exit(code=result.returncode)
