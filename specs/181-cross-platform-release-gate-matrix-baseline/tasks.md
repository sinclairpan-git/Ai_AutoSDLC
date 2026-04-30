---
related_doc:
  - "packaging/offline/RELEASE_CHECKLIST.md"
  - ".github/workflows/windows-offline-smoke.yml"
---
# Tasks: Cross-platform Release Gate Matrix Baseline

**Work item**: `181-cross-platform-release-gate-matrix-baseline`
**Source**: `spec.md` + `plan.md`

## Batch Strategy

```text
Batch 1: Formal baseline and TDD red test
Batch 2: POSIX workflow implementation
Batch 3: Release checklist alignment and focused verification
```

## Batch 1: Formal Baseline and TDD Red Test

### Task T11: Freeze formal work item docs

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: none
- **Files**: `spec.md`, `plan.md`, `tasks.md`, `task-execution-log.md`
- **Acceptance**:
  1. The work item defines the release-gate matrix problem and scope.
  2. The work item names Windows and POSIX evidence as separate release gates.

### Task T12: Add failing workflow contract test

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T11
- **Files**: `tests/integration/test_github_workflows.py`
- **Acceptance**:
  1. Test requires `.github/workflows/posix-offline-smoke.yml`.
  2. Test requires `macos-latest`, `ubuntu-latest`, `install_offline.sh`, `.venv/bin/ai-sdlc`, `adapter status`, `run --dry-run`, and artifact upload.
- **Verification**:
  - Red: `python -m pytest tests/integration/test_github_workflows.py -q` fails before the workflow exists.

## Batch 2: POSIX Workflow Implementation

### Task T21: Add POSIX offline smoke workflow

- **Priority**: P0
- **Status**: Complete
- **Dependencies**: T12
- **Files**: `.github/workflows/posix-offline-smoke.yml`
- **Acceptance**:
  1. Workflow runs on pull requests and manual dispatch.
  2. Workflow runs a matrix over `macos-latest` and `ubuntu-latest`.
  3. Workflow builds the offline bundle, installs it, verifies CLI help, adapter status, and `run --dry-run`.
  4. Workflow uploads per-platform evidence.
- **Verification**:
  - Green: `python -m pytest tests/integration/test_github_workflows.py -q` passes locally.
  - Target proof remains CI execution.

## Batch 3: Release Checklist Alignment and Verification

### Task T31: Update release checklist evidence contract

- **Priority**: P1
- **Status**: Complete
- **Dependencies**: T21
- **Files**: `packaging/offline/RELEASE_CHECKLIST.md`
- **Acceptance**:
  1. Checklist explicitly says both Windows and POSIX smoke evidence are required for cross-platform release claims.
  2. Checklist identifies `posix-offline-smoke-evidence` and its required log files.
  3. Checklist warns that Windows success does not prove macOS/Linux and POSIX success does not prove Windows.

### Task T32: Record verification and open gates

- **Priority**: P1
- **Status**: Complete
- **Dependencies**: T31
- **Files**: `task-execution-log.md`
- **Acceptance**:
  1. Local focused test result is recorded.
  2. Long-running local `run --dry-run` timeout and target-platform CI gates are recorded as open evidence requirements.
