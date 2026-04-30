# Feature Spec: Cross-platform Release Gate Matrix Baseline

**Work item**: `181-cross-platform-release-gate-matrix-baseline`
**Created**: 2026-04-30
**Status**: Draft
**Input**: Design and implement bidirectional release gates so macOS development must prove Windows compatibility and Windows development must prove macOS/POSIX compatibility before AI-SDLC framework releases.
**References**: `packaging/offline/RELEASE_CHECKLIST.md`, `.github/workflows/windows-offline-smoke.yml`

## Problem

AI-SDLC already has Windows offline smoke coverage, but the release contract is still asymmetric. A release prepared mostly on macOS can accidentally treat `.zip` creation as Windows proof, while a release prepared mostly on Windows can accidentally treat PowerShell/CMD success as POSIX proof. Both are unsafe.

Cross-platform compatibility must be proven by target-platform evidence, not by developer workstation assumptions. The framework needs a release-gate matrix that makes the evidence boundary explicit:

- macOS/Linux development must still prove Windows install and CLI smoke.
- Windows development must still prove macOS/POSIX install and CLI smoke.
- Shell syntax, path separators, executable locations, archive formats, and bundled Python runtime layout must be validated on the target platform.

## Scope

### In Scope

- Add a POSIX offline smoke workflow that runs on macOS and Linux runners.
- Require the POSIX smoke workflow to build the POSIX offline bundle, install it with `install_offline.sh`, and collect evidence.
- Keep the existing Windows offline smoke workflow as the Windows target proof.
- Update release checklist wording so Windows and POSIX evidence are both mandatory before cross-platform release claims.
- Add regression tests that assert both workflows exist and cover build, install, CLI, adapter status, `run --dry-run`, encoding/runtime evidence, and artifact upload.

### Out of Scope

- No shell command transpiler.
- No installer rewrite beyond evidence-gate alignment.
- No claim that local Windows or macOS development alone proves the other platform.
- No deletion of existing Windows smoke behavior.

## User Stories

### US-181-001: macOS developer proves Windows compatibility

As a maintainer developing on macOS or Linux, I need a Windows target smoke gate so I cannot publish a release that only worked on POSIX.

**Acceptance**:

1. Given a release PR, when Windows-relevant files change, then `windows-offline-smoke.yml` runs on `windows-latest`.
2. Given the Windows smoke completes, then it uploads `windows-offline-smoke-evidence` with install, help, adapter status, dry-run, and manifest logs.

### US-181-002: Windows developer proves macOS/POSIX compatibility

As a maintainer developing on Windows, I need a macOS/POSIX target smoke gate so I cannot publish a release that only worked in PowerShell/CMD.

**Acceptance**:

1. Given a release PR, when offline packaging or source files change, then `posix-offline-smoke.yml` runs on `macos-latest` and `ubuntu-latest`.
2. Given the POSIX smoke completes, then it uploads per-platform evidence with install, help, adapter status, dry-run, and manifest logs.

### US-181-003: Release notes do not overclaim platform support

As a release owner, I need the checklist to distinguish generated archives from verified target-platform installation evidence.

**Acceptance**:

1. `.zip` creation is not accepted as Windows proof.
2. `.tar.gz` creation is not accepted as macOS/Linux proof.
3. Cross-platform release claims require both Windows and POSIX smoke evidence.

## Requirements

- **FR-181-001**: The repository must include a POSIX offline smoke GitHub Actions workflow.
- **FR-181-002**: The POSIX workflow must run on `macos-latest` and `ubuntu-latest`.
- **FR-181-003**: The POSIX workflow must build the offline bundle with `packaging/offline/build_offline_bundle.sh`.
- **FR-181-004**: The POSIX workflow must install using `install_offline.sh`, not PowerShell or CMD.
- **FR-181-005**: The POSIX workflow must verify `.venv/bin/ai-sdlc`.
- **FR-181-006**: The POSIX workflow must execute `ai-sdlc --help`, `ai-sdlc adapter status`, and `ai-sdlc run --dry-run`.
- **FR-181-007**: The POSIX workflow must upload evidence containing `install.log`, `help.txt`, `adapter-status.txt`, `run-dry-run.txt`, and `bundle-manifest.json`.
- **FR-181-008**: Regression tests must assert the Windows and POSIX workflow contracts.
- **FR-181-009**: The offline release checklist must state that Windows and POSIX smoke evidence are separate mandatory release gates for cross-platform claims.
- **FR-181-010**: Documentation must prefer Python/pathlib-style cross-platform checks for logic, leaving shell scripts as platform entrypoints.

## Key Entities

- **Release Gate Matrix**: The required target-platform proof set for a release.
- **Windows Smoke Evidence**: Artifact produced by `windows-offline-smoke.yml`.
- **POSIX Smoke Evidence**: Artifact produced by `posix-offline-smoke.yml`.
- **Platform Claim**: Any release statement that says a package works on Windows, macOS, Linux, or zero-preinstalled-Python targets.

## Success Criteria

- **SC-181-001**: `tests/integration/test_github_workflows.py` fails before the POSIX workflow exists and passes after it is added.
- **SC-181-002**: The repository contains both Windows and POSIX offline smoke workflows.
- **SC-181-003**: The POSIX workflow explicitly covers macOS and Linux runners.
- **SC-181-004**: The release checklist states that both smoke workflows are required before cross-platform release claims.
- **SC-181-005**: Local verification records any unavailable long-running or target-platform checks as open release gates instead of claiming success.

---
related_doc:
  - "packaging/offline/RELEASE_CHECKLIST.md"
  - ".github/workflows/windows-offline-smoke.yml"
frontend_evidence_class: "framework_capability"
---
