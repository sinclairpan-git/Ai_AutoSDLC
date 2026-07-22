# Continuity Handoff

- Updated: 2026-07-22T05:10:00Z
- Reason: 合并已验收的 close-pending lifecycle prerequisite，继续处理 PR #170 source-inventory P1
- Goal: 归档 WI218 产品需求并完成消费项目/框架约束隔离实现与验收
- State: lifecycle PR #171 已合并并通过 detached fresh-main；formal 分支正在同步 main，随后补诚实 close-pending summary、恢复 zero-missing 并重新冻结评审身份
- Stage: review
- Work Item: 218-consumer-framework-constraint-isolation
- Branch: feature/218-consumer-framework-constraint-isolation-docs

## Changed Files
- UU .ai-sdlc/state/codex-handoff.md
- M src/ai_sdlc/core/program_service.py
- M tests/unit/test_program_service.py

## Key Decisions
- WI218 summary 只声明 formal archive candidate，必须包含 `stage: close-pending`，不得声称 T13/T21～T33 已完成
- 恢复 WI201 常驻 `missing_sources=0` / close fully materialized 断言，不保留 active-WI waiver

## Commands / Tests
- PR #171 current HEAD Codex clean、22/22 checks、squash merge=fb75a9d6；detached fresh-main focused=4、ProgramService=416、CLI=233、Ruff/constraints PASS

## Blockers / Risks
- none

## Local PR Review
- Codex #170 P1 与 LEAN/SAFETY cross-review 已共同确认：summary-only 需先补 lifecycle false-close；前置条件现已满足

## Exact Next Steps
- 完成 main merge；新增 close-pending summary，修正 formal plan/tasks/log 与 manifest exact；truth sync 后重新取得同一身份 LEAN/SAFETY PASS0，再推送 #170 并重审
