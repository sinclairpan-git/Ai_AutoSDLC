# 功能规格：Frontend P3 Modern Provider Expansion Baseline

**功能编号**：`151-frontend-p3-modern-provider-expansion-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：承接 `145 Track E`，将 `modern provider expansion`、`public provider choice surface` 与 `React exposure boundary` 正式 materialize 为最后一条前端后续主线 child work item。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`、`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`、`specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md`

> 口径：`145` 已把剩余前端 later-phase capability 拉平成 `Track A -> Track B -> Track C -> Track D -> Track E` 的 canonical child DAG；`073` 已冻结 provider/style 第一阶段 truth，并明确 `react` 目前只作为内部可建模值存在、不进入 UI/推荐/计算；`150` 已冻结 cross-provider consistency 的认证门槛、public choice surface 受限开放规则与 Track E readiness gate。`151` 的职责不是跳过 Track D 直接扩 provider，也不是立即把 React 暴露到所有入口，而是把“哪些 modern provider 可被纳入候选 roster、何时允许进入 public choice surface、何时只允许受限暴露、React exposure 如何从 internal-only 进入受控公开边界”冻结成 Track E 的单一真值。

## 问题定义

当前仓库已经具备 Track E 所需的两类直接上游能力：

- `073` 已提供 provider/style 第一阶段真值，包括 `provider_manifest.style_support_matrix`、requested/effective 边界、simple/advanced mode 行为，以及 `react` 当前 internal-only 的事实；
- `150` 已提供 Track E 必须消费的 `ready / conditional / blocked` 一致性准入门槛，以及 provider expansion 不得绕开的 certification truth。

但 Track E 仍缺少一条独立 child 去回答以下问题：

- 额外的 modern provider 到底如何进入候选 roster，必须满足哪些 admission 条件，哪些只能保持 deferred；
- public provider choice surface 何时可以从当前受限状态扩张，哪些 provider 可以进入 simple mode、哪些只能进入 advanced mode、哪些只能 internal-only；
- `react` 何时可以从 `073` 的 internal-only 状态进入公开边界，是先 advanced-only、再 public selectable，还是继续只做建模值；
- provider expansion 到底消费 `150` 的哪一层 certification truth，而不是每次扩 provider 时再临时解释 `conditional`/`blocked`；
- provider roster、choice surface 与 React exposure 扩张之后，应如何进入 ProgramService / CLI / verify / global truth，而不是继续只停留在文档口径。

如果没有 `151`，后续实现会继续出现几类偏差：

- 在没有统一 admission/readiness rules 的情况下直接加 provider，导致 roster 扩张与 public exposure 每次都按会话解释推进；
- 把 `react` 从 internal-only 改成 public selectable，却没有经过 Track D certification 或 choice-surface boundary 审核；
- 把 `conditional` provider 直接放入 simple mode 主推荐，破坏 `073` 已冻结的 requested/effective 与 degraded/supported 边界。

因此，`151` 的职责是先 formalize Track E 的 canonical boundary、provider admission policy、choice-surface rollout、React exposure state 与 downstream truth surfacing，再决定后续 runtime 如何逐批落地。

## 范围

- **覆盖**：
  - 冻结 Track E `modern provider expansion` 的问题定义、单一真值边界与 owner boundary
  - 明确 `073` 提供 provider/style 第一阶段 truth，`150` 提供必须消费的 certification/readiness gate
  - 冻结 modern provider admission policy、public provider choice surface expansion policy 与 React exposure boundary
  - 冻结 provider 的 `certification_gate`、`roster_admission_state`、`choice_surface_visibility` 为相互独立的状态轴
  - 冻结 simple mode / advanced mode / internal modeling 对 provider roster 的准入矩阵与展示规则
  - 冻结后续 runtime 推荐切片：admission models -> roster/choice-surface artifacts -> validator/policy -> ProgramService/CLI/verify/global truth handoff
- **不覆盖**：
  - 不重写 `073` 已完成的 provider/style 第一阶段 truth
  - 不重写 `150` 的 consistency certification truth、gate matrix 或 public exposure 受限条件
  - 不在本工单中直接实现新的 provider adapter、scaffold、真实 React public runtime 或新的 UI
  - 不把 `conditional`/`blocked` provider 伪装成已可公开推荐
  - 不绕过 Track D certification 直接放行 provider roster 扩张

## 已锁定决策

