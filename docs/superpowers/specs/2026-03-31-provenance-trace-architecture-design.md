# Provenance Trace Architecture Design

## 1. Positioning And Scope

### 1.1 Positioning

- 本设计定义的是 telemetry 内部的 provenance 扩展，不是 telemetry 之外的第二事实系统。
- 第一阶段目标是建立一套 `gate-capable` 的只读审计层：对象模型、落盘纪律、来源闭包与 inspection 面先成立，但默认不进入自动阻断路径。
- 第二阶段只允许把第一阶段的 injected / adapter ingress 替换为真实 host-native ingress，不允许回改第一阶段冻结的 contracts。

### 1.2 Scope Summary

本设计要解决的问题不是“马上把 Codex 宿主全接进来”，而是先把 provenance architecture 本身做成可验证、可扩展、可进入未来 gate 的内核。第一阶段先完成三件事：

1. 冻结 provenance facts / interpretation / governance-ready hook 的对象模型。
2. 打通 storage / writer / resolver / source closure / inspection。
3. 用 injected / replay / manual adapter 把调用链审计能力跑通，证明模型、闭包与 inspection 成立。

### 1.3 Phase 1 Boundary

Phase 1 明确是 `gate-capable but read-only`：

- 可以生成 provenance-based blocker candidate。
- 可以生成 governance-ready payload hook。
- 可以在 inspection 面展示 provenance 风险与缺口。
- 但默认不得进入 `verify / close-check / release` 的自动阻断路径。

### 1.4 Core Rules

1. provenance trace 是 telemetry facts 层中的专门事实对象，不得演化成第二事实系统。
2. facts 层与 interpretation / governance 层分离：ingress 只写 `facts + evidence`，不得顺手生成 assessment 或 governance hook。
3. provenance 的宿主接入增强的是 facts 可得性、closure 完整度与 confidence 上限，不改变 assessment / governance 的解释权边界。
4. Phase 1 的 injected validation 是正式验证手段，不等于低价值证据，但默认不与 host-native `auto` 采集拥有相同 gate 权重。
5. provenance 接 gate 只能走 provenance-specific policy；即使第二阶段真实宿主接入完成，也不得默认把 `execute` 变成 provenance blocker 面。

## 2. Data Objects

### 2.1 Shared Semantic Baseline

- `confidence` 分层语义固定：
  - facts 层上的 `confidence` 表示观测来源 / 记录可靠度。
  - interpretation / governance 层上的 `confidence` 表示解释或治理结论置信度。
- `ingress_kind` 最小值域固定为 `auto | injected | inferred`。
  - `unknown` 只表示 gap / placeholder 语义，不是完整 ingress fact kind。
- `scope_level` Phase 1 只复用现有 `session | run | step`，不新增 provenance 专用层级。
- `ingestion_order` 固定为 session-local 单调递增排序号，由 writer 分配；同一写入批次按 append 顺序稳定排序。
- `relation_kind` 的命名统一按 `from_ref -> to_ref` 方向解释。
- 对 `injected / inferred` 的 node/edge，`source_object_refs` 与 `source_evidence_refs` 至少一类必须存在，不能同时为空。

### 2.2 ProvenanceNodeFact

- 角色：
  - `facts` 层对象。
  - 表达一个可审计的 provenance 主体，例如触发消息、skill 调用、命令桥接、规则引用。
- 最小字段：
  - `node_id`
  - `node_kind`
  - `ingress_kind`
  - `confidence`
  - `scope_level`
  - `trace_context`
  - `observed_at`
  - `ingestion_order`
  - `source_object_refs`
  - `source_evidence_refs`
- 核心约束：
  - `append-only`
  - facts 层只允许 `auto | injected | inferred`
  - `unknown` 不伪装成完整节点
  - V1 `node_kind` 冻结为：
    - `trigger_point`
    - `conversation_message`
    - `skill_invocation`
    - `exec_command_bridge`
    - `rule_reference`
  - V1 用 `skill_invocation` 覆盖 skill/tool 级调用，但保留未来拆分 `tool_invocation` 的扩展位
- 和现有 telemetry 的关系：
  - 通过 `source_object_refs` 挂到现有 `event / evidence / evaluation / violation / artifact`
  - 通过 `trace_context` 复用现有 session/run/step 主键链
