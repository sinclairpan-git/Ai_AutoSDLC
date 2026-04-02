---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/015-frontend-ui-kernel-standard-baseline/spec.md"
  - "specs/016-frontend-enterprise-vue2-provider-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Generation Governance Baseline

**编号**：`017-frontend-generation-governance-baseline` | **日期**：2026-04-03 | **规格**：specs/017-frontend-generation-governance-baseline/spec.md

## 概述

本计划处理的是 `009` 下游的“前端生成约束” formal baseline，而不是直接实现完整生成 runtime。当前仓库已经在上游锁定并实现了：

- `011`：frontend contract 基础形状与 verify 主链
- `015`：UI Kernel standard body、models 与 artifact
- `016`：enterprise-vue2 Provider profile、models 与 artifact

但 `009` 的 MVP 主线“前端生成约束”仍缺少独立 child work item 去冻结：

- 生成约束对象到底承载什么
- 生成控制面的顺序、显式引用要求与最小约束集合如何定义
- Hard Rules、token rules 与结构化例外如何与 recipe / whitelist 一起形成可追踪控制面
- 后续 generation constraint models / artifacts / tests 应从哪里开始

因此，本计划的目标是建立统一的 `Frontend Generation Governance Baseline`：

- 先冻结 generation governance truth order 与 non-goals
- 再冻结 recipe / whitelist / hard rules / token rules / exceptions 五类约束对象
- 最后给出后续 `models / artifacts / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入第一批实现切片：`generation constraint models`，把 recipe / whitelist / hard rules / token rules / exceptions 收敛到共享 `models/`；不同时触碰完整生成 runtime、gate 或 recheck / auto-fix。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`011` Contract baseline、`015` UI Kernel baseline、`016` Provider baseline、冻结设计稿第 11 章  
**主要约束**：

- generation governance 只能承接上游 truth，不得反向重写 Contract / Kernel / Provider
- 当前阶段只冻结 generation control plane，不直接进入完整生成 runtime
- Hard Rules 不可突破边界与结构化例外边界必须同时成立
- generation governance 必须保持 artifact-driven，而不是退回 prompt-only 约束

## 项目结构

```text
specs/017-frontend-generation-governance-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前激活的实现触点

```text
src/ai_sdlc/
└── models/
    └── frontend_generation_constraints.py     # recipe / whitelist / hard rules / token rules / exceptions

tests/
└── unit/test_frontend_generation_constraints.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将前端生成约束主线从 `009` 母规格拆成单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/017/...` 文档改动。

### Phase 1：Generation truth freeze

**目标**：锁定 generation governance 在 `Contract -> Kernel -> generation -> code generation -> Gate` 主线中的 truth order、scope 与 non-goals。  
**产物**：scope baseline、truth-order baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Constraint object freeze

**目标**：锁定 recipe / whitelist / hard rules / token rules / exceptions 五类对象与执行顺序。  
**产物**：constraint-object baseline、ordering baseline、exception baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。

### Phase 4：Generation constraint models slice

**目标**：落下 generation governance 的最小结构化模型与 MVP builder，先稳定 recipe / whitelist / hard rules / token rules / exceptions 的上游控制面。
**产物**：`src/ai_sdlc/models/frontend_generation_constraints.py`、`tests/unit/test_frontend_generation_constraints.py`、`src/ai_sdlc/models/__init__.py`。
**验证方式**：定向 `pytest`、`uv run ruff check src tests`、`git diff --check`、`uv run ai-sdlc verify constraints`。
**回退方式**：仅回退本阶段涉及的 `models/`、`tests/` 与 execution log 变更。

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| generation truth order | 文档交叉引用检查 | 人工审阅 |
| explicit reference clarity | formal wording review | 人工审阅 |
| constraint object clarity | contract review | 测试矩阵回挂 |
| hard rules and exception boundary clarity | scope review | 术语对账 |
| downstream handoff clarity | file-map review | 人工审阅 |
| generation constraint model correctness | `uv run pytest tests/unit/test_frontend_generation_constraints.py -q` | model payload / builder review |
