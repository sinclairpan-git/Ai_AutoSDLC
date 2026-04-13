# 实施计划：Frontend Mainline Delivery Materialization Runtime Baseline

**功能编号**：`124-frontend-mainline-delivery-materialization-runtime-baseline`
**日期**：2026-04-14

## 实施批次

1. 定义 `124` formal carrier，并把 `120/T12` 回链到新工单
2. 先写红灯测试，锁定 `dependency_install` payload、`artifact_generate` boundary 与 preflight/execute 分流
3. 扩展 managed delivery runtime model / executor / service wiring
4. 做 focused verification，并准备后续对抗评审

## 边界

- 只补 `dependency_install` 与 `artifact_generate`
- 只允许 managed target 子树写入
- 不碰 browser gate、workspace takeover、root integration
