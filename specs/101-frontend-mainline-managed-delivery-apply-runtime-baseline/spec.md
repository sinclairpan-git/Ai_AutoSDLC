# 功能规格：Frontend Mainline Managed Delivery Apply Runtime Baseline

**功能编号**：`101-frontend-mainline-managed-delivery-apply-runtime-baseline`  
**创建日期**：2026-04-12  
**状态**：formal baseline 已冻结；作为 `095` 的 `Managed Action Engine` 第二正式切片  
**输入**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../098-frontend-mainline-posture-detector-baseline/spec.md`](../098-frontend-mainline-posture-detector-baseline/spec.md)、[`../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md`](../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)

> 口径：`101` 冻结的不是 action planner、不是 browser quality gate、也不是 program execute gate，而是 `100` 下游的 apply runtime 本身。它只回答五个问题：确认后的 `frontend_action_plan` 如何被转成唯一执行会话；哪些 action 真正可执行、按什么顺序执行、怎样把结果写进 `delivery_action_ledger`；失败后 rollback / cleanup / retry 如何继续服从 `100` 已冻结的 action id 与 risk boundary；partial progress 与 manual recovery 怎样被诚实暴露；以及 apply runtime 的结果怎样交给后续 browser gate 与 `020` readiness handoff，而不是在本层偷发最终“ready”结论。

## 问题定义

`100` 已经把 action plan、确认页与 ledger continuity 冻结出来，但链路中还缺最后一段关键合同：**确认页上的动作，如何真正按 machine truth 执行，而不是退回临时脚本或隐式 shell 操作**。

当前仓库对这层 still missing 的风险很集中：

- `frontend_action_plan` 与执行器之间还没有正式的 input/output 合同，容易在执行时临时新增动作、修改顺序或跳过 required action
- `delivery_action_ledger` 已有 formal 字段面，但没有 apply runtime contract 去规定何时创建、何时更新、何时允许 rollback/retry
- `partial failure`、`non_rollbackable_effect`、`manual_recovery_required` 如果不先冻结执行语义，后续实现很容易把失败统一压成“执行失败”
- `020` 只允许消费按 spec 粒度的 frontend readiness / recheck / remediation handoff；如果 apply runtime 不先提供单一结果面，后续很容易把执行日志、browser 证据与 program execute gate 混在一起

因此，`101` 的目标是把 confirmed plan 的 apply runtime 固定成一个最小但严格的执行基线：先冻结 decision receipt、execution session、ledger write、rollback/cleanup/retry 与 apply result handoff，再把 browser quality gate 与 program execute aggregation 继续留在下游切片。

## 范围

- **覆盖**：
  - 已确认 `frontend_action_plan` 的 execution prerequisites、启动条件与执行会话模型
  - `mutate` action 的 executable scope、依赖顺序、before/after state 与 ledger 写入规则
  - rollback / cleanup / retry 的 runtime boundary 与 partial-progress 语义
  - `ManagedDeliveryApplyResult` 到 browser gate / `020` readiness handoff 的最小输出面
  - `101` 与 `100 / 020` 的单向交接边界
- **不覆盖**：
  - 重新生成或改写 `frontend_action_plan`
  - 在本 work item 中实现 package installer、template writer、rollback executor 或 browser gate runtime
  - 重新定义 `020` 的 execute gate、`073` 的 solution truth、`096` 的 runtime truth、`098` 的 posture truth、`099` 的 delivery bundle truth
  - 在 apply runtime 层自动接管旧 frontend 根或放宽 `new_controlled_subtree` 默认边界
  - 在 apply runtime 层直接产出最终 program-level `frontend_readiness = ready`

## 已锁定决策

- `101` 只能消费 `100` 已确认的 `frontend_action_plan`、`delivery_execution_confirmation_surface` 与显式用户决策回执；不得回到 planning 阶段改 plan。
- 只有 `effect_kind = mutate` 且在决策回执中被选中的 action 才能进入 apply runtime；`observe / plan` action 只保留为 source linkage。
- `delivery_action_ledger` 必须在第一个 mutate action 执行前创建，并继续沿用 `100.action_items[].action_id` 作为唯一执行索引。
- executor 不得新增未在 plan 中出现的隐藏动作；任何 root-level integration 仍然必须服从 `100` 已冻结的 optional/default-selected 规则。
- `rollback`、`cleanup`、`retry` 都必须围绕同一组 `action_id` 运转；不得通过“重新规划一份新 plan”来伪装 retry。
- 含 `non_rollbackable_effect` 或 `manual_recovery_required` 的 action，即使执行器已经开始，也不得自动宣称“已恢复”；必须落到结构化结果面。
- `101` 产出的 apply result 只能作为 browser gate 与 `020` recheck/remediation handoff 的输入；它本身不是最终 readiness gate。

## Apply Runtime Inputs

### 1. DeliveryApplyDecisionReceipt

`DeliveryApplyDecisionReceipt` 是 apply runtime 的唯一用户决策入口。

其最小字段至少包括：

- `decision_receipt_id`
- `action_plan_id`
- `confirmation_surface_id`
- `decision`
  - `continue`
  - `cancel`
  - `return_to_solution`
  - `return_to_action_plan`
- `selected_action_ids`
- `deselected_optional_action_ids`
- `risk_acknowledgement_ids`
- `second_confirmation_acknowledged`
- `created_at`

规则：

- 只有 `decision = continue` 时，executor 才能进入启动流程
- 当 `confirmation_surface.second_confirmation_required = true` 时，`second_confirmation_acknowledged` 不为真则不得启动
- `selected_action_ids` 必须是 `100.frontend_action_plan.action_items[].action_id` 的子集

### 2. ManagedDeliveryExecutionSession

`ManagedDeliveryExecutionSession` 是 apply runtime 的唯一会话真值。

其最小字段至少包括：

- `execution_session_id`
- `action_plan_id`
- `confirmation_surface_id`
- `decision_receipt_id`
- `ledger_id`
- `managed_target_ref`
- `attachment_scope_ref`
- `readiness_subject_id`
- `spec_dir`
- `execution_mode`
  - `apply`
  - `retry_failed_action`
  - `rollback_requested`
  - `cleanup_requested`
- `status`
  - `pending_start`
  - `running`
  - `rollback_running`
  - `cleanup_running`
  - `retry_pending`
  - `manual_recovery_required`
  - `succeeded`
  - `failed`
  - `blocked`
  - `cancelled`
- `current_action_id`
- `started_at`
- `updated_at`
- `finished_at`
- `blocking_reason_codes`

规则：

- 一个已确认的 action plan 在任一时刻只能有一个 active apply session
- `managed_target_ref` 必须继续对齐 `100.managed_target_ref`
- `attachment_scope_ref / readiness_subject_id / spec_dir` 用于后续 browser gate 与 `020` handoff 的 source linkage，不得在执行后临时猜测补写

### 3. ManagedDeliveryApplyResult

`ManagedDeliveryApplyResult` 是 apply runtime 对下游暴露的唯一执行结果面。

其最小字段至少包括：

- `apply_result_id`
- `execution_session_id`
- `action_plan_id`
- `ledger_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `readiness_subject_id`
- `result_status`
  - `apply_succeeded_pending_browser_gate`
  - `apply_partial_failure`
  - `rollback_completed`
  - `rollback_failed`
  - `manual_recovery_required`
  - `blocked_before_start`
  - `cancelled`
