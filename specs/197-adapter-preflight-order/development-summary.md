# Development Summary：WI-197 Adapter/Preflight 顺序修复

**状态**：PR review finding fixed，fresh verification passed，final branch reviews pending
**父项**：WI-196 `GAP-07 / T51`
**设计哈希**：`7627839c93ba3c227790a9df57b288baaef32a5368790e7d3746c2c2ad356633`

## 当前结论

- 未改代码全量基线：`3145 passed, 3 skipped`；RED commit `b89203c4` 可信暴露 3 个顺序缺陷，既有非 RED 用例 `13 passed, 4 deselected`。
- 首个 GREEN commit `c644884e` 按 strict Click `ctx.meta` composition 修复顺序；PR Codex review 随后发现 duplicate canonical docs 仍在 adapter 后拒绝。
- remediation RED `4c7b35a3` 精确证明第二次 duplicate init 会再次调用 adapter；最小 GREEN `3940723e` 把既有 duplicate validation 前移到 preview，并用 module-private canonical 名称清单供 preview/scaffold 复用。
- 兼容安全与精简效率两个本地独立 Agent 已对最新同一设计哈希 PASS；RED 与 GREEN task reviewer 均给出 `Spec compliant: Yes / Task quality: Approved`，无 Critical、Important 或 Minor 问题。
- 实现边界为 root → workitem group callback 委托；合法 `init` 在 duplicate-target validation 与 clean-tree preflight 后执行 adapter，脏树/重复目标/其他无效 `init` 零 adapter 写入，合法非 `init` 子命令仍在 handler 前执行一次。
- GAP-10 只接受已冻结的 proof 持久化时序 expected delta，不修改 proof schema、校验或 blocker。
- 产品代码累计 numstat 为 `main.py +5/-1`、`workitem_cmd.py +17/-0`、`workitem_scaffold.py +10/-12`，合计 `+32/-13 = net +19 LOC`；WI 测试累计 `+80/-5`；无新增产品文件、公共抽象、依赖或配置，最终 runtime/test diff 为 4 个授权文件。
- 当前 `feature/197-adapter-preflight-order` 是 PR merge carrier；duplicate 错误文本与 `WorkitemScaffoldError`→exit 1 映射不变；adapter 非 special-case 异常与 strict-meta composition 异常继续传播，本变更未新增异常吞没或映射；runtime rollback 依次 revert `3940723e` 与 `c644884e`。
- remediation fresh verification：三个 focused 文件 `26 passed`；full suite `3149 passed, 3 skipped`；全量 ruff PASS，constraints 无 BLOCKER，diff-check PASS；truth audit snapshot fresh，inventory/blocker 集合未漂移。

## 未完成

- remediation 后的兼容安全与精简效率 final whole-branch reviews 尚未完成。
- PR `#121` 已存在；remediation 提交尚未推送，Codex re-review 与新 HEAD required checks 尚未执行。
- main program truth 同步与 GAP-07 close 尚未执行；不得把当前 branch runtime 状态视为 mainline 已交付。
