# 功能规格：前端治理与 UI Kernel

**功能编号**：`009-frontend-governance-ui-kernel`  
**创建日期**：2026-04-02  
**状态**：已冻结（formal baseline）  
**输入**：[`../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`](../../docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md)、[`../../src/ai_sdlc/rules/pipeline.md`](../../src/ai_sdlc/rules/pipeline.md)、[`../../docs/USER_GUIDE.zh-CN.md`](../../docs/USER_GUIDE.zh-CN.md)

> 口径：本 work item 不是直接实现完整前端运行时，也不是把冻结设计再复制成第二套正文，而是把“前端治理与 UI Kernel”转成 framework 内可继续分解与执行的 canonical formal baseline。

## 范围

- **覆盖**：
  - 将前端治理与 UI Kernel 方案正式落为 `specs/009/...` 的 canonical truth
  - 锁定 `Contract / UI Kernel / enterprise-vue2 provider / 前端生成约束 / Gate-Recheck-Auto-fix` 五条主线的 formal 边界
  - 锁定现存项目的 legacy 治理口径：`Legacy Boundary + Compatibility Profile + Legacy Adapter + 同一套 gate matrix 的兼容执行口径`
  - 明确 `PRD/spec -> Contract -> code` 的前端真值顺序
  - 为后续 design / decompose / execute 提供可追溯、可拆分、可验证的 formal 基线
- **不覆盖**：
  - 直接实现 modern provider 运行时
  - 直接重构公司组件库或清理其全部历史源码
  - 在仓库中建设完整前端 runtime monorepo
  - 一次性完成所有 legacy 页面迁移
  - 把 `docs/superpowers/*` 继续当作法定执行真值

## 已锁定决策

- `UI Kernel != 公司组件库 != Provider`
- 公司组件库只能作为 `enterprise-vue2 provider` 的能力来源，被选择性包装、受控暴露和风险隔离
- `page recipe` 标准本体归 `UI Kernel`，`recipe declaration` 归 `Contract`
- `Compatibility` 不是第二套规则系统，也不是第二套 gate 体系，而是**同一套 gate matrix 的兼容执行口径**
- MVP 阶段 legacy 相关信息优先作为 `page/module contract` 的扩展字段承载，不引入独立平行 contract 体系
- legacy 允许存在，但所有新增与改动必须先收口，禁止继续扩散
- `Core / Provider / Runtime` 三层职责必须稳定，Provider 不得反向主导 Kernel

## 用户故事与验收

### US-009-1 — Framework Maintainer 需要单一 canonical 基线

作为**框架维护者**，我希望把冻结版前端治理与 UI Kernel 方案正式落为 `specs/009/...` 的 canonical formal 文档，以便后续需求拆解、实现与验证都围绕同一套真值展开，而不是继续停留在 design input 层。

**验收**：

1. Given 已有冻结设计稿，When formalize 为 `009`，Then `spec.md / plan.md / tasks.md` 可以独立描述后续执行边界  
2. Given `009` 已创建，When 后续 review / decompose / execute 引用该能力，Then 不再要求回到 `docs/superpowers/*` 作为法定执行入口

### US-009-2 — Reviewer 需要清晰的 legacy 治理边界

作为**reviewer**，我希望在 formal work item 中看到现存项目兼容策略、Compatibility 口径和 Legacy Adapter 边界被正式写死，以便后续实现不会在 legacy 线上再次摇摆。

**验收**：

1. Given 现存项目场景，When 审阅 `009` formal docs，Then 可以明确读到 `存量兼容、增量收口、边界隔离、渐进迁移` 的统一策略  
2. Given legacy 相关设计，When 审阅 `009` formal docs，Then 不会把 Compatibility 理解成第二套规则或第二套 gate 体系

### US-009-3 — Operator 需要可继续拆解的 formal 入口

作为**operator**，我希望 `009` formal docs 不只是冻结设计的副本，而是已经按 framework 约束收敛成可继续拆解、可继续 verify 的 work item，以便下一步能直接进入规范化 design/decompose 路径。

**验收**：

1. Given `009` 的 formal docs，When 进入下一轮 design/decompose，Then 可以直接基于 `spec.md / plan.md / tasks.md` 继续拆解  
2. Given `009` formal docs，When 运行只读校验，Then 不会因为双轨真值或术语漂移而产生歧义

## 功能需求

### Formal Truth And Scope

