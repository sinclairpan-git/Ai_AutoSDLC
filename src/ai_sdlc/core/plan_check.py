"""Read-only plan vs Git drift detection (FR-087 / plan-check CLI)."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from ai_sdlc.utils.helpers import _dedupe_text_items as _dedupe_text_items
from ai_sdlc.utils.helpers import find_project_root, is_git_repo


@dataclass(frozen=True, slots=True)
class CommandSurfaceReport:
    checked_command_count: int
    errors: tuple[str, ...] = ()

    @property
    def valid(self) -> bool:
        return self.checked_command_count > 0 and not self.errors


@dataclass(frozen=True, slots=True)
class _CommandSource:
    line: int
    text: str


_APPROVED_WRAPPERS = ("ai-sdlc", "uv run ai-sdlc", "python -m ai_sdlc")
_ASCII_WHITESPACE = " \t\r\f\v"


def _is_approved_command_source(text: str) -> bool:
    return any(text == wrapper or text.startswith(f"{wrapper} ") for wrapper in _APPROVED_WRAPPERS)


def _extract_ai_sdlc_command_sources(markdown: str) -> tuple[_CommandSource, ...]:
    sources: set[_CommandSource] = set()
    fence: tuple[str, int] | None = None
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        fence_match = re.match(r"^\s*([`~]{3,})", line)
        if fence is not None:
            if (
                fence_match is not None
                and fence_match.group(1)[0] == fence[0]
                and len(fence_match.group(1)) >= fence[1]
                and not line[fence_match.end() :].strip()
            ):
                fence = None
                continue
            text = line.strip()
            if _is_approved_command_source(text):
                sources.add(_CommandSource(line_number, text))
            continue
        if fence_match is not None:
            fence = (fence_match.group(1)[0], len(fence_match.group(1)))
            continue
        for match in re.finditer(r"(?<!`)`([^`\n]*)`(?!`)", line):
            text = match.group(1).strip()
            if _is_approved_command_source(text):
                sources.add(_CommandSource(line_number, text))
    return tuple(sorted(sources, key=lambda source: (source.line, source.text)))


def _tokenize_canonical_argv(text: str) -> tuple[tuple[str, ...], str | None]:
    reasons = {
        "|": "pipe", "&": "command separator", ";": "command separator",
        "<": "redirect", ">": "redirect", "$": "variable expansion",
        "`": "backtick", "\\": "escape",
    }
    for character, reason in reasons.items():
        if character in text:
            return (), reason

    tokens: list[str] = []
    cursor = 0
    length = len(text)
    while cursor < length:
        while cursor < length and text[cursor] in _ASCII_WHITESPACE:
            cursor += 1
        if cursor == length:
            break
        if text[cursor] in "\"'":
            quote = text[cursor]
            end = text.find(quote, cursor + 1)
            if end < 0:
                return (), "unclosed quote"
            token = text[cursor + 1 : end]
            cursor = end + 1
            if cursor < length and text[cursor] not in _ASCII_WHITESPACE:
                return (), "quoted/unquoted concatenation"
            tokens.append(token)
            continue
        end = cursor
        while end < length and text[end] not in _ASCII_WHITESPACE:
            if text[end] in "\"'":
                return (), "quoted/unquoted concatenation"
            end += 1
        tokens.append(text[cursor:end])
        cursor = end
    return tuple(tokens), None


def _canonical_argv(argv: tuple[str, ...]) -> tuple[tuple[str, ...], str | None]:
    for wrapper in (("ai-sdlc",), ("uv", "run", "ai-sdlc"), ("python", "-m", "ai_sdlc")):
        if argv[: len(wrapper)] == wrapper:
            return argv[len(wrapper) :], None
    return (), "unsupported command wrapper"


def _resolve_leaf_command(
    argv: tuple[str, ...],
) -> tuple[object | None, tuple[str, ...], str | None]:
    """返回 leaf command、剩余 argv 和稳定错误；只遍历公开 commands。"""
    import typer.main

    from ai_sdlc.cli.command_names import collect_flat_command_strings
    from ai_sdlc.cli.main import app

    paths = [
        tuple(path.split())[1:]
        for path in collect_flat_command_strings()
        if tuple(path.split())[1:] == argv[: len(tuple(path.split())[1:])]
    ]
    if not paths:
        return None, (), "unknown command"
    path = max(paths, key=len)
    command: object = typer.main.get_command(app)
    for part in path:
        commands = getattr(command, "commands", None)
        if not isinstance(commands, dict) or part not in commands:
            return None, (), "unsupported command metadata"
        command = commands[part]
    return command, argv[len(path) :], None


def _is_negative_number(token: str) -> bool:
    return re.fullmatch(r"-\d+(?:\.\d+)?", token) is not None


def _validate_leaf_argv(command: object, argv: tuple[str, ...]) -> str | None:
    """只用公开 parameter metadata 校验 option spelling 与 token arity。"""
    context_settings = getattr(command, "context_settings", {})
    if not isinstance(context_settings, dict) or any(
        context_settings.get(key, False)
        for key in ("allow_extra_args", "ignore_unknown_options")
    ):
        return "unsupported command metadata"
    params = getattr(command, "params", None)
    if not isinstance(params, list):
        return "unsupported command metadata"
    options: dict[str, object] = {}
    arguments: list[object] = []
    for param in params:
        param_type = getattr(param, "type", None)
        if type(param_type).__module__ not in {"click.types", "typer.models"}:
            return "unsupported command metadata"
        if getattr(param, "callback", None) is not None or getattr(param, "prompt", None):
            return "unsupported command metadata"
        opts = tuple(getattr(param, "opts", ()))
        secondary_opts = tuple(getattr(param, "secondary_opts", ()))
        if any(option.startswith("-") for option in opts + secondary_opts):
            for option in opts + secondary_opts:
                if not isinstance(option, str) or not option.startswith("-"):
                    return "unsupported command metadata"
                options[option] = param
        else:
            arguments.append(param)

    positionals: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--":
            return "extra token: --"
        if token.startswith("-") and not _is_negative_number(token):
            option, equals, _ = token.partition("=")
            if token.startswith("-") and not token.startswith("--") and len(option) > 2:
                return "short option aggregation"
            param = options.get(option)
            if param is None:
                return f"unknown option: {option}"
            is_flag = bool(getattr(param, "is_flag", False))
            count = bool(getattr(param, "count", False))
            nargs = getattr(param, "nargs", None)
            if not isinstance(nargs, int) or nargs < 0:
                return "unsupported command metadata"
            if equals:
                if not option.startswith("--") or is_flag or count or nargs != 1:
                    return f"invalid option value: {option}"
                index += 1
                continue
            if is_flag or count:
                index += 1
                continue
            if index + nargs >= len(argv):
                return f"missing value: {option}"
            values = argv[index + 1 : index + 1 + nargs]
            if any(value.startswith("-") and not _is_negative_number(value) for value in values):
                return f"missing value: {option}"
            index += nargs + 1
            continue
        positionals.append(token)
        index += 1

    position = 0
    for param in arguments:
        nargs = getattr(param, "nargs", None)
        if not isinstance(nargs, int) or nargs < 0:
            return "unsupported command metadata"
        if len(positionals) - position < nargs:
            if bool(getattr(param, "required", False)):
                return "missing argument"
            continue
        position += nargs
    if position != len(positionals):
        return f"extra token: {positionals[position]}"
    return None


def validate_plan_ai_sdlc_commands(markdown: str) -> CommandSurfaceReport:
    sources = _extract_ai_sdlc_command_sources(markdown)
    if not sources:
        return CommandSurfaceReport(0, ("no approved ai-sdlc commands found",))
    errors: list[str] = []
    for source in sources:
        try:
            argv, error = _tokenize_canonical_argv(source.text)
            if error is None:
                argv, error = _canonical_argv(argv)
            if error is None:
                command, remaining, error = _resolve_leaf_command(argv)
            if error is None and command is not None:
                error = _validate_leaf_argv(command, remaining)
        except Exception:
            error = "unsupported command metadata"
        if error is not None:
            errors.append(f"line {source.line}: {source.text}: {error}")
    return CommandSurfaceReport(len(sources), tuple(errors))


def parse_markdown_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    """Return (frontmatter dict, body) for a Markdown file with optional YAML FM."""
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, raw
    if not isinstance(fm, dict):
        return {}, raw
    return fm, parts[2]


def _resolve_plan_file(root: Path, wi_dir: Path, related: str) -> Path:
    rel = Path(related)
    if rel.is_absolute():
        return rel
    candidate = (root / rel).resolve()
    if candidate.exists():
        return candidate
    return (wi_dir / rel).resolve()


def resolve_plan_path_from_wi(root: Path, wi_dir: Path) -> Path | None:
    """Pick external plan file from tasks.md or plan.md frontmatter ``related_plan``."""
    for name in ("tasks.md", "plan.md"):
        p = wi_dir / name
        if not p.is_file():
            continue
        fm, _ = parse_markdown_frontmatter(p)
        rel = fm.get("related_plan")
        if isinstance(rel, str) and rel.strip():
            return _resolve_plan_file(root, wi_dir, rel.strip())
    return None


def count_pending_todos(frontmatter: dict[str, Any]) -> int:
    """Count todos with status ``pending`` (Cursor / IDE plan frontmatter)."""
    todos = frontmatter.get("todos")
    if not isinstance(todos, list):
        return 0
    n = 0
    for item in todos:
        if not isinstance(item, dict):
            continue
        status = item.get("status")
        if isinstance(status, str) and status.strip().lower() == "pending":
            n += 1
    return n


def git_changed_paths(root: Path) -> list[str]:
    """List paths with unstaged or staged changes vs HEAD (tracked/untracked)."""
    if not is_git_repo(root):
        return []

    out: list[str] = []
    # Porcelain: detect modified + untracked
    r1 = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if r1.returncode != 0:
        return []

    for line in r1.stdout.splitlines():
        if len(line) < 4:
            continue
        path_part = line[3:].strip()
        # rename: "R  old -> new"
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[-1].strip()
        if path_part:
            out.append(path_part)

    return sorted(set(out))


@dataclass
class PlanCheckResult:
    """Outcome of comparing plan todos vs Git working tree."""

    drift: bool
    plan_file: Path | None
    pending_todos: int
    changed_paths: list[str] = field(default_factory=list)
    error: str | None = None
    checked_command_count: int | None = None
    command_surface_valid: bool | None = None

    def __post_init__(self) -> None:
        self.changed_paths = _dedupe_text_items(self.changed_paths)

    def to_json_dict(self) -> dict[str, Any]:
        payload = {
            "drift": self.drift,
            "plan_file": str(self.plan_file) if self.plan_file else None,
            "pending_todos": self.pending_todos,
            "changed_paths": _dedupe_text_items(self.changed_paths),
            "error": self.error,
        }
        if self.command_surface_valid is not None:
            payload["checked_command_count"] = self.checked_command_count
            payload["command_surface_valid"] = self.command_surface_valid
        return payload


def run_plan_check(
    *,
    cwd: Path | None,
    wi: Path | None,
    plan: Path | None,
    check_ai_sdlc_commands: bool = False,
) -> PlanCheckResult:
    """Compare pending external-plan todos with Git changes under project root."""
    start = (cwd or Path.cwd()).resolve()
    root = find_project_root(start)
    if root is None:
        return PlanCheckResult(
            drift=False,
            plan_file=None,
            pending_todos=0,
            error="Not inside an AI-SDLC project (.ai-sdlc/ not found).",
        )

    plan_path: Path | None = None
    if plan is not None:
        plan_path = plan if plan.is_absolute() else (start / plan).resolve()
        if not plan_path.is_file():
            return PlanCheckResult(
                drift=False,
                plan_file=plan_path,
                pending_todos=0,
                error=f"Plan file not found: {plan_path}",
            )
    elif wi is not None:
        wi_dir = wi if wi.is_absolute() else (start / wi).resolve()
        if not wi_dir.is_dir():
            return PlanCheckResult(
                drift=False,
                plan_file=None,
                pending_todos=0,
                error=f"Work item directory not found: {wi_dir}",
            )
        plan_path = resolve_plan_path_from_wi(root, wi_dir)
        if plan_path is None or not plan_path.is_file():
            return PlanCheckResult(
                drift=False,
                plan_file=plan_path,
                pending_todos=0,
                error="No related_plan in tasks.md/plan.md or file missing.",
            )
    else:
        return PlanCheckResult(
            drift=False,
            plan_file=None,
            pending_todos=0,
            error="Specify --wi or --plan.",
        )

    fm, _ = parse_markdown_frontmatter(plan_path)
    pending = count_pending_todos(fm)
    if check_ai_sdlc_commands:
        report = validate_plan_ai_sdlc_commands(plan_path.read_text(encoding="utf-8"))
        return PlanCheckResult(
            drift=False,
            plan_file=plan_path,
            pending_todos=pending,
            changed_paths=[],
            error="\n".join(report.errors) if report.errors else None,
            checked_command_count=report.checked_command_count,
            command_surface_valid=report.valid,
        )
    changed = git_changed_paths(root)

    drift = pending > 0 and len(changed) > 0
    return PlanCheckResult(
        drift=drift,
        plan_file=plan_path,
        pending_todos=pending,
        changed_paths=changed,
        error=None,
    )


def format_json(result: PlanCheckResult) -> str:
    return json.dumps(result.to_json_dict(), ensure_ascii=False, indent=2)
