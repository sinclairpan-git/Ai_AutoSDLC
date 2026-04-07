# 功能规格：Frontend P1 UI Kernel Semantic Expansion Baseline

**功能编号**：`067-frontend-p1-ui-kernel-semantic-expansion-baseline`
**创建日期**：2026-04-06
**状态**：accepted child baseline；formal baseline 已冻结；唯一首批 implementation slice（Batch 5）已验证
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../015-frontend-ui-kernel-standard-baseline/spec.md`](../015-frontend-ui-kernel-standard-baseline/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `066-frontend-p1-experience-stability-planning-baseline` 冻结后的首条下游 child work item，先把 P1 的 UI Kernel 语义扩展正式冻结成单一 formal truth；在 formal baseline 完成后，再允许唯一的首批 implementation slice，把同一份 truth 落到 Kernel model 与定向 unit tests。它只处理“新增哪些 `Ui*` 语义组件协议、扩展哪些页面状态语义、这些语义如何继续保持 Provider 无关性与与 recipe/diagnostics 的边界”这条 Kernel 主线；它不是 page recipe 扩展工单，不是 diagnostics / drift 工单，也不是 provider/runtime 实现工单。

## 问题定义

`015` 已冻结 MVP 阶段的 UI Kernel standard body，明确了 MVP 首批 `Ui*` 语义组件、`ListPage / FormPage / DetailPage` page recipe 标准本体，以及最小状态/交互底线。`066` 又进一步冻结了 P1 的 child DAG，明确第一条主线应先 formalize `frontend-p1-ui-kernel-semantic-expansion-baseline`，再进入 recipe、diagnostics、recheck 与 visual/a11y。

但当前仓库仍缺少一份正式的 P1 Kernel 扩展真值，回答以下问题：

- P1 在 MVP 之上到底新增哪些 `Ui*` 语义组件协议
- P1 的页面级状态语义要扩展到什么范围，才能支撑 search/filter/result/dashboard/wizard 等后续体验稳定层场景
- 这些新增语义如何继续保持“Kernel 是标准协议层，不是 provider/runtime API 透传”
- 哪些内容必须继续留在 `068` 的 page recipe 扩展与 `069` 的 diagnostics / drift 工单，而不能在 `067` 里抢跑

如果不先冻结 `067`，后续 P1 child 会快速滑向三种典型偏差：

- `068` 在没有 expanded kernel truth 的情况下直接扩 page recipe，导致 recipe 标准本体倒逼 `Ui*` 协议
- `069` 在没有 expanded state semantics 的情况下先扩 drift / diagnostics，导致 gate 反馈只能围绕临时命名或 provider 细节
- provider 或企业项目历史页面模式反向主导 P1 组件集，使 `UiTabs / UiSearchBar / UiFilterBar / UiToolbar / UiPagination / UiSection / UiCard / UiResult` 退化成底层 API 别名

因此，`067` 的职责是先冻结 P1 UI Kernel semantic expansion truth；在 formal baseline 完成后，当前工单只允许唯一的首批 kernel model semantic expansion slice，把该 truth 落到模型与定向单测，而不是继续扩大到 recipe、diagnostics、provider/runtime 或 root sync。

## 范围

- **覆盖**：
  - 将 P1 UI Kernel semantic expansion 正式定义为 `066` 下游的独立 child work item
  - 锁定 P1 新增 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 的最小语义边界
  - 锁定 P1 页面级状态语义扩展，至少包括 `refreshing / submitting / no-results / partial-error / success-feedback`
  - 锁定新增语义组件与状态语义继续保持 Provider 无关性的方式
  - 为后续 `068` recipe 扩展、`069` diagnostics / drift 扩展提供 canonical baseline
  - 在 formal baseline 完成后，仅允许唯一的首批 implementation slice 将 expanded kernel truth 落到 `src/ai_sdlc/models/frontend_ui_kernel.py` 与 `src/ai_sdlc/models/__init__.py`
  - 用 `tests/unit/test_frontend_ui_kernel_models.py` 与 `tests/unit/test_frontend_ui_kernel_artifacts.py` 验证模型层 truth 与 artifact payload 承接保持一致
- **不覆盖**：
  - 定义 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 的 page recipe 标准本体
  - 扩张 whitelist、token rules、drift diagnostics、同一套 gate matrix 的兼容执行口径相关规则/反馈面或 remediation feedback
  - 定义 `Ui* -> enterprise-vue2 provider` 的具体映射、wrapper API、白名单承接或 runtime 组件实现
  - 直接修改 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py` 或扩大到其他 `src/` / `tests/` 写面
  - 改写 `015` 已冻结的 MVP Kernel truth、`017/018` 的治理与 gate truth，或将 sample self-check 语义混入 Kernel baseline
  - formalize 下游 `068/069`，或改 root `program-manifest.yaml`、`frontend-program-branch-rollout-plan.md`
  - 引入 P2 的 `modern provider / multi-theme / multi-style` 或更完整的运行时体验平台

