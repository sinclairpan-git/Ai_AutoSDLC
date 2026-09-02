"""Unit tests for plan vs Git drift logic (FR-087)."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import click
import pytest

import ai_sdlc.core.plan_check as pc
from ai_sdlc.core.plan_check import (
    CommandSurfaceReport,
    PlanCheckResult,
    count_pending_todos,
    git_changed_paths,
    parse_markdown_frontmatter,
    resolve_plan_path_from_wi,
    run_plan_check,
    validate_plan_ai_sdlc_commands,
)
from ai_sdlc.utils.helpers import _dedupe_text_items as dedupe


class _CustomParamType(click.ParamType):
    name = "custom"


def test_shared_text_dedupe_contract() -> None:
    value = MagicMock(**{"__str__.side_effect": RuntimeError("boom")})
    assert pc._dedupe_text_items is dedupe and dedupe(None) == []
    assert dedupe([" beta ", "", "alpha", "beta"]) == ["beta", "alpha"]
    with pytest.raises(RuntimeError, match="boom"):
        dedupe([value])


def test_count_pending_todos() -> None:
    fm = {
        "todos": [
            {"id": "a", "status": "pending"},
            {"id": "b", "status": "completed"},
            {"id": "c", "status": "pending"},
        ]
    }
    assert count_pending_todos(fm) == 2
    assert count_pending_todos({}) == 0
    assert count_pending_todos({"todos": "bad"}) == 0


def test_parse_markdown_frontmatter(tmp_path: Path) -> None:
    p = tmp_path / "x.md"
    p.write_text(
        "---\nfoo: 1\ntodos:\n  - id: a\n    status: pending\n---\nBody\n",
        encoding="utf-8",
    )
    fm, body = parse_markdown_frontmatter(p)
    assert fm.get("foo") == 1
    assert "Body" in body


def test_resolve_plan_path_from_wi(tmp_path: Path) -> None:
    root = tmp_path
    wi = root / "specs/001-wi"
    wi.mkdir(parents=True)
    plan_dir = root / ".cursor" / "plans"
    plan_dir.mkdir(parents=True)
    plan_file = plan_dir / "p.md"
    plan_file.write_text("---\ntodos: []\n---\n")
    (wi / "tasks.md").write_text(
        '---\nrelated_plan: ".cursor/plans/p.md"\n---\n',
        encoding="utf-8",
    )
    got = resolve_plan_path_from_wi(root, wi)
    assert got == plan_file.resolve()


@pytest.fixture()
def git_project_with_plan(tmp_path: Path) -> Path:
    """Git repo with .ai-sdlc, specs WI, and external plan with one pending todo."""
    root = tmp_path / "proj"
    root.mkdir()
    subprocess.run(
        ["git", "init", "--initial-branch=main"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=root,
        check=True,
        capture_output=True,
    )

    ai = root / ".ai-sdlc" / "project" / "config"
    ai.mkdir(parents=True)
    (ai / "project-state.yaml").write_text(
        "status: initialized\nproject_name: p\nnext_work_item_seq: 1\nversion: '1.0'\n",
        encoding="utf-8",
    )

    plan_dir = root / ".cursor" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "p.md").write_text(
        "---\n"
        "todos:\n"
        "  - id: x\n    content: Work\n    status: pending\n"
        "---\n\n# P\n",
        encoding="utf-8",
    )

    wi = root / "specs" / "001-wi"
    wi.mkdir(parents=True)
    (wi / "tasks.md").write_text(
        '---\nrelated_plan: ".cursor/plans/p.md"\n---\n',
        encoding="utf-8",
    )

    (root / "README.md").write_text("# R\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return root


def test_run_plan_check_drift_pending_and_dirty(git_project_with_plan: Path) -> None:
    (git_project_with_plan / "README.md").write_text("# changed\n", encoding="utf-8")
    r = run_plan_check(
        cwd=git_project_with_plan,
        wi=Path("specs/001-wi"),
        plan=None,
    )
    assert r.error is None
    assert r.drift is True
    assert r.pending_todos == 1
    assert len(r.changed_paths) >= 1


def test_run_plan_check_no_drift_pending_clean_tree(git_project_with_plan: Path) -> None:
    r = run_plan_check(
        cwd=git_project_with_plan,
        wi=Path("specs/001-wi"),
        plan=None,
    )
    assert r.error is None
    assert r.drift is False
    assert r.pending_todos == 1


def test_git_changed_paths_empty_when_not_git(tmp_path: Path) -> None:
    assert git_changed_paths(tmp_path) == []


def test_plan_check_to_json_dict_deduplicates_changed_paths() -> None:
    payload = PlanCheckResult(
        drift=True,
        plan_file=None,
        pending_todos=1,
        changed_paths=["README.md", "README.md"],
    ).to_json_dict()

    assert payload["changed_paths"] == ["README.md"]


def test_plan_check_result_canonicalizes_runtime_changed_paths() -> None:
    result = PlanCheckResult(
        drift=True,
        plan_file=None,
        pending_todos=1,
        changed_paths=["README.md", "README.md"],
    )

    assert result.changed_paths == ["README.md"]


@pytest.mark.parametrize(
    ("command", "expected_fragment"),
    [
        ("ai-sdlc workitem truth-sync", "unknown command"),
        ("uv run ai-sdlc workitem truth-audit", "unknown command"),
        (
            "python -m ai_sdlc workitem plan-check --wi-id specs/226",
            "unknown option: --wi-id",
        ),
        ("ai-sdlc workitem plan-check --wi", "missing value: --wi"),
    ],
)
def test_command_surface_rejects_invalid_path_option_and_arity(
    command: str, expected_fragment: str
) -> None:
    report = validate_plan_ai_sdlc_commands(f"```text\n{command}\n```\n")

    assert report.valid is False
    assert expected_fragment in "\n".join(report.errors)


def test_command_surface_accepts_three_wrappers_and_secondary_flag() -> None:
    report = validate_plan_ai_sdlc_commands(
        "\n".join(
            [
                "`ai-sdlc program truth sync --dry-run`",
                "`uv run ai-sdlc program truth audit`",
                "`python -m ai_sdlc workitem plan-check --wi specs/226`",
                "`ai-sdlc program truth audit --manifest=program-manifest.yaml`",
                "`ai-sdlc program truth sync --execute --yes`",
            ]
        )
    )

    assert report == CommandSurfaceReport(checked_command_count=5)
    grouped = validate_plan_ai_sdlc_commands("`ai-sdlc program truth sync -xy`")
    assert grouped.valid is False
    assert "short option aggregation" in "\n".join(grouped.errors)


def test_command_surface_rejects_zero_match_and_shell_surfaces() -> None:
    report = validate_plan_ai_sdlc_commands(
        "\n".join(
            [
                "no approved command here",
                "`ai-sdlc program truth audit | more`",
                "`ai-sdlc program truth audit > output.txt`",
                "`ai-sdlc program truth audit $(whoami)`",
                "`ai-sdlc program truth audit; other`",
                "```text",
                "ai-sdlc program truth audit `",
                "```",
                "```text",
                "ai-sdlc program truth audit \\",
                "--manifest program-manifest.yaml",
                "```",
            ]
        )
    )

    assert report.valid is False
    errors = "\n".join(report.errors)
    for fragment in ("pipe", "redirect", "variable", "backtick", "command separator", "escape"):
        assert fragment in errors

    zero = validate_plan_ai_sdlc_commands("ordinary prose only")
    assert zero.checked_command_count == 0
    assert zero.errors == ("no approved ai-sdlc commands found",)


def test_command_surface_preserves_physical_lines_deduplicates_fences_and_aggregates_errors() -> None:
    markdown = """---