- `151` 是 `145` 已指定的 Track E child，不重新做 capability census；
- Track E 必须消费 `073` provider/style 第一阶段 truth 与 `150` 的 readiness gate，禁止回退到“先加 provider、后补认证”的倒挂流程；
- Track E 不得把 provider 的认证结果与 UI 暴露策略混成一个枚举；至少要将 `certification_gate`、`roster_admission_state`、`choice_surface_visibility` 三层分开定义；
- `react` 当前仍保持 `073` 定义的 internal-only 事实；Track E 只能冻结其升级路径与公开门槛，不得在本工单中伪造已 public-ready；
- simple mode 仍保持 `073` 冻结的一套主推荐，不展示并列备选；advanced mode 才允许结构化暴露 gated provider options；`blocked` provider 不得进入任何 public choice surface；
- Track E 必须定义 pair-level `150` certification truth 如何聚合为 provider-level admission truth，避免同一 provider 因多 pair / 多 journey / 多 roster scope 得出多个互相冲突的公开状态；
- Track E 必须定义 machine-verifiable 的 roster/choice-surface artifact root、handoff schema 与 truth surfacing record，供 ProgramService、CLI、verify 与 global truth 直接消费；
- `151` 当前只做 docs-only formal freeze，不进入 `src/` / `tests/`，不宣称 modern provider expansion runtime 已落地。

## 用户故事与验收

### US-151-1 — Maintainer 需要独立的 Track E baseline

作为**框架维护者**，我希望 modern provider expansion 有独立 child work item，这样我不需要继续把 provider 扩张、choice surface 和 React exposure 混写在 consistency 或第一阶段 provider/style 工单里。

**优先级说明**：P0。`145` 已明确 Track E 必须独立存在；如果继续缺位，provider roster 扩张仍会失去统一准入规则。

**独立测试**：只阅读 `151/spec.md`，就能知道 Track E 到底解决什么、依赖什么、当前明确不解决什么。

**验收场景**：

1. **Given** 我审阅 `151/spec.md`，**When** 我检查 scope 与 locked decisions，**Then** 我能明确看到 Track E 与 `073/150` 的边界
2. **Given** 我对照 `145`，**When** 我检查 child DAG，**Then** 我能确认 `151` 就是 Track E 的正式承接

### US-151-2 — Provider roster owner 需要稳定的 admission policy

作为**provider roster 维护者**，我希望 Track E 明确 provider 何时可以进入 internal-only、advanced-only、public-conditional、public-ready，这样我不需要在每次新增 provider 时重新解释准入规则。

**优先级说明**：P0。没有 admission policy，provider expansion 仍会退回会话式裁决。

**独立测试**：`151` 的实体与 gate matrix 可以直接被 runtime 实现与 global truth 引用。

**验收场景**：

1. **Given** 我准备扩张 provider roster，**When** 我查看 `151`，**Then** 我能找到必须消费的 readiness gate 与 choice-surface policy
2. **Given** 我检查 `151` 的 non-goals，**When** 我规划实现切片，**Then** 我不会把 adapter/runtime 真实实现混进当前 child

### US-151-3 — Reviewer 需要 public choice surface 的诚实边界

作为**reviewer**，我希望 `151` 明确 simple mode、advanced mode 与 internal-only 对 provider 的不同准入规则，这样我可以判断后续公开暴露是不是越过了既定边界。

**优先级说明**：P0。provider 是否公开，不只是 roster 问题，也是用户面风险控制问题。

**独立测试**：阅读 `151` 后，reviewer 能明确说出 `public-ready`、`public-conditional` 与 `blocked` 在 choice surface 上的差异。

**验收场景**：

1. **Given** 我查看 `151` 的 choice surface policy，**When** 我核对 `073/150`，**Then** 我能区分 simple mode、advanced mode 与 internal-only 的准入边界
2. **Given** 我查看 `151` 的范围，**When** 我检查 React exposure 与 provider choice surface，**Then** 我能确认它不会伪造已公开

### US-151-4 — React boundary owner 需要明确升级路径

作为**React 边界维护者**，我希望 `151` 明确 `react` 从 internal-only 到受控公开的状态迁移条件，这样我不需要在 provider 扩张时临时解释 React 是否应暴露。

**优先级说明**：P1。React exposure 是 later-phase 目标，但一旦缺少边界，会直接破坏 `073` 已冻结的当前事实。

**独立测试**：`151/plan.md` 可以直接读出 React exposure 只在满足 gate 的前提下进入下一阶段。

**验收场景**：

1. **Given** 我审阅 `151/plan.md`，**When** 我检查 React exposure boundary，**Then** 我能看到从 internal-only 到 advanced/public 的明确升级条件
2. **Given** 我对照 `073`，**When** 我检查 current-state honesty，**Then** 我能确认 `151` 没有把 `react` 伪装成已经 public-ready

