---
related_doc:
  - "docs/superpowers/specs/2026-04-02-ai-autosdlc-frontend-governance-ui-kernel-design.md"
  - "specs/050-frontend-program-final-proof-archive-project-cleanup-baseline/spec.md"
  - "specs/052-frontend-program-final-proof-archive-explicit-cleanup-targets-baseline/spec.md"
  - "specs/054-frontend-program-final-proof-archive-cleanup-mutation-eligibility-baseline/spec.md"
  - "specs/056-frontend-program-final-proof-archive-project-cleanup-preview-plan-baseline/spec.md"
  - "specs/057-frontend-program-final-proof-archive-cleanup-preview-plan-consumption-baseline/spec.md"
---
# 实施计划：Frontend Program Final Proof Archive Cleanup Mutation Proposal Baseline

**编号**：`058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline` | **日期**：2026-04-04 | **规格**：specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/spec.md

## 概述

`058` 是一个 docs-only 的 truth freeze work item。它不进入 `ProgramService`、CLI、tests 或真实 cleanup mutation，而是把 `cleanup_mutation_proposal` 正式定义为 `050` final proof archive project cleanup artifact 内的 canonical sibling truth surface，确保后续 child work item 在进入 proposal consumption / approval semantics 之前，先拥有稳定、可审计、不可推断的单一 proposal truth。

## 技术背景

**语言/版本**：Python 3.12  
**主要依赖**：Typer、PyYAML、pytest、ruff  
**存储**：项目内 canonical YAML artifact（`.ai-sdlc/memory/frontend-final-proof-archive-project-cleanup/latest.yaml`）  
**测试**：本 work item 为 docs-only；focused verification 使用 `uv run ai-sdlc verify constraints` 与 `git diff --check`  
**目标平台**：本地 CLI 驱动的 framework workflow  
**约束**：
- 只定义 `cleanup_mutation_proposal` truth，不新增旁路 artifact
- 只允许显式 proposal truth，禁止从 targets、eligibility、preview plan 或隐式信号推断
- 不执行真实 cleanup mutation
- 不修改 `src/` 与 `tests/`
- 为 future child work item 固定 `failing tests -> service/CLI proposal consumption -> approval/gating semantics -> execution` 的顺序

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| 单一事实源 | 将 `cleanup_mutation_proposal` 固定为 `050` cleanup artifact 的 sibling truth surface |
| 诚实边界 | 明确 proposal truth 只代表 future-consumable proposal，不授权任何 real cleanup mutation |
| focused scope | 本次仅修改 `specs/058-.../` 文档与脚手架自动更新的 project state |
| 接力顺序 | 下一子项必须先写 proposal consumption 的 failing tests，再进入 service/CLI 接线 |

## 项目结构

### 文档结构

```text
specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline/
├── spec.md
├── plan.md
├── task-execution-log.md
└── tasks.md
```

### 未来源码触点

```text
src/ai_sdlc/core/program_service.py
src/ai_sdlc/cli/program_cmd.py
tests/unit/test_program_service.py
tests/integration/test_cli_program.py
```

## 阶段计划

### Phase 0：context alignment

**目标**：确认 `058` 是 `057` 之后的 proposal truth freeze，而不是 proposal consumption 或 real mutation  
**产物**：`task-execution-log.md` 中的上下文对账记录  
**验证方式**：审阅 `050/052/054/056/057` docs 的 handoff 语义  
**回退方式**：仅回退 `058` 文档草稿内容

### Phase 1：formal truth freeze

**目标**：将 `cleanup_mutation_proposal` 的位置、字段、状态、对齐约束与 honesty boundary 冻结到 canonical docs  
**产物**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：文档对账 + `uv run ai-sdlc verify constraints`  
**回退方式**：仅回退 `specs/058-.../` 文档变更

### Phase 2：focused verification

**目标**：确认 docs-only 变更满足约束，并留下可审计验证证据  
**产物**：更新后的 `task-execution-log.md`  
**验证方式**：`uv run ai-sdlc verify constraints`、`git diff --check -- specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline .ai-sdlc/project/config/project-state.yaml`  
**回退方式**：根据失败点只调整 `058` docs

## 工作流计划

### 工作流 A：Proposal truth shape freeze

**范围**：定义 `cleanup_mutation_proposal` 的 canonical shape、state 和 item-level 对齐约束  
**影响范围**：`spec.md`、`plan.md`、`tasks.md`  
**验证方式**：审阅文档中字段与状态定义是否和 `050/052/054/056/057` 对齐  
**回退方式**：回退 proposal shape 相关段落

### 工作流 B：Proposal honesty boundary freeze

**范围**：明确 `cleanup_mutation_proposal` 与 approval / execution 的边界，并固定 future child work item 的接力顺序  
**影响范围**：`spec.md`、`plan.md`、`tasks.md`、`task-execution-log.md`  
**验证方式**：审阅是否明确写出 `failing tests -> service/CLI proposal consumption -> approval/gating semantics -> execution`  
**回退方式**：回退 handoff / non-goals 相关段落

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| `cleanup_mutation_proposal` 被固定为 sibling truth surface | 审阅 `spec.md` 中 canonical truth 定义 | 对账 `plan.md` / `tasks.md` 是否保持同一口径 |
| proposal truth 未被误写为 approval 或 execution | 审阅 `spec.md` 的非范围、需求与成功标准 | 检查 `task-execution-log.md` 是否明确 no-mutation boundary |
| docs-only 变更满足约束 | `uv run ai-sdlc verify constraints` | `git diff --check -- specs/058-frontend-program-final-proof-archive-cleanup-mutation-proposal-baseline .ai-sdlc/project/config/project-state.yaml` |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| proposal consumption 需要暴露哪些 CLI/report 字段 | 已延期到后续 child work item | 不阻塞 `058` |
| proposal review / approval 是否需要单独 truth surface | 当前保持最小 proposal baseline，不在本项扩张 | 不阻塞 `058` |

## 实施顺序建议

1. 审阅 `050/052/054/056/057`，确认 `058` 的合法承接点是 mutation proposal truth freeze，而不是 proposal consumption。
2. 重写 `058` formal docs，冻结 `cleanup_mutation_proposal` truth、alignment constraints 与 non-goals。
3. 运行 focused verification，并将证据追加到 `task-execution-log.md`。
4. 下一 child work item 从 proposal consumption 的 failing tests 开始，而不是直接做 approval 或 execution。
