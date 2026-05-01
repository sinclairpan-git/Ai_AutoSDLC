---
related_doc:
  - "docs/releases/v0.7.0.md"
  - "README.md"
  - "USER_GUIDE.zh-CN.md"
  - "specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/"
  - "specs/180-shell-preference-persistence-and-migration-baseline/"
  - "specs/181-cross-platform-release-gate-matrix-baseline/"
  - ".github/workflows/compatibility-gate.yml"
---
# Tasks: V0.7 Mainline Value Closure Audit Baseline

**Work item**: `183-v0-7-mainline-value-closure-audit-baseline`
**Source**: `spec.md` + `plan.md`

## Batch Strategy

```text
Batch 1: Materialize audit task and initial value matrix
Batch 2: Source implementation/test evidence pass
Batch 3: CI and release-package evidence pass
Batch 4: Gap assignment and closeout recommendation
```

## Batch 1: Materialize Audit Task and Initial Value Matrix

### Task T11: Freeze formal audit docs

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: none
- **Files**: `spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **Acceptance**:
  1. The work item states that the audit is evidence classification, not feature implementation.
  2. The scope excludes training-material branches and files.
  3. The audit defines the five v0.7 value targets under review.

### Task T12: Create initial value-target matrix

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T11
- **Files**: `value-target-matrix.md`
- **Acceptance**:
  1. The matrix has one row for each v0.7 value target.
  2. Each row includes implementation files, tests, CI evidence, release-package validation, status, v0.7.x follow-up, and v0.8 follow-up.
  3. The initial matrix records known evidence and known gaps without claiming final closure.

## Batch 2: Source Implementation/Test Evidence Pass

### Task T21: Audit frontend technology-stack and provider evidence

- **Priority**: P0
- **Status**: Pending
- **Dependencies**: T12
- **Files**: `value-target-matrix.md`
- **Acceptance**:
  1. Map solution-confirm, provider selection, component library profiles, style packs, managed delivery, and browser-gate integration to source files.
  2. Map tests that prove the behavior.
  3. Identify any public Vue2 versus public PrimeVue/Vue3 wording mismatch.
  4. Assign missing provider/runtime/component-completeness work to v0.7.x, v0.8, or documentation correction.

### Task T22: Audit beginner-friendly CLI evidence

- **Priority**: P0
- **Status**: Pending
- **Dependencies**: T12
- **Files**: `value-target-matrix.md`
- **Acceptance**:
  1. Map bilingual messages, next-step guidance, doctor/status hints, and automated dependency installation paths.
  2. Identify host-runtime, private-registry, and browser-runtime boundaries.
  3. Decide whether remaining simplification belongs in v0.7.x or v0.8.

### Task T23: Audit shell preference persistence evidence

- **Priority**: P1
- **Status**: Pending
- **Dependencies**: T12
- **Files**: `value-target-matrix.md`
- **Acceptance**:
  1. Map init-time selection, adapter shell-select, persisted config, AGENTS materialization, and tests.
  2. Confirm whether this value target can be marked complete.

## Batch 3: CI and Release-Package Evidence Pass

### Task T31: Record current-main GitHub Actions evidence

- **Priority**: P0
- **Status**: Pending
- **Dependencies**: T12
- **Files**: `value-target-matrix.md`, `task-execution-log.md`
- **Acceptance**:
  1. Record current `main` SHA.
  2. Record compatibility-gate run ID/URL and conclusion.
  3. Record any POSIX/Windows offline smoke runs and conclusions.
  4. Keep current-main CI proof separate from release-package proof.

### Task T32: Verify release-package smoke evidence

- **Priority**: P0
- **Status**: Pending
- **Dependencies**: T31
- **Files**: `value-target-matrix.md`, `task-execution-log.md`
- **Acceptance**:
  1. Identify published v0.7 release artifacts under audit.
  2. Record Windows, macOS, and Linux install/run commands from the release package.
  3. Mark missing or failed release-package evidence explicitly.
  4. Assign any missing packaged-user-path proof to v0.7.x.

## Batch 4: Gap Assignment and Closeout Recommendation

### Task T41: Reconcile stale or conflicting status documents

- **Priority**: P1
- **Status**: Pending
- **Dependencies**: T21, T22, T23, T31, T32
- **Files**: `value-target-matrix.md`, `task-execution-log.md`
- **Acceptance**:
  1. Compare release notes, user guide, defect docs, and specs 179/180/181.
  2. Record where implementation has advanced beyond stale docs.
  3. Record where docs overclaim beyond evidence.

### Task T42: Produce final completion recommendation

- **Priority**: P0
- **Status**: Pending
- **Dependencies**: T41
- **Files**: `value-target-matrix.md`, `development-summary.md`
- **Acceptance**:
  1. Every value target has a final status.
  2. Every unresolved gap has a destination: v0.7.x, v0.8, or docs correction.
  3. The summary states whether v0.7 can be called fully closed.
