---
related_doc:
  - "specs/009-frontend-governance-ui-kernel/spec.md"
  - "specs/009-frontend-governance-ui-kernel/plan.md"
  - "specs/017-frontend-generation-governance-baseline/spec.md"
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
---
# 实施计划：Frontend Gate Compatibility Baseline

**编号**：`018-frontend-gate-compatibility-baseline` | **日期**：2026-04-03 | **规格**：specs/018-frontend-gate-compatibility-baseline/spec.md

## 概述

本计划处理的是 `009` 下游的 `Gate-Recheck-Auto-fix / Compatibility` formal baseline，而不是直接实现完整前端诊断平台。当前仓库已经在上游锁定并实现了：

- `011 / 012 / 013 / 014`：contract-aware verify 主链、observation provider 与 runtime attachment
- `017`：generation control plane models + artifact

但最后一条 MVP 主线仍缺少独立 child work item 去冻结：

- MVP gate matrix 到底覆盖什么
- Compatibility 如何作为同一套 gate matrix 的执行强度，而不是第二套规则
- 结构化输出与 Recheck / Auto-fix 的边界如何定义
- 后续 `models / reports / gates / tests` 的实现应从哪里开始

因此，本计划的目标是建立统一的 `Frontend Gate Compatibility Baseline`：

- 先冻结 gate / compatibility truth order 与 non-goals
- 再冻结 MVP gate matrix、结构化输出、Recheck 和 Auto-fix 边界
- 最后给出后续 `models / reports / gates / tests` 的推荐文件面与测试矩阵

当前 formal baseline 已完成。经用户明确要求连续推进 MVP 后，当前允许继续进入第一批实现切片：`gate matrix and report models`，把 MVP gate matrix、Compatibility 执行口径和结构化输出收敛到共享 `models/`；不同时触碰完整 gate execution runtime 或 auto-fix engine。

## 技术背景

**语言/版本**：Python 3.11+、Markdown formal docs  
**主要依赖**：`011` / `017` 上游 baseline、现有 `verify_constraints` 与 `pipeline_gates` 框架、冻结设计稿第 12 章  
**主要约束**：

- Compatibility 不能被实现成第二套 gate / 规则系统
- Gate / Recheck / Auto-fix 只能消费上游 truth，不得反向改写 Contract / Kernel / Provider / generation baseline
- 当前阶段只冻结并实现最小 gate matrix / report models，不直接实现完整 auto-fix runtime

## 项目结构

```text
specs/018-frontend-gate-compatibility-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 当前激活的实现触点

```text
src/ai_sdlc/
└── models/
    └── frontend_gate_policy.py               # gate matrix / compatibility policy / report models

tests/
└── unit/test_frontend_gate_policy_models.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：将 Gate / Compatibility 主线从 `009` 母规格拆成单独 canonical formal docs。  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`。  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`。  
**回退方式**：仅回退 `specs/018/...` 文档改动。

### Phase 1：Gate truth freeze

**目标**：锁定 gate / compatibility 在闭环中的 truth order、scope 与 non-goals。  
**产物**：scope baseline、truth-order baseline、non-goals baseline。  
**验证方式**：`spec.md / plan.md / tasks.md` 交叉对账。  
**回退方式**：不进入实现。

### Phase 2：Matrix / output / recheck / fix boundary freeze

**目标**：锁定 MVP gate matrix、Compatibility 执行口径、结构化输出、Recheck 与 Auto-fix 边界。  
**产物**：gate matrix baseline、compatibility baseline、report baseline、recheck/fix baseline。  
**验证方式**：contract review。  
**回退方式**：不写入代码。

### Phase 3：Implementation handoff and verification freeze

**目标**：锁定推荐文件面、ownership 边界、最小测试矩阵与进入实现前提。  
**产物**：implementation touchpoints、tests matrix、execute handoff baseline。  
**验证方式**：formal docs review + `verify constraints`。  
**回退方式**：仅回退 planning baseline。
