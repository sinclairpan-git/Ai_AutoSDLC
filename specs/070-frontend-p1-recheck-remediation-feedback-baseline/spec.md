# 功能规格：Frontend P1 Recheck Remediation Feedback Baseline

**功能编号**：`070-frontend-p1-recheck-remediation-feedback-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `066-frontend-p1-experience-stability-planning-baseline` 冻结后的第四条下游 child work item，用于把 P1 的 frontend recheck / bounded remediation feedback / author experience loop 正式冻结成单一 formal truth。它只处理“在 `069` diagnostics / drift truth 冻结之后，哪些 frontend blocker 需要进入 bounded remediation runbook、何时触发 recheck、哪些 writeback / handoff artifact 可以被 program surface 与作者工作流消费、以及这些反馈如何继续服从 `017/018/065/069` 已冻结的单一 truth model”这条体验闭环主线；它不是 diagnostics child，不是 visual / a11y child，也不是 provider/runtime 实现工单。

## 问题定义

`017` 已冻结并实现 generation control plane，`018` 已冻结 gate / compatibility / report / recheck-fix boundary，`065` 已冻结 sample source self-check 的显式输入边界，`067/068` 已冻结 P1 的 expanded kernel / page recipe truth，`069` 又进一步冻结了 diagnostics coverage matrix、gap / empty / drift classification 与 compatibility feedback boundary。

但当前 P1 仍缺少一份正式的 recheck / remediation feedback baseline，回答以下问题：

- diagnostics / drift 输出在 P1 阶段何时升级为作者可执行的 frontend remediation 输入
- readiness 已达 `READY` 时，frontend recheck handoff 应如何表达，才能保持 `execute -> verify -> close/report` 闭环诚实
- remediation runbook 允许暴露哪些 bounded commands、writeback artifact 与 provider handoff 信息，哪些行为仍必须留给外部前端项目或更后续实现工单
- `frontend_contract_observations`、governance artifacts、diagnostics drift 等 fix inputs 如何映射为作者可读的 suggested actions，而不膨胀成“自动整页重写”
- 哪些能力必须继续留给 `071` visual / a11y child、完整 auto-fix engine 或 provider/runtime 工单，而不能在 `070` 里抢跑

如果不先冻结 `070`，后续 P1 很容易滑向三类偏差：

- 把 diagnostics 直接等同于 remediation，导致 `069` 的分类 truth 与作者反馈面耦死在一起
- 把 remediation runbook 误做成开放式命令执行器，破坏 bounded / reviewable / explicit 的框架约束
- 把 recheck、writeback、provider handoff 与 visual/a11y 或 runtime 实现混在一起，造成 P1 child track 边界漂移

因此，`070` 的职责是先冻结 P1 frontend recheck / remediation feedback truth，而不是立刻进入完整 auto-fix runtime 或业务前端代码修改实现。

## 范围

- **覆盖**：
  - 将 P1 frontend recheck / remediation feedback 正式定义为 `066` 下游的独立 child work item
  - 锁定 `069` diagnostics / drift truth 如何映射为 `frontend_recheck_handoff` 与 `frontend_remediation_input`
  - 锁定 bounded remediation runbook、writeback artifact、provider handoff payload 与作者工作流的最小反馈面
  - 锁定 recheck 触发时机、readiness state 与 remediation/recheck 的 truth-order
  - 锁定 remediation command honesty、source-root honesty 与 reviewable writeback 边界
  - 为后续 `program_service`、`program_cmd`、`verify constraints` 关联反馈面与相关测试切片提供 canonical baseline
- **不覆盖**：
  - 改写 `069` 已冻结的 diagnostics coverage matrix、classification 或 compatibility feedback boundary
  - 扩张 `071` 的 visual / a11y foundation、截图比对或可访问性平台
  - 引入完整 auto-fix engine、任意脚本执行器、整页重写或 provider/runtime 代码生成
  - 将 sample source self-check 变成默认 remediation 路径、隐式 source-root 发现或隐式 observation materialization
  - 改写 `017` generation truth、`018` gate matrix / report family / priority order 或 root program truth
  - 引入 P2 的 modern provider、多主题、多风格或完整 authoring platform

## 已锁定决策

- `070` 是 P1 的 recheck / remediation feedback child work item，不是 diagnostics / visual-a11y / provider 工单
- `070` 必须消费 `069 + 018 + 017 + 065 + 067 + 068` 的组合 truth，而不是重新发明 diagnostics、gate 或 provider 语义
- readiness 未达 `READY` 时，应暴露 `frontend_remediation_input`；readiness 达 `READY` 后，应暴露 `frontend_recheck_handoff`
- bounded remediation feedback 允许输出 fix inputs、suggested actions、recommended commands、writeback artifact 与 provider handoff，但不得升级为开放式命令执行或整页重写
- remediation command 仍必须保持显式、可审计、受限；涉及 observation 扫描时必须要求显式 `<frontend-source-root>`
- recheck 的目标是“在 execute 后重新验证当前 frontend truths 是否闭环”，不是在本工单中发明新的 gate matrix 或 visual/a11y 平台
- `070` 当前只做 docs-only formal freeze，不进入 `src/` / `tests/`，不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`

