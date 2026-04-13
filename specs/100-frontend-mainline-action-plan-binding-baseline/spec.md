# 功能规格：Frontend Mainline Action Plan Binding Baseline

**功能编号**：`100-frontend-mainline-action-plan-binding-baseline`  
**创建日期**：2026-04-12  
**状态**：formal baseline 已冻结；作为 `095` 的 `Managed Action Engine` 第一正式切片  
**输入**：[`../010-agent-adapter-activation-contract/spec.md`](../010-agent-adapter-activation-contract/spec.md)、[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../094-stage0-init-dual-path-project-onboarding-baseline/spec.md`](../094-stage0-init-dual-path-project-onboarding-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../096-frontend-mainline-host-runtime-manager-baseline/spec.md`](../096-frontend-mainline-host-runtime-manager-baseline/spec.md)、[`../098-frontend-mainline-posture-detector-baseline/spec.md`](../098-frontend-mainline-posture-detector-baseline/spec.md)、[`../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md`](../099-frontend-mainline-delivery-registry-resolver-baseline/spec.md)、[`../../src/ai_sdlc/models/frontend_solution_confirmation.py`](../../src/ai_sdlc/models/frontend_solution_confirmation.py)、[`../../src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py`](../../src/ai_sdlc/generators/frontend_solution_confirmation_artifacts.py)、[`../../src/ai_sdlc/core/verify_constraints.py`](../../src/ai_sdlc/core/verify_constraints.py)

> 口径：`100` 冻结的不是 installer runtime、不是 rollback executor、也不是 browser gate，而是 `095` 四块实现切片里的第三块正式切片。它只回答五个问题：`096.host_runtime_plan`、`098.frontend_posture_assessment`、`099.delivery_bundle_entry` 与本地检测证据如何收敛成单一 `frontend_action_plan`；`observe / plan / mutate` 如何继续保持单向分层；`delivery_execution_confirmation_surface` 在执行前必须展示什么；`delivery_action_ledger` 如何与 action id、rollback、retry 对齐；以及当上游 truth 或本地 evidence 不完整时，action plan 应如何 fail-closed，而不是靠执行期临场猜测。

## 问题定义

`095` 已经把主线产品交付总合同锁住，`096` 把 host runtime 自愈单独切出来，`098` 把 posture detector 单独切出来，`099` 又把 delivery registry resolver 独立冻结。但当前链路仍缺一个关键中段：**谁来把这些上游 truth 绑定成一个可确认、可执行、可回滚、可重试的前端动作计划**。

如果这一层不先冻结，后续实现会继续在四种漂移之间反复摆动：

- 把 `073.solution_snapshot`、`096.host_runtime_plan`、`099.delivery_bundle_entry` 各自解释一遍，最后 runtime truth、package truth 与 target truth 出现三份口径
- 把本地缺失依赖、升级替换、sidecar root、workspace 集成直接写成临时 shell 指令，导致 `frontend_action_plan` 失去结构化动作边界
- 在没有 `delivery_execution_confirmation_surface` 的情况下提前执行 mutate，最后用户只能在事后猜测“系统到底改了什么”
- 执行完成后才临时补日志，导致 action id、rollback checkpoint、retry 单元与确认页展示内容无法一一对应

`100` 的目标就是把这段中间层固定下来：先冻结 action binding truth order、动作分类、必需/可选边界、确认页内容面和 ledger 绑定规则，再把真正的 apply runtime 与 browser gate 保持在后续切片中独立推进。

## 范围

- **覆盖**：
  - `frontend_action_plan` 的输入面、truth order 与 plan materialization 规则
  - `096.host_runtime_plan`、`098.frontend_posture_assessment`、`099.delivery_bundle_entry` 与本地检测 evidence 的绑定边界
  - `action_items` 的 `effect_kind / requiredness / default_selected / rollback / retry / risk` 语义
  - `will_install / will_download / will_modify / will_generate / will_not_touch` 五类结果面的正式含义
  - `delivery_execution_confirmation_surface` 的最小展示面、决策入口与二次确认规则
  - `delivery_action_ledger` 的 action-id continuity、whole-plan rollback、per-action retry 与 partial-progress 语义
  - `100` 与后续 `managed_delivery_apply` / browser gate 的 handoff 边界
