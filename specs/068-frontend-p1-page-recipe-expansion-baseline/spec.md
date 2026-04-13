# 功能规格：Frontend P1 Page Recipe Expansion Baseline

**功能编号**：`068-frontend-p1-page-recipe-expansion-baseline`  
**创建日期**：2026-04-06  
**状态**：accepted child baseline；formal baseline 已冻结；唯一首批 implementation slice（Batch 5）已验证
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `066-frontend-p1-experience-stability-planning-baseline` 冻结后的第二条下游 child work item，先把 P1 的 page recipe expansion 正式冻结成单一 formal truth；在 formal baseline 完成后，再允许唯一的首批 implementation slice，把同一份 recipe truth 落到 Kernel model 与定向 unit tests。它只处理“新增哪些 page recipe 标准本体、这些 recipe 的 `required area / optional area / forbidden pattern` 是什么、它们如何消费 `067` 已冻结的 expanded kernel truth、以及它们与 diagnostics / provider/runtime 的边界”这条 recipe 主线；它不是 semantic component 工单，不是 diagnostics / drift 工单，也不是 provider/runtime 实现工单。

## 问题定义

`015` 已冻结 MVP 阶段的 `ListPage / FormPage / DetailPage` page recipe 标准本体，并明确 `page recipe standard body` 归 UI Kernel、`recipe declaration` 归 Contract。`067` 又进一步冻结了 P1 的 expanded kernel truth，补齐了 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 与 `refreshing / submitting / no-results / partial-error / success-feedback` 这组新增语义。

但当前仓库仍缺少一份正式的 P1 recipe 扩展真值，回答以下问题：

- P1 在 MVP recipe 之上到底新增哪些 page recipe 标准本体
- `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 各自的 `required area / optional area / forbidden pattern` 应如何冻结
- 这些 recipe 如何消费 `067` 的 expanded kernel truth，而不是反向重写 `Ui*` 组件语义
- 哪些内容必须继续留在下游 diagnostics / drift、同一套 gate matrix 的兼容执行口径相关规则/反馈面与 provider/runtime 工单，而不能在 `068` 里抢跑

如果不先冻结 `068`，后续 P1 child 会快速滑向三种典型偏差：

- `SearchListPage` 在没有 formal recipe truth 的情况下继续沿用自由拼装页面，导致 `UiSearchBar / UiFilterBar / UiResult / UiPagination` 的结构角色漂移
- `DialogFormPage / WizardPage` 在没有标准本体的情况下被 provider runtime 或企业历史骨架反向主导，退化成 overlay API 或页面实现细节
- `069` 在没有 expanded recipe truth 的情况下先扩 diagnostics / drift，只能围绕临时页面结构或 provider 局部命名写规则

因此，`068` 的职责是先冻结 P1 page recipe expansion truth；在 formal baseline 完成后，当前工单只允许唯一的首批 page recipe implementation slice，把该 truth 落到模型与定向单测，而不是继续扩大到 diagnostics、provider/runtime、root sync 或下游 `069` formalize。

## 范围

- **覆盖**：
  - 将 P1 page recipe expansion 正式定义为 `066` 下游的独立 child work item
  - 锁定 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 的标准本体、适用场景与结构边界
  - 锁定每个 P1 recipe 的 `required area / optional area / forbidden pattern`
  - 锁定各 recipe 对 `067` expanded kernel truth 与 `015` MVP recipe baseline 的消费关系
  - 锁定 recipe 级状态期望与与 `069` diagnostics / drift、provider/runtime 工单的 handoff 边界
  - 为后续 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py` 与对应测试切片提供 canonical baseline
  - 在 formal baseline 完成后，仅允许唯一的首批 implementation slice 将 page recipe expansion truth 落到 `src/ai_sdlc/models/frontend_ui_kernel.py` 与 `src/ai_sdlc/models/__init__.py`
  - 用 `tests/unit/test_frontend_ui_kernel_models.py` 与 `tests/unit/test_frontend_ui_kernel_artifacts.py` 验证 page recipe builder、recipe consumption boundary 与 artifact payload 承接保持一致
