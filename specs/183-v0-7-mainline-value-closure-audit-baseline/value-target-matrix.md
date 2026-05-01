# V0.7 Mainline Value Target Matrix

**Work item**: `183-v0-7-mainline-value-closure-audit-baseline`
**Created**: 2026-05-01
**Status legend**:

- `complete`: implementation, tests, current-main CI, and any release-package proof required by the claim are recorded.
- `substantially complete`: core implementation and tests exist, but one bounded proof or documentation reconciliation remains.
- `partial`: meaningful implementation exists, but the stated value is broader than the current proof.
- `not proven`: evidence is missing or not yet reviewed.

## Current Matrix

| Value target | Current status | Implementation files / artifacts audited | Tests audited | Current-main CI evidence | Release-package validation | Remaining gaps / risks | v0.7.x candidate | v0.8 candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VT-183-001 Frontend technology stack optimization | partial | `src/ai_sdlc/cli/program_cmd.py`; `src/ai_sdlc/core/program_service.py`; `src/ai_sdlc/core/managed_delivery_apply.py`; `src/ai_sdlc/models/frontend_solution_confirmation.py`; `src/ai_sdlc/models/frontend_provider_profile.py`; `providers/frontend/public-primevue/`; `providers/frontend/enterprise-vue2/`; `governance/frontend/`; `managed/frontend/`; specs 095, 099, 101, 145, 152, 153, 165-179 | `tests/unit/test_managed_delivery_apply.py`; frontend solution-confirm/provider/page-ui/generation/browser-gate tests to be enumerated in the final pass | Compatibility Gate run `25207598621` passed on `main` SHA `00745c74a5bbe1395f10056e130b4d7b46a30135`, but it proves repository tests, not full frontend E2E delivery | Current-main offline smoke runs `25209967716` and `25209967949` prove build/install/CLI smoke from freshly built offline bundles. Published v0.7.0 assets exist but were not revalidated after mainline fixes | Confirmed product direction: public provider is PrimeVue / Vue3 (`public-primevue`, `vue3-public-primevue`), not public Vue2. Enterprise provider remains Vue2. Full "all components" and real empty-project frontend browser closure still need explicit coverage evidence | Correct any public Vue2 wording to PrimeVue / Vue3; add component coverage manifest; prove empty-project managed frontend delivery from a v0.7.x release artifact | Broader provider expansion, full component coverage claims, richer runtime adapters |
| VT-183-002 Beginner-friendly CLI experience | partial | `src/ai_sdlc/cli/status_guidance.py`; `src/ai_sdlc/cli/doctor_cmd.py`; `src/ai_sdlc/cli/commands.py`; `src/ai_sdlc/core/managed_delivery_apply.py`; `packaging/offline/`; `README.md`; `USER_GUIDE.zh-CN.md` | CLI guidance, doctor/status, managed-delivery, install/offline smoke tests to be enumerated in the final pass | Compatibility Gate run `25207598621` passed; offline smoke runs `25209967716` and `25209967949` validate `install_offline`, `--help`, `adapter status`, and `run --dry-run` smoke | Current-main-built offline bundles smoke on Ubuntu, macOS, and Windows. Published v0.7.0 zip/tar.gz not yet revalidated after fixes | User flow still requires explicit commands; host Python/Node/package-manager/browser/private-registry conditions are diagnosed or delegated rather than universally auto-installed | Document the minimum beginner path and dependency boundaries; fix remaining Node 20 warnings in offline smoke workflows before 2026-06-02 | More automatic orchestration and richer beginner-mode UX |
| VT-183-003 Windows/macOS/Linux compatibility | substantially complete for current main; partial for published v0.7.0 artifacts | `.github/workflows/compatibility-gate.yml`; `.github/workflows/windows-offline-smoke.yml`; `.github/workflows/posix-offline-smoke.yml`; `src/ai_sdlc/core/managed_delivery_apply.py`; specs 179 and 181 | Cross-platform CLI/module tests; Windows package-manager resolution tests in `tests/unit/test_managed_delivery_apply.py`; offline smoke workflow tests | Compatibility Gate run `25207598621` passed on `main` SHA `00745c74a5bbe1395f10056e130b4d7b46a30135`: Ubuntu/macOS/Windows x Python 3.11/3.12 plus Windows `pwsh`/`cmd`; final check `Compatibility Gate Result` succeeded | Current-main offline smoke passed: POSIX run `25209967716` on Ubuntu/macOS; Windows run `25209967949`; both build offline bundles, install them, and run CLI smoke. v0.7.0 release assets remain unproven after later fixes | Current-main-built bundle proof is not the same as published v0.7.0 zip/tar.gz proof. Offline smoke workflows still warn on Node 20 through `actions/upload-artifact@v4` | Either publish and prove v0.7.x assets or explicitly mark v0.7.0 assets as superseded; fix offline smoke Node 20 warning | Broader OS/package-manager matrix and packaged installer hardening |
| VT-183-004 Shell entry selection and persistence | substantially complete | `src/ai_sdlc/cli/adapter_cmd.py`; `src/ai_sdlc/cli/commands.py`; `src/ai_sdlc/core/config.py`; `src/ai_sdlc/models/project.py`; `AGENTS.md`; spec 180 | `tests/unit/test_shell_preference.py`; init/adapter shell-select/status tests recorded in spec 180 | Compatibility Gate run `25207598621` passed repository tests on all matrix OS/Python combinations | Current-main offline smoke validates CLI startup paths, not the full interactive init shell selector | Needs final source/test enumeration only; no major product gap found | Mark complete after final evidence enumeration | Optional richer shell migration UX |
| VT-183-005 Other v0.7 optimizations | partial as a grouped target | Browser-gate baseline promotion, fail-closed behavior, delivery registry/runtime handoff, continuity handoff, action/check naming, status guidance, offline smoke workflows | Relevant focused tests across frontend, handoff, status, workflows | Compatibility Gate and offline smoke evidence exists for current main | Depends on each optimization's release claim | This bucket remains too broad to close as one value. Offline smoke Node 20 warning is a concrete 0.7.x hygiene issue | Split into concrete subtargets; fix offline smoke Node 20 warning | Move non-release-critical optimization backlog to v0.8 |