- **不覆盖**：
  - 在本 work item 中直接实现 runtime executor、package installer、file writer、rollback executor 或 browser gate
  - 重写 `073` 已冻结的 requested/effective solution truth
  - 重写 `096` 的 host runtime readiness truth、`098` 的 support status truth、`099` 的 registry entry truth
  - 定义 takeover old frontend 的默认路径；v1 继续以 `new_controlled_subtree` 为默认 managed target
  - 新增 registry entry、provider、style pack、browser probe 或新的姿态分类
  - 在 action binding 阶段静默执行任何 mutate 行为

## 已锁定决策

- `073.solution_snapshot` 与 `073.solution_confirmation_surface` 继续独占方案 truth；`100` 只能在 `solution_snapshot confirmed` 之后生成 `frontend_action_plan`。
- `010.agent_target + activation_state + support_tier + evidence` 继续作为进入受控交付的前置门；未激活状态最多允许查看推荐与阻断原因，不得生成可执行 mutate plan。
- `096.host_runtime_plan` 继续独占 runtime remediation truth；`100` 只能把其中需要执行的 runtime action 绑定进计划，不得重复推导另一套 runtime requirements。
- `098.frontend_posture_assessment` 继续独占 posture/no-touch truth；`100` 只能消费其 `support_status`、`reason_codes`、`sidecar_root_recommendation` 与 `source_paths`。
- `099.delivery_bundle_entry` 继续独占 provider/component-library delivery truth；`100` 只能引用其 `runtime_requirements`、`component_library_packages`、`adapter_packages`、`verification_probes` 与 `preferred_managed_target_kind`。
- v1 默认 managed target 仍固定为 `new_controlled_subtree`；对 `unsupported_existing_frontend_sidecar_only` 与 `supported_existing_candidate`，旧 frontend 根、旧 manifest、旧 lockfile 默认都必须进入 `will_not_touch`。
- `frontend_action_plan` 必须继续保持 `observe / plan / mutate` 三段分层；任何 `mutate` action 都不得在 `delivery_execution_confirmation_surface` 之前执行。
- `root-level workspace/lockfile/CI/proxy/route` 集成必须被表达为单独 `optional` action，默认关闭，不得伪装成 sidecar 必做步骤。
- `delivery_action_ledger` 不在 planning 阶段补写伪结果；它只在确认后的自动动作真正开始时创建，并继续沿用 `action_plan.action_items[].action_id` 作为唯一执行索引。
- 含 `non_rollbackable_effect` 或 `manual_recovery_required` 的 action，必须在确认页单独暴露风险，并要求二次确认。

## Action Binding Inputs

### 1. ActionBindingContext

`ActionBindingContext` 是 `100` 允许消费的最小 project-scoped 绑定上下文，用来把上游 truth 与本地 evidence 收敛到一个计划面。

其最小字段至少包括：

- `binding_id`
- `activation_ref`
- `solution_snapshot_ref`
- `host_runtime_plan_ref`
- `posture_assessment_ref`
- `delivery_bundle_entry_ref`
- `managed_target_ref`
- `preferred_managed_target_kind`
- `local_evidence_refs`
- `requested_optional_actions`
- `blocking_reason_codes`

规则：

- `activation_ref` 必须能回溯到 `010` 的 activation truth
- `solution_snapshot_ref` 必须指向 `073` 已确认的 solution snapshot
- `host_runtime_plan_ref`、`posture_assessment_ref`、`delivery_bundle_entry_ref` 必须全部存在；缺任一 ref 时不得生成 confirmable plan
- `managed_target_ref` 在 v1 默认指向 framework-managed `new_controlled_subtree`
- `local_evidence_refs` 只承载检测证据，不得自持第二份 provider/style/runtime truth

### 2. LocalDetectionEvidence

`LocalDetectionEvidence` 用来表达 action planning 阶段真正观察到的本地状态，而不是再次推导方案。

其最小字段至少包括：

- `evidence_id`
- `subject_kind`
  - `runtime`
  - `dependency`
  - `managed_target`
  - `workspace_integration`
  - `browser_dependency`
- `subject_ref`
- `observed_state`
  - `present_compatible`
  - `present_incompatible`
  - `missing`
  - `blocked`
- `source_paths`
- `reason_codes`

规则：

- `observed_state = missing / present_incompatible / blocked` 时，系统必须把它显式收敛为 action 或 blocker；不得留给执行期临时判断
- `workspace_integration` 相关 evidence 只能驱动独立 optional action，不得提升成 sidecar 默认必做项

### 3. FrontendActionPlan