- `executed_action_ids`
- `succeeded_action_ids`
- `failed_action_ids`
- `rolled_back_action_ids`
- `skipped_action_ids`
- `cleanup_required_action_ids`
- `recheck_required`
- `browser_gate_required`
- `blockers`
- `remediation_hints`
- `source_linkage_refs`

规则：

- `ManagedDeliveryApplyResult` 可以表达“已执行成功但仍待 browser gate”，但不得直接宣称最终 readiness 已通过
- `recheck_required` 与 `remediation_hints` 必须使用 `020` 可消费的 execute/recheck vocabulary，不得在本层自造 program 私有 verdict

## Runtime Truth Order

apply runtime 的顺序固定如下：

1. **Decision gate first**
   - 校验 `action_plan.status = confirmed_for_execution`
   - 校验 `confirmation_surface.status = decision_captured`
   - 校验存在合法 `DeliveryApplyDecisionReceipt`
2. **Session bootstrap second**
   - 创建 `ManagedDeliveryExecutionSession`
   - 锁定 `managed_target_ref / attachment_scope_ref / readiness_subject_id / spec_dir`
   - 创建空的 `delivery_action_ledger`
3. **Executable scope freeze third**
   - 从 `selected_action_ids` 中筛出 `effect_kind = mutate` 的 action
   - 将 `deselected_optional_action_ids` 标记为 skipped，但不得丢失其 source linkage
4. **Action execution fourth**
   - 按 `depends_on_action_ids` 做拓扑排序
   - 每个 action 都必须在执行前写 `before_state`，执行后写 `after_state + result_status`
5. **Failure classification fifth**
   - 区分 `retryable failure / rollbackable failure / non_rollbackable failure / manual recovery required / blocked before start`
6. **Rollback, cleanup, retry sixth**
   - rollback 只针对已成功执行且存在 `rollback_ref` 的 action
   - cleanup 只针对无法严格回滚的外部副作用
   - retry 只针对被标记为 retryable 的 action，且必须保留原 action id
7. **Result finalization last**
   - 生成 `ManagedDeliveryApplyResult`
   - 把结果交给 browser gate 与 `020` 下游 handoff