- 第一阶段用途：
  - inspection graph 的基础节点
  - 承载 injected validation 的原始事实
  - 为 future gate hook 提供可追溯上游节点
- 第二阶段扩展位：
  - 可补 host-native 字段，如 host message id、skill runtime id、bridge runtime id
  - 不改变 `node_id / node_kind / ingress_kind / refs` 语义

### 2.3 ProvenanceEdgeFact

- 角色：
  - `facts` 层对象。
  - 表达 provenance 节点之间，以及 provenance 与现有 telemetry objects 之间的关系。
- 最小字段：
  - `edge_id`
  - `relation_kind`
  - `from_ref`
  - `to_ref`
  - `ingress_kind`
  - `confidence`
  - `observed_at`
  - `ingestion_order`
  - `source_object_refs`
  - `source_evidence_refs`
- 核心约束：
  - `append-only`
  - `relation_kind` 按 `from_ref -> to_ref` 解释
  - V1 `relation_kind` 冻结为：
    - `triggered_by`
    - `invoked`
    - `bridged_to`
    - `cites`
    - `derived_from`
    - `supports`
    - `produced`
  - `inferred` edge 必须显式带推断依据 refs
- 和现有 telemetry 的关系：
  - `from_ref / to_ref` 允许指向 provenance node
  - `from_ref / to_ref` 也允许指向现有 `event / evidence / evaluation / violation / artifact`
- 第一阶段用途：
  - 构建 chain view
  - 回答“由谁触发”“调用了谁”“桥到了什么”“引用了什么”
- 第二阶段扩展位：
  - 可补 host-native relation metadata
  - 不改变方向语义与闭包规则

### 2.4 ProvenanceAssessment

- 角色：
  - `interpretation` 层对象。
  - 对一个 provenance subgraph 做总体可读判断。
- 最小字段：
  - `assessment_id`
  - `subject_ref`
  - `chain_status`
  - `overall_confidence`
  - `highest_confidence_source`
  - `trigger_summary`
  - `skill_summary`
  - `bridge_summary`
  - `rule_summary`
  - `key_gaps`
  - `source_object_refs`
  - `source_evidence_refs`
- 核心约束：
  - `mutable current + revisions`
  - `chain_status` 只做总体闭合度摘要，V1 固定为 `closed | partial | unknown`
  - `highest_confidence_source` 表示当前 assessment 所依赖的最高置信来源类别，或其代表性来源引用摘要
  - 只能 enrich，不能 override 现有 evaluation 主结果
  - 不得由 ingress adapter 直接生成
- 和现有 telemetry 的关系：
  - 可映射到补充型 `Evaluation`
  - 不替代现有 evaluation 的主语义
- 第一阶段用途：
  - 作为 assessment view 主输出
  - 固定回答 5 个 inspection 问题
- 第二阶段扩展位：
  - 可增加 host-native explain fields
  - 不改变 `subject_ref / chain_status / confidence / refs` 形状

### 2.5 ProvenanceGapFinding

- 角色：
  - `interpretation` 层对象。
  - 表达 provenance 链上的具体缺口，而不是总体结论。
- 最小字段：
  - `gap_id`
  - `subject_ref`
  - `gap_kind`
  - `gap_location`
  - `expected_relation`
  - `confidence`
  - `detail`
  - `source_object_refs`
  - `source_evidence_refs`
- 核心约束：
  - `mutable current + revisions`
  - `gap_kind` V1 固定为：
    - `unknown`
    - `unobserved`
    - `incomplete`
    - `unsupported`
  - `unsupported` 只表示“当前 ingress / host capability 根本不支持提供该段链路”
  - `detail` 优先结构化、机器可消费；必要时可附带人类可读补充说明
  - 具体原因分类只由 gap 承担，不由 `chain_status` 承担
- 和现有 telemetry 的关系：
  - 可挂到 provenance node/edge
  - 也可挂到现有 `evaluation / violation / artifact` 作为补充解释
- 第一阶段用途：
  - 作为 gaps view 主输出
  - 把 `unknown / unobserved / unsupported` 显式结构化
- 第二阶段扩展位：
  - 可映射成 provenance-specific finding
  - 默认仍不直接改变 gate verdict

