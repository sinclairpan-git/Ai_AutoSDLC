# Task Execution Log: V0.7 Mainline Value Closure Audit Baseline

**Work item**: `183-v0-7-mainline-value-closure-audit-baseline`
**Created**: 2026-05-01
**Status**: In progress

## Rules

- Record exact commands and results.
- Treat current-main CI, release-package smoke, and external private-provider evidence as separate proof classes.
- Do not include local training-material branches or files as mainline evidence.
- Do not mark a value target complete without implementation, tests, CI or release evidence as required by its claim.

## Batch 2026-05-01-001 | T11-T12

### Scope

- Materialized the v0.7 mainline value closure audit work item.
- Created the initial value-target matrix covering all five stated v0.7 value targets.
- Captured known evidence and known gaps from prior mainline assessment without treating them as final audit closure.

### Commands

- `python -m ai_sdlc run --dry-run`
- `git fetch origin`
- `git ls-tree -d --name-only origin/main specs/ | sort | tail -20`
- `git worktree add -b codex/v0.7-value-closure-audit-task /private/tmp/Ai_AutoSDLC-v07-audit origin/main`

### Observed Results

- `python -m ai_sdlc run --dry-run`: `Stage close: PASS`; `Pipeline completed. Stage: close`.
- `origin/main`: `00745c74a5bbe1395f10056e130b4d7b46a30135`.
- Latest numbered work item on `origin/main`: `182-continuity-handoff-runtime-baseline`.
- Created this work item as `183-v0-7-mainline-value-closure-audit-baseline`.
- The active user workspace is on a training-material branch with unrelated dirty files; this audit was created in a clean `origin/main` worktree to avoid mixing training content into mainline evidence.

### Open Evidence Gates

- Batch 1 only creates the audit task and initial matrix. It does not complete the full audit.
- CI run IDs and release-asset proof still need to be recorded during Batch 3.
- Stale or conflicting v0.7 docs still need reconciliation during Batch 4.

## Batch 2026-05-01-002 | T21-T42

### Scope

- Recorded owner decision that the public component-library path is PrimeVue / Vue3, not public Vue2.
- Collected current-main GitHub Actions evidence for compatibility and offline smoke.
- Triggered missing current-main offline smoke workflows for POSIX and Windows.
- Updated the value matrix with the current conclusion, v0.7.x gaps, and v0.8 candidates.

### Commands

- `python -m ai_sdlc run --dry-run`
- `gh run list --workflow compatibility-gate.yml --branch main --limit 5`
- `gh run view 25207598621 --json databaseId,displayTitle,conclusion,status,headSha,url,createdAt,updatedAt,workflowName,event,jobs`
- `gh workflow run posix-offline-smoke.yml --ref main`
- `gh workflow run windows-offline-smoke.yml --ref main`
- `gh run watch 25209967716 --exit-status`
- `gh run watch 25209967949 --exit-status`
- `gh run view 25209967716 --json databaseId,displayTitle,conclusion,status,headSha,url,createdAt,updatedAt,workflowName,event,jobs`
- `gh run view 25209967949 --json databaseId,displayTitle,conclusion,status,headSha,url,createdAt,updatedAt,workflowName,event,jobs`
- `gh release view v0.7.0 --json tagName,name,publishedAt,url,assets`
- `rg -n "public-primevue|enterprise-vue2|frontend_stack|provider_id|PrimeVue|shell-select|preferred_shell|npm\\.cmd|_resolve_host_command|Compatibility Gate Result" ...`

### Observed Results

- `python -m ai_sdlc run --dry-run`: command executed and reported the existing close gate as `RETRY` with `reason: Final tests did not pass`; adapter ingress remains `materialized (unverified)`. The command also refreshed `.cursor/rules/ai-sdlc.mdc`, which was restored because it was not part of this audit.
- Compatibility Gate run `25207598621`: success on `main` SHA `00745c74a5bbe1395f10056e130b4d7b46a30135`.
  - Ubuntu, macOS, and Windows matrix passed for Python 3.11 and 3.12.
  - Windows shell smoke passed for `pwsh` and `cmd`.
  - Final job `Compatibility Gate Result` succeeded.
- POSIX Offline Smoke run `25209967716`: success on `main` SHA `00745c74a5bbe1395f10056e130b4d7b46a30135`.
  - `smoke (ubuntu-latest)`: success.
  - `smoke (macos-latest)`: success.
  - Built offline bundle, installed it, ran CLI smoke, and uploaded evidence.
- Windows Offline Smoke run `25209967949`: success on `main` SHA `00745c74a5bbe1395f10056e130b4d7b46a30135`.
  - Built Windows offline bundle, installed it, ran CLI smoke, and uploaded evidence.
- Offline smoke workflows still emit a Node 20 deprecation warning from `actions/upload-artifact@v4`; this is a v0.7.x hygiene gap before 2026-06-02.
- v0.7.0 release artifacts found:
  - `ai-sdlc-offline-0.7.0.tar.gz`, digest `sha256:615f5813461062095db2d0e6b348b151461adfd5347f8154ac19a754deaa9499`.
  - `ai-sdlc-offline-0.7.0.zip`, digest `sha256:5eff3ff3eff4cde2e4f15f7b39bf0db1fd28d6abc608963f11381ef22e3a5eb8`.

### Current Conclusion

- Current `main` has passed baseline compatibility and current-main-built offline bundle smoke across Windows, macOS, and Linux.
- The full v0.7 value set should not be marked complete yet because published v0.7.0 artifacts have not been revalidated after later fixes, and full empty-project frontend managed delivery/browser closure still needs release-asset proof.
- Public provider wording is resolved: use PrimeVue / Vue3, not public Vue2.

### Open Evidence Gates

- Published v0.7.0 zip/tar.gz artifacts need validation or supersession by a v0.7.x release.
- Empty-project frontend managed delivery from release artifacts needs OS-matrix proof.
- Component coverage needs a manifest before claiming "all components" are adapted.
- Specs 179/181 and v0.7 release/defect docs need reconciliation.
