# Continuity Handoff

- Updated: 2026-07-07T07:51:20+00:00
- Reason: v0.9.6 release prep validation complete
- Goal: 发布 AI-SDLC v0.9.6，包含 Vue3 public-primevue v1.8 视觉规范刷新
- State: 已在 codex/release-v0.9.6-vue3-v1.8 分支完成版本 bump 与 release truth 同步：pyproject/src version、uv.lock、README、USER_GUIDE、offline docs/checklist、workflow defaults、verify_constraints、tests、docs/releases/v0.9.6.md，以及 v1.8 provider/generation/adapters 变更。
- Stage: execute
- Work Item: 195-loop-engine-frontend-evidence-loop-runtime
- Branch: codex/release-v0.9.6-vue3-v1.8

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/195-loop-engine-frontend-evidence-loop-runtime/codex-handoff.md
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M .github/workflows/windows-update-prompt-e2e.yml
- M .github/workflows/windows-user-guide-e2e.yml
- M AGENTS.md
- M README.md
- M USER_GUIDE.zh-CN.md
- M "docs/Vue3\344\274\201\344\270\232\347\272\247\345\211\215\347\253\257\345\274\200\345\217\221\350\247\204\350\214\203\346\226\271\346\241\210.md"
- M docs/pull-request-checklist.zh.md
- M docs/vue3-public-primevue-default-provider-prd.zh-CN.md
- M "docs/\346\241\206\346\236\266\350\207\252\350\277\255\344\273\243\345\274\200\345\217\221\344\270\216\345\217\221\345\270\203\347\272\246\345\256\232.md"
- M governance/frontend/generation/hard-rules.yaml
- M governance/frontend/generation/token-rules.yaml
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M providers/frontend/public-primevue/provider.manifest.yaml
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/adapters/claude_code/AI-SDLC.md
- M src/ai_sdlc/adapters/codex/AI-SDLC.md
- M src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md
- M src/ai_sdlc/adapters/vscode/AI-SDLC.md
- M src/ai_sdlc/core/verify_constraints.py
- M src/ai_sdlc/generators/frontend_provider_profile_artifacts.py
- M src/ai_sdlc/models/frontend_generation_constraints.py
- M src/ai_sdlc/rules/pipeline.md
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_frontend_generation_constraint_artifacts.py
- M tests/unit/test_frontend_generation_constraints.py
- M tests/unit/test_frontend_provider_profile_artifacts.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.9.6.md

## Key Decisions
- v0.9.6 是 v1.8 frontend visual contract patch release；旧 v0.9.5 release notes 保留为历史，不参与当前 release truth。

## Commands / Tests
- uv lock => resolved 31 packages
- uv run python -m ai_sdlc --version => 0.9.6
- uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 189 passed
- uv run pytest tests/unit/test_frontend_* tests/unit/test_managed_delivery_apply.py tests/unit/test_program_service.py -q => 764 passed, 2 skipped
- uv run ruff check src tests => All checks passed
- uv run ai-sdlc verify constraints => no BLOCKERs
- git diff --check => pass

## Blockers / Risks
- none

## Local PR Review
- none

## Exact Next Steps
- 提交分支、push、创建 PR，评论 @codex review，进入 heartbeat 等待 review/checks。
