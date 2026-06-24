# Continuity Handoff

- Updated: 2026-06-24T05:21:56+00:00
- Reason: meaningful code/test change batch completed
- Goal: 实现 AI-SDLC 新版本提醒确认：CLI 任意命令检测到新版本时提示当前/最新版本并支持确认升级；AI 非交互式命令输出对话提醒。
- State: 已修改 self-update 入口提醒逻辑与回归测试；保留每日 GitHub 检查缓存逻辑。
- Stage: close
- Work Item: 187-agentops-self-iteration-monitoring
- Branch: main

## Changed Files
- M .ai-sdlc/state/resume-pack.yaml
- M src/ai_sdlc/cli/self_update_cmd.py
- M src/ai_sdlc/core/update_advisor.py
- M tests/integration/test_cli_self_update.py

## Key Decisions
- 交互式终端使用 y/n 确认，y 调用 self_update_install 后停止旧命令；非交互式 AI 会话不阻塞 stdin，输出确认升级提示和 ai-sdlc self-update check 命令。

## Commands / Tests
- uv run pytest tests/integration/test_cli_self_update.py tests/unit/test_update_advisor.py -q => 28 passed, 1 skipped
- uv run ruff check src/ai_sdlc/cli/self_update_cmd.py src/ai_sdlc/core/update_advisor.py tests/integration/test_cli_self_update.py tests/unit/test_update_advisor.py => passed
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- none

## Exact Next Steps
- 如需发布，开 v0.8.8 补丁分支并跑 Windows/Release upgrade E2E。
