# Development Summary：WI-197 Adapter/Preflight 顺序修复

**状态**：runtime implemented and task reviews approved，PR pending
**父项**：WI-196 `GAP-07 / T51`
**设计哈希**：`0c97361ef27901ef3d207cc1c21980e2cc9cb64c633d4c03caa1e43db74a9236`

## 当前结论

- 未改代码全量基线：`3145 passed, 3 skipped`；RED commit `b89203c4` 可信暴露 3 个顺序缺陷，既有非 RED 用例 `13 passed, 4 deselected`。
- 最小 GREEN commit `c644884e` 已按 strict Click `ctx.meta` composition 修复顺序；full suite `3149 passed, 3 skipped`。
- 兼容安全与精简效率两个本地独立 Agent 已对同一设计哈希 PASS，并对最终 strict meta 修订方案统一 PASS。
- RED 与 GREEN task reviewer 均给出 `Spec compliant + Task quality: Approved`；GREEN 无 Critical、Important 或 Minor 问题。
- 实现边界为 root → workitem group callback 委托；合法 `init` 在 clean-tree preflight 后执行 adapter，脏树/无效 `init` 零写入，合法非 `init` 子命令仍在 handler 前执行一次。
- GAP-10 只接受已冻结的 proof 持久化时序 expected delta，不修改 proof schema、校验或 blocker。
- 产品净新增 21 LOC；WI 测试累计 72 additions / 0 deletions；无新增产品文件、公共抽象、依赖或配置，最终 runtime diff 为 3 个授权文件。
- 当前 `feature/197-adapter-preflight-order` 是 PR merge carrier；异常保持原样传播，runtime rollback 为 revert `c644884e`。
- 交付准备 fresh verification：focused 三文件 `58 passed`，全量 ruff PASS，constraints 无 BLOCKER，diff-check PASS；truth audit fresh 且 inventory/blocker 集合未漂移。

## 未完成

- final whole-branch review 尚未执行。
- PR、Codex review、required checks 与 merge 尚未执行。
- main program truth 同步与 GAP-07 close 尚未执行；不得把当前 branch runtime 状态视为 mainline 已交付。
