# Branch Lifecycle Truth Guard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn branch/worktree lifecycle into an auditable framework surface so stale scratch branches and worktrees cannot silently drift away from `main` after a work item is otherwise treated as complete.

**Architecture:** Keep the solution read-only by default. Add a single branch inventory helper on top of `GitClient`, classify local branches/worktrees into lifecycle kinds, compute divergence against `main`, and feed that inventory into three bounded consumers: `verify constraints`, `workitem close-check` / `branch-check`, and `status --json` / `doctor`. Tighten rules and execution-log close-out markers so related branches must be explicitly disposed as `merged`, `archived`, or `deleted`, without auto-deleting or auto-merging anything.

**Tech Stack:** Python 3.11, Typer CLI, pytest, Rich, Markdown rules/docs, Git CLI

---

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Behavior |
| --- | --- | --- |
| branch inventory | list branches/worktrees, classify lifecycle kind, compute divergence/read-only facts | must not auto-delete branches or mutate refs |
| verification surfaces | surface unresolved branch lifecycle gaps to `verify constraints` | must not silently downgrade blocker-worthy active WI gaps |
| close surfaces | enforce work-item branch disposition and branch-vs-main truth at close time | must not infer “merged” from chat or plan text |
| readiness surfaces | expose bounded branch inventory summaries in `status --json` / `doctor` | must not trigger fetch/prune/rebuild side effects |
| rules/docs | freeze lifecycle kinds, disposition semantics, and close-out wording | must not leave “delete merged branches (optional)” as the only closure path |

## Planned File Structure

- `src/ai_sdlc/branch/git_client.py`: add read-only branch/worktree listing and divergence helpers.
- `src/ai_sdlc/core/branch_inventory.py`: normalize Git facts into lifecycle-aware inventory objects.
- `src/ai_sdlc/core/verify_constraints.py`: add branch lifecycle governance surface and stable warning/blocker text.
- `src/ai_sdlc/core/close_check.py`: require explicit branch disposition truth for work-item-bound branches before close passes.
- `src/ai_sdlc/core/workitem_traceability.py`: share work-item-to-branch association checks with close surfaces.
- `src/ai_sdlc/cli/workitem_cmd.py`: add a read-only `branch-check` entry point or equivalent work-item-scoped branch inventory surface.
- `src/ai_sdlc/telemetry/readiness.py`: expose bounded branch inventory summaries for `status --json` / `doctor`.
- `src/ai_sdlc/cli/commands.py`: wire `status --json` branch summary if needed.
- `src/ai_sdlc/cli/doctor_cmd.py`: render branch lifecycle readiness findings without side effects.
- `src/ai_sdlc/rules/git-branch.md`: freeze branch/worktree lifecycle kinds and disposition semantics.
- `src/ai_sdlc/rules/pipeline.md`: require branch disposition truth before close.
- `docs/框架自迭代开发与发布约定.md`: document “分支已实现 ≠ 主线已兑现” and the required close-out sequence.
- `templates/execution-log-template.md`: add branch close-out markers for latest-batch disposition truth.
- `src/ai_sdlc/templates/execution-log.md.j2`: keep generator output aligned with the new markers.
- `docs/USER_GUIDE.zh-CN.md`: document `branch-check` and bounded branch inventory reading.
- `tests/unit/test_git_client.py`: branch/worktree read helper coverage.
- `tests/unit/test_branch_inventory.py`: lifecycle kind classification, divergence, and disposition logic.
- `tests/unit/test_verify_constraints.py`: branch lifecycle governance surface.
- `tests/unit/test_close_check.py`: close blockers for unresolved work-item branches.
- `tests/integration/test_cli_verify_constraints.py`: verify output for branch lifecycle gaps.
- `tests/integration/test_cli_workitem_close_check.py`: work-item close behavior with unresolved branches.
- `tests/integration/test_cli_status.py`: bounded `status --json` branch inventory summary.
- `tests/integration/test_cli_doctor.py`: doctor output for branch lifecycle readiness.

## Decision Log

- `DL-001`: Branch inventory remains read-only. Phase 1 does not auto-merge, auto-delete, auto-prune, or auto-archive any branch/worktree.
- `DL-002`: `scratch` branches/worktrees are allowed, but only as temporary execution containers. They must not remain unclassified or undisposed at close-out.
- `DL-003`: Historical unrelated branches may surface as warnings in repo-wide read surfaces; only branches/worktrees associated with the active work item may block close.
- `DL-004`: `archived` is a real disposition distinct from `merged`; archived branches may remain intentionally unmerged, but that fact must be explicit and auditable.

## Guardrails

