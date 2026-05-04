"""Host runtime planning CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from ai_sdlc.cli.beginner_guidance import render_single_next_step
from ai_sdlc.cli.status_guidance import render_status_guidance
from ai_sdlc.core.host_runtime_manager import evaluate_current_host_runtime
from ai_sdlc.models.host_runtime_plan import HostRuntimePlan
from ai_sdlc.utils.helpers import find_project_root

host_runtime_app = typer.Typer(help="Read-only host runtime planning commands")
console = Console()


def _dedupe_text_items(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique


def _resolve_root() -> Path:
    root = find_project_root()
    if root is None:
        console.print(
            "[red]Not inside an AI-SDLC project. Run this command from a project root.[/red]"
        )
        raise typer.Exit(code=2)
    return root


@host_runtime_app.command("plan")
def host_runtime_plan(
    as_json: bool = typer.Option(False, "--json", help="Machine-readable plan."),
    details: bool = typer.Option(
        False,
        "--details",
        help="Show the full diagnostic plan for framework developers.",
    ),
) -> None:
    """Print the bounded host runtime plan for the current project host."""

    root = _resolve_root()
    plan = evaluate_current_host_runtime(root)

    if as_json:
        typer.echo(json.dumps(plan.model_dump(mode="json"), indent=2, ensure_ascii=False))
    elif details:
        _print_plan(plan)
    else:
        console.print(_host_runtime_beginner_guidance(plan))

    raise typer.Exit(code=_exit_code_for_status(plan.status))


def _print_plan(plan: HostRuntimePlan) -> None:
    console.print("[bold cyan]Host Runtime Plan[/bold cyan]")
    console.print(f"status: {plan.status}", markup=False)
    console.print(
        f"surface: {plan.surface_kind} / {plan.surface_binding_state}",
        markup=False,
    )
    console.print(
        f"platform: {plan.platform_os} / {plan.platform_arch}",
        markup=False,
    )
    console.print(
        "reason_codes: "
        + (
            ", ".join(_dedupe_text_items(plan.reason_codes))
            if plan.reason_codes
            else "<none>"
        ),
        markup=False,
    )
    if plan.bootstrap_acquisition is not None:
        console.print(
            f"bootstrap_handoff: {plan.bootstrap_acquisition.handoff_kind}",
            markup=False,
        )
    if plan.remediation_fragment is not None:
        console.print(
            "remediation_targets: "
            + ", ".join(_dedupe_text_items(plan.remediation_fragment.will_install)),
            markup=False,
        )
    console.print("")
    console.print(_host_runtime_guidance(plan))


def _host_runtime_guidance(plan: HostRuntimePlan) -> str:
    if plan.status == "ready":
        return render_status_guidance(
            current_status_zh="宿主运行时已就绪，可以继续检查 adapter 接入真值。",
            current_status_en="Host runtime is ready. You can now verify adapter ingress truth.",
            next_steps=(
                (
                    "ai-sdlc adapter status",
                    "检查 adapter 接入真值、验证结果和治理状态。",
                    "Inspect adapter ingress truth, verification result, and governance state.",
                ),
                (
                    "ai-sdlc run --dry-run",
                    "执行安全预演，确认阶段路由与入口链路。",
                    "Run the safe rehearsal to confirm stage routing and startup flow.",
                ),
            ),
        )
    if plan.status == "remediation_required":
        return render_status_guidance(
            current_status_zh="宿主运行时可执行，但仍缺少附加依赖；先补齐再进入完整流水线。",
            current_status_en="Host runtime is usable, but supporting dependencies are still missing.",
            next_steps=(
                (
                    "ai-sdlc adapter status",
                    "先确认接入真值，再根据 remediation_targets 补齐剩余依赖。",
                    "Verify adapter ingress truth, then fill the remaining remediation targets.",
                ),
            ),
        )
    return render_status_guidance(
        current_status_zh="宿主运行时尚未就绪；先完成 bootstrap 或修复阻塞项。",
        current_status_en="Host runtime is not ready yet. Complete bootstrap or resolve blockers first.",
        next_steps=(
            (
                "ai-sdlc host-runtime plan --json",
                "查看 machine-readable 计划，识别缺失的运行时与阻塞原因。",
                "Inspect the machine-readable plan to see missing runtimes and blockers.",
            ),
        ),
    )


def _exit_code_for_status(status: str) -> int:
    if status in {"ready", "remediation_required"}:
        return 0
    return 1


def _host_runtime_beginner_guidance(plan: HostRuntimePlan) -> str:
    if plan.status == "ready":
        return render_single_next_step(
            result_zh="正常：运行环境已就绪。你不需要手动检查 Python 或安装额外依赖。",
            result_en="OK: the runtime is ready. You do not need to manually check Python or install extra dependencies.",
            next_command="ai-sdlc run --dry-run",
            next_zh="继续安全预演，确认项目初始化路径正常。",
            next_en="Continue with the safe rehearsal to confirm the project startup path.",
        )
    if plan.status == "remediation_required":
        missing_entries = getattr(plan, "missing_runtime_entries", None)
        if missing_entries is None and plan.remediation_fragment is not None:
            missing_entries = plan.remediation_fragment.will_install
        missing = ", ".join(_dedupe_text_items(list(missing_entries or [])))
        return render_single_next_step(
            result_zh=f"基础运行环境可用；仍缺少 {missing or '附加运行时'}。框架会把这些依赖放在托管运行时目录中处理，不要求你手动改系统环境。",
            result_en=f"The base runtime is usable; {missing or 'supporting runtime entries'} are still missing. The framework handles these in the managed runtime area instead of asking you to change the system environment manually.",
            next_command="ai-sdlc run --dry-run",
            next_zh="先继续安全预演；真正需要附加依赖的阶段会给出自动化处理路径。",
            next_en="Continue with the safe rehearsal; stages that need extra dependencies will provide an automated handling path.",
        )
    return render_single_next_step(
        result_zh="运行环境还不能直接启动。请使用 AI-SDLC 官方安装器或离线包完成框架运行时安装，不要手动拼装 Python/Node 环境。",
        result_en="The runtime cannot start directly yet. Use the official AI-SDLC installer or offline bundle to prepare the framework runtime instead of assembling Python/Node manually.",
        next_command="ai-sdlc host-runtime plan --details",
        next_zh="查看诊断详情；安装器/离线包应负责后续运行时准备。",
        next_en="Inspect diagnostic details; the installer/offline bundle should own runtime preparation.",
    )
