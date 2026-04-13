# 功能规格：Frontend Mainline Browser Gate Recheck Remediation Binding Baseline

**功能编号**：`104-frontend-mainline-browser-gate-recheck-remediation-binding-baseline`  
**创建日期**：2026-04-13  
**状态**：已冻结（formal baseline）  
**输入**：[`../020-frontend-program-execute-runtime-baseline/spec.md`](../020-frontend-program-execute-runtime-baseline/spec.md)、[`../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`](../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md)、[`../102-frontend-mainline-browser-quality-gate-baseline/spec.md`](../102-frontend-mainline-browser-quality-gate-baseline/spec.md)、[`../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md`](../103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md)

> 口径：`104` 冻结的不是 browser gate contract、不是 probe runtime、不是 auto-fix engine，也不是无限重跑 loop，而是 `102/103` 结果进入 `020` execute vocabulary 的 recheck/remediation binding 本身。它只回答五个问题：`browser_quality_bundle + FrontendBrowserGateHandoff` 如何生成单一 execute handoff decision；`incomplete / blocked / passed_with_advisories / passed` 如何稳定映射到 `ready / blocked / recheck_required / needs_remediation`；哪些结果必须保留 bounded recheck 语义，哪些结果只能给 remediation hint；`blockers / remediation_hints / source_linkage_refs` 如何保持 spec 级可追溯；以及 replay request 的边界如何被冻结而不滑成自动修复或后台循环。

## 问题定义

`102` 已冻结 browser gate contract、失败分级与 `FrontendBrowserGateHandoff` 的最小字段面，`103` 进一步冻结了 probe runtime、artifact materialization 与 bundle input。

但当前链路里仍缺少一份独立 formal baseline，回答以下问题：

- `browser_quality_bundle.overall_gate_status` 与 per-check verdict 到底如何稳定映射到 `020` 的 execute gate vocabulary
- `evidence_missing`、`transient_run_failure`、`actual_quality_blocker`、`advisory_only` 何时触发 `recheck_required`，何时触发 `needs_remediation`
- `020` 所消费的 `blockers / remediation_hints / source_linkage_refs` 应如何从 browser gate 结果继承，而不是在 execute runtime 反向猜测
- 什么叫 bounded replay request，什么情况下允许要求重跑 browser gate，什么情况下只能留下 remediation hint
- stale bundle、scope mismatch、linkage 缺失或结果不自洽时，系统应 fail-closed 到哪一种 execute handoff state

如果不先冻结 `104`，后续实现会快速滑向四种常见偏差：

- 把 `incomplete`、`blocked`、`advisory` 全部压成一个“browser gate failed”，让 `020` 无法区分重跑和修复
- 让 `020` 直接猜测 browser bundle 与 apply/source linkage 的关系，形成第二套 handoff truth
- 把 recheck binding 扩张成后台自动循环，或把 remediation hint 偷渡成默认 auto-fix
- 遇到 stale bundle、scope mismatch 或 linkage 缺失时继续放行 execute，导致 spec 级 readiness 失真

因此，`104` 的目标是把 browser gate 的结果绑定层冻结成最小但严格的正式合同：先锁定 handoff decision、recheck/remediation mapping、bounded replay request 与 fail-closed 规则，再把自动修复、自动重跑 orchestration 与 program 级聚合继续留在后续切片。

## 范围

- **覆盖**：
  - 将 browser gate recheck/remediation binding 正式定义为 `103` 下游独立 child work item
  - 锁定 `browser_quality_bundle + FrontendBrowserGateHandoff -> 020` execute handoff decision 的最小映射规则
  - 锁定 `recheck_required`、`needs_remediation`、`blocked`、`ready` 的 browser-gate-side 触发边界
  - 锁定 `ProgramFrontendRecheckBinding`、`ProgramFrontendRemediationBinding` 与 `BrowserGateReplayRequest` 的最小字段面
  - 锁定 stale bundle、scope mismatch、source linkage 缺失与 result inconsistency 的 fail-closed 规则
- **不覆盖**：
  - 改写 `102` 已冻结的 gate eligibility、bundle schema 或 failure taxonomy
  - 改写 `103` 已冻结的 probe runtime、artifact store、trace/screenshot materialization 或 execution order
  - 在本 work item 中实现 auto-fix、自动重跑 loop、后台 replay orchestration、program aggregation 或 `src/` / `tests/` 代码
  - 把 advisory 升级为阻断，或把 remediation hint 伪装成已执行修复

## 已锁定决策