## 已锁定决策

- `067` 是 P1 的 UI Kernel semantic expansion child work item，不是 recipe / diagnostics / provider 工单
- P1 新增语义组件固定包括 `UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiResult`、`UiSection`、`UiToolbar`、`UiPagination`、`UiCard`
- `067` 只扩展 UI Kernel 标准协议与页面级状态语义，不直接创建新的 page recipe 标准本体
- `068` 必须消费 `067` 的 expanded kernel truth；`069` 必须消费 `067 + 068 + 017 + 018 + 065` 的组合 truth
- `067` 中的状态语义仍属于 Kernel baseline，drift / diagnostics / checkability 归后续治理工单承接
- 新增 `Ui*` 协议定义的是能力、语义、结构角色与边界，不是底层组件库 API 透传
- 新增页面状态语义必须与 `015` 的 `loading / empty / error / disabled / no-permission` 共存，而不是重写 MVP baseline
- `067` formal baseline 已完成；当前唯一允许的实现批次是 Batch 5 kernel model semantic expansion slice，写面仅限 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py`
- 当前 implementation slice 不改 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`，不改 root `program-manifest.yaml` 或 `frontend-program-branch-rollout-plan.md`，也不 formalize 下游 `068/069`
- `067` 的当前状态必须被表达为 `accepted child baseline + verified first implementation slice`，但这不代表 recipe、diagnostics、provider/runtime、root sync 或 close-ready 已开始

## 用户故事与验收

### US-067-1 — Kernel Maintainer 需要 P1 扩展组件集先于 recipe formalize

作为**Kernel 维护者**，我希望 P1 先把新增 `Ui*` 语义组件协议冻结成独立 child baseline，以便 `068` 扩展 page recipe 时直接消费 expanded kernel truth，而不是反向定义组件语义。

**验收**：

1. Given 我查看 `067` formal docs，When 我审阅 P1 component set，Then 可以直接读到 8 个新增 `Ui*` 语义组件的正式集合与边界
2. Given 我继续 formalize `068`，When 我读取 `067`，Then 可以明确知道 recipe 扩展只能消费这些组件语义，而不能反向重写它们

### US-067-2 — Governance Author 需要状态语义先冻结，再进入 diagnostics

作为**治理作者**，我希望 P1 的页面级状态语义先在 Kernel 层冻结，以便后续 diagnostics / drift 能围绕同一组语义状态工作，而不是围绕 provider 私有字段或页面临时命名。

**验收**：

1. Given 我查看 `067` formal docs，When 我审阅状态语义，Then 可以直接读到 P1 在 MVP 之上扩展的状态集合
2. Given 我继续 formalize `069`，When 我读取 `067`，Then 可以明确知道 diagnostics 应消费 expanded state semantics，而不是重新发明状态分类

### US-067-3 — Reviewer 需要确认 P1 Kernel 扩展不越界

作为**reviewer**，我希望 `067` 明确说明什么属于 semantic kernel expansion、什么继续留在 recipe / diagnostics / provider 下游，以便后续子项不会把多条主线混在一起推进。

**验收**：

1. Given 我查看 `067` formal docs，When 我检查 non-goals，Then 可以明确读到 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 不在本工单内
2. Given 我查看 `067` formal docs，When 我检查 owner boundary，Then 可以明确知道 `069` 前不扩 diagnostics，`enterprise-vue2 provider` 前不扩 runtime 映射

### US-067-4 — Model Maintainer 需要在不扩 scope 的前提下落地已冻结 truth

