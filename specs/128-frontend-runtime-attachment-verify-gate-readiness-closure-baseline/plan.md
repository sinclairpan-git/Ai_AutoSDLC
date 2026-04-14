# 实施计划：Frontend Runtime Attachment Verify Gate Readiness Closure Baseline

**功能编号**：`128-frontend-runtime-attachment-verify-gate-readiness-closure-baseline`
**日期**：2026-04-14

## 实施批次

1. 定义 `128` formal carrier，并把 `120/T22` 回链到新工单
2. 先写红灯测试，锁定 verify context / CLI JSON / unresolved scope fail-closed 行为
3. 扩展 `verify_constraints` 与 `verify_cmd`，让 verify/gate/readiness 共享 runtime attachment truth
4. 做 focused verification，并进入对抗评审

## 边界

- 只补 runtime attachment 在 verify/gate/readiness 汇聚面上的接线
- 不新增 execute side effects、artifact materialization 或 writeback
- freshness advisory 保持诚实暴露，但不在本批改写既有 PASS 语义