- `104` 只能消费 `102.browser_quality_bundle`、`102.FrontendBrowserGateHandoff`、`103` runtime evidence 继承结果与 `020` execute vocabulary；不得另造第三套 readiness truth
- `passed` 与 `passed_with_advisories` 只能映射到 spec 级 `ready`，不得伪造 program 级最终 ready
- `evidence_missing` 与 `transient_run_failure` 主导的 `incomplete` 结果必须优先映射到 `recheck_required`，而不是误判为真实质量 blocker
- `actual_quality_blocker` 主导的 `blocked` 结果必须优先映射到 `needs_remediation`；只有 source/scope/linkage 不可信时才允许 fail-closed 到 `blocked`
- `BrowserGateReplayRequest` 只是一份 bounded recheck handoff，不等于自动调度器、后台循环或默认 auto-fix

## 用户故事与验收

### US-104-1 — Framework Maintainer 需要 browser gate 结果绑定层有独立 formal truth

作为**框架维护者**，我希望 browser gate 的 recheck/remediation binding 在 formal docs 中有独立 child work item，以便 `102/103` 的结果映射、`020` vocabulary 与 bounded replay boundary 不再混在 contract 或 runtime 里。

**验收**：

1. Given 我查看 `104` formal docs，When 我追踪 browser gate 主线，Then 可以明确看到它位于 `103` 下游且只负责结果绑定  
2. Given 我审阅 `104` non-goals，When 我确认边界，Then 可以明确读到 auto-fix、自动重跑 loop 与 program aggregation 不在本工单内

### US-104-2 — Operator 需要知道何时重跑，何时修复

作为**operator**，我希望 browser gate 结束后系统能清楚告诉我是应该重跑 gate、修前端，还是仅记录 advisory，以便 `program --execute` 不会把所有问题都当成同一种失败。

**验收**：

1. Given bundle 主导状态为 `incomplete` 且原因来自 `evidence_missing` 或 `transient_run_failure`，When 我查看 handoff，Then 必须得到 `execute_gate_state=recheck_required`  
2. Given bundle 主导状态为 `blocked` 且原因来自 evidence-backed `actual_quality_blocker`，When 我查看 handoff，Then 必须得到 `execute_gate_state=needs_remediation`

### US-104-3 — Reviewer 需要 stale 或不自洽结果 fail-closed

作为**reviewer**，我希望 stale bundle、scope mismatch、source linkage 缺失与结果不自洽在 formal docs 中被明确 fail-closed，以便 execute runtime 不会放行不可信的 browser gate 结果。

**验收**：

