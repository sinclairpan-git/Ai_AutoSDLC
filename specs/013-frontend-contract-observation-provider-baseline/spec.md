# 功能规格：Frontend Contract Observation Provider Baseline

**功能编号**：`013-frontend-contract-observation-provider-baseline`  
**创建日期**：2026-04-02  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`../011-frontend-contract-authoring-baseline/spec.md`](../011-frontend-contract-authoring-baseline/spec.md)、[`../011-frontend-contract-authoring-baseline/plan.md`](../011-frontend-contract-authoring-baseline/plan.md)、[`../012-frontend-contract-verify-integration/spec.md`](../012-frontend-contract-verify-integration/spec.md)、[`../012-frontend-contract-verify-integration/plan.md`](../012-frontend-contract-verify-integration/plan.md)

> 口径：本 work item 是 `012-frontend-contract-verify-integration` 下游的 child work item，用于把 frontend contract observation provider / scanner baseline 收敛成单一 formal truth。它不是 verify integration 的延长线，不是 registry attachment，也不是 auto-fix 或 remediation workflow；它只处理“谁产生结构化 observation、以什么 artifact 落盘、scanner 在其中扮演什么角色”这条主线。

## 问题定义

`011` 已冻结 contract artifact truth，`012` 已冻结 verify integration truth，并把 `frontend-contract-observations.json` 固定为 verify 侧消费的结构化输入边界。但当前框架仍有三类 provider baseline 空缺：

- 还没有一个独立 work item 定义 observation provider 的正式对象边界，导致“谁负责产出 `PageImplementationObservation`”仍依赖口头约定
- scanner 与 provider 的关系没有被正式冻结，容易让后续实现把“scanner 是一种候选 provider”误写成“scanner 就是全部 provider 合同”
- observation artifact 的最小序列化、provenance 与 freshness 语义没有被单独定义，导致下游 verify 只能消费文件名，不能消费可靠的 provider 合同

因此，本 work item 先要解决的不是“立刻写 AST 扫描器”，而是：

- observation provider 的 canonical contract 是什么
- `PageImplementationObservation` 与 `frontend-contract-observations.json` 的 artifact 边界如何定义
- manual authoring、export tool 和 scanner 三类 observation source 的关系是什么
- 哪些内容必须明确留在下游实现工单，而不能继续混进 `012`

## 范围

- **覆盖**：
  - 将 frontend contract observation provider 正式定义为 `012` 上游的独立 child work item
  - 锁定 provider 的最小输入、输出、artifact envelope、provenance 与 freshness 语义
  - 锁定 `PageImplementationObservation` 或兼容 JSON 结构作为 provider 输出真值
  - 锁定 scanner 只是 provider 的一种候选实现，而不是 provider baseline 本身
  - 为后续 `core / scanners / cli / tests` 的实现提供 canonical formal baseline
- **不覆盖**：
  - 实现真实 AST/source scanner 或前端框架特定解析器
  - 改写 `012` 已冻结的 verify mainline、`VerificationGate`、CLI verify 或 registry attachment
  - 实现 auto-fix、contract writeback、drift remediation 或回写前端代码
  - 定义 runtime provider registry、调度系统或长期缓存策略
  - 在本 work item 中直接完成 observation provider 的全部运行时代码

## 已锁定决策

- observation provider 必须位于 `011` contract truth 与 `012` verify consumption 之间，作为单独上游能力存在
- provider 输出必须是结构化 `PageImplementationObservation` 列表或兼容的 JSON envelope，不得退回 prompt、自然语言摘要或自由文本比对
- `frontend-contract-observations.json` 是 observation artifact 的 canonical 文件名，但具体由哪个 active work item 消费，必须由下游集成工单显式决定
- scanner 只是 observation provider 的一种候选实现；manual authoring、脚本导出或 bridge tool 同样可以是 provider
- provider 产物必须显式携带 provenance / freshness 语义，避免下游把过期 observation 当成当前真值
- registry attachment、auto-fix 与 remediation workflow 保持在下游 work item，不在 `013` 中混做

## 用户故事与验收

### US-013-1 — Framework Maintainer 需要 observation provider 成为独立真值层

作为**框架维护者**，我希望 observation provider 在 formal docs 中有独立合同，以便 contract artifact 与 verify integration 之间不再靠临时约定接线。

**验收**：

1. Given 我查看 `013` formal docs，When 我追踪 frontend contract 主线，Then 可以明确看到 provider 位于 `011` 与 `012` 之间  
2. Given 我审阅 `013` formal docs，When 我检查 provider 输出，Then 可以明确读到它必须产出结构化 observation，而不是自由文本

### US-013-2 — Scanner Author 需要 scanner 与 provider 边界清晰

作为**scanner 作者**，我希望 scanner 在 formal docs 中被明确为 provider 的候选实现，而不是整个 provider contract 本身，以便后续实现不会把扫描策略和 provider baseline 混为一体。

**验收**：