`frontend_action_plan` 是 `100` 对外暴露的唯一 action planning truth。它继续满足 `095` 的建议字段面，并补齐上游 ref 绑定。

其最小字段至少包括：

- `action_plan_id`
- `solution_snapshot_ref`
- `host_runtime_plan_ref`
- `posture_assessment_ref`
- `delivery_bundle_entry_ref`
- `managed_target_ref`
- `requested_actions`
- `effective_actions`
- `action_items[]`
  - `action_id`
  - `effect_kind`
    - `observe`
    - `plan`
    - `mutate`
  - `action_type`
    - `runtime_remediation`
    - `managed_target_prepare`
    - `dependency_install`
    - `dependency_reconcile`
    - `artifact_generate`
    - `workspace_integration`
    - `browser_dependency_provision`
  - `target`
  - `requiredness`
    - `required`
    - `optional`
  - `default_selected`
  - `depends_on_action_ids`
  - `rollback_checkpoint_ref`
  - `retry_ref`
  - `risk_flags`
- `will_install`
- `will_download`
- `will_modify`
- `will_generate`
- `will_not_touch`
- `rollback_checkpoint_ids`
- `retryable_action_ids`
- `status`
  - `draft`
  - `confirm_required`
  - `blocked`
  - `confirmed_for_execution`
  - `superseded`

其中：

- `requested_actions` 表达用户或上游 truth 希望发生的动作面
- `effective_actions` 表达在 activation、posture、bundle、local evidence 与 requiredness 过滤后真正可进入确认页的动作面
- `action_type` 必须来自受控枚举，不允许自由文本拼接 shell 步骤
- `rollback_checkpoint_ref`、`retry_ref` 只声明执行时应如何对齐 ledger；它们不是 planning 阶段的执行结果

### 4. DeliveryExecutionConfirmationSurface

`delivery_execution_confirmation_surface` 是执行前必须展示的唯一确认面。

其最小字段至少包括：

- `surface_id`
- `action_plan_id`
- `summary_reason_codes`
- `required_actions`
- `optional_actions`
- `host_runtime_actions`
- `dependency_actions`
- `write_targets`
- `generated_artifacts`
- `will_not_touch`
- `fallback_differences`
- `rollback_points`
- `retry_units`
- `risk_items`
  - `risk_level`
  - `non_rollbackable_effect`
  - `manual_recovery_required`
  - `recovery_path`
- `decision_options`
  - `continue`
  - `return_to_solution`
  - `return_to_action_plan`
  - `cancel`
- `second_confirmation_required`
- `status`
  - `ready_for_decision`
  - `decision_captured`
  - `superseded`

### 5. DeliveryActionLedger

`delivery_action_ledger` 承载 action 级审计、结果回放、rollback/retry 与 partial-progress truth。

其最小字段至少包括：

- `ledger_id`
- `action_plan_id`
- `actions[]`
  - `action_id`
  - `action_type`
  - `target`
  - `before_state`
  - `after_state`
  - `result_status`
    - `planned`
    - `running`
    - `succeeded`
    - `failed`
    - `rolled_back`
    - `skipped`
    - `cancelled`
  - `error_code`
  - `rollback_ref`
  - `retry_ref`
  - `cleanup_ref`
  - `non_rollbackable_effect`
  - `manual_recovery_required`
- `created_at`
- `updated_at`

规则：

- `actions[].action_id` 必须与 `frontend_action_plan.action_items[].action_id` 一一对应
- ledger 只记录真实执行过或被真实跳过/取消的 action；不得在 planning 阶段预填成功结果
- whole-plan rollback 与 per-action retry 都必须基于 ledger 中的 action-level 记录，而不是依赖口头说明

## Action Plan Truth Order

action binding 的顺序固定如下：

1. **Activation gate first**
   - 先读取 `010` 的 activation truth
   - 未激活或不受支持时，`frontend_action_plan.status` 必须为 `blocked`
2. **Solution truth second**
   - 读取 `073` 的 `solution_snapshot confirmed`
   - 未确认 solution 时不得生成 mutate-capable plan
3. **Posture and target freeze third**
   - 读取 `098` 的 `support_status`、`reason_codes`、`sidecar_root_recommendation`
   - 结合 `099.preferred_managed_target_kind` 固定 `managed_target_ref`
4. **Host runtime truth fourth**
   - 读取 `096.host_runtime_plan`
   - 仅把其中 required remediation 转写为 action item；不得重新做 runtime 推理