- **不覆盖**：
  - 改写 `067` 已冻结的 `Ui*` 语义组件协议或页面级状态语义
  - 扩张 whitelist、token rules、drift diagnostics、同一套 gate matrix 的兼容执行口径相关规则/反馈面或 remediation feedback
  - 定义 `Ui* -> provider/runtime` 的具体映射、wrapper API、Vue 组件实现或企业样式承接
  - 引入新的 `UiStepper`、图表协议或其他未在 `067` 正式冻结的语义组件
  - 直接修改 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py` 或扩大到其他 `src/` / `tests/` 写面
  - 改写 `015` 已冻结的 MVP recipe truth、`017/018` 的治理与 gate truth，或将 sample self-check 语义混入 recipe baseline
  - 引入 P2 的 `modern provider / multi-theme / multi-style` 或更完整的 visual / a11y 平台

## 已锁定决策

- `068` 是 P1 的 page recipe expansion child work item，不是 diagnostics / provider/runtime 工单
- P1 新增 recipe 标准本体固定包括 `DashboardPage`、`DialogFormPage`、`SearchListPage`、`WizardPage`
- `068` 继续遵守 `recipe standard body` 归 UI Kernel、`recipe declaration` 归 Contract 的单一真值顺序
- `068` 必须消费 `067` 已冻结的 expanded kernel truth，不能反向重写 `UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 等组件语义
- `SearchListPage` 是对 MVP `ListPage` 的 P1 扩展 recipe，不等于自由拼装的“搜索页 + 列表页”混合体
- `DialogFormPage` 定义的是受控 overlay/drawer 语义下的 form recipe 标准本体，不等于 provider runtime 的具体弹层 API
- `WizardPage` 定义的是有顺序约束的多步流程 recipe；本工单不因此新增 `UiStepper` 协议，具体 step progress primitive 以后续实现与更后续 child 为准
- `DashboardPage` 定义的是 overview / section / card / result composition 的 page recipe 标准本体，不等于自由堆叠卡片墙，也不预设图表组件协议
- `069` 必须消费 `067 + 068 + 017 + 018 + 065` 的组合 truth，当前 `068` 不提前写 diagnostics / drift 或 gate feedback
- `068` formal baseline 已完成；当前唯一允许的实现批次是 Batch 5 page recipe model expansion slice，写面仅限 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py`
- 当前 implementation slice 不改 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`，不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`，也不 formalize 下游 `069`
- `068` 的当前状态必须被表达为 `accepted child baseline + verified first implementation slice`，但这不代表 `069`、provider/runtime、root sync 或 close-ready 已开始

## 用户故事与验收

### US-068-1 — Recipe Author 需要 P1 recipe 标准本体先冻结

作为**recipe 作者**，我希望 P1 先把新增 page recipe 标准本体冻结成独立 child baseline，以便后续实现和 contract declaration 直接消费统一的 recipe truth，而不是继续靠自由拼装页面结构。

**验收**：

1. Given 我查看 `068` formal docs，When 我审阅 P1 recipe 集，Then 可以直接读到 4 个新增 recipe 标准本体及其结构边界
2. Given 我继续 formalize 或实现下游 recipe 相关切片，When 我读取 `068`，Then 可以明确知道每个 recipe 的 `required area / optional area / forbidden pattern`

### US-068-2 — Contract Author 需要 recipe declaration 与 recipe 标准本体继续分层

作为**Contract 作者**，我希望 `068` 继续明确 `recipe standard body != recipe declaration`，以便 contract 只负责声明当前页面选哪个 recipe，而不是重新定义页面结构。

**验收**：

1. Given 我查看 `068` formal docs，When 我检查 truth order，Then 可以明确读到 recipe 标准本体仍归 UI Kernel，Contract 只承载 declaration
2. Given 我准备写 `SearchListPage` 或 `WizardPage` declaration，When 我读取 `068`，Then 可以明确知道 declaration 不能反向改写标准本体

### US-068-3 — Governance Author 需要 recipe truth 先于 diagnostics freeze

作为**治理作者**，我希望 P1 recipe 先在 Kernel 层冻结，以便后续 diagnostics / drift 可以围绕同一套 recipe 结构语义工作，而不是围绕 provider 私有页面结构或旧页面骨架写规则。

**验收**：

1. Given 我查看 `068` formal docs，When 我审阅 recipe 级状态期望与 forbidden pattern，Then 可以直接读到 `069` 应消费的结构真值
2. Given 我继续 formalize `069`，When 我读取 `068`，Then 可以明确知道 diagnostics 不应重新发明 recipe 结构语义

### US-068-4 — Model Maintainer 需要在不扩 scope 的前提下落地已冻结 recipe truth

作为**model 维护者**，我希望在 formal baseline 完成后，只用一个狭窄的 implementation slice 把 P1 page recipe expansion truth 落到 model 与 unit tests，以便后续 diagnostics / provider child 消费的是同一份 recipe truth，而不是临时实现细节。

**验收**：

1. Given 我查看 `068` formal docs，When 我检查当前 implementation slice，Then 可以明确读到唯一允许的写面只包括 2 个 model 文件和 2 个 unit test 文件
2. Given 我查看 `068` formal docs，When 我检查当前状态表达，Then 可以明确知道首批 implementation slice 已验证，但 `069`、provider/runtime、root sync 仍未开始

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-068-001 | `068` 必须作为 `066` 下游的 page recipe expansion child work item 被正式定义，用于冻结 P1 page recipe truth |
| FR-068-002 | `068` 必须明确自身位于 `067` expanded kernel truth 之后、`069` diagnostics / drift 扩展之前 |
| FR-068-003 | `068` 必须继续遵守 `Contract -> Kernel -> Provider/Code -> Gate` 的单一真值顺序，并明确 `recipe standard body` 归 UI Kernel、`recipe declaration` 归 Contract |
| FR-068-004 | `068` 必须明确当前 work item 的非目标，包括 diagnostics / drift、同一套 gate matrix 的兼容执行口径相关规则/反馈面、provider 映射与 runtime 实现 |

### P1 Page Recipe Set Expansion

| ID | 需求 |
|----|------|
| FR-068-005 | `068` 必须冻结 P1 新增 recipe 集合，至少包括 `DashboardPage`、`DialogFormPage`、`SearchListPage`、`WizardPage` |
| FR-068-006 | `068` 必须明确每个 recipe 定义的是页面结构真值、区域角色与交互边界，而不是 provider runtime API 的直接透传 |
| FR-068-007 | `068` 必须明确 `SearchListPage` 消费 `067` 中的 `UiSearchBar / UiFilterBar / UiResult / UiToolbar / UiPagination` 语义，而不得反向重定义这些组件协议 |
| FR-068-008 | `068` 必须明确 `DialogFormPage` 承接 `FormPage` 的受控 overlay/drawer 变体语义，但不得退化为某个 provider 弹窗组件 API 的别名 |
| FR-068-009 | `068` 必须明确 `WizardPage` 表达有顺序约束的多步流程 recipe，但本工单不得因此新增未冻结的 `Ui*` 组件协议 |
| FR-068-010 | `068` 必须明确 `DashboardPage` 表达 overview / section / card / result composition 的 page recipe 语义，不得被自由卡片堆叠或 provider 历史骨架反向主导 |
| FR-068-011 | `068` 必须明确 P1 recipe 继续保持 Provider 无关性，并为 `enterprise-vue2 provider` 与 future modern provider 共同服务 |

### Recipe Area Constraint And State Expectations

| ID | 需求 |
|----|------|
| FR-068-012 | `068` 必须为每个 P1 recipe 冻结 `required area / optional area / forbidden pattern` 三类区域约束 |
| FR-068-013 | `068` 必须明确 `SearchListPage` 至少覆盖 search / result / content / pagination / state 这些 area 角色，并与 MVP `ListPage` 的无查询上下文列表页保持区分 |
| FR-068-014 | `068` 必须明确 `DialogFormPage`、`WizardPage` 至少冻结提交过程、局部失败与成功反馈相关的 recipe 级状态期望，但不得在本工单中直接工程化为 gate 规则 |
| FR-068-015 | `068` 必须明确 `DashboardPage`、`SearchListPage` 至少冻结 `refreshing` 与 `partial-error` 的 recipe 级状态期望，并保持与 `015` MVP baseline 的单一真值关系 |
| FR-068-016 | `068` 必须明确任何页面级 declaration、provider 例外或历史页面骨架都不得实质性重写已冻结的 P1 recipe 标准本体 |

### Downstream Handoff And Rollout Honesty

| ID | 需求 |
|----|------|
| FR-068-017 | `068` 必须明确 `069` 负责 whitelist / token / drift diagnostics / coverage expansion，不得在当前工单抢跑 |
| FR-068-018 | `068` 必须在 formal baseline 完成后允许唯一的 Batch 5 implementation slice，且写面仅限 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py` |
| FR-068-019 | `068` 的当前 implementation slice 必须在 `067` 已落地的 kernel semantic truth 之上 materialize `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 与 `consumed_protocols / minimum_state_expectations` 的模型真值 |
| FR-068-020 | `068` 的当前 implementation slice 必须通过定向 RED/GREEN unit tests 证明 page recipe truth 既可被 Kernel model 构造/校验，也继续被 artifact payload 消费 |
| FR-068-021 | `068` 必须明确当前状态是 `accepted child baseline + verified first implementation slice`，不生成 `development-summary.md`，也不宣称 `069`、provider/runtime、root sync 或 close-ready 已开始 |
| FR-068-022 | `068` 必须明确当前阶段不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`，root sync 以后续 child formalize 节奏另行评估 |
| FR-068-023 | `068` 必须明确文中出现的下游 diagnostics child 编号只用于当前 planning 口径；真实后续编号以后续 scaffold 时的 `project-state` 为准 |

