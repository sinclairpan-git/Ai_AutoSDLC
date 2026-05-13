# Continuity Handoff

- Updated: 2026-05-13T05:17:40+00:00
- Reason: after local verification for v0.7.15 hotfix
- Goal: Publish v0.7.15 hotfix for current-directory offline install guidance
- State: Current-directory guide fix and v0.7.15 version sync are implemented. Local verification passed, including PowerShell current-directory package lookup.
- Stage: close
- Work Item: 181-cross-platform-release-gate-matrix-baseline
- Branch: codex/release-v0.7.15-current-dir-install

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/181-cross-platform-release-gate-matrix-baseline/codex-handoff.md
- M .cursor/rules/ai-sdlc.mdc
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M docs/releases/v0.7.0.md
- M docs/releases/v0.7.1.md
- M docs/releases/v0.7.2.md
- M docs/releases/v0.7.3.md
- M docs/releases/v0.7.4.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/install_online.sh
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_cli_self_update.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_packaging_backend.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.7.15.md

## Key Decisions
- none

## Commands / Tests
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/unit/test_verify_constraints.py -q: 151 passed
- PowerShell current-directory lookup simulation: found ai-sdlc-offline-0.7.15-windows-amd64.zip without changing directory
- uv run pytest tests/integration/test_offline_bundle_scripts.py tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/unit/test_packaging_backend.py tests/integration/test_cli_self_update.py -q: 173 passed
- uv run ruff check src tests packaging/offline/verify_offline_bundle.py: passed
- uv run ai-sdlc verify constraints: no BLOCKERs
- uv build: built ai_sdlc-0.7.15 sdist/wheel
- uv run pytest -q: 2531 passed, 2 skipped

## Blockers / Risks
- none

## Exact Next Steps
- Review diff, commit, push branch, create PR, request @codex review, wait for checks/review, then merge and publish v0.7.15.
