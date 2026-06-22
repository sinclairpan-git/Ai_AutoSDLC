# Continuity Handoff

- Updated: 2026-06-22T11:24:38+00:00
- Reason: v0.8.4 release validation passed
- Goal: Publish AI-SDLC v0.8.4
- State: v0.8.4 version truth, release docs, workflows, verify constraints, and tests are updated on codex/release-0.8.4. Local release verification set passed.
- Stage: close
- Work Item: release-v0.8.4
- Branch: codex/release-0.8.4

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M docs/releases/v0.8.4.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/unit/test_verify_constraints.py
- M uv.lock

## Key Decisions
- Keep the release PR focused on version and release-entry consistency before creating the GitHub Release/tag.

## Commands / Tests
- uv run pytest tests/unit/test_frontend_solution_confirmation_artifacts.py tests/unit/test_managed_delivery_apply.py tests/unit/test_verify_constraints.py tests/unit/test_frontend_browser_gate_runtime.py -q: 211 passed, 2 skipped
- uv run pytest tests/integration -k 'visual or browser_gate or a11y' -q: 56 passed, 601 deselected
- uv run ruff check src tests: pass
- uv run ai-sdlc verify constraints: no BLOCKERs
- git diff --check: pass

## Blockers / Risks
- PR review/checks and GitHub release/tag still pending.

## Exact Next Steps
- Commit and push codex/release-0.8.4, open PR, request Codex review, monitor checks, merge, then tag and publish v0.8.4.
