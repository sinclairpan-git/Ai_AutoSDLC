# Continuity Handoff

- Updated: 2026-06-22T12:49:38+00:00
- Reason: 用户反馈升级后 adapter ingress/materialized/unverified 文案令人困惑
- Goal: 修复 v0.8.4 升级后 adapter 未验证提示造成用户困惑的问题
- State: 已调整 beginner-facing CLI 文案：materialized/unverified 明确说明不是安装或升级失败；run --dry-run 指向 AI 对话而非排障循环；host-runtime ready 默认不再把 dry-run 当主路径；用户手册已补充解释。
- Stage: close
- Work Item: adapter-upgrade-guidance-ux
- Branch: codex/adapter-upgrade-guidance-ux

## Changed Files
- M USER_GUIDE.zh-CN.md
- M src/ai_sdlc/cli/beginner_guidance.py
- M src/ai_sdlc/cli/host_runtime_cmd.py
- M src/ai_sdlc/cli/run_cmd.py
- M tests/integration/test_cli_beginner_ux.py
- M tests/integration/test_cli_host_runtime.py

## Key Decisions
- 保留机器可读 adapter 真值，但默认输出只展示用户结论和下一步；内部状态继续通过 adapter status --json 供排查使用。

## Commands / Tests
- uv run pytest tests/integration/test_cli_beginner_ux.py tests/integration/test_cli_host_runtime.py tests/integration/test_cli_run.py::TestRunCommand::test_run_dry_run_continues_without_manual_adapter_activation -q => 10 passed
- uv run pytest tests/integration/test_cli_beginner_ux.py tests/integration/test_cli_host_runtime.py tests/integration/test_cli_init.py tests/integration/test_cli_adapter.py tests/integration/test_cli_run.py tests/unit/test_verify_constraints.py -q => 210 passed
- uv run ruff check src tests => pass
- uv run ai-sdlc verify constraints => no BLOCKERs

## Blockers / Risks
- 源码态临时 dry-run 在本地自开发环境末尾出现 AgentOps missing_token，与本次用户提示文案无关；正式测试路径已关闭/隔离该配置并通过。

## Exact Next Steps
- 如需发布补丁版，提交当前分支并走 PR/Codex review/release 流程。
