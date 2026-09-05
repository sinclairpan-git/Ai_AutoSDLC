# 开发摘要：Requirement Loop 有界动态专家评审纵向薄片

**功能编号**：`228-requirement-bounded-dynamic-expert-review`
**状态**：implementation GO；terminal exact-head gates 待完成

## 交付结果

- 为 Requirement Loop 增加只读 `review` 入口：输出 canonical requirement projection、SHA-256 digest、固定主审角色和至多一个确定性风险角色。
- 新 requirement 默认要求完整临时 execution；旧 artifact 保持兼容并提示。missing/malformed/stale/failed/incomplete/duplicate/unknown execution 在 writer adapter 前拒绝。
- actionable execution 只允许一次 round 1→2 修订；freeze 只接受当前 clean execution 并关闭实际 current round。review/execution/finding 不作为 Loop artifact 持久化。
- 实现复用现有 `LoopRun/LoopRound` 和 freeze writer；无新依赖、workflow、状态机、ledger、provider registry 或第二类 Loop。产品 gross additions 为 `595/600`，未越过 formal 7 文件 allowlist。

## 价值与安全证据

- 三例真实 CLI 匿名盲测中，A 安全/权限与 B 数据迁移各产生经独立裁决的有效增量 finding；全新随机 ID、全新 reviewer 的 C 纯函数 clean 负向对照无 finding；合计 `valid_incremental=6,false_actionable=0`。所有不合格 clean 候选均按真实 finding 或 clarification 作废并留痕，没有改判。
- A/B 都只修订一次并在 round 2 由原两个角色返回 clean；C 在 round 1 直接 clean。终态均 closed，三例 Loop 内持久化 execution/finding 文件计数为 0。
- review 前后完整隐藏目录文件集合与逐文件 SHA-256 一致；被拒 execution 的 start/freeze 由 CLI integration 覆盖 adapter 零调用与整树零变化。

## 验证

- 唯一聚焦整改后的定向回归：`101 passed`；扩大相邻回归：`407 passed`。
- 唯一整改后的最终全量：`3486 passed, 3 skipped in 1019.87s`。
- Ruff、constraints、program validate、plan-check 和 `git diff --check` 通过；Program Truth inventory 为 `1190/1190/0/7`、close `219/226`，manifest regression 为 `1 passed`。final truth、close-check、双专家 exact-head 与 GitHub PR gates 在 terminal content 完整后串行执行。

## 终止边界

本项 GO 只关闭 Requirement 纵向薄片。它不启动通用五 Loop kernel，不创建新的减重任务，也不自动推进 Design Contract、Implementation、Frontend Evidence 或 Local PR Review；后续能力必须回到正常特性优先级并独立证明 ROI。
