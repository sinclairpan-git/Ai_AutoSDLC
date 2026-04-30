---
related_doc:
  - ".ai-sdlc/state/resume-pack.yaml"
  - ".ai-sdlc/state/checkpoint.yml"
  - "AGENTS.md"
---
# Tasks: Continuity Handoff Runtime Baseline

**Work item**: `182-continuity-handoff-runtime-baseline`
**Source**: `spec.md` + `plan.md`

## Batch Strategy

```text
Batch 1: Formal baseline and core TDD
Batch 2: CLI handoff surface
Batch 3: Status/recover visibility and AGENTS protocol
Batch 4: Verification and execution-log closeout
```

## Batch 1: Formal Baseline and Core TDD

### Task T11: Freeze formal work item docs

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: none
- **Files**: `spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **Acceptance**:
  1. The work item defines the continuity handoff problem and scope.
  2. The work item explicitly distinguishes handoff readiness from SDLC/release readiness.

### Task T12: Add failing core handoff tests

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T11
- **Files**: `tests/unit/test_handoff.py`
- **Acceptance**:
  1. Tests require canonical and work-item-scoped handoff writes.
  2. Tests require resume-pack `context_summary` refresh.
  3. Tests require freshness classification.
- **Verification**:
  - Red: focused test fails before `ai_sdlc.core.handoff` exists.

### Task T13: Implement core handoff service

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T12
- **Files**: `src/ai_sdlc/core/handoff.py`
- **Acceptance**:
  1. Service renders concise Markdown handoff content.
  2. Service writes canonical and scoped copies.
  3. Service reads missing/stale/ready state without unbounded Git calls.
  4. Service updates resume-pack context summary when possible.

## Batch 2: CLI Handoff Surface

### Task T21: Add failing CLI handoff tests

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T13
- **Files**: `tests/integration/test_cli_handoff.py`
- **Acceptance**:
  1. Tests require `handoff update` to write the handoff.
  2. Tests require `handoff show` to print it.
  3. Tests require `handoff check` to report ready/missing/stale.

### Task T22: Implement `ai-sdlc handoff`

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T21
- **Files**: `src/ai_sdlc/cli/handoff_cmd.py`, `src/ai_sdlc/cli/main.py`
- **Acceptance**:
  1. CLI exposes `update`, `show`, and `check`.
  2. `update` accepts explicit `--goal`, `--state`, `--decision`, `--command`, `--blocker`, and `--next-step` options.
  3. Missing handoff produces a clear failure for `show` and an action item for `check`.

## Batch 3: Status/Recover Visibility and AGENTS Protocol

### Task T31: Surface handoff state in status/recover

- **Priority**: P1
- **Status**: Complete
- **Dependencies**: T22
- **Files**: `src/ai_sdlc/cli/commands.py`, `tests/integration/test_cli_status.py`
- **Acceptance**:
  1. `status` shows handoff state and path.
  2. `recover` shows handoff state and path.
  3. The surface is lightweight and does not rebuild full program truth.

### Task T32: Add AGENTS Continuity Protocol

- **Priority**: P1
- **Status**: Complete
- **Dependencies**: T22
- **Files**: `AGENTS.md`
- **Acceptance**:
  1. AGENTS.md names `.ai-sdlc/state/codex-handoff.md`.
  2. AGENTS.md lists event-triggered update rules.
  3. AGENTS.md tells future sessions to read the handoff before continuing interrupted work.

## Batch 4: Verification and Execution Log

### Task T41: Run focused verification

- **Priority**: P1
- **Status**: Complete
- **Dependencies**: T31, T32
- **Files**: touched tests and implementation files
- **Acceptance**:
  1. Focused handoff tests pass.
  2. Focused status tests pass.
  3. Ruff passes for touched Python files.
  4. `python -m ai_sdlc run --dry-run` returns within the bounded local timeout.

### Task T42: Record execution evidence and open gates

- **Priority**: P1
- **Status**: Complete
- **Dependencies**: T41
- **Files**: `task-execution-log.md`
- **Acceptance**:
  1. Execution log records red/green verification.
  2. Execution log records any still-open close/release/governance gates.
