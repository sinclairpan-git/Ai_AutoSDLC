# 功能规格：Provenance Trace Phase 1

**功能编号**：`006-provenance-trace-phase-1`  
**创建日期**：2026-03-31  
**状态**：已冻结（formal work item baseline）  
**输入**：[`../../docs/superpowers/specs/2026-03-31-provenance-trace-architecture-design.md`](../../docs/superpowers/specs/2026-03-31-provenance-trace-architecture-design.md)、[`../../docs/superpowers/plans/2026-03-31-provenance-trace-phase-1.md`](../../docs/superpowers/plans/2026-03-31-provenance-trace-phase-1.md)、[`../../docs/framework-defect-backlog.zh-CN.md`](../../docs/framework-defect-backlog.zh-CN.md) `FD-2026-03-31-001`

> 口径：本 work item 不是把 Codex 宿主事件一次性全接入 telemetry，而是先把 provenance trace 做成 telemetry 内部的 gate-capable、read-only 审计层正式内核。

## 范围

- **覆盖**：
  - telemetry 内部 provenance facts / interpretation / governance-ready hook 对象模型
  - provenance `node / edge / assessment / gap / hook` 的持久化、解析与 source closure
  - `conversation/message`、`skill invocation`、`exec_command bridge`、`rule provenance` 四类 provenance ingress contract
  - injected / replay / manual validation 与 explicit `unknown / unobserved / unsupported` gap 语义
  - read-only provenance inspection 与 CLI：`summary / explain / gaps / --json`
  - provenance-specific observer / governance enrichment，与未来 gate consumption placeholder
  - Phase 1 的 docs、CLI discoverability、snapshot-friendly JSON shape 与回归矩阵
- **不覆盖**：
  - 完整 host-native Codex ingress 覆盖
  - 默认 blocker、默认 published governance artifact、默认 execute 阻断
  - 重型交互式 graph viewer
  - 自动 root cause / remediation 生成
  - 第二事实系统、第二 evidence store、旁路 graph database

## 已锁定决策

- provenance trace 是 telemetry facts 层中的专门事实对象，不是第二事实系统
- Phase 1 只做 `gate-capable but read-only`
- `ingress_kind` 对 facts 固定为 `auto | injected | inferred`；`unknown` 只属于 gap 语义
- `chain_status` 固定为 `closed | partial | unknown`；`unsupported` 不是 `chain_status`
- Phase 2 只允许替换 ingress，不允许回改 Phase 1 冻结的 contracts
- provenance candidate / hook 只能 enrich，不能 override 现有 evaluation / gate truth

## 用户故事与验收

### US-006-1 — Framework Maintainer 需要可审计的 provenance facts

作为**框架维护者**，我希望 provenance trace 作为 telemetry 内部正式 facts 写入、解析和闭包，以便后续任何审计能力都不需要再长第二套事实系统。

**验收**：

1. Given provenance node/edge 被写入 telemetry，When 读取 store 与 resolver，Then 系统能稳定解析对象、refs 与 source closure
2. Given injected / inferred provenance facts，When 执行解析，Then 系统不会允许空 refs 或伪造 raw host facts

### US-006-2 — Reviewer 需要 read-only provenance inspection

作为**reviewer**，我希望在不依赖 agent 自述的情况下回答“由谁触发、调了什么、引了什么、哪里缺链”，以便判断 agent 产出是否合理。

**验收**：

1. Given 一个 provenance subgraph，When 执行 `summary / explain / gaps`，Then inspection 能回答 5 个固定审计问题
2. Given 同一 provenance 输入，When 多次读取 inspection，Then assessment/gap/json 的结构顺序保持稳定

### US-006-3 — Governance Maintainer 需要 gate-capable 但 non-blocking 的 provenance hook

作为**governance maintainer**，我希望 provenance assessment 能形成 governance-ready payload 与 blocker candidate，但默认只读、不改现有门禁，以便先验证模型，再决定是否接 gate。

**验收**：

