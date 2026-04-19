# 任务分解：Frontend Solution Confirm Continue Apply Orchestration Baseline

**编号**：`165-frontend-solution-confirm-continue-apply-orchestration-baseline` | **日期**：2026-04-19

## T1：组合流红测

- [x] 为 `solution-confirm --execute --continue` 补 success / ack-required / registry-blocked 三条集成测试
- [x] 为 apply request builder 补 `second_confirmation_missing` 单测
- [x] 为 truth-derived `managed-delivery-apply --execute` 补 ack-required / ack-success 集成测试

## T2：CLI / service 编排

- [x] 为 `solution-confirm` 增加 `--continue`
- [x] 为 `solution-confirm` 增加 `--ack-effective-change`
- [x] 在 `ProgramService` 中增加受控的 `second_confirmation_acknowledged` 入参
- [x] 复用现有 apply request / result / artifact 渲染逻辑，不重写 executor
- [x] 让 truth-derived `managed-delivery-apply` 入口继承同样的 effective-change 二次确认门槛

## T3：formal truth

- [x] 新增 `165` spec/plan/tasks
- [x] 明确记录 `adapter_packages` 继续为空的边界决策

## T4：验证

- [x] 运行 focused unit / integration tests
- [x] 汇总结果与剩余风险
