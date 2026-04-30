---
related_doc:
  - "packaging/offline/RELEASE_CHECKLIST.md"
  - ".github/workflows/windows-offline-smoke.yml"
---
# Implementation Plan: Cross-platform Release Gate Matrix Baseline

**Work item**: `181-cross-platform-release-gate-matrix-baseline`
**Spec**: `specs/181-cross-platform-release-gate-matrix-baseline/spec.md`
**Date**: 2026-04-30

## Goal

Make cross-platform release claims depend on target-platform smoke evidence from both Windows and POSIX runners.

## Architecture

The design keeps installer logic unchanged and strengthens the release gate layer. GitHub Actions workflows provide target-platform evidence; regression tests prevent the workflow contracts from silently weakening; the release checklist defines what evidence is required before release notes can claim support.

## Technical Background

- **Language**: Python 3.11 for framework and tests.
- **CI**: GitHub Actions.
- **Windows entrypoint**: `install_offline.ps1` / `.venv\Scripts\ai-sdlc.exe`.
- **POSIX entrypoint**: `install_offline.sh` / `.venv/bin/ai-sdlc`.
- **Packaging**: `packaging/offline/build_offline_bundle.sh`.
- **Evidence**: uploaded workflow artifacts.

## Constitution Alignment

| Gate | Plan response |
| --- | --- |
| Critical path must be verifiable | Add workflow-level evidence for both target families. |
| No false activation or release claims | Checklist separates archive generation from installation proof. |
| Prefer durable, inspectable artifacts | Upload logs and manifests for release audit. |
| Keep scope narrow | No installer rewrite or shell transpiler in this work item. |

## File Structure

```text
.github/workflows/
  windows-offline-smoke.yml
  posix-offline-smoke.yml
packaging/offline/
  RELEASE_CHECKLIST.md
tests/integration/
  test_github_workflows.py
specs/181-cross-platform-release-gate-matrix-baseline/
  spec.md
  plan.md
  tasks.md
  task-execution-log.md
```

## Phases

### Phase 0: Formal Baseline

Freeze `spec.md`, `plan.md`, `tasks.md`, and `task-execution-log.md` so the work item has a clear release-gate contract.

### Phase 1: TDD Workflow Contract

Add failing regression tests that require a POSIX smoke workflow and matrix evidence. Run only the focused workflow tests to avoid long local gates.

### Phase 2: POSIX Workflow

Add `.github/workflows/posix-offline-smoke.yml` with a matrix over `macos-latest` and `ubuntu-latest`. Build the offline bundle, install it, run CLI smoke commands, and upload evidence.

### Phase 3: Release Checklist Alignment

Update `packaging/offline/RELEASE_CHECKLIST.md` to say cross-platform release claims require both Windows and POSIX smoke evidence.

### Phase 4: Focused Verification

Run `python -m pytest tests/integration/test_github_workflows.py -q`. Record that target-platform workflow execution remains a CI gate, not a local proof.

## Verification Strategy

| Path | Primary verification | Boundary |
| --- | --- | --- |
| Workflow contract | `python -m pytest tests/integration/test_github_workflows.py -q` | Static contract only. |
| Windows install proof | `windows-offline-smoke.yml` artifact | Must run on `windows-latest`. |
| macOS/Linux install proof | `posix-offline-smoke.yml` artifact | Must run on `macos-latest` and `ubuntu-latest`. |
| Release wording | Checklist review + test assertions | Prevents overclaiming. |

## Risks

- Local Windows pytest and `run --dry-run` may be slow or blocked by temp-directory permissions; these cannot be treated as release evidence.
- macOS runner availability and runtime cost may make the workflow slower than Ubuntu-only checks.
- `build_offline_bundle.sh` depends on POSIX shell tooling and must remain a POSIX-only entrypoint.

## Rollback

- Remove `.github/workflows/posix-offline-smoke.yml`.
- Revert the checklist wording and workflow regression test additions.
- Keep existing Windows workflow unchanged.