### Implementation Slice Contract

| ID | 需求 |
|----|------|
| FR-068-024 | 当前 implementation slice 不得直接修改 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`，除非 RED 证明 page recipe expansion truth 不能被现有 artifact 层消费；在当前工单已验证路径中，该 generator 保持不变 |
| FR-068-025 | 当前 implementation slice 不得扩张到 diagnostics / drift、provider/runtime 映射、root truth sync 或下游 `069` formalize |

## 关键实体

- **P1 Page Recipe Set**：承载 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 的 page recipe 标准本体扩展集合
- **Recipe Area Constraint Model**：承载每个 recipe 的 `required area / optional area / forbidden pattern`
- **Recipe State Expectation Baseline**：承载 recipe 级最小状态期望与与 `015` / `067` 状态语义的关系
- **Kernel-Recipe Consumption Boundary**：描述 `068` 如何消费 `067` expanded kernel truth，而不反向改写 `Ui*` 协议
- **Recipe-Governance Handoff Boundary**：描述 `068` 与后续 diagnostics / drift child 之间“先 recipe、后治理”的消费关系

## P1 新增 page recipe 标准本体

| Recipe | 核心场景 | required area | optional area | forbidden pattern |
|--------|----------|---------------|---------------|-------------------|
| `DashboardPage` | 概览、指标总览、卡片化信息分区、跨区域总览操作 | `PageHeader`、`Summary Area`、`Main Insight Area`、`State Area` | `Filter Scope Area`、`Toolbar / Quick Action Area`、`Secondary Section Area` | 自由卡片墙替代标准区域结构；将完整表单页或单一列表页直接冒充 dashboard |
| `DialogFormPage` | 受控弹层/抽屉中的录入、编辑、确认型表单流程 | `Overlay Shell Area`、`Title / Context Area`、`Form Area`、`Action Area`、`State / Validation Area` | `Help / Description Area`、`Secondary Section Area` | 退化为 provider 弹窗 API 别名；引入分页区或自由列表区作为主骨架；把多步流程直接混入单步对话表单 |
| `SearchListPage` | 有明确搜索/筛选上下文的结果页、资源检索页、结果集页面 | `PageHeader`、`Search Area`、`Result Summary Area`、`Content Area`、`State Area`、`Pagination Area` | `Filter Area`、`Toolbar / Primary Action Area` | 将无查询上下文列表页当作 `SearchListPage`；跳过结果摘要直接自由拼装结果区；用任意布局绕开分页与状态区 |
| `WizardPage` | 有顺序约束的多步流程、分步录入、分步确认 | `PageHeader / Step Context Area`、`Step Progress Area`、`Step Content Area`、`Action Area`、`State / Feedback Area` | `Review / Summary Area`、`Help / Aside Area` | 用自由 tab 切换冒充步骤语义；在同一步暴露多个并列主操作；将步骤内容拆成无顺序约束的自由页面片段 |

## Recipe 级状态期望

| Recipe | 最低状态期望 | 关系说明 |
|--------|---------------|----------|
| `DashboardPage` | `refreshing`、`partial-error` | 表达已有内容基础上的刷新与局部区域失败；不替代全局 `loading / error` |
| `DialogFormPage` | `submitting`、`partial-error`、`success-feedback` | 表达对话式表单的提交中、局部校验/提交流程失败与短时成功反馈 |
| `SearchListPage` | `refreshing`、`no-results`、`partial-error` | 与 MVP `ListPage` 的 `empty` 分离，强调查询/筛选上下文下的空结果 |
| `WizardPage` | `submitting`、`partial-error`、`success-feedback` | 表达步骤推进或最终提交过程中的状态与有限成功反馈，不等于新增 stepper 协议 |

## 成功标准

- **SC-068-001**：`068` formal docs 能独立表达 P1 page recipe expansion 的 scope、non-goals、recipe 集与 area constraint，而无需回到 design 总览临时推断
- **SC-068-002**：`067` 的 expanded kernel truth 被 `068` 直接消费，而不会再通过 recipe 反向定义组件语义
- **SC-068-003**：后续 diagnostics / drift child 可以直接根据 `068` 读取 recipe 结构真值与最小状态期望，而不会围绕 provider 私有页面结构重写规则
- **SC-068-004**：reviewer 能从 `068` 直接读出 `068 != 067 != 069 != provider/runtime` 的边界
- **SC-068-005**：`068` 当前状态被清楚表达为 `accepted child baseline + verified first implementation slice`，不会被误读成 `069`、provider/runtime、root program sync 或 close-ready 已开始
- **SC-068-006**：reviewer 能从 `068` 直接读出当前 implementation slice 的唯一允许写面、验证方式与继续排除的 non-goals，而不需要回头依赖 `plan.md / tasks.md / task-execution-log.md` 反向推断顶层真值

---
related_doc:
  - "specs/108-frontend-legacy-framework-evidence-class-backfill-baseline/spec.md"
frontend_evidence_class: "framework_capability"
---