5. **Delivery bundle truth fifth**
   - 读取 `099.delivery_bundle_entry`
   - 仅把其中 package/runtime/verification truth 绑定到 action item；不得再生成第二份 bundle
6. **Local evidence sixth**
   - 读取本地 runtime、dependency、managed target 与 workspace integration evidence
   - 按 `present_compatible / present_incompatible / missing / blocked` 分类
7. **Requiredness and selection seventh**
   - 把 action item 分成 `required / optional`
   - 仅允许 `optional` action 被取消或延后
8. **Confirmation surface last**
   - 由 `effective_actions + will_* + risk_items + rollback/retry units` 生成唯一确认页
   - 没有 confirmation surface 就不得进入 apply runtime

优先级护栏：

- `100` 不得因为本地已有某个包，就覆盖 `073` 已确认的 provider/style truth
- `100` 不得因为 posture 是 `supported_existing_candidate`，就默认接管旧 frontend 根
- `100` 不得把 `workspace_integration` 或 `browser_dependency_provision` 混成隐式动作
- 任一上游 ref 缺失、冲突或无法定位时，plan 必须 fail-closed 为 `blocked`

## Plan Materialization Rules

### 1. Action family binding

action family 的来源固定如下：

- `runtime_remediation`：仅来自 `096.host_runtime_plan`
- `managed_target_prepare`：仅来自 `098.posture` 与 `099.preferred_managed_target_kind`
- `dependency_install / dependency_reconcile`：仅来自 `099.delivery_bundle_entry` + local dependency evidence
- `artifact_generate`：仅来自受控 provider/template/scaffold 产物，不接受自由文本生成路径
- `workspace_integration`：仅来自 root-level 集成 evidence 与显式可选请求
- `browser_dependency_provision`：只表达浏览器依赖准备动作；browser gate verdict 继续留给后续切片

### 2. Requiredness policy

v1 requiredness 规则固定如下：

- 以下动作必须是 `required`：
  - 满足 `096.host_runtime_plan` 的 runtime remediation
  - 创建 `new_controlled_subtree` 所必需的 managed target prepare
  - 让 `099.delivery_bundle_entry` 落地所必需的 dependency install/reconcile
  - provider/template 正常启动所必需的 artifact generate
- 以下动作默认只能是 `optional`：
  - root-level workspace / lockfile / CI / proxy / route integration
  - 对旧 frontend 根的任何接触性集成
  - 不影响当前主线成立的便利性动作
  - 可推迟到 browser gate 前再执行的非关键浏览器依赖预置

规则：

- `optional` action 可以在不回到 solution freeze 的前提下取消或延后
- `required` action 不得在确认页中被取消
- `default_selected = false` 只能用于 `optional` action

### 3. Will-surface binding

`frontend_action_plan` 必须显式产出五类结果面：

- `will_install`：依赖安装、升级、替换、浏览器依赖 provision
- `will_download`：runtime/bootstrap/template/browser artifact 下载
- `will_modify`：受控写入、补丁、配置改动、lockfile 变更、root integration
- `will_generate`：新 scaffold、provider wiring、受控模板输出
- `will_not_touch`：旧 frontend 根、旧 manifest、旧 lockfile、旧 CI、旧 proxy、旧 route、未选择的 optional integration

规则：

- `will_not_touch` 不能靠默认常识推断，必须由 posture/source paths/managed target 边界显式展开
- 对 `unsupported_existing_frontend_sidecar_only`，旧 frontend 目录必须始终进入 `will_not_touch`
- 对 `supported_existing_candidate`，在 v1 默认 `new_controlled_subtree` 下，旧工程仍保持 no-touch，直到后续切片另行 formalize takeover

### 4. Blocked and fallback semantics

以下情况必须让 `frontend_action_plan.status = blocked`：

- `activation_ref`、`solution_snapshot_ref`、`host_runtime_plan_ref`、`posture_assessment_ref`、`delivery_bundle_entry_ref` 任一缺失
- `096.host_runtime_plan` 自身已处于 `blocked`
- `099.delivery_bundle_entry` 无法解析或与 current solution mismatch
- 本地 evidence 表明 required action 缺少合法 target、缺少合法 installer/channel、或恢复边界不可表达
- posture 只能进入 sidecar/no-touch，但计划仍试图生成 takeover old frontend 动作

blocked 时必须：

- 输出结构化 `blocking_reason_codes`
- 保留 `will_not_touch`
- 不生成可执行 mutate action

