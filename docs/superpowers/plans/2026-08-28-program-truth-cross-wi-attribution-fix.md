# Program Truth Cross-WI Attribution Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent an unrelated work-item branch from proving execution for historical work items during `workitem truth-check` and Program Truth sync.

**Architecture:** Keep the existing merge-base and execution-log history algorithms. Before classifying branch-local changed paths, require the diff to contain a canonical or scoped control path for the requested work item; otherwise treat the branch-local path set as unattributed and empty.

**Tech Stack:** Python 3.11+, pytest, Typer CLI, Git fixtures

**Spec:** `docs/FRAMEWORK_ROADMAP.zh-CN.md` §10.4 D2

## Global Constraints

- Do not change work-item schemas, Program Truth schemas, lifecycle states, or CLI arguments.
- Preserve `branch_only_implemented` for branches that contain the requested WI controls plus implementation paths.
- Preserve mainline historical implementation detection from canonical execution-log evidence.
- Add one behavior-level regression and the minimum production change needed to pass it.

---

### Task 1: Bind branch-local paths to the requested work item

**Files:**
- Modify: `tests/integration/test_cli_workitem_truth_check.py`
- Modify: `src/ai_sdlc/core/workitem_truth.py`

**Interfaces:**
- Consumes: `run_truth_check(cwd: Path | None, wi: Path, rev: str | None)` and the existing merge-base changed-path set.
- Produces: requested-WI-attributed `changed_paths`, `execution_started`, and `classification` without changing the result schema.

- [x] **Step 1: Write the failing regression test**

```python
def test_truth_check_ignores_unrelated_formal_branch_for_historical_work_item(
    self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _init_repo(root)
    _commit_all(root, "init")
    historical_id = "095-historical-formal-only"
    _write_formal_docs(root / "specs" / historical_id, include_exec_log=True)
    _commit_all(root, "formalize historical work item")

    subprocess.run(
        ["git", "checkout", "-b", "feature/220-formal"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    _write_formal_control_change_set(root, "220-unrelated-formal")
    _commit_all(root, "formalize unrelated work item")

    payload = _truth_payload(root, monkeypatch, historical_id)

    assert payload["classification"] == "formal_freeze_only"
    assert payload["execution_started"] is False
    assert payload["changed_paths"] == []
    assert payload["code_paths"] == []
    assert payload["test_paths"] == []
```

- [x] **Step 2: Verify RED**

Run: `uv run pytest tests/integration/test_cli_workitem_truth_check.py::TestCliWorkitemTruthCheck::test_truth_check_ignores_unrelated_formal_branch_for_historical_work_item -q`

Expected: FAIL because the current implementation reports `branch_only_implemented` and includes WI220 paths.

- [x] **Step 3: Implement the minimum attribution guard**

```python
def _has_workitem_scoped_change(paths: tuple[str, ...], wi_rel: str) -> bool:
    work_item_id = Path(wi_rel).name
    scoped_prefixes = (f"{wi_rel}/", f".ai-sdlc/work-items/{work_item_id}/")
    return any(path.startswith(scoped_prefixes) for path in paths)
```

After computing the symmetric merge-base changed-path set, replace it with an empty tuple when it has no requested-WI-scoped change. Keep all existing classification and history logic unchanged.

- [x] **Step 4: Verify GREEN and focused regressions**

Run:

```text
uv run pytest tests/integration/test_cli_workitem_truth_check.py -q
uv run pytest tests/unit/test_program_service.py -k "truth_snapshot" -q
uv run ruff check src/ai_sdlc/core/workitem_truth.py tests/integration/test_cli_workitem_truth_check.py
uv run ai-sdlc verify constraints
```

Expected: all commands pass; the new regression fails if the attribution guard is removed.

- [x] **Step 5: Reproduce the real WI095/WI121 boundary**

Run both work items against `origin/main` and the defect branch HEAD. Until real D2 evidence exists, both revisions must remain `formal_freeze_only`; Program Truth must not become ready from the unrelated defect or WI220 Formal commit.

- [x] **Step 6: Commit the focused defect**

```text
git add docs/superpowers/plans/2026-08-28-program-truth-cross-wi-attribution-fix.md tests/integration/test_cli_workitem_truth_check.py src/ai_sdlc/core/workitem_truth.py
git commit -m "fix: bind workitem truth to scoped branch evidence"
```
