# 功能规格：Frontend P2 Page UI Schema Baseline

**功能编号**：`147-frontend-p2-page-ui-schema-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（implementation baseline）
**输入**：承接 `145` 所冻结的 Track A，将更深的 `page schema / UI schema / schema versioning / render slot truth` 正式物化为下一条前端主线 child work item。参考：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`、`specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md`、`specs/073-frontend-p2-provider-style-solution-baseline/spec.md`、`specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md`

> 口径：`145` 已把剩余前端 deferred capability 全量拉平，并明确 Track A 的下一条 child 必须是 `frontend-p2-page-ui-schema-baseline`。`147` 的职责不是直接实现新的 provider 或 theme 系统，而是把 “provider-neutral page schema / UI schema / schema versioning / render slot truth” 物化成 framework 内可验证的 runtime baseline，作为后续 `multi-theme/token governance`、`quality platform`、`cross-provider consistency` 的共同上游。

## 问题定义

当前前端主线已经具备几条关键基础：

- `011/015` 已冻结 `Contract / UI Kernel` 的基础边界；
- `068` 已把 page recipe expansion 正式化；
- `073` 已完成 provider/style 第一阶段的 solution baseline；
- `145` 已明确顶层设计中后续 Track A-E 的顺序与边界。

但目前仍缺少一个单独的 canonical child，去回答这些更深层的结构问题：

- 页面结构到底如何被表达成 provider-neutral schema，而不只是一组 recipe/solution 约定；
- UI schema、page schema、render slot、section anchor、field block 之间的边界如何固定；
- 未来更复杂的企业页面、多区块布局、可扩展控件区与 schema versioning 如何在不重写 `068/073` 的前提下继续演进；
- 后续的 theme token、quality platform、cross-provider consistency 应该消费哪一层共同结构真值。

如果没有 `147` 这条 child，后续实现会反复出现两个风险：

- 把更深的页面结构问题混进 `073` 的 provider/style 轨道里，造成 provider truth 和 schema truth 纠缠；
- 在 quality / consistency / theme 阶段才倒逼补 schema，导致下游工单先跑、上游结构真值后补。

因此，`147` 的职责是先把 page/UI schema 这一层从顶层设计中独立出来，形成后续前端主线的第一个正式 child baseline。

## 范围

- **覆盖**：
  - 冻结 `page schema` 与 `ui schema` 的分层定义
  - 冻结 `schema versioning`、`render slot`、`section anchor`、`provider-neutral layout truth` 的最小 contract
  - 明确 `147` 与 `068/073` 的继承关系，不重写已冻结的 recipe 或 provider/style 第一阶段 truth
  - 明确 `147` 作为 `145 Track A` 的上游地位，为 `Track B/C/D/E` 提供共同 schema anchor
  - 物化 schema models、artifact materialization、validator/versioning 与 provider/kernel handoff surface
  - 冻结并执行实现切片的推荐顺序
- **不覆盖**：
  - 不在本工单中实现新的 provider、theme pack、visual regression 或 cross-provider certification
  - 不开放 React exposure boundary、公开 provider choice surface 或 style editor
  - 不把 `073` 已有的 provider/style solution baseline 回写成 page schema 的唯一来源
  - 不把 Track B/C/D/E 伪装成已经完成

## 已锁定决策

- `147` 是 `145` 明确指定的下一条优先 child，不再重新做 capability census；
- `147` 的 schema truth 必须保持 provider-neutral，不能先绑死在单一 provider 实现上；
- `page schema` 与 `ui schema` 需要显式分层：前者表达页面结构/意图，后者表达可渲染组件结构与 slot 约束；
- `147` 在本工单内继续落实模型、序列化、校验与 provider/kernel consumption handoff，但不得越界进入 theme/quality/provider expansion；
- `147` 完成后，后续 `multi-theme/token governance`、`quality platform`、`cross-provider consistency` 应以上游 schema truth 为 anchor，而不是各自另造结构定义。

## 用户故事与验收

### US-147-1 — Maintainer 需要一个独立的 page/UI schema child baseline

作为**框架维护者**，我希望顶层设计里提到的更深 page/UI schema 能有独立 child work item，这样我不需要再把结构真值塞进 `073` 或后续其他轨道里。

**优先级说明**：P0。`145` 已经把它定为下一条优先 child，如果继续缺位，后续主线仍会重新漏项。

**独立测试**：只阅读 `147/spec.md` 就可以知道 page schema / UI schema 这条 track 要解决什么、依赖什么、当前不解决什么。

**验收场景**：

1. **Given** 我审阅 `147/spec.md`，**When** 我检查核心范围，**Then** 我能明确看到 page schema、ui schema、schema versioning、render slot、section anchor 的定义边界
2. **Given** 我对照 `145`，**When** 我检查 child sequence，**Then** 我能确认 `147` 就是 Track A 的正式承接

### US-147-2 — Provider/Theme/Quality 下游需要共享 schema anchor

作为**后续 child 的执行者**，我希望 page/UI schema 先被 formalize，这样 theme、quality、consistency 等下游工单可以消费同一套结构真值，而不是各自临时推导。

**优先级说明**：P0。缺少共享 schema anchor，会直接导致 Track B/C/D 重复定义页面结构。

