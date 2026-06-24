# Continuity Handoff

- Updated: 2026-06-24T01:33:28+00:00
- Reason: 记录用户反馈补丁实现和验证
- Goal: 修复用户升级路径：0.7.6+ self-update check 自动升级、--version 可用、init 普通输出不暴露内部 adapter 排查语
- State: 已在分支 codex/update-ux-self-update-version 修改：python -m ai_sdlc --version 直接输出版本；init 完成兜底从 adapter status 改为 adapter select/回到 AI 对话；新增 0.7.6+ unknown channel self-update check 自动安装回归测试；更新 init UX 测试。
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: codex/update-ux-self-update-version

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M src/ai_sdlc/__main__.py
- M src/ai_sdlc/cli/beginner_guidance.py
- M tests/integration/test_cli_init.py
- M tests/integration/test_cli_module_invocation.py
- M tests/integration/test_cli_self_update.py

## Key Decisions
- 普通用户路径不再把 adapter status/run dry-run/host ingress 作为 init 已完成后的下一步；历史 0.7.6+ 安装渠道未知也必须可由 self-update check 自动进入安装流程。

## Commands / Tests
- uv run pytest tests/integration/test_cli_self_update.py tests/integration/test_cli_module_invocation.py tests/integration/test_cli_init.py tests/integration/test_cli_beginner_ux.py -q => 39 passed
- uv run ai-sdlc verify constraints => no BLOCKERs
- git diff --check => pass
- uv run ai-sdlc --version => 0.8.6; uv run python -m ai_sdlc --version => 0.8.6

## Blockers / Risks
- none

## Exact Next Steps
- stage commit, push branch, open PR, request Codex review, wait for CI, merge, then publish v0.8.7 so installed users receive the fix
