# 功能规格：Frontend Mainline Managed Delivery Apply Runtime Implementation Baseline

**功能编号**：`123-frontend-mainline-managed-delivery-apply-runtime-implementation-baseline`
**创建日期**：2026-04-13
**状态**：formal baseline 已冻结；runtime implementation 已完成首批切片
**输入**：[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)、[`../100-frontend-mainline-action-plan-binding-baseline/spec.md`](../100-frontend-mainline-action-plan-binding-baseline/spec.md)、[`../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md`](../101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md)、[`../120-open-capability-tranche-backlog-baseline/tasks.md`](../120-open-capability-tranche-backlog-baseline/tasks.md)、[`../../src/ai_sdlc/core/program_service.py`](../../src/ai_sdlc/core/program_service.py)、[`../../src/ai_sdlc/cli/program_cmd.py`](../../src/ai_sdlc/cli/program_cmd.py)、[`../../tests/unit/test_program_service.py`](../../tests/unit/test_program_service.py)、[`../../tests/integration/test_cli_program.py`](../../tests/integration/test_cli_program.py)

> 口径：`123` 是 `120/T11` 的 implementation carrier，也是 `101` 的窄版 apply executor 写面。它只把 confirmed `frontend_action_plan` 的第一批可执行动作落成真实 runtime：execution session、ledger bootstrap、依赖排序、partial-progress honesty 与 apply result。`123` 不实现 `dependency_install`、file writer、browser gate、program readiness 聚合、自动 rollback/retry/cleanup，也不把 `122` host ingress truth sync 混进 apply executor 本体。

> 当前状态：仅 `123` implementation carrier/docs 已建立；runtime implementation 尚未完成或验证。后续即使 apply 成功，也不等于 frontend delivery 完成、browser gate 通过或 readiness ready。

## 问题定义

`101` 已经把 managed delivery apply runtime 的 formal truth 冻结出来，但它本身明确禁止改 `src/` / `tests/`。这意味着仓库当前仍缺一条合法实现写面去承接 `120/T11`：

- confirmed `frontend_action_plan` 还不能转成唯一 execution session
- `delivery_action_ledger` 还没有实际的创建/更新 runtime
- action ordering、dependency blocker、partial progress 与 manual recovery 还停留在 wording
- apply 成功、blocked、partial failure 与 pending browser gate 的诚实语义还没有统一结果面

如果继续跳过这层，后续 `T12/T13` 会建立在空心主线上：installer、writer 和 browser gate 都会被迫自己猜 action 执行 truth。`123` 的目标就是先把最小但严格的 apply executor 主线落成 runtime，并把后续动作继续留给下游 tranche。

## 范围

- **覆盖**：
  - 新建 `123` formal docs 与 execution log
  - 新增 `ConfirmedActionPlanExecutionView`、`DeliveryApplyDecisionReceipt`、`ManagedDeliveryExecutionSession` 与 `ManagedDeliveryApplyResult` 的 runtime model
  - 新增窄版 `managed_delivery_apply` executor，落实 session bootstrap、ledger bootstrap、dependency graph、before/after state capture 与 apply result 组装
  - 在 `ProgramService` 中接入薄的 apply request/result surface
  - 在 `program_cmd.py` 中接入最小 preview/execute surface
  - 补 focused unit/integration tests，锁定 fail-closed 与 honest result semantics
  - 注册 `123` 到 `program-manifest.yaml`，并将 `.ai-sdlc/project/config/project-state.yaml` 推进到 `124`
- **不覆盖**：
  - 改写 `101` 的 formal contract 或回到 planner 重写 `frontend_action_plan`
  - 实现 `dependency_install`、`artifact_generate`、`workspace_integration`、`browser_dependency_provision`
  - 实现 browser gate、`020` execute aggregation、program readiness `ready`
  - 实现自动 rollback、自动 retry、自动 cleanup
  - 扩大 managed target 边界或默认接管旧 frontend 根目录

## 已锁定决策

- `123` 只实现 review 收敛后的窄版 `B-lite` apply executor，不采用把逻辑塞进 `program_service.py` / `program_cmd.py` 的大杂烩做法。
- 第一批允许真实执行的 `action_type` 只包括：
  - `runtime_remediation`
  - `managed_target_prepare`
- `dependency_install`、`artifact_generate`、`workspace_integration`、`browser_dependency_provision` 在 `123` 中都必须诚实标记为当前 executor scope 未覆盖；不得伪装成成功或自动跳过。
- apply runtime 必须引入 `plan_fingerprint`，并在 execution view、decision receipt、execution session 与 apply result 间保持一致；任一不一致都必须 `blocked_before_start`。
- ledger 必须在决策校验通过后创建，并先于真实 action 执行写入 action-level truth；不得只在会话结束时补总结果。
- dependency graph 必须基于全部 selected mutate actions 建立，而不是只基于 allowlist action；否则 unsupported dependency 会被错误绕过。
- apply success 的 handoff vocabulary 必须继续沿用 `101` 的 `apply_succeeded_pending_browser_gate`；不得在 implementation carrier 中另起 token。
- rollback/retry/cleanup 在 `123` 中只允许记录 structured refs 与 manual recovery boundary；不得声称已经真正执行。
- user-facing apply headline 不得只输出 raw success token；必须同时明确：
  - delivery is not complete
  - browser gate has not run
  - unsupported / downstream not-run actions are listed in the ledger

## 用户故事与验收

### US-123-1 — Operator 需要诚实的 apply 执行结果

作为 **operator**，我希望 confirmed action plan 执行后能明确看到哪些 action 真正执行了、哪些被阻断、哪些只是当前切片未覆盖，这样我不会把 “apply 成功” 误读成 “前端已经完全交付完成”。

