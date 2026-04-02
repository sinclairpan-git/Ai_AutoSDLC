---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：前端治理与 UI Kernel

**编号**：`009-frontend-governance-ui-kernel` | **日期**：2026-04-02 | **规格**：specs/009-frontend-governance-ui-kernel/spec.md

## 概述

本计划当前不进入代码实现，而是把冻结版“前端治理与 UI Kernel”方案转为 framework 内的 canonical formal baseline。它要完成的不是新做一套运行时，而是把后续实现所需的真值顺序、边界、legacy 治理策略、执行口径和拆解顺序正式落到 `specs/009/...`。

该计划默认保持 **single canonical formal truth**：`docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md` 作为 reference-only design input，后续 design / decompose / verify / execute 以 `specs/009/...` 为法定入口。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：现有 `ai-sdlc` pipeline、`specs/<WI>/` canonical docs、仓库 rules/guide 约束  
**现有基础**：
- 冻结版设计文档已归档到 `docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md`
- 仓库已完成 AI-SDLC formal init，可使用 direct-formal work item 路径
- `008-direct-formal-workitem-entry` 已明确 `docs/superpowers/*` 只是 design input，不能替代 `specs/<WI>/`

**目标平台**：AI-SDLC 框架仓库自身，面向后续 design/decompose/execute 的 canonical 文档真值  
**主要约束**：
- 不把当前 work item 直接膨胀成完整前端 runtime 实现
- 不把 Compatibility 写成第二套规则/第二套 gate
- 不把 legacy artifact 做成 MVP 平行 contract 系统
- 不把公司组件库、Provider 或 Wrapper 混写成 UI Kernel
- 不绕过 formal docs，继续把 `docs/superpowers/*` 当 canonical truth

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 当前阶段只完成 canonical formal baseline 与可继续拆解的任务分批，不直接进入完整实现 |
| MUST-2 关键路径可验证 | formal docs 需可被只读校验、可被后续 verify/decompose 消费 |
| MUST-3 范围声明与回退 | 明确覆盖/不覆盖，保持单一文档基线，所有变更仅作用于本 work item formal docs |
| MUST-4 状态落盘 | design input 已归档，formal truth 落到 `specs/009/...`，避免继续依赖对话或外部草稿 |
| MUST-5 产品代码与开发框架隔离 | 当前阶段只处理 framework formal docs 与规则边界，不在仓库中引入前端 runtime 实现 |

## 项目结构

### 文档结构

```text
specs/009-frontend-governance-ui-kernel/
├── spec.md
├── plan.md
└── tasks.md
```

### 后续实现涉及的主要代码/规则面

```text
src/ai_sdlc/
├── models/           # frontend contract / compatibility context 模型（后续）
├── gates/            # frontend gate matrix / compatibility execution policy（后续）
├── core/             # contract drift / fix loop orchestration（后续）
└── rules/            # frontend governance / pipeline wording（后续）

docs/
├── USER_GUIDE.zh-CN.md
└── 框架自迭代开发与发布约定.md
```

## 开始执行前必须锁定的阻断决策

- `UI Kernel != Provider != 公司组件库`
- `recipe standard body != recipe declaration`
- `Compatibility` 只是**同一套 gate matrix 的兼容执行口径**
- legacy 信息在 MVP 优先以 `page/module contract` 扩展字段承载
- legacy 允许存在，但新增与改动必须先收口，禁止继续扩散
- `docs/superpowers/*` 是 reference-only design input，不是 execute truth

未锁定上述决策前，不得进入该能力的代码实现任务。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| formal docs | 锁定 scope、truth order、legacy policy、execution baseline | 不得把 frozen design 再复制成第二套 canonical 内容 |
| future contract surface | 定义 frontend contract / compatibility context 标准结构 | 不得在未锁定 spec 前直接实现代码 surface |
| future kernel/provider surface | 定义 Kernel / Provider / legacy adapter 的标准与边界 | 不得由 Provider 或公司组件库反向主导 Kernel |
| future gate surface | 定义 gate matrix、compatibility execution policy、report/fix truth | 不得新增第二套 compatibility rules 或第二套 gate system |

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：把冻结版设计转为 canonical formal `spec.md / plan.md / tasks.md`。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/009/...` 文档改动。

### Phase 1：Workstream slicing

**目标**：把大方案拆成可继续执行的五条 workstream。  
**产物**：任务分批、scope matrix、legacy/compatibility baseline。  
**验证方式**：`tasks.md` 与 `spec.md / plan.md` 对账。  
**回退方式**：不触发代码实现。

### Phase 2：Execution handoff baseline

**目标**：为后续 design/decompose/verify 阶段提供统一执行前提和只读验证基线。  
**产物**：执行顺序、验证命令、下一阶段前置约束。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

## 工作流计划

### 工作流 A：Single canonical truth freeze

**范围**：formal docs、related_doc 挂接、truth order。  
**影响范围**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：formal docs 对账。  
**回退方式**：不影响任何产品代码。

### 工作流 B：Frontend governance workstream slicing

**范围**：Contract、UI Kernel、Provider、生成约束、Gate/Compatibility 五条主线的拆分。  
**影响范围**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：scope matrix 与 batch 依赖对账。  
**回退方式**：不进入 execute。

### 工作流 C：Legacy strategy freeze

**范围**：Legacy Boundary、Compatibility Profile、Migration Level、Migration Scope、Legacy Adapter 的 formal 口径。  
**影响范围**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：术语一致性和优先级边界对账。  
**回退方式**：不影响既有 runtime。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| formal single truth | 文档对账 | `uv run ai-sdlc verify constraints` |
| legacy policy consistency | 术语与口径搜索 | 人工审阅 |
| recipe / contract / provider 边界 | `spec.md / plan.md / tasks.md` 交叉引用检查 | 人工审阅 |
| next-step readiness | tasks batch / dependency review | `git status --short` |

## 已锁定决策

- 当前 work item 先完成 canonical formal baseline，不直接进入实现
- 冻结设计稿只作为 reference-only input
- 后续实现必须以 `specs/009/...` 为入口，不得反向依赖 `docs/superpowers/*`
- Compatibility 只描述执行强度差异，不描述独立规则集合
- legacy 相关 MVP 信息优先轻量承载，不引入 artifact 爆炸

## 实施顺序建议

1. 先冻结 `009` formal spec/plan/tasks，避免 canonical truth 继续缺位。
2. 再将大方案收敛为五条 workstream：Contract、UI Kernel、enterprise-vue2 Provider、前端生成约束、Gate/Compatibility。
3. 再把 legacy 线织入这些 workstream，确保它不是附会补丁而是内建边界。
4. 完成 formal baseline 校验后，再决定后续是继续在 `009` 下执行，还是拆成更细的 implementation work item。
