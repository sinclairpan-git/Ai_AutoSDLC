# Continuity Handoff

- Updated: 2026-06-22T11:46:50+00:00
- Reason: Codex review P2 修复后交接
- Goal: 发布 AI-SDLC v0.8.4
- State: PR #86 checks 已通过；Codex review 对最新提交提出 P2：Windows release note 不应把 install_offline.ps1 写成 --upgrade-existing。已修正为 install_offline.ps1 -UpgradeExisting。
- Stage: close
- Work Item: release-v0.8.4
- Branch: codex/release-0.8.4

## Changed Files
- M docs/releases/v0.8.4.md

## Key Decisions
- Windows .ps1 示例使用 -UpgradeExisting；macOS/Linux shell installer 继续使用 --upgrade-existing。

## Commands / Tests
- uv run ai-sdlc verify constraints => no BLOCKERs
- uv run pytest tests/unit/test_verify_constraints.py tests/integration/test_github_workflows.py tests/integration/test_offline_bundle_scripts.py -q => 173 passed

## Blockers / Risks
- none

## Exact Next Steps
- 提交并推送 Codex P2 修复，重新请求 Codex review 并等待 PR #86 checks 重新通过后合并。
