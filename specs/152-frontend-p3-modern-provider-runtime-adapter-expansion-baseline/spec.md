# 功能规格：Frontend P3 Modern Provider Runtime Adapter Expansion Baseline

**功能编号**：`152-frontend-p3-modern-provider-runtime-adapter-expansion-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：承接 `151` 之后的真实 modern provider runtime / adapter expansion 后续工单，formalize provider adapter runtime、受控 runtime carrier 与 rollout boundary，不再停留在 policy truth。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/009-frontend-governance-ui-kernel/spec.md`、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`、`specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md`

> 口径：`145` 已把后续前端主线拉平成 `Track A -> Track B -> Track C -> Track D -> Track E`，`151` 又把 modern provider expansion 的 policy truth、choice-surface boundary、React exposure boundary 与 consumer handoff 固定下来。当前缺的已经不是 `provider admission policy`，而是把这些 truth 变成真实 provider runtime / adapter expansion 承接面的 successor work item。`152` 的职责不是回头重写 `151` 的 policy，也不是在 Ai_AutoSDLC Core 仓库里直接维护现代前端运行时代码，而是把“真实 provider runtime 应落在哪、Core 应输出哪些 scaffold/handoff/证据回流 contract、哪些 rollout 必须在目标业务前端项目或独立适配包中完成”冻结成单一真值。

## 问题定义

当前仓库已经具备三类前置真值：

- `073` 已冻结 provider/style 第一阶段 truth、requested/effective 边界与 `react` 当前 `internal-only` 的事实；
- `150` 已冻结跨 provider consistency certification truth；
- `151` 已冻结 provider admission policy、choice-surface visibility、React exposure boundary，以及 `ProgramService / CLI / verify / global truth` 的 consumer handoff。

但真实 modern provider runtime / adapter expansion 仍然没有 canonical successor 去回答以下问题：

- modern provider 的真实运行时代码到底应落在目标业务前端项目，还是独立适配包，触发条件是什么；
- Core 仓库不维护运行时代码的前提下，应向外部 runtime carrier 输出哪些 scaffold、handoff contract、delivery receipt 与 evidence 回流接口；
- `151` 里的 `admitted / advanced-visible / public-visible / simple-default-eligible` 如何从 policy truth 进入真实 adapter/runtime rollout，而不是继续停留在 artifact truth；
- `react stack visibility` 与 `react provider binding visibility` 被允许升级之后，如何在目标项目里以受控方式 materialize，而不是只停留在 `151` 的状态轴；
- 目标项目或独立适配包完成 runtime expansion 后，应如何把 machine-verifiable 证据写回 Core 的 `ProgramService / verify / global truth / release audit`。

如果没有 `152`，后续实现会继续出现几类偏差：

- 在 `151` policy 已就绪后，真实 provider runtime 仍以会话式、项目私有脚本式方式推进，缺少统一 handoff；
- Core 与目标业务前端项目之间的责任边界再次模糊，出现“Core 直接维护 provider runtime 源码”或“业务项目绕过 Kernel Wrapper / Provider Adapter”；
- `react` 或 modern provider 的公开 rollout 只在 UI 层看起来可见，但没有对应的 adapter evidence 回流到 global truth；
- 是否沉淀为独立适配包缺少统一门槛，导致过早包化或多个目标项目各自漂移。

因此，`152` 的职责是先 formalize 真实 modern provider runtime / adapter expansion 的工程承接边界、runtime carrier 模式、handoff/scaffold contract、证据回流口径与 rollout honesty，再决定后续实现切片如何在 Core 与目标项目之间展开。

## 范围

- **覆盖**：
  - 冻结 `151` 之后的真实 modern provider runtime / adapter expansion successor scope
  - 明确 Ai_AutoSDLC Core、目标业务前端项目、独立适配包三者的责任边界
  - 冻结 runtime carrier 模式：`目标业务前端项目内适配层优先`、`2+ 项目验证后再考虑独立适配包`
  - 冻结 provider runtime scaffold / handoff contract / evidence 回流 contract
  - 冻结 modern provider runtime rollout 与 React public runtime rollout 的受控升级前置条件
  - 冻结后续 runtime 推荐切片：carrier scaffold truth -> delivery handoff -> evidence ingestion -> ProgramService / verify / global truth surfacing
- **不覆盖**：
  - 不在本工单中直接实现真实 modern provider 运行时代码
  - 不在 Ai_AutoSDLC Core 仓库中维护目标业务项目或独立适配包里的 adapter 源码
  - 不重写 `073` 的 provider/style truth、`150` 的 consistency truth、`151` 的 provider expansion policy truth
  - 不直接把 `react` 或第二 public provider 伪装成已经 public-ready
  - 不把公司组件库内部历史源码治理纳入当前工单

## 已锁定决策

- `152` 是 `151` 的正式 successor work item，不重新做 `145` 级 capability census；
- Ai_AutoSDLC Core 负责 contract、rule、gate、handoff、evidence ingestion 与 truth surfacing，不负责直接承载 modern provider 运行时代码；
- 真实 provider runtime / adapter 承载优先落在目标业务前端项目内的受控适配层；只有在 `2 个及以上项目` 验证出稳定复用价值后，才考虑升级为独立适配包；
- 业务项目不得绕过 `Kernel Wrapper / Provider Adapter`，直接把公司组件库或底层 runtime 作为页面默认入口；
- `152` 只能消费 `151` 已冻结的 `certification_gate / roster_admission_state / choice_surface_visibility / react visibility`，不得重新解释 public exposure policy；
- runtime rollout 必须把 machine-verifiable 证据回流到 Core 的 `ProgramService / CLI / verify / global truth / release audit`，不能只停留在外部项目本地状态；
- 当前工单只冻结 successor baseline，不宣称真实 runtime adapter、独立包化或 React public rollout 已落地。

## 用户故事与验收

### US-152-1 — Framework Maintainer 需要真实 runtime successor 的单一真值

作为**框架维护者**，我希望 `151` 之后的真实 modern provider runtime / adapter expansion 有独立 successor work item，这样我不需要继续把 policy truth 与运行时代码承接混写。

**优先级说明**：P0。`151` 已完成既定 decomposition；如果没有 successor，前端主线会再次回到“策略已冻结、运行时靠会话推进”的状态。

**独立测试**：只阅读 `152/spec.md`，就能明确知道真实 runtime expansion 解决什么、依赖什么、当前明确不解决什么。

**验收场景**：

1. **Given** 我审阅 `152/spec.md`，**When** 我检查 scope 与 locked decisions，**Then** 我能明确看到它承接的是 `151` 之后的真实 runtime successor
2. **Given** 我对照 `009/151`，**When** 我检查边界，**Then** 我能确认 Core 不直接维护 provider 运行时代码

### US-152-2 — Delivery Owner 需要清晰的 runtime carrier 与 handoff contract

作为**交付负责人**，我希望真实 provider runtime 的 carrier mode、scaffold contract 与 evidence 回流 contract 被提前冻结，这样我可以在目标业务前端项目中落地，而不是继续靠口头约定。

**优先级说明**：P0。没有 handoff contract，`151` 的 policy truth 无法变成真实运行时交付。

**独立测试**：`152` 的实体与 handoff contract 能直接指导目标项目或独立适配包的承接。

**验收场景**：

1. **Given** 我准备在目标业务前端项目中接入 modern provider runtime，**When** 我查看 `152`，**Then** 我能找到 carrier mode、scaffold 输出与 evidence 回流要求
2. **Given** 我评估是否沉淀独立适配包，**When** 我查看 `152`，**Then** 我能看到 `2+ 项目验证后再包化` 的门槛

### US-152-3 — Reviewer 需要 React / public rollout 的真实边界

作为**reviewer**，我希望 `152` 明确 React public runtime rollout 与第二 public provider rollout 必须消费哪些上游 truth、由谁提供证据回流，这样我能判断后续 rollout 是否越界。

**优先级说明**：P0。provider 是否真正公开，不再只是 `151` 的可见性策略，而是运行时事实与证据事实。

**独立测试**：阅读 `152` 后，reviewer 能明确说出 runtime rollout 与 policy truth 的分层关系。

**验收场景**：

1. **Given** 我查看 `152` 的 rollout boundary，**When** 我核对 `151`，**Then** 我能区分“policy allowed”和“runtime delivered”是两层不同真值
2. **Given** 我检查 React 相关条目，**When** 我对照 `073/151`，**Then** 我能确认 `152` 没有把 React public runtime 伪装成已完成

### US-152-4 — Program Truth Owner 需要外部 runtime 证据回流口径

作为**program/global truth 维护者**，我希望外部项目完成 runtime adapter expansion 后的证据可以 machine-verifiable 地回流到 Core，这样 release truth 才不会再次脱节。

**优先级说明**：P1。没有回流口径，global truth 只能持续停留在 policy 层。

**独立测试**：`152/plan.md` 可以直接读出 evidence ingestion 与 global truth surfacing 的后续顺序。

**验收场景**：

1. **Given** 我审阅 `152/plan.md`，**When** 我检查 future runtime slices，**Then** 我能看到 scaffold/handoff/evidence/program truth 的承接顺序
2. **Given** 我对照 `146/151`，**When** 我检查 evidence return contract，**Then** 我能确认 runtime 事实不是只留在目标项目本地

### 边界情况

- provider 在 `151` 中已 `admitted`，但目标项目尚无 adapter scaffold 时，不得误报为 runtime delivered
- `react stack visibility` 在 policy 层允许升级，但目标项目未提供 binding/runtime evidence 时，不得进入 public runtime truth
- 仅有单个项目实验性接入时，不得提前宣称独立适配包已经成为 canonical carrier
- `blocked` 或 `needs-recheck` 的 provider 不得进入真实 public runtime rollout，即使外部项目已有临时实验分支
- 目标项目若绕过 `Kernel Wrapper / Provider Adapter` 直接绑定底层组件库，应被视为 boundary violation，而不是 runtime delivered

## 冻结的真实 runtime 承接模型

### Runtime Carrier Modes

`152` 将真实 modern provider runtime 的承接载体拆成两种受控模式：

| carrier_mode | 含义 | 适用条件 |
|--------------|------|----------|
| `target-project-adapter-layer` | 在目标业务前端项目内，以受控 adapter / wrapper 层承载 modern provider runtime | 首选模式；单项目验证阶段 |
| `independent-adapter-package` | 在独立适配包中沉淀复用的 modern provider adapter/runtime carrier | 仅在 `2+ 项目` 验证同形态稳定复用后允许考虑 |

补充规则：

1. 当前默认推荐 `target-project-adapter-layer`，不得在首个项目就强行包化。
2. 进入 `independent-adapter-package` 前，必须先证明多个项目的 wrapper / adapter 形态稳定且治理边界一致。
3. 不论落在哪种 carrier mode，Ai_AutoSDLC Core 都只维护 contract / handoff / evidence truth，不直接维护运行时代码主体。

### Runtime Expansion State Axes

真实 runtime 扩张至少拆成以下状态轴：

| 状态轴 | 允许值 | 含义 |
|--------|--------|------|
| `policy_gate` | 消费 `151` 的 `certification_gate` / visibility truth | 表达 policy 是否允许进入下一阶段 |
| `carrier_mode` | `target-project-adapter-layer` / `independent-adapter-package` | 表达运行时代码落位方式 |
| `runtime_delivery_state` | `not-started` / `scaffolded` / `implemented` / `verified` | 表达真实 adapter/runtime 的交付进度 |
| `evidence_return_state` | `missing` / `partial` / `fresh` | 表达外部项目证据是否已回流并可被 Core 验证 |

约束：

- `policy_gate` 只表达是否被允许，不等于 runtime 已交付；
- `runtime_delivery_state=implemented` 不等于 `evidence_return_state=fresh`；
- 只有 `runtime_delivery_state=verified` 且 `evidence_return_state=fresh`，才允许被 global truth 视为真实 runtime delivered；
- `policy_gate` 未满足时，不得继续推进 `scaffolded -> implemented` 的公开 rollout。

### Runtime Handoff Contract

Core 对外部 runtime carrier 至少输出以下 handoff surface：

1. **Adapter Scaffold Contract**：定义目标项目必须具备的 Kernel Wrapper、Provider Adapter、Legacy Adapter 受控桥接层结构。
2. **Runtime Boundary Receipt**：记录当前 provider/runtime rollout 依赖的上游 truth refs、policy gate、carrier mode 与 boundary constraints。
3. **Evidence Return Contract**：定义目标项目完成 adapter/runtime 后，如何回传 machine-verifiable 证据与 refs。
4. **Program Surfacing Contract**：定义 Core 如何把外部 runtime evidence 接入 `ProgramService / verify / global truth / release audit`。

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-152-001 | `152` 必须把 `151` 之后的真实 modern provider runtime / adapter expansion 定义为独立 successor baseline，而不是继续混写在 `151` 的非目标里 |
| FR-152-002 | `152` 必须明确继续遵守 `073 -> 150 -> 151 -> 真实 runtime expansion` 的单一真值顺序 |
| FR-152-003 | `152` 必须明确 Ai_AutoSDLC Core 不承载真实 provider 运行时代码，只承载 contract / handoff / evidence truth |
| FR-152-004 | `152` 必须明确当前工单是 formal baseline，不直接宣称 modern provider runtime 或 React public runtime 已落地 |

### Carrier And Runtime Boundary

| ID | 需求 |
|----|------|
| FR-152-005 | `152` 必须冻结 `target-project-adapter-layer` 与 `independent-adapter-package` 两种 carrier mode 的定义与切换门槛 |
| FR-152-006 | `152` 必须明确默认优先使用目标业务前端项目内的受控 adapter 层，而不是首个项目就独立包化 |
| FR-152-007 | `152` 必须明确只有在 `2+ 项目` 验证同形态 wrapper / adapter 稳定复用后，才允许考虑独立适配包 |
| FR-152-008 | `152` 必须明确目标项目不得绕过 `Kernel Wrapper / Provider Adapter`，直接把底层组件库作为页面默认入口 |
| FR-152-009 | `152` 必须明确真实 runtime expansion 仍需遵守 Legacy Adapter / Compatibility Wrapper 的受控桥接边界 |

### Runtime Handoff And Evidence Return

| ID | 需求 |
|----|------|
| FR-152-010 | `152` 必须定义 machine-verifiable 的 Adapter Scaffold Contract，而不是口头约定目标项目如何起 adapter 层 |
| FR-152-011 | `152` 必须定义 Runtime Boundary Receipt，记录上游 truth refs、policy gate、carrier mode 与 boundary constraints |
| FR-152-012 | `152` 必须定义 Evidence Return Contract，明确目标项目或独立适配包应回传哪些 machine-verifiable 证据 |
| FR-152-013 | `152` 必须定义外部 runtime evidence 如何进入 Core 的 `ProgramService / verify / global truth / release audit` |
| FR-152-014 | `152` 必须明确 runtime delivered truth 必须同时满足 `runtime_delivery_state` 与 `evidence_return_state`，不得只凭外部项目自述通过 |

### Rollout Honesty

| ID | 需求 |
|----|------|
| FR-152-015 | `152` 必须明确 `151` 的 `admitted / public-visible / simple-default-eligible` 仍属于 policy truth，不等于 runtime delivered |
| FR-152-016 | `152` 必须明确 React public runtime rollout 只能在满足 `073/150/151` 上游 truth 后，由真实 runtime evidence 证明 |
| FR-152-017 | `152` 必须明确第二 public provider 或 React public rollout 的真实交付必须通过 evidence return，而不是只靠 CLI/policy state |
| FR-152-018 | `152` 必须明确当前工单不伪造任何外部项目 adapter 已完成或 public rollout 已完成 |

### Successor Execution

| ID | 需求 |
|----|------|
| FR-152-019 | `152` 必须在 `plan.md` 中给出后续 runtime 推荐切片，至少包括 scaffold truth、delivery handoff、evidence ingestion、program surfacing |
| FR-152-020 | `152` 必须在 `tasks.md` 中把 docs-only formal freeze 与后续 runtime 承接清晰分离 |
| FR-152-021 | `152` 必须允许后续执行者直接根据本工单进入真实 target-project adapter 承接，而无需再次回到顶层设计做 carrier census |
| FR-152-022 | `152` 必须把 `python -m ai_sdlc program truth sync --execute --yes` 与 `python -m ai_sdlc program truth audit` 纳入 close-out 的强制真值门禁 |

## 关键实体

- **RuntimeCarrierMode**：表达真实 modern provider runtime 的承接模式
- **AdapterImplementationTarget**：表达目标业务前端项目或独立适配包这一运行时落位实体
- **ProviderAdapterRuntimeContract**：表达 Core 输出给外部 runtime carrier 的 scaffold / boundary / receipt 合约
- **RuntimeExpansionEvidenceReceipt**：表达外部项目完成 runtime 交付后回传到 Core 的 machine-verifiable 证据摘要
- **RuntimeBoundaryDecision**：表达当前 provider/runtime rollout 是否满足进入下一阶段的边界裁决

## 成功标准

- **SC-152-001**：`152` 能独立表达 `151` 之后真实 runtime expansion 的 scope、non-goals 与 engineering boundary，而无需继续依赖会话记忆
- **SC-152-002**：`152` 明确隔离 policy truth 与 runtime delivered truth，避免再次把 provider policy 当成真实 rollout 完成
- **SC-152-003**：`152` 明确给出 carrier mode、Adapter Scaffold Contract、Evidence Return Contract 与 Program Surfacing Contract
- **SC-152-004**：`152` 明确 Ai_AutoSDLC Core 与目标业务前端项目/独立适配包的边界，不再模糊谁负责真实运行时代码
- **SC-152-005**：`152` 能作为后续真实 modern provider runtime / adapter expansion 的 canonical planning input，被 global truth 直接消费

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/151-frontend-p3-modern-provider-expansion-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