优先级护栏：

- executor 不得因为某个 action 执行失败，就回到 planner 重新生成另一份 plan
- executor 不得因为旧工程中存在可写对象，就扩大 `managed_target_ref`
- executor 不得把 browser gate evidence、program execute gate 或 auto-fix 逻辑直接并入 apply runtime

## Execution Semantics

### 1. Executable action selection

v1 的 executable scope 规则固定如下：

- 只有 `selected_action_ids` 中的 `mutate` action 可以执行
- `observe / plan` action 不进入 mutate runtime，但必须保留为 source linkage 与审计背景
- `required` action 一旦未被选中，session 必须直接 `blocked_before_start`
- `optional` 且未被选中的 action 必须进入 `skipped_action_ids`

### 2. Ordering and atomicity boundary

- executor 必须按 `depends_on_action_ids` 保证依赖顺序
- 对同一 managed target 的写操作，不得越过未完成的前置 required action
- 每个 action 的 ledger 记录必须至少包含：启动前 `before_state`、执行后 `after_state`、结果状态、错误码、rollback/retry/cleanup ref
- apply runtime 可以在 action 内部使用局部原子写策略，但不得把多个 action 合并成一个不可分解的黑盒步骤

### 3. Failure handling

执行失败至少必须被分成五类：

- `blocked_before_start`
- `retryable_failure`
- `rollbackable_failure`
- `non_rollbackable_failure`
- `manual_recovery_required`

规则：

- `retryable_failure` 只能进入 `retry_pending`，不得伪装成自动成功
- `rollbackable_failure` 可以触发 whole-plan rollback 或 action-scoped rollback
- `non_rollbackable_failure` 必须保留 `cleanup_required_action_ids`
- `manual_recovery_required` 必须中止自动流程并暴露恢复路径

### 4. Rollback, cleanup, retry

- whole-plan rollback 必须按照已成功 action 的反向依赖顺序执行
- per-action retry 必须沿用同一 `action_id`，并保留之前失败记录
- cleanup 只能补偿无法严格回滚的外部副作用；cleanup 完成不等于主计划成功
- rollback 或 cleanup 过程中再失败时，apply result 必须诚实标记 `rollback_failed` 或 `manual_recovery_required`

### 5. Partial progress honesty

- 一旦任何 action 已成功写入结果，apply runtime 就不得把整个会话压扁成“未执行”
- `executed_action_ids / succeeded_action_ids / failed_action_ids / rolled_back_action_ids / skipped_action_ids` 必须始终可重放
- 失败后的 remediation hint 必须绑定具体 action，而不是只给抽象建议

## Ledger Rules

`delivery_action_ledger` 在 apply runtime 中必须满足：

- 创建时机：第一个 mutate action 执行前
- 写入粒度：每个 action 一次结构化更新；不得只在会话结束时补总结果
- action continuity：ledger 里的 action id 必须与 `frontend_action_plan.action_items[].action_id` 一一对应
- rollback continuity：rollback 只能引用 plan 中已有 `rollback_checkpoint_ref / rollback_ref`
- retry continuity：retry 只能引用 plan 中已有 `retry_ref`
- cleanup continuity：对 `non_rollbackable_effect` 必须写入 `cleanup_ref` 与恢复说明

## Browser Gate And 020 Handoff

`101` 对下游的 handoff 规则固定如下：

- browser gate 只能消费：
  - `ManagedDeliveryApplyResult.result_status`
  - `ledger_id`
  - `spec_dir`
  - `attachment_scope_ref`
  - `managed_frontend_target`
  - `readiness_subject_id`
- `020` 只能消费 apply result 中的：
  - `recheck_required`
  - `blockers`
  - `remediation_hints`
  - `source_linkage_refs`
- `101` 不得直接产出最终 program execute gate verdict
- `101` 不得把 browser gate 缺失伪装成 apply 成功后的 readiness 完结

## 验收场景

1. Given `100` 已生成 confirmed plan 且用户在确认页选择继续，When apply runtime 启动，Then 系统必须先创建 execution session 与空 ledger，再按依赖顺序执行 selected mutate actions
2. Given 某个 optional root-level integration action 在确认页被取消，When session 启动，Then 该 action 必须进入 `skipped_action_ids`，且不会被 executor 隐式补执行
3. Given 某个 action 执行后出现 `retryable_failure`，When 用户选择重试，Then executor 必须沿用同一 `action_id` 更新 ledger，而不是重新生成 plan
4. Given 某个 action 产生 `non_rollbackable_effect` 且后续失败，When session 结束，Then apply result 必须暴露 `cleanup_required_action_ids` 或 `manual_recovery_required`，并且不得宣称 apply 已成功
5. Given apply 已完成且 browser gate 尚未运行，When 系统生成结果，Then `result_status` 必须是 `apply_succeeded_pending_browser_gate`，而不是最终 readiness `ready`