### 边界情况

- provider 通过 Track D 的 `conditional` 认证时，只能在受限场景暴露，不能默认进入 simple mode 主推荐
- provider 处于 `blocked` 或 `needs-recheck` 时，不得进入 public choice surface，即使内部已有建模或实验值
- `react` 即使在内部模型中存在，也不得因为“能建模”就自动进入公开 provider 列表
- 新 provider 可先进入 internal-only 或 advanced-only roster，用于收集后续认证与适配证据，但这不代表已 public-ready
- public choice surface 的扩张必须保留 requested/effective 边界，不得覆盖用户原始选择或静默 fallback

## 冻结的 Track E 状态与公开策略模型

### Provider Admission And Exposure Model

Track E 不使用单一 `provider exposure state`，而是至少拆分为三层正交状态：

| 状态轴 | 允许值 | 含义 |
|--------|--------|------|
| `certification_gate` | 消费 `150` 的 `ready / conditional / blocked` | 表达是否满足 Track D 认证门槛 |
| `roster_admission_state` | `candidate` / `admitted` / `deferred` | 表达 provider 是否已进入可被框架承认的候选 roster |
| `choice_surface_visibility` | `hidden` / `advanced-visible` / `public-visible` / `simple-default-eligible` | 表达 provider 是否以及以何种方式进入用户可见选择面 |

约束：

- `certification_gate` 只表达认证结果，不直接决定 UI 暴露层级；
- `choice_surface_visibility` 只表达展示范围，不得编码 `conditional/blocked` 等认证语义；
- `roster_admission_state=admitted` 不等于 automatically public-visible；
- `simple-default-eligible` 只允许在 `certification_gate=ready` 且满足 simple mode 主推荐条件时出现。

### Choice Surface Admission Matrix

| surface | `hidden` | `advanced-visible` | `public-visible` | `simple-default-eligible` |
|---------|----------|--------------------|------------------|---------------------------|
| internal modeling | allowed | allowed | allowed | allowed |
| simple mode default recommendation | forbidden | forbidden | forbidden | allowed |
| advanced mode chooser | forbidden | allowed | allowed | allowed |
| public choice surface | forbidden | forbidden | allowed with caveat when gate != blocked | allowed |

补充规则：

1. simple mode 继续保持 `073` 已冻结的“一套主推荐”产品策略，不展示并列 provider 备选。
2. advanced mode 是 provider 受控扩张的主要公开入口；`certification_gate=conditional` 的 provider 只允许在此处受控展示并附带 caveat。
3. `certification_gate=blocked` 的 provider 不得进入 `public-visible` 或 `simple-default-eligible`。
4. `public-visible` 不等于 `simple-default-eligible`；前者表示可在公开选择面出现，后者表示可进入 simple mode 主推荐候选。

### React Exposure Boundary

`react` 当前状态保持为 `073` 已冻结的 internal-only stack value。Track E 将 React 暴露拆成两个相互关联、但不可混写的选择单元：

- **React stack visibility**：用户是否能看到 `frontend_stack=react`
- **React provider binding visibility**：当 `frontend_stack=react` 可见时，是否存在可选的 React provider 绑定项

Track E 只冻结以下升级路径：

1. `react stack visibility: hidden -> advanced-visible`：前提是至少存在一个 React provider binding 已进入 `roster_admission_state=admitted`，且对应 `certification_gate` 不为 `blocked`。
2. `react provider binding visibility: hidden -> advanced-visible/public-visible`：前提是对应 provider binding 满足 Track D gate 与 Track E choice-surface policy。
3. `react stack visibility/public-visible -> simple-default-eligible`：前提是 React stack 与其默认 provider binding 均满足 `certification_gate=ready`，且不会破坏 `073` 当前 requested/effective honesty。
4. 在 Track E docs-only baseline 中，不允许宣称 `react` 已经完成以上任一升级。

## 冻结的 Track E handoff contract

### Canonical artifact root

```text
governance/frontend/provider-expansion/
├── provider-expansion.manifest.yaml
├── handoff.schema.yaml
├── truth-surfacing.yaml
├── choice-surface-policy.yaml
├── react-exposure-boundary.yaml
└── providers/
    └── <provider_id>/
        ├── admission.yaml
        ├── roster-state.yaml
        └── certification-ref.yaml
```

### Frozen handoff schema

