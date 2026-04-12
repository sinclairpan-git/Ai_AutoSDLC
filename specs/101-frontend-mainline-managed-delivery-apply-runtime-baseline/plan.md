# 执行计划：Frontend Mainline Managed Delivery Apply Runtime Baseline

**功能编号**：`101-frontend-mainline-managed-delivery-apply-runtime-baseline`  
**创建日期**：2026-04-12  
**状态**：docs-only apply runtime contract freeze  
**对应规格**：[`spec.md`](./spec.md)

## 1. 目标与定位

`101` 的目标不是实现 executor，而是把 `100` 下游的 apply runtime 先冻结成正式合同：

- 冻结 decision receipt、execution session 与 executable scope；
- 冻结 `delivery_action_ledger` 的创建时机、写入粒度与 action-id continuity；
- 冻结 rollback / cleanup / retry / partial-progress 的运行时边界；
- 冻结 `ManagedDeliveryApplyResult` 到 browser gate 与 `020` 的 handoff 面；
- 保持 browser quality gate 与 program execute aggregation 继续在后续切片独立演进。

## 2. 范围

### 2.1 In Scope

- 创建 `101` formal docs 与 execution log
- 推进 `.ai-sdlc/project/config/project-state.yaml` 到 `102`
- 在 `program-manifest.yaml` 为 `101` 增加 canonical registry entry 与 `frontend_evidence_class` mirror
- 冻结 confirmed plan 到 execution session / ledger / apply result 的链路
- 冻结 rollback、cleanup、retry、partial-progress 与 `020` handoff

### 2.2 Out Of Scope

- 修改 `src/` / `tests/`
- 实现 package installer、writer、rollback executor 或 browser gate
- 改写 `100` planner truth、`020` execute gate truth 或更早上游 truth
- 直接产出最终 program-level readiness `ready`
- 放宽 `new_controlled_subtree` 默认 managed target 边界

## 3. 变更文件面

当前批次只允许改以下文件面：

- `program-manifest.yaml`
- `.ai-sdlc/project/config/project-state.yaml`
- `specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`
- `specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/plan.md`
- `specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/tasks.md`
- `specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/task-execution-log.md`

## 4. Contract Freeze Rules

### 4.1 Runtime boundary

- `101` 只能消费已确认的 `100` 产物，不得回到 planner 修改 action plan
- 只有 selected `mutate` action 才能进入 executable scope
- apply runtime 不得隐式新增 root-level integration 或旧工程 takeover 动作

### 4.2 Ledger and recovery boundary

- `delivery_action_ledger` 必须先于第一个 mutate action 创建
- rollback / cleanup / retry 都必须继续围绕同一组 `action_id`
- `non_rollbackable_effect` 与 `manual_recovery_required` 不得被自动抹平
- partial progress 必须诚实保留

### 4.3 Handoff boundary

- `ManagedDeliveryApplyResult` 只做 browser gate 与 `020` handoff
- `101` 不得直接产出 browser verdict 或最终 execute gate
- `101` 不得把 remediation hint 伪装成 auto-fix

## 5. 分阶段计划

### Phase 0：boundary reconciliation

- 回读 `095` 对 `managed_delivery_apply` 的主线顺序要求
- 回读 `100` 的 plan/confirmation/ledger continuity 与下游 handoff
- 回读 `020` 的 execute/recheck/remediation vocabulary

### Phase 1：formal apply runtime freeze

- 在 `spec.md` 冻结 decision receipt、execution session 与 apply result
- 在 `spec.md` 冻结 executable scope、ledger 写入、rollback/cleanup/retry 与 failure 分类
- 在 `spec.md` 写清 browser gate 与 `020` 的下游交接边界

### Phase 2：registry sync and verification

- 创建 `task-execution-log.md`
- 记录 research inputs、touched files、验证命令与结果
- fresh 运行 `verify constraints`、`program validate` 与 diff hygiene

## 6. 最小验证策略

- `uv run ai-sdlc verify constraints`
- `uv run ai-sdlc program validate`
- `git diff --check -- program-manifest.yaml .ai-sdlc/project/config/project-state.yaml specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline`

## 7. 回滚原则

- 如果 `101` 让人误以为 planner、browser gate 或 `020` execute gate 已在本切片实现，必须回退
- 如果 `101` 允许执行器在 apply 期偷偷新增 plan 外动作，必须回退
- 如果 `101` 把 partial failure、cleanup 或 manual recovery 压成统一成功结论，必须回退
- 如果本轮误改 `src/`、`tests/` 或既有上游 spec，必须回退
