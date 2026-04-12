# 功能规格：Frontend Mainline Browser Quality Gate Baseline

**功能编号**：`102-frontend-mainline-browser-quality-gate-baseline`  
**创建日期**：2026-04-13  
**状态**：已冻结（formal baseline）  
**输入**：[`../014-frontend-contract-runtime-attachment-baseline/spec.md`](../014-frontend-contract-runtime-attachment-baseline/spec.md)、[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)、[`../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`](../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md)

> 口径：`102` 冻结的不是 action planner、不是 apply runtime、不是 remediation engine，也不是完整 visual regression 平台，而是 `101` 下游的真实浏览器质量门禁本身。它只回答五个问题：什么条件下允许从 `ManagedDeliveryApplyResult` 进入 browser gate；`playwright_smoke / visual_expectation / basic_a11y / interaction_anti_pattern_checks` 四类检查如何形成单一 gate contract；缺证据、瞬时运行失败、真实质量阻断和仅建议项如何被诚实区分；`browser_quality_bundle` 如何保持 `one bundle == one active spec scope == one managed frontend target`；以及 browser verdict 如何以 `020` 可消费的方式交给 execute readiness handoff，而不是在本层偷发 program 级最终 ready。

## 问题定义

`095` 已把 browser quality gate 定义成 frontend mainline mandatory gate，`100` 又把 browser dependency provision 留在 action plan 中，`101` 进一步把 apply runtime 收束成 `ManagedDeliveryApplyResult -> browser gate / 020` 的单向 handoff。

但当前链路里仍缺少一份独立 formal baseline，回答以下问题：

- browser gate 到底在什么前置状态下允许启动，什么情况下必须直接 fail-closed
- 四类检查面各自消费什么上游 truth，而不是在运行时临时猜测 provider/style/a11y 口径
- 缺少证据、Playwright 瞬时失败、真实前端质量 blocker 与 advisory 如何避免混报成一类“测试失败”
- `browser_quality_bundle` 的 scope、target、evidence refs、requirement linkage 与 gate verdict 应如何冻结
- browser gate 的输出怎样交给 `020` 的 execute / recheck / remediation vocabulary，而不是在本层发明第二套 readiness state

如果不先冻结 `102`，后续实现会快速滑向四种常见偏差：

- 在没有真实浏览器证据的前提下，用静态代码检查或主观截图点评替代 mandatory gate
- 把 `visual_expectation` 扩张成完整 visual regression 平台，或者反过来退化成“页面能打开就算过”
- 把 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only` 混成单一失败态，导致 operator 无法判断该重跑、该修代码还是只看建议
- 让 `browser_quality_bundle` 漂移成项目级最新快照，失去 `spec_dir + attachment_scope_ref + managed_frontend_target + readiness_subject_id` 的单一绑定

因此，`102` 的目标是把 browser quality gate 冻结成最小但严格的正式合同：先锁定 gate eligibility、四类检查、失败分类、证据打包与 `020` handoff，再把 remediation replay、多浏览器矩阵与更宽质量平台继续留在后续切片。

## 范围

- **覆盖**：
  - 将 browser quality gate 正式定义为 `101` 下游独立 child work item
  - 锁定 browser gate 的启动条件、输入面与 scope binding
  - 锁定 `playwright_smoke`、`visual_expectation`、`basic_a11y`、`interaction_anti_pattern_checks` 四类检查面的最低合同
  - 锁定 `browser_quality_bundle`、失败分类、evidence refs、requirement linkage 与 advisory/blocker 语义
  - 锁定 browser gate 到 `020` execute/recheck/remediation handoff 的最小输出面
- **不覆盖**：
  - 在本 work item 中实现 Playwright runner、视觉回归平台、自动修复、自动重跑或 remediation workflow
  - 改写 `101` 的 apply runtime truth、`100` 的 action plan truth、`073` 的 provider/style truth 或 `071` 的 a11y foundation truth
  - 把 browser gate 扩张成多浏览器/多设备矩阵、完整 WCAG 平台、完整 visual diff 平台或 backend/test 优化平台
  - 在本 work item 中直接产出 program 级最终 ready verdict 或第二套 execute gate system

## 已锁定决策

- `102` 只能消费 `101.ManagedDeliveryApplyResult`、`073.solution_snapshot`、`071` visual/a11y foundation 与 `020` execute vocabulary；不得另造主流程私有 truth
- browser gate 只允许在真实浏览器中运行；静态 lint、单纯 DOM snapshot 或“页面打开成功”都不能替代 mandatory gate
- `visual_expectation` 必须绑定 `073` 已确认的 `effective_provider / effective_style_pack / style_fidelity_status`；`basic_a11y` 必须绑定 `071` 的 perceivability / semantics / keyboard / focus 底线
- 失败分类固定为 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only`；`advisory_only` 明确是非阻断结果
- `browser_quality_bundle` 必须保持 `one bundle == one active spec scope == one managed frontend target`，不得把 latest bundle 伪装成项目级全局结论
- `102` 的输出只能作为 `020` per-spec execute gate 的输入；它本身不是 program 级最终 readiness aggregator