### 2.6 ProvenanceGovernanceHook

- 角色：
  - `governance-ready hook` 对象。
  - 用来冻结未来 provenance 接 gate 的 payload 形状。
- 最小字段：
  - `hook_id`
  - `subject_ref`
  - `decision_subject`
  - `candidate_result`
  - `confidence`
  - `source_closure_status`
  - `evidence_refs`
  - `source_object_refs`
  - `policy_name`
  - `advisories`
- 核心约束：
  - `mutable current + revisions`
  - `candidate_result` V1 固定为：
    - `advisory`
    - `warning`
    - `blocker_candidate`
  - `policy_name` 表示 policy 的稳定标识，和现有 `policy / profile / mode` 口径对齐
  - Phase 1 只读可见，不自动进入 gate
  - 追加 provenance 维度，不改写现有 violation 真值
  - candidate 可生成，不等于默认可发布
- 和现有 telemetry 的关系：
  - 兼容现有 `Violation / GateDecisionPayload` 口径
  - 必须能引用 provenance assessment、gaps 和 raw evidence
- 第一阶段用途：
  - inspection 可见的 governance-ready 输出
  - future gate 接入的 contract placeholder
- 第二阶段扩展位：
  - 允许接入 `verify / close-check / release`
  - 但必须受 provenance-specific policy 控制

### 2.7 Evidence Reuse Rules

- 角色：
  - provenance 不新增第二种 evidence 模型，继续复用现有 telemetry `Evidence`。
- 最小字段：
  - 复用现有 `evidence_id / status / capture_mode / confidence / locator / digest`
  - V1 新增 provenance locator family 约定：
    - `prov://conversation/...`
    - `prov://skill/...`
    - `prov://exec-bridge/...`
    - `prov://rule/...`
    - `prov://adapter-payload/...`
    - `prov://inference/...`
- 核心约束：
  - provenance facts 不得脱离 evidence 单独宣称 closure 成立
  - `injected` evidence 必须标明注入来源
  - `inferred` evidence 不得伪装成 raw host payload
  - 缺失链路时必须落 gap，不得伪造 evidence
- 和现有 telemetry 的关系：
  - 继续 obey 现有 writer / resolver / source-closure discipline
  - 只扩展 locator namespace，不新增旁路 evidence store
- 第一阶段用途：
  - 支撑 closure、inspection、snapshot tests、future governance hook
- 第二阶段扩展位：
  - host-native ingress 只替换 evidence 来源，不改变 digest / locator / resolver discipline

### 2.8 Layering Summary

- `ProvenanceNodeFact / ProvenanceEdgeFact` 属于 facts
- `ProvenanceAssessment / ProvenanceGapFinding` 属于 interpretation
- `ProvenanceGovernanceHook` 属于 governance-ready hook
- 原始材料继续复用现有 telemetry evidence discipline

## 3. Module Boundaries

### 3.1 Contracts / Model Files

- `src/ai_sdlc/telemetry/provenance_contracts.py`
  - 责任：
    - 定义 `ProvenanceNodeFact / ProvenanceEdgeFact / ProvenanceAssessment / ProvenanceGapFinding / ProvenanceGovernanceHook`
    - 明确 append-only 与 mutable 边界
  - 不该做什么：
    - 不做 ingest
    - 不做 resolver
    - 不做 inspection
  - 与现有 telemetry 的交互：
    - 复用现有 `ScopeLevel / Confidence / SourceClosureStatus / TraceContext`
  - 第一阶段启用范围：
    - 冻结对象模型
  - 第二阶段扩展位：
    - 追加 host-native fields，但不改核心 contract

- `src/ai_sdlc/telemetry/enums.py`
  - 责任：
    - 定义 provenance 所需 enum：`IngressKind`、`ProvenanceNodeKind`、`ProvenanceRelationKind`、`ProvenanceGapKind`、`ProvenanceCandidateResult`
  - 不该做什么：
    - 不散落 duplicate literals
  - 与现有 telemetry 的交互：
    - 与现有 enum 共享模块，不分叉
  - 第一阶段启用范围：
    - 单一枚举真值源
  - 第二阶段扩展位：
    - 只允许追加新值，不回改既有值语义