## Completion Criteria By Target

### VT-183-001 Frontend Technology Stack Optimization

Mark complete only when the audit records:

- implementation and tests for stack/provider/style selection;
- implementation and tests for managed component-library delivery;
- evidence for both enterprise Vue2 and public PrimeVue / Vue3 provider paths;
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
| Current `main` compatibility gate run | `gh run view 25207598621` | Collected: success on `00745c74a5bbe1395f10056e130b4d7b46a30135`. |
| POSIX offline smoke | `gh workflow run posix-offline-smoke.yml --ref main`; `gh run view 25209967716` | Collected: success on Ubuntu/macOS for current main-built bundle. |
| Windows offline smoke | `gh workflow run windows-offline-smoke.yml --ref main`; `gh run view 25209967949` | Collected: success on Windows for current main-built bundle. |
| v0.7 release artifacts | `gh release view v0.7.0 --json tagName,name,publishedAt,url,assets` | Collected artifact identities; still need to validate the published assets or supersede them with v0.7.x. |
| Frontend provider truth | Source review of `providers/frontend/`, `governance/frontend/`, and related tests | Resolved by owner decision: public path is PrimeVue / Vue3, not public Vue2. |
| Stale status reconciliation | Specs 179, 180, 181 plus defect docs | Decide docs correction versus code follow-up. |

## Recorded CI Evidence

| Evidence class | Run | SHA | Result | Notes |
| --- | --- | --- | --- | --- |
| Current-main compatibility gate | `https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/25207598621` | `00745c74a5bbe1395f10056e130b4d7b46a30135` | success | Ubuntu/macOS/Windows x Python 3.11/3.12; Windows `pwsh`/`cmd`; `Compatibility Gate Result` succeeded. |
| Current-main POSIX offline smoke | `https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/25209967716` | `00745c74a5bbe1395f10056e130b4d7b46a30135` | success | Builds offline bundle, installs it, runs CLI smoke on Ubuntu and macOS, uploads evidence. |
| Current-main Windows offline smoke | `https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/25209967949` | `00745c74a5bbe1395f10056e130b4d7b46a30135` | success | Builds Windows offline bundle, installs it, runs CLI smoke, uploads evidence. |

## Recorded Release Artifacts

| Release | Artifact | Digest | Status |
| --- | --- | --- | --- |
| `v0.7.0` | `ai-sdlc-offline-0.7.0.tar.gz` | `sha256:615f5813461062095db2d0e6b348b151461adfd5347f8154ac19a754deaa9499` | Published on 2026-04-24; not revalidated after current-main fixes. |
| `v0.7.0` | `ai-sdlc-offline-0.7.0.zip` | `sha256:5eff3ff3eff4cde2e4f15f7b39bf0db1fd28d6abc608963f11381ef22e3a5eb8` | Published on 2026-04-24; not revalidated after current-main fixes. |

## Current Recommendation

| Decision area | Recommendation |
| --- | --- |
| Overall v0.7 closure | Do not mark the entire v0.7 value set complete yet. Mark current-main compatibility and offline bundle smoke as proven, with published-asset proof still open. |
| Public component-library wording | Use PrimeVue / Vue3 wording. Do not describe the public path as public Vue2. |
| v0.7.x scope | Publish or validate a v0.7.x artifact from the current main fixes; prove empty-project frontend managed delivery on Windows/macOS/Linux; fix offline smoke Node 20 warning; reconcile specs 179/181 and release docs. |
| v0.8 scope | Full provider expansion, "all components" coverage beyond the current governed mappings, richer runtime adapters, and more automatic beginner orchestration. |
