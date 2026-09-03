# Continuity Handoff

- Updated: 2026-09-03T10:16:08+00:00
- Reason: WI226 T31 v0.9.9 release truth completed.
- Goal: Complete WI226 canonical v0.9.9 release plan.
- State: T31 done; T32 is the sole todo.
- Stage: close
- Work Item: 226-v0-9-9-canonical-release
- Branch: feature/226-v0-9-9-canonical-release-docs

## Changed Files

- M .ai-sdlc/project/config/project-state.yaml
- M program-manifest.yaml
- M tests/integration/test_repo_program_manifest.py
- specs/226-v0-9-9-canonical-release/spec.md
- specs/226-v0-9-9-canonical-release/plan.md
- specs/226-v0-9-9-canonical-release/tasks.md
- specs/226-v0-9-9-canonical-release/task-execution-log.md
- src/ai_sdlc/core/program_service.py
- tests/unit/test_program_service.py
- src/ai_sdlc/cli/program_cmd.py
- tests/integration/test_cli_program.py
- src/ai_sdlc/core/program_service.py
- .ai-sdlc/state/codex-handoff.md
- .superpowers/sdd/plan/task-2-report.md
- .superpowers/sdd/plan/task-3-report.md
- .github/workflows/pr-checks.yml
- .github/workflows/release-build.yml
- tests/integration/test_github_workflows.py
- .superpowers/sdd/plan/task-4-report.md
- .superpowers/sdd/plan/task-5-report.md
- docs/releases/v0.9.9.md
- pyproject.toml
- uv.lock
- src/ai_sdlc/__init__.py
- src/ai_sdlc/core/verify_constraints.py
- README.md
- USER_GUIDE.zh-CN.md
- packaging/offline/README.md
- packaging/offline/RELEASE_CHECKLIST.md
- docs/pull-request-checklist.zh.md
- docs/框架自迭代开发与发布约定.md
- .github/workflows/release-artifact-smoke.yml
- .github/workflows/windows-user-guide-e2e.yml
- .github/workflows/macos-user-guide-e2e.yml
- .github/workflows/windows-update-prompt-e2e.yml
- .github/workflows/windows-offline-smoke.yml
- tests/unit/test_verify_constraints.py
- tests/integration/test_offline_bundle_scripts.py

## Key Decisions

- Formal remediation is confined to this canonical WI226 baseline.
- The parser/guard sees T23 as the unique next executable task; T31/T32 remain blocked.
- T21 evaluates only the root release-candidate spec and its explicit DFS dependency closure through existing single-spec readiness.
- T21 is a thin 89-line production addition; global-blocked, dependency-blocked, and stale fixtures invoke real single-spec readiness.
- Aggregate preflight failures now return bounded detail/actions; readiness success logic is unchanged.
- T31 must create the release note before registering it, and T32 is the final repository executable/checklist task.
- PR Checks and Release Build use the exact same unconditional WI226 truth-audit command; Release Build places it before build, attestation, and upload.
- T31 creates and registers the v0.9.9 release note atomically; current entry
  surfaces move to v0.9.9 while explicit post-v0.9.8 history remains unchanged.

## Commands / Tests

- guard => PASS; selected T21.
- program validate => PASS.
- verify constraints => PASS; no BLOCKERs.
- git diff --check => PASS.
- uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness' => RED 5 failed (method absent), then GREEN 5 passed.
- uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness' => PASS; 12 passed, 409 deselected.
- uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py => PASS.
- uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request "进入 T22 truth audit CLI TDD" --json => PASS; selected T22.
- uv run pytest tests/unit/test_program_service.py -q -k 'release_candidate_truth_readiness' => PASS; 5 passed, 416 deselected.
- uv run pytest tests/unit/test_program_service.py -q -k 'build_spec_truth_readiness or release_candidate_truth_readiness' => PASS; 12 passed, 409 deselected.
- uv run ruff check src/ai_sdlc/core/program_service.py tests/unit/test_program_service.py => PASS; git diff --check => PASS.
- uv run pytest tests/integration/test_repo_program_manifest.py -q => PASS; 1 passed in 132.58s.
- uv run pytest tests/integration/test_cli_program.py -q -k 'truth_audit and release_candidate' => RED 3 failed because --wi was unknown (exit 2), then GREEN 5 passed, 233 deselected.
- uv run pytest tests/integration/test_cli_program.py -q -k 'program_truth_audit' => PASS; 9 passed, 229 deselected.
- uv run ruff check src/ai_sdlc/cli/program_cmd.py tests/integration/test_cli_program.py => PASS; git diff --check => PASS.
- uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request "进入 T23 PR/tag 工作流门禁" --json => PASS; selected T23.
- terminal repair RED => 1 failed, 6 passed because README.md was unmapped with empty detail/actions; GREEN => 7 passed. Task2 focused => 12 passed; audit => 11 passed; Ruff and diff-check => PASS.
- T23 RED => 1 failed, 4 passed, 12 deselected because the PR gate was absent; GREEN => 5 passed, 12 deselected. Full workflow contract => 17 passed; Ruff test file and diff-check => PASS.
- `uv run ai-sdlc workitem guard --wi specs/226-v0-9-9-canonical-release --request '进入 T31 v0.9.9 release truth 同步' --json` => PASS; selected T31.
- T31 RED: version-contract tests failed while current entry surfaces still named v0.9.8.
- T31 GREEN: focused release suite => 213 passed; manifest inventory => 1 passed with 1180/1180 mapped, unmapped 0, missing 6, release layer 45.
- T31: `uv run ai-sdlc verify constraints`, `uv run ruff check src tests`, and `git diff --check` => PASS.

## Blockers / Risks

- No T31 blocker. T32 must still run truth sync and its final local verification.

## Local PR Review

- none

## Exact Next Steps

- Execute T32 final local validation and truth refresh only.