| ID | 需求 |
|----|------|
| FR-009-001 | 系统必须把冻结版前端治理与 UI Kernel 方案转为 `specs/009/...` 下的 canonical formal truth |
| FR-009-002 | `009` 必须明确覆盖 `Contract / UI Kernel / enterprise-vue2 provider / 前端生成约束 / Gate-Recheck-Auto-fix` 五条主线 |
| FR-009-003 | `009` 必须明确本次 work item 的非目标，包括 modern provider runtime、完整 design token 平台、公司组件库全面重构和全量 legacy 迁移 |

### Contract And Kernel Boundary

| ID | 需求 |
|----|------|
| FR-009-004 | `009` 必须锁定 `PRD/spec -> Contract -> code` 的前端真值顺序，并明确 gate 以 Contract 与代码对照，不以 prompt 为准 |
| FR-009-005 | `009` 必须明确 `page recipe` 标准本体归 UI Kernel，`recipe declaration` 归 Contract，且两者不得混写 |
| FR-009-006 | `009` 必须明确 `Ui*` 协议、状态/交互底线与 Theme/Token 边界，为后续 Provider 与 Gate 提供标准本体 |

### Provider And Legacy Strategy

| ID | 需求 |
|----|------|
| FR-009-007 | `009` 必须明确公司组件库只能作为 `enterprise-vue2 provider` 的能力来源，不得直接充当 UI Kernel 或 AI 默认入口 |
| FR-009-008 | `009` 必须明确 Legacy Adapter 是受控桥接层，不是长期默认入口 |
| FR-009-009 | `009` 必须明确对现存项目采取“存量兼容、增量收口、边界隔离、渐进迁移”的治理策略 |
| FR-009-010 | `009` 必须明确 Compatibility 是同一套 gate matrix 的兼容执行口径，而不是第二套规则系统或第二套 gate 体系 |

### Execution Handoff

| ID | 需求 |
|----|------|
| FR-009-011 | `009` 必须把 legacy 相关信息的 MVP 承载方式收敛为 `page/module contract` 扩展字段优先，而不是独立平行 artifact 爆炸 |
| FR-009-012 | `009` 必须输出可继续拆解的 formal `plan.md / tasks.md`，为后续 design/decompose/verify 提供单一基线 |
| FR-009-013 | `009` 必须把五条主线冻结为可单独引用的 formal execution surface，并写清各自的边界、输入真值和后续 handoff 目标 |
| FR-009-014 | `009` 必须明确 `MVP / P1 / P2` 的交付分层，其中 MVP 只覆盖 `Vue2 企业项目 + 最小治理闭环 + legacy 轻量兼容`，不得把 modern provider 路线偷渡进 MVP |
| FR-009-015 | `009` 必须明确后续任何 `src/` / `tests/` 级实现，都应通过下游 child work item 或单独 formalize 的执行工单承接，而不是把 `009` 直接膨胀成运行时实现工单 |

## 关键实体

- **Frontend Contract Set**：承载 `page metadata / recipe declaration / i18n / validation / hard rules / whitelist / token refs` 的结构化真值集合
- **UI Kernel Standard Body**：承载 `Ui*` 协议、page recipe 标准本体、状态与交互底线的标准层
- **enterprise-vue2 Provider Profile**：承载 `Ui* -> 企业实现` 映射、白名单包装、危险能力隔离与 Legacy Adapter 边界的实现层
- **Compatibility Context**：承载 `Compatibility Profile / Migration Level / Migration Scope / Legacy Boundary` 的兼容治理上下文
- **Gate Matrix**：承载 `i18n / validation / recipe / whitelist / hard rules / token` 统一检查基线及其兼容执行口径

## 五条主 workstream

| Workstream | 当前 formal 边界 | 输入真值 | `009` 内冻结内容 | 明确不在 `009` 内直接实现 |
|------------|------------------|----------|------------------|---------------------------|
| Contract | `page/module metadata`、`recipe declaration`、`i18n / validation / hard rules / whitelist / token refs`、legacy 扩展字段 | `PRD/spec`、治理规则、domain requirement | 前端 contract shape、legacy 扩展字段承载规则、authoring truth order | 页面生成器、运行时 adapter、批量迁移器 |
| UI Kernel | `Ui*` 协议、`page recipe standard body`、状态/交互底线、Theme/Token 边界 | Contract、设计冻结稿 | Kernel 标准本体、禁止 Provider 反向定义 Kernel 的边界 | 公司组件库直出、企业样式实现、modern runtime |
| enterprise-vue2 Provider | `Ui* -> 企业实现` 映射、白名单包装、危险能力隔离、Legacy Adapter 边界 | UI Kernel、公司组件库能力盘点、Compatibility Context | Provider profile、Legacy Adapter 受控桥接口径 | modern provider runtime、全量组件库重构 |
| 前端生成约束 | 生成器输出纪律、文件/组件白名单、recipe 对齐、Contract 到代码的最小产物约束 | Contract、UI Kernel、Provider profile | 生成约束的 formal baseline、不得以 prompt 替代 contract 的规则 | 完整生成器 runtime、自主推断业务逻辑 |
| Gate-Recheck-Auto-fix | gate matrix、Compatibility 执行强度、diagnostics、recheck loop、bounded auto-fix policy | Contract、代码、Provider profile、Compatibility Context | 同一套 gate matrix 的兼容执行口径、recheck / auto-fix 的边界 | 第二套 compatibility rule system、隐式自修复 runtime |

