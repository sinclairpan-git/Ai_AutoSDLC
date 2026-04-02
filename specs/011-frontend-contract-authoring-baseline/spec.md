# 功能规格：Frontend Contract Authoring Baseline

**功能编号**：`011-frontend-contract-authoring-baseline`  
**创建日期**：2026-04-02  
**状态**：已冻结（formal baseline）  
**输入**：[`../009-frontend-governance-ui-kernel/spec.md`](../009-frontend-governance-ui-kernel/spec.md)、[`../009-frontend-governance-ui-kernel/plan.md`](../009-frontend-governance-ui-kernel/plan.md)、[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)

> 口径：本 work item 是 `009-frontend-governance-ui-kernel` 下游的第一个 child work item，用于把 `Contract` 主线收敛成单一 formal baseline。它不是 UI Kernel、Provider 或 Gate 的替代实现，也不是直接建设完整前端 runtime，而是先把 Contract 真值面、artifact 链路、legacy 扩展字段和 drift 口径正式冻结。

## 问题定义

`009` 已经把前端治理方案收敛为五条主 workstream，但 `Contract` 这条线尚未被单独 formalize 成可继续实现的 child work item。若继续直接进入页面生成、Kernel 标准层或 Provider 包装实现，会同时出现三类风险：

- `recipe declaration`、`i18n / validation / whitelist / token rules` 等对象继续混在 prompt 或临时 Markdown 说明里，没有单一结构化真值
- `Contract / Kernel / Provider / Gate` 的职责会被重新混写，后续实现很容易在“页面该声明什么”与“标准本体是什么”之间反复摇摆
- 存量项目需要的 `compatibility_profile / migration_level / legacy_boundary_ref / migration_scope` 等信息没有正式承载面，只能退回平行 artifact 或口头约定

因此，本 work item 要先解决的不是“生成页面代码”，而是：

- Contract 到底承载哪些对象
- Contract 如何进入现有 `refine / design / decompose / verify / execute / close` artifact 链路
- Contract 与 UI Kernel、Provider、Gate 的硬边界是什么
- legacy 与 compatibility 信息在 MVP 阶段如何以扩展字段方式受控落位

## 范围

- **覆盖**：
  - 将 `009` 中的 `Contract` 主线正式落为 `specs/011/...` 的 canonical formal truth
  - 锁定 `page/module metadata`、`recipe declaration`、`i18n`、`validation`、`hard rules`、`whitelist`、`token refs/rules`、legacy 扩展字段的 Contract 边界
  - 锁定 Contract 在 `refine / design / decompose / verify / execute / close` 中的 artifact 链路位置
  - 锁定 `Contract drift` 的正式处理口径：`回写 Contract` 或 `修正实现代码`
  - 锁定 MVP 阶段 legacy 相关信息以 `page/module contract` 扩展字段承载的单一路径
  - 为后续模型、实例化、序列化、drift 检查与验证测试提供 formal baseline
- **不覆盖**：
  - 定义 `Ui*` 协议、page recipe 标准本体和状态/交互底线
  - 定义 `enterprise-vue2 provider` 的映射、wrapper 或 runtime 包装
  - 定义 Gate / Recheck / Auto-fix 的完整策略与执行实现
  - 直接实现页面生成 runtime、完整 schema 引擎或前端 monorepo
  - 为 legacy 再建立第二套平行 contract / artifact 体系

## 已锁定决策

- Contract 是**实例化 artifact**，不是补充性文档
- `page recipe` 标准本体归 `UI Kernel`，Contract 只承载 `recipe declaration`
- `i18n / validation / hard rules / whitelist / token rules` 是 MVP 首批必须进入 Contract 的对象
- Contract 必须同时服务于生成、检查与修复，而不是只服务于生成
- legacy 迁移相关信息在 MVP 优先以 `page/module contract` 扩展字段承载，不另起平行 artifact
- Contract 必须接入现有 Ai_AutoSDLC 的 artifact 链路，而不是另起独立前端流水线
- Contract 漂移不能长期存在；发现漂移后只能 `回写 Contract` 或 `修正实现代码`

## 用户故事与验收

### US-011-1 — Framework Maintainer 需要单一的 Contract 真值面

作为**框架维护者**，我希望把 `Contract` 主线从 `009` 母规格中拆成单独 child work item，以便后续模型、实例化、验证和修复都围绕一套结构化 Contract 真值展开，而不是继续混在 prompt 或散落文档中。

**验收**：

1. Given `011` formal docs 已冻结，When 后续实现 Frontend Contract Set，Then 可直接根据 `spec.md / plan.md / tasks.md` 确定 Contract 的边界与输入对象  
2. Given `011` 已创建，When 后续 review / decompose / verify 引用该能力，Then 不再要求回到 `009` 或设计稿临时解释 Contract 的具体承载面

### US-011-2 — Reviewer 需要清晰的 Contract / Kernel / Provider 边界

作为**reviewer**，我希望在 `011` 中清楚看到 Contract 与 UI Kernel、Provider、Gate 的职责边界，以便后续实现不会把 `recipe declaration` 和 `recipe standard body`、结构化规则与运行时包装混写。

**验收**：