作为**model 维护者**，我希望在 formal baseline 完成后，只用一个狭窄的 implementation slice 把 expanded kernel truth 落到 model 与 unit tests，以便后续 recipe / diagnostics / provider child 消费的是同一份 Kernel truth，而不是临时实现细节。

**验收**：

1. Given 我查看 `067` formal docs，When 我检查当前 implementation slice，Then 可以明确读到唯一允许的写面只包括 2 个 model 文件和 2 个 unit test 文件
2. Given 我查看 `067` formal docs，When 我检查当前状态表达，Then 可以明确知道首批 implementation slice 已验证，但 `068/069`、provider/runtime、root sync 仍未开始

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-067-001 | `067` 必须作为 `066` 下游的第一条 child work item 被正式定义，用于冻结 P1 UI Kernel semantic expansion truth |
| FR-067-002 | `067` 必须明确自身位于 `015` MVP Kernel baseline 之后、`068` recipe 扩展之前 |
| FR-067-003 | `067` 必须明确当前 work item 的非目标，包括 page recipe 标准本体扩展、governance diagnostics / drift、provider 映射与 runtime 实现 |
| FR-067-004 | `067` 必须继续遵守 `009` 已冻结的 `Contract -> Kernel -> Provider/Code -> Gate` 单一真值顺序 |

### P1 Semantic Component Expansion

| ID | 需求 |
|----|------|
| FR-067-005 | `067` 必须冻结 P1 新增语义组件集合，至少包括 `UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiResult`、`UiSection`、`UiToolbar`、`UiPagination`、`UiCard` |
| FR-067-006 | `067` 必须明确新增 `Ui*` 协议定义的是结构角色、能力边界与交互语义，而不是底层企业组件库 API 的直接透传 |
| FR-067-007 | `067` 必须明确 `UiSearchBar / UiFilterBar / UiToolbar / UiPagination / UiSection / UiCard / UiResult` 属于可被 page recipe 消费的 Kernel 结构语义，不得在 `068` 中被反向重定义 |
| FR-067-008 | `067` 必须明确 `UiTabs` 作为语义导航/分段容器协议存在，不能被任意页面局部例外声明改写为 provider 私有实现细节 |
| FR-067-009 | `067` 必须明确新增语义组件继续保持 Provider 无关性，并为 `enterprise-vue2 provider` 与 future modern provider 共同服务 |

### P1 State Semantic Expansion

| ID | 需求 |
|----|------|
| FR-067-010 | `067` 必须在 `015` 的 MVP 状态基线之上扩展 P1 页面级状态语义，至少包括 `refreshing`、`submitting`、`no-results`、`partial-error`、`success-feedback` |
| FR-067-011 | `067` 必须明确 `no-results` 与 MVP 的 `empty` 语义不同：前者表示查询/筛选后的空结果，后者表示页面在无筛选上下文下的空态 |
| FR-067-012 | `067` 必须明确 `partial-error` 表示页面或区域的部分失败，不得与全局 `error` 合并为同一语义 |
| FR-067-013 | `067` 必须明确 `refreshing / submitting / success-feedback` 属于页面级体验状态基线，后续 diagnostics / recheck 可消费，但不得在本工单中直接工程化为 gate 规则 |
| FR-067-014 | `067` 必须明确新增状态语义与最小可感知性边界继续归 Kernel baseline 持有，而不是由 provider 或单页实现自行命名 |

### Downstream Handoff And Rollout Honesty