1. Given 我查看 `013` formal docs，When 我检查 scanner 角色，Then 可以明确读到 scanner 只是 candidate provider  
2. Given 我准备实现 scanner，When 我查看 `013` plan/tasks，Then 可以直接获得推荐文件面与测试矩阵，而无需反推 `012`

### US-013-3 — Operator 需要 observation artifact 的 provenance/freshness 可判断

作为**operator**，我希望 observation artifact 能明确标识来源和时效，以便不会把过期扫描结果误判为当前实现真值。

**验收**：

1. Given observation artifact 来自 manual export 或 scanner，When 我查看 `013` formal docs，Then 可以明确读到 artifact 需要记录 provenance  
2. Given observation artifact 已过期或来源不明，When 下游 verify 或 review 消费它，Then `013` formal docs 已明确这类状态必须被诚实暴露，而不是默默接受

## 功能需求

### Scope And Truth Order

| ID | 需求 |
|----|------|
| FR-013-001 | `013` 必须作为 `012` 下游的 observation provider child work item 被正式定义，而不是继续把 provider/scanner 细节堆回 `012` |
| FR-013-002 | `013` 必须明确 observation provider 位于 `011` contract artifact truth 与 `012` verify consumption truth 之间 |
| FR-013-003 | `013` 必须明确当前 work item 的非目标，包括 registry attachment、verify mainline 变更、auto-fix、contract writeback 与 runtime provider orchestration |
| FR-013-004 | `013` 必须明确 provider baseline 与 scanner implementation baseline 的关系，避免二者被误读为同一层 |

### Provider Output Contract

| ID | 需求 |
|----|------|
| FR-013-005 | `013` 必须定义 observation provider 的最小输入/输出合同，输出以 `PageImplementationObservation` 或兼容 JSON 结构表示 |
| FR-013-006 | `013` 必须定义 `frontend-contract-observations.json` 作为 observation artifact 的 canonical 文件名与最小 envelope 语义 |
| FR-013-007 | `013` 必须明确 artifact 至少携带 provenance、生成时刻或等价 freshness 信息，以及 observation payload |
| FR-013-008 | `013` 必须明确 provider 输出必须可被下游 verify integration 消费，而不是停留在 scanner 专用内部格式 |
| FR-013-009 | `013` 必须明确 observation payload 至少需要支持 page-level implementation facts、route/layout hints、i18n/validation usage 或等价 contract 对照信息 |

### Provider Provenance And Source Separation

| ID | 需求 |
|----|------|
| FR-013-010 | `013` 必须明确 manual authoring、script export、scanner 都可以是 provider，但必须落到统一 artifact contract |
| FR-013-011 | `013` 必须明确 scanner 只是 provider 的一种候选实现，不得被 formal docs 写成唯一输入来源 |
| FR-013-012 | `013` 必须明确 provider artifact 若来源不明、结构不完整或 freshness 不可判断，下游必须能够诚实识别为风险或缺口 |
| FR-013-013 | `013` 必须明确 provider baseline 不得直接篡改 `011` contract artifact，也不得在当前 work item 中直接驱动 `012` verify decision |

### Implementation Handoff

| ID | 需求 |
|----|------|
| FR-013-014 | `013` 必须为后续 `core / scanners / cli / tests` 的实现提供单一 formal baseline |
| FR-013-015 | `013` 必须明确最小验证面至少覆盖 manual provider、scanner provider、artifact 缺字段、provenance/freshness 缺失与 downstream handoff 场景 |
| FR-013-016 | `013` 必须明确实现起点优先是 provider contract / artifact IO / scanner candidate slice，而不是直接扩张 verify mainline |

## 关键实体

- **Frontend Contract Observation Provider**：承载从实现侧收集并输出结构化 observation 的正式 provider 合同
- **Page Implementation Observation**：承载 page-level implementation facts 的结构化 observation 实体，供 contract drift 与 verify consumption 使用
- **Observation Artifact Envelope**：承载 `frontend-contract-observations.json` 的 envelope、payload、provenance 与 freshness 元数据
- **Observation Provider Provenance**：承载 manual / export tool / scanner 等来源信息，避免来源丢失
- **Observation Freshness Marker**：承载 observation 生成时刻、输入摘要或等价 freshness 证据
- **Scanner Candidate Provider**：承载 scanner 作为 provider 的候选实现角色，而不是 provider baseline 本体

## 成功标准

- **SC-013-001**：`013` formal docs 可以独立表达 observation provider 的 scope、truth order 与 non-goals，而无需回到 `012` 临时推断
- **SC-013-002**：`frontend-contract-observations.json` 的 artifact envelope、provenance 与 freshness 语义在 formal docs 中具有单一真值
- **SC-013-003**：reviewer 能从 `013` 直接读出 scanner 只是 candidate provider，不是 provider contract 全部
- **SC-013-004**：后续实现团队能够从 `013` 直接读出 `core / scanners / cli / tests` 的推荐文件面与最小测试矩阵
- **SC-013-005**：`013` formal baseline 不会回写或冲掉 `011` / `012` 已冻结的 contract artifact truth 与 verify integration truth
