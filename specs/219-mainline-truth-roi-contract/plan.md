# 实施计划：主线真值复位与轻量 ROI 合同

**编号**：`219-mainline-truth-roi-contract`
**状态**：等待用户审阅 `spec.md`
**规格**：`specs/219-mainline-truth-roi-contract/spec.md`

## 当前授权边界

当前只授权 formal 规格冻结、基线取证、Program Truth 映射、对应 root inventory tuple 的机械断言和
continuity 更新。尚未授权产品模板、特性回归测试或运行时实现。详细实施计划必须在用户审阅并批准
`spec.md` 后生成。

## 已冻结推荐方案

采用规格 §3 的方案 B：保留现有 link/handoff/reconcile 写入合同，以一个共享纯解析 helper 统一 resume、
readiness/status 和 execute authorization 的 linked-first active binding，并以两份现有 spec 模板承载轻量
ROI 提示。不得建立 ROI/Lean 运行时、额外工件或 close 门禁。

## 计划生成条件

用户批准规格后，下一步必须使用正式 planning 流程，逐项冻结：

1. Track A 的历史 feature + 新 linked WI characterization RED、共享纯解析 helper 和三个消费方最小 GREEN；
2. Track A 的真实 CLI link→status 闭环、无 linked/linked missing 兼容回归和前后对账命令；
3. Track B 的模板 RED/GREEN 测试与精确文件范围；
4. focused/full verification、回退和两轮评审边界。

批准前不得新增实现任务或修改规格 §4 允许范围内的产品/测试文件。