1. Given provenance assessment 与 gaps 已存在，When observer/governance 运行，Then 可生成 provenance hook/candidate
2. Given provenance hook/candidate 已存在，When 执行 `verify / close-check / release`，Then 默认 blocker 结果不发生变化

## 功能需求

### Contracts And Facts

| ID | 需求 |
|----|------|
| FR-006-001 | provenance 必须作为 telemetry 内部事实扩展实现，不得创建第二事实系统 |
| FR-006-002 | 系统必须提供 `ProvenanceNodeFact` 与 `ProvenanceEdgeFact`，并保持 append-only |
| FR-006-003 | 系统必须提供 `ProvenanceAssessment`、`ProvenanceGapFinding`、`ProvenanceGovernanceHook`，并保持 `mutable current + revisions` |
| FR-006-004 | provenance 必须复用现有 `Evidence`、`TraceContext`、`SourceClosureStatus` 与 writer discipline |
| FR-006-005 | facts 层 `ingress_kind` 必须固定为 `auto`、`injected`、`inferred`，`unknown` 不得伪装成完整 fact |

### Persistence, Resolution, And Closure

| ID | 需求 |
|----|------|
| FR-006-006 | writer 必须分配 session-local、单调递增的 `ingestion_order`，而不是让 ingress 自行分配 |
| FR-006-007 | resolver 必须检测孤儿边、悬空节点、指向不存在 telemetry object 的 edge，以及 trace-context 无法挂回的 provenance object |
| FR-006-008 | provenance `chain_status` 必须固定为 `closed / partial / unknown`，且不得把 `unsupported` 混入其中 |
| FR-006-009 | `source_object_refs` 与 `source_evidence_refs` 对 `injected / inferred` facts 至少一类必须存在，不得双空 |

### Ingress And Inspection

| ID | 需求 |
|----|------|
| FR-006-010 | 系统必须为 `conversation/message`、`skill invocation`、`exec_command bridge`、`rule provenance` 四类 trace 提供 ingress/adapters |
| FR-006-011 | `unknown / unobserved / unsupported` 必须作为 gap/finding 语义显式落盘，不得生成 placeholder fact |
| FR-006-012 | inspection 必须提供只读 `summary / explain / gaps / --json`，并固定回答 5 个审计问题 |
| FR-006-013 | inspection 不得做 graph rewrite、graph repair、隐式 rebuild、隐式 init 或自动补链 |

### Governance And Phase Boundary

| ID | 需求 |
|----|------|
| FR-006-014 | Phase 1 必须允许生成 provenance-based blocker candidate 与 governance-ready hook，但默认不进入 published artifact 语义 |
| FR-006-015 | provenance-specific finding 只能 enrich，不得 override 现有 evaluation 主结果 |
| FR-006-016 | `verify / close-check / release` 默认 blocker 路径不得因 Phase 1 provenance 接入而改变 |
| FR-006-017 | `manual injection` 只能作为测试/诊断/回放入口，不得成为默认业务入口 |
| FR-006-018 | Phase 2 真实宿主接入只能替换 ingress，不得回改 Phase 1 冻结的 contracts |

## 成功标准

- **SC-006-001**：provenance node/edge 能 append-only 落盘，并保持 refs、ID、enum literal 与 serialization shape 稳定
- **SC-006-002**：resolver 能区分 parse failure 与 closure failure，且能稳定输出 orphan/dangling/missing-object failure class
- **SC-006-003**：`summary / explain / gaps / --json` 能稳定回答 5 个 provenance 审计问题，且人类视图与 JSON 语义一致
- **SC-006-004**：四条 provenance 链都至少有一组 positive sample 与一组 negative sample，覆盖 `parse failure`、`unsupported`、`unknown/unobserved`
- **SC-006-005**：provenance hook/candidate 能生成，但默认不会进入 published artifact 或默认 blocker 路径
- **SC-006-006**：Phase 1 结束时，host-native ingress 仍可缺席，但 contracts、storage、inspection、closure 与 non-blocking governance 已形成正式真值
