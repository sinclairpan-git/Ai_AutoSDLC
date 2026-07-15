# Development Summary：WI-203 Finalization Command Family Reduction Contract

**状态**：formal 已由 PR #126 合入 mainline，sponsor receipt 已形成；candidate 实现未授权，工作项未关闭
**父项**：WI-196 `WP-07 / GAP-04`
**当前 formal hash**：`cfcd63d7662175e8e9d413b831e582ee81d00958cb8d9c3c8c717de0987dc57f`

## 当前结论

- 已冻结 9 个 `program` finalization handler 的候选边界、兼容合同、预算、T61A/T61B、
  分阶段迁移、稳定版删除和真实回滚要求。
- Round 7 已由兼容安全与精简效率两个独立 Agent 对同一 formal hash 完成复审，均为 `PASS`；
  Round 1～6 只保留为已失效审计历史。
- Formal PR #126 已以 merge `75d3dda5ec8b45d0f9441058da889163d814b717` 形成不可变 sponsor
  receipt；它不包含 `src/`、runtime rule、发布配置或 candidate 实现，也不授权删除 legacy。
- Sponsor 只有进入 `settled` 才能关闭；candidate 取消、停滞、被替代、No-Go、基线或范围变化、
  receipt 被 revert 时必须撤销或缩小 WI-202 claim。
- 本文件只物化 WI-203 已登记的 close-layer source，证明 formal 设计交付状态；不得被解释为
  candidate 已实现、稳定版已发布或工作项已关闭。
- 旧 WI-202 的 ≤170 allocation 已因 T62A RC-09 No-Go 撤销；该 allocation 从未激活 claim、未消费
  unique key，effective claim=0，且不得复活、转给新 T62A 或与 candidate 未用预算合并。
- WI-203 candidate 的 ≤180 allocation 与旧 WI-202 独立；当前没有 candidate claim，effective
  claim=0。它只能由新的独立 candidate 合同按原 sponsor 生命周期激活，不能扩大 T62A 预算；
  reserve=3 继续不可 claim。

## 待完成

1. 不再恢复 WI-202；T62A 重启必须使用新工作项，同时取得新的/替代 sponsor 与父合同同哈希
   双 PASS，旧 allocation 不能作为重启依据。
2. 后续独立 WP-07 candidate 若启动，必须在 ≤180 的独立 envelope 内重新登记 owner、baseline、
   handoff 与 actual claim，依次完成 T61A、候选迁移、T61B、稳定发布、独立 legacy 删除和 rollback
   rehearsal。
3. WI-203 只有 candidate/deletion/rollback 与 actual LOC settlement 全部完成并进入 `settled` 后
   才能关闭；当前 receipt 存在不等于 reduction 已完成。
