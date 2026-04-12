# 任务分解：Frontend Mainline Action Plan Binding Baseline

**编号**：`100-frontend-mainline-action-plan-binding-baseline` | **日期**：2026-04-12  
**来源**：plan.md + spec.md（`FR-100-001` ~ `FR-100-020` / `SC-100-001` ~ `SC-100-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: action-plan-binding contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `100` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/100/...`
- `100` 不得实现 apply runtime、installer、writer、rollback executor 或 browser gate
- `100` 不得复制 `096`、`098`、`099` 的上游 truth
- `100` 不得新增 old frontend takeover 默认路径
- `100` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 Managed Action Engine 承接边界

- [x] 回读 `095` 中 `frontend_action_plan`、`delivery_execution_confirmation_surface`、`delivery_action_ledger` 的要求
- [x] 回读 `096`、`098`、`099` 的 handoff boundary
- [x] 确认 `100` 只收 action-plan binding，不把 resolver runtime、apply runtime 或 browser gate 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `100` 是 `Managed Action Engine` 的 formal baseline，而不是新的总线母规格

## Batch 2：action-plan-binding contract freeze

### Task 2.1 冻结 action plan 输入与 truth order

- [x] 在 `spec.md` 冻结 ActionBindingContext 与 LocalDetectionEvidence
- [x] 在 `spec.md` 冻结 activation -> solution -> posture/target -> runtime -> bundle -> local evidence -> confirmation 的绑定顺序
- [x] 在 `spec.md` 固定 `frontend_action_plan` 的 action family、requiredness 与 `will_* / will_not_touch` 语义

**完成标准**

- reviewer 能直接判断任一 action item 来自哪些上游 truth 与本地 evidence

### Task 2.2 冻结 confirmation surface 与 ledger continuity

- [x] 在 `spec.md` 固定 `delivery_execution_confirmation_surface` 的最小展示面与二次确认规则
- [x] 在 `spec.md` 冻结 `delivery_action_ledger` 的 action-id continuity、rollback、retry 与 partial-progress 语义
- [x] 在 `spec.md` 写清 blocked/fail-closed 与 downstream executor/browser gate handoff

**完成标准**

- maintainer 能直接回答为什么确认页、ledger 与 action id 必须是一条链，而不是三个分离概念

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `100` 能独立说明 action binding、requiredness、confirmation、ledger 与 no-touch 边界

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `100` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `100` 推进到 `101`

**完成标准**

- `100` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/100-frontend-mainline-action-plan-binding-baseline`

**完成标准**

- 本轮 diff 保持 docs-only action-plan-binding 边界且 fresh verification 通过
