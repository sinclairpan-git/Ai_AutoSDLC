# 功能规格：Frontend P1 Visual A11y Foundation Baseline

**功能编号**：`071-frontend-p1-visual-a11y-foundation-baseline`  
**创建日期**：2026-04-06  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md`](../069-frontend-p1-governance-diagnostics-drift-baseline/spec.md)、[`../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md`](../070-frontend-p1-recheck-remediation-feedback-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `066-frontend-p1-experience-stability-planning-baseline` 冻结后的第五条下游 child work item，用于把 P1 的 visual / a11y foundation 正式冻结成单一 formal truth。它只处理“P1 级基础 visual / a11y 检查应覆盖哪些最小质量面、这些检查如何继续消费 `067 + 068 + 069 + 018 + 065` 的组合 truth、以及它们与 sibling recheck/remediation feedback、provider/runtime、完整质量平台之间的边界”这条体验质量主线；它不是 diagnostics / drift 工单，不是 recheck / remediation 工单，也不是 provider/runtime 实现工单。

## 问题定义

`067` 已冻结 P1 的 expanded `Ui*` 与页面级状态语义，`068` 已冻结 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 的 page recipe 标准本体与 area constraint，`069` 又进一步冻结了 P1 diagnostics coverage matrix、gap / empty / drift classification 与同一套 gate matrix 的兼容执行口径相关反馈边界。

但当前仓库仍缺少一份正式的 P1 visual / a11y foundation 真值，回答以下问题：

- P1 的“基础 visual / a11y 检查”到底只到哪一层，哪些内容必须继续留在 P2 的完整质量平台
- visual / a11y foundation 应消费哪些上游 Kernel / Recipe / Diagnostics truths，而不是围绕 provider 私有 DOM、样式细节或自由截图脚本重新定义规则
- 最小 visual quality 面、最小 a11y 底线与证据输入边界应如何冻结，才能既支持后续实现，又不把当前工单膨胀成完整 visual regression / WCAG 平台
- 缺少实现证据、存在稳定空输入、以及真实 visual / a11y 问题之间如何保持诚实区分
- 哪些内容必须继续留给 sibling recheck/remediation feedback 与更后续 provider/runtime / quality platform 工单，而不能在 `071` 里抢跑

如果不先冻结 `071`，后续 P1 child 会快速滑向三种典型偏差：

- 把 visual / a11y 检查直接膨胀成完整截图平台、跨浏览器矩阵或完整无障碍平台，越过 P1 的“基础能力”边界
- 围绕 provider 私有 DOM、企业样式细节或临时截图脚本写规则，脱离 `067 + 068 + 069` 已冻结的统一语义真值
- 缺少实现证据时把问题误报成 visual / a11y drift，或反过来把真实质量缺陷误归入 diagnostics / remediation

因此，`071` 的职责是先冻结 P1 visual / a11y foundation truth，而不是立刻进入代码实现。

## 范围

- **覆盖**：
  - 将 P1 visual / a11y foundation 正式定义为 `066` 下游的独立 child work item
  - 锁定 P1 visual foundation 的最小覆盖面，包括状态可见性、关键区域可感知性与受控容器视觉连续性
  - 锁定 P1 a11y foundation 的最小覆盖面，包括错误/状态可感知性、基础语义/命名、键盘可达性与焦点连续性
  - 锁定 visual / a11y foundation 如何消费 `067 + 068 + 069 + 018 + 065` 的组合 truth
  - 锁定 visual / a11y 反馈继续服从 `018` 已冻结的同一套 gate matrix 与 report family，而不是新增第二套质量系统
  - 为后续 `frontend_gate_verification`、`frontend_contract_gate`、`verify_constraints`、visual / a11y evidence fixtures 与对应测试切片提供 canonical baseline
- **不覆盖**：
  - 改写 `067` 已冻结的 `Ui*` 语义组件协议、`068` 的 page recipe 标准本体、或 `069` 的 diagnostics coverage matrix / drift classification
  - 扩张 sibling recheck / remediation feedback、bounded remediation runbook、writeback artifact、provider handoff payload 或完整 auto-fix engine
  - 建设完整 visual regression 平台、跨浏览器/跨设备截图矩阵、完整 WCAG/a11y 平台、交互动效质量平台或多 theme / 多 provider 一致性平台
  - 定义 `Ui* -> provider/runtime` 的具体映射、样式实现、Vue 组件代码或企业视觉规范承接
  - 将 sample fixture、当前仓库根或任意隐式路径视为默认 visual / a11y evidence source
  - 引入 P2 的 `modern provider / multi-theme / multi-style` 或完整 visual / interaction quality gate

## 已锁定决策

- `071` 是 P1 的 visual / a11y foundation child work item，不是 diagnostics、recheck/remediation 或 provider/runtime 工单
- `071` 必须消费 `067 + 068 + 069 + 018 + 065` 的组合 truth，而不是重新发明 Kernel / Recipe / Diagnostics / Gate 语义
- P1 visual foundation 重点是“状态与关键区域是否可见、可感知、不断裂”，而不是像素级还原、完整主题保真或跨平台截图体系
- P1 a11y foundation 重点是“错误/状态可感知、基础语义可识别、主交互可键盘到达、焦点连续”，而不是完整 WCAG 审计平台
- visual / a11y 反馈继续复用 `018` 已冻结的同一套 gate matrix 与 report family，不得新增第二套 visual quality gate 或第二套报告系统
- `065` 的 sample source self-check 只能作为显式输入源；`071` 不得把 sample fixture、当前仓库根或隐式截图路径变成默认 evidence source
- sibling 的 recheck / remediation feedback 继续由 `070` 级别的作者体验主线承接；`071` 只冻结检查面与最小反馈边界，不冻结 remediation runbook
- `071` 当前只做 docs-only formal freeze，不进入 `src/` / `tests/`，不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`

