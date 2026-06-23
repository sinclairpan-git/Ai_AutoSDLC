# Continuity Handoff

- Updated: 2026-06-23T09:43:14+00:00
- Reason: after release preparation document/version change batch
- Goal: Ship v0.8.6 patch release for Windows upgrade and internal diagnostic UX
- State: PR #89 has been merged to main; v0.8.6 release metadata is prepared with version/docs/workflow/test references updated and docs/releases/v0.8.6.md added. Targeted release and UX validation passed.
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: main

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
- ?? docs/releases/v0.8.6.md

## Key Decisions
- Release must follow existing v0.8.5 pattern: update version truth, release notes, offline/user docs, workflow defaults, and release consistency tests together.

## Commands / Tests
- `uv run pytest tests/integration/test_cli_beginner_ux.py tests/integration/test_cli_host_runtime.py tests/integration/test_cli_init.py tests/integration/test_cli_adapter.py tests/integration/test_cli_run.py tests/unit/test_cli_hooks.py tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q` => 254 passed.
- `uv run ruff check src tests` => passed.
- `uv run ai-sdlc verify constraints` => no BLOCKERs.
- `git diff --check` => passed.
- `uv run ai-sdlc --version` => 0.8.6.

## Blockers / Risks
- none

## Exact Next Steps
- Commit v0.8.6 release metadata, push main, create tag/release, and monitor release asset build/smoke.
