# 003 Runtime Contract Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the remaining `003` reviewer and backend delegation contracts into real runtime behavior, then tighten the verification surfaces so false-green coverage is no longer possible.

**Architecture:** Add two thin coordination layers instead of scattering fixes across the codebase. `reviewer_gate.py` will own checkpoint-specific approval requirements for state transitions and close gates, while `routing.py` will own backend selection for spec/plan/tasks generation. Verification will then be tightened to require those runtime integration points, not just contract tokens.

**Tech Stack:** Python 3.11, Typer CLI, Pydantic v2, pytest, Rich, Markdown/YAML work-item artifacts

---

### Task 1: Add Checkpoint-Specific Reviewer Artifact Persistence

**Files:**
- Modify: `src/ai_sdlc/core/p1_artifacts.py`
- Modify: `src/ai_sdlc/cli/commands.py`
- Test: `tests/unit/test_p1_artifacts.py`
- Test: `tests/integration/test_cli_workitem_link.py`

- [ ] **Step 1: Write the failing persistence tests**

Add tests for:
- saving reviewer decisions separately for `prd_freeze`, `docs_baseline_freeze`, and `pre_close`
- loading a decision for a specific checkpoint
- status still showing the latest reviewer decision across multiple checkpoint files
- compatibility fallback when only the legacy single-file reviewer artifact exists

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_p1_artifacts.py tests/integration/test_cli_workitem_link.py -k "reviewer or checkpoint" -q`
Expected: FAIL because reviewer persistence currently supports only a single artifact file and status does not aggregate per-checkpoint artifacts.

- [ ] **Step 3: Implement checkpoint-specific persistence**

Implement:
- checkpoint-specific save/load helpers for reviewer decisions
- compatibility read path for the legacy artifact
- latest-decision aggregation for the status surface

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_p1_artifacts.py tests/integration/test_cli_workitem_link.py -k "reviewer or checkpoint" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/p1_artifacts.py src/ai_sdlc/cli/commands.py tests/unit/test_p1_artifacts.py tests/integration/test_cli_workitem_link.py
git commit -m "feat: persist reviewer decisions per checkpoint"
```

### Task 2: Enforce Reviewer Gates On Runtime State Transitions

**Files:**
- Create: `src/ai_sdlc/core/reviewer_gate.py`
- Modify: `src/ai_sdlc/core/state_machine.py`
- Test: `tests/unit/test_state_machine.py`
- Test: `tests/flow/test_new_requirement_flow.py`

- [ ] **Step 1: Write the failing reviewer gate tests**

Add tests for:
- blocking `GOVERNANCE_FROZEN` when `prd_freeze=approve` is missing
- blocking `DOCS_BASELINE` when `docs_baseline_freeze=approve` is missing
- blocking `DEV_REVIEWED` when `pre_close=approve` is missing
- denying transitions when the reviewer decision is `revise` or `block`
- allowing transitions only when the required checkpoint decision is `approve`

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_state_machine.py tests/flow/test_new_requirement_flow.py -k "reviewer or freeze or baseline or pre_close" -q`
Expected: FAIL because state transitions currently validate only status edges and never consume reviewer artifacts.

- [ ] **Step 3: Implement reviewer gate coordination**

Implement:
- checkpoint-to-target-state mapping
- structured gate results with `allow / deny_missing / deny_revise / deny_block`
- state-machine integration before persistence of gated transitions

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_state_machine.py tests/flow/test_new_requirement_flow.py -k "reviewer or freeze or baseline or pre_close" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/reviewer_gate.py src/ai_sdlc/core/state_machine.py tests/unit/test_state_machine.py tests/flow/test_new_requirement_flow.py
git commit -m "feat: enforce reviewer gates on state transitions"
```

### Task 3: Make Close-Check Consume Formal Reviewer Approval

**Files:**
- Modify: `src/ai_sdlc/core/close_check.py`
- Test: `tests/unit/test_close_check.py`
- Test: `tests/integration/test_cli_workitem_close_check.py`

- [ ] **Step 1: Write the failing close-check tests**

Add tests for:
- `003` close-check blocking when `pre_close` reviewer approval is missing
- `003` close-check blocking when `pre_close` is `revise`
- `003` close-check blocking when `pre_close` is `block`
- `003` close-check passing when `pre_close=approve` exists

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "pre_close or reviewer_gate" -q`
Expected: FAIL because close-check currently treats review evidence as free-form log text instead of a formal reviewer decision gate.

- [ ] **Step 3: Implement formal reviewer gate consumption**

Implement:
- `003`-specific reviewer approval check in close-check
- reuse of reviewer-gate helper instead of duplicating checkpoint semantics
- clear blocker messaging including checkpoint, reason, and next action

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py -k "pre_close or reviewer_gate" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/close_check.py tests/unit/test_close_check.py tests/integration/test_cli_workitem_close_check.py
git commit -m "feat: require formal reviewer approval for 003 closeout"
```

