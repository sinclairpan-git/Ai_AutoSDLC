# 实施计划：Direct Formal Work Item Entry

**编号**：`008-direct-formal-workitem-entry` | **日期**：2026-03-31 | **规格**：specs/008-direct-formal-workitem-entry/spec.md

## 概述

本计划的目标不是再给 `docs/superpowers/*` 增加一层“formalize 后再复制”的流程，而是把新 framework capability 的默认入口改成 direct-to-formal：一开始就落 `specs/<WI>/spec.md + plan.md + tasks.md`，并通过 CLI scaffold、模板复用与规则文档同步，把这条路径做成 canonical default。

本计划默认保持 **single canonical doc set**。external design docs 可以继续存在，但只能被 formal docs 引用，不能再要求重复搬运为另一套 canonical 正文。

## 技术背景

**语言/版本**：Python 3.11+  
**主要依赖**：Typer、Pathlib、现有 Markdown templates、pytest  
**现有基础**：仓库已有 `templates/spec-template.md`、`templates/plan-template.md`、`templates/tasks-template.md`；`workitem_cmd.py` 已承载 `plan-check / close-check / branch-check / link` 子命令；`pipeline.md` 与用户约定已明确 `docs/superpowers/*` 只是 design input  
**目标平台**：框架仓库自迭代主路径  
**主要约束**：
- 不能再把 `docs/superpowers/*` 当作 canonical save path
- direct-formal scaffold 必须复用现有模板
- 不修改宿主 skill 仓库本体
- 不自动迁移历史双轨文档

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| MUST-1 MVP 优先 | 首期只做 direct-formal scaffold、规则/文档口径与最小 CLI discoverability |
| MUST-2 关键路径可验证 | scaffold、parser-friendly output、规则/文档一致性都要有 focused tests |
| MUST-3 范围声明与回退 | 不做历史迁移、不改宿主 skill 仓库、不碰 execute 逻辑 |
| MUST-4 状态落盘 | formal work item 从一开始就落到 `specs/<WI>/`，减少口头或外部文档真值 |
| MUST-5 产品代码隔离 | CLI scaffold、核心 helper、规则文档和用户文档分层实现 |

## 项目结构

### 文档结构

```text
specs/008-direct-formal-workitem-entry/
├── spec.md
├── plan.md
└── tasks.md
```

### 源码结构

```text
src/ai_sdlc/
├── cli/
│   ├── workitem_cmd.py            # add direct-formal scaffold/init command
│   ├── main.py                    # register/update command discovery if needed
│   └── command_names.py           # keep flat command list aligned
├── core/
│   └── workitem_scaffold.py       # new helper for parser-friendly formal doc init
└── rules/
    └── pipeline.md                # canonical direct-formal entry wording

templates/
├── spec-template.md
├── plan-template.md
└── tasks-template.md
```

## 开始编码前必须锁定的阻断决策

- new framework capability 的 canonical docs 直接位于 `specs/<WI>/`
- external design docs 只能作为 reference，不是第二 canonical set
- scaffold/init 复用现有模板，不另造模板树
- 不要求先写 `docs/superpowers/*`
- 不修改宿主 skill 仓库

未锁定上述决策前，不得进入 scaffold 实现 task。

## Owner Boundaries

| Owner Area | Responsibility | Forbidden Cross-Layer Writes |
| --- | --- | --- |
| rules/docs | direct-formal canonical path、reference-only semantics、operator wording | 不得重新把 `docs/superpowers/*` 写回 canonical truth |
| scaffold helper | 生成 parser-friendly formal docs skeleton、处理引用挂接 | 不得擅自生成 execute truth 或 execution log 内容 |
| CLI surface | 暴露 `workitem init` 或等价 direct-formal 命令 | 不得写第二套设计文档路径 |
| regression | focused scaffold tests、doc/command consistency | 不得扩大到宿主 skill 仓库改造 |

## 阶段计划

### Phase 0：Formal work item freeze

**目标**：把 direct-to-formal 方案本身落成正式 `008` work item 真值。  
**产物**：`spec.md`、`plan.md`、`tasks.md`。  
**验证方式**：文档对账 + `verify constraints`。  
**回退方式**：只改 formal docs。

### Phase 1：Canonical path policy freeze

**目标**：把 direct-formal entry path 与 reference-only semantics 固化到规则和用户文档。  
**产物**：`pipeline.md`、用户约定、用户手册。  
**验证方式**：规则文档对账。  
**回退方式**：不触发 CLI 行为改动。

### Phase 2：Direct-formal scaffold helper

**目标**：新增 work item scaffold helper，直接用模板生成 `spec.md / plan.md / tasks.md`。  
**产物**：`core/workitem_scaffold.py`、模板挂接、focused tests。  
**验证方式**：helper unit tests。  
**回退方式**：未进入 CLI 前不影响已有命令。

### Phase 3：CLI discoverability

**目标**：通过 `workitem init` 或等价入口把 direct-formal scaffold 暴露给 operator。  
**产物**：`cli/workitem_cmd.py`、`command_names.py`、integration tests。  
**验证方式**：CLI scaffold integration tests。  
**回退方式**：命令可先实验性存在，但不能写第二套 canonical docs。

### Phase 4：Docs + regression close-out

**目标**：统一 docs、rules、CLI examples，并用 focused tests 与 repo read-only verification 收口。  
**产物**：文档、focused tests、final verification evidence。  
**验证方式**：focused scaffold suite + `verify constraints`。  
**回退方式**：不碰 execute 阶段行为。

## 工作流计划

### 工作流 A：Policy before tooling

**范围**：canonical path 与 reference-only 语义  
**影响范围**：`pipeline.md`、自迭代约定、用户文档  
**验证方式**：文档对账  
**回退方式**：未完成 policy 前，不提供 scaffold CLI

### 工作流 B：Scaffold before discoverability

**范围**：helper、模板复用、parser-friendly skeleton  
**影响范围**：`core/workitem_scaffold.py`、templates、unit tests  
**验证方式**：focused unit tests  
**回退方式**：未稳定生成 formal docs 前，不注册 CLI

### 工作流 C：CLI after skeleton stability

**范围**：`workitem init`、command discovery、examples  
**影响范围**：`cli/workitem_cmd.py`、`command_names.py`、integration tests、用户文档  
**验证方式**：CLI integration tests  
**回退方式**：不写第二套 docs

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| direct-formal policy | `uv run ai-sdlc verify constraints` | docs/rules diff review |
| scaffold helper | focused unit tests | generated file snapshot assertions |
| CLI init command | focused integration tests | command discovery assertions |
| final rollout | focused scaffold suite | `uv run ai-sdlc verify constraints` |

## 已锁定决策

- direct-formal is the default canonical path
- external design docs are references only
- no host skill repo modification in this work item
- no historical mass migration
- no second canonical doc set

## 实施顺序建议

1. 先冻结 `008` formal 文档，避免又先走一轮外部 design doc。
2. 先固化 canonical path 规则，再做 scaffold helper。
3. helper 稳定后，再通过 CLI 暴露 direct-formal entry。
4. 最后统一 docs/examples/tests，确认仓库不再把 `docs/superpowers/*` 当默认最终落点。