### 3.2 Ingress Files

- `src/ai_sdlc/telemetry/provenance_ingress.py`
  - 责任：
    - 把宿主、fixture、manual injection、推断器输入规范化成 node/edge/evidence 写入请求
  - 不该做什么：
    - 不得自行分配 `ingestion_order`
    - 不得直接生成 assessment 或 governance hook
  - 与现有 telemetry 的交互：
    - 通过 writer API 提交写入请求
  - 第一阶段启用范围：
    - injected/manual/fixture 为主
  - 第二阶段扩展位：
    - 用 host-native ingress 替换 adapter 实现

- `src/ai_sdlc/telemetry/provenance_adapters.py`
  - 责任：
    - 为四类 trace 提供 adapter：
      - `conversation/message`
      - `skill invocation`
      - `exec_command bridge`
      - `rule provenance`
  - 不该做什么：
    - 不得绕过 source refs discipline
  - 与现有 telemetry 的交互：
    - 复用 `Evidence` 和 `TraceContext`
  - 第一阶段启用范围：
    - injected validation contract
  - 第二阶段扩展位：
    - 替换为真实 host-native payload mapping

### 3.3 Persistence / Resolution Files

- `src/ai_sdlc/telemetry/provenance_store.py`
  - 责任：
    - node/edge append-only 持久化
    - assessment/gap/hook current + revisions
  - 不该做什么：
    - 不做解释
  - 与现有 telemetry 的交互：
    - 复用现有 store layout discipline
  - 第一阶段启用范围：
    - provenance facts 作为 telemetry facts 子集落盘
  - 第二阶段扩展位：
    - 增加更强 replay/index，但不做第二套 graph database

- `src/ai_sdlc/telemetry/provenance_resolver.py`
  - 责任：
    - 解析 node/edge/source refs
    - 做 integrity / closure check
  - 不该做什么：
    - integrity/closure 失败结果不得伪装成 raw fact 回写图中
  - 与现有 telemetry 的交互：
    - 对接现有 `event / evidence / evaluation / violation / artifact`
  - 第一阶段启用范围：
    - 检出孤儿边、悬空节点、指向不存在 telemetry object 的 edge
    - 输出稳定的 machine-readable failure class，供 inspection 与 snapshot tests 消费
  - 第二阶段扩展位：
    - 追加 host-aware resolution helpers

### 3.4 Inspection / Read Surfaces

- `src/ai_sdlc/telemetry/provenance_inspection.py`
  - 责任：
    - 提供 `chain view / assessment view / gap view`
  - 不该做什么：
    - 不写状态
    - 不触发隐式 rebuild / init
  - 与现有 telemetry 的交互：
    - 只读 provenance store/resolver 与现有 telemetry objects
  - 第一阶段启用范围：
    - 输出固定 5 问的审计结果
  - 第二阶段扩展位：
    - 追加 richer filters / exports

- `src/ai_sdlc/cli/provenance_cmd.py`
  - 责任：
    - 暴露 read-only `summary / explain / gaps / --json`
  - 不该做什么：
    - 不做重型交互 viewer
  - 与现有 telemetry 的交互：
    - 只读 inspection layer
  - 第一阶段启用范围：
    - 稳定 machine-readable 输出
  - 第二阶段扩展位：
    - 保持 `--json` 结构兼容的前提下追加展示能力

### 3.5 Integration / Future Gate Files

- `src/ai_sdlc/telemetry/provenance_observer.py`
  - 责任：
    - 把 provenance subgraph 映射成 assessment 与 provenance-specific finding
  - 不该做什么：
    - 不 override 现有 evaluation 主结果
  - 与现有 telemetry 的交互：
    - 衔接现有 observer/evaluator family
  - 第一阶段启用范围：
    - enrich only
  - 第二阶段扩展位：
    - 增强 host-native explain coverage

- `src/ai_sdlc/telemetry/provenance_governance.py`
  - 责任：
    - 生成 provenance governance-ready hook 与 blocker candidate
  - 不该做什么：
    - 不改变现有 violation 主语义
  - 与现有 telemetry 的交互：
    - 兼容现有 governance payload 口径
  - 第一阶段启用范围：
    - read-only candidate generation
  - 第二阶段扩展位：
    - 受 provenance-specific policy 管控的 gate-ready integration