1. Given 我审阅 `011` formal docs，When 我检查 `recipe declaration` 的归属，Then 可以明确读到它属于 Contract，而不是 UI Kernel 标准本体  
2. Given 我审阅 `011` formal docs，When 我检查 Contract 的职责，Then 不会把 Provider 映射、Kernel 标准层或 Gate 诊断面误读成 Contract 的一部分

### US-011-3 — Operator 需要 Contract 能进入 artifact 链路

作为**operator**，我希望 `Contract` 不只是“生成前的说明”，而是可以进入现有 `refine / design / decompose / verify / execute / close` 链路的正式 artifact，以便生成、检查和回修都基于同一真值运行。

**验收**：

1. Given `011` formal docs，When 我查看 stage 关系，Then 可以明确看到 Contract 在 `refine / design / decompose / verify / execute / close` 中的落位  
2. Given 发现 Contract 与代码不一致，When 我查看 `011` formal docs，Then 可以明确看到只能选择 `回写 Contract` 或 `修正实现代码` 的 drift 处理口径

## 功能需求

### Formal Truth And Scope

| ID | 需求 |
|----|------|
| FR-011-001 | 系统必须把 `009` 的 `Contract` 主线转为 `specs/011/...` 下的 canonical formal truth |
| FR-011-002 | `011` 必须明确覆盖 `page/module metadata`、`recipe declaration`、`i18n`、`validation`、`hard rules`、`whitelist`、`token refs/rules` 与 legacy 扩展字段 |
| FR-011-003 | `011` 必须明确本次 work item 的非目标，包括 UI Kernel 标准本体、Provider 映射、Gate / Recheck / Auto-fix 实现与完整前端 runtime |

### Contract Object Model And Boundary

| ID | 需求 |
|----|------|
| FR-011-004 | `011` 必须明确 `Frontend Contract Set` 是实例化 artifact，不是补充性文档 |
| FR-011-005 | `011` 必须明确 `page contract` 与 `module contract` 是 MVP 阶段的主要承载单元 |
| FR-011-006 | `011` 必须明确 `page recipe` 标准本体归 UI Kernel，Contract 只承载 `recipe declaration` |
| FR-011-007 | `011` 必须明确 `i18n / validation / hard rules / whitelist / token rules` 是 MVP 首批 Contract 对象 |
| FR-011-008 | `011` 必须明确受控例外、特殊豁免和边界声明必须作为结构化 Contract 字段存在，而不是停留在自由文本 prompt 中 |

### Artifact Chain And Drift Control

| ID | 需求 |
|----|------|
| FR-011-009 | `011` 必须明确 Contract 接入现有 `refine / design / decompose / verify / execute / close` artifact 链路，而不是另起平行前端流水线 |
| FR-011-010 | `011` 必须明确 `decompose`、`verify` 与后续 Gate 以 Contract 与代码对照，不以 prompt 为准 |
| FR-011-011 | `011` 必须明确 Contract 漂移处理只能在 `回写 Contract` 与 `修正实现代码` 之间二选一 |
| FR-011-012 | `011` 必须明确 Contract 同时服务于生成、检查与修复，不得退化成只服务于生成的临时输入 |

### Legacy Extension And Implementation Handoff

| ID | 需求 |
|----|------|
| FR-011-013 | `011` 必须明确 `compatibility_profile / migration_level / legacy_boundary_ref / migration_scope` 等 legacy 信息优先作为 `page/module contract` 扩展字段承载 |
| FR-011-014 | `011` 必须为后续 Contract 模型、实例化、序列化与 drift 检查实现提供单一 formal baseline |
| FR-011-015 | `011` 必须明确后续实现的最小验证面至少覆盖模型形状、序列化、stage integration、legacy 扩展字段和 drift 正反向场景 |

## 关键实体

- **Frontend Contract Set**：承载一个 capability 下全部 `page/module contract` 的结构化真值集合
- **Page Contract**：承载页面级 `metadata`、`recipe declaration`、规则、例外与 legacy 扩展字段的主 artifact
- **Module Contract**：承载模块级或复用片段级约束，使 Contract 不必退化成“只支持整页”的粗粒度对象
- **Contract Rule Bundle**：承载 `i18n / validation / hard rules / whitelist / token rules` 的结构化规则集合
- **Contract Legacy Context**：承载 `compatibility_profile / migration_level / legacy_boundary_ref / migration_scope` 等存量治理上下文
- **Contract Drift Record**：承载 Contract 与实现之间的偏差类型、定位、处理方式与回写结论

## 成功标准

- **SC-011-001**：`011` formal docs 可以独立表达 Contract 主线的边界，而无需再次回到 `009` 母规格正文解释
- **SC-011-002**：`recipe declaration` 与 `recipe standard body`、Contract 与 Kernel、Contract 与 Provider 的边界在全文保持单一真值
- **SC-011-003**：`i18n / validation / hard rules / whitelist / token rules` 都被明确纳入 MVP Contract 对象，而不是继续停留在 prompt 或散落规则描述中
- **SC-011-004**：legacy 相关信息始终作为 `page/module contract` 扩展字段承载，不形成第二套平行 contract / artifact 系统
- **SC-011-005**：`refine / design / decompose / verify / execute / close` 与 Contract 的关系在 formal docs 中可被直接引用
- **SC-011-006**：后续实现团队能够从 `011` 直接读出模型、实例化、drift 检查和测试面的最小边界，而不需要重新发明对象模型
