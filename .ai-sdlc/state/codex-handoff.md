# Continuity Handoff

- Updated: 2026-06-24T13:26:13+00:00
- Reason: Before release patch commit
- Goal: Prepare v0.8.9 patch release with truthful Windows upgrade guidance
- State: Bumped current release surfaces to v0.8.9, added v0.8.9 release notes, kept 0.7.6+ self-update check as first upgrade path, and documented package rescue only when historical installs do not finish upgrading.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/windows-update-e2e-v088

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
- M tests/unit/test_update_advisor.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.8.9.md

## Key Decisions
- 0.7.6+ remains intended to self-upgrade via ai-sdlc self-update check; cloud Windows E2E showed some historical packages still need one rescue package replacement.

## Commands / Tests
- uv run ai-sdlc --version => 0.8.9
- uv run pytest tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py -q => 30 passed, 1 skipped
- uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_verify_constraints.py -q => 174 passed
- uv run ruff check src/ai_sdlc/core/update_advisor.py src/ai_sdlc/core/verify_constraints.py tests/unit/test_update_advisor.py tests/integration/test_cli_self_update.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_verify_constraints.py => pass
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- none

## Exact Next Steps
- Commit and push v0.8.9 patch surfaces, monitor PR checks including Windows user guide E2E, request review, then merge and publish v0.8.9.
