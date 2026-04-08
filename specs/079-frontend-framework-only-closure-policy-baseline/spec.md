# 功能规格：Frontend Framework-Only Closure Policy Baseline

**功能编号**：`079-frontend-framework-only-closure-policy-baseline`  
**创建日期**：2026-04-08  
**状态**：已冻结（formal baseline）  
**输入**：[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../076-frontend-p1-root-close-sync-baseline/spec.md`](../076-frontend-p1-root-close-sync-baseline/spec.md)、[`../077-frontend-contract-observation-backfill-playbook-baseline/spec.md`](../077-frontend-contract-observation-backfill-playbook-baseline/spec.md)、[`../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md`](../078-frontend-contract-sample-selfcheck-fallback-clarification-baseline/spec.md)

> 口径：`079` 不是新的 root close-sync carrier，也不是对 `068` ~ `071` 的 retroactive close。它只冻结一条 policy：当仓库本身是 framework-only repository、并不承载真实业务前端实现时，相关 work item 的“框架能力完成”与“消费方实现证据齐备”必须被明确拆层，不能再被要求落到同一个 close 语义里。

## 问题定义

当前仓库已经冻结了两条都成立的 truth：

- `065` / `078`：框架仓库可以通过 sample self-check 证明 scanner/export/gate 主线可运行
- `076` / `077`：`068` ~ `071` 当前仍缺真实 `frontend_contract_observations`，因此 root truth 不能伪装成 consumer implementation 已完成

冲突不在实现层，而在 closure policy：

- 当前这些前端 P1 work item 实际编写的是框架能力、治理和 gate 语义
- 但 close 面又要求真实消费方页面实现证据
- 框架仓库本身没有真实业务前端代码，因此这两类证据不可能由同一仓库同时自然产出

如果不单独冻结 policy，后续只会反复在三种错误之间摆动：

- 为了“关单”伪造外部实现 evidence
- 为了“诚实”一直把 framework capability work item 停在永远不能 close 的状态
- 把 sample self-check 偷换成真实实现 evidence

因此，`079` 需要冻结的不是新的状态机实现，而是一个更上游的 truth：

- framework-only repo 中，框架能力完成可以独立成立
- consumer implementation evidence 仍然是独立的下游接入事实
- 两者必须分层表达，不能继续绑成同一个 close 条件

## 范围

- **覆盖**：
  - 冻结 framework-only repository 下 frontend work item 的 closure policy 分层
  - 冻结 framework capability evidence 与 consumer implementation evidence 的边界
  - 冻结 sample self-check 在 framework capability close 中的合法角色
  - 冻结后续如何 rescope 类似 `068` ~ `071` work item 的原则
- **不覆盖**：
  - 修改 `program status`、`verify constraints`、runtime attachment 或 gate 实现
  - retroactively 改写 `068` ~ `071` 为已 close
  - 修改 `frontend-program-branch-rollout-plan.md`、`program-manifest.yaml`、`src/` 或 `tests/`
  - 发明新的 runtime status code，如 `framework-ready`

## 已锁定决策

- framework-only repository 中，框架能力 work item 的完成证据应来自：
  - formal docs
  - 框架代码/测试
  - sample self-check 或等价 framework self-check
- 真实 `frontend-contract-observations.json` 仍然只代表 consumer implementation evidence，不代表框架能力是否存在
- 缺少真实 consumer implementation evidence 时，不得伪造 active spec 已拥有真实页面实现
- 未来类似 `068` ~ `071` 的 work item，必须在设计阶段就拆清：
  - 哪些是 framework capability baseline
  - 哪些是 external consumer backfill / adoption evidence
- `079` 只冻结 policy，不直接更改现有 root rollout machine truth；若要改 root wording，必须另起后续 carrier 如实同步

## 用户故事与验收

### US-079-1 — Framework Maintainer 需要一个不会把框架能力永久卡死的 close policy

- **Given** 仓库只承载 framework 代码与规则，不承载真实业务前端页面
- **When** maintainer 完成框架能力实现、测试与 sample self-check
- **Then** `079` 必须明确这已经构成 framework capability complete，而不再要求同仓库同时产出真实 consumer artifact

### US-079-2 — Reviewer 需要避免把 sample self-check 误判成真实消费方证据

- **Given** sample self-check 已通过
- **When** reviewer 审核某个 frontend work item 是否具有 consumer implementation evidence
- **Then** `079` 必须明确答案仍是否定的，除非外部真实实现已生成 canonical artifact

### US-079-3 — Program Author 需要知道后续应该怎么拆 work item

- **Given** 后续还会出现类似 frontend contract / gate / diagnostics / rollout 的 framework-side work item
- **When** author 编写新 spec 或 root rollout
- **Then** `079` 必须明确 future work 应把 framework capability 与 consumer adoption evidence 分成不同层级，而不是塞进同一个 close gate

## 功能需求

| ID | 需求 |
|----|------|
| FR-079-001 | `079` 必须明确自己是 docs-only policy baseline，而不是 root close-sync carrier |
| FR-079-002 | `079` 必须明确 framework-only repository 不承载真实业务前端实现这一前提 |
| FR-079-003 | `079` 必须明确 framework capability evidence 与 consumer implementation evidence 是两类不同真值 |
| FR-079-004 | `079` 必须明确 sample self-check 只可用于 framework capability evidence，不可冒充 consumer implementation evidence |
| FR-079-005 | `079` 必须明确未来类似 `068` ~ `071` 的 work item 需要在 design 阶段拆成 framework baseline 与 external backfill / adoption evidence |
| FR-079-006 | `079` 必须明确当前 root machine truth 不会因本 policy baseline 自动改变 |
| FR-079-007 | `079` 不得发明新的 runtime status code 或修改现有 `src/` / `tests/` 实现 |
| FR-079-008 | `079` 必须将 `.ai-sdlc/project/config/project-state.yaml` 的 `next_work_item_seq` 从 `78` 推进到 `79` |

## Policy Split

- **Framework Capability Evidence**
  - 证明框架能力、规则、诊断、gate、CLI、artifact contract 已具备
  - 允许使用 sample self-check、单测、集成测试与 formal docs
- **Consumer Implementation Evidence**
  - 证明真实业务前端页面已按 contract 实现
  - 必须来自真实实现来源生成的 canonical `frontend-contract-observations.json`
- **Root Sync Responsibility**
  - 如需把现有 rollout wording 调整到新的 policy split，必须由单独 honesty-sync carrier 执行

## 成功标准

- **SC-079-001**：reviewer 能从 `079` 直接读出 framework capability complete 与 consumer implementation evidence 的边界
- **SC-079-002**：future frontend specs 不会再把 sample self-check 与真实 consumer artifact 混成一个 close 条件
- **SC-079-003**：`079` 不会伪造 `068` ~ `071` 已解除当前 root blocker
- **SC-079-004**：本轮 diff 仅新增 `079` formal docs 并把 `project-state.yaml` 推进到 `79`
