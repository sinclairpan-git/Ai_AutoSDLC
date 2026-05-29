# Continuity Handoff

- Updated: 2026-05-29T03:18:24+00:00
- Reason: pre-PR validation completed
- Goal: Prepare v0.8.1 Windows old-user upgrade reliability patch
- State: Added permanent Windows old-user upgrade CI matrix for v0.7.5/v0.7.6 on Python 3.11/3.12, using branch-built v0.8.1 offline bundle and manual-equivalent -UpgradeExisting/init/dry-run commands.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/release-v0.8.1-upgrade-abi

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/187-agentops-self-iteration-monitoring/codex-handoff.md
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M packaging/offline/build_offline_bundle.sh
- M packaging/offline/install_offline.ps1
- M packaging/offline/install_offline.sh
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.8.1.md

## Key Decisions
- Use v0.8.1 patch instead of documenting Python 3.11-only support; novice-facing install/upgrade commands stay unchanged.

## Commands / Tests
- uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py tests/unit/test_verify_constraints.py -q: 164 passed
- uv run ruff check src tests: pass
- uv run ai-sdlc verify constraints: pass

## Blockers / Risks
- Need GitHub Actions clean Windows E2E result and Codex PR review after pushing PR.

## Exact Next Steps
- Commit, push branch, open PR, request @codex review, create 5-minute heartbeat monitor, then watch checks/review and fix any blockers on the same branch.
