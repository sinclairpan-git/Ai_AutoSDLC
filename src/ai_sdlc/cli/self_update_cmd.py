"""Self-update advisor commands."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PureWindowsPath

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.cli.beginner_guidance import render_single_next_step
from ai_sdlc.core.update_advisor import (
    NOTICE_ACTIONABLE,
    NOTICE_FAILED,
    NOTICE_LIGHT,
    ack_notice,
    detect_runtime_identity,
    evaluate_update_advisor,
    notice_already_acknowledged,
    notice_version_for,
    platform_asset_hint,
    render_notice_lines,
    should_auto_render_notice,
)

self_update_app = typer.Typer(
    help="Check and apply AI-SDLC framework updates.",
    no_args_is_help=True,
)
console = Console()
notice_console = Console(stderr=True)


class SelfUpdateError(RuntimeError):
    """Raised when the automatic self-update cannot complete safely."""


def _print_json(payload: dict[str, object]) -> None:
    console.print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def maybe_render_update_notice() -> None:
    """Render the Stage 0 update notice for interactive installed CLI runs."""
    if not should_auto_render_notice():
        return
    evaluation = evaluate_update_advisor()
    classes = list(evaluation.eligible_notice_classes)
    if not classes and evaluation.refresh_result not in {
        "network_error",
        "parse_error",
        "timeout",
    }:
        return

    notice_class = None
    if NOTICE_ACTIONABLE in classes:
        notice_class = NOTICE_ACTIONABLE
    elif NOTICE_LIGHT in classes:
        notice_class = NOTICE_LIGHT
    elif evaluation.refresh_attempted:
        notice_class = NOTICE_FAILED

    if notice_class is None or notice_already_acknowledged(evaluation, notice_class):
        return

    lines = render_notice_lines(evaluation)
    if not lines:
        return
    notice_console.print(
        Panel(
            "\n".join(lines),
            title="AI-SDLC Update Advisor",
            border_style="yellow",
        )
    )
    ack_notice(
        notice_class,
        notice_version_for(evaluation, notice_class),
    )


@self_update_app.command("identity")
def self_update_identity(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    )
) -> None:
    """Show the installed-runtime identity used by update advisor."""
    identity = detect_runtime_identity()
    payload = identity.to_machine_dict()
    if json_output:
        _print_json(payload)
        return
    console.print(Panel(json.dumps(payload, ensure_ascii=False, indent=2), title="Update Identity"))


@self_update_app.command("evaluate")
def self_update_evaluate(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    ),
    no_refresh: bool = typer.Option(
        False,
        "--no-refresh",
        help="Evaluate cache-only without a network refresh attempt.",
    ),
) -> None:
    """Evaluate update notice eligibility."""
    evaluation = evaluate_update_advisor(allow_refresh=not no_refresh)
    payload = evaluation.to_machine_dict()
    if json_output:
        _print_json(payload)
        return
    lines = render_notice_lines(evaluation)
    if lines:
        console.print(Panel("\n".join(lines), title="AI-SDLC Update Advisor"))
        return
    console.print("[green]No actionable AI-SDLC update notice is available.[/green]")
    console.print(f"reason_code: {evaluation.reason_code}", markup=False)


@self_update_app.command("check")
def self_update_check(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    )
) -> None:
    """User-facing update check for the current installed runtime."""
    self_update_evaluate(json_output=json_output, no_refresh=False)


@self_update_app.command("install")
def self_update_install(
    version: str = typer.Option(
        ...,
        "--version",
        help="Release version to install, for example 0.7.4.",
    ),
) -> None:
    """Download, install, and verify a GitHub release for the current runtime."""
    _reexec_windows_launcher_if_needed(version)
    try:
        release_version, _release_url, asset_url, hint = _release_asset_context(version)
        with tempfile.TemporaryDirectory(prefix="ai-sdlc-self-update-") as temp_root:
            temp_path = Path(temp_root)
            archive_path = temp_path / hint["filename"]
            _download_asset(asset_url, archive_path)
            bundle_dir = _extract_release_asset(archive_path, temp_path / "bundle", hint)
            _install_bundle_into_current_runtime(bundle_dir, release_version)
            installed_version = _read_installed_version()
        if installed_version != release_version:
            raise SelfUpdateError(
                f"installed version is {installed_version}, expected {release_version}"
            )
    except SelfUpdateError as exc:
        console.print(
            Panel(
                render_single_next_step(
                    result_zh=f"更新失败：{exc}",
                    result_en=f"Update failed: {exc}",
                    next_command=f"ai-sdlc self-update install --version {version}",
                    next_zh="修复上方错误后，重新执行同一条更新命令。",
                    next_en="Fix the error above, then rerun the same update command.",
                ),
                title="AI-SDLC Self Update",
                border_style="red",
            )
        )
        raise typer.Exit(1) from exc

    console.print(
        Panel(
            render_single_next_step(
                result_zh=f"更新完成：当前 AI-SDLC 已是 {installed_version}。",
                result_en=f"Update completed: current AI-SDLC is {installed_version}.",
                next_command=None,
                next_zh="不需要继续执行升级命令；回到原项目继续使用 AI-SDLC。",
                next_en="No more update commands are needed; return to your project and keep using AI-SDLC.",
                notes=(
                    (
                        f"已自动安装 release 资产：{hint['filename']}",
                        f"Installed release asset automatically: {hint['filename']}",
                    ),
                ),
            ),
            title="AI-SDLC Self Update",
            border_style="green",
        )
    )


@self_update_app.command("ack-notice")
def self_update_ack_notice(
    notice_class: str = typer.Argument(..., help="Notice class to acknowledge."),
    notice_version: str = typer.Argument(..., help="Notice version or reason code."),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit the helper machine contract as JSON.",
    ),
) -> None:
    """Record that a notice was shown by a CLI/IDE/AI surface."""
    ack = ack_notice(notice_class, notice_version)
    payload = ack.to_machine_dict()
    if json_output:
        _print_json(payload)
        return
    if ack.ack_recorded:
        console.print("[green]Update notice acknowledgement recorded.[/green]")
    else:
        console.print("[yellow]Update notice acknowledgement was not recorded.[/yellow]")


def _release_asset_context(
    version: str,
) -> tuple[str, str, str, dict[str, str]]:
    hint = platform_asset_hint(version)
    release_version = version[1:] if version.startswith("v") else version
    if not release_version:
        raise SelfUpdateError("missing target version")
    tag = f"v{release_version}"
    release_url = f"https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/tag/{tag}"
    asset_url = (
        f"https://github.com/sinclairpan-git/Ai_AutoSDLC/releases/download/"
        f"{tag}/{hint['filename']}"
    )
    return release_version, release_url, asset_url, hint


def _reexec_windows_launcher_if_needed(version: str) -> None:
    if not _should_reexec_windows_launcher():
        return
    env = os.environ.copy()
    env["AI_SDLC_SELF_UPDATE_REEXEC"] = "1"
    command = [
        sys.executable,
        "-m",
        "ai_sdlc",
        "self-update",
        "install",
        "--version",
        version,
    ]
    os.execve(sys.executable, command, env)


def _should_reexec_windows_launcher(
    *,
    platform_name: str = sys.platform,
    argv0: str = sys.argv[0],
    env: dict[str, str] | None = None,
) -> bool:
    if platform_name != "win32":
        return False
    env_map = env or os.environ
    if env_map.get("AI_SDLC_SELF_UPDATE_REEXEC") == "1":
        return False
    launcher = PureWindowsPath(argv0).name.lower()
    return launcher in {"ai-sdlc.exe", "ai_sdlc.exe"}


def _download_asset(asset_url: str, archive_path: Path) -> None:
    request = urllib.request.Request(
        asset_url,
        headers={"User-Agent": "ai-sdlc-self-update"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            archive_path.write_bytes(response.read())
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        raise SelfUpdateError(f"download failed: {asset_url}") from exc
    if not archive_path.exists() or archive_path.stat().st_size == 0:
        raise SelfUpdateError("downloaded release asset is empty")


def _extract_release_asset(
    archive_path: Path, extract_root: Path, hint: dict[str, str]
) -> Path:
    extract_root.mkdir(parents=True, exist_ok=True)
    try:
        if hint["archive"] == "zip":
            with zipfile.ZipFile(archive_path) as archive:
                _safe_extract_zip(archive, extract_root)
        else:
            with tarfile.open(archive_path, "r:gz") as archive:
                _safe_extract_tar(archive, extract_root)
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as exc:
        raise SelfUpdateError("release asset extraction failed") from exc

    expected_name = hint["filename"]
    if expected_name.endswith(".tar.gz"):
        expected_name = expected_name.removesuffix(".tar.gz")
    else:
        expected_name = Path(expected_name).stem
    expected_dir = extract_root / expected_name
    if expected_dir.is_dir():
        return expected_dir
    bundle_dirs = [path for path in extract_root.iterdir() if path.is_dir()]
    if len(bundle_dirs) == 1:
        return bundle_dirs[0]
    raise SelfUpdateError("release asset did not contain a single install bundle")


def _safe_extract_tar(archive: tarfile.TarFile, extract_root: Path) -> None:
    root = extract_root.resolve()
    for member in archive.getmembers():
        if member.issym() or member.islnk():
            raise SelfUpdateError("release asset contains a link member")
        if not (member.isdir() or member.isfile()):
            raise SelfUpdateError("release asset contains an unsupported member type")
        target = (extract_root / member.name).resolve()
        if target != root and not str(target).startswith(str(root) + os.sep):
            raise SelfUpdateError("release asset contains an unsafe path")
    archive.extractall(extract_root)


def _safe_extract_zip(archive: zipfile.ZipFile, extract_root: Path) -> None:
    root = extract_root.resolve()
    for member in archive.infolist():
        target = (extract_root / member.filename).resolve()
        if target != root and not str(target).startswith(str(root) + os.sep):
            raise SelfUpdateError("release asset contains an unsafe path")
    archive.extractall(extract_root)


def _install_bundle_into_current_runtime(bundle_dir: Path, release_version: str) -> None:
    wheels_dir = bundle_dir / "wheels"
    if not wheels_dir.is_dir():
        raise SelfUpdateError("release bundle is missing wheels/")
    wheels = sorted(wheels_dir.glob(f"ai_sdlc-{release_version}-*.whl"))
    if not wheels:
        raise SelfUpdateError(
            f"release bundle is missing the ai_sdlc {release_version} wheel"
        )
    if len(wheels) > 1:
        raise SelfUpdateError(
            f"release bundle contains multiple ai_sdlc {release_version} wheels"
        )
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "--no-index",
        f"--find-links={wheels_dir}",
        str(wheels[0]),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired as exc:
        raise SelfUpdateError("pip install timed out") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "pip install failed").strip()
        raise SelfUpdateError(_tail(detail))


def _read_installed_version() -> str:
    command = [
        sys.executable,
        "-c",
        "from importlib.metadata import version; print(version('ai-sdlc'))",
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise SelfUpdateError("version verification timed out") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "version verification failed").strip()
        raise SelfUpdateError(_tail(detail))
    return result.stdout.strip()


def _tail(text: str, limit: int = 800) -> str:
    if len(text) <= limit:
        return text
    return "..." + text[-limit:]


@self_update_app.command("instructions")
def self_update_instructions(
    version: str = typer.Option(
        "",
        "--version",
        help="Release version to install, for example 0.7.4.",
    ),
) -> None:
    """Point users to the automatic self-update command."""
    display_version = (version or "<version>").removeprefix("v")
    console.print(
        Panel(
            render_single_next_step(
                result_zh="这不是更新执行命令；当前安装尚未变化。",
                result_en="This is not the update execution command; your current install has not changed.",
                next_command=f"ai-sdlc self-update install --version {display_version}",
                next_zh="执行这一条命令即可自动下载、安装并校验版本。",
                next_en="Run this one command to download, install, and verify the version automatically.",
                notes=(
                    (
                        "正常用户不需要手动下载 release 包或运行离线安装脚本。",
                        "Normal users do not need to manually download release assets or run offline install scripts.",
                    ),
                ),
            ),
            title="AI-SDLC Self Update",
        )
    )
