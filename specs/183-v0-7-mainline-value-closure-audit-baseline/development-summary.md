# Development Summary: V0.7 Mainline Value Closure Audit Baseline

## Current Conclusion

The v0.7 mainline value set is not fully closed.

Current `main` has strong evidence for baseline compatibility:

- Compatibility Gate passed on Ubuntu, macOS, and Windows across Python 3.11 and 3.12.
- Windows `pwsh` and `cmd` doctor smoke passed.
- Current-main-built offline bundles passed smoke on Ubuntu, macOS, and Windows.

This proves the current repository revision is broadly compatible across the supported OS matrix. It does not prove that the already published v0.7.0 zip/tar.gz artifacts include all later fixes or that the complete empty-project frontend delivery path is closed from those published artifacts.

## Decisions Recorded

- The public component provider is PrimeVue / Vue3 (`public-primevue`, `vue3-public-primevue`).
- The enterprise provider remains Vue2 (`enterprise-vue2`).
- Any wording that describes the public provider as public Vue2 should be corrected.
- Training-material branches and files are excluded from this audit and from mainline release proof.

## Evidence Recorded

- Compatibility Gate: `https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/25207598621`
- POSIX Offline Smoke: `https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/25209967716`
- Windows Offline Smoke: `https://github.com/sinclairpan-git/Ai_AutoSDLC/actions/runs/25209967949`
- Current `main` SHA: `00745c74a5bbe1395f10056e130b4d7b46a30135`
- v0.7.0 artifacts:
  - `ai-sdlc-offline-0.7.0.tar.gz`
  - `ai-sdlc-offline-0.7.0.zip`

## Remaining v0.7.x Gaps

- Validate or supersede the published v0.7.0 offline artifacts after the current-main fixes.
- Prove the empty-project frontend managed delivery path from a release artifact on Windows, macOS, and Linux.
- Add or publish a component coverage manifest before claiming "all components" are adapted.
- Fix Node 20 deprecation warnings in offline smoke workflows before 2026-06-02.
- Reconcile stale status in specs 179/181 and v0.7 release/defect docs.
- Document the minimum beginner path and clearly separate auto-installed dependencies from diagnosed external prerequisites.

## v0.8 Candidates

- Broader provider expansion beyond enterprise Vue2 and public PrimeVue.
- Richer runtime adapters and target-project adapter automation.
- More complete beginner-mode orchestration.
- Larger "all components" coverage beyond the current governed mappings.