## 用户故事与验收

### US-071-1 — Quality Author 需要 P1 visual / a11y foundation 直接消费上游 truth

作为**质量作者**，我希望 P1 的基础 visual / a11y 检查直接消费 `067`、`068`、`069` 已冻结的 truth，以便检查围绕统一的 `Ui*`、page recipe、state 与 diagnostics 分类工作，而不是围绕 provider 私有 DOM 或自由截图脚本写规则。

**验收**：

1. Given 我查看 `071` formal docs，When 我审阅 visual / a11y coverage matrix，Then 可以直接读到它消费的 `Ui*`、recipe 与状态语义对象
2. Given 我继续 formalize 或实现 visual / a11y 相关切片，When 我读取 `071`，Then 可以明确知道 visual / a11y 只能消费上游 truths，而不能反向重写 Kernel / Recipe / Diagnostics baseline

### US-071-2 — Reviewer 需要确认 P1 foundation 不膨胀成完整质量平台

作为**reviewer**，我希望 `071` 明确说明什么属于 P1 的基础 visual / a11y 能力、什么继续留在 P2 的完整质量平台，以便后续不会把截图矩阵、完整 WCAG 平台或 interaction quality gate 混进当前工单。

**验收**：

1. Given 我查看 `071` formal docs，When 我检查 non-goals，Then 可以明确读到完整 visual regression 平台、完整 a11y 平台、跨 provider 一致性平台均不在本工单内
2. Given 我查看 `071` formal docs，When 我检查 owner boundary，Then 可以明确知道 sibling recheck/remediation 与 provider/runtime 仍在当前工单之外

### US-071-3 — Operator 需要诚实地区分 evidence gap 与真实质量问题

作为**operator**，我希望 `071` 明确 visual / a11y evidence 缺失、稳定空输入与真实问题三者的边界，以便 verify surface 不会把“无证据”误报成“质量退化”，也不会把真实问题静默吞掉。

**验收**：

1. Given 我查看 `071` formal docs，When 我检查 evidence boundary，Then 可以明确知道缺少显式 evidence source 时应暴露 input gap，而不是默认 fallback 到 sample fixture 或仓库根
2. Given 我查看 `071` formal docs，When 我检查 feedback boundary，Then 可以明确知道真实 visual / a11y 问题仍继续复用 `018` 的 report family，而不是另起一套报告系统

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-071-001 | `071` 必须作为 `066` 下游的 visual / a11y foundation child work item 被正式定义，用于冻结 P1 基础体验质量真值 |
| FR-071-002 | `071` 必须明确自身位于 `067 + 068 + 069` 之后，并与 sibling recheck / remediation feedback child 并列，而不是互相吞并 |
| FR-071-003 | `071` 必须继续遵守 `Contract -> Kernel -> Provider/Code -> Gate` 的单一真值顺序，并明确自身只消费 gate 之后的质量检查与反馈面，不反向重写上游 truths |
| FR-071-004 | `071` 必须明确当前 work item 的非目标，包括 diagnostics / drift、recheck / remediation runbook、provider/runtime 实现、完整 visual regression 平台与完整 a11y 平台 |