## 用户故事与验收

### US-102-1 — Framework Maintainer 需要真实浏览器 gate 有独立 formal truth

作为**框架维护者**，我希望 browser quality gate 在正式文档里有独立 child work item，以便真实浏览器门禁、四类检查与 `020` handoff 不再混在 apply runtime 或母规格的抽象描述里。

**验收**：

1. Given 我查看 `102` formal docs，When 我追踪 frontend mainline，Then 可以明确看到它位于 `101` 之后且只消费 apply result + solution/a11y truth  
2. Given 我审阅 `102` formal docs，When 我确认 non-goals，Then 可以明确读到 remediation engine、多浏览器矩阵与完整 visual/a11y 平台仍留在下游

### US-102-2 — Operator 需要区分“缺证据、瞬时失败、真实 blocker、仅建议”

作为**operator**，我希望 browser gate 失败时能诚实告诉我到底是缺证据、环境瞬时失败、真实质量 blocker，还是只有 advisory，以便我知道下一步该重跑、补证据还是修前端。

**验收**：

1. Given browser gate 无法拿到完整 evidence，When 我查看结果，Then 可以明确读到 `evidence_missing`，而不是被混报成 blocker  
2. Given 只有 advisory 级问题，When 我查看结果，Then gate 不会被伪装成阻断失败，并且会附带通俗下一步建议

### US-102-3 — Reviewer 需要确认 bundle 与 020 handoff 都是单一真值

作为**reviewer**，我希望 `browser_quality_bundle` 的 scope/target 绑定和 `020` handoff 字段面在 formal docs 中只有一套真值，以便后续不会出现“同一 bundle 被多个 scope 复用”或“另造第二套 execute verdict”。

**验收**：

1. Given 我检查 `102` formal docs，When 我确认 bundle schema，Then 可以明确读到 `spec_dir + attachment_scope_ref + managed_frontend_target + readiness_subject_id` 是单一绑定  
2. Given 我检查 `102` formal docs，When 我查看 handoff 规则，Then 可以明确读到 browser gate 只输出 `020` 可消费的 gate/recheck/remediation vocabulary，而不是 program 私有 verdict

## 关键实体

### 1. BrowserQualityGateExecutionContext

`BrowserQualityGateExecutionContext` 是 browser gate 在启动前冻结的唯一执行上下文。

其最小字段至少包括：

- `gate_run_id`
- `apply_result_id`
- `solution_snapshot_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `readiness_subject_id`
- `effective_provider`
- `effective_style_pack`
- `style_fidelity_status`
- `required_probe_set`
  - `playwright_smoke`
  - `visual_expectation`
  - `basic_a11y`
  - `interaction_anti_pattern_checks`
- `browser_entry_ref`
- `source_linkage_refs`

规则：

- 只有当 `ManagedDeliveryApplyResult.result_status = apply_succeeded_pending_browser_gate`、`browser_gate_required = true` 且 scope linkage 完整时，才允许创建 execution context
- `effective_provider / effective_style_pack / style_fidelity_status` 必须直接来自 `073.solution_snapshot`，不得在 gate 运行期临时猜测
- `spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 必须直接继承自 `101` apply result，不得在 browser gate 中漂移

### 2. BrowserQualityCheckResult

`BrowserQualityCheckResult` 是每一类 browser gate 检查输出的最小结果面。

