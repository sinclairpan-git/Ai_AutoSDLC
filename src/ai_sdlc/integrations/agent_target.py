"""Agent target detection and interactive selection helpers."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Mapping
from enum import Enum
from pathlib import Path
from typing import TextIO

from ai_sdlc.models.project import PreferredShell


class IDEKind(str, Enum):
    CURSOR = "cursor"
    VSCODE = "vscode"
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"
    GENERIC = "generic"


AGENT_TARGET_OPTIONS: tuple[IDEKind, ...] = (
    IDEKind.CLAUDE_CODE,
    IDEKind.CODEX,
    IDEKind.CURSOR,
    IDEKind.VSCODE,
    IDEKind.GENERIC,
)

_TARGET_LABELS: dict[IDEKind, str] = {
    IDEKind.CLAUDE_CODE: "Claude Code",
    IDEKind.CODEX: "Codex",
    IDEKind.CURSOR: "Cursor",
    IDEKind.VSCODE: "VS Code",
    IDEKind.GENERIC: "其他-通用",
}

_MARKER_PRIORITY: tuple[tuple[str, IDEKind], ...] = (
    (".cursor", IDEKind.CURSOR),
    (".codex", IDEKind.CODEX),
    (".claude", IDEKind.CLAUDE_CODE),
    (".vscode", IDEKind.VSCODE),
)

PREFERRED_SHELL_OPTIONS: tuple[PreferredShell, ...] = (
    PreferredShell.POWERSHELL,
    PreferredShell.BASH,
    PreferredShell.ZSH,
    PreferredShell.CMD,
    PreferredShell.AUTO,
)

_SHELL_LABELS: dict[PreferredShell, str] = {
    PreferredShell.POWERSHELL: "PowerShell",
    PreferredShell.BASH: "bash",
    PreferredShell.ZSH: "zsh",
    PreferredShell.CMD: "cmd",
    PreferredShell.AUTO: "auto",
}


def agent_target_label(kind: IDEKind) -> str:
    """Return the user-facing label for an agent target."""
    return _TARGET_LABELS[kind]


def preferred_shell_label(kind: PreferredShell) -> str:
    """Return the user-facing label for a preferred shell."""
    return _SHELL_LABELS[kind]


def recommended_shell_for_platform(platform: str | None = None) -> PreferredShell:
    """Return the recommended shell for the current host platform."""
    current = (platform or sys.platform).lower()
    if current.startswith("win"):
        return PreferredShell.POWERSHELL
    if current == "darwin":
        return PreferredShell.ZSH
    if current.startswith("linux"):
        return PreferredShell.BASH
    return PreferredShell.AUTO


def detect_agent_target(
    root: Path,
    *,
    environ: Mapping[str, str] | None = None,
) -> IDEKind:
    """Detect the most likely AI agent target for the current project."""
    env = environ or os.environ
    # Live agent runtime evidence is more authoritative than repo-local IDE
    # markers, which may be historical artifacts from a different tool.
    if env.get("OPENAI_CODEX") or env.get("CODEX_CLI_READY"):
        return IDEKind.CODEX
    if env.get("CLAUDE_CODE_ENTRYPOINT") or env.get("CLAUDECODE"):
        return IDEKind.CLAUDE_CODE
    if env.get("CURSOR_TRACE_ID") or env.get("CURSOR_AGENT"):
        return IDEKind.CURSOR
    if env.get("VSCODE_IPC_HOOK_CLI"):
        return IDEKind.VSCODE

    for dirname, kind in _MARKER_PRIORITY:
        if (root / dirname).is_dir():
            return kind

    if env.get("TERM_PROGRAM", "").lower() == "vscode":
        return IDEKind.VSCODE
    return IDEKind.GENERIC


def is_interactive_terminal() -> bool:
    """Return whether stdin/stdout appear to be interactive TTY streams."""
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:
        return False


def interactive_select_agent_target(
    default_target: IDEKind,
    *,
    output_stream: TextIO | None = None,
    read_key: Callable[[], str] | None = None,
) -> IDEKind:
    """Select an agent target with arrow keys and Enter confirmation."""
    output = output_stream or sys.stdout
    options = AGENT_TARGET_OPTIONS
    index = options.index(default_target) if default_target in options else len(options) - 1
    next_key = read_key or _read_selector_key

    while True:
        _render_selector(output, index)
        key = next_key()
        if key == "up":
            index = (index - 1) % len(options)
        elif key == "down":
            index = (index + 1) % len(options)
        elif key == "enter":
            output.write("\n")
            output.flush()
            return options[index]
        elif key == "interrupt":
            raise KeyboardInterrupt


def interactive_select_preferred_shell(
    default_shell: PreferredShell,
    *,
    output_stream: TextIO | None = None,
    read_key: Callable[[], str] | None = None,
) -> PreferredShell:
    """Select a preferred shell with arrow keys and Enter confirmation."""
    output = output_stream or sys.stdout
    options = PREFERRED_SHELL_OPTIONS
    index = options.index(default_shell) if default_shell in options else 0
    next_key = read_key or _read_selector_key

    while True:
        _render_shell_selector(output, index)
        key = next_key()
        if key == "up":
            index = (index - 1) % len(options)
        elif key == "down":
            index = (index + 1) % len(options)
        elif key == "enter":
            output.write("\n")
            output.flush()
            return options[index]
        elif key == "interrupt":
            raise KeyboardInterrupt


def _render_selector(output: TextIO, index: int) -> None:
    _clear_selector_screen(output)
    lines = [
        "请选择当前实际用于聊天开发的 AI 代理入口（方向键选择，回车确认）：",
    ]
    for position, option in enumerate(AGENT_TARGET_OPTIONS):
        prefix = ">" if position == index else " "
        lines.append(f"{prefix} {agent_target_label(option)}")
    output.write("\n".join(lines))
    output.flush()


def _render_shell_selector(output: TextIO, index: int) -> None:
    _clear_selector_screen(output)
    lines = [
        "请选择当前项目默认使用的命令 Shell（方向键选择，回车确认）：",
    ]
    for position, option in enumerate(PREFERRED_SHELL_OPTIONS):
        prefix = ">" if position == index else " "
        lines.append(f"{prefix} {preferred_shell_label(option)}")
    output.write("\n".join(lines))
    output.flush()


def _clear_selector_screen(output: TextIO) -> None:
    if not _selector_output_is_tty(output):
        should_separate = False
        tell = getattr(output, "tell", None)
        if callable(tell):
            try:
                should_separate = tell() > 0
            except Exception:
                should_separate = False
        if should_separate:
            output.write("\n")
        return
    if os.name == "nt":
        os.system("cls")
        return
    output.write("\x1b[2J\x1b[H")


def _selector_output_is_tty(output: TextIO) -> bool:
    isatty = getattr(output, "isatty", None)
    if not callable(isatty):
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


def _read_selector_key() -> str:
    if os.name == "nt":
        return _read_selector_key_windows()
    return _read_selector_key_posix()


def _read_selector_key_windows() -> str:
    import msvcrt  # pragma: no cover

    while True:  # pragma: no cover
        key = msvcrt.getwch()
        if key in ("\r", "\n"):
            return "enter"
        if key == "\x03":
            return "interrupt"
        if key in ("\x00", "\xe0"):
            arrow = msvcrt.getwch()
            if arrow == "H":
                return "up"
            if arrow == "P":
                return "down"


def _read_selector_key_posix() -> str:
    import termios  # pragma: no cover
    import tty  # pragma: no cover

    stream = sys.stdin
    fd = stream.fileno()
    original = termios.tcgetattr(fd)
    try:  # pragma: no cover
        tty.setraw(fd)
        first = stream.read(1)
        if first in ("\r", "\n"):
            return "enter"
        if first == "\x03":
            return "interrupt"
        if first == "\x1b":
            second = stream.read(1)
            third = stream.read(1)
            if second == "[" and third == "A":
                return "up"
            if second == "[" and third == "B":
                return "down"
        return first
    finally:  # pragma: no cover
        termios.tcsetattr(fd, termios.TCSADRAIN, original)