- `src/ai_sdlc/core/provenance_gate.py`
  - 责任：
    - 冻结未来接入 `verify / close-check / release` 的消费接口
  - 不该做什么：
    - 第一阶段不得通过 hidden flag 或实验开关把 provenance candidate 接进默认阻断路径
  - 与现有 telemetry 的交互：
    - 对接现有 verify/close/release gates
  - 第一阶段启用范围：
    - 可见但不可控
  - 第二阶段扩展位：
    - 仅在 provenance-specific policy 下启用正式 gate

## 4. Phase 1 Acceptance Criteria

### 4.1 Facts Acceptance

- `ProvenanceNodeFact / ProvenanceEdgeFact` 必须 append-only 落盘，不得 current-snapshot 覆盖写。
- `ingestion_order` 必须由 writer 分配，且在同一 session 内单调递增；同一写入批次排序稳定。
- `prov://...` locator namespace 必须可写入、可解析、可被 inspection 识别。
- 对 `injected / inferred` 的 node/edge，`source_object_refs` 与 `source_evidence_refs` 不得同时为空。
- 同一 injected payload / 同一 adapter replay 的重复写入必须有明确幂等或去重策略，至少不能 silently 破坏 closure 与审计判断。
- ingress 层只提交写入请求，不得自行分配 writer-owned 字段。

### 4.2 Resolver / Closure Acceptance

- provenance node、edge 和其 `source refs` 必须可解析到目标对象或明确失败类型。
- 测试必须区分：
  - `resolver parse failure`
  - `closure incomplete / unknown`
- resolver 必须检出：
  - 孤儿边
  - 悬空节点
  - 指向不存在 telemetry object 的 edge
  - 无法挂回 `trace_context` 的 provenance object
- 上述 failure class 的分类值和输出结构必须稳定，适合 snapshot tests 与 downstream inspection 消费。
- closure 状态至少区分 `closed | partial | unknown`。
- integrity / closure 失败结果必须进入 `assessment / gap / finding`，不得伪造 fact。
- `unsupported` 只能表示 host capability 不支持，不得和 `unknown / unobserved / incomplete` 混用。

### 4.3 Inspection Acceptance

- `summary / explain / gaps / --json` 必须回答：
  - 这次行为由哪条消息 / 命令 / 触发点引发
  - 调用了哪些 skill / tool / bridge
  - 引用了哪些规则 / 文档
  - 哪些链是 `auto / injected / inferred / unknown`
  - 哪个 provenance 缺口阻止了形成更高置信结论
- `assessment view` 固定输出：
  - 总体链状态
  - 最高置信来源
  - 关键缺口
- 对同一 provenance subgraph，`summary / assessment / gaps / --json` 的结构顺序和字段存在性必须稳定，适合 snapshot 测试。
- `--json` 优先服务 automation / snapshot tests，而不是人类排版优化。
- inspection 必须保持 read-only。

### 4.4 Injected Validation Acceptance

- 以下四条链都必须有 injected validation：
  - `conversation/message`
  - `skill invocation`
  - `exec_command bridge`
  - `rule provenance`
- 每条链至少要有一组能闭包的正样本和一组显式缺口/失败的负样本。
- 每条链都必须证明：
  - 能落盘
  - 能解析
  - 能闭包
  - 能审计
- injected 是正式 ingress validation 手段，不得被视为天然无效。
- inferred 链补全必须显式附带推断依据 refs。
- 缺失链路必须显式落成 `unknown / unobserved / unsupported`，不得伪造完整调用链。

### 4.5 Non-Blocking Governance Acceptance

- provenance-based blocker candidate 与 governance-ready hook 必须可生成，并可在 inspection 面看到。
- provenance-specific finding 只能 enrich，不能 override 现有 evaluation 主结果。
- Phase 1 不得改变 `verify / close-check / release` 的默认阻断路径。
- provenance candidate 默认只作为只读审计输出，不自动进入 gate verdict。
- candidate 可生成不等于默认可发布；Phase 1 的 provenance hook/candidate 不能视为正式 published governance artifact。
- CLI / gate 不允许通过 hidden flag 或实验开关绕过 Phase 1 边界。

