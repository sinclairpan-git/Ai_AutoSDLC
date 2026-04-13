---
related_doc:
  - "docs/framework-defect-backlog.zh-CN.md"
  - "cursor/rules/ai-sdlc.md"
  - "src/ai_sdlc/stages/refine.yaml"
  - "USER_GUIDE.zh-CN.md"
---
# 实施计划：Formal Artifact Target Guard Baseline

**编号**：`117-formal-artifact-target-guard-baseline` | **日期**：2026-04-13 | **规格**：specs/117-formal-artifact-target-guard-baseline/spec.md

## 概述

`117` 的交付目标是把 formal artifact canonical target 与 breach backlog 原子记账，从规则文字收敛成真正的 guard surface。推荐做法是增加一个 formal artifact target helper，专门判断“当前 artifact 类型是否允许写到这个路径”，再补一个 breach logging check surface，供后续 review / close / preflight 消费。

## 技术背景

**语言/版本**：Python 3.11  
**主要依赖**：Typer、本仓库现有 doc/workitem helpers、close-check / verify / rules surfaces  
**存储**：`specs/<WI>/`、`docs/framework-defect-backlog.zh-CN.md`、`docs/superpowers/*`  
**测试**：`pytest` unit + integration  
**目标平台**：formal artifact write path / read-only guard surfaces  
**约束**：
- 不把 `docs/superpowers/*` 整体封死，只阻断 formal artifact 落点误写
- 不依赖会话记忆判断“是否已识别 breach”，优先通过结构化输入或 persisted signal 建模
- 保持 bounded surface，避免把 guard 做成模糊自然语言建议

## 宪章检查

| 宪章门禁 | 计划响应 |
|----------|----------|
| canonical truth 优先 | formal artifact 目标只能从 work item contract 反推 |
| 流程违约必须可审计 | breach logging check 必须能给出稳定 blocker |
| 最小改动面 | 只针对 formal artifact target 与 breach logging 原子性，不扩展到其他文档族 |

## 项目结构

### 文档结构

```text
specs/117-formal-artifact-target-guard-baseline/
├── spec.md
├── plan.md
├── tasks.md
└── task-execution-log.md
```

### 源码结构

```text
src/ai_sdlc/core/
├── artifact_target_guard.py          # 新增：formal artifact canonical target preflight
├── backlog_breach_guard.py           # 新增：识别已引用 defect 但 backlog 未登记
├── workitem_scaffold.py              # formal scaffold producer，接 canonical target guard
└── verify_constraints.py             # verify surface，暴露 misplaced / missing-backlog blocker

src/ai_sdlc/telemetry/
└── readiness.py                      # status --json surface

src/ai_sdlc/cli/
└── commands.py                       # status text surface

tests/unit/
├── test_artifact_target_guard.py
├── test_backlog_breach_guard.py
├── test_verify_constraints.py
└── test_workitem_scaffold.py

tests/integration/
├── test_cli_status.py
└── test_cli_workitem_init.py
```

## 阶段计划

### Phase 0：Formal baseline freeze

**目标**：纠正 `117` 自身 formal docs，使其与 `FD-2026-04-07-002` 对齐  
**产物**：`spec.md` / `plan.md` / `tasks.md` / `task-execution-log.md`  
**验证方式**：文档自检 + `uv run ai-sdlc verify constraints`  
**回退方式**：仅回退 `117` formal carrier

### Phase 1：Formal artifact target guard

**目标**：实现 canonical-path preflight，区分 formal vs auxiliary artifact  
**产物**：guard helper + unit tests  
**验证方式**：focused unit tests  
**回退方式**：回退 helper 与接线

### Phase 2：Breach logging atomicity guard

**目标**：为“已识别违约但未同轮补录 backlog”提供 blocker / check surface  
**产物**：breach guard helper + tests  
**验证方式**：focused unit/integration tests + `uv run ai-sdlc verify constraints`  
**回退方式**：回退该 check，不影响 artifact target guard

## 工作流计划

### 工作流 A：Artifact target canonicalization

**范围**：formal artifact path classification、allow/block reason codes  
**影响范围**：core helper 与 producer 接线  
**验证方式**：正反夹具  
**回退方式**：helper 独立回退

### 工作流 B：Breach logging atomicity

**范围**：breach identified -> backlog logged 的顺序约束  
**影响范围**：guard/check surfaces 与 review/close 路径  
**验证方式**：流程级夹具  
**回退方式**：独立回退，不影响 canonical path guard

## 关键路径验证策略

| 关键路径 | 主验证方式 | 次验证方式 |
|----------|------------|------------|
| formal spec 误写到 `docs/superpowers/*` | unit test | integration smoke |
| legal `specs/<WI>/spec.md` path 允许写入 | unit test | workitem init regression |
| breach 已识别但 backlog 未补录 | unit/integration test | `verify constraints` / `status` surface check |

## 开放问题

| 问题 | 状态 | 阻塞阶段 |
|------|------|----------|
| breach-identified signal 以何种 persisted shape 表达 | 待设计 | Phase 2 |
| 是否应接入 close-check、verify，还是独立 CLI/check helper | 待设计 | Phase 2 |

## 实施顺序建议

1. 先冻结 `117` formal docs 边界
2. 先写 artifact target 正反测试
3. 实现 canonical path guard
4. 再补 breach logging atomicity surface 与回归