title: command test
---

`ai-sdlc workitem truth-sync`

```text
ai-sdlc workitem truth-audit
```
"""

    report = validate_plan_ai_sdlc_commands(markdown)

    assert report.checked_command_count == 2
    assert report.valid is False
    assert report.errors == tuple(sorted(report.errors))
    assert report.errors[0].startswith("line 5:")
    assert report.errors[1].startswith("line 8:")


@pytest.mark.parametrize(
    "command",
    [
        click.Command(
            "audit",
            params=[
                click.Option(
                    ["--value"], callback=lambda _ctx, _param, value: value
                )
            ],
        ),
        click.Command("audit", params=[click.Option(["--value"], prompt=True)]),
        click.Command(
            "audit",
            params=[click.Option(["--value"], type=_CustomParamType())],
        ),
        click.Command("audit", context_settings={"allow_extra_args": True}),
        click.Command("audit", context_settings={"ignore_unknown_options": True}),
    ],
)
def test_command_surface_fail_closes_unsupported_leaf_metadata(command: click.Command) -> None:
    assert pc._validate_leaf_argv(command, ()) == "unsupported command metadata"


def test_command_surface_never_invokes_callback_or_touches_sentinel(tmp_path: Path) -> None:
    sentinel = tmp_path / "callback-ran"
    calls = 0

    def callback(_: object) -> object:
        nonlocal calls
        calls += 1
        sentinel.write_text("ran", encoding="utf-8")
        return _

    command = click.Command(
        "audit",
        callback=callback,
        params=[click.Option(["--execute"], is_flag=True, callback=callback)],
    )

    assert pc._validate_leaf_argv(command, ("--execute",)) == "unsupported command metadata"
    assert calls == 0
    assert sentinel.exists() is False


def test_command_surface_mode_does_not_run_git_subprocess(
    git_project_with_plan: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = git_project_with_plan / ".cursor" / "plans" / "commands.md"
    plan.write_text("`ai-sdlc program truth audit`\n", encoding="utf-8")

    def fail_if_called(_: Path) -> list[str]:
        raise AssertionError("git_changed_paths must not run in command-surface mode")

    monkeypatch.setattr(pc, "git_changed_paths", fail_if_called)
    result = run_plan_check(
        cwd=git_project_with_plan,
        wi=None,
        plan=plan,
        check_ai_sdlc_commands=True,
    )

    assert result.error is None
    assert result.drift is False
    assert result.changed_paths == []
    assert result.checked_command_count == 1
    assert result.command_surface_valid is True


def test_plan_check_default_json_contract_has_no_command_surface_keys() -> None:
    payload = PlanCheckResult(
        drift=False,
        plan_file=Path("plan.md"),
        pending_todos=0,
    ).to_json_dict()

    assert set(payload) == {
        "drift",
        "plan_file",
        "pending_todos",
        "changed_paths",
        "error",
    }