## 5. Injection Validation Matrix

### 5.1 Relation Semantics

- `cites`：主体显式引用规则/文档。
- `supports`：规则/文档作为某个 assessment / candidate 的支持依据。
- 对 `auto` 来源，Phase 1 的 `unsupported` 是允许的正式结果，表示宿主 ingress 尚未接入，不代表 contract 失败。

### 5.2 Matrix

| Trace | Source | V1 必测 | 最小输入形态 | 预期落盘对象 | 默认 chain_status | 最低可接受 confidence | 预期 inspection / closure 结果 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `conversation/message` | `auto` | 契约必测，宿主原生非强制 | `message_id`、`role`、`observed_at`、`content_digest/summary` | `Node(conversation_message, auto)` + `Evidence(prov://conversation/...)` | `closed` 或 `unknown/unsupported` | `medium`，完整宿主接入时可到 `high` | inspection 能识别触发消息；宿主未接时不得伪造完整链 |
| `conversation/message` | `injected` | 是 | fixture/manual message payload + `target_ref` | `Node` + `Evidence` + `Edge(triggered_by)` | `closed` | `medium` | 缺 `target_ref` 按 parse failure 处理；完整输入时可落盘、可解析、可闭包、可审计 |
| `conversation/message` | `inferred` | 是 | downstream subject + inference basis refs + stable upstream message key | `Node/Edge(inferred)` + `Evidence(prov://inference/...)` | `partial`，条件满足时可 `closed` | `low` 到 `medium` | inspection 必须明示 `inferred`；不得伪装成 raw message capture |
| `conversation/message` | `unknown` | 是 | 仅声明“应存在 message trigger”，无 message payload | `GapFinding` | `unknown` 或 `partial` | 不形成正向高置信结论 | 不得伪造 message node；必须显式 gap |
| `skill invocation` | `auto` | 契约必测，宿主原生非强制 | stable invocation id、skill 标识、caller ref、`observed_at` | `Node(skill_invocation, auto)` + `Evidence(prov://skill/...)` + `Edge(invoked)` | `closed` 或 `unsupported` | `medium`，完整宿主接入时可到 `high` | inspection 能列出 skill；宿主缺位时不能伪造 |
| `skill invocation` | `injected` | 是 | fixture skill payload + caller ref | `Node` + `Edge(invoked)` + `Evidence` | `closed` | `medium` | 可落盘、可解析、可闭包、可审计 |
| `skill invocation` | `inferred` | 是 | tool/bridge facts + inference basis refs | `Node/Edge(inferred)` + `Evidence(prov://inference/...)` | `partial`，条件满足时可 `closed` | `low` 到 `medium` | inspection 明示 `inferred skill`，不得伪装成 auto |
| `skill invocation` | `unknown` | 是 | 仅声明“应存在 skill segment” | `GapFinding` | `unknown` 或 `partial` | 不形成正向高置信结论 | 不得伪造 skill node |
| `exec_command bridge` | `auto` | 契约必测，宿主原生非强制 | stable bridge call id、command digest、target ref、`observed_at` | `Node(exec_command_bridge, auto)` + `Evidence(prov://exec-bridge/...)` + `Edge(bridged_to)` | `closed` 或 `unsupported` | `medium`，完整宿主接入时可到 `high` | inspection 能识别 bridge；宿主缺位时不能伪造 |
| `exec_command bridge` | `injected` | 是 | fixture bridge payload + command digest + target refs | `Node` + `Edge(bridged_to/produced)` + `Evidence` | `closed` | `medium` | 可落盘、可解析、可闭包、可审计 |
| `exec_command bridge` | `inferred` | 是 | bridge-related basis refs + command/tool facts | `Node/Edge(inferred)` + `Evidence(prov://inference/...)` | `partial`，条件满足时可 `closed` | `low` 到 `medium` | 不得仅凭 command 文本硬推 bridge；至少要有 bridge-related basis refs |
| `exec_command bridge` | `unknown` | 是 | 仅声明“应存在 bridge segment” | `GapFinding` | `unknown` 或 `partial` | 不形成正向高置信结论 | 必须显式产出 gap，不得伪造 bridge node |
| `rule provenance` | `auto` | 契约必测，宿主原生非强制 | stable `rule_path/anchor`、subject ref、`observed_at` | `Node(rule_reference, auto)` + `Evidence(prov://rule/...)` + `Edge(cites/supports)` | `closed` 或 `unsupported` | `medium`，完整宿主接入时可到 `high` | inspection 能列出规则/文档引用；宿主缺位时不能伪造 |
| `rule provenance` | `injected` | 是 | fixture rule/doc payload + cited subject ref | `Node` + `Edge(cites/supports)` + `Evidence` | `closed` | `medium` | 可落盘、可解析、可闭包、可审计 |
| `rule provenance` | `inferred` | 是 | prompt/context/eval refs + inference basis refs | `Node/Edge(inferred)` + `Evidence(prov://inference/...)` | `partial`，条件满足时可 `closed` | `low` 到 `medium` | inspection 明示 `inferred citation`，不得伪装成显式引用 |
| `rule provenance` | `unknown` | 是 | 仅声明“应存在 rule/doc citation” | `GapFinding` | `unknown` 或 `partial` | 不形成正向高置信结论 | 不得伪造 rule node |

