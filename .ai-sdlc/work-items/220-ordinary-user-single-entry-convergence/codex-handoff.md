# Continuity Handoff

- Updated: 2026-08-29T18:50:12+00:00
- Reason: T32 GREEN 并切换到 T41
- Goal: 完成 WI220 有界 guidance 对账与全量交付
- State: P2A/P2B GREEN；T32 done；仅 T41 todo
- Stage: close
- Work Item: 220-ordinary-user-single-entry-convergence
- Branch: feature/220-ordinary-user-single-entry-convergence-docs

## Changed Files
- M README.md
- M specs/220-ordinary-user-single-entry-convergence/task-execution-log.md
- M specs/220-ordinary-user-single-entry-convergence/tasks.md
- M src/ai_sdlc/__main__.py
- M src/ai_sdlc/cli/command_names.py
- M src/ai_sdlc/cli/main.py
- M tests/integration/test_cli_beginner_ux.py

## Key Decisions
- 默认双入口仅六命令；21 个高级入口只从 root help 隐藏，直接调用与 134 条 command inventory 保留

## Commands / Tests
- P2B focused 4 passed；完整三文件 16 passed in 5.27s；Ruff/diff-check PASS

## Blockers / Risks
- 无；T41 只允许修复 rg 证明的真实入口文案漂移

## Local PR Review
- none

## Exact Next Steps
- 提交 T32；用 rg 对账 AGENTS/template/adapters/docs 中仍要求普通用户先跑 diagnostics 的文案，只改真实冲突
