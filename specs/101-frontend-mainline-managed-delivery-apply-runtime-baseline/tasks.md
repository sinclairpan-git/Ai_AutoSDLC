# 任务分解：Frontend Mainline Managed Delivery Apply Runtime Baseline

**编号**：`101-frontend-mainline-managed-delivery-apply-runtime-baseline` | **日期**：2026-04-12  
**来源**：plan.md + spec.md（`FR-101-001` ~ `FR-101-019` / `SC-101-001` ~ `SC-101-004`）

---

## 分批策略

```text
Batch 1: boundary reconciliation
Batch 2: apply-runtime contract freeze
Batch 3: registry sync, project-state update, verification
```

---

## 执行护栏

- `101` 只允许修改 `program-manifest.yaml`、`.ai-sdlc/project/config/project-state.yaml` 与 `specs/101/...`
- `101` 不得实现 package installer、writer、rollback executor 或 browser gate
- `101` 不得回写 `100` planner truth 或 `020` execute gate truth
- `101` 不得新增 old frontend takeover 默认路径
- `101` 不得修改 `src/`、`tests/`

---

## Batch 1：boundary reconciliation

### Task 1.1 对齐 apply runtime 承接边界

- [x] 回读 `095` 中 `managed_delivery_apply`、rollback/retry 与 partial failure 的原始要求
- [x] 回读 `100` 中 confirmed plan、confirmation surface、ledger continuity 与下游 handoff
- [x] 回读 `020` 的 execute/recheck/remediation vocabulary
- [x] 确认 `101` 只收 apply runtime，不把 planner、browser gate 或 program execute aggregation 混入本切片

**完成标准**

- 能用单一 wording 解释为什么 `101` 是 `100` 的 executor child slice，而不是新的 readiness 母规格

## Batch 2：apply-runtime contract freeze

### Task 2.1 冻结 execution session 与 executable scope

- [x] 在 `spec.md` 冻结 `DeliveryApplyDecisionReceipt`、`ManagedDeliveryExecutionSession` 与 `ManagedDeliveryApplyResult`
- [x] 在 `spec.md` 冻结 selected mutate action 的 executable scope 与 blocked-before-start 规则
- [x] 在 `spec.md` 固定 decision gate -> session bootstrap -> ledger -> action execute -> result finalize 的顺序

**完成标准**

- reviewer 能直接判断 apply runtime 在什么前提下允许启动，以及它绝不会在执行期改 plan

### Task 2.2 冻结 ledger、rollback、cleanup、retry 与 handoff

- [x] 在 `spec.md` 固定 `delivery_action_ledger` 的创建时机、写入粒度与 action-id continuity
- [x] 在 `spec.md` 冻结 failure classification、rollback/cleanup/retry 与 partial-progress honesty
- [x] 在 `spec.md` 写清 browser gate 与 `020` handoff 的最小输出面

**完成标准**

- maintainer 能直接回答为什么 apply result 只能是下游输入，而不是最终 readiness verdict

## Batch 3：registry sync, project-state update, verification

### Task 3.1 初始化 canonical docs

- [x] 创建 `spec.md / plan.md / tasks.md / task-execution-log.md`
- [x] 在 `task-execution-log.md` 记录 research、命令与结果

**完成标准**

- `101` 能独立说明 apply runtime、ledger、rollback/cleanup/retry 与 `020` handoff 边界

### Task 3.2 同步 manifest 与 project-state

- [x] 在 `program-manifest.yaml` 增加 `101` canonical entry 与 `frontend_evidence_class` mirror
- [x] 在 `.ai-sdlc/project/config/project-state.yaml` 将 `next_work_item_seq` 从 `101` 推进到 `102`

**完成标准**

- `101` 已进入 program registry，下一工作项序号与本轮 baseline 对齐

### Task 3.3 运行验证

- [x] 运行 `uv run ai-sdlc verify constraints`
- [x] 运行 `uv run ai-sdlc program validate`
- [x] 运行 `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline`

**完成标准**

- 本轮 diff 保持 docs-only apply-runtime 边界且 fresh verification 通过
