# 功能规格：Frontend P2 P3 Deferred Capability Expansion Planning Baseline

**功能编号**：`145-frontend-p2-p3-deferred-capability-expansion-planning-baseline`
**创建日期**：2026-04-16
**状态**：已冻结（formal baseline）
**输入**：顶层前端治理设计中已明确、但尚未 materialize 为 canonical child work item 的后续能力；[`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)、[`../073-frontend-p2-provider-style-solution-baseline/spec.md`](../073-frontend-p2-provider-style-solution-baseline/spec.md)、[`../071-frontend-p1-visual-a11y-foundation-baseline/spec.md`](../071-frontend-p1-visual-a11y-foundation-baseline/spec.md)、[`../095-frontend-mainline-product-delivery-baseline/spec.md`](../095-frontend-mainline-product-delivery-baseline/spec.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的 P2/P3 母级 planning baseline，用于把“已经在顶层设计中被定义、但仍停留在 deferred / non-goal / later-phase 文字口径里的前端后续能力”一次性纳入 formal truth。它不重做 `073` 已落地的 provider/style 第一阶段，不重写 `071/137/095/143` 已冻结或已实现的基础 quality / browser gate truth，也不在本批直接进入 `src/` / `tests/` 级实现；它只负责把剩余能力集合、边界、依赖顺序与下一条实现入口冻结成单一 canonical planning truth。

## 问题定义

截至当前分支，前端主线已经完成了三类关键落地：

- `073` 及其后续 runtime 承接，已经把 P2 第一阶段的 `provider/style pack/solution_snapshot/preflight/CLI confirm/verify consistency` 物化进代码主链；
- `071/137` 已把 P1 基础 visual / a11y foundation 真值与 runtime 诚实收束；
- `095/102/103/104/105/125/143/144` 已把 frontend mainline 的 managed delivery、browser gate、real probe 与 workspace integration 主链做成 release-ready truth。

但顶层设计里仍然存在一批明确写过、却没有形成 canonical downstream work item 的后续能力，典型包括：

- 更深的 `page schema / UI schema`
- 更完整的 multi-theme / token 检查与自定义 style token 治理
- 完整的 visual / a11y / interaction quality platform
- 更成熟的跨 Provider 一致性检查
- 额外的 modern provider 扩展、公开选择面扩张，以及更后续的 React 暴露边界

当前这些内容分散存在于顶层设计、`073` 第一阶段非目标、`071` 的 non-goals 与 `095` 的 bounded browser gate 边界中。结果是：

- 全局真值现在已经做到 source-complete，但还不能直接回答“设计里剩下哪些前端主线需求尚未 materialize”
- 已交付的一期能力与未来阶段能力容易混在一起，被误判为“未实现”或“已无需承接”
- 后续如果直接开始写代码，仍然会重复发生“漏掉设计里提到的后续项、或把多个子系统混在一个实现工单里”的问题

因此，`145` 的职责不是补某一条 runtime，而是先把剩余 deferred capability 一次性 formalize，为下一轮连续实现建立诚实、稳定的入口。

## 范围

- **覆盖**：
  - 一次性冻结顶层设计中剩余的前端 P2/P3 capability 集合
  - 明确区分“已 materialize 的第一阶段能力”与“仍待 downstream child 承接的能力”
  - 冻结剩余 capability 的 child track 集合、推荐 slug、依赖 DAG 与 rollout 顺序
  - 明确每条 child track 的 owner boundary 与禁止跨层改写边界
  - 指定下一条优先实现 carrier：`frontend-p2-page-ui-schema-baseline`
  - 使 `145` 可以作为 program/global truth 对“后续前端优化主线”进行诚实表达的 canonical planning input
- **不覆盖**：
  - 直接进入 `src/` / `tests/` 的 runtime / model / CLI 实现
  - 重新设计 `073` 的第一阶段 provider/style pack truth
  - 重新定义 `071/137` 的 visual / a11y foundation 或 `095/143` 的 bounded browser gate
  - 在本工单中开放 React UI 选择面、第二公开 Vue3 provider、开放式 style editor 或真实多浏览器矩阵执行
  - 把多个 downstream child 合并成单一实现工单

## 已锁定决策

- `145` 是“剩余 deferred capability 的母级 planning truth”，不是实现工单。
- 已经 materialize 的 P2 第一阶段与 frontend mainline 主链必须与后续阶段能力分开表达，不能再混成“全都未做”。
- 设计中剩余的后续能力，至少要拆成 `page/ui schema`、`multi-theme/token governance`、`quality platform`、`cross-provider consistency`、`modern provider expansion` 五条 child tracks。
- 下一条优先承接的 child 必须是 `frontend-p2-page-ui-schema-baseline`，因为当前仓库中还没有与之对应的 `specs/<WI>/` 或 `src/tests` 载体。
- 后续 child 仍必须遵守 `Contract -> Kernel -> Provider/Style -> Gate -> Program` 的单一真值顺序。
- `145` 只允许引用顶层设计与既有 formal docs，不能在 `docs/superpowers/*` 再创建第二套 canonical docs。

## 用户故事与验收

### US-145-1 — Framework Maintainer 需要剩余前端 deferred capability 的单一真值

作为**框架维护者**，我希望顶层设计里还没 materialize 的前端后续能力能被一次性拉平到一个正式 planning baseline 中，这样我可以明确知道还剩哪些主线没有进入 canonical child work item。

**优先级说明**：P0。用户已经明确指出“全局真值虽然 source-complete，但 capability-level 仍不完整”，如果不先 formalize，后续实现仍会继续漏项。

**独立测试**：阅读 `145/spec.md` 时，可以直接列出剩余 child tracks 与下一条实现 carrier，而不需要回到顶层设计全文重新人工归纳。

**验收场景**：

1. **Given** 我审阅 `145`，**When** 我检查剩余 capability 集合，**Then** 我能直接看到 `page/ui schema`、`multi-theme/token governance`、`quality platform`、`cross-provider consistency`、`modern provider expansion`
2. **Given** 我准备继续实现前端后续主线，**When** 我使用 `145`，**Then** 我不需要再回到对话上下文重新猜测哪些 later-phase 能力还没承接

### US-145-2 — Reviewer 需要区分已交付的第一阶段能力与真正未 materialize 的后续主线

作为**reviewer**，我希望 `145` 明确说明 `073/071/137/095/143/144` 已经承接了什么、后续 child 又还剩什么，以便避免继续把“已完成的一期能力”误报成未实现缺口。

**优先级说明**：P0。当前最大的风险不是“少写一条文档”，而是继续把已完成与未完成混在一起，导致实现顺序失真。

**独立测试**：`145` 中能清楚读到 delivered/deferred 边界，并且不会把 `073` 的第一阶段或 `071/137` 的基础 quality foundation 再表述为未落地。

**验收场景**：

1. **Given** 我检查 `145` 的边界说明，**When** 我对照 `073/071/095/143`，**Then** 我能明确知道哪些能力已经 materialize，哪些仍待 child 承接
2. **Given** 我执行后续 truth refresh，**When** 我查看 `145`，**Then** 我不会再把 bounded browser gate 或 first-phase provider/style truth 当成“当前缺失”

### US-145-3 — Operator 需要下一条实现 carrier 与推荐顺序

作为**operator**，我希望 `145` 不只是列出“还有很多后续项”，而是明确给出 child DAG、推荐顺序和下一条要开的工单，这样我可以在框架约束下连续推进而不中断。

**优先级说明**：P0。用户明确要求“按照这个顺序，逐步推进，框架约束下不中断”。

**独立测试**：`145/plan.md` 和 `145/tasks.md` 可以直接告诉执行者先开哪条 child、哪些可并行、哪些必须等待上游真值冻结。

**验收场景**：

1. **Given** 我审阅 `145/plan.md`，**When** 我检查实施顺序建议，**Then** 第一条 child 是 `frontend-p2-page-ui-schema-baseline`
2. **Given** 我检查 child track 依赖，**When** 我决定下一轮 formalize/实现，**Then** 我能看到哪些 track 可以在后续有限并行、哪些不能抢跑

## 功能需求

### Deferred Capability Truth Coverage

| ID | 需求 |
|----|------|
| FR-145-001 | `145` 必须作为 `009` 下游的独立 P2/P3 母级 planning baseline 被正式定义，而不是把剩余前端主线继续留在 design 的 later-phase 文字里 |
| FR-145-002 | `145` 必须一次性收敛剩余 capability 集合，至少包括 `page/ui schema`、`multi-theme/token governance`、完整 `visual/a11y/interaction quality platform`、`cross-provider consistency`、`modern provider expansion` |
| FR-145-003 | `145` 必须明确区分已 materialize 能力与仍 deferred 能力，不得把 `073` 第一阶段、`071/137` foundation、`095/143/144` mainline 主链重新表述为未落地 |
| FR-145-004 | `145` 必须明确当前工单只冻结 planning truth，不进入 `src/` / `tests/` 实现 |
| FR-145-005 | `145` 必须指定下一条优先 child 为 `frontend-p2-page-ui-schema-baseline` |
| FR-145-006 | `145` 必须明确后续 child 继续遵守 `Contract -> Kernel -> Provider/Style -> Gate -> Program` 的单一真值顺序 |

### Child Track Topology

| ID | 需求 |
|----|------|
| FR-145-007 | `145` 必须冻结至少五条 downstream child tracks，并给出建议 slug、目标与上游依赖 |
| FR-145-008 | `145` 必须明确 `frontend-p2-page-ui-schema-baseline` 承接更深的 page schema / UI schema，而不是重写当前 Contract declaration |
| FR-145-009 | `145` 必须明确 `frontend-p2-multi-theme-token-governance-baseline` 承接 multi-theme、token mapping、自定义 theme token 与 style editor boundary |
| FR-145-010 | `145` 必须明确 `frontend-p2-quality-platform-baseline` 承接完整 visual regression、完整 a11y platform、interaction quality gate 与多浏览器/多设备矩阵 |
| FR-145-011 | `145` 必须明确 `frontend-p2-cross-provider-consistency-baseline` 承接跨 Provider 一致性检查，并依赖共享 schema / theme / quality truth |
| FR-145-012 | `145` 必须明确 `frontend-p3-modern-provider-expansion-baseline` 承接额外 modern provider、公开选择面扩张与更后续的 React 暴露边界 |

### Rollout Policy And Boundary Honesty

| ID | 需求 |
|----|------|
| FR-145-013 | `145` 必须明确本工单中不得开放 React UI 选择面、第二公开 Provider、开放式 style editor 或真实 quality platform 执行 |
| FR-145-014 | `145` 必须明确外部 design docs 仅作为 reference-only 输入，不得成为第二套 canonical truth |
| FR-145-015 | `145` 必须明确 downstream child 继续遵守“一工单一分支”的 branch rollout 纪律 |
| FR-145-016 | `145` 必须明确 root truth / program sync 应晚于 `145` docs-only freeze，并在 child formalize 后持续推进，而不是继续停留在设计引用层 |
| FR-145-017 | `145` 必须明确 quality platform、cross-provider consistency 与 provider expansion 之间的先后顺序，避免“先开 provider 再补 certification harness”的倒挂 |

### Handoff And Verification

| ID | 需求 |
|----|------|
| FR-145-018 | `145` 必须在 `plan.md` 中给出 child DAG、owner boundary、推荐顺序与有限并行窗口 |
| FR-145-019 | `145` 必须在 `tasks.md` 中把 docs-only formal freeze、后续 child formalize 与 truth sync readiness 清晰分离 |
| FR-145-020 | `145` 必须给出 docs-only verification profile，至少包含 `uv run ai-sdlc verify constraints`、`python -m ai_sdlc workitem close-check --wi ...` 与 `git diff --check` |
| FR-145-021 | `145` 必须允许后续执行者直接根据本工单开启 `frontend-p2-page-ui-schema-baseline`，而无需重新回到顶层设计做 capability census |
| FR-145-022 | `145` 必须在 `development-summary.md` 中诚实声明“当前收口的是 planning truth，不是 runtime 完成” |

## 关键实体

- **Deferred Capability Set**：顶层设计中已定义、但当前尚未 materialize 为 canonical child work item 的后续前端能力集合
- **Delivered/Deferred Boundary**：用于区分 `073/071/137/095/143/144` 已承接内容与后续 child 待承接内容的边界真值
- **Capability Track DAG**：定义 `page/ui schema -> multi-theme/token -> quality platform -> cross-provider consistency -> provider expansion` 的推荐顺序与依赖窗口
- **Page/UI Schema Track**：承接 provider-neutral page schema、UI schema、schema versioning、结构锚点与更复杂外部系统页面的 formal baseline
- **Theme Token Governance Track**：承接 multi-theme pack、自定义 token map、style editor boundary 与 style truth 的后续治理扩展
- **Quality Platform Track**：承接完整 visual regression、完整 a11y、interaction quality、多浏览器/多设备矩阵与 richer evidence platform
- **Cross-Provider Consistency Track**：承接基于同一 schema/theme/quality truth 的跨 Provider 一致性检查与差异诊断
- **Modern Provider Expansion Track**：承接新 modern provider、公开 provider 选择面扩张以及更后续的 React exposure boundary

## 推荐的 downstream child tracks

本规格中的 child slug 只作为 planning truth，不构成编号预留；真实编号以下一轮 scaffold 时的 `project-state` 为准。

| Track | 建议 slug | 主要承接内容 | 上游依赖 |
|-------|-----------|--------------|----------|
| A | `frontend-p2-page-ui-schema-baseline` | 更深的 page schema / UI schema、schema versioning、结构锚点、provider-neutral render slot truth | `011`、`015`、`068`、`073` |
| B | `frontend-p2-multi-theme-token-governance-baseline` | multi-theme pack、自定义 theme token、token mapping、style editor boundary | `073`、Track A（共享 schema anchor 时） |
| C | `frontend-p2-quality-platform-baseline` | visual regression、完整 a11y、interaction quality、多浏览器/多设备矩阵 | `071/137`、`095/143`、Track A、Track B |
| D | `frontend-p2-cross-provider-consistency-baseline` | enterprise/public provider 之间的 shared verdict、diff surface、consistency certification | `073`、Track B、Track C |
| E | `frontend-p3-modern-provider-expansion-baseline` | 额外 public modern provider、provider choice surface 扩张、React exposure boundary | `073`、Track D |

## 成功标准

- **SC-145-001**：`145` 能独立表达“设计里剩余哪些前端 capability 尚未 materialize”，不再依赖对话记忆或人工重读整个顶层设计
- **SC-145-002**：`145` 明确隔离 `073/071/137/095/143/144` 已承接内容，避免再次误报已完成能力
- **SC-145-003**：`145` 给出五条 downstream child tracks、建议 slug、依赖 DAG 与推荐顺序
- **SC-145-004**：`145` 明确下一条优先实现 carrier 是 `frontend-p2-page-ui-schema-baseline`
- **SC-145-005**：`145` 的收口口径诚实停留在 planning truth，不伪造 runtime 已完成

---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/073-frontend-p2-provider-style-solution-baseline/spec.md"
  - "specs/071-frontend-p1-visual-a11y-foundation-baseline/spec.md"
  - "specs/095-frontend-mainline-product-delivery-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
