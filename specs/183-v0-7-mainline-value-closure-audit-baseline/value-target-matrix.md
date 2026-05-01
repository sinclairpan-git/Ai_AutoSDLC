# V0.7 Mainline Value Target Matrix

**Work item**: `183-v0-7-mainline-value-closure-audit-baseline`
**Created**: 2026-05-01
**Status legend**:

- `complete`: implementation, tests, current-main CI, and any release-package proof required by the claim are recorded.
- `substantially complete`: core implementation and tests exist, but one bounded proof or documentation reconciliation remains.
- `partial`: meaningful implementation exists, but the stated value is broader than the current proof.
- `not proven`: evidence is missing or not yet reviewed.

## Initial Matrix

| Value target | Initial status | Implementation files / artifacts to audit | Tests to audit | Current-main CI evidence | Release-package validation | Remaining gaps / risks | v0.7.x candidate | v0.8 candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VT-183-001 Frontend technology stack optimization | partial | `src/ai_sdlc/cli/program_cmd.py`; `src/ai_sdlc/core/program_service.py`; `src/ai_sdlc/core/managed_delivery_apply.py`; `governance/frontend/`; `providers/frontend/`; `managed/frontend/`; specs 095, 099, 101, 145, 152, 153, 165-178 | frontend solution-confirm, managed-delivery, provider/runtime, browser-gate, and generation-governance tests | Need exact workflow/run evidence; current compatibility gate proves repository tests, not full provider E2E | Need packaged empty-project frontend flow from release artifacts on Windows/macOS/Linux | Public provider appears to be `public-primevue` rather than a public Vue2 library; provider expansion/runtime adapter docs say some paths remain follow-up; enterprise private registry paths depend on external credentials/packages | Reconcile public Vue2 wording, prove release-package empty-project managed delivery, update stale docs | Broader provider expansion, full component coverage claims, richer runtime adapters |
| VT-183-002 Beginner-friendly CLI experience | partial | `src/ai_sdlc/cli/status_guidance.py`; `src/ai_sdlc/cli/doctor_cmd.py`; `src/ai_sdlc/cli/commands.py`; `src/ai_sdlc/core/managed_delivery_apply.py`; install/offline scripts; `README.md`; `USER_GUIDE.zh-CN.md` | CLI guidance, doctor/status, managed-delivery, install/offline smoke tests | Need exact workflow/run evidence for CLI paths | Need release-package first-run/user-path smoke evidence | Framework still requires several explicit commands; host Python/Node/package-manager/browser/private-registry conditions are not always auto-installed | Verify and document minimum command path; improve next-command guidance where gaps remain | More automatic orchestration and richer beginner-mode UX |
| VT-183-003 Windows/macOS/Linux compatibility | substantially complete for current-main CI; partial for release-package proof | `.github/workflows/compatibility-gate.yml`; `.github/workflows/cross-platform-core.yml`; `.github/workflows/windows-offline-smoke.yml`; `.github/workflows/posix-offline-smoke.yml`; `src/ai_sdlc/core/managed_delivery_apply.py`; specs 179 and 181 | cross-platform CLI/module tests; Windows package-manager resolution tests; smoke tests | Current `main` compatibility gate is known to pass for `00745c74a5bbe1395f10056e130b4d7b46a30135`; exact run ID/URL must be recorded in Batch 3 | Release/offline asset proof must be verified per OS and per release artifact | Current-main CI does not by itself prove published offline package behavior; spec 179 status appears stale relative to later code | Record Actions run IDs and release artifact smoke; reconcile spec 179 status | Broader OS/package-manager matrix and packaged installer hardening |
| VT-183-004 Shell entry selection and persistence | substantially complete | `src/ai_sdlc/cli/adapter_cmd.py`; `src/ai_sdlc/cli/commands.py`; `src/ai_sdlc/core/config.py`; `AGENTS.md`; spec 180 | `tests/unit/test_shell_preference.py` and CLI init/adapter shell tests | Need exact current-main run evidence showing these tests pass | Release-package init-path validation still useful but may not be required for core closure | Need confirm all later command guidance consistently follows selected shell | Likely mark complete after source/test/CI evidence is recorded | Optional richer shell migration UX |
| VT-183-005 Other v0.7 optimizations | not proven as a grouped target | Browser-gate baseline promotion, fail-closed behavior, delivery registry/runtime handoff, continuity handoff, action/check naming, status guidance | Relevant focused tests across frontend, handoff, status, workflows | Need exact workflow/run evidence | Depends on each optimization's release claim | This bucket is broad; must be decomposed or it will stay unverifiable | Split into concrete subtargets and close individually | Move non-release-critical optimization backlog to v0.8 |

## Completion Criteria By Target

### VT-183-001 Frontend Technology Stack Optimization

Mark complete only when the audit records:

- implementation and tests for stack/provider/style selection;
- implementation and tests for managed component-library delivery;
- evidence for both enterprise Vue2 and public provider paths, with exact wording corrected if the public path is not Vue2;
- release-package empty-project frontend flow on Windows, macOS, and Linux or an explicit decision that packaged proof is out of the v0.7 contract.

### VT-183-002 Beginner-Friendly CLI Experience

Mark complete only when the audit records:

- bilingual key-step messages and next-command guidance;
- the shortest supported beginner command path;
- what dependencies are auto-installed versus only diagnosed;
- release-package first-run evidence or a scoped documentation correction.

### VT-183-003 Windows / macOS / Linux Compatibility

Mark complete only when the audit records:

- current-main compatibility gate run ID/URL and conclusion;
- Windows `pwsh` and `cmd` doctor smoke evidence;
- Python 3.11 and 3.12 matrix evidence;
- release-package or offline smoke evidence for Windows, macOS, and Linux if the claim is about downloaded framework behavior.

### VT-183-004 Shell Entry Selection and Persistence

Mark complete only when the audit records:

- init-time shell selection;
- standalone shell selection or migration path;
- persisted configuration and materialized AGENTS guidance;
- tests and current-main CI evidence.

### VT-183-005 Other v0.7 Optimization Points

Mark complete only after decomposing the bucket into named subtargets with their own evidence chains. Until then, the group remains an umbrella backlog rather than a closable release value.

## Evidence To Collect Next

| Evidence item | Command or source | Owner decision needed |
| --- | --- | --- |
| Current `main` compatibility gate run | `gh run list --workflow compatibility-gate.yml --branch main --limit 5` and `gh run view <id>` | Record exact URL and conclusion. |
| POSIX offline smoke | `gh run list --workflow posix-offline-smoke.yml --branch main --limit 5` | Decide whether current evidence is release-blocking. |
| Windows offline smoke | `gh run list --workflow windows-offline-smoke.yml --branch main --limit 5` | Decide whether current evidence is release-blocking. |
| v0.7 release artifacts | `gh release view v0.7.0 --json tagName,assets` | Identify exact artifacts under packaged-user-path audit. |
| Frontend provider truth | Source review of `providers/frontend/`, `governance/frontend/`, and related tests | Correct public Vue2 wording if unsupported. |
| Stale status reconciliation | Specs 179, 180, 181 plus defect docs | Decide docs correction versus code follow-up. |