- `provider-expansion.manifest.yaml`：声明 schema version、producer version、source roster ref、candidate roster ref、artifact root ref。
- `handoff.schema.yaml`：声明 `certification_gate / roster_admission_state / choice_surface_visibility / provider_certification_aggregate / react_stack_visibility / react_binding_visibility / truth_surface` 的字段面。
- `truth-surfacing.yaml`：声明 Track E 输出进入 AI-SDLC global truth 时的 `truth_layer`、`provider_roster_state`、`choice_surface_state`、`react_stack_visibility`、`react_binding_visibility`、`artifact_root_ref` 与 `certification_ref`。
- `choice-surface-policy.yaml`：声明 simple mode / advanced mode / public choice surface 的准入矩阵。
- `react-exposure-boundary.yaml`：声明 `react` 的 current-state、upgrade prerequisites 与 exposure limits。
- `providers/<provider_id>/admission.yaml`：记录单个 provider 的 admission 条件与当前 `certification_gate / roster_admission_state / choice_surface_visibility`。
- `providers/<provider_id>/roster-state.yaml`：记录 provider 当前在 roster/simple/advanced/public surface 中的可见性。
- `providers/<provider_id>/certification-ref.yaml`：记录指向 `150` pair-level certification bundle 的 repo-relative refs。
- `providers/<provider_id>/provider-certification-aggregate.yaml`：记录如何从多个 pair / journey / roster scope 的 certification 结果聚合出单个 provider 的 admission truth。

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-151-001 | `151` 必须把 Track E 定义为独立的 `modern provider expansion` child baseline，而不是 `073` 或 `150` 的附注 |
| FR-151-002 | `151` 必须明确 Track E 位于 `150` 之后，并继续遵守 `schema -> theme -> quality -> consistency -> provider expansion` 的单一真值顺序 |
| FR-151-003 | `151` 必须明确 `073` 提供 provider/style 第一阶段 truth，`150` 提供 readiness/certification gate，当前工单不重复这些能力 |
| FR-151-004 | `151` 必须明确当前 work item 的非目标，包括真实 provider adapter/runtime 落地、绕开 consistency gate、伪造 React 已公开可用 |

### Provider Admission And Choice Surface Policy

| ID | 需求 |
|----|------|
| FR-151-005 | `151` 必须明确 Track E 至少承接 `provider admission policy`、`public choice surface expansion policy`、`React exposure boundary` 三类能力 |
| FR-151-006 | `151` 必须将 provider 的 `certification_gate`、`roster_admission_state`、`choice_surface_visibility` 拆成独立状态轴，而不是单一 exposure 枚举 |
| FR-151-007 | `151` 必须明确 simple mode、advanced mode、public choice surface 与 internal modeling 的准入矩阵与展示规则，而不是只写“以后再开放” |
| FR-151-008 | `151` 必须明确 simple mode 继续保持单一路径主推荐；即便 provider 可 public-visible，也不得自动成为 simple mode 默认候选 |
| FR-151-009 | `151` 必须明确 `conditional` provider 只允许在 advanced mode 或受限 public surface 中展示并附带 caveat，`blocked` provider 不得进入 public choice surface |

### React Exposure Boundary

| ID | 需求 |
|----|------|
| FR-151-010 | `151` 必须明确 `react` 当前仍是 internal-only 的 current-state，不得伪造已公开 |
| FR-151-011 | `151` 必须把 React 暴露拆成 `react stack visibility` 与 `react provider binding visibility` 两个选择单元，而不是模糊成“React 已公开” |
| FR-151-012 | `151` 必须冻结 `react` 从 internal-only 到 advanced/public exposure 的升级路径与前置条件 |
| FR-151-013 | `151` 必须明确 React exposure 只能消费 Track D gate 与 Track E choice-surface policy，不得单独绕开 roster admission 或 requested/effective honesty |

### Upstream Inputs And Handoff

| ID | 需求 |
|----|------|
| FR-151-014 | `151` 必须明确上游至少依赖 `073/150`，并说明分别提供 provider/style truth 与 consistency certification truth |
| FR-151-015 | `151` 必须明确 provider admission 必须消费 `150` 的 `ready / conditional / blocked` gate，而不是重新解释 readiness |
| FR-151-016 | `151` 必须定义 machine-verifiable 的 provider expansion artifact root，而不是人工清单、临时对话或未归档脚本输出 |
| FR-151-017 | `151` 必须定义 pair-level `150` certification truth 如何聚合为单个 provider 的 admission truth，避免单个 provider 出现多个相互冲突的公开状态 |
| FR-151-018 | `151` 必须定义 future `provider admission bundle`、`choice surface policy` 与 `react exposure boundary` handoff contract，供 ProgramService、CLI、verify 与 global truth 直接消费 |

### Program Surfacing And Rollout Honesty