## 6. Phase 2 Host Integration Boundaries

### 6.1 Only Ingress Is Replaceable; Contracts Are Not

- Phase 2 只允许把 injected / adapter ingress 替换为真实 host-native ingress。
- 不允许回改 Phase 1 冻结的对象模型、refs 规则、closure 语义、confidence 分层、payload 形状。
- host-native ingress 只能增强，不能降级已有 injected validation 能力。
- `fixture / replay / manual injection` 必须长期保留，继续用于测试、回放与诊断。

### 6.2 Minimal Host Contract

- `conversation/message` host ingress 最少提供：
  - stable `message_id`
  - message role/type
  - `observed_at`
  - content digest 或 summary
  - 可挂接的 target ref
- `skill invocation` host ingress 最少提供：
  - stable invocation id
  - skill 标识
  - caller/callee 关系
  - 时点
  - raw payload evidence
- `exec_command bridge` host ingress 最少提供：
  - stable bridge call id
  - command digest 或 argv digest
  - target ref
  - 时点
  - bridge payload evidence
- `rule provenance` host ingress 最少提供：
  - stable rule/doc id
  - path/anchor
  - cited subject ref
  - 时点
  - citation evidence
- 宿主接入增强的是 facts 可得性、closure 完整度和 confidence 上限。
- 解释权边界保持不变：
  - assessment 仍由 inspection / observer 生成
  - governance hook 仍由治理层生成
  - host ingress 自身不得直接产出 blocker verdict

### 6.3 Host Failure And Degradation Semantics

- 真实 ingress 接不上时，不回退改 contracts。
- 继续保留 `injected / inferred / unknown / unsupported` 路径，inspection 必须仍可工作。
- Phase 2 必须区分：
  - `宿主未提供`
  - `宿主明确否认`
- 二者不能都落成 `unknown`。
- `宿主明确否认` 在 Phase 2 可落成单独的负向事实或负向解释对象，但 Phase 1 不冻结其具体对象模型。

### 6.4 Injected Paths That Stay Or Recede

- 长期保留：
  - `fixture injection`
  - `replay injection`
  - `manual injection`
- 它们继续承担：
  - ingress contract tests
  - snapshot tests
  - 回放与诊断
- 只有“作为宿主替代真值的临时 injected adapter”会被 host-native ingress 部分替换。

### 6.5 What May Eventually Enter Formal Gate

- provenance 不是“接上宿主事件就能 blocker”。
- 未来只有同时满足以下条件的 provenance 结果，才允许进入正式 gate：
  - 高置信
  - 可追溯
  - source closure 成立
  - 直接影响收口正确性
  - 被 provenance-specific policy 明确允许
- 即使 Phase 2 真实宿主接入后，也不得默认把 provenance 接进 `execute` blocker。

## 7. Out Of Scope For Phase 1

- 真实 Codex 宿主层的全覆盖原生采集
- provenance 默认 blocker
- 重型交互式 provenance viewer
- 自动 root cause / remediation 生成
- `execute` 面 provenance 阻断
- 因宿主原生接入而删除 injected / replay / manual validation 路径
