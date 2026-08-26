# Continuity Handoff

- Updated: 2026-08-26T01:22:30+00:00
- Reason: 完成 A0 RED/GREEN/refactor、Go/No-Go 与独立提交。
- Goal: 继续实施 WI219；A0 已 Go，下一批用 TDD 统一 linked-first active binding。
- State: A0 已提交为 3dbdd8a2；truth-check 14 passed，Ruff PASS；真实 WI219 HEAD formal candidate 正确为 formal_freeze_only。
- Stage: close
- Work Item: 219-mainline-truth-roi-contract
- Branch: feature/219-mainline-truth-roi-contract-docs

## Changed Files
- M specs/219-mainline-truth-roi-contract/plan.md
- M specs/219-mainline-truth-roi-contract/task-execution-log.md
- M specs/219-mainline-truth-roi-contract/tasks.md

## Key Decisions
- behind-only 仅使用已有 remote ref；formal-only 仅识别精确路径集合；不加入内容 parser 或新状态。

## Commands / Tests
- A0 RED：4 failed/10 passed；GREEN：14 passed；Ruff 与 diff-check PASS；产品 38增/3删、测试 161增。

## Blockers / Risks
- 当前无 blocker；A1 若需要第二 resolver、writer/schema/status 格式或 silent historical fallback 则 No-Go。

## Local PR Review
- none

## Exact Next Steps
- 执行 T30：先为 active_work_item_spec_dir 和全部 linked-first consumer matrix 写失败测试。
