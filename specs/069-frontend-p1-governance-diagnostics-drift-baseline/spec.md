# 功能规格：Frontend P1 Governance Diagnostics Drift Baseline

**功能编号**：`069-frontend-p1-governance-diagnostics-drift-baseline`  
**创建日期**：2026-04-06  
**状态**：accepted child baseline；formal baseline 已冻结；唯一首批 implementation slice（Batch 5）已完成
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../017-frontend-generation-governance-baseline/spec.md`](../017-frontend-generation-governance-baseline/spec.md)、[`../018-frontend-gate-compatibility-baseline/spec.md`](../018-frontend-gate-compatibility-baseline/spec.md)、[`../065-frontend-contract-sample-source-selfcheck-baseline/spec.md`](../065-frontend-contract-sample-source-selfcheck-baseline/spec.md)、[`../066-frontend-p1-experience-stability-planning-baseline/spec.md`](../066-frontend-p1-experience-stability-planning-baseline/spec.md)、[`../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md`](../067-frontend-p1-ui-kernel-semantic-expansion-baseline/spec.md)、[`../068-frontend-p1-page-recipe-expansion-baseline/spec.md`](../068-frontend-p1-page-recipe-expansion-baseline/spec.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `066-frontend-p1-experience-stability-planning-baseline` 冻结后的第三条下游 child work item，先把 P1 的 governance diagnostics / drift expansion 正式冻结成单一 formal truth；在 formal baseline 完成后，再允许唯一的首批 implementation slice，把同一份 diagnostics truth 落到 gate policy model、artifact generator 与定向 unit tests。它只处理“P1 扩张哪些 diagnostics coverage 面、如何分类 gap / empty / drift、以及这些反馈如何继续服从 `018` 已冻结的同一套 gate matrix 执行口径”这条治理主线；它不是 recheck / remediation child，不是 visual / a11y child，也不是 provider/runtime 执行链实现工单。

## 问题定义

`017` 已冻结并实现了 MVP generation governance truth，`018` 已冻结并实现了 shared gate matrix、Compatibility 执行口径、结构化 report family 与 gate policy artifacts，`067` 与 `068` 又分别补齐了 P1 semantic component truth 与 page recipe truth。

但当前仓库仍缺少一份正式的 P1 diagnostics / drift 扩展真值，回答以下问题：

- P1 在 MVP diagnostics 之上到底扩张哪些 semantic component / recipe / state / whitelist / token coverage 面
- 这些新增 diagnostics 如何继续服从 `018` 的同一套 gate matrix，而不是演化成第二套 compatibility gate
- `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 与 `refreshing / submitting / no-results / partial-error / success-feedback` 的 drift / coverage 反馈应如何分类
- observation artifact 缺失、observation 为空、以及真实 drift 三者如何保持诚实区分
- 哪些内容必须继续留给 `070` recheck / remediation feedback child、`071` visual / a11y child 与更后续 provider/runtime 工单，而不能在 `069` 里抢跑

如果不先冻结并 materialize `069`，后续 P1 child 会快速滑向三种典型偏差：

- diagnostics 围绕 provider 私有实现细节或历史页面骨架扩张，而不是消费 `067 + 068` 的统一结构真值
- Compatibility 被重新表述成“第二套 gate”，导致不同执行强度与不同规则集混用
- observation 输入缺失、空结果与真实 drift 被混在同一类报错里，破坏 `065` 和 `018` 已冻结的诚实输入模型

因此，`069` 的职责是先冻结 P1 governance diagnostics / drift truth；在 formal baseline 完成后，当前工单只允许唯一的首批 implementation slice，把该 truth 落到 model 与 artifact，而不是继续扩大到 `frontend_gate_verification`、`verify_constraints`、`frontend_contract_gate`、provider/runtime 或 root sync。

## 范围

