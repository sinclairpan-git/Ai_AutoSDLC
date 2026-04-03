# 功能规格：Frontend Contract Runtime Attachment Baseline

**功能编号**：`014-frontend-contract-runtime-attachment-baseline`  
**创建日期**：2026-04-03  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`../011-frontend-contract-authoring-baseline/spec.md`](../011-frontend-contract-authoring-baseline/spec.md)、[`../011-frontend-contract-authoring-baseline/plan.md`](../011-frontend-contract-authoring-baseline/plan.md)、[`../012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`../012-frontend-contract-verify-integration/plan.md`](../012-frontend-contract-verify-integration/plan.md)、[`../013-frontend-contract-observation-provider-baseline/spec.md`](../013-frontend-contract-observation-provider-baseline/spec.md)、[`../013-frontend-contract-observation-provider-baseline/plan.md`](../013-frontend-contract-observation-provider-baseline/plan.md)

> 口径：本 work item 是 `013-frontend-contract-observation-provider-baseline` 下游的 child work item，用于把 frontend contract observation export surface 与正式 runtime/orchestration entrypoint 之间的接线规则收敛成单一 formal truth。它不是 provider contract 的延长线，不是 verify/gate 语义重写，也不是 registry、auto-fix 或 remediation workflow；它只处理“谁在什么入口、按什么范围、以什么安全默认值触发 observation artifact attachment”这条主线。

## 问题定义

`013` 已冻结 observation provider、scanner candidate、canonical artifact loader 与 `scan` export surface，当前仓库已经具备：

- `frontend-contract-observations.json` 的 canonical artifact 合同
- `ai-sdlc scan --frontend-contract-spec-dir ...` 的显式 operator export surface
- `verify_constraints` 对 canonical loader 的消费能力

但 runtime/orchestration attachment 仍缺少独立 formal truth：

- 还没有一个独立 work item 明确 `scan` export 与 `run`/`runner`/`program` 等正式入口之间的职责边界
- active `spec_dir` 如何成为 attachment scope 仍依赖局部实现直觉，缺少显式真值
- runtime 何时允许自动生成、复用或拒绝 observation artifact 没有 formal baseline，容易造成静默写入或跨 spec 污染
- export surface、runner orchestration 与 downstream verify consumer 之间的 ownership 顺序没有单独冻结

因此，本 work item 先要解决的不是“立刻让 runner 自动扫描前端”，而是：

- runtime attachment 的正式入口和安全默认值是什么
- operator 显式 export 与 runtime orchestrated attachment 的关系是什么
- active `spec_dir`、artifact locality、freshness honesty 与 failure surfacing 如何统一
- 哪些 runtime/orchestration 行为必须继续留在下游实现工单，而不能混回 `013`

## 范围

- **覆盖**：
  - 将 frontend contract runtime attachment 正式定义为 `013` 下游的独立 child work item
  - 锁定 operator 显式 export、runner attachment、program orchestration handoff 的职责顺序
  - 锁定 active `spec_dir`、artifact locality、attachment trigger 与 failure honesty 的 formal truth
  - 锁定 runtime attachment 的安全默认值，包括禁止静默跨 spec 写入、禁止无范围自动扫描、禁止隐式改写 provider contract
  - 为后续 `core / cli / runner / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 重新定义 `013` 已冻结的 provider artifact contract、scanner payload 或 canonical file naming
  - 改写 `012` 已冻结的 verify mainline、`VerificationGate`、CLI verify 或 gate aggregation
  - 在本 work item 中直接实现 runner 自动扫描、program integrate 自动注入或长期 registry attachment
  - 定义 auto-fix、contract writeback、drift remediation 或回写前端代码
  - 在本 work item 中直接扩张新的顶层命令面

## 已锁定决策

- runtime attachment 必须位于 `013` provider/export truth 与未来 runtime/orchestration execution truth 之间，作为单独下游能力存在
- operator 显式 export 仍是当前唯一已落地的调用面；任何自动化 runtime attachment 都必须在下游实现中显式接线，不得从 `013` 的 CLI export 行为隐式推导
- attachment scope 必须绑定 active `spec_dir` 或等价显式输入；不得把 observation artifact 静默写到未声明的 spec 目录
- runtime attachment 只能复用 `013` 已冻结的 canonical artifact contract，不得引入 runner 专用私有格式
- 若 attachment 前置条件不满足，例如 scope 不明、artifact 缺失、freshness 不可判断或 provider 失败，runtime 必须诚实暴露，不得静默降级为“看起来通过”
- registry、auto-refresh、auto-fix 与 remediation 仍留在下游 work item，不在 `014` 中混做

## 用户故事与验收

### US-014-1 — Framework Maintainer 需要 runtime attachment 成为独立真值层

作为**框架维护者**，我希望 runtime attachment 在 formal docs 中有独立合同，以便 observation export surface 与正式 pipeline/runtime 入口之间不再靠临时约定接线。

**验收**：

1. Given 我查看 `014` formal docs，When 我追踪 frontend contract 主线，Then 可以明确看到 runtime attachment 位于 `013` 下游  
2. Given 我审阅 `014` formal docs，When 我检查 runtime entrypoint 边界，Then 可以明确读到 operator export 与 runner attachment 不是同一个层

### US-014-2 — Operator 需要 attachment scope 与失败语义清晰

作为**operator**，我希望 runtime attachment 明确依赖 active `spec_dir` 和显式范围，以便不会把 observation artifact 写到错误的 spec，或在失败时被静默吞掉。

**验收**：

1. Given 我通过 CLI 或 runtime 入口触发 attachment，When 我查看 `014` formal docs，Then 可以明确读到 attachment 必须绑定 active `spec_dir` 或等价显式输入  
2. Given attachment 缺 scope、artifact 不存在或 freshness 不可判断，When runtime 消费它，Then `014` formal docs 已明确这类状态必须诚实暴露

### US-014-3 — Runner Author 需要 orchestration ownership 顺序可执行

作为**runner 作者**，我希望 formal docs 先锁定 CLI export、runner、program orchestration 的 ownership 边界，以便后续实现不会把 attachment、verify 与 registry 写成一团。

**验收**：

1. Given 我准备实现 runtime attachment，When 我查看 `014` plan/tasks，Then 可以直接获得推荐文件面与测试矩阵  
2. Given 我检查 `014` formal docs，When 我确认 non-goals，Then 可以明确读到当前 work item 不默认启用 runner 自动扫描、program auto-integration 或 registry attachment

## 功能需求

### Scope And Truth Order

| ID | 需求 |
|----|------|
| FR-014-001 | `014` 必须作为 `013` 下游的 runtime attachment child work item 被正式定义，而不是继续把 orchestration 细节堆回 `013` |
| FR-014-002 | `014` 必须明确 runtime attachment 位于 `013` provider/export truth 与 future runtime/orchestration execution truth 之间 |
| FR-014-003 | `014` 必须明确当前 work item 的非目标，包括 verify/gate 语义重写、registry attachment、auto-refresh、auto-fix 与 remediation |
| FR-014-004 | `014` 必须明确 operator export surface 与 runtime orchestrated attachment 是分层关系，而不是同一入口的两个别名 |

### Runtime Attachment Contract

| ID | 需求 |
|----|------|
| FR-014-005 | `014` 必须定义 runtime attachment 的最小触发合同，包括显式 entrypoint、active `spec_dir` 解析与 attachment scope |
| FR-014-006 | `014` 必须明确 attachment 只能复用 `013` 已冻结的 canonical artifact contract，不得引入 runner/program 私有 observation 格式 |
| FR-014-007 | `014` 必须明确 attachment 不得静默写入未声明的 spec 目录，不得跨 active work item 污染其他 spec |
| FR-014-008 | `014` 必须明确 operator 显式 export、runner 触发 attachment 与 program-level orchestration 的 ownership 顺序 |
| FR-014-009 | `014` 必须明确当前已存在的 `scan --frontend-contract-spec-dir` 只是显式 export surface，而不是自动 runtime attachment 已完成的证明 |

### Failure Honesty And Freshness Guard

| ID | 需求 |
|----|------|
| FR-014-010 | `014` 必须明确 attachment 前置条件至少包括 scope 可解析、artifact location 可确定，以及 freshness/provenance 可判断或可诚实报告 |
| FR-014-011 | `014` 必须明确当 scope 不明、artifact 缺失、provider 失败或 freshness 无法判断时，runtime 必须诚实暴露缺口而不是静默通过 |
| FR-014-012 | `014` 必须明确 runtime attachment 不得偷偷触发 verify/gate 语义变更，不得把 attachment 失败伪装成 verify success |
| FR-014-013 | `014` 必须明确任何自动生成 artifact 的 runtime 行为都需要显式 opt-in 或下游工单授权，不得默认开启 |

### Implementation Handoff

| ID | 需求 |
|----|------|
| FR-014-014 | `014` 必须为后续 `core / cli / runner / tests` 的实现提供单一 formal baseline |
| FR-014-015 | `014` 必须明确最小验证面至少覆盖 explicit export handoff、runner attachment scope、missing/stale artifact honesty、以及 program orchestration non-goal 场景 |
| FR-014-016 | `014` 必须明确实现起点优先是 runtime attachment helper / runner wiring baseline，而不是继续扩张 provider contract 或 verify mainline |

## 关键实体

- **Frontend Contract Runtime Attachment**：承载 observation artifact 从显式 export 面进入正式 runtime/orchestration 入口的接线合同
- **Attachment Scope Resolver**：承载 active `spec_dir` 或等价显式输入的解析规则
- **Observation Export Entrypoint**：承载 `scan --frontend-contract-spec-dir` 这类 operator 显式 export surface
- **Runtime Attachment Policy**：承载 runtime 何时允许复用、拒绝或显式生成 observation artifact 的规则
- **Attachment Freshness Guard**：承载 freshness/provenance 可判断性与失败暴露语义
- **Program Orchestration Handoff**：承载 program-level integrate/status/plan 等入口与 runtime attachment 的职责边界

## 成功标准

- **SC-014-001**：`014` formal docs 可以独立表达 runtime attachment 的 scope、truth order 与 non-goals，而无需回到 `013` 临时推断
- **SC-014-002**：operator export、runner attachment 与 program orchestration 的职责顺序在 formal docs 中具有单一真值
- **SC-014-003**：reviewer 能从 `014` 直接读出 active `spec_dir` scope、artifact locality 与 failure honesty 的正式口径
- **SC-014-004**：后续实现团队能够从 `014` 直接读出 `core / cli / runner / tests` 的推荐文件面与最小测试矩阵
- **SC-014-005**：`014` formal baseline 不会回写或冲掉 `013` 已冻结的 provider/export truth 与 `012` 已冻结的 verify integration truth
