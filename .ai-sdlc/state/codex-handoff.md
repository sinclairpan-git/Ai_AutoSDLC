# Continuity Handoff

- Updated: 2026-06-23T08:52:25+00:00
- Reason: 完成本轮 Windows 升级 UX 补丁后记录连续性
- Goal: 修复 Windows 升级后普通用户 CLI 输出困惑：project-config 锁定不中断、默认输出隐藏 adapter/internal activation 诊断、self-update 文案更明确
- State: 已完成实现并通过验证；本轮继续完善 PR #89，默认 adapter/status/run/host-runtime 输出不再暴露 ingress/materialized/unverified/governance activation proof，诊断信息保留在 --details/--json。非强制 AgentOps pending 仅 verbose 输出。涉及 CLI UX、adapter 模板、用户手册和回归测试。
- Stage: close
- Work Item: windows-project-config-permission-ux
- Branch: codex/windows-project-config-permission-ux

## Changed Files
- M AGENTS.md
- M USER_GUIDE.zh-CN.md
- M src/ai_sdlc/cli/cli_hooks.py
- M src/ai_sdlc/adapters/claude_code/AI-SDLC.md
- M src/ai_sdlc/adapters/codex/AI-SDLC.md
- M src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md
- M src/ai_sdlc/adapters/vscode/AI-SDLC.md
- M src/ai_sdlc/cli/adapter_cmd.py
- M src/ai_sdlc/cli/beginner_guidance.py
- M src/ai_sdlc/cli/host_runtime_cmd.py
- M src/ai_sdlc/cli/run_cmd.py
- M src/ai_sdlc/core/update_advisor.py
- M tests/integration/test_cli_adapter.py
- M tests/integration/test_cli_beginner_ux.py
- M tests/integration/test_cli_host_runtime.py
- M tests/integration/test_cli_run.py
- M tests/integration/test_cli_self_update.py
- M tests/unit/test_cli_hooks.py

## Key Decisions
- 普通用户默认路径只展示结果和下一步；内部 adapter 状态和激活证明类字段仅通过 --details/--json 暴露。
- run --dry-run 不再为 materialized adapter 打印额外提示，避免把非门禁诊断误读为错误。
- 非强制 AgentOps pending/transport diagnostic 静默处理；required 模式仍打印并阻断。
- Codex P2 反馈成立：CLI hook 只应吞 project-config.yaml 持久化权限错误，不得吞 AGENTS.md 等 adapter 文件写入权限错误；已按路径收窄。

## Commands / Tests
- uv run pytest tests/unit/test_ide_adapter.py::TestApplyAdapter::test_all_ide_templates_point_to_init_then_troubleshooting_only tests/integration/test_cli_beginner_ux.py tests/integration/test_cli_adapter.py tests/integration/test_cli_host_runtime.py tests/integration/test_cli_self_update.py tests/integration/test_cli_run.py tests/unit/test_cli_hooks.py tests/unit/test_project_config.py tests/unit/test_verify_constraints.py -q => 222 passed
- uv run ruff check targeted files => pass
- uv run ai-sdlc verify constraints => no BLOCKERs
- git diff --check => pass

## Blockers / Risks
- verify constraints 会刷新 .ai-sdlc/state/resume-pack.yaml；提交前需确认该运行态噪声未被纳入。

## Exact Next Steps
- 提交并 force-push PR #89，重新请求 Codex review 并等待 checks。
