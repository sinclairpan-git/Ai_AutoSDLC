# 任务清单：Frontend P1 Governance Diagnostics Drift Baseline

**功能编号**：`069-frontend-p1-governance-diagnostics-drift-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（docs-only formal baseline）

## 任务总览

- [x] Batch 1：冻结 positioning / truth-order / non-goals
- [x] Batch 2：冻结 P1 diagnostics coverage matrix
- [x] Batch 3：冻结 drift / gap / compatibility feedback boundary
- [x] Batch 4：归档 execution log、推进 `project-state` 并完成 docs-only 门禁

## 执行护栏

- 当前 work item 只允许 docs-only formal freeze；不得进入 `src/` / `tests/`。
- 当前 work item 不得改写 `017` generation truth、`018` gate / report family truth、`067/068` kernel / recipe truth。
- 当前 work item 不得抢跑 `070` recheck / remediation feedback、`071` visual / a11y、provider/runtime 实现或 root program sync。
- 当前 work item 不得把 sample source self-check 写成隐式 observation fallback；diagnostics 必须继续要求显式 artifact 输入。
- 当前 work item 不得生成 `development-summary.md`，也不得宣称 close-ready 或已实现。
- 只有在 `069` docs-only 门禁通过且用户明确要求继续时，才允许进入实现批次或 formalize 下游 child。

## Batch 1：冻结 positioning / truth-order / non-goals

### Task 1.1 冻结 `069` 的 child 定位

- [x] 在 `spec.md` 明确 `069` 是 `066` 下游第三条 child work item
- [x] 在 `spec.md` 明确 `069` 位于 `067/068` 之后、`070/071` 之前
- [x] 在 `spec.md` 明确 `069` 不是 recheck / remediation、visual / a11y、provider/runtime 工单

**完成标准**

- `spec.md` 能独立表达 `069 != 067 != 068 != 070 != 071`

### Task 1.2 冻结 diagnostics truth-order

- [x] 在 `spec.md` 明确 `069` 只能消费 `067 + 068 + 017 + 018 + 065`
- [x] 在 `plan.md` 明确 diagnostics 不得反向重写 kernel / recipe / generation / gate baseline
- [x] 在 `tasks.md` 明确当前工单禁止跨层写入

**完成标准**

- reviewer 可直接从 formal docs 读出 `Contract -> Kernel -> Provider/Code -> Gate` 顺序未变化

## Batch 2：冻结 P1 diagnostics coverage matrix

### Task 2.1 冻结 semantic component / recipe / state coverage

- [x] 在 `spec.md` 给出 semantic component coverage 的最小覆盖对象
- [x] 在 `spec.md` 给出 recipe coverage 与 area constraint 的消费边界
- [x] 在 `spec.md` 给出 state coverage 与 `015` MVP 状态基线的共存关系

**完成标准**

- 文档明确 `Ui*`、recipe、state 三类 coverage 面如何消费上游 truths

### Task 2.2 冻结 whitelist / token coverage 扩张边界

- [x] 在 `spec.md` 明确 whitelist coverage 仍服从 `017` whitelist ref truth
- [x] 在 `spec.md` 明确 token coverage 仍服从 `017` minimal token / naked-value truth
- [x] 在 `spec.md` 明确 P1 只扩结构场景覆盖，不升级为完整 token 平台

**完成标准**

- 文档明确 diagnostics 扩张的是覆盖面，不是 generation constraint schema 重写

## Batch 3：冻结 drift / gap / compatibility feedback boundary

### Task 3.1 冻结 gap / empty / drift 分类

- [x] 在 `spec.md` 明确 `input gap / stable empty observation / drift` 的区分
- [x] 在 `spec.md` 明确 `recipe structure drift / state expectation drift / whitelist leakage / token leakage` 的最小分类
- [x] 在 `plan.md` 明确 `065` sample self-check 只作为显式输入源

**完成标准**

- 文档明确缺输入、空输入与真实漂移不会混淆

### Task 3.2 冻结 compatibility feedback honesty

- [x] 在 `spec.md` 明确 compatibility 仍是同一套 gate matrix 的兼容执行口径
- [x] 在 `spec.md` 明确 diagnostics 复用 `018` 的 report family，不新增第二套 report schema
- [x] 在 `tasks.md` 明确当前工单不新增新的执行模式或第二套规则系统

**完成标准**

- reviewer 可直接读出 `Compatibility != second gate system`

### Task 3.3 冻结 downstream handoff

- [x] 在 `spec.md` 明确 `070` 承接 recheck / remediation feedback
- [x] 在 `spec.md` 明确 `071` 承接 visual / a11y foundation
- [x] 在 `plan.md` 明确当前批次只冻结 diagnostics baseline，不进入下游 formalize

**完成标准**

- 文档明确 diagnostics 之后的两条 child 轨道如何消费 `069`

## Batch 4：归档 execution log、推进 `project-state` 并完成 docs-only 门禁

### Task 4.1 初始化 canonical docs 与 execution log

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 写入当前边界、批次范围与状态归档
- [x] 在 `project-state.yaml` 将 `next_work_item_seq` 从 `69` 推进到 `70`

**完成标准**

- 目录结构完整，且当前状态诚实表达为 docs-only formal baseline freeze 已完成

### Task 4.2 运行 docs-only 门禁

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `git diff --check`
- [x] 在 `task-execution-log.md` 记录 touched files、命令与结果

**完成标准**

- `verify constraints` 无 blocker
- `git diff --check` 无输出

## 完成定义

- `069` formal docs 可独立表达 diagnostics / drift expansion 的 scope、coverage matrix、classification 与 handoff boundary
- `069` 不被误读成 recheck / visual / provider 实现工单
- docs-only 门禁通过，且状态诚实表达为“formal freeze 已完成并 accepted（accepted child baseline）”
- 文中出现的下游 `070/071` 编号仅作当前 planning 占位；真实编号以后续 scaffold 时的 `project-state` 为准
