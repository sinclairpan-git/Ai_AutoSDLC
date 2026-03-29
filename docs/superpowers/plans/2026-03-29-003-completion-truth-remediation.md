# 003 Completion Truth Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the framework guardrails that falsely marked `003` as closable, then complete the still-missing `003` authoring / reviewer / backend / release-gate contracts with fresh evidence.

**Architecture:** Split the remediation into two layers. First, strengthen repo-wide completion truth by teaching `close-check` and `verify constraints` to reason about planned-batch coverage and feature-contract surfaces. Then implement the missing `003` product contracts in focused slices: PRD draft authoring, reviewer checkpoints, backend delegation/fallback, and measurable release-gate evidence.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic v2, pytest, Rich, Markdown governance docs

---

### Task 1: Add Planned-Batch Completion Truth To Close-Check

**Files:**
- Create: `src/ai_sdlc/core/workitem_traceability.py`
- Modify: `src/ai_sdlc/core/close_check.py`
- Test: `tests/unit/test_close_check.py`
- Test: `tests/integration/test_cli_workitem_close_check.py`

- [ ] **Step 1: Write the failing close-check tests**

Add tests for:
- a work item with multiple planned batches but execution evidence only for the latest batch
- a `tasks.md` file without unchecked checkboxes but with a reopened status note
- a work item whose spec/tasks declare FR clusters that are missing execution coverage

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "traceability or batch or completion_truth" -q`
Expected: FAIL because close-check currently only validates checkboxes, execution-log fields, verification profile, and git closure.

- [ ] **Step 3: Implement the minimal completion-truth parser**

Implement:
- planned batch/task extraction from `tasks.md`
- execution batch coverage extraction from `task-execution-log.md`
- reopened-status / missing-evidence detection
- close-check blockers for partial implementation masquerading as full completion

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "traceability or batch or completion_truth" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/workitem_traceability.py src/ai_sdlc/core/close_check.py tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py
git commit -m "feat: block partial workitem closeout"
```

### Task 2: Extend Verify Constraints With Feature-Contract Coverage

**Files:**
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `src/ai_sdlc/cli/verify_cmd.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing verification tests**

Add tests for:
- an active `003` work item that lacks `draft_prd/final_prd` surfaces
- missing reviewer decision surface
- missing backend delegation/fallback surface
- missing release-gate evidence surface

- [ ] **Step 2: Run the focused verification tests to verify they fail**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "feature_contract or 003" -q`
Expected: FAIL because verification gate objects do not currently include work-item feature-contract coverage.

- [ ] **Step 3: Implement feature-contract coverage objects**

Implement:
- a minimal registry of feature-contract surfaces for the active work item
- coverage checks for `003` authoring / reviewer / backend / release-gate contracts
- human-readable BLOCKER messages in both CLI text and JSON output

- [ ] **Step 4: Run the focused verification tests to verify they pass**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "feature_contract or 003" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/verify_cmd.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: verify feature contract coverage"
```

### Task 3: Implement 003 PRD Draft Authoring And Reviewer Contracts

**Files:**
- Modify: `src/ai_sdlc/models/work.py`
- Modify: `src/ai_sdlc/studios/prd_studio.py`
- Modify: `src/ai_sdlc/core/close_check.py`
- Test: `tests/unit/test_prd_studio.py`
- Test: `tests/unit/test_close_check.py`

- [ ] **Step 1: Write the failing authoring and reviewer tests**

Add tests for:
- one-line idea input generating a draft PRD with explicit unresolved placeholders
- distinct `draft_prd` vs `final_prd` states
- reviewer decision artifacts with `approve` / `revise` / `block`, timestamp, reason, target, and next action

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_prd_studio.py tests/unit/test_close_check.py -k "draft_prd or reviewer" -q`
Expected: FAIL because the current PRD studio only performs readiness review and the work models do not expose reviewer contracts.

- [ ] **Step 3: Implement the minimal authoring and reviewer surfaces**

Implement:
- new `003` work models for draft/final PRD and reviewer decisions
- one-line idea -> draft PRD generation path with explicit placeholders
- compatibility boundary so existing readiness review still works
- close-check consumption of reviewer decision surfaces

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_prd_studio.py tests/unit/test_close_check.py -k "draft_prd or reviewer" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/models/work.py src/ai_sdlc/studios/prd_studio.py src/ai_sdlc/core/close_check.py tests/unit/test_prd_studio.py tests/unit/test_close_check.py
git commit -m "feat: add 003 prd authoring and reviewer contracts"
```

### Task 4: Implement 003 Backend Delegation And Fallback Contracts

**Files:**
- Modify: `src/ai_sdlc/backends/native.py`
- Create: `src/ai_sdlc/backends/routing.py`
- Test: `tests/unit/test_backends.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing backend tests**

Add tests for:
- capability declaration enumeration
- native vs plugin selection reason recording
- explicit fallback when coverage is missing
- explicit BLOCK when plugin failure is unsafe to fall back from

- [ ] **Step 2: Run the focused backend tests to verify they fail**

Run: `uv run pytest tests/unit/test_backends.py -q`
Expected: FAIL because the current backend layer only provides a basic registry and default native backend.

- [ ] **Step 3: Implement the minimal routing and fallback layer**

Implement:
- capability declarations
- backend choice records
- safe-fallback vs hard-block outcomes
- compatibility with the existing native default path

- [ ] **Step 4: Run the focused backend tests to verify they pass**

Run: `uv run pytest tests/unit/test_backends.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/backends/native.py src/ai_sdlc/backends/routing.py tests/unit/test_backends.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: add backend delegation contracts"
```

### Task 5: Implement 003 Release-Gate Evidence And Final Traceability

**Files:**
- Modify: `src/ai_sdlc/core/close_check.py`
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `src/ai_sdlc/cli/verify_cmd.py`
- Modify: `specs/003-cross-cutting-authoring-and-extension-contracts/tasks.md`
- Modify: `specs/003-cross-cutting-authoring-and-extension-contracts/task-execution-log.md`
- Test: `tests/unit/test_close_check.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing release-gate tests**

Add tests for:
- PASS / WARN / BLOCK release verdict structure
- evidence source requirement for each blocker
- `003` staying blocked until Tasks `1.1 ~ 5.2` have real execution evidence

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_close_check.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "release_gate or pass_warn_block or 003" -q`
Expected: FAIL because the current repo does not expose explicit `003` release-gate evidence objects.

- [ ] **Step 3: Implement release-gate evidence surfaces and update 003 execution truth**

Implement:
- explicit PASS / WARN / BLOCK verdict objects
- evidence-source reporting for blockers
- `003` task/execution-log updates only after real implementation batches land

- [ ] **Step 4: Run the full repository verification**

Run:
- `uv run pytest -q`
- `uv run ruff check src tests`
- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc workitem close-check --wi specs/003-cross-cutting-authoring-and-extension-contracts --all-docs`

Expected:
- all tests pass
- lint passes
- `verify constraints` returns no BLOCKERs
- `close-check` for `003` only passes once Batch `1 ~ 5` are truly implemented and evidenced

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/close_check.py src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/verify_cmd.py specs/003-cross-cutting-authoring-and-extension-contracts/tasks.md specs/003-cross-cutting-authoring-and-extension-contracts/task-execution-log.md tests/unit/test_close_check.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: close 003 completion-truth gaps"
```
