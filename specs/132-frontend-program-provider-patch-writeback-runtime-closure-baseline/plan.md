# 实施计划：Frontend Program Provider, Patch Apply And Cross-Spec Writeback Runtime Closure Baseline

**功能编号**：`132-frontend-program-provider-patch-writeback-runtime-closure-baseline`
**日期**：2026-04-14

## 实施批次

1. 核对 `025-031` formal 约束与现有 deferred baseline 的真实缺口
2. 通过 TDD 将 provider runtime、patch apply、cross-spec writeback 从 `deferred` 推进到真实执行链
3. 定义 `132` formal carrier，并把 `120/T32` 回链到新工单
4. 运行 focused verification 与对抗评审，固定这条 closure slice 的现状

## 边界

- 本批不引入 registry/governance/persistence 主线
- 本批只关闭 `025-031` 的 provider/apply/writeback runtime 缺口
- 后续 `T33` 继续承接 registry、broader/final governance 与 persisted truth