| ID | 需求 |
|----|------|
| FR-151-019 | `151` 必须明确 ProgramService / CLI / verify constraints 至少消费哪些最小字段，以及它们分别如何对应 pass/warn/block、chooser visibility 与 roster admission 决策 |
| FR-151-020 | `151` 必须定义 Track E 输出进入 AI-SDLC global truth 的 truth surfacing record，包括 `truth_layer`、`provider_roster_state`、`choice_surface_state`、`react_stack_visibility`、`react_binding_visibility`、`artifact_root_ref` 与 `certification_ref` |
| FR-151-021 | `151` 必须明确 Track E 输出在 global truth 中属于 planning truth、runtime truth 还是 release gate input，以及 program truth / release audit 应消费哪一层作为 canonical state |
| FR-151-022 | `151` 必须在 `plan.md` 中给出未来 runtime 推荐切片，至少包括 admission models、roster/choice-surface artifacts、validator/policy、ProgramService/CLI/verify/global truth handoff |
| FR-151-023 | `151` 必须清楚区分 docs-only formal freeze、后续 runtime slices 与 truth refresh readiness，不得用“provider expansion”掩盖尚未实现的事实 |
| FR-151-024 | `151` 当前不得宣称 modern provider roster、public choice surface、React exposure runtime 已落地；close 语义只能是“Track E canonical baseline 与 decomposition 已冻结” |
| FR-151-025 | `151` 必须把 `python -m ai_sdlc program truth sync --execute --yes` 与 `python -m ai_sdlc program truth audit` 纳入 Track E close-out 的强制真值门禁 |

## 关键实体

- **Provider Admission Policy**：表达 provider 如何从 deferred 候选进入受控 roster
- **Provider Admission State**：表达 provider 是否已从 candidate 进入 admitted/deferred roster
- **Choice Surface Visibility State**：表达 provider 在 hidden/advanced/public/simple-default 之间的可见性层级
- **Choice Surface Policy**：表达 simple mode、advanced mode、public choice surface 与 internal modeling 的准入矩阵
- **React Stack Visibility State**：表达 `frontend_stack=react` 在 hidden/advanced/public/simple-default 之间的可见性
- **React Provider Binding Visibility State**：表达 React provider binding 是否可见及其受何种 gate 约束
- **React Exposure Boundary**：表达 `react` 的 current-state、升级路径与暴露约束
- **Provider Admission Bundle**：表达单个 provider 对 global truth / ProgramService 的 admission 结果与 certification 聚合引用
- **Provider Certification Aggregate**：表达如何从多个 pair-level certification 结果聚合为单个 provider 的 canonical admission truth
- **Truth Surfacing Record**：表达 Track E 输出如何进入 AI-SDLC global truth 的稳定字段面与引用关系

## 推荐的 Track E capability decomposition

| 子域 | 主要职责 | 必须消费的上游 truth | 当前不做 |
|------|----------|----------------------|----------|
| `Admission Policy Layer` | 定义 provider 从 candidate 到 admitted/deferred 的 admission 规则 | `073`、`150` | 不直接实现 adapter/runtime |
| `Choice Surface Layer` | 定义 simple/advanced/public surface 的可见性矩阵与展示规则 | `073`、`150` | 不直接改 UI |
| `React Exposure Layer` | 定义 React stack visibility、binding visibility 与受控公开边界 | `073`、`150` | 不伪造 React 已公开 |
| `Program Surfacing Layer` | surfaced provider roster、choice surface、react exposure truth | Track E 前三层输出 | 不绕开 Track D gate |

## 成功标准

- **SC-151-001**：`151` 能独立表达 Track E 的 scope、non-goals、upstream inputs 与 downstream handoff，而无需重新回到顶层设计临时推断
- **SC-151-002**：`151` 明确隔离 `073/150` 已提供 truth 与 Track E 自身新增的 provider expansion 能力，不再误报已完成内容
- **SC-151-003**：`151` 明确要求 Track E 必须消费 `150` 的 readiness/certification gate，不再退回“先扩 provider 再补认证”
- **SC-151-004**：`151` 的 `plan.md / tasks.md` 能直接读出后续 runtime 切片与 ProgramService/CLI/verify/global truth 接入顺序
- **SC-151-005**：`151` 明确冻结 provider admission state、choice-surface visibility、React stack/binding visibility 与 certification aggregation，避免后续 runtime 再发明第二套规则
- **SC-151-006**：`151` formal docs 不再包含模板占位、范围冲突或“provider expansion/consistency/runtime”混写的模糊表述

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/150-frontend-p2-cross-provider-consistency-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