1. Given bundle 的 `spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 与 handoff 或 apply result 不一致，When 结果绑定发生，Then 必须 fail-closed 为 `blocked`  
2. Given `overall_gate_status=passed` 但某个 check verdict 仍为 `actual_quality_blocker`，When 系统执行绑定，Then 必须被判为 result inconsistency，且不得输出 `ready`

## 关键实体

### 1. BrowserGateExecuteHandoffDecision

`BrowserGateExecuteHandoffDecision` 是 `104` 唯一的 browser-gate-side execute decision 真值。

其最小字段至少包括：

- `decision_id`
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
- `decision_reason`
  - `all_checks_passed`
  - `advisory_only`
  - `evidence_missing`
  - `transient_run_failure`
  - `actual_quality_blocker`
  - `scope_or_linkage_invalid`
  - `result_inconsistency`
- `blockers`
- `recheck_required`
- `remediation_hints`
- `source_linkage_refs`
- `generated_at`

规则：

- `execute_gate_state` 必须只使用 `020` 可消费 vocabulary
- `decision_reason` 必须能回溯到 bundle 主导状态或 fail-closed condition
- `ready` 只允许出现在 `all_checks_passed` 或 `advisory_only` 两类决策原因

### 2. ProgramFrontendRecheckBinding

`ProgramFrontendRecheckBinding` 是 browser gate 交给 `020` 的 bounded recheck handoff。

其最小字段至少包括：

- `recheck_binding_id`
- `apply_result_id`
- `bundle_id`
- `spec_dir`
- `readiness_subject_id`
- `recheck_required`
- `recheck_reason_codes`
- `replay_scope`
  - `browser_gate`
- `replay_trigger`
  - `evidence_missing`
  - `transient_run_failure`
  - `dependency_refresh_required`
- `recheck_instructions`
- `source_linkage_refs`

规则：

- 只有 `execute_gate_state=recheck_required` 时，才允许 materialize `ProgramFrontendRecheckBinding`
- `replay_scope` 在 Phase 1 固定为 `browser_gate`，不得扩张成 apply runtime、program 全量 replay 或无限循环
- `recheck_instructions` 只能描述补证据、重跑 gate prerequisite 或重新执行 browser gate；不得暗示自动修复已发生

### 3. ProgramFrontendRemediationBinding

`ProgramFrontendRemediationBinding` 是 browser gate 交给 `020` 的 remediation hint handoff。

其最小字段至少包括：

- `remediation_binding_id`
- `apply_result_id`
- `bundle_id`
- `spec_dir`
- `readiness_subject_id`
- `needs_remediation`
- `blocking_reason_codes`
- `remediation_hints`
- `artifact_refs`
- `anchor_refs`
- `source_linkage_refs`

规则：

- 只有 `execute_gate_state=needs_remediation` 或 fail-closed `blocked` 时，才允许 materialize remediation binding
- `remediation_hints` 必须继承 `102/103` 中 evidence-backed blocker context；不得只写“修一下前端”
- fail-closed `blocked` 可以只有 linkage/scope diagnostics，但不得伪装成 evidence-backed quality blocker

### 4. BrowserGateReplayRequest

`BrowserGateReplayRequest` 是 `104` 对“是否允许重跑 browser gate”给出的唯一 replay truth。

其最小字段至少包括：

- `replay_request_id`
- `apply_result_id`
- `bundle_id`
- `requested_scope`
  - `browser_gate`
- `requested_reason`
  - `evidence_missing`
  - `transient_run_failure`
  - `scope_linkage_refresh`
- `blocking_preconditions`
- `requested_at`

规则：

- replay request 只是一份请求，不等于后台调度已启动
- `requested_scope` 在本切片固定为 `browser_gate`
- 若需要重新生成 apply result 或更新 source linkage，只能写成 `blocking_preconditions`，不得直接触发上游 runtime

## Mapping Rules

### 1. Bundle status 到 execute gate state 的主映射

| browser bundle truth | 主要条件 | execute gate state | decision reason |
|---|---|---|---|
| `overall_gate_status=passed` | 四类检查均 `pass` | `ready` | `all_checks_passed` |
| `overall_gate_status=passed_with_advisories` | 仅含 `advisory_only` | `ready` | `advisory_only` |
| `overall_gate_status=incomplete` | 主导原因是 `evidence_missing` | `recheck_required` | `evidence_missing` |
| `overall_gate_status=incomplete` | 主导原因是 `transient_run_failure` | `recheck_required` | `transient_run_failure` |
| `overall_gate_status=blocked` | 主导原因是 `actual_quality_blocker` | `needs_remediation` | `actual_quality_blocker` |

### 2. Fail-closed 条件

以下任一条件出现时，不得输出 `ready` 或 `needs_remediation` 的伪可信结果，而必须输出 `execute_gate_state=blocked`：

- bundle 与 handoff 的 `spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 不一致
- `apply_result_id`、`bundle_id` 或 `source_linkage_refs` 缺失，导致无法确认来源
- `overall_gate_status` 与 per-check verdict 不自洽
- handoff 声称 `ready`，但 bundle 仍包含 `evidence_missing`、`transient_run_failure` 或 `actual_quality_blocker`

此时 `decision_reason` 必须固定为 `scope_or_linkage_invalid` 或 `result_inconsistency`，并只允许输出诊断性 blockers / remediation hints。

## Runtime Truth Order

结果绑定层的单向顺序固定如下：

1. **Bundle receipt**
   - 接收 `browser_quality_bundle` 与 `FrontendBrowserGateHandoff`
   - 校验 `apply_result_id / spec_dir / attachment_scope_ref / managed_frontend_target / readiness_subject_id` 一致
2. **Consistency validation**
   - 校验 `overall_gate_status` 与 per-check verdict 一致
   - 校验 `source_linkage_refs` 可追溯
3. **Decision materialization**
   - 生成唯一 `BrowserGateExecuteHandoffDecision`
   - 只写 `020` 可消费的 execute state、recheck_required、blockers 与 remediation hints
4. **Recheck binding**
   - 若决策为 `recheck_required`，生成 `ProgramFrontendRecheckBinding`
   - 必须同时生成 `BrowserGateReplayRequest`
5. **Remediation binding**
   - 若决策为 `needs_remediation`，生成 `ProgramFrontendRemediationBinding`
   - 若决策为 fail-closed `blocked`，只允许生成 diagnostics-first remediation binding
6. **020 handoff**
   - 将 decision + optional recheck/remediation binding 暴露给 `020`
   - 不得在本层继续调度自动重跑或自动修复

## Binding Honesty Rules

- `advisory_only` 只能留下 advisory-level `remediation_hints`，不得把 `execute_gate_state` 升级成 `needs_remediation`
- `evidence_missing` 不能因为 hint 看起来像代码问题就被误报为 `actual_quality_blocker`
- `transient_run_failure` 必须保留 replay 语义，不得在无证据情况下要求代码修复
- `actual_quality_blocker` 必须带上 blocker reason、artifact refs、anchor refs 与 source linkage；否则不得映射为 `needs_remediation`
- fail-closed `blocked` 只表示当前 handoff 不可信，不表示已经发现真实前端质量 blocker

