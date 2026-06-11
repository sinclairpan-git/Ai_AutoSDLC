# Continuity Handoff

- Updated: 2026-06-11T01:58:32+00:00
- Reason: after preparing v0.8.3 release changes and completing local validation
- Goal: Publish AI-SDLC v0.8.3 patch release for the frontend stack/component-library confirmation guard.
- State: Prepared release branch codex/release-v0.8.3. Version surfaces updated from 0.8.2 to 0.8.3 across pyproject, package fallback version, release entry docs, offline packaging docs, release workflows, Windows offline upgrade smoke expected version, verify_constraints release truth, and tests. Added docs/releases/v0.8.3.md describing the frontend-governance safety patch.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/release-v0.8.3

## Changed Files
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.8.3.md

## Key Decisions
- Release v0.8.3 as a patch because latest GitHub Release is v0.8.2 and the merged frontend confirmation guard is user-facing governance behavior that should be available in packaged installs.

## Commands / Tests
- uv run ai-sdlc verify constraints => no BLOCKERs
- uv run ruff check src tests => All checks passed
- uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 168 passed
- uv run pytest => 2666 passed, 2 skipped
- git diff --check => pass

## Blockers / Risks
- Official @codex review may still be quota-limited; use independent read-only review fallback if needed, as in PR #82.

## Exact Next Steps
- Commit v0.8.3 release branch, push, open PR, request @codex review, create 5-minute heartbeat, monitor checks/review, merge when clean, create GitHub Release v0.8.3, run release-build.yml with upload_to_release=true, then run release-artifact-smoke.yml for v0.8.3.
