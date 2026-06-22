# Continuity Handoff

- Updated: 2026-06-22T11:29:40+00:00
- Reason: PR #86 verify CI 修复后交接
- Goal: 发布 AI-SDLC v0.8.4
- State: PR #86 已创建并请求 Codex review；CI verify 失败原因定位为 workflow/offline 指南测试仍断言 v0.8.3，已同步到 v0.8.4。
- Stage: close
- Work Item: release-v0.8.4
- Branch: codex/release-0.8.4

## Changed Files
- M tests/integration/test_github_workflows.py
- M tests/integration/test_offline_bundle_scripts.py

## Key Decisions
- 历史 docs/releases/v0.8.3.md 保留不改；当前发布面测试断言同步到 v0.8.4。

## Commands / Tests
- uv run pytest tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 40 passed
- uv run ruff check src tests => passed
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- none

## Exact Next Steps
- 提交并推送 CI 断言修复，重新监控 PR #86 检查和 Codex review。
