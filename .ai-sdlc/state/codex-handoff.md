# Continuity Handoff

- Updated: 2026-06-22T13:16:00+00:00
- Reason: v0.8.5 补丁发布分支版本漂移修正后验证完成
- Goal: 发布 v0.8.5 补丁版，修复升级后 adapter 未验证提示造成用户困惑的问题
- State: 已修正 Windows upgrade smoke 仍匹配 0.8.4 的版本漂移；v0.8.5 release docs、workflow 默认 tag、offline 文档、约束标记和测试夹具已对齐。
- Stage: close
- Work Item: release-0.8.5
- Branch: codex/release-0.8.5

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .github/workflows/release-artifact-smoke.yml
- M .github/workflows/release-build.yml
- M .github/workflows/windows-offline-smoke.yml
- M README.md
- M USER_GUIDE.zh-CN.md
- M docs/pull-request-checklist.zh.md
- M docs/框架自迭代开发与发布约定.md
- M packaging/offline/README.md
- M packaging/offline/RELEASE_CHECKLIST.md
- M pyproject.toml
- M src/ai_sdlc/__init__.py
- M src/ai_sdlc/core/verify_constraints.py
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_verify_constraints.py
- M uv.lock
- ?? docs/releases/v0.8.5.md

## Key Decisions
- Windows offline upgrade smoke 必须断言 0.8.5，不能只更新错误文案而保留 0.8.4 正则。

## Commands / Tests
- uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 173 passed
- uv run ai-sdlc verify constraints => no BLOCKERs
- git diff --check => pass

## Blockers / Risks
- 需完成 PR/Codex review、合并、tag/release/build/smoke。

## Exact Next Steps
- 提交并推送 codex/release-0.8.5，创建 PR，等待 Codex review 与 required checks。