## 功能需求

### Positioning And Inputs

| ID | 需求 |
|----|------|
| FR-101-001 | `101` 必须作为 `095.Managed Action Engine` 的第二正式切片被定义，用于冻结 confirmed action plan 的 apply runtime、ledger、rollback/retry/cleanup 与结果 handoff |
| FR-101-002 | `101` 只能消费并串联 `014 / 020 / 073 / 094 / 095 / 096 / 098 / 099 / 100`，不得回写或重写这些已冻结 truth |
| FR-101-003 | apply runtime 只能在 `100.frontend_action_plan.status = confirmed_for_execution` 且存在合法 `DeliveryApplyDecisionReceipt(decision=continue)` 时启动 |
| FR-101-004 | 当确认页要求二次确认时，未提供 `second_confirmation_acknowledged` 不得启动 apply runtime |

### Execution Session And Scope

| ID | 需求 |
|----|------|
| FR-101-005 | apply runtime 必须创建唯一的 `ManagedDeliveryExecutionSession`，并锁定 `managed_target_ref`、`attachment_scope_ref`、`readiness_subject_id` 与 `spec_dir` |
| FR-101-006 | 只有 `effect_kind = mutate` 且被选中的 action 才能进入 executable scope；`observe / plan` action 不得被 executor 二次执行 |
| FR-101-007 | executor 必须按 `depends_on_action_ids` 保证 action 执行顺序，不得在执行期偷偷新增 plan 外动作 |
| FR-101-008 | 对未被选中的 `optional` action，executor 必须显式记录为 skipped；对未被选中的 `required` action，session 必须 fail-closed 为 `blocked_before_start` |

### Ledger, Rollback, Retry, Cleanup

| ID | 需求 |
|----|------|
| FR-101-009 | `delivery_action_ledger` 必须在第一个 mutate action 执行前创建，并以 `action_id` 为唯一执行索引逐 action 写入 |
| FR-101-010 | 每个 action 的 ledger 记录必须至少包含 `before_state`、`after_state`、`result_status`、`error_code`、`rollback_ref`、`retry_ref` 与必要时的 `cleanup_ref` |
| FR-101-011 | apply runtime 必须显式区分 `retryable_failure / rollbackable_failure / non_rollbackable_failure / manual_recovery_required / blocked_before_start` |
| FR-101-012 | whole-plan rollback 必须基于已成功 action 的反向依赖顺序执行；不得依赖口头说明或隐藏脚本 |
| FR-101-013 | per-action retry 必须沿用同一 `action_id` 并保留之前失败记录；不得通过重新规划新 plan 伪装 retry |
| FR-101-014 | 对 `non_rollbackable_effect` 或 cleanup 失败的情况，apply result 必须诚实暴露 `cleanup_required_action_ids` 或 `manual_recovery_required` |
| FR-101-015 | apply runtime 必须保留 honest partial-progress state，不得把已执行 action 压扁成“未开始” |

### Result Handoff

| ID | 需求 |
|----|------|
| FR-101-016 | apply runtime 必须生成结构化 `ManagedDeliveryApplyResult`，至少包含执行结果、失败/回滚/跳过 action 集合、source linkage 与下游 handoff 字段 |
| FR-101-017 | `ManagedDeliveryApplyResult` 可以表达 `apply_succeeded_pending_browser_gate`，但不得直接宣称最终 readiness 已通过 |
| FR-101-018 | `020` 只允许消费 `101` 结果中的 `recheck_required`、`blockers`、`remediation_hints` 与 `source_linkage_refs`；`101` 不得直接改写 `020` execute gate truth |
| FR-101-019 | `101` 不得把 browser gate runtime 或 program execute aggregation 混入 apply runtime 本身 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-101-001 | reviewer 能从任一 apply session 直接追溯到 decision receipt、confirmed plan、ledger 与 apply result 的单向链路 |
| SC-101-002 | reviewer 能直接解释失败分类、rollback/cleanup/retry 与 partial-progress 如何围绕同一组 action id 运转 |
| SC-101-003 | reviewer 能确认 `101` 只产出 apply result handoff，而不会提前宣称 browser gate 或 `020` readiness 已完成 |
| SC-101-004 | 当前规格不会让人误以为 planner、browser gate 或 program execute aggregation 已在本批实现 |

## 后续实现拆分建议

`101` 之后至少还需要一个正式下游切片：

1. **Browser Quality Gate Baseline**
   - 负责 Playwright smoke、visual/a11y/interaction evidence bundle
   - 负责把 browser verdict 与 `ManagedDeliveryApplyResult` 绑定
   - 负责向 `020` 提供最终可执行的 frontend readiness handoff