## 用户故事与验收

### US-070-1 — Operator 需要根据 readiness 状态得到诚实的 remediation 或 recheck 提示

作为**operator**，我希望当前 frontend readiness 若未闭环时得到 bounded remediation feedback，若已闭环则得到 recheck handoff，以便 program dry-run / integrate surface 可以继续沿着同一条 truth-order 前进，而不是混淆“先修复”与“再复查”。

**验收**：

1. Given 我查看 `070` formal docs，When 我检查 remediation / recheck 分流，Then 可以明确读到 `retry -> remediation input`、`ready -> recheck handoff`
2. Given 我继续实现或测试 program surface，When 我读取 `070`，Then 可以明确知道 remediation 和 recheck 不能在同一状态下同时冒充默认主路径

### US-070-2 — Author 需要收到 bounded、可执行、可审计的 frontend feedback

作为**author**，我希望 frontend diagnostics 被转换为 bounded remediation feedback，而不是泛化成自然语言建议或开放式命令执行器，以便我能按固定 fix input、建议动作和推荐命令完成修复并保留审计痕迹。

**验收**：

1. Given 我查看 `070` formal docs，When 我检查 remediation feedback 对象，Then 可以明确读到 fix inputs、suggested actions、recommended commands、source linkage、writeback artifact 的最小边界
2. Given 我查看 `070` formal docs，When 我检查 command honesty，Then 可以明确读到 observation 相关命令必须使用显式 `<frontend-source-root>`，不得回退到 `scan .`

### US-070-3 — Reviewer 需要确认 bounded remediation 不会膨胀成 auto-fix engine

作为**reviewer**，我希望 `070` 明确说明 remediation feedback 只是 bounded author loop，而不是完整 auto-fix runtime，以便 P1 child 不会越界侵入 provider/runtime 或整页重写。

**验收**：

1. Given 我查看 `070` formal docs，When 我检查 non-goals，Then 可以明确读到完整 auto-fix engine、任意脚本执行、整页重写和 provider/runtime 实现均不属于本工单
2. Given 我查看 `070` formal docs，When 我检查 handoff boundary，Then 可以明确读到 visual/a11y 仍由 `071` 承接，provider/runtime 仍留给更后续工单

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-070-001 | `070` 必须作为 `066` 下游的 recheck / remediation feedback child work item 被正式定义，用于冻结 P1 frontend author feedback truth |
| FR-070-002 | `070` 必须明确自身位于 `069` diagnostics / drift truth 之后、与 `071` visual / a11y child 并列而不互相吞并 |
| FR-070-003 | `070` 必须继续遵守 `Contract -> Kernel -> Provider/Code -> Gate -> Recheck/Remediation Feedback` 的单一 truth-order，并明确其反馈面只能消费 `069 + 018 + 017 + 065 + 067 + 068` |
| FR-070-004 | `070` 必须明确当前 work item 的非目标，包括 diagnostics baseline 重写、visual / a11y、完整 auto-fix runtime、provider 映射与 runtime 实现 |

### Frontend Recheck Handoff

| ID | 需求 |
|----|------|
| FR-070-005 | `070` 必须冻结 `frontend_recheck_handoff` 的最小边界，至少包括 `required`、`reason`、`recommended_commands` 与 `source_linkage` |
| FR-070-006 | `070` 必须明确 frontend readiness 仅在 `READY` 时进入 recheck handoff，且推荐命令继续指向 `uv run ai-sdlc verify constraints` 这类单一 verify surface |
| FR-070-007 | `070` 必须明确 recheck handoff 的目的，是在 execute 后重新验证 diagnostics / gate / attachment truths 是否仍闭环，而不是发明新的 gate matrix 或另起一套 report family |
| FR-070-008 | `070` 必须明确 recheck handoff 仍服从 `018` 已冻结的 report / priority order，并复用现有 source linkage，而不是覆盖上游诊断来源 |

