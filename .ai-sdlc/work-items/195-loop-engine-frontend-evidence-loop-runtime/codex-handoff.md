# Continuity Handoff

- Updated: 2026-07-04T06:09:59+00:00
- Reason: prepare v0.9.5 release after v1.7.1 frontend governance refresh
- Goal: 发布 AI-SDLC v0.9.5，包含 Vue3 public-primevue v1.7.1 视觉规范刷新
- State: v0.9.5 版本面已同步：新增 docs/releases/v0.9.5.md；pyproject、__init__、uv.lock、README、USER_GUIDE、offline docs/checklist、GitHub workflows、verify_constraints 和版本敏感测试已从 v0.9.4 对齐到 v0.9.5；v1.7.1 前端治理改动保持在同一发布分支。
- Stage: execute
- Work Item: 195-loop-engine-frontend-evidence-loop-runtime
- Branch: codex/release-v0.9.5-vue3-v1.7.1

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
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M providers/frontend/public-primevue/provider.manifest.yaml
- M pyproject.toml
- M specs/188-vue3-public-primevue-default-provider-governance/task-execution-log.md
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/adapters/claude_code/AI-SDLC.md
- M src/ai_sdlc/adapters/codex/AI-SDLC.md
- M src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md
- M src/ai_sdlc/adapters/vscode/AI-SDLC.md
- M src/ai_sdlc/core/frontend_theme_token_governance.py
- M src/ai_sdlc/core/program_service.py
- M src/ai_sdlc/core/verify_constraints.py
- M src/ai_sdlc/generators/frontend_provider_profile_artifacts.py
- M src/ai_sdlc/models/frontend_generation_constraints.py
- M src/ai_sdlc/models/frontend_solution_confirmation.py
- M src/ai_sdlc/rules/pipeline.md
- M tests/integration/test_cli_program.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_frontend_generation_constraint_artifacts.py
- M tests/unit/test_frontend_generation_constraints.py
- M tests/unit/test_frontend_provider_profile_artifacts.py
- M tests/unit/test_frontend_solution_confirmation_artifacts.py
- M tests/unit/test_frontend_solution_confirmation_models.py
- M tests/unit/test_frontend_theme_token_governance.py
- M tests/unit/test_program_service.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.9.5.md

## Key Decisions
- 目标版本按远端最新 v0.9.4 的补丁发布，使用 v0.9.5。
- 历史 docs/releases/v0.9.4.md 保留不改；当前发布入口和校验面指向 v0.9.5。

## Commands / Tests
- uv lock => resolved 31 packages
- uv run python -m ai_sdlc --version => 0.9.5
- uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 186 passed
- uv run pytest frontend governance/program service unit suite -q => 416 passed
- uv run pytest managed delivery apply integration targets -q => 2 passed
- uv run ai-sdlc verify constraints => no BLOCKERs
- uv run ruff check src tests => All checks passed
- git diff --check => pass

## Blockers / Risks
- PowerShell on this machine still fails to start due to .NET assembly load error; local validation used zsh/uv. Windows validation must rely on GitHub workflows after PR/release.

## Local PR Review
- none

## Exact Next Steps
- Stage, commit, push codex/release-v0.9.5-vue3-v1.7.1, open PR, request Codex review, monitor required checks, then merge and create/publish v0.9.5 release after release-build assets exist.
