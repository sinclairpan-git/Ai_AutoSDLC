# Continuity Handoff

- Updated: 2026-09-03T10:16:08+00:00
- Reason: WI226 T31 v0.9.9 release truth completed
- Goal: Complete WI226 canonical v0.9.9 release plan.
- State: T31 done; T32 is the sole todo.
- Stage: close
- Work Item: 226-v0-9-9-canonical-release
- Branch: feature/226-v0-9-9-canonical-release-docs

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .github/workflows/macos-user-guide-e2e.yml
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M .github/workflows/windows-update-prompt-e2e.yml
- M .github/workflows/windows-user-guide-e2e.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M program-manifest.yaml
- M pyproject.toml
- M specs/226-v0-9-9-canonical-release/task-execution-log.md
- M specs/226-v0-9-9-canonical-release/tasks.md
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/integration/test_repo_program_manifest.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.9.9.md

## Key Decisions
- Current release surfaces and default tags use v0.9.9; explicit post-v0.9.8 history is preserved.

## Commands / Tests
- RED release-contract tests; GREEN 213 focused tests, manifest 1 passed, constraints, ruff, and diff-check passed.

## Blockers / Risks
- No T31 blocker. T32 has not yet run truth sync, full pytest, or external release evidence.

## Local PR Review
- none

## Exact Next Steps
- Execute T32 final local validation and truth refresh only.