**验收**：

1. Given selected required action 中包含当前切片未支持的 mutate action，When 我尝试执行 apply，Then 结果必须 `blocked_before_start` 或同等 fail-closed 状态，而不是部分执行后宣称成功
2. Given allowlist action 已执行成功，When apply result 生成，Then 状态必须是 `apply_succeeded_pending_browser_gate`

### US-123-2 — Reviewer 需要 ledger 与 partial-progress truth 不被压扁

作为 **reviewer**，我希望 action-level ledger、failure classification 与 partial progress 在 runtime 中被单独保留，这样后续 browser gate、manual recovery 或 retry baseline 不会丢失真实执行边界。

**验收**：

1. Given 某个 action 已成功、后续 action 失败，When executor 结束，Then ledger 必须保留 succeeded/failed action truth，而不是把整次运行压成 “未执行”
2. Given before-state 捕获失败，When executor 准备执行 action，Then 该 action 不得继续执行

### US-123-3 — Maintainer 需要 apply scope 与 host ingress gate 分离

作为 **maintainer**，我希望 `123` 只消费已经通过最低 mutate delivery 门禁的 host ingress truth，而不是在 executor 内部重新猜测 `installed / acknowledged / verified` 语义，这样 T00/T11/T12 的边界不会再次混乱。

**验收**：

1. Given host ingress 仍未达到 mutating delivery 阈值，When 尝试进入 `123` execute path，Then 系统必须在 apply 前 fail-closed
2. Given host ingress 已通过最低阈值，When apply 结果输出，Then 结果中不得重新引入 `installed / acknowledged / verified` 混合语义

## 功能需求

| ID | 需求 |
|----|------|
| FR-123-001 | `123` 必须作为 `101` 的 runtime implementation carrier，为 `src/` / `tests/` 改动提供合法写面 |
| FR-123-002 | 系统必须新增 `ConfirmedActionPlanExecutionView`，并保证它只是 confirmed plan 的 runtime projection，而不是第二套 planner truth |
| FR-123-003 | 系统必须在 apply runtime 中校验 `decision receipt / selected action ids / required action selection / risk acknowledgement / second confirmation / plan_fingerprint`；任一不满足都必须 `blocked_before_start` |
| FR-123-004 | 系统必须在真实 action 执行前创建 `delivery_action_ledger`，并按 action 粒度写入 `queued_not_started / running / succeeded / failed / blocked / skipped` truth 与 `failure_classification` |
| FR-123-005 | 系统必须基于全部 selected mutate actions 建 dependency graph，并将 `required_unsupported`、`selected_optional_unsupported`、`dependency_blocked_by_unsupported` 与 `user_deselected_optional` 区分开 |
| FR-123-006 | 第一批真实执行的 `action_type` 只能是 `runtime_remediation` 与 `managed_target_prepare` |
| FR-123-007 | 系统必须在 allowlist action 执行前写入 `before_state`，执行后写入 `after_state + result_status`；若 `before_state` 写入失败，该 action 不得执行 |
| FR-123-008 | apply result 必须诚实暴露 executed / succeeded / failed / blocked / skipped action ids、partial progress、manual recovery boundary、rollback/retry/cleanup refs recorded-only，以及 `browser_gate_required=true` |
| FR-123-009 | apply result / CLI headline 必须同时暴露 `delivery is not complete`、`browser gate has not run` 与 unsupported/downstream not-run actions list，不得只输出 raw success token |
| FR-123-010 | 系统不得把 `apply_succeeded_pending_browser_gate` 误报为最终交付成功、browser gate 通过或 program readiness `ready` |
| FR-123-011 | `123` 不得实现 `dependency_install`、file writer、browser gate、program execute aggregation、自动 rollback/retry/cleanup |
| FR-123-012 | `ProgramService` 与 `program_cmd.py` 只允许提供薄 apply request/result wiring；不得把 executor scope、browser gate 或 installer scope 混成一层 |
| FR-123-013 | `123` 只消费既有 mutate-delivery threshold 的 host ingress truth；未达阈值时必须在 apply 前 `blocked_before_start`，不得在本层重建 `installed / acknowledged / verified` 状态机 |
| FR-123-014 | `tests/unit/test_managed_delivery_apply.py`、`tests/unit/test_program_service.py` 与 `tests/integration/test_cli_program.py` 必须覆盖 fail-closed、dependency blocker、partial progress、manual recovery boundary 与 pending browser gate 语义 |

## 123 Implementation Exit Criteria

- **SC-123-001**：confirmed `frontend_action_plan` 已能转成唯一 execution session
- **SC-123-002**：`delivery_action_ledger` 已在真实 mutate action 前创建，并沿用既有 `action_id`
- **SC-123-003**：required unsupported / dependency blocked / partial progress / manual recovery 在 runtime 中有稳定 truth
- **SC-123-004**：focused unit/integration tests 通过，且 `uv run ai-sdlc verify constraints`、`uv run ai-sdlc program validate` 与 `git diff --check` 通过

---
related_doc:
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
  - "specs/100-frontend-mainline-action-plan-binding-baseline/spec.md"
  - "specs/101-frontend-mainline-managed-delivery-apply-runtime-baseline/spec.md"
  - "specs/120-open-capability-tranche-backlog-baseline/tasks.md"
  - "src/ai_sdlc/core/program_service.py"
  - "src/ai_sdlc/cli/program_cmd.py"
  - "tests/unit/test_program_service.py"
  - "tests/integration/test_cli_program.py"
frontend_evidence_class: "framework_capability"
---
