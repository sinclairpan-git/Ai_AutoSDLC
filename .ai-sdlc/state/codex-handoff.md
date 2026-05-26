# Continuity Handoff

- Updated: 2026-05-26T09:54:54+00:00
- Reason: Post-change checkpoint for PowerShell selector fix
- Goal: Triage and patch AI-SDLC Windows/Codex onboarding production defects
- State: Implemented the PowerShell selector fix that was previously only described: Windows now uses numbered selection for agent target and shell prompts, avoiding redraw-based clear-screen behavior entirely. Added unit tests that monkeypatch Windows mode and fail if os.system('cls') is called, while asserting no ANSI clear sequence or arrow-key prompt appears.
- Stage: close
- Work Item: 181-cross-platform-release-gate-matrix-baseline
- Branch: codex/agentops-runtime-bridge-v0718

## Changed Files
- M .ai-sdlc/state/codex-handoff.md
- M .ai-sdlc/state/resume-pack.yaml
- M .ai-sdlc/work-items/181-cross-platform-release-gate-matrix-baseline/codex-handoff.md
- M USER_GUIDE.zh-CN.md
- M packaging/install_online.ps1
- M packaging/offline/install_offline.ps1
- M src/ai_sdlc/adapters/claude_code/AI-SDLC.md
- M src/ai_sdlc/adapters/codex/AI-SDLC.md
- M src/ai_sdlc/adapters/cursor/rules/ai-sdlc.md
- M src/ai_sdlc/adapters/generic/ide-hint.md
- M src/ai_sdlc/adapters/vscode/AI-SDLC.md
- M src/ai_sdlc/cli/beginner_guidance.py
- M src/ai_sdlc/core/verify_constraints.py
- M src/ai_sdlc/integrations/agent_target.py
- M tests/integration/test_cli_beginner_ux.py
- M tests/integration/test_cli_init.py
- M tests/integration/test_offline_bundle_scripts.py
- M tests/unit/test_agent_target.py
- M tests/unit/test_ide_adapter.py
- M tests/unit/test_verify_constraints.py

## Key Decisions
- PowerShell selector reliability must not depend on terminal clear-screen support; Windows uses stable numbered prompts by default.

## Commands / Tests
- uv run pytest tests/unit/test_agent_target.py tests/integration/test_cli_init.py tests/integration/test_cli_adapter.py -q: 34 passed
- uv run ruff check src/ai_sdlc/integrations/agent_target.py tests/unit/test_agent_target.py: passed
- uv run ai-sdlc verify constraints: no BLOCKERs

## Blockers / Risks
- Published v0.7.18 assets still need rebuilding before the numbered PowerShell selector reaches users.
- 删除注释记录: .ai-sdlc/state/resume-pack.yaml 中旧 context_summary 包含 '#66 checks 和 Codex review 结论。'，本轮 handoff 刷新为当前生产缺陷摘要，删除原因是上下文已从 PR #66 监控切换到 Windows/Codex onboarding 与 PowerShell selector 修复。

## Exact Next Steps
- Rebuild and smoke-test Windows release asset, verifying init selector transcript has no ANSI clear codes, no cls redraw dependency, and no duplicated menus.