### P1 Visual Foundation Coverage

| ID | 需求 |
|----|------|
| FR-071-005 | `071` 必须冻结 P1 visual foundation coverage matrix，至少覆盖 `state visual presence`、`required-area visual presence`、`controlled-container visual continuity` 三类质量面 |
| FR-071-006 | `071` 必须明确 `state visual presence` 消费 `067` 中的 `refreshing`、`submitting`、`no-results`、`partial-error`、`success-feedback`，检查这些状态是否有可见、可感知且不与上下文断裂的表现 |
| FR-071-007 | `071` 必须明确 `required-area visual presence` 消费 `068` 中各 recipe 的 `required area`，用于检查关键区域与反馈区是否可见、可辨认，而不是重新定义 recipe 结构真值 |
| FR-071-008 | `071` 必须明确 `controlled-container visual continuity` 至少覆盖 `DialogFormPage`、`WizardPage`、`SearchListPage`、`DashboardPage` 的受控容器/主内容连续性，防止反馈脱离当前上下文，但不得升级为完整响应式/跨设备矩阵 |
| FR-071-009 | `071` 必须明确 visual foundation 的目标是“用户可感知的最小视觉底线”，而不是像素级还原、完整主题保真、动效质量或品牌视觉审核 |

### P1 A11y Foundation Coverage

| ID | 需求 |
|----|------|
| FR-071-010 | `071` 必须冻结 P1 a11y foundation coverage matrix，至少覆盖 `error/status perceivability`、`accessible naming / semantics`、`keyboard reachability`、`focus continuity` 四类质量面 |
| FR-071-011 | `071` 必须明确 `error/status perceivability` 至少消费 `015` 的最小可访问性底线与 `067` 的状态语义，要求错误与状态变化可感知，不得完全依赖视觉位置表达关键状态 |
| FR-071-012 | `071` 必须明确 `accessible naming / semantics` 至少覆盖表单输入、主操作、`UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiToolbar`、`UiPagination`、`UiResult` 等关键语义入口的基础可识别性，而不是建立完整 ARIA/WCAG 平台 |
| FR-071-013 | `071` 必须明确 `keyboard reachability` 至少覆盖搜索/筛选触发、分页导航、主次操作、对话表单动作与向导步骤推进，不得退化为只验证鼠标路径 |
| FR-071-014 | `071` 必须明确 `focus continuity` 至少覆盖 `DialogFormPage` 与 `WizardPage` 的打开、关闭、步骤推进、提交失败与成功反馈后的焦点连续性，但不得扩张为完整交互流程平台 |

### Evidence Boundary And Feedback Honesty

| ID | 需求 |
|----|------|
| FR-071-015 | `071` 必须明确 visual / a11y foundation 只能消费显式 evidence input；sample fixture、当前仓库根或任意隐式截图路径都不得成为默认来源 |
| FR-071-016 | `071` 必须明确 evidence 缺失时应暴露 input gap，而不是伪造 visual / a11y drift；evidence 存在但无可判定对象时，应保留稳定空输入语义 |
| FR-071-017 | `071` 必须明确 visual / a11y 反馈继续复用 `018` 已冻结的 `Violation Report / Coverage Report / Drift Report / legacy expansion report` family，不得新增第二套 report schema |
| FR-071-018 | `071` 必须明确 visual / a11y findings 可以影响 severity、location anchors、quality hints 与 changed-scope 解释，但不得在本工单中直接定义 recheck 计划、remediation runbook 或自动修复动作 |
| FR-071-019 | `071` 必须明确 sibling recheck / remediation feedback 继续承接作者体验闭环；当前工单只冻结 visual / a11y foundation 的检查面与最小反馈边界 |

### Rollout Honesty