| ID | 需求 |
|----|------|
| FR-067-015 | `067` 必须明确 `068` 负责 page recipe 标准本体扩展，至少承接 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` |
| FR-067-016 | `067` 必须明确 `069` 负责 whitelist / token / drift diagnostics / coverage expansion，不得在当前工单抢跑 |
| FR-067-017 | `067` 必须在 formal baseline 完成后允许唯一的 Batch 5 implementation slice，且写面仅限 `src/ai_sdlc/models/frontend_ui_kernel.py`、`src/ai_sdlc/models/__init__.py`、`tests/unit/test_frontend_ui_kernel_models.py`、`tests/unit/test_frontend_ui_kernel_artifacts.py` |
| FR-067-018 | `067` 的当前 implementation slice 必须把 expanded semantic component / state truth 落到 Kernel model，并通过定向 RED/GREEN unit tests 证明该 truth 继续被 artifact payload 消费 |
| FR-067-019 | `067` 必须明确当前状态是 `accepted child baseline + verified first implementation slice`，不生成 `development-summary.md`，也不宣称 `068/069`、provider/runtime、root sync 或 close-ready 已开始 |

### Implementation Slice Contract

| ID | 需求 |
|----|------|
| FR-067-020 | 当前 implementation slice 不得直接修改 `src/ai_sdlc/generators/frontend_ui_kernel_artifacts.py`，除非 RED 证明 expanded kernel truth 不能被现有 artifact 层消费；在当前工单已验证路径中，该 generator 保持不变 |
| FR-067-021 | 当前 implementation slice 不得扩张到 page recipe 标准本体、diagnostics / drift、provider/runtime 映射、root truth sync 或下游 `068/069` formalize |

## 关键实体

- **P1 Semantic Component Set**：承载 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 的结构化语义组件扩展集合
- **P1 View State Semantic Baseline**：承载 `refreshing / submitting / no-results / partial-error / success-feedback` 的页面级状态语义扩展
- **Component Capability Boundary**：描述新增 `Ui*` 协议的结构角色、可接受能力面与禁止透出的底层实现细节
- **Kernel-Recipe Handoff Boundary**：描述 `067` 与 `068` 之间“先 Kernel、后 Recipe”的消费关系
- **Kernel-Governance Handoff Boundary**：描述 `067` 与 `069` 之间“先状态语义、后 diagnostics / drift”的消费关系

## P1 新增语义组件与状态语义

### 新增语义组件集合

| 组件 | 核心角色 | 明确边界 |
|------|----------|----------|
| `UiTabs` | 语义分段切换与主内容分域容器 | 不得退化为任意 provider tab API 透传 |
| `UiSearchBar` | 承载搜索条件输入与触发语义 | 不得隐式取代完整 page recipe |
| `UiFilterBar` | 承载筛选条件集合、筛选反馈与清理动作 | 不得被 provider 私有 filter panel 结构反向主导 |
| `UiResult` | 承载结果概览、成功/失败/提示性输出 | 不得与通用消息提示混同 |
| `UiSection` | 承载页面内部结构分区与区域标题/操作边界 | 不得替代 page recipe 标准本体 |
| `UiToolbar` | 承载页内主次操作与批量动作区域 | 不得透出任意布局实现 API |
| `UiPagination` | 承载分页导航与结果集翻页语义 | 不得与 provider 数据表私有分页 API 绑定 |
| `UiCard` | 承载结构化信息块与块级操作容器 | 不得退化为纯视觉盒子组件协议 |

### 新增页面级状态语义

| 状态 | 语义 | 与 MVP 基线关系 |
|------|------|----------------|
| `refreshing` | 页面已有内容基础上的重新拉取/刷新过程 | 不替代 `loading`，而是补充“有旧内容时的刷新” |
| `submitting` | 表单或局部页面动作提交进行中 | 不替代 `disabled`，而是表达提交过程语义 |
| `no-results` | 搜索/筛选后的结果为空 | 与无上下文的 `empty` 分离 |
| `partial-error` | 页面或区域局部失败，但其余内容仍可展示 | 与全局 `error` 分离 |
| `success-feedback` | 操作成功后的有限反馈状态 | 不等于长期页面状态，也不取代结构型结果呈现 |

## 成功标准

- **SC-067-001**：`067` formal docs 能独立表达 P1 UI Kernel semantic expansion 的 scope、non-goals、组件集合与状态语义，而无需回到 design 总览临时推断
- **SC-067-002**：`068` 可以直接根据 `067` 读取 expanded kernel truth，而不会再通过 recipe 反向定义组件语义
- **SC-067-003**：`069` 可以直接根据 `067` 读取 expanded state semantics，而不会将状态命名退回 provider 私有口径
- **SC-067-004**：reviewer 能从 `067` 直接读出 `067 != 068 != 069 != provider/runtime` 的边界
- **SC-067-005**：`067` 当前状态被清楚表达为 `accepted child baseline + verified first implementation slice`，不会被误读成 `068/069`、provider/runtime、root program sync 或 close-ready 已开始
- **SC-067-006**：reviewer 能从 `067` 直接读出当前 implementation slice 的唯一允许写面、验证方式与继续排除的 non-goals，而不需要回头依赖 `plan.md / tasks.md / task-execution-log.md` 反向推断顶层真值
