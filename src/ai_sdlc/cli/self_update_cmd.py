"""Self-update advisor commands."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

import typer
from rich.console import Console
from rich.panel import Panel

from ai_sdlc.cli.beginner_guidance import render_single_next_step
from ai_sdlc.core.update_advisor import (
    EXPLICIT_CHECK_TIMEOUT_SECONDS,
    NOTICE_ACTIONABLE,
    REFRESH_BACKOFF,
    REFRESH_NETWORK_ERROR,
    REFRESH_PARSE_ERROR,
    REFRESH_TIMEOUT,
    ack_notice,
    detect_runtime_identity,
    evaluate_update_advisor,
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


@dataclass(frozen=True)
class PathCandidate:
    path: str
    version: str | None
    error: str | None = None


def _print_json(payload: dict[str, object]) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def maybe_render_update_notice() -> None:
    """Prompt installed CLI users and AI sessions when a newer release exists."""
    if not should_auto_render_notice():
        return
    evaluation = evaluate_update_advisor()
    if (
        NOTICE_ACTIONABLE not in evaluation.eligible_notice_classes
        or not evaluation.upgrade_command
    ):
        return
    current_version = evaluation.runtime_identity.installed_version or "unknown"
    latest_version = evaluation.channel_latest_version or evaluation.upstream_latest_version
    if not latest_version:
        return

    prompt = _update_confirmation_prompt(current_version, latest_version)
    if _can_prompt_for_update_confirmation():
        if not typer.confirm(prompt, default=False, err=True):
            notice_console.print("已跳过本次升级，继续执行当前命令。")
            return
        self_update_install(version=latest_version)
        raise typer.Exit(0)

    notice_console.print(
        Panel(
            "\n".join(
                [
                    prompt,
                    "请在对话中回复“确认升级”或“y”；AI 助手应执行：ai-sdlc self-update check",
                    "If you approve the update in chat, the AI assistant should run: ai-sdlc self-update check",
                ]
            ),
            title="AI-SDLC Update",
            border_style="yellow",
        )
    )


def _update_confirmation_prompt(current_version: str, latest_version: str) -> str:
    return (
        f"当前AI-SDLC版本是{current_version}，最新版本是{latest_version}，"
        "是否升级？回复 y/n"
    )


def _can_prompt_for_update_confirmation() -> bool:
    if os.environ.get("AI_SDLC_UPDATE_ADVISOR_FORCE_TTY") == "1":
        return True
    try:
        return bool(sys.stdin.isatty()) and bool(sys.stderr.isatty())
    except OSError:
        return False


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
    evaluation = evaluate_update_advisor(
        allow_refresh=True,
        ignore_failure_backoff=True,
        timeout_seconds=EXPLICIT_CHECK_TIMEOUT_SECONDS,
    )
    if json_output:
        _print_json(evaluation.to_machine_dict())
        return

    target_version = evaluation.channel_latest_version or evaluation.upstream_latest_version
    if evaluation.upgrade_command and target_version:
        console.print(
            Panel(
                render_single_next_step(
                    result_zh=f"检测到可更新版本：AI-SDLC {target_version}，现在自动更新。",
                    result_en=f"Update available: AI-SDLC {target_version}. Updating now.",
                    next_command=None,
                    next_zh="无需复制下一条命令；CLI 会继续下载、安装并校验版本。",
                    next_en="No extra command is needed; the CLI will download, install, and verify the version.",
                ),
                title="AI-SDLC Self Update",
                border_style="yellow",
            )
        )
        self_update_install(version=target_version)
        return

    lines = render_notice_lines(evaluation)
    if lines:
        if evaluation.refresh_result in {
            REFRESH_BACKOFF,
            REFRESH_NETWORK_ERROR,
            REFRESH_PARSE_ERROR,
            REFRESH_TIMEOUT,
        }:
            console.print(
                Panel(
                    render_single_next_step(
                        result_zh="本次无法刷新 AI-SDLC 最新版本信息，当前安装尚未变化。",
                        result_en="AI-SDLC could not refresh latest-version truth; the current install was not changed.",
                        next_command="ai-sdlc self-update check",
                        next_zh="网络恢复后重新执行同一条命令；显式 check 会重新尝试，不会被上次失败缓存挡住。",
                        next_en="After network access recovers, rerun the same command; explicit check retries instead of being blocked by the previous failure cache.",
                        notes=(
                            (
                                "如果你已经拿到更新版本的 Release 离线包，请在解压后的包目录执行 `./install_offline.sh --upgrade-existing`。",
                                "If you already have the newer Release offline package, run `./install_offline.sh --upgrade-existing` from the unpacked bundle directory.",
                            ),
                            (
                                "Windows 使用 `powershell -ExecutionPolicy Bypass -File .\\install_offline.ps1 -UpgradeExisting`。",
                                "On Windows, use `powershell -ExecutionPolicy Bypass -File .\\install_offline.ps1 -UpgradeExisting`.",
                            ),
                        ),
                    ),
                    title="AI-SDLC Self Update",
                    border_style="red",
                )
            )
            raise typer.Exit(1)
        console.print(Panel("\n".join(lines), title="AI-SDLC Update Advisor"))
        return

    installed = evaluation.runtime_identity.installed_version or "unknown"
    if evaluation.reason_code in {
        "source_or_module_runtime",
        "editable_runtime",
        "distribution_not_found",
    }:
        result_zh = "当前是源码/开发运行环境，不执行自动更新。"
        result_en = "Current runtime is source/development mode; automatic update is skipped."
    else:
        result_zh = f"当前已是最新可用版本：AI-SDLC {installed}。"
        result_en = f"Current AI-SDLC is already up to date: {installed}."
    console.print(
        Panel(
            render_single_next_step(
                result_zh=result_zh,
                result_en=result_en,
                next_command=None,
                next_zh="不需要继续执行升级命令。",
                next_en="No further update command is needed.",
            ),
            title="AI-SDLC Self Update",
            border_style="green",
        )
    )


@self_update_app.command("install")
def self_update_install(
    version: str = typer.Option(
        ...,
        "--version",
        help="Release version to install, for example 0.7.10.",
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
            _repair_current_user_path_if_possible()
            bare_version: str | None
            try:
                bare_version = _verify_bare_cli_version(release_version)
            except SelfUpdateError:
                if shutil.which("ai-sdlc"):
                    raise
                bare_version = None
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

    verification_note = (
        (
            f"已校验命令：ai-sdlc --version => {bare_version}",
            f"Verified command: ai-sdlc --version => {bare_version}",
        )
        if bare_version is not None
        else (
            f"已校验安装版本：AI-SDLC {installed_version}",
            f"Verified installed version: AI-SDLC {installed_version}",
        )
    )
    console.print(
        Panel(
            render_single_next_step(
                result_zh=f"更新完成：当前 AI-SDLC 已是 {installed_version}。",
                result_en=f"Update completed: current AI-SDLC is {installed_version}.",
                next_command=None,
                next_zh="不需要继续执行升级命令；回到原项目继续使用 AI-SDLC。",
                next_en="No more update commands are needed; return to your project and keep using AI-SDLC.",
                notes=(verification_note,),
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


def _candidate_names() -> tuple[str, ...]:
    if sys.platform == "win32":
        return ("ai-sdlc.exe", "ai-sdlc.cmd", "ai-sdlc.bat", "ai-sdlc")
    return ("ai-sdlc",)


def _discover_path_candidates(env_path: str | None = None) -> list[PathCandidate]:
    path_value = env_path if env_path is not None else os.environ.get("PATH", "")
    seen: set[str] = set()
    candidates: list[PathCandidate] = []
    for raw_entry in path_value.split(os.pathsep):
        if not raw_entry:
            continue
        entry = Path(raw_entry)
        for name in _candidate_names():
            candidate = entry / name
            if not candidate.exists() or not candidate.is_file():
                continue
            try:
                key = str(candidate.resolve()).lower()
            except OSError:
                key = str(candidate).lower()
            if key in seen:
                continue
            seen.add(key)
            version, error = _read_cli_candidate_version(candidate)
            candidates.append(
                PathCandidate(path=str(candidate), version=version, error=error)
            )
            break
    return candidates


def _read_cli_candidate_version(candidate: Path) -> tuple[str | None, str | None]:
    try:
        result = subprocess.run(
            [str(candidate), "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, _tail(str(exc), limit=200)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "version command failed").strip()
        return None, _tail(detail, limit=200)
    version = result.stdout.strip().splitlines()[-1].strip() if result.stdout else ""
    return version or None, None


def _verify_bare_cli_version(expected_version: str) -> str:
    candidates = _discover_path_candidates()
    resolved = shutil.which("ai-sdlc")
    if resolved:
        version, _error = _read_cli_candidate_version(Path(resolved))
        if version == expected_version:
            return version

    if sys.platform != "win32":
        raise SelfUpdateError(
            "更新已安装；请重新打开终端后再次执行 ai-sdlc self-update check 完成确认。"
        )

    preferred_dirs = _preferred_cli_dirs_for_update(expected_version, candidates)
    for preferred_dir in preferred_dirs:
        _prefer_cli_dir_in_process_path(preferred_dir)
        _repair_user_path_if_possible(preferred_dir)

    resolved = shutil.which("ai-sdlc")
    if resolved:
        version, _error = _read_cli_candidate_version(Path(resolved))
        if version == expected_version:
            return version

    # Keep default output user-facing. Detailed PATH diagnostics stay out of
    # normal update screens because beginners cannot act on them reliably.
    raise SelfUpdateError(
        "更新已安装；请重新打开终端后再次执行 ai-sdlc self-update check 完成确认。"
    )


def _preferred_cli_dirs_for_update(
    expected_version: str, candidates: list[PathCandidate]
) -> list[Path]:
    dirs: list[Path] = []
    current_dir = _current_cli_directory()
    if current_dir is not None:
        dirs.append(current_dir)
    for candidate in candidates:
        if candidate.version != expected_version:
            continue
        candidate_dir = Path(candidate.path).parent
        if candidate_dir not in dirs:
            dirs.append(candidate_dir)
    return dirs


def _current_cli_directory() -> Path | None:
    executable = Path(sys.executable)
    if sys.platform == "win32" and executable.name.lower() == "python.exe":
        if executable.parent.name.lower() == "scripts":
            return executable.parent
    argv0 = Path(sys.argv[0])
    if argv0.name.lower() in _candidate_names():
        return argv0.parent
    return None


def _repair_current_user_path_if_possible() -> None:
    if sys.platform != "win32":
        return
    cli_dir = _current_cli_directory()
    if cli_dir is None:
        return
    _repair_user_path_if_possible(cli_dir)


def _prefer_current_cli_dir_in_process_path() -> None:
    cli_dir = _current_cli_directory()
    if cli_dir is None:
        return
    _prefer_cli_dir_in_process_path(cli_dir)


def _repair_user_path_if_possible(preferred_dir: Path) -> None:
    if sys.platform == "win32":
        _repair_windows_user_path(preferred_dir)


def _prefer_cli_dir_in_process_path(cli_dir: Path) -> None:
    entries = _dedupe_preferred_path_entries(
        os.environ.get("PATH", ""),
        str(cli_dir),
    )
    os.environ["PATH"] = os.pathsep.join(entries)


def _repair_windows_user_path(preferred_dir: Path) -> None:
    """Prefer the current ai-sdlc directory in User PATH without deleting files."""

    try:
        import winreg  # type: ignore[import-not-found]
    except ImportError:  # pragma: no cover - only available on Windows.
        return
    preferred = _norm_path(preferred_dir)
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        "Environment",
        0,
        winreg.KEY_READ | winreg.KEY_SET_VALUE,
    ) as key:
        try:
            current_user_path, value_type = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_user_path, value_type = "", winreg.REG_EXPAND_SZ
        entries = _dedupe_preferred_path_entries(
            str(current_user_path),
            preferred,
        )
        winreg.SetValueEx(key, "Path", 0, value_type, os.pathsep.join(entries))

    os.environ["PATH"] = os.pathsep.join(
        _dedupe_preferred_path_entries(
            os.environ.get("PATH", ""),
            preferred,
        )
    )


def _dedupe_preferred_path_entries(
    path_value: str,
    preferred_dir: str,
) -> list[str]:
    # 只前置当前 CLI 目录；旧目录可能是共享 Scripts 目录，不能静默移除。
    preferred_norm = _norm_path(Path(preferred_dir))
    result = [preferred_dir]
    seen = {preferred_norm}
    for raw_entry in path_value.split(os.pathsep):
        entry = raw_entry.strip()
        if not entry:
            continue
        normalized = _norm_path(Path(entry))
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(entry)
    return result


def _norm_path(path: Path) -> str:
    try:
        resolved = path.expanduser().resolve()
    except OSError:
        resolved = path.expanduser()
    text = str(resolved)
    return text.lower() if sys.platform == "win32" else text


def _tail(text: str, limit: int = 800) -> str:
    if len(text) <= limit:
        return text
    return "..." + text[-limit:]


@self_update_app.command("instructions")
def self_update_instructions(
    version: str = typer.Option(
        "",
        "--version",
        help="Release version to install, for example 0.7.10.",
    ),
) -> None:
    """Point users to the automatic self-update command."""
    display_version = (version or "<version>").removeprefix("v")
    console.print(
        Panel(
            render_single_next_step(
                result_zh="这不是更新执行命令；当前安装尚未变化。",
                result_en="This is not the update execution command; your current install has not changed.",
                next_command="ai-sdlc self-update check",
                next_zh=(
                    "执行这一条命令即可自动检查最新 release，并在需要时下载、"
                    f"安装并校验版本；目标版本示例：{display_version}。"
                ),
                next_en=(
                    "Run this one command to check the latest release and, when needed, "
                    f"download, install, and verify it; example target: {display_version}."
                ),
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