### Task 4: Route Spec/Plan/Tasks Generation Through Backend Selection

**Files:**
- Create: `src/ai_sdlc/backends/routing.py`
- Modify: `src/ai_sdlc/backends/native.py`
- Modify: generation entry path discovered during implementation (`src/ai_sdlc/studios/router.py` and/or the shared generation caller)
- Test: `tests/unit/test_backends.py`
- Test: `tests/unit/test_studios.py`
- Test: `tests/flow/test_new_requirement_flow.py`

- [ ] **Step 1: Write the failing backend routing tests**

Add tests for:
- spec generation routing through `select_backend()`
- plan generation routing through `select_backend()`
- tasks generation routing through `select_backend()`
- plugin delegation when capability coverage is complete
- native fallback when plugin is missing or incomplete
- hard block when plugin failure is unsafe to fallback from

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_backends.py tests/unit/test_studios.py tests/flow/test_new_requirement_flow.py -k "backend or routing or generate_spec or generate_plan or generate_tasks" -q`
Expected: FAIL because backend routing logic currently exists only in the registry and is not called by the real generation path.

- [ ] **Step 3: Implement runtime generation routing**

Implement:
- a coordinator that maps generation action -> required capability
- typed runtime error for blocked backend decisions
- integration of the coordinator into the actual spec/plan/tasks generation caller
- surfaced `BackendSelectionDecision` so later gates and logs can consume it

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_backends.py tests/unit/test_studios.py tests/flow/test_new_requirement_flow.py -k "backend or routing or generate_spec or generate_plan or generate_tasks" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/backends/routing.py src/ai_sdlc/backends/native.py src/ai_sdlc/studios/router.py tests/unit/test_backends.py tests/unit/test_studios.py tests/flow/test_new_requirement_flow.py
git commit -m "feat: route generation through backend selection"
```

### Task 5: Tighten Verification So Runtime Integration Is Required

**Files:**
- Modify: `src/ai_sdlc/core/verify_constraints.py`
- Modify: `src/ai_sdlc/cli/verify_cmd.py`
- Test: `tests/unit/test_verify_constraints.py`
- Test: `tests/integration/test_cli_verify_constraints.py`

- [ ] **Step 1: Write the failing verification tests**

Add tests for:
- reviewer tokens present but no runtime gate integration
- backend registry tokens present but no runtime generation caller integration
- `003` passing only when runtime integration points exist in addition to contract tokens

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "003 and runtime" -q`
Expected: FAIL because verify-constraints currently checks only file presence and token existence for the `003` feature-contract surfaces.

- [ ] **Step 3: Implement runtime-aware verification**

Implement:
- feature-contract checks that require the reviewer runtime gate helper
- feature-contract checks that require backend routing integration for generation actions
- clear blocker messages distinguishing “surface exists” from “runtime path integrated”

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py -k "003 and runtime" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ai_sdlc/core/verify_constraints.py src/ai_sdlc/cli/verify_cmd.py tests/unit/test_verify_constraints.py tests/integration/test_cli_verify_constraints.py
git commit -m "feat: require runtime integration for 003 contracts"
```

### Task 6: Final Traceability And Repository Verification

**Files:**
- Modify: `specs/003-cross-cutting-authoring-and-extension-contracts/task-execution-log.md`
- Modify: `specs/003-cross-cutting-authoring-and-extension-contracts/tasks.md`
- Modify: `docs/framework-defect-backlog.zh-CN.md`

- [ ] **Step 1: Update 003 execution evidence and task truth**

Document:
- reviewer gate remediation implementation evidence
- backend runtime routing implementation evidence
- verification tightening evidence

- [ ] **Step 2: Run the full verification suite**

Run:
- `uv run pytest -q`
- `uv run ruff check src tests`
- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc workitem close-check --wi specs/003-cross-cutting-authoring-and-extension-contracts --all-docs`

Expected:
- full pytest passes
- lint passes
- `verify constraints` returns no BLOCKERs
- `close-check` stays PASS with formal reviewer gate and runtime backend routing in place

- [ ] **Step 3: Commit**

```bash
git add specs/003-cross-cutting-authoring-and-extension-contracts/task-execution-log.md specs/003-cross-cutting-authoring-and-extension-contracts/tasks.md docs/framework-defect-backlog.zh-CN.md
git commit -m "docs: record 003 runtime contract remediation"
```