## Confirmation Surface Rules

`delivery_execution_confirmation_surface` 必须满足以下规则：

- 必须同时展示：
  - 本次会做什么
  - 不会改什么
  - 为什么需要这样做
  - fallback 差异
  - 失败后怎么退回
  - 现在可继续、返回改方案、返回改动作、取消
- 必须把 action 明确分成 `required_actions` 与 `optional_actions`
- 必须列出 host runtime 动作、dependency 动作、write targets、generated artifacts、rollback points、retry units
- 必须把 `non_rollbackable_effect` 与 `manual_recovery_required` 升格成独立 `risk_items`
- 当存在高风险项时，`second_confirmation_required = true`
- 确认页是唯一允许用户做最终执行决策的入口；执行器不得绕过它直接起 mutate

## Ledger, Rollback, Retry

`delivery_action_ledger` 的执行边界固定如下：

- 只有在用户确认继续后，executor 才能创建 ledger 并按 action 顺序记录结果
- `before_state` 与 `after_state` 必须按 action 粒度记录，不得只在 plan 级别写一个笼统摘要
- whole-plan rollback 依赖 `rollback_checkpoint_ids + ledger.actions[].rollback_ref`
- per-action retry 依赖 `retryable_action_ids + ledger.actions[].retry_ref`
- 对无法严格回滚的外部副作用，ledger 必须写入 `cleanup_ref`、`non_rollbackable_effect` 与 `manual_recovery_required`
- 发生 partial failure 时，ledger 必须诚实保留成功、失败、跳过、回滚各自的 action 结果，不得统一覆盖成“本次失败”

## 下游交接边界

- `100` 的输出面只有三块：
  - `frontend_action_plan`
  - `delivery_execution_confirmation_surface`
  - `delivery_action_ledger` 的 schema 与 action-id continuity contract
- 真正的 `managed_delivery_apply` executor 继续属于后续切片；它只能消费 `100` 生成的 plan/surface/ledger schema，不得反向改写 plan truth
- browser quality gate 继续属于后续切片；`100` 最多只允许把 `browser_dependency_provision` 表达为 action item，不得产出 browser verdict
- `020` readiness 与更高层 orchestrator 只能消费已确认且已落 ledger 的执行结果，不得把 draft plan 伪装成“已经交付”

## 验收场景

1. Given `073` 已确认 `vue3 + public-primevue`，`096` 表示 runtime 已 ready，`099` 成功解析 entry，且本地缺少组件库依赖，When 系统生成 plan，Then 必须得到包含 `dependency_install` 与 `artifact_generate` 的 `frontend_action_plan`，并生成可确认的 `delivery_execution_confirmation_surface`
2. Given posture 为 `unsupported_existing_frontend_sidecar_only`，When 系统生成 plan，Then 旧 frontend 根、旧 manifest、旧 lockfile 必须进入 `will_not_touch`，且 root-level integration 只能以 `optional` action 形式出现
3. Given `096.host_runtime_plan` 中存在 required remediation，When 系统生成确认页，Then host runtime 动作必须作为 `required_actions` 单独展示，并与 dependency/write actions 一起进入 rollback/retry 说明
4. Given 某个 action 含 `non_rollbackable_effect` 或 `manual_recovery_required`，When 用户查看确认页，Then 系统必须展示风险说明、恢复路径，并要求二次确认后才能继续

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-100-001 | `100` 必须作为 `095.Managed Action Engine` 的第一正式切片被定义，用于冻结 action binding、confirmation surface 与 ledger continuity 合同 |
| FR-100-002 | `100` 只能消费并串联 `010 / 014 / 073 / 094 / 095 / 096 / 098 / 099`，不得回写或重写这些已冻结 truth |
| FR-100-003 | 在进入 action binding 前，系统必须先通过 `010` activation gate；未激活状态最多允许展示阻断原因，不得生成可执行 mutate plan |
| FR-100-004 | `frontend_action_plan` 必须只在 `073.solution_snapshot confirmed` 之后生成；未确认 solution 时不得生成 mutate-capable plan |
| FR-100-005 | action binding 的 truth order 必须固定为：activation -> solution -> posture/target -> host runtime -> delivery bundle -> local evidence -> requiredness -> confirmation surface |
| FR-100-006 | `096.host_runtime_plan`、`098.frontend_posture_assessment`、`099.delivery_bundle_entry` 必须继续分别独占 runtime truth、posture truth 与 delivery truth；`100` 不得复制或重算第二份并行真值 |