- **覆盖**：
  - 将 P1 governance diagnostics / drift expansion 正式定义为 `066` 下游的独立 child work item
  - 锁定 P1 对 semantic component / recipe / state / whitelist / token diagnostics coverage 的最小扩张面
  - 锁定 `067 + 068 + 017 + 018 + 065` 的组合 truth 如何被 diagnostics / drift 反馈消费
  - 锁定 P1 drift / gap classification 与 compatibility feedback boundary
  - 为后续 `src/ai_sdlc/models/frontend_gate_policy.py`、`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py` 与对应测试切片提供 canonical baseline
  - 在 formal baseline 完成后，仅允许唯一的首批 implementation slice 将 diagnostics coverage matrix、drift classification 与 compatibility feedback boundary 落到 gate policy model / artifact generator / 定向 unit tests
- **不覆盖**：
  - 改写 `017` 已冻结的 generation truth、`018` 已冻结的 gate matrix / report family truth、或 `067/068` 已冻结的 kernel / recipe truth
  - 扩张 `frontend_gate_verification.py`、`verify_constraints.py`、`frontend_contract_gate.py`、CLI summary surface 或 integration tests
  - 抢跑 `070` recheck / remediation feedback、`071` visual / a11y、provider/runtime 映射、root `program-manifest.yaml` sync 或 `frontend-program-branch-rollout-plan.md`
  - 把 sample source self-check 写成运行时默认 observation fallback
  - 引入新的执行模式、第二套 report schema、第二套 compatibility 规则系统或完整 diagnostics runtime

## 已锁定决策

- `069` 是 P1 的 governance diagnostics / drift child work item，不是 recheck / remediation、visual / a11y 或 provider/runtime 工单
- `069` 必须消费 `067 + 068 + 017 + 018 + 065` 的组合 truth，而不是重新发明 kernel / recipe / generation / gate 语义
- P1 diagnostics 扩展重点包括更完整的 semantic component coverage、recipe coverage、state coverage、whitelist leakage 识别、token leakage 识别与 drift 分类
- Compatibility 仍是同一套 gate matrix 的兼容执行口径；`069` 不得把它重新表述为第二套 gate 或第二套规则集
- observation artifact 缺失属于 input gap，observation artifact 存在但 observations 为空属于 stable empty observation，存在结构或语义不匹配才属于 drift
- `069` formal baseline 已完成；当前唯一允许的实现批次是 Batch 5 diagnostics truth materialization slice，写面仅限 `src/ai_sdlc/models/frontend_gate_policy.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py`、`tests/unit/test_frontend_gate_policy_models.py`、`tests/unit/test_frontend_gate_policy_artifacts.py`
- 当前 implementation slice 不得修改 `src/ai_sdlc/core/frontend_gate_verification.py`、`src/ai_sdlc/core/verify_constraints.py`、`src/ai_sdlc/gates/frontend_contract_gate.py`，也不改 root truth 文件
- `069` 的当前状态必须被表达为 `accepted child baseline + first implementation slice in progress`，但这不代表 `070`、`071`、provider/runtime、root sync 或 close-ready 已开始

## 用户故事与验收

### US-069-1 — Governance Author 需要 P1 diagnostics 直接消费 expanded kernel / recipe truth

作为**治理作者**，我希望 P1 diagnostics / drift 扩展直接消费 `067` 和 `068` 已冻结的 truth，以便 semantic component / recipe / state / whitelist / token 反馈围绕统一的 `Ui*` 与 page recipe 语义工作，而不是围绕 provider 私有实现细节重写规则。

**验收**：