- Do not redefine branch truth in chat prose. The only acceptable lifecycle outputs are Git facts plus explicit disposition markers in work-item close-out surfaces.
- Do not collapse `unsupported` or “not associated” into “safe to ignore”; unrelated old branches may warn, but active WI branches require explicit treatment.
- Do not put branch lifecycle under execute blocker by default. The blocking surface is close-out truth, not ordinary step execution.
- Do not add hidden flags or environment toggles that promote branch inventory warnings into silent destructive cleanup.

### Task 1: Add Read-Only Branch Inventory Primitives

**Files:**
- Create: `src/ai_sdlc/core/branch_inventory.py`
- Modify: `src/ai_sdlc/branch/git_client.py`
- Test: `tests/unit/test_git_client.py`
- Test: `tests/unit/test_branch_inventory.py`

- [ ] **Step 1: Write the failing inventory tests**

Cover:
- local branch enumeration with upstream/worktree binding
- worktree enumeration with path and checked-out branch
- divergence counts against `main`
- lifecycle kind classification for `design/*`, `feature/*`, `codex/*`, backup/archive, and unmanaged names
- stable machine-readable inventory ordering

- [ ] **Step 2: Run the focused inventory tests and confirm they fail**

Run: `uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py -q`
Expected: FAIL because branch inventory helpers and lifecycle classification do not exist yet.

- [ ] **Step 3: Implement the minimal read-only inventory layer**

Implement:
- read-only git helpers for branch/worktree listing and divergence
- lifecycle-aware inventory objects
- stable ordering so downstream read surfaces can snapshot the output

- [ ] **Step 4: Re-run the focused inventory tests**

Run: `uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/branch/git_client.py src/ai_sdlc/core/branch_inventory.py tests/unit/test_git_client.py tests/unit/test_branch_inventory.py
git commit -m "feat: add branch lifecycle inventory primitives"
```

### Task 2: Add Work-Item Branch Disposition Truth To Close Surfaces

**Files:**
- Modify: `src/ai_sdlc/core/close_check.py`
- Modify: `src/ai_sdlc/core/workitem_traceability.py`
- Modify: `src/ai_sdlc/cli/workitem_cmd.py`
- Modify: `templates/execution-log-template.md`
- Modify: `src/ai_sdlc/templates/execution-log.md.j2`
- Test: `tests/unit/test_close_check.py`
- Test: `tests/integration/test_cli_workitem_close_check.py`

- [ ] **Step 1: Write the failing close-surface tests**

Cover:
- a work item whose related scratch branch still has unique commits beyond `main`
- a work item whose old worktree still exists without explicit disposition
- `merged / archived / deleted` disposition markers in the latest batch close-out block
- unrelated historical branches only warning, not blocking
- stable read-only `workitem branch-check` output

- [ ] **Step 2: Run the close-surface tests and confirm they fail**

Run: `uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "branch or disposition" -q`
Expected: FAIL because close-check does not currently reason about work-item-bound branches or branch disposition markers.

- [ ] **Step 3: Implement branch disposition truth**

Implement:
- work-item-to-branch association logic
- latest-batch disposition marker parsing
- close blockers for unresolved active-WI branches/worktrees
- a read-only `branch-check` surface under `workitem`

- [ ] **Step 4: Re-run the close-surface tests**

Run: `uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "branch or disposition" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/close_check.py src/ai_sdlc/core/workitem_traceability.py src/ai_sdlc/cli/workitem_cmd.py templates/execution-log-template.md src/ai_sdlc/templates/execution-log.md.j2 tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py
git commit -m "feat: enforce branch lifecycle closeout truth"
```

### Task 3: Extend Verify Constraints With Branch Lifecycle Governance

**Files:**
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing verification tests**

Cover:
- active work item with unresolved scratch/worktree branch
- missing branch disposition marker in latest close-out evidence
- archived-but-explicit branch surfacing as non-blocking
- stable machine-readable failure classes for branch lifecycle gaps

- [ ] **Step 2: Run the verification tests and confirm they fail**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "branch_lifecycle or disposition" -q`
Expected: FAIL because verify constraints has no branch lifecycle governance surface yet.

- [ ] **Step 3: Implement the verification surface**

Implement:
- branch lifecycle governance object registration
- blocker/warning text for active-WI unresolved branches
- JSON-safe structured output for downstream inspection and telemetry

- [ ] **Step 4: Re-run the verification tests**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "branch_lifecycle or disposition" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/verify_constraints.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: verify branch lifecycle governance"
```

### Task 4: Add Bounded Branch Inventory To Status And Doctor

