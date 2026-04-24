# 开发摘要：V0.7.0 Windows 离线 E2E 修复基线

**功能编号**：`179-v0-7-0-windows-offline-e2e-remediation-baseline`
**当前状态**：正式拆分完成，尚未进入代码实现

## 当前完成

- 将缺陷归档转成正式 `spec.md`
- 补充 design 阶段 `research.md` 和 `data-model.md`
- 补充 `plan.md` 与 `tasks.md`
- 建立 `task-execution-log.md`

## 下一步

从 `tasks.md` 的 Batch 1 开始实现：

1. T179-01 跨平台包管理器命令解析
2. T179-02 前端依赖模式与 mutate 前 preflight
3. T179-03 失败 artifact 和下游阻断合同
4. T179-04 Windows release asset P0 smoke

## 当前风险

- adapter 仍缺少 machine-verifiable activation evidence。
- 本 work item 涉及运行时、CLI、telemetry、release docs 和 E2E，多批次推进时必须避免一次性大改。