1. Given 我查看 `069` formal docs，When 我审阅 diagnostics coverage matrix，Then 可以直接读到 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` 与 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 的治理消费面
2. Given 我继续 formalize 或实现 diagnostics 相关切片，When 我读取 `069`，Then 可以明确知道 diagnostics 只能消费上游 truths，而不能反向改写 kernel / recipe baseline

### US-069-2 — Reviewer 需要确认 Compatibility 仍是同一套 gate matrix 的执行口径

作为**reviewer**，我希望 `069` 明确说明 P1 diagnostics 的 compatibility feedback 仍属于 `018` 已冻结的同一套 gate matrix，而不是额外生长出新的 compatibility gate。

**验收**：

1. Given 我查看 `069` formal docs，When 我检查 compatibility wording，Then 可以明确读到它只表达执行强度与反馈口径，不是第二套 gate system
2. Given 我查看 `069` formal docs，When 我检查当前 implementation slice 的 scope，Then 可以明确读到它只落在 gate policy model / artifact truth，不改 verify / gate runtime

### US-069-3 — Operator 需要诚实地区分 gap、empty 与 drift

作为**operator**，我希望 `069` 明确 observation input gap、稳定空 observations 与真实 drift 三者的诊断分类，以便 verify surface 不会把“缺输入”误报成“实现漂移”，也不会把“空结果”误报成“无事发生”。

**验收**：

1. Given 我查看 `069` formal docs，When 我检查 drift classification，Then 可以读到 `input gap != stable empty observation != drift`
2. Given 我读取本工单 implementation slice contract，When 我检查 artifact materialization 目标，Then 可以确认这些分类会先落到 gate policy artifacts，而不是直接侵入 runtime

## 功能需求

### Positioning And Truth Order

| ID | 需求 |
|----|------|
| FR-069-001 | `069` 必须作为 `066` 下游的 governance diagnostics / drift child work item 被正式定义 |
| FR-069-002 | `069` 必须明确只能消费 `067 + 068 + 017 + 018 + 065` 的组合 truth，不得反向改写 kernel / recipe / generation / gate baseline |
| FR-069-003 | `069` 必须明确 Compatibility 仍是 `018` 已冻结的 shared gate matrix 执行口径，而不是第二套规则系统或第二套 gate |
| FR-069-004 | `069` 必须明确当前 implementation slice 只放行 gate policy model / artifact truth materialization，不放行 verify / gate runtime 改写 |

### P1 Diagnostics Coverage Expansion

| ID | 需求 |
|----|------|
| FR-069-005 | `069` 必须冻结 P1 diagnostics coverage matrix，至少覆盖 semantic component coverage、page recipe coverage、state coverage、whitelist coverage 与 token rule coverage 五类面 |
| FR-069-006 | `069` 必须明确 semantic component coverage 消费 `067` 中的 `UiTabs / UiSearchBar / UiFilterBar / UiResult / UiSection / UiToolbar / UiPagination / UiCard` |
| FR-069-007 | `069` 必须明确 recipe coverage 消费 `068` 中的 `DashboardPage / DialogFormPage / SearchListPage / WizardPage` 标准本体及其 `required area / optional area / forbidden pattern` |
| FR-069-008 | `069` 必须明确 state coverage 至少覆盖 `refreshing`、`submitting`、`no-results`、`partial-error`、`success-feedback`，并继续与 `015` 的 MVP 状态基线共存 |
| FR-069-009 | `069` 必须明确 whitelist coverage 以 `017` 的 whitelist truth 为前提，P1 扩张重点是新增 `Ui*` 语义组件与新 recipe 组合下的入口合规，而不是扩大底层组件豁免 |
| FR-069-010 | `069` 必须明确 token rule coverage 仍以 `017` 的 minimal token / naked-value truth 为前提，P1 只扩细粒度的结构场景覆盖，不将其升级为完整 design token 平台 |
| FR-069-011 | `069` 必须明确 diagnostics 只能消费显式 observation artifact；sample source self-check 只作为 `065` 定义的显式输入源，不得成为运行时默认 observation 来源 |

### Drift Classification And Compatibility Feedback

| ID | 需求 |
|----|------|
| FR-069-012 | `069` 必须冻结 P1 drift / gap classification，至少区分 `input gap`、`stable empty observation`、`recipe structure drift`、`state expectation drift`、`whitelist leakage`、`token leakage` |
| FR-069-013 | `069` 必须明确 observation artifact 缺失时应暴露 `gap` 而不是 `drift`；observation artifact 存在但 observations 为空时，应暴露稳定空结果语义，而不是隐式转绿 |
| FR-069-014 | `069` 必须明确 drift / coverage feedback 继续复用 `018` 已冻结的 `Violation Report / Coverage Report / Drift Report / legacy expansion report` family，不得新增第二套 report schema |
| FR-069-015 | `069` 必须明确 compatibility feedback 只承接 `018` 的 `Strict / Incremental / Compatibility` 执行强度，不得在本工单中新增新的执行模式或第二套 compatibility 规则 |
| FR-069-016 | `069` 必须明确 compatibility feedback 可以影响 report severity、changed-scope 解释与 remediation hint，但不得改变上游 truth 或隐式放宽 kernel / recipe / whitelist / token 基线 |
| FR-069-017 | `069` 必须明确 drift diagnostics 的目标是暴露结构或语义偏差，而不是在本工单中直接定义 recheck loop 或自动修复动作 |

### Downstream Handoff And Rollout Honesty

| ID | 需求 |
|----|------|
| FR-069-018 | `069` 必须明确 `070` 承接 bounded remediation feedback、recheck 策略与作者体验闭环，不得在当前工单抢跑 |
| FR-069-019 | `069` 必须明确 `071` 承接 visual / a11y foundation，不得在当前工单抢跑截图、视觉回归或完整无障碍平台能力 |
| FR-069-020 | `069` 必须在 formal baseline 完成后允许唯一的 Batch 5 implementation slice，且写面仅限 `src/ai_sdlc/models/frontend_gate_policy.py`、`src/ai_sdlc/models/__init__.py`、`src/ai_sdlc/generators/frontend_gate_policy_artifacts.py`、`tests/unit/test_frontend_gate_policy_models.py`、`tests/unit/test_frontend_gate_policy_artifacts.py` |
| FR-069-021 | `069` 的当前 implementation slice 必须在 `018` shared gate truth 基础上 materialize diagnostics coverage matrix、drift classification 与 compatibility feedback boundary 的结构化 model / artifact truth |
| FR-069-022 | `069` 的当前 implementation slice 必须通过定向 RED/GREEN unit tests 证明 diagnostics truth 既可被 gate policy model 构造/校验，也可被 artifact payload 消费 |
| FR-069-023 | `069` 必须明确当前状态是 `accepted child baseline + first implementation slice in progress`，不生成 `development-summary.md`，也不宣称 `070`、`071`、provider/runtime、root sync 或 close-ready 已开始 |
| FR-069-024 | 当前 implementation slice 不得扩张到 `frontend_gate_verification.py`、`verify_constraints.py`、`frontend_contract_gate.py`、integration tests、CLI summary surface 或 root truth sync |

## 关键实体

- **P1 Diagnostics Coverage Matrix**：承载 semantic component / recipe / state / whitelist / token 五类 P1 diagnostics coverage 面
- **P1 Drift Classification Baseline**：承载 `input gap / stable empty observation / recipe structure drift / state expectation drift / whitelist leakage / token leakage` 的分类真值
- **Compatibility Feedback Boundary**：描述 `018` 的 shared gate modes 可以影响哪些反馈面，以及绝对不能修改哪些上游 truths
- **Observation Input Boundary**：描述 `065` sample self-check、外部 observation artifact 与 `069` diagnostics 之间的显式输入关系
- **Diagnostics-Recheck Handoff Boundary**：描述 `069` 与 `070` 之间“先诊断分类、后 remediation / recheck 体验”的消费关系

## P1 diagnostics coverage matrix

| Coverage 面 | Governed targets | Consumes truth from | 口径边界 |
|-------------|------------------|---------------------|----------|
| `Semantic Component Coverage` | `UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiResult`、`UiSection`、`UiToolbar`、`UiPagination`、`UiCard` | `067`、`018` | 只检查是否按受控语义入口与结构角色使用，不定义 provider 级实现 API |
| `Recipe Coverage` | `DashboardPage`、`DialogFormPage`、`SearchListPage`、`WizardPage` | `068`、`018` | 只消费 `required area / optional area / forbidden pattern`，不重写 recipe 标准本体 |
| `State Coverage` | `refreshing`、`submitting`、`no-results`、`partial-error`、`success-feedback` | `067`、`068`、`018` | 与 MVP `loading / empty / error / disabled / no-permission` 并存，不覆盖旧基线 |
| `Whitelist Coverage` | `UiTabs`、`UiSearchBar`、`UiFilterBar`、`UiResult`、`UiSection`、`UiToolbar`、`UiPagination`、`UiCard`、`DashboardPage`、`DialogFormPage`、`SearchListPage`、`WizardPage` | `017`、`067`、`068`、`018` | 重点检查绕过 `Ui*` 入口与 recipe 结构泄漏，不扩大底层组件默认豁免 |
| `Token Rule Coverage` | `DashboardPage`、`DialogFormPage`、`SearchListPage`、`WizardPage` | `017`、`068`、`018` | 仍是最小视觉控制面，只扩新结构场景覆盖，不升级为完整 token 平台 |

## P1 drift and gap classification

| 分类 | 触发条件 | 归属 report family | 诊断边界 |
|------|----------|--------------------|----------|
| `input gap` | 目标 `spec_dir` 缺少 observation artifact | `coverage-report` | 报告输入缺失，不得误报为 drift |
| `stable empty observation` | observation artifact 存在且 envelope 稳定，但 observations 为空 | `coverage-report` | 表示当前无可比对实现事实，不得隐式转绿 |
| `recipe structure drift` | 实现侧结构与 `required area / forbidden pattern` 明显偏离 | `drift-report` | 只消费已冻结 recipe truth，不重写 recipe |
| `state expectation drift` | P1 页面级状态语义缺失、误用或与 recipe 期望冲突 | `drift-report` | 只基于 `067 + 068` 的状态真值判断 |
| `whitelist leakage` | 绕过 `Ui*` 受控入口或越过白名单默认组件边界 | `violation-report` | 仍服从 `017` whitelist truth |
| `token leakage` | 出现裸视觉值、越过 token rule 边界或结构场景下的最小视觉失控 | `violation-report` | 仍服从 `017` minimal token truth |

## Compatibility feedback boundary

| Shared mode | 允许影响的反馈面 | 禁止修改的 truth |
|-------------|------------------|-------------------|
| `strict` | report severity、changed-scope wording、remediation hint | `kernel truth`、`recipe truth`、`whitelist truth`、`token truth` |
| `incremental` | report severity、changed-scope wording、remediation hint | `kernel truth`、`recipe truth`、`whitelist truth`、`token truth` |
| `compatibility` | report severity、changed-scope wording、remediation hint、legacy expansion context | `kernel truth`、`recipe truth`、`whitelist truth`、`token truth`、`second gate system` |

## 成功标准

- **SC-069-001**：`069` formal docs 能独立表达 P1 diagnostics / drift expansion 的 scope、coverage matrix、classification 与 compatibility feedback boundary，而无需回到 design 总览临时推断
- **SC-069-002**：后续 diagnostics 实现可以直接根据 `067 + 068 + 017 + 018 + 065` 读取 P1 治理消费面，而不会回退到 provider 私有命名
- **SC-069-003**：reviewer 能从 `069` 直接读出 `Compatibility != second gate system`
- **SC-069-004**：operator 能从 `069` 直接读出 `input gap != stable empty observation != drift`
- **SC-069-005**：reviewer 能从 `069` 直接读出当前 implementation slice 的唯一允许写面、验证方式与继续排除的 non-goals，而不需要回头依赖 `plan.md / tasks.md / task-execution-log.md` 反向推断顶层真值
- **SC-069-006**：`069` 当前状态被清楚表达为 `accepted child baseline + first implementation slice in progress`，不会被误读成 `070`、`071`、provider/runtime、root sync 或 close-ready 已开始
