# Continuity Handoff

- Updated: 2026-07-02T06:59:54+00:00
- Reason: After v0.9.3 release prep validation
- Goal: 发布 v0.9.3：Vue3 前端规范 v1.3 AI 执行版
- State: 已完成 v0.9.3 版本面升级、发布说明新增、README/USER_GUIDE/offline/workflow/test/verify constraints 同步；前端规范 v1.3、provider manifest、generation hard/token rules、adapter 模板、CLI 展示与测试保持一致。当前分支 codex/release-v0.9.3-vue3-standard。
- Stage: execute
- Work Item: 195-loop-engine-frontend-evidence-loop-runtime
- Branch: codex/release-v0.9.3-vue3-standard

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
- M providers/frontend/public-primevue/provider.manifest.yaml
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/adapters/claude_code/AI-SDLC.md
- M src/ai_sdlc/adapters/codex/AI-SDLC.md
- M src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md
- M src/ai_sdlc/adapters/vscode/AI-SDLC.md
- M src/ai_sdlc/cli/program_cmd.py
- M src/ai_sdlc/core/verify_constraints.py
- M src/ai_sdlc/models/frontend_generation_constraints.py
- M src/ai_sdlc/models/frontend_solution_confirmation.py
- M src/ai_sdlc/rules/pipeline.md
- M tests/integration/test_cli_init.py
- M tests/integration/test_cli_program.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_frontend_generation_constraint_artifacts.py
- M tests/unit/test_frontend_provider_profile_artifacts.py
- M tests/unit/test_ide_adapter.py
- M tests/unit/test_program_service.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.9.3.md

## Key Decisions
- v0.9.3 定位为 Vue3 frontend governance release；默认仍为 vue3/public-primevue/modern-saas，Vue2/enterprise-vue2 兼容路径保留。

## Commands / Tests
- uv lock --check => resolved 31 packages
- uv run ai-sdlc verify constraints => no BLOCKERs
- uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 185 passed
- uv run pytest tests/unit/test_frontend_generation_constraint_artifacts.py tests/unit/test_frontend_solution_confirmation_artifacts.py tests/unit/test_frontend_provider_profile_artifacts.py tests/unit/test_program_service.py tests/integration/test_cli_init.py tests/integration/test_cli_program.py tests/unit/test_ide_adapter.py -q => 672 passed
- uv run ruff check src tests => passed
- git diff --check => clean

## Blockers / Risks
- 尚未创建 PR；推送后需按 Local Repository PR Protocol 请求 Codex review 并观察 required checks。

## Local PR Review
- none

## Exact Next Steps
- 提交当前发布分支，推送并打开 PR；随后请求 Codex review 并监控检查状态。
