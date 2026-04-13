# 功能规格：Frontend P1 Experience Stability Planning Baseline

**功能编号**：`066-frontend-p1-experience-stability-planning-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（formal baseline）  
**输入**：用户确认的 P1 进入策略；[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的 P1 母级 planning baseline，用于把“在 MVP 已落稳的前提下进入第二阶段体验稳定层”冻结成单一 formal truth。它不直接进入 `src/` / `tests/` 实现，不重写 `009/015/017/018/065` 已冻结真值，不创建第二套 Contract / Kernel / Gate，也不提前把 P2 的 `modern provider / multi-theme / multi-style` 路线偷渡进 P1。

## 问题定义

截至当前主线，frontend MVP 已经完成了最小治理闭环所需的 formal truth 与实现承接：

- `009` 冻结了 `Contract / UI Kernel / enterprise-vue2 provider / 前端生成约束 / Gate-Recheck-Auto-fix` 的母级边界
- `015`、`017`、`018` 分别冻结了 UI Kernel 标准本体、生成治理基线与 Compatibility 口径下的 gate 基线
- `065` 进一步补齐了 sample source self-check 的自包含路径，但没有改写 production truth model

因此，当前真正缺少的不是再补一条 MVP 子实现，而是一份正式的 P1 planning baseline，回答下面几个问题：

- P1 只承接哪些“体验稳定层”能力，哪些内容必须继续留在 P2
- 现有 MVP truths 之上，应拆出哪些 child tracks，彼此依赖顺序如何
- 哪些 child tracks 可以并行，哪些必须串行
- root-level rollout plan、branch 命名与 program sync 应在什么时点发生，避免把 planning baseline 误当实现工单

如果不先把这些边界冻结，后续进入 P1 时会快速滑向三种典型问题：

- 直接散开写多个 child work item，导致 kernel、recipe、diagnostics、recheck、visual/a11y 各自扩张，排序漂移
- 把 `modern provider`、多 theme pack、多风格 token 映射等 P2 内容误带进 P1
- 在没有母级 formal truth 的情况下，过早把 root `program-manifest.yaml` 和 rollout plan 改成不稳定状态

因此，`066` 的职责是先冻结 P1 的规划真值，而不是马上承载实现。

## 范围

- **覆盖**：
  - 将 P1 正式定义为“在 MVP 真值不变前提下，从正确性止血走向体验稳定”的第二阶段
  - 冻结 P1 的明确目标、非目标与与 P2 的边界
  - 冻结 P1 的推荐 child tracks、依赖 DAG、有限并行窗口与 branch rollout 规则
  - 冻结后续 child work item 的命名口径、owner boundary 与 root truth sync 时机
  - 以 docs-only 方式为下一轮 design/decompose 提供单一母级 planning truth
- **不覆盖**：
  - 直接进入 `src/` / `tests/` 级实现
  - 直接 scaffold `067+` 的下游 child work item
  - 在本批把 `066` 写入根级 `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`
  - 改写 `009/015/017/018/065` 的既有 formal truth
  - 引入 `modern provider`、多 theme pack、多风格 token 映射或完整 visual / a11y 平台
  - 建立第二套 Contract、UI Kernel、Compatibility 或 Gate 体系

## 已锁定决策

- `066` 是 P1 的母级 planning baseline，而不是实现工单
- P1 只承接体验稳定层，不改写 MVP 的单一真值顺序
- P1 不包含 `modern provider`、多 theme pack、多风格 token 映射、完整 visual regression 平台或完整 a11y 平台
- `066` 只冻结 child tracks、依赖关系、排序与 rollout 规则；具体 `src/` / `tests/` 改动必须由后续 child work item 承接
- 在 child work item 尚未 formalize 前，`066` 不进入 root `program-manifest.yaml`，也不作为 close-ready program item 宣称已实现
- 推荐的 P1 child tracks 必须共用 `009` 已确立的 `Contract -> Kernel -> Provider/Code -> Gate` truth order，不得另起第二套体系
- root-level rollout plan 只能在 child baseline 已 formalize 且需要 program-level sync 时再补；`066` 当前只输出 planning truth

## 用户故事与验收

### US-066-1 — Framework Maintainer 需要单一 P1 母级 planning truth

作为**框架维护者**，我希望在进入 P1 前先有一份正式的母级 planning baseline，用于冻结阶段边界、child track 与排序规则，以便后续拆解不再依赖对话记忆或 design 总览临时推断。

**验收**：

1. Given 我审阅 `066` formal docs，When 我确认 P1 目标，Then 可以明确读到 P1 只承接体验稳定层，而不是 P2 的 modern provider / multi-style 路线
2. Given 我准备继续拆 child work item，When 我使用 `066`，Then 可以直接得到推荐 child tracks、依赖 DAG 与 rollout 规则

### US-066-2 — Reviewer 需要确认 P1 不污染 MVP 与 P2 边界

作为**reviewer**，我希望 `066` 明确声明“不改写 MVP truth、不偷渡 P2 能力”，以便后续任何 P1 子项都能被快速判定是否越界。

**验收**：

1. Given 我审阅 `066` formal docs，When 我检查 non-goals，Then 可以明确读到不新增第二套 Contract / Kernel / Gate，也不引入 modern provider
2. Given 我查看 child track DAG，When 我确认依赖顺序，Then 不会看到绕开 `015/017/018/065` 或回写 `009` 的设计

### US-066-3 — Operator 需要 docs-only planning freeze，而不是提前进入实现

作为**operator**，我希望 `066` 当前只冻结 planning truth、任务批次与 handoff 边界，而不是顺手创建 root-level program close 输入或直接写实现，以便后续推进仍符合框架 formalize discipline。

**验收**：

1. Given `066` 当前处于 formal baseline 阶段，When 我查看 `tasks.md` 与 execution log，Then 可以明确看到本批只允许 docs-only freeze
2. Given 我运行只读门禁，When 我确认当前 work item 状态，Then 不会误把 `066` 当成已实现或已 close-ready 的 program item

## 功能需求

### P1 Scope And Non-Goals

| ID | 需求 |
|----|------|
| FR-066-001 | `066` 必须作为 `009` 下游的独立 P1 母级 planning baseline 被正式定义，而不是把 P1 规划内容继续散落在 design 总览或对话上下文里 |
| FR-066-002 | `066` 必须明确 P1 的目标是“在 MVP 真值不变前提下，从正确性止血走向体验稳定” |
| FR-066-003 | `066` 必须明确 P1 只承接更完整的 `Ui*`、page recipe、governance diagnostics、recheck 协同与基础 visual / a11y 能力 |
| FR-066-004 | `066` 必须明确 P1 不覆盖 `modern provider`、多 theme pack、多风格 token 映射、完整 visual regression 平台、完整 a11y 平台或完整 page schema / UI schema |
| FR-066-005 | `066` 必须明确 P1 不得创建第二套 Contract、UI Kernel、Compatibility 或 Gate 体系，也不得以 prompt truth 替代 Contract truth |
| FR-066-006 | `066` 必须明确任何 P1 实现仍然必须遵守 `009` 已冻结的 `Contract -> Kernel -> Provider/Code -> Gate` 单一真值顺序 |

### Child Track Topology

| ID | 需求 |
|----|------|
| FR-066-007 | `066` 必须冻结推荐的 P1 child track 集合，至少包括 `Kernel 扩展`、`Recipe 扩展`、`Gate / Diagnostics / Drift`、`Recheck / Remediation Feedback`、`Visual / A11y Foundation` 五条主线 |
| FR-066-008 | `066` 必须为每条 child track 给出建议 slug 或等价命名口径，以便后续 scaffold 保持一致 |
| FR-066-009 | `066` 必须明确 `Recipe 扩展` 依赖 `Kernel 扩展`，不得绕开 UI Kernel 标准本体直接扩 recipe |
| FR-066-010 | `066` 必须明确 `Gate / Diagnostics / Drift` 依赖 expanded kernel / recipe truth 以及 `017/018/065` 的既有基线 |
| FR-066-011 | `066` 必须明确 `Recheck / Remediation Feedback` 依赖诊断与 drift truth，不能在 diagnostics 未冻结时先行扩张 |
| FR-066-012 | `066` 必须明确 `Visual / A11y Foundation` 依赖 expanded kernel / recipe 与 diagnostics truth，但仍保持在 P1 的“基础能力”范围，不得直接膨胀为完整平台 |

### Rollout Policy And Program Sync

| ID | 需求 |
|----|------|
| FR-066-013 | `066` 必须明确当前批次只做 docs-only formal baseline freeze，不直接 scaffold downstream child work items |
| FR-066-014 | `066` 必须明确后续 child work items 继续遵守“一工单一分支”的 branch rollout 纪律 |
| FR-066-015 | `066` 必须明确有限并行窗口只允许出现在 diagnostics truth 冻结之后；在此之前以串行冻结 kernel / recipe truth 为主 |
| FR-066-016 | `066` 必须明确 root `program-manifest.yaml` 与 `frontend-program-branch-rollout-plan.md` 的同步时机应晚于 child baseline formalize，不得在母级 planning freeze 阶段抢跑 |
| FR-066-017 | `066` 必须明确当前 work item 不得生成 `development-summary.md`，也不得宣称 close-ready 或已实现 |
| FR-066-018 | `066` 必须明确 `.ai-sdlc/project/config/project-state.yaml` 只推进 `next_work_item_seq`，不伪造 program close 状态或 mainline sync |

### Handoff And Verification

| ID | 需求 |
|----|------|
| FR-066-019 | `066` 必须输出可直接承接下一轮 design/decompose 的 `spec.md / plan.md / tasks.md / task-execution-log.md` 单一 truth |
| FR-066-020 | `066` 必须在 `plan.md` 中给出推荐 child track 文件面、DAG、阶段边界与 owner boundary |
| FR-066-021 | `066` 必须在 `tasks.md` 中把 docs-only freeze、后续 child formalization 与 root sync 前提清晰分离 |
| FR-066-022 | `066` 当前批次的验证只允许使用 docs-only / read-only 门禁，例如 `uv run ai-sdlc verify constraints` 与 `git diff --check` |
| FR-066-023 | `066` 必须让后续 child work item 可以直接读取 P1 scope、non-goals、排序与 branch rollout 规则，而无需回到 design 总览重做解释 |

## 关键实体

- **P1 Experience Stability Envelope**：P1 阶段允许承接的体验稳定层能力边界，排除 P2 的 modern provider / multi-style 路线
- **P1 Child Track Set**：由 `Kernel 扩展`、`Recipe 扩展`、`Gate / Diagnostics / Drift`、`Recheck / Remediation Feedback`、`Visual / A11y Foundation` 组成的正式推荐主线集合
- **Child Track DAG**：定义各 child tracks 的串并行关系、依赖顺序与可并行窗口的 planning truth
- **Branch Rollout Policy**：后续 child 工单的 branch 命名、并行边界、program sync 时机与 root truth 对齐规则
- **Planning-Only Baseline State**：`066` 当前处于 docs-only formal freeze 的状态，不构成 close-ready implementation artifact

## 推荐的下游 child tracks

本规格中出现的下游 child 编号仅作为 planning 占位建议，不构成编号预留；真实 child work item 编号以后续 scaffold 时的 `project-state` 为准。

| Track | 建议 slug | 主要承接内容 | 上游依赖 |
|-------|-----------|--------------|----------|
| A | `frontend-p1-ui-kernel-semantic-expansion-baseline` | 扩展 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 等语义组件与页面状态语义 | `009`、`015` |
| B | `frontend-p1-page-recipe-expansion-baseline` | 扩展 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 等 page recipe 标准本体与声明约束 | Track A、`015` |
| C | `frontend-p1-governance-diagnostics-drift-baseline` | 扩展 whitelist / token / 状态覆盖、drift 诊断与更丰富的治理反馈面 | Track A、Track B、`017`、`018`、`065` |
| D | `frontend-p1-recheck-remediation-feedback-baseline` | 扩展 frontend recheck agent、bounded remediation feedback 与作者体验闭环 | Track C、`017`、`018` |
| E | `frontend-p1-visual-a11y-foundation-baseline` | 建立 P1 级 visual / a11y 基础检查能力与最小反馈面 | Track A、Track B、Track C |

## 成功标准

- **SC-066-001**：`066` formal docs 能独立表达 P1 的目标、非目标、child track 集合与排序规则，而无需回到 design 总览或对话推断
- **SC-066-002**：P1 与 P2 的边界保持单一真值，`modern provider / multi-theme / multi-style` 不再被误表述为 P1 内容
- **SC-066-003**：后续 child work item 可直接根据 `066` 的 DAG 与 branch rollout 规则继续 formalize，而不会出现 kernel / recipe / diagnostics 排序漂移
- **SC-066-004**：`066` 当前状态被清楚表达为 docs-only planning baseline，不会被误读成已实现或已 close-ready 的 program item
- **SC-066-005**：`066` 对 root truth sync 的时机表述保持诚实，不提前修改 `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`

---
related_doc:
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
