# Continuity Handoff

- Updated: 2026-07-03T10:52:03+00:00
- Reason: after full pytest for v0.9.4 release
- Goal: 发布 AI-SDLC v0.9.4，包含 Vue3 v1.6.1 前端规范刷新
- State: v0.9.4 发布分支本地验证已完成，diff 仅集中在 release truth surfaces、测试期望、uv.lock 与 handoff。
- Stage: execute
- Work Item: 195-loop-engine-frontend-evidence-loop-runtime
- Branch: codex/release-v0.9.4-vue3-standard

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md
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
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.9.4.md

## Key Decisions
- none

## Commands / Tests
- uv run pytest -q => 3142 passed, 3 skipped in 500.01s
- uv run ruff check src tests => passed
- uv run ai-sdlc verify constraints => no BLOCKERs
- git diff --check => clean

## Blockers / Risks
- none

## Local PR Review
- none

## Exact Next Steps
- stage/commit/push，创建 PR 并请求 Codex review 与 CI。
