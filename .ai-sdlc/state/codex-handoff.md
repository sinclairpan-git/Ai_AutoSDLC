# Continuity Handoff

- Updated: 2026-06-29T01:55:28+00:00
- Reason: Release prep validation completed
- Goal: Publish AI-SDLC v0.9.1 patch release
- State: Prepared v0.9.1 release branch with version bump, current release docs/user guide/workflow defaults/constraint constants aligned to v0.9.1, and new docs/releases/v0.9.1.md. Local validation passed.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/release-0.9.1

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
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
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_cli_self_update.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_program_service.py
- M tests/unit/test_update_advisor.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.9.1.md

## Key Decisions
- Publish as patch version v0.9.1 because v0.9.0 already exists on GitHub and PR #101 merged Vue3 PrimeVue spec alignment after that published release.

## Commands / Tests
- uv run pytest tests/unit/test_frontend_solution_confirmation_models.py tests/unit/test_program_service.py tests/integration/test_cli_program.py tests/unit/test_verify_constraints.py tests/unit/test_ide_adapter.py tests/integration/test_cli_init.py tests/integration/test_cli_verify_constraints.py -q: 845 passed
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/integration/test_github_workflows.py tests/integration/test_cli_self_update.py tests/unit/test_update_advisor.py -q: 71 passed, 1 skipped
- uv run ruff check src tests: passed
- git diff --check: passed
- uv run ai-sdlc verify constraints: no BLOCKERs

## Blockers / Risks
- none

## Exact Next Steps
- Commit v0.9.1 release prep, push branch, open PR, request Codex review, monitor checks, merge, tag v0.9.1, publish release assets, then run release artifact smoke.