## 验证场景

1. Given bundle `overall_gate_status=passed` 且四类检查均 `pass`，When 结果绑定发生，Then 必须输出 `execute_gate_state=ready`
2. Given bundle `overall_gate_status=passed_with_advisories` 且只含 `advisory_only`，When 结果绑定发生，Then 必须输出 `ready`，并保留 advisory hints 但不生成 remediation binding
3. Given bundle `overall_gate_status=incomplete` 且视觉截图缺失，When 结果绑定发生，Then 必须输出 `recheck_required`，并生成 `BrowserGateReplayRequest`
4. Given bundle `overall_gate_status=blocked` 且 smoke/visual evidence 指向真实质量问题，When 结果绑定发生，Then 必须输出 `needs_remediation`，并保留 blocker linkage
5. Given bundle scope 与 handoff scope 不一致，When 结果绑定发生，Then 必须 fail-closed 为 `blocked`，且不得把结果伪装成 quality blocker

## 功能需求

| ID | 需求 |
|----|------|
| FR-104-001 | `104` 必须作为 `103` 下游的 browser gate recheck/remediation binding child work item 被正式定义 |
| FR-104-002 | `104` 必须明确结果绑定层只消费 `102.browser_quality_bundle`、`102.FrontendBrowserGateHandoff`、`103` artifacts lineage 与 `020` execute vocabulary |
| FR-104-003 | `104` 必须定义唯一 `BrowserGateExecuteHandoffDecision`，并只使用 `ready / blocked / recheck_required / needs_remediation` 四种 execute gate state |
| FR-104-004 | `overall_gate_status=passed` 必须映射为 `execute_gate_state=ready`，且不得引入额外阻断 |
| FR-104-005 | `overall_gate_status=passed_with_advisories` 必须映射为 `ready`，并保留 advisory hints 但不得触发 remediation binding |
| FR-104-006 | `evidence_missing` 或 `transient_run_failure` 主导的 `incomplete` 必须映射为 `recheck_required` |
| FR-104-007 | evidence-backed `actual_quality_blocker` 主导的 `blocked` 必须映射为 `needs_remediation` |
| FR-104-008 | stale bundle、scope mismatch、source linkage 缺失与 result inconsistency 必须 fail-closed 为 `blocked`，不得输出 `ready` |
| FR-104-009 | `ProgramFrontendRecheckBinding` 只能在 `execute_gate_state=recheck_required` 时 materialize，且 replay scope 固定为 `browser_gate` |
| FR-104-010 | `BrowserGateReplayRequest` 必须明确是 bounded request，而不是后台自动循环或默认调度器 |
| FR-104-011 | `ProgramFrontendRemediationBinding` 必须继承 blocker artifact、anchor 与 source linkage；不得只写泛化修复建议 |
| FR-104-012 | advisory-only 结果不得升级为 `needs_remediation` 或 `blocked` |
| FR-104-013 | fail-closed `blocked` 必须与 evidence-backed quality blocker 在 wording 与 reason code 上保持区分 |
| FR-104-014 | `104` 不得在本层实现 auto-fix、auto-recheck orchestration、program aggregation 或 `src/` / `tests/` 代码 |
| FR-104-015 | `104` 当前只 formalize browser gate result binding contract，不得声称 runtime replay、auto-fix engine 或 CLI wiring 已在本切片实现 |

## 成功标准

| ID | 标准 |
|----|------|
| SC-104-001 | reviewer 能从 `104` 直接读出 bundle/handoff 到 `020` execute state 的稳定映射，而无需回到 `020` 或 `102` 临时拼接 |
| SC-104-002 | maintainer 能直接确认 `recheck_required` 与 `needs_remediation` 的边界不再混淆 |
| SC-104-003 | operator 能从 `104` 直接理解什么时候该重跑 browser gate，什么时候该修代码，什么时候只是 advisory |
| SC-104-004 | 当前规格不会让人误以为 auto-fix、后台 replay loop 或 program aggregation 已在本批实现 |

## 后续实现拆分建议

`104` 之后如果继续深化，优先应落在代码实现与 `020` wiring，而不是再扩文档合同：

1. **Browser Gate Result Binding Runtime**
   - 负责在 `core` 中 materialize handoff decision、recheck binding 与 remediation binding
2. **Program Execute Browser Gate Wiring**
   - 负责把 `104` 的 decision surface 接到 `020` 已有 execute preflight / recheck handoff

---
related_doc:
  - "specs/020-frontend-program-execute-runtime-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/102-frontend-mainline-browser-quality-gate-baseline/spec.md"
  - "specs/103-frontend-mainline-browser-gate-probe-runtime-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