**Files:**
- Modify: `src/ai_sdlc/telemetry/readiness.py`
- Modify: `src/ai_sdlc/cli/commands.py`
- Modify: `src/ai_sdlc/cli/doctor_cmd.py`
- Test: `tests/integration/test_cli_status.py`
- Test: `tests/integration/test_cli_doctor.py`

- [ ] **Step 1: Write the failing read-surface tests**

Cover:
- `status --json` branch inventory summary
- `doctor` branch lifecycle readiness rows
- bounded output size and stable field order
- no implicit fetch/prune/write side effects

- [ ] **Step 2: Run the read-surface tests and confirm they fail**

Run: `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -k "branch or lifecycle" -q`
Expected: FAIL because status/doctor do not currently expose branch lifecycle readiness.

- [ ] **Step 3: Implement bounded branch read surfaces**

Implement:
- branch inventory summary in `status --json`
- doctor findings for stale active-WI branch/worktree state
- strict read-only behavior with no implicit repository mutation

- [ ] **Step 4: Re-run the read-surface tests**

Run: `uv run pytest tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -k "branch or lifecycle" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/telemetry/readiness.py src/ai_sdlc/cli/commands.py src/ai_sdlc/cli/doctor_cmd.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py
git commit -m "feat: surface branch lifecycle readiness"
```

### Task 5: Tighten Rules, Docs, And Command Discovery

**Files:**
- Modify: `src/ai_sdlc/rules/git-branch.md`
- Modify: `src/ai_sdlc/rules/pipeline.md`
- Modify: `docs/框架自迭代开发与发布约定.md`
- Modify: `docs/USER_GUIDE.zh-CN.md`

- [ ] **Step 1: Write the failing doc/rule assertions**

Cover:
- `git-branch.md` defining lifecycle kinds and disposition semantics
- `pipeline.md` requiring branch disposition truth before close
- self-iteration docs distinguishing “分支已实现” from “主线已兑现”
- user guide documenting read-only branch inventory commands

- [ ] **Step 2: Run the targeted checks and confirm they fail**

Run:
- `uv run pytest tests/unit/test_verify_constraints.py -k "doc_first or branch_lifecycle" -q`
- `uv run ai-sdlc verify constraints`

Expected:
- targeted tests FAIL before rule/doc strings exist
- `verify constraints` stays green or gives a missing-surface signal until docs are aligned

- [ ] **Step 3: Update rules and docs**

Implement:
- branch/worktree lifecycle types and disposition policy in `git-branch.md`
- close-stage policy linkage in `pipeline.md`
- self-iteration branch close-out sequence
- user-facing command discovery and semantics

- [ ] **Step 4: Re-run the targeted checks**

Run:
- `uv run pytest tests/unit/test_verify_constraints.py -k "doc_first or branch_lifecycle" -q`
- `uv run ai-sdlc verify constraints`

Expected:
- targeted tests PASS
- `verify constraints` returns no branch-lifecycle governance blockers on the clean baseline

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/rules/git-branch.md src/ai_sdlc/rules/pipeline.md docs/框架自迭代开发与发布约定.md docs/USER_GUIDE.zh-CN.md
git commit -m "docs: define branch lifecycle closeout policy"
```

### Task 6: Run Final Regression And Freeze The New Close-Out Path

**Files:**
- Verify only: repository root plus updated docs/tests above

- [ ] **Step 1: Run the focused branch lifecycle suite**

Run:
- `uv run pytest tests/unit/test_git_client.py tests/unit/test_branch_inventory.py tests/unit/test_verify_constraints.py tests/unit/test_close_check.py tests/integration/test_cli_verify_constraints.py tests/integration/test_cli_workitem_close_check.py tests/integration/test_cli_status.py tests/integration/test_cli_doctor.py -q`

Expected:
- all focused branch lifecycle tests PASS

- [ ] **Step 2: Run full repo verification**

Run:
- `uv run pytest -q`
- `uv run ruff check src tests`
- `uv run ai-sdlc verify constraints`

Expected:
- all tests PASS
- lint PASS
- `verify constraints` returns no BLOCKERs on the clean baseline

- [ ] **Step 3: Smoke the new read-only commands**

Run:
- `uv run ai-sdlc workitem branch-check --wi specs/001-ai-sdlc-framework`
- `uv run ai-sdlc status --json`
- `uv run ai-sdlc doctor`

Expected:
- `branch-check` reports branch disposition truth for the target work item
- `status --json` and `doctor` expose bounded branch lifecycle summaries
- docs, integration tests, and command discovery all use the same command set

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "test: freeze branch lifecycle closeout guardrails"
```