| ID | 需求 |
|----|------|
| FR-071-020 | `071` 必须在 `plan.md` 中给出未来 visual / a11y 实现的推荐触点、evidence fixture 边界与最小测试矩阵，但当前批次不得直接修改这些文件 |
| FR-071-021 | `071` 必须明确当前批次只做 docs-only formal freeze，不生成 `development-summary.md`，不宣称 close-ready 或已实现 |
| FR-071-022 | `071` 必须明确当前阶段不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`，root sync 以后续 child formalize 节奏另行评估 |
| FR-071-023 | `071` 必须明确 `.ai-sdlc/project/config/project-state.yaml` 只推进 `next_work_item_seq`，不伪造 root truth sync、program close 或实现落地状态 |

## 关键实体

- **P1 Visual Foundation Coverage Matrix**：承载状态可见性、关键区域可感知性与受控容器视觉连续性的最小质量面
- **P1 A11y Foundation Coverage Matrix**：承载错误/状态可感知性、基础语义/命名、键盘可达性与焦点连续性的最小质量面
- **Visual A11y Evidence Boundary**：描述 visual / a11y 检查可消费的显式 evidence source，以及 input gap / stable empty 的诚实边界
- **Visual A11y Feedback Boundary**：描述 visual / a11y findings 如何继续复用 `018` 的 report family 与 severity / hint 机制
- **Diagnostics-Visual Consumption Boundary**：描述 `071` 如何消费 `069` 已冻结的 diagnostics truth，而不反向定义 diagnostics
- **Visual-Remediation Handoff Boundary**：描述 `071` 与 sibling recheck/remediation feedback 之间“先检查面、后作者反馈闭环”的消费关系

## P1 visual foundation coverage matrix

| 质量面 | 最小覆盖对象 | 口径边界 |
|--------|--------------|----------|
| `State Visual Presence` | `refreshing`、`submitting`、`no-results`、`partial-error`、`success-feedback` | 检查状态是否有明确、可感知、不断裂的视觉表现；不要求像素级一致 |
| `Required-Area Visual Presence` | `PageHeader`、`Search Area`、`Result Summary Area`、`Content Area`、`Action Area`、`State Area`、`Overlay Shell Area`、`Step Context Area` | 只检查关键区域是否可见、可辨认、未被反馈层遮蔽；不重写 recipe 结构真值 |
| `Controlled-Container Visual Continuity` | `DialogFormPage`、`WizardPage`、`SearchListPage`、`DashboardPage` | 检查对话/向导/搜索结果/概览页在状态切换与反馈出现时是否保持主上下文连续性；不升级为完整响应式矩阵 |

## P1 a11y foundation coverage matrix

| 质量面 | 最小覆盖对象 | 口径边界 |
|--------|--------------|----------|
| `Error / Status Perceivability` | 表单错误、提交中、刷新中、空结果、局部失败、成功反馈 | 检查错误与状态变化可被感知；不要求完整无障碍平台或完整朗读脚本体系 |
| `Accessible Naming / Semantics` | 表单输入、主次操作、`UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiToolbar`、`UiPagination`、`UiResult` | 检查关键入口是否保留基础可识别语义；不扩张为完整 ARIA 规范平台 |
| `Keyboard Reachability` | 搜索触发、筛选清理、分页导航、主次操作、对话表单动作、向导推进/返回 | 检查关键路径可通过键盘到达；不扩张为完整交互路径回放平台 |
| `Focus Continuity` | `DialogFormPage`、`WizardPage`、提交失败/成功反馈后的主上下文 | 检查焦点打开、关闭、推进与返回的连续性；不扩张为复杂交互编排平台 |

## 成功标准

- **SC-071-001**：`071` formal docs 能独立表达 P1 visual / a11y foundation 的 scope、non-goals、coverage matrix 与 evidence boundary，而无需回到 design 总览临时推断
- **SC-071-002**：后续 visual / a11y 实现可以直接根据 `067 + 068 + 069 + 018 + 065` 读取 P1 质量消费面，而不会回退到 provider 私有 DOM 或自由截图脚本
- **SC-071-003**：reviewer 能从 `071` 直接读出 `foundation != full visual regression platform != full a11y platform`
- **SC-071-004**：operator 能从 `071` 直接读出 `input gap != stable empty evidence != actual visual/a11y issue`
- **SC-071-005**：sibling recheck/remediation feedback 主线与 `071` 的 handoff 边界清晰，不会把 remediation runbook 或完整作者体验闭环混入当前工单
- **SC-071-006**：`071` 当前状态被清楚表达为 docs-only formal baseline，不会被误读成已实现、已 close-ready 或已进入 root program sync

---
related_doc:
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