### Action Plan Binding

| ID | 需求 |
|----|------|
| FR-100-007 | 本地缺失、升级替换、受控写入、sidecar prepare、workspace integration、browser dependency provision 都必须收敛成结构化 `frontend_action_plan.action_items[]`，不得降级为自由文本步骤 |
| FR-100-008 | 每个 action item 都必须显式带有 `effect_kind`、`action_type`、`requiredness`、`default_selected`、`depends_on_action_ids` 与 rollback/retry 相关 ref |
| FR-100-009 | `frontend_action_plan` 必须显式列出 `will_install / will_download / will_modify / will_generate / will_not_touch` 五类结果面 |
| FR-100-010 | `frontend_action_plan` 必须把 action 明确区分为 `required / optional`；只有 `optional` action 才允许取消或延后 |
| FR-100-011 | 对 `unsupported_existing_frontend_sidecar_only` 与 v1 的 `supported_existing_candidate`，默认 managed target 必须仍为 `new_controlled_subtree`，旧 frontend 根与旧 manifest/lockfile 必须进入 `will_not_touch` |
| FR-100-012 | root-level workspace / lockfile / CI / proxy / route integration 必须被表达为独立 `optional` action，默认关闭，不得伪装成 sidecar 必做项 |
| FR-100-013 | 任一上游 ref 缺失、mismatch 或 required action 恢复边界不可表达时，`frontend_action_plan.status` 必须 fail-closed 为 `blocked` |

### Confirmation Surface

| ID | 需求 |
|----|------|
| FR-100-014 | 任何 `mutate` action 在执行前都必须先进入 `delivery_execution_confirmation_surface`；没有确认页就不得开始自动执行 |
| FR-100-015 | `delivery_execution_confirmation_surface` 至少必须展示：本次会做什么、不会改什么、为什么需要这样做、fallback 差异、失败后怎么退回、继续/返回改方案/返回改动作/取消 |
| FR-100-016 | `delivery_execution_confirmation_surface` 必须把 host runtime 动作、dependency 动作、write targets、generated artifacts、rollback points 与 retry units 一并暴露 |
| FR-100-017 | 当 action plan 含 `non_rollbackable_effect` 或 `manual_recovery_required` 时，确认页必须展示风险说明与恢复路径，并要求二次确认后才能继续 |

### Ledger And Downstream Handoff

| ID | 需求 |
|----|------|
| FR-100-018 | 所有自动动作都必须以 `frontend_action_plan.action_items[].action_id` 作为唯一执行索引写入 `delivery_action_ledger` |
| FR-100-019 | `delivery_action_ledger` 必须支持 whole-plan rollback、per-action retry 与 honest partial-progress replay；不得只支持“全部重来” |
| FR-100-020 | `100` 只能 formalize `frontend_action_plan`、`delivery_execution_confirmation_surface` 与 `delivery_action_ledger` 的合同，不得声称 apply runtime 或 browser quality gate 已在本切片实现 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-100-001 | reviewer 能从任一 action item 追溯到对应的 activation、solution、runtime、posture、delivery bundle 与 local evidence 输入 |
| SC-100-002 | reviewer 能在执行前明确区分本次会安装/下载/修改/生成什么，以及哪些旧工程对象明确不会被触碰 |
| SC-100-003 | reviewer 能直接解释确认页与 ledger 如何围绕同一组 action id 对齐 rollback、retry 与 partial-progress |
| SC-100-004 | 当前规格不会让人误以为 executor、rollback runtime 或 browser gate 已在本批实现 |

## 后续实现拆分建议

`100` 之后至少还需要两个下游实现切片：

1. **Managed Delivery Apply Runtime**
   - 负责执行已确认的 `frontend_action_plan`
   - 负责创建并更新 `delivery_action_ledger`
   - 负责 rollback / cleanup / retry runtime
2. **Browser Quality Gate Baseline**
   - 负责 Playwright smoke、visual/a11y/interaction evidence bundle
   - 负责把 browser verdict 接到 `020` readiness

---
related_doc:
  - "specs/014-frontend-contract-runtime-attachment-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/094-stage0-init-dual-path-project-onboarding-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/096-frontend-mainline-host-runtime-manager-baseline/spec.md"
  - "specs/098-frontend-mainline-posture-detector-baseline/spec.md"
  - "specs/099-frontend-mainline-delivery-registry-resolver-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