其最小字段至少包括：

- `check_name`
  - `playwright_smoke`
  - `visual_expectation`
  - `basic_a11y`
  - `interaction_anti_pattern_checks`
- `verdict`
  - `pass`
  - `evidence_missing`
  - `transient_run_failure`
  - `actual_quality_blocker`
  - `advisory_only`
- `anchor_refs`
- `evidence_refs`
- `requirement_linkage`
- `blocking_reason_codes`
- `advisory_reason_codes`
- `recheck_required`
- `remediation_hints`

规则：

- 每个 `actual_quality_blocker` 都必须绑定 probe、anchor、evidence 与 requirement linkage，不得只写泛化“前端质量失败”
- `advisory_only` 必须保留 evidence 与 next-step hint，但不得阻断 gate
- `evidence_missing` 与 `transient_run_failure` 必须与真实 blocker 明确分开，便于 `020` 决定是 recheck、remediation 还是阻断

### 3. browser_quality_bundle

`browser_quality_bundle` 是 browser gate 对下游暴露的唯一结构化证据包。

其最小字段至少包括：

- `bundle_id`
- `gate_run_id`
- `apply_result_id`
- `solution_snapshot_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `source_artifact_ref`
- `readiness_subject_id`
- `playwright_trace_refs`
- `screenshot_refs`
- `check_results`
- `smoke_verdict`
- `visual_verdict`
- `a11y_verdict`
- `interaction_anti_pattern_verdict`
- `overall_gate_status`
  - `passed`
  - `passed_with_advisories`
  - `blocked`
  - `incomplete`
- `requirement_linkage`
- `blocking_reason_codes`
- `advisory_reason_codes`
- `generated_at`

规则：

- `one bundle == one active spec scope == one managed frontend target`
- bundle 必须同时绑定 `spec_dir + attachment_scope_ref + managed_frontend_target + readiness_subject_id`，不得只保留其中一部分
- `overall_gate_status = passed` 只允许在四类检查都没有 blocker、没有 evidence 缺失、没有 transient failure 时出现
- `passed_with_advisories` 允许存在 `advisory_only`，但不得掺入 blocker、evidence_missing 或 transient failure
- `incomplete` 只用于 `evidence_missing` 或 `transient_run_failure` 主导、尚无法给出完整 gate verdict 的情形

### 4. FrontendBrowserGateHandoff

`FrontendBrowserGateHandoff` 是 `102` 向 `020` 暴露的最小执行交接面。

其最小字段至少包括：

- `apply_result_id`
- `bundle_id`
- `spec_dir`
- `attachment_scope_ref`
- `managed_frontend_target`
- `readiness_subject_id`
- `execute_gate_state`
  - `ready`
  - `blocked`
  - `recheck_required`
  - `needs_remediation`
- `blockers`
- `recheck_required`
- `remediation_hints`
- `source_linkage_refs`

规则：

- handoff 只能使用 `020` 可消费的 execute/recheck/remediation vocabulary，不得在本层发明 program 私有 state
- `ready` 只表示当前 spec 的 browser gate 已满足交接条件，不等于 program 级最终 ready verdict
- `blocked / recheck_required / needs_remediation` 必须能追溯回具体 `BrowserQualityCheckResult`

## Runtime Truth Order

browser quality gate 的单向顺序固定如下：

1. **Eligibility check**
   - 校验 `ManagedDeliveryApplyResult.result_status = apply_succeeded_pending_browser_gate`
   - 校验 `browser_gate_required = true`
   - 校验 `spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 完整
   - 任一前提缺失时直接 fail-closed，不得启动伪 gate
2. **Execution context freeze**
   - 创建唯一 `BrowserQualityGateExecutionContext`
   - 锁定 `073.solution_snapshot` 的 provider/style truth
   - 锁定 `071` 的 visual/a11y foundation 底线
3. **Probe execution**
   - 依次运行 `playwright_smoke`、`visual_expectation`、`basic_a11y`、`interaction_anti_pattern_checks`
   - 每类检查都必须产出结构化 `BrowserQualityCheckResult`