**独立测试**：`147` 的 scope 与 downstream dependency 表能直接被后续 `multi-theme/token governance`、`quality platform`、`cross-provider consistency` 引用。

**验收场景**：

1. **Given** 我准备进入 Track B 或 Track C，**When** 我查看 `147`，**Then** 我能找到可引用的 schema anchor，而不需要重新定义 page structure
2. **Given** 我检查 `147` 的边界，**When** 我阅读 non-goals，**Then** 我不会把 theme/quality/provider expansion 混进当前 child

### US-147-3 — Reviewer 需要分清 recipe truth 与 schema truth

作为**reviewer**，我希望 `147` 明确指出它和 `068/073` 的关系，这样我能判断当前是“补更深的结构层”，不是重写已有 recipe/provider truth。

**优先级说明**：P1。当前最容易发生的误解就是把 page schema 当成 `073` 的另一个说法。

**独立测试**：阅读 `147` 后，reviewer 能明确说出 `068`、`073`、`147` 三者边界。

**验收场景**：

1. **Given** 我对照 `068` 和 `073`，**When** 我查看 `147` 的问题定义，**Then** 我能明确知道它是更深的结构层，不是 recipe/style 第一阶段重做
2. **Given** 我检查 `147` 的已锁定决策，**When** 我评估 scope，**Then** 我能确认它保持 provider-neutral

### 边界情况

- 简单 recipe 页面与复杂多区块企业页面需要共用同一 schema 演进路径
- provider 当前只支持第一阶段 solution snapshot，但 schema 不能因此绑定到某一 provider pack
- theme/quality/consistency 尚未 formalize 为 runtime 时，schema 仍应先独立冻结
- schema versioning 需要允许后续扩展，而不是一次性把后续轨道的全部语义塞进本工单

## 功能需求

### Schema Layer Contract

| ID | 需求 |
|----|------|
| FR-147-001 | `147` 必须把 `page schema` 与 `ui schema` 作为独立但关联的两个结构层冻结下来 |
| FR-147-002 | `147` 必须定义 provider-neutral 的 `render slot`、`section anchor`、结构块与页面层级 truth |
| FR-147-003 | `147` 必须冻结 `schema versioning` 的存在与演进边界，允许后续 child 在不重写上游 truth 的前提下扩展 |
| FR-147-004 | `147` 必须明确它承接的是更深 page/UI structure，而不是重写 `068` 的 recipe truth 或 `073` 的 provider/style 第一阶段 truth |

### Upstream / Downstream Boundary

| ID | 需求 |
|----|------|
| FR-147-005 | `147` 必须明确上游依赖至少包括 `011/015/068/073/145` 的结构语义输入 |
| FR-147-006 | `147` 必须明确下游 `multi-theme/token governance`、`quality platform`、`cross-provider consistency` 应消费其 schema anchor |
| FR-147-007 | `147` 当前不得开放新的 provider、theme editor、React exposure 或 quality execution |
| FR-147-008 | `147` 必须保持 provider-neutral，不得先绑死在 public/enterprise 单一 provider 上 |

### Rollout And Verification Honesty

| ID | 需求 |
|----|------|
| FR-147-009 | `147` 必须把 page schema / ui schema runtime baseline 落到 `src/` / `tests/`，至少覆盖 schema models、baseline builders 与 machine-verifiable artifact materialization |
| FR-147-010 | `147` 必须实现 validator / versioning / anchor contract，能对 recipe、component、state、anchor、slot 引用给出结构化阻断信息 |
| FR-147-011 | `147` 必须提供 provider/kernel consumption handoff surface，使后续 Track B/C/D 能消费同一套 schema anchor |
| FR-147-012 | `147` 的 close 语义必须诚实表达为“page/ui schema runtime baseline 已落地”，但不得伪造 multi-theme、quality、cross-provider 或 provider expansion 已完成 |

## 关键实体

- **Page Schema**：描述页面结构意图、区块层级、页面组成与语义边界的 provider-neutral 结构层
- **UI Schema**：描述可渲染组件结构、slot 约束、容器/控件组织的渲染结构层
- **Render Slot**：provider 或 solution layer 需要消费的稳定布局挂点
- **Section Anchor**：用于跨 provider / theme / quality 对齐页面结构的稳定锚点
- **Schema Versioning Contract**：保证 schema 可演进但不破坏上游/下游引用关系的版本边界

## 成功标准

- **SC-147-001**：`147` 独立成为 `145 Track A` 的 canonical child baseline，不再依赖会话记忆说明其存在
- **SC-147-002**：`147` 明确区分 page schema、ui schema、render slot、section anchor 的结构边界
- **SC-147-003**：`147` 明确指出与 `068/073` 的关系，不再混淆 recipe truth、provider/style truth 与 schema truth
- **SC-147-004**：`147` 落实 schema model、artifact、validator 与 provider/kernel handoff，并为 Track B/C/D 提供 schema anchor
- **SC-147-005**：`147` 的收口语义诚实停留在 page/ui schema runtime baseline，不伪造 Track B/C/D/E 已完成

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/068-frontend-p1-page-recipe-expansion-baseline/spec.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/145-frontend-p2-p3-deferred-capability-expansion-planning-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
