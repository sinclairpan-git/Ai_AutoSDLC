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
# Implementation Plan: V0.7 Mainline Value Closure Audit Baseline

**Work item**: `183-v0-7-mainline-value-closure-audit-baseline`
**Spec**: `specs/183-v0-7-mainline-value-closure-audit-baseline/spec.md`
**Date**: 2026-05-01

## Goal

Create a machine-auditable, maintainer-readable closure task for the v0.7 series. The task should make it clear which value targets are already proven on `main`, which are only partially implemented, and which require v0.7.x or v0.8 follow-up.

## Audit Method

Use a five-column evidence chain for each value target:

1. Implementation files or generated artifacts.
2. Focused tests or regression tests.
3. Current-main CI evidence.
4. Release-package or offline E2E evidence.
5. Remaining gaps and release assignment.

The audit must not treat any one evidence source as sufficient for full closure. Passing unit tests prove behavior only at the tested boundary; current-main CI proves repository compatibility for that revision; release-package smoke proves packaged distribution behavior; private registry or browser-runtime paths remain externally conditioned unless validated with real credentials and runtime assets.

## File Structure

```text
specs/183-v0-7-mainline-value-closure-audit-baseline/
  spec.md
  plan.md
  tasks.md
  task-execution-log.md
  value-target-matrix.md
```

## Phases

### Phase 0: Formal Task Materialization

Create the work item docs and initial matrix. Preserve the current assessment that v0.7 has substantial mainline capability but is not fully closed until the matrix is verified.

### Phase 1: Source Evidence Pass

Read the core implementation, tests, workflow files, release notes, user guide, and follow-up specs. Record concrete file paths and the exact claims they support.

Primary sources:

- frontend solution and managed delivery commands;
- component provider profiles and runtime adapters;
- bilingual guidance and status/doctor surfaces;
- shell preference persistence;
- cross-platform workflows;
- Windows package-manager resolution and offline smoke docs;
- release notes and defect archives.

### Phase 2: CI Evidence Pass

Record GitHub Actions run IDs/URLs for current `main`, especially the compatibility gate and any POSIX/Windows offline smoke workflows. Separate successful repository checks from release-asset checks.

### Phase 3: Release-Package Evidence Pass

Verify or mark missing the release-package smoke evidence for Windows, macOS, and Linux. Include artifact names, checksums or release IDs when available, and commands used to install/run from the published asset.

### Phase 4: Gap Assignment

Classify every remaining item:

- `v0.7.x`: needed to make the existing v0.7 promise truthful and complete.
- `v0.8`: a larger capability expansion or provider/runtime scope beyond the current release contract.
- `docs`: wording must be corrected because implementation intentionally does not cover the claim.

### Phase 5: Closeout

Update `task-execution-log.md` with exact commands, evidence links, and the final status of each target. Do not close this work item until every target has a decision.

## Verification Strategy

| Path | Primary verification | Boundary |
| --- | --- | --- |
| Matrix completeness | Review `value-target-matrix.md` against the five declared value targets | Proves audit coverage, not feature behavior. |
| Source mapping | `rg` and direct file reads for implementation/test references | Proves files exist and claims are grounded. |
| Current-main CI | `gh run view` / `gh pr checks` evidence | Proves GitHub-hosted checks for a revision only. |
| Release-package proof | Install/run from release artifacts on target OSes | Required before claiming packaged user path closure. |
| Documentation reconciliation | Compare README/user guide/release notes/defect docs | Identifies overclaim and stale-status risk. |

## Risks

- A capability may be implemented but not release-proven; the audit must mark that as incomplete evidence, not incomplete code.
- Some provider and private registry claims depend on external credentials or package availability.
- Local training-material files may appear in dirty worktrees; they are explicitly excluded from this audit.
- Existing follow-up specs may be stale after later code changes; the audit should reconcile status instead of trusting one document blindly.

## Rollback

Remove `specs/183-v0-7-mainline-value-closure-audit-baseline/` if the audit task is superseded by a different planning artifact.