### Bounded Remediation Feedback

| ID | 需求 |
|----|------|
| FR-070-009 | `070` 必须冻结 `frontend_remediation_input` 的最小边界，至少包括 `state`、`fix_inputs`、`blockers`、`suggested_actions`、`recommended_commands` 与 `source_linkage` |
| FR-070-010 | `070` 必须明确 remediation input 仅在 frontend readiness 未达 `READY` 时暴露，并继续消费 `069` 的 `gap / stable empty / drift` 分类，而不是重定义分类 |
| FR-070-011 | `070` 必须明确 remediation suggested actions 可将 fix inputs 翻译为作者动作，但不得脱离 fix inputs 生成开放式策略建议或另起第二套自然语言 truth |
| FR-070-012 | `070` 必须明确 observation 相关 remediation command 需要显式 `<frontend-source-root>`，不得默认假定当前仓库根或 sample fixture 路径 |
| FR-070-013 | `070` 必须明确 governance artifact remediation 可建议物化 gate policy / generation constraint artifacts，但不得在当前工单中放宽 whitelist / token / recipe / state truths |
| FR-070-014 | `070` 必须明确 remediation command 集必须保持 bounded、可审计、可白名单化，不得升级为任意脚本执行器或整页重写入口 |

### Runbook, Writeback, And Handoff Honesty

| ID | 需求 |
|----|------|
| FR-070-015 | `070` 必须冻结 bounded remediation runbook 的最小职责：汇总 per-spec remediation steps、执行已知命令、保留 command result，并在失败时诚实回报 remaining blockers |
| FR-070-016 | `070` 必须冻结 remediation writeback artifact 的最小角色：记录 runbook/execution 来源、step 级输入输出与 writeback 路径，供后续作者审计与 provider handoff 消费 |
| FR-070-017 | `070` 必须明确 provider handoff payload 只承接 remediation writeback 的只读摘要，不得在当前工单直接修改外部前端项目代码或 provider/runtime 仓库 |
| FR-070-018 | `070` 必须明确 remediation / recheck feedback 只是作者体验闭环；完整 auto-fix engine、业务代码修改与 close 阶段集成仍是下游实现议题 |
| FR-070-019 | `070` 必须明确 `071` 继续承接 visual / a11y foundation，当前工单不得混入截图、视觉回归或可访问性平台反馈 |
| FR-070-020 | `070` 当前只允许 docs-only formal freeze，不得进入 `src/` / `tests/`、root program sync 或 `development-summary.md` 生成 |
| FR-070-021 | `070` 中出现的下游 `071` 编号只用于当前 planning 口径；真实后续编号以后续 scaffold 时的 `project-state` 为准 |

## 关键实体

- **Frontend Recheck Handoff**：描述 readiness 已闭环后，程序层如何要求作者在 execute 后重新跑 frontend verify
- **Frontend Remediation Input**：描述 readiness 未闭环时，程序层如何把 fix inputs、建议动作与推荐命令暴露为 bounded remediation feedback
- **Bounded Remediation Command Set**：描述 remediation runbook 允许执行的受限命令集合及其审计边界
- **Frontend Remediation Writeback Artifact**：描述 remediation runbook / execution 的 canonical 写回摘要，用于审计与 handoff
- **Provider Handoff Payload**：描述由 remediation writeback 派生的只读 provider 交接载荷，而非直接代码写入
- **Author Feedback Honesty Boundary**：描述 remediation / recheck feedback 与 diagnostics / visual-a11y / runtime 实现之间的边界

## 成功标准

- **SC-070-001**：`070` formal docs 能独立表达 recheck handoff、bounded remediation feedback、runbook / writeback / handoff 的 scope、truth-order 与 non-goals
- **SC-070-002**：reviewer 能从 `070` 直接读出 `bounded remediation != auto-fix engine`，以及 `recheck handoff != second gate`
- **SC-070-003**：作者能从 `070` 直接读出 fix inputs、suggested actions、recommended commands 与 `<frontend-source-root>` honesty 的边界
- **SC-070-004**：`070` 不会回写或冲掉 `069` 的 diagnostics truth，也不会抢跑 `071` visual / a11y foundation
- **SC-070-005**：`070` 当前状态被清楚表达为 docs-only child baseline，不会被误读成已实现、已 close-ready 或已 root sync 的 program item

---
related_doc:
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
