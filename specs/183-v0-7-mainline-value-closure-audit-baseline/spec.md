# Feature Spec: V0.7 Mainline Value Closure Audit Baseline

**Work item**: `183-v0-7-mainline-value-closure-audit-baseline`
**Created**: 2026-05-01
**Status**: Audit baseline recorded; stale-doc reconciliation remains open
**Input**: Create a v0.7 mainline value closure audit that maps each stated value target to implementation files, tests, CI evidence, release-package validation, and remaining gaps so maintainers can decide what is complete, what belongs in v0.7.x, and what moves to v0.8.
**References**: `docs/releases/v0.7.0.md`, `README.md`, `USER_GUIDE.zh-CN.md`, `specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/`, `specs/180-shell-preference-persistence-and-migration-baseline/`, `specs/181-cross-platform-release-gate-matrix-baseline/`, `.github/workflows/compatibility-gate.yml`

## Problem

The v0.7 series has accumulated multiple mainline capabilities: frontend solution confirmation, managed frontend delivery, bilingual CLI guidance, cross-platform command hardening, shell preference persistence, and GitHub Actions compatibility proof. These capabilities are valuable, but the current truth surface mixes implemented code, release notes, internal follow-up specs, defect archives, and CI evidence.

Without a dedicated closure audit, maintainers can accidentally overclaim that the entire v0.7 value set is complete when only a subset has machine-verifiable evidence. The project needs a structured audit task that separates:

- implemented and tested framework capability;
- current-main GitHub Actions compatibility proof;
- release-package and offline E2E proof;
- external-environment dependencies such as private registries, host runtimes, and browser installation;
- explicit follow-up ownership for v0.7.x or v0.8.

## Scope

### In Scope

- Create a canonical v0.7 value-target audit matrix under this work item.
- Map each user-facing v0.7 value target to implementation files, tests, CI results, release-package validation, and remaining gaps.
- Classify each value target as `complete`, `substantially complete`, `partial`, or `not proven`.
- Identify which remaining gaps are suitable for v0.7.x maintenance versus v0.8 scope.
- Reconcile conflicting or stale evidence from v0.7 release docs, defect docs, and follow-up specs.
- Define the minimum evidence required before any target can be marked complete.

### Out of Scope

- Do not implement missing v0.7 functionality in this audit baseline.
- Do not modify GitHub repository settings.
- Do not merge PRs or push to `main`.
- Do not rewrite release claims without a reviewed follow-up change.
- Do not include local training-material work; that content remains separate and should not be part of mainline closure evidence.

## Value Targets Under Audit

### VT-183-001: Frontend Technology Stack Optimization

Audit the v0.7 target covering existing frontend stack/component-library recognition, requirement-time frontend stack recommendation, user selection of component library and style, managed download/application of enterprise Vue2 and public component-library providers, and component coverage/adaptation claims.

### VT-183-002: Beginner-Friendly CLI Experience

Audit bilingual key-step messaging, reduced command burden, next-command guidance, automatic framework dependency preparation where supported, and explicit handoff when a user must run a command manually.

### VT-183-003: Windows / macOS / Linux Compatibility

Audit command, test, and workflow compatibility across Windows, macOS, and Linux, including Python 3.11/3.12, Windows shell smoke coverage, package-manager command resolution, and release/offline smoke evidence.

### VT-183-004: Shell Entry Selection and Persistence

Audit init-time shell selection, persisted shell preference, adapter guidance materialization, migration behavior for existing projects, and later command guidance that follows the selected shell.

### VT-183-005: Other v0.7 Optimization Points

Audit supporting improvements such as browser-gate baseline promotion, fail-closed behavior, delivery registry/runtime handoff, managed delivery evidence, action/check naming, and continuity or status guidance that affects v0.7 release readiness.

## Requirements

- **FR-183-001**: The work item must include a `value-target-matrix.md` file.
- **FR-183-002**: The matrix must include one row per value target with columns for implementation files, tests, CI evidence, release-package validation, status, v0.7.x follow-up, and v0.8 follow-up.
- **FR-183-003**: The matrix must distinguish current-main CI success from release-package/offline E2E proof.
- **FR-183-004**: The audit must explicitly identify any overclaim risk, stale documentation, or evidence conflict.
- **FR-183-005**: The audit must exclude local training-material branches and files from mainline value proof.
- **FR-183-006**: The audit must define completion criteria for marking each value target complete.
- **FR-183-007**: The audit must record exact commands, GitHub Actions run links or IDs, and release artifact identifiers used as evidence.
- **FR-183-008**: The audit must produce a recommendation table assigning incomplete items to v0.7.x or v0.8.

## Success Criteria

- **SC-183-001**: Maintainers can read `value-target-matrix.md` and see which v0.7 targets are complete, partial, or not proven.
- **SC-183-002**: Every target links to concrete implementation files and tests or explicitly says evidence is missing.
- **SC-183-003**: Current-main compatibility proof is separated from release-package proof.
- **SC-183-004**: Any stale status in v0.7 follow-up specs is called out for reconciliation instead of silently ignored.
- **SC-183-005**: The audit gives an actionable next decision for each unresolved gap: v0.7.x, v0.8, or documentation correction.

---
related_doc:
  - "docs/releases/v0.7.0.md"
  - "README.md"
  - "USER_GUIDE.zh-CN.md"
  - "specs/179-v0-7-0-windows-offline-e2e-remediation-baseline/"
  - "specs/180-shell-preference-persistence-and-migration-baseline/"
  - "specs/181-cross-platform-release-gate-matrix-baseline/"
  - ".github/workflows/compatibility-gate.yml"
frontend_evidence_class: "framework_capability"
---