`009` 的职责是把以上五条主线冻结为后续可拆分、可 formalize、可 verify 的 execution surface，而不是在当前 work item 中直接落 `src/` / `tests/` 级实现。

## 交付分层（MVP / P1 / P2）

| 层级 | 目标 | 明确覆盖 | 明确不覆盖 |
|------|------|----------|------------|
| MVP | 建立 `Vue2 企业项目 + 最小治理闭环 + legacy 轻量兼容` 的首个可执行治理基线 | Contract 基础形状、UI Kernel 标准本体、enterprise-vue2 Provider profile、Compatibility Context、同一套 gate matrix 下的兼容执行口径 | modern provider runtime、全量 token 平台、全量 legacy 迁移、终局体验层 |
| P1 | 在 MVP 真值不变的前提下补强体验稳定层与诊断能力 | 更完整的 recipe / gate diagnostics / recheck 策略、作者体验与治理反馈面 | 第二套 Contract / Kernel、本地 prompt truth |
| P2 | 承接 modern provider 路线与更强迁移能力 | modern provider、设计 token 平台、迁移加速器、多 provider/runtime 演进 | 回写或改写 MVP 的单一真值顺序 |

## Formal 真值顺序与执行前提

1. `PRD/spec` 定义业务意图、页面目标和治理边界。
2. `Contract` 将这些意图收敛成结构化真值，包括 `recipe declaration`、规则、扩展字段和允许的生成输入。
3. `code / provider / runtime` 只能实现并满足 Contract，不得反向改写 Contract。
4. Gate 以 `Contract <-> code` 对照为准，prompt、对话和临时推断都不是法定真值。
5. `009` 当前只授权 formal freeze、design/decompose 和 verify handoff；任何后续 `src/` / `tests/` 实现必须先挂到新的 downstream work item，再进入 execute。

## Verify / Decompose Handoff

- 下一轮 design / decompose 的法定入口固定为 `specs/009-frontend-governance-ui-kernel/`，不回退到 `docs/superpowers/*`。
- 推荐的只读 handoff 基线是：`uv run ai-sdlc verify constraints`、`uv run ai-sdlc workitem truth-check --wi specs/009-frontend-governance-ui-kernel`、`git status --short`。
- 若要进入 `src/` / `tests/` 实现，应先围绕五条主线拆出 downstream child work item，并在其 `spec.md / plan.md / tasks.md` 中明确回挂 `009`。
- `009` 自身保留为母规格与 formal governance baseline；后续实现不应再把它改写成“直接承载完整运行时”的工单。

## 成功标准

- **SC-009-001**：`009` formal docs 可以独立表达前端治理与 UI Kernel 的核心边界，而不是仅依赖冻结设计稿正文  
- **SC-009-002**：全文对 legacy 的统一口径保持单一：legacy 允许存在，但新增与改动必须先收口，禁止继续扩散  
- **SC-009-003**：`Compatibility` 在 formal docs 中始终被表述为同一套 gate matrix 的兼容执行口径  
- **SC-009-004**：`recipe standard` 与 `recipe declaration`、`Kernel` 与 `Provider`、`Core` 与 `Runtime` 的边界在 formal docs 中保持单一真值  
- **SC-009-005**：`009` formal docs 足以支撑后续 design/decompose 继续细化，而无需再回到 `docs/superpowers/*` 建第二套 canonical 文档
- **SC-009-006**：五条主 workstream 都能被独立引用，并能清楚回答“边界是什么、输入真值是什么、后续应由哪个下游工单承接”
- **SC-009-007**：MVP / P1 / P2 的边界保持单一，MVP 不再被表述成“首版即终局能力”
- **SC-009-008**：后续任何实现任务都必须显式回挂到 `009` 的下游 work item，而不是绕过 formalize 直接扩张 `009`