4. **Failure classification**
   - 将各检查结果归入 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only`
   - 保持 blocker 与 advisory 的独立 reason codes
5. **Bundle materialization**
   - 生成唯一 `browser_quality_bundle`
   - 固定 scope binding、evidence refs 与 requirement linkage
6. **020 handoff**
   - 生成 `FrontendBrowserGateHandoff`
   - 把 spec 级 gate state、recheck/remediation hints 与 source linkage 交给 `020`

## 四类检查面的固定边界

### 1. `playwright_smoke`

- 必须验证当前实现的关键主路径是否真实可操作，而不是只检查页面可打开
- 必须至少能暴露主路径是否卡死、关键操作是否无法触发、关键反馈是否完全缺失
- Phase 1 不要求把整套业务流程都回放成端到端矩阵

### 2. `visual_expectation`

- 必须基于 `073.solution_snapshot` 的 `effective_provider / effective_style_pack / style_fidelity_status` 进行判定
- 至少覆盖关键区域可见性、明显布局断裂、文字溢出、遮挡、空白主视图
- 它是 requirement-linked 可执行检查，不是完整 visual regression 替代品

### 3. `basic_a11y`

- 必须至少消费 `071` 已冻结的 `error/status perceivability`、`accessible naming / semantics`、`keyboard reachability`、`focus continuity`
- 不得发明第二套 a11y truth，也不得扩张成完整 WCAG 平台
- 必须把缺乏基础语义、键盘不可达或焦点连续性断裂等问题以 evidence-backed 方式输出

### 4. `interaction_anti_pattern_checks`

- Phase 1 只允许覆盖 machine-checkable 反模式：
  - `main_action_not_visible`
  - `critical_feedback_out_of_context`
  - `interaction_dead_end`
  - `focus_trap`
  - `destructive_action_defaulted`
  - `text_overflow_or_occlusion`
- 每个 blocker 都必须绑定 probe、anchor 与 evidence
- 不得把主观审美评价、品牌偏好或完整交互动效平台混入本检查面

## Failure Honesty And 020 Handoff Rules

- `evidence_missing`：缺少完成 gate 所需证据或 scope linkage；必须提示补证据或重新执行 gate prerequisite，不得伪装成代码 blocker
- `transient_run_failure`：运行环境或浏览器执行瞬时失败；必须保留重跑/复查语义，不得直接断言前端质量不合格
- `actual_quality_blocker`：真实质量问题；必须携带 blocker reason、anchor、evidence 与 requirement linkage
- `advisory_only`：非阻断问题；必须保留建议和 evidence，但不得让 gate 误判为 blocked
- `020` 只允许消费：
  - `FrontendBrowserGateHandoff.execute_gate_state`
  - `blockers`
  - `recheck_required`
  - `remediation_hints`
  - `source_linkage_refs`
- `102` 不得把 browser gate 缺失或 advisory 包装成 program 级 ready，也不得让 `020` 去反向猜 bundle scope

## 验证场景

1. Given apply result 为 `apply_succeeded_pending_browser_gate` 且四类检查均 `pass`，When 系统生成 bundle，Then `overall_gate_status` 必须为 `passed`，并向 `020` 交付 `execute_gate_state=ready`
2. Given smoke 或 visual 证据缺失，When gate 运行结束，Then 结果必须显式为 `evidence_missing` / `incomplete`，而不是 `actual_quality_blocker`
3. Given 浏览器运行中发生瞬时崩溃，When 系统分类结果，Then 必须得到 `transient_run_failure` 并保留 recheck 语义
4. Given 检测到主操作不可见或空白主视图，When 系统生成结果，Then 必须得到带 anchor/evidence 的 `actual_quality_blocker`
5. Given 仅发现不阻断的可读性或轻微布局建议，When 系统生成 bundle，Then 必须得到 `passed_with_advisories`，而不是 `blocked`

## 功能需求

| ID | 需求 |
|----|------|
| FR-102-001 | `102` 必须作为 `101` 下游的 browser quality gate child work item 被正式定义 |
| FR-102-002 | `102` 必须明确 browser gate 只消费 `101.ManagedDeliveryApplyResult`、`073.solution_snapshot`、`071` visual/a11y foundation 与 `020` execute/recheck/remediation vocabulary |
| FR-102-003 | browser gate 只能在 `ManagedDeliveryApplyResult.result_status = apply_succeeded_pending_browser_gate`、`browser_gate_required = true` 且 source linkage 完整时启动 |
| FR-102-004 | browser quality gate 必须运行在真实浏览器中；静态代码检查、纯 DOM snapshot 或页面可打开都不能替代 mandatory gate |
| FR-102-005 | browser quality gate 至少必须包含 `playwright_smoke`、`visual_expectation`、`basic_a11y`、`interaction_anti_pattern_checks` 四类检查面 |
| FR-102-006 | `playwright_smoke` 必须验证关键主路径真实可操作，而不是只检查页面能打开 |
| FR-102-007 | `visual_expectation` 必须绑定 `073.solution_snapshot` 中已确认的 `effective_provider / effective_style_pack / style_fidelity_status`，并基于关键区域可见性、布局断裂、文字溢出、遮挡、空白主视图等规则生成 evidence-backed verdict |
| FR-102-008 | `basic_a11y` 必须至少消费 `071` 已冻结的 perceivability / semantics / keyboard / focus 底线，不得额外发明第二套 a11y truth |
| FR-102-009 | `interaction_anti_pattern_checks` Phase 1 只允许覆盖 machine-checkable 反模式：主操作不可见、关键反馈脱离上下文、交互路径死胡同、异常 focus trap、destructive action 默认化、文本溢出/遮挡 |
| FR-102-010 | 每一类检查都必须产出结构化 `BrowserQualityCheckResult`，并为 blocker/advisory 保留 anchor、evidence、requirement linkage 与 reason codes |
| FR-102-011 | browser quality gate 必须产出结构化 `browser_quality_bundle`，至少包含 trace、截图、四类检查 verdict、scope binding、requirement linkage 与 blocker/advisory reason codes |
| FR-102-012 | `browser_quality_bundle` 必须满足 `one bundle == one active spec scope == one managed frontend target`；`020` 不得把 latest bundle 伪装成项目级全局结论 |
| FR-102-013 | browser quality gate 失败时，系统必须明确区分 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only`，不得全部混报成“前端测试失败” |
| FR-102-014 | `advisory_only` 明确定义为非阻断结果，必须附带通俗下一步建议，不得让 execute gate 误判为 blocked |
| FR-102-015 | `evidence_missing` 与 `transient_run_failure` 必须保留 recheck 语义；`actual_quality_blocker` 必须保留 remediation hint 与 source linkage；三者不得互相伪装 |
| FR-102-016 | browser gate 必须生成 `FrontendBrowserGateHandoff`，并只使用 `020` 可消费的 execute/recheck/remediation/source-linkage 字段面 |
| FR-102-017 | `FrontendBrowserGateHandoff.execute_gate_state=ready` 只表示当前 spec 的 browser gate 条件满足，不得等同于 program 级最终 ready verdict |
| FR-102-018 | `102` 不得把 remediation engine、自动修复、自动重跑、多浏览器矩阵、完整 visual regression 平台或完整 WCAG 平台混入 browser gate 本身 |
| FR-102-019 | `102` 当前只 formalize browser gate contract，不得声称 Playwright runner、quality probes 或 `020` program aggregation 已在本切片实现 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-102-001 | reviewer 能从 `102` 直接读出 browser gate 的启动条件、四类检查面与 failure classification，而无需回到 `095` 或 `101` 临时拼接 |
| SC-102-002 | maintainer 能直接确认 `browser_quality_bundle` 与 `020` handoff 都保持单一 scope/target/source linkage 真值 |
| SC-102-003 | operator 能从 `102` 直接区分 `evidence_missing / transient_run_failure / actual_quality_blocker / advisory_only` 的下一步动作 |
| SC-102-004 | 当前规格不会让人误以为 remediation engine、多浏览器矩阵或 program 级最终 readiness aggregation 已在本批实现 |

## 后续实现拆分建议

`102` 之后如果继续深化，优先应落在 browser gate 的实现与回放层，而不是重写主合同：

1. **Browser Gate Probe Runtime**
   - 负责 Playwright probe orchestration、trace/screenshot materialization 与 per-check result 写出
2. **Browser Gate Recheck And Remediation Binding**
   - 负责把 `102` 的 `incomplete / blocked / advisory` 结果绑定到 `020` recheck/remediation replay
