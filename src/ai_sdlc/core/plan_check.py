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

def _extract_ai_sdlc_command_sources(markdown: str, errors: list[str]) -> tuple[_CommandSource, ...]:
    def accepts(text: str) -> bool:
        return any(text.startswith(w) and (len(text) == len(w) or text[len(w)] in _ASCII_WHITESPACE) for w in _APPROVED_WRAPPERS)

    sources: set[_CommandSource] = set()
    fence: tuple[str, int, int] | None = None
    for number, line in enumerate(markdown.splitlines(), start=1):
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence is not None:
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] and not line[match.end() :].strip():
                fence = None
                continue
            if match and not line[match.end() :].strip():
                errors.append(f"line {number}: mismatched fenced code block (opened line {fence[2]})")
            text = line.strip()
            if accepts(text):
                sources.add(_CommandSource(number, text))
            continue
        if match:
            fence = (match.group(1)[0], len(match.group(1)), number)
            continue
        for match in re.finditer(r"(?<!`)`([^`\n]*)`(?!`)", line):
            text = match.group(1).strip()
            if accepts(text):
                sources.add(_CommandSource(number, text))
    if fence is not None:
        errors.append(f"line {fence[2]}: unclosed fenced code block")
    return tuple(sorted(sources, key=lambda source: (source.line, source.text)))


def _tokenize_canonical_argv(text: str) -> tuple[tuple[str, ...], str | None]:
    if "\n" in text or "\r" in text:
        return (), "newline"
    for character, reason in (("|", "pipe"), ("&", "command separator"), (";", "command separator"), ("<", "redirect"), (">", "redirect"), ("$", "variable expansion"), ("`", "backtick")):
        if character in text:
            return (), reason
    tokens: list[str] = []
    cursor, length = 0, len(text)
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
            if text[end] == "\\":
                return (), "escape"
            end += 1
        tokens.append(text[cursor:end])
        cursor = end
    return tuple(tokens), None


def _resolve_leaf_command(argv: tuple[str, ...]) -> tuple[object | None, tuple[str, ...], str | None]:
    """返回 leaf command、剩余 argv 和稳定错误；只遍历公开 commands。"""
    import typer.main

    from ai_sdlc.cli.command_names import collect_flat_command_strings
    from ai_sdlc.cli.main import app
    path = max((p for value in collect_flat_command_strings() if (p := tuple(value.split()[1:])) == argv[: len(p)]), key=len, default=())
    if not path:
        return None, (), "unknown command"
    command: object = typer.main.get_command(app)
    for part in path:
        commands = getattr(command, "commands", None)
        if not isinstance(commands, dict) or part not in commands:
            return None, (), "unsupported command metadata"
        command = commands[part]
    return command, argv[len(path) :], None

def _validate_leaf_argv(command: object, argv: tuple[str, ...]) -> str | None:
    """只用公开 parameter metadata 校验 option spelling 与 token arity。"""
    context_settings = getattr(command, "context_settings", {})
    if not isinstance(context_settings, dict) or any(context_settings.get(key, False) for key in ("allow_extra_args", "ignore_unknown_options")):
        return "unsupported command metadata"
    params = getattr(command, "params", None)
    if not isinstance(params, list):
        return "unsupported command metadata"
    options: dict[str, object] = {}
    arguments: list[object] = []
    required_options: list[tuple[int, str]] = []
    for param in params:
        param_type = getattr(param, "type", None)
        if type(param_type).__module__ not in {"click.types", "typer.models"} or getattr(param, "callback", None) is not None or getattr(param, "prompt", None):
            return "unsupported command metadata"
        names = tuple(getattr(param, "opts", ())) + tuple(getattr(param, "secondary_opts", ()))
        if any(name.startswith("-") for name in names):
            if not all(isinstance(name, str) and name.startswith("-") for name in names):
                return "unsupported command metadata"
            options.update(dict.fromkeys(names, param))
            if bool(getattr(param, "required", False)):
                required_options.append((id(param), next((name for name in names if name.startswith("--")), names[0])))
        else:
            arguments.append(param)
    if any(not bool(getattr(param, "required", False)) for param in arguments[:-1]):
        return "unsupported command metadata"
    positionals: list[str] = []
    provided_options: set[int] = set()
    index = 0
    while index < len(argv):
        token = argv[index]
        if token == "--":
            return "extra token: --"
        if token.startswith("-") and not re.fullmatch(r"-\d+(?:\.\d+)?", token):
            option, equals, _ = token.partition("=")
            if token.startswith("-") and not token.startswith("--") and len(option) > 2:
                return "short option aggregation"
            param = options.get(option)
            if param is None:
                return f"unknown option: {option}"
            provided_options.add(id(param))
            is_flag, count = bool(getattr(param, "is_flag", False)), bool(getattr(param, "count", False))
            if equals and (not option.startswith("--") or is_flag or count or getattr(param, "nargs", None) != 1):
                return f"invalid option value: {option}"
            if equals:
                index += 1
                continue
            if is_flag or count:
                index += 1
                continue
            nargs = getattr(param, "nargs", None)
            if not isinstance(nargs, int) or nargs < 0:
                return "unsupported command metadata"
            values = argv[index + 1 : index + 1 + nargs]
            if len(values) != nargs or any(value.startswith("-") and not re.fullmatch(r"-\d+(?:\.\d+)?", value) for value in values):
                return f"missing value: {option}"
            index += nargs + 1
            continue
        positionals.append(token)
        index += 1

    for param_id, option in required_options:
        if param_id not in provided_options:
            return f"missing option: {option}"
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
    errors: list[str] = []
    sources = _extract_ai_sdlc_command_sources(markdown, errors)
    if not sources:
        return CommandSurfaceReport(0, tuple(errors or ["no approved ai-sdlc commands found"]))
    for source in sources:
        try:
            argv, error = _tokenize_canonical_argv(source.text)
            if error is None:
                wrapper = next((w for w in (("ai-sdlc",), ("uv", "run", "ai-sdlc"), ("python", "-m", "ai_sdlc")) if argv[: len(w)] == w), ())
                argv, error = (argv[len(wrapper) :], None) if wrapper else ((), "unsupported command wrapper")
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
            error=f"{plan_path}: " + "\n".join(report.errors) if report.errors else None,
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
